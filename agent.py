from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from tools import search_web, extract_claims
from credibility import CredibilityAnalyzer
import json

class ResearchAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        self.credibility_analyzer = CredibilityAnalyzer(self.llm)
        self.research_cache = {}
        
    def research(self, topic):
        """Conduct credibility-aware research"""
        print("🔎 Searching web sources...")
        search_results = search_web(topic)
        
        print("📝 Extracting claims...")
        claims = []
        for result in search_results[:5]:  # Top 5 results
            extracted = extract_claims(result['content'], result['url'], self.llm)
            claims.extend(extracted)
        
        print(f"✅ Found {len(claims)} claims")
        print("🎯 Analyzing credibility...")
        
        # Score each claim
        scored_claims = []
        for claim in claims:
            score = self.credibility_analyzer.score_claim(
                claim['text'], 
                claim['source_type'], 
                claim['context']
            )
            claim['credibility_score'] = score
            claim['action'] = self._determine_action(score)
            scored_claims.append(claim)
        
        # Cache for updates
        self.research_cache[topic] = {
            'claims': scored_claims,
            'sources': search_results
        }
        
        print("📄 Generating report...")
        report = self._generate_report(topic, scored_claims)
        
        return {
            'report': report,
            'claims': scored_claims,
            'overall_credibility': self._calc_overall_score(scored_claims),
            'sources_count': len(search_results)
        }
    
    def update_research(self, filepath):
        """Update research with new source"""
        print("📖 Reading update file...")
        with open(filepath, 'r') as f:
            content = f.read()
        
        print("📝 Extracting new claims...")
        new_claims = extract_claims(content, filepath, self.llm)
        
        print("🔄 Reconciling with existing research...")
        # Get cached research
        topic = list(self.research_cache.keys())[0]
        existing_claims = self.research_cache[topic]['claims']
        
        # Score new claims
        for claim in new_claims:
            score = self.credibility_analyzer.score_claim(
                claim['text'], 
                claim['source_type'], 
                claim['context']
            )
            claim['credibility_score'] = score
            claim['action'] = self._determine_action(score)
        
        # Reconcile claims
        reconciled = self._reconcile_claims(existing_claims, new_claims)
        
        # Update cache
        self.research_cache[topic]['claims'] = reconciled
        
        print("📄 Generating updated report...")
        report = self._generate_report(topic, reconciled)
        
        return {
            'report': report,
            'claims': reconciled,
            'overall_credibility': self._calc_overall_score(reconciled)
        }
    
    def _reconcile_claims(self, existing, new):
        """Reconcile new claims with existing ones"""
        prompt = PromptTemplate(
            template="""Compare these claims and identify conflicts, reinforcements, or new info.

Existing Claims:
{existing}

New Claims:
{new}

Return JSON with: {{"conflicts": [], "reinforcements": [], "new": []}}""",
            input_variables=["existing", "new"]
        )
        
        result = self.llm.invoke(
            prompt.format(
                existing=json.dumps([c['text'] for c in existing[:10]]),
                new=json.dumps([c['text'] for c in new])
            )
        )
        
        try:
            analysis = json.loads(result.content)
            # Merge: prioritize higher credibility scores
            all_claims = existing + new
            all_claims.sort(key=lambda x: x['credibility_score'], reverse=True)
            return all_claims
        except:
            return existing + new
    
    def _determine_action(self, score):
        """Determine action based on credibility score"""
        if score >= 7:
            return "INCLUDE"
        elif score >= 4:
            return "INCLUDE_WITH_WARNING"
        else:
            return "EXCLUDE"
    
    def _calc_overall_score(self, claims):
        """Calculate overall credibility"""
        if not claims:
            return 0
        valid_claims = [c for c in claims if c['action'] != 'EXCLUDE']
        if not valid_claims:
            return 0
        return sum(c['credibility_score'] for c in valid_claims) / len(valid_claims)
    
    def _generate_report(self, topic, claims):
        """Generate final research report"""
        high_cred = [c for c in claims if c['credibility_score'] >= 7]
        med_cred = [c for c in claims if 4 <= c['credibility_score'] < 7]
        
        prompt = PromptTemplate(
            template="""Generate a research report on: {topic}

High Credibility Claims ({count_high}):
{high_claims}

Medium Credibility Claims ({count_med}):
{med_claims}

Write a comprehensive report. Mark medium credibility claims with [⚠️ VERIFY].
Focus on high-credibility information.""",
            input_variables=["topic", "count_high", "high_claims", "count_med", "med_claims"]
        )
        
        result = self.llm.invoke(
            prompt.format(
                topic=topic,
                count_high=len(high_cred),
                high_claims="\n".join([f"- {c['text']}" for c in high_cred[:15]]),
                count_med=len(med_cred),
                med_claims="\n".join([f"- {c['text']}" for c in med_cred[:10]])
            )
        )
        
        return result.content