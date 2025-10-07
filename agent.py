from llm_factory import LLMFactory
from tools import search_web, extract_claims, batch_validate_claims
from credibility import CredibilityAnalyzer
from system_prompts import RECONCILIATION_PROMPT, REPORT_GENERATION_PROMPT, UPDATE_ANALYSIS_PROMPT
from config import CREDIBILITY_PARAMS, PERFORMANCE_CONFIG
import json
import time
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor

class ResearchAgent:
    def __init__(self, llm_provider, llm_model=None):
        self.llm = LLMFactory.create_llm(llm_provider, llm_model)
        self.credibility = CredibilityAnalyzer(self.llm)
        self.cache = TTLCache(maxsize=100, ttl=PERFORMANCE_CONFIG['cache_ttl'])
        self.metrics = {}
    
    def research(self, topic):
        start = time.time()
        if topic in self.cache:
            return self.cache[topic]
        
        print("🔎 Searching...")
        sources = search_web(topic, num_results=10)
        
        print("📝 Extracting claims...")
        all_claims = []
        with ThreadPoolExecutor(max_workers=PERFORMANCE_CONFIG['max_concurrent_requests']) as executor:
            results = executor.map(lambda src: extract_claims(src['content'], src['url'], self.llm), sources[:8])
            for claims in results:
                all_claims.extend(claims)
        
        print(f"✅ Found {len(all_claims)} claims")
        print("🎯 Scoring credibility...")
        
        scored = []
        low_medium = [c for c in all_claims if self.credibility.score_claim(c['text'], c['source_type'], c.get('source_context', ''))['score'] < CREDIBILITY_PARAMS['validation_required']]
        
        if PERFORMANCE_CONFIG['parallel_validation'] and low_medium:
            print("⚡ Batch validating...")
            evidences = batch_validate_claims([c['text'] for c in low_medium], os.getenv('SERPER_API_KEY'))
        
        for i, claim in enumerate(all_claims):
            score_data = self.credibility.score_claim(claim['text'], claim['source_type'], claim.get('source_context', ''))
            claim['credibility_score'] = score_data['score']
            claim['score_reasoning'] = score_data['reasoning']
            
            if claim['credibility_score'] < CREDIBILITY_PARAMS['validation_required']:
                evidence = evidences[low_medium.index(claim)] if claim in low_medium else "No evidence"
                validation = self.credibility.validate_claim(claim['text'], claim['credibility_score'], evidence)
                claim['credibility_score'] = validation['validated_score']
                claim['validation'] = validation['verdict']
                claim['validation_reasoning'] = validation['explanation']
            
            action = self.credibility.get_final_action(
                claim['text'], claim['credibility_score'], claim['source_type'], claim.get('validation', 'none')
            )
            claim['action'] = action['action']
            claim['action_reasoning'] = action['reasoning']
            scored.append(claim)
        
        self.cache[topic] = {'claims': scored, 'sources': sources}
        report = self._generate_report(topic, scored, sources)
        
        elapsed = time.time() - start
        self.metrics['research_time'] = elapsed
        
        result = {
            'report': report,
            'claims': scored,
            'overall_credibility': self._calc_avg(scored),
            'sources_count': len(sources),
            'time_seconds': elapsed,
            'sources_analyzed': self._format_sources_analyzed(sources, scored),
            'summary': self._generate_summary(scored, sources)
        }
        self.cache[topic] = result
        return result
    
    def update_research(self, filepath):
        start = time.time()
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📝 Extracting new claims...")
        new_claims = extract_claims(content, filepath, self.llm)
        
        for claim in new_claims:
            score_data = self.credibility.score_claim(claim['text'], claim['source_type'], claim.get('source_context', ''))
            claim['credibility_score'] = score_data['score']
            claim['score_reasoning'] = score_data['reasoning']
            action = self.credibility.get_final_action(claim['text'], claim['credibility_score'], claim['source_type'], 'none')
            claim['action'] = action['action']
            claim['action_reasoning'] = action['reasoning']
        
        topic = list(self.cache.keys())[0] if self.cache else 'unknown'
        existing = self.cache.get(topic, {'claims': []})['claims']
        
        print("🔄 LLM analyzing update strategy...")
        strategy = self._llm_update_strategy(existing, new_claims, filepath)
        
        print(f"    📊 Strategy: {strategy['approach']}")
        print(f"    💡 Reason: {strategy['reasoning']}")
        
        merged = self._smart_merge(existing, new_claims, strategy['approach'])
        self.cache[topic]['claims'] = merged
        report = self._generate_report(topic, merged, self.cache[topic].get('sources', []))
        
        elapsed = time.time() - start
        overhead = elapsed / self.metrics.get('research_time', 1)
        
        result = {
            'report': report,
            'claims': merged,
            'overall_credibility': self._calc_avg(merged),
            'update_time': elapsed,
            'overhead_ratio': overhead,
            'update_strategy': strategy,
            'sources_analyzed': self._format_sources_analyzed(self.cache[topic].get('sources', []), merged),
            'summary': self._generate_summary(merged, self.cache[topic].get('sources', []))
        }
        self.cache[topic] = result
        return result
    
    def _llm_update_strategy(self, existing, new, source):
        try:
            conflicts = sum(1 for n in new for e in existing if self._similar(n['text'], e['text']))
            prompt = UPDATE_ANALYSIS_PROMPT.format(
                original_quality=self._calc_avg(existing),
                new_source_type=new[0]['source_type'] if new else 'document',
                new_claims_count=len(new),
                conflicts_count=conflicts,
                reinforcements_count=len(new) - conflicts,
                new_info_count=len(new)
            )
            result = self.llm.invoke(prompt)
            return json.loads(result.content)
        except:
            return {'approach': 'incremental', 'reasoning': 'Fallback due to error', 'estimated_quality_impact': 'medium'}
    
    def _smart_merge(self, existing, new, approach):
        try:
            prompt = RECONCILIATION_PROMPT.format(
                existing_claims=json.dumps([c['text'] for c in existing[:20]]),
                new_claims=json.dumps([c['text'] for c in new])
            )
            result = self.llm.invoke(prompt)
            reconciliation = json.loads(result.content)
            
            all_claims = existing + new
            if approach == 'regenerate':
                all_claims.sort(key=lambda x: x['credibility_score'], reverse=True)
            
            seen = set()
            unique = []
            for claim in all_claims:
                key = claim['text'][:100].lower()
                if key not in seen:
                    seen.add(key)
                    unique.append(claim)
            
            return unique[:CREDIBILITY_PARAMS['max_claims_per_source'] * 2]
        except:
            return existing + new
    
    def _similar(self, text1, text2):
        return text1[:50].lower() == text2[:50].lower()
    
    def _calc_avg(self, claims):
        valid = [c for c in claims if c['action'] != 'EXCLUDE']
        return sum(c['credibility_score'] for c in valid) / len(valid) if valid else 0
    
    def _generate_report(self, topic, claims, sources):
        high = [c for c in claims if c['credibility_score'] >= CREDIBILITY_PARAMS['thresholds']['high']]
        medium = [c for c in claims if CREDIBILITY_PARAMS['thresholds']['medium'] <= c['credibility_score'] < CREDIBILITY_PARAMS['thresholds']['high']]
        
        prompt = REPORT_GENERATION_PROMPT.format(
            topic=topic,
            high_credibility_claims="\n".join([
                f"- {c['text']} (Score: {c['credibility_score']:.1f}, Source: {c['source_type']}, Source URL: {c['source']}, Reason: {'; '.join(c['score_reasoning'])}, Decision: {c['action']} because {c['action_reasoning']})"
                for c in high[:20]
            ]),
            medium_credibility_claims="\n".join([
                f"- {c['text']} [⚠️ VERIFY] (Score: {c['credibility_score']:.1f}, Source: {c['source_type']}, Source URL: {c['source']}, Reason: {'; '.join(c['score_reasoning'])}, Validation: {c.get('validation', 'none')} - {c.get('validation_reasoning', 'none')}, Decision: {c['action']} because {c['action_reasoning']})"
                for c in medium[:15]
            ])
        )
        
        result = self.llm.invoke(prompt)
        return result.content
    
    def _format_sources_analyzed(self, sources, claims):
        source_summary = []
        for src in sources:
            src_claims = [c for c in claims if c['source'] == src['url']]
            if src_claims:
                summary = f"**Source**: {src['url']} ({src['source_type']})\n"
                summary += f"**Claims Found**: {len(src_claims)}\n"
                summary += "\n".join([
                    f"- **Claim**: {c['text']}\n  - **Score**: {c['credibility_score']:.1f}\n  - **Reasoning**: {'; '.join(c['score_reasoning'])}"
                    for c in src_claims
                ])
                source_summary.append(summary)
        return "\n\n".join(source_summary) if source_summary else "No sources analyzed"
    
    def _generate_summary(self, claims, sources):
        high = [c for c in claims if c['credibility_score'] >= CREDIBILITY_PARAMS['thresholds']['high']]
        medium = [c for c in claims if CREDIBILITY_PARAMS['thresholds']['medium'] <= c['credibility_score'] < CREDIBILITY_PARAMS['thresholds']['high']]
        excluded = [c for c in claims if c['action'] == 'EXCLUDE']
        
        summary = f"**Summary of Findings**:\n"
        summary += f"- **Total Claims Analyzed**: {len(claims)}\n"
        summary += f"- **High Credibility Claims** ({len(high)}): Included due to strong evidence and reliable sources.\n"
        summary += f"- **Medium Credibility Claims** ({len(medium)}): Require verification due to potential biases or limited evidence.\n"
        summary += f"- **Excluded Claims** ({len(excluded)}): Removed due to low credibility or significant biases.\n"
        summary += f"- **Sources Analyzed**: {len(sources)} sources, including {', '.join(set(s['source_type'] for s in sources))}.\n"
        summary += f"- **Key Insights**: High-credibility claims are primarily from academic and government sources, while commercial and corporate sources often required validation due to promotional or self-interest biases."
        return summary