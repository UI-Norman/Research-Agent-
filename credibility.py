from system_prompts import (
    VALIDATION_DECISION_PROMPT,
    BIAS_DETECTION_PROMPT,
    CLAIM_VALIDATION_PROMPT,
    FINAL_ACTION_PROMPT,
    SYSTEM_CONFIG
)
import re
import json
from cachetools import TTLCache

class CredibilityAnalyzer:
    def __init__(self, llm):
        self.llm = llm
        self.weights = SYSTEM_CONFIG['source_weights']
        self.cache = TTLCache(maxsize=1000, ttl=7200)
    
    def score_claim(self, claim_text, source_type, context):
        cache_key = f"{claim_text[:50]}_{source_type}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        base_score = self.weights.get(source_type, 0.5) * 10
        promo = self._detect_promotional(claim_text)
        absolute = self._detect_absolute(claim_text)
        self_interest = self._detect_self_interest(claim_text, context)
        evidence = self._detect_evidence(claim_text)
        
        heuristic_score = base_score - promo - absolute - self_interest + evidence
        heuristic_score = max(0, min(10, heuristic_score))
        
        decision = self._llm_decide_validation(
            claim_text, source_type, context, heuristic_score,
            promo, absolute, self_interest, evidence
        )
        
        final_score = heuristic_score
        reasoning = [f"Base score: {base_score:.1f} due to {source_type} source"]
        if promo:
            reasoning.append(f"Promotional penalty: -{promo:.1f} for promotional language")
        if absolute:
            reasoning.append(f"Absolute language penalty: -{absolute:.1f} for absolute terms")
        if self_interest:
            reasoning.append(f"Self-interest penalty: -{self_interest:.1f} due to self-serving context")
        if evidence:
            reasoning.append(f"Evidence bonus: +{evidence:.1f} for research-based evidence")
        
        if decision['needs_deep_analysis']:
            reasoning.append(f"LLM analysis: {decision['reasoning']}")
            bias_result = self._llm_bias_analysis(claim_text, context)
            final_score += bias_result['adjustment']
            final_score = max(0, min(10, final_score))
            reasoning.append(f"Bias adjustment: {bias_result['adjustment']:.1f} due to {', '.join(bias_result['bias_types'])}")
        else:
            reasoning.append(f"LLM decision: {decision['reasoning']}")
        
        self.cache[cache_key] = {'score': round(final_score, 1), 'reasoning': reasoning}
        return self.cache[cache_key]
    
    def _llm_decide_validation(self, claim, source_type, context, score, promo, absolute, self_interest, evidence):
        try:
            prompt = VALIDATION_DECISION_PROMPT.format(
                claim=claim[:300],
                source_type=source_type,
                heuristic_score=round(score, 1),
                context=context[:200],
                promo_penalty=promo,
                absolute_penalty=absolute,
                self_interest_penalty=self_interest,
                evidence_bonus=evidence
            )
            result = self.llm.invoke(prompt)
            return json.loads(result.content)
        except:
            return {'needs_deep_analysis': 3.5 <= score <= 7.5, 'reasoning': 'Fallback due to parsing error', 'confidence': 5}
    
    def _llm_bias_analysis(self, text, context):
        try:
            prompt = BIAS_DETECTION_PROMPT.format(text=text[:500], context=context[:200])
            result = self.llm.invoke(prompt)
            analysis = json.loads(result.content)
            return {
                'adjustment': analysis.get('adjustment', 0),
                'bias_types': analysis.get('bias_types', []),
                'severity': analysis.get('severity', 'medium')
            }
        except:
            return {'adjustment': 0, 'bias_types': [], 'severity': 'unknown'}
    
    def validate_claim(self, claim, score, evidence):
        try:
            prompt = CLAIM_VALIDATION_PROMPT.format(claim=claim, score=score, evidence=evidence[:1500])
            result = self.llm.invoke(prompt)
            validation = json.loads(result.content)
            new_score = score + validation.get('score_adjustment', 0)
            return {
                'validated_score': max(0, min(10, new_score)),
                'verdict': validation.get('verdict', 'NEUTRAL'),
                'confidence': validation.get('confidence', 5),
                'explanation': validation.get('explanation', 'No explanation provided')
            }
        except:
            return {'validated_score': score, 'verdict': 'NEUTRAL', 'confidence': 5, 'explanation': 'Fallback validation due to error'}
    
    def get_final_action(self, claim, score, source_type, validation_status):
        try:
            prompt = FINAL_ACTION_PROMPT.format(
                claim=claim[:200],
                score=score,
                source_type=source_type,
                validation_status=validation_status
            )
            result = self.llm.invoke(prompt)
            decision = json.loads(result.content)
            return {'action': decision.get('action', self._fallback_action(score)),
                    'reasoning': decision.get('reasoning', 'Fallback decision')}
        except:
            return {'action': self._fallback_action(score), 'reasoning': 'Fallback due to parsing error'}
    
    def _fallback_action(self, score):
        if score >= 7.5:
            return "INCLUDE"
        elif score >= 4.5:
            return "WARN"
        return "EXCLUDE"
    
    def _detect_promotional(self, text):
        patterns = [
            r'\b(best|greatest|amazing|revolutionary|guaranteed|perfect|ultimate)\b',
            r'\b(world.?class|industry.?leading|award.?winning)\b'
        ]
        penalty = sum(len(re.findall(p, text.lower())) * 1.5 for p in patterns)
        return min(penalty, 4)
    
    def _detect_absolute(self, text):
        words = ['always', 'never', 'every', 'all', 'none', 'impossible', 'guaranteed']
        return min(sum(0.7 for w in words if w in text.lower()), 3)
    
    def _detect_self_interest(self, text, context):
        penalty = 0
        if any(r in context.lower() for r in ['ceo', 'founder', 'executive', 'sponsored']):
            if any(r in text.lower() for r in ['our', 'we', 'us', 'my', 'i']):
                penalty += 3.0
        if 'commercial' in context.lower() or 'advertisement' in context.lower():
            penalty += 3.5
        return min(penalty, 5)
    
    def _detect_evidence(self, text):
        bonus = 0
        if re.search(r'\b(study|research|peer.?reviewed|published)\b', text.lower()):
            bonus += 2.0
        if re.search(r'\d+(\.\d+)?%|\d+\s*(participants|subjects|samples)', text.lower()):
            bonus += 1.5
        if re.search(r'(according to|expert|professor|dr\.)', text.lower()):
            bonus += 1.0
        if 'independent' in text.lower() or 'unbiased' in text.lower():
            bonus += 1.5
        return min(bonus, 4)