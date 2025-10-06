from langchain.prompts import PromptTemplate
import re

class CredibilityAnalyzer:
    def __init__(self, llm):
        self.llm = llm
        self.source_weights = {
            'academic': 1.0,
            'news': 0.8,
            'government': 0.9,
            'corporate': 0.5,
            'blog': 0.4,
            'social': 0.3,
            'commercial': 0.3
        }
    
    def score_claim(self, claim_text, source_type, context):
        """Score a claim's credibility (0-10)"""
        # Base score from source type
        base_score = self.source_weights.get(source_type, 0.5) * 10
        
        # Bias detection
        bias_penalty = self._detect_bias(claim_text, context)
        
        # Language analysis
        language_penalty = self._analyze_language(claim_text)
        
        # Context relevance
        context_bonus = self._check_context(claim_text, context, source_type)
        
        # Calculate final score
        final_score = base_score - bias_penalty - language_penalty + context_bonus
        final_score = max(0, min(10, final_score))  # Clamp 0-10
        
        return round(final_score, 1)
    
    def _detect_bias(self, claim, context):
        """Detect bias indicators"""
        penalty = 0
        
        # Promotional language
        promo_words = ['best', 'greatest', 'amazing', 'revolutionary', 'guaranteed']
        for word in promo_words:
            if word.lower() in claim.lower():
                penalty += 1.5
        
        # Self-promotion context
        if 'ceo' in context.lower() or 'founder' in context.lower():
            if 'our' in claim.lower() or 'we' in claim.lower():
                penalty += 2
        
        # Commercial context
        if 'commercial' in context.lower() or 'advertisement' in context.lower():
            penalty += 2.5
        
        return min(penalty, 5)  # Max 5 point penalty
    
    def _analyze_language(self, claim):
        """Analyze claim language for credibility markers"""
        penalty = 0
        
        # Absolute statements
        absolute_words = ['always', 'never', 'every', 'all', 'none', 'perfect']
        for word in absolute_words:
            if re.search(r'\b' + word + r'\b', claim.lower()):
                penalty += 0.5
        
        # Emotional language
        emotional_words = ['shocking', 'unbelievable', 'incredible', 'devastating']
        for word in emotional_words:
            if word in claim.lower():
                penalty += 0.5
        
        # Vague quantifiers
        if re.search(r'many|some|several|few', claim.lower()):
            penalty += 0.3
        
        return min(penalty, 3)  # Max 3 point penalty
    
    def _check_context(self, claim, context, source_type):
        """Check if context improves credibility"""
        bonus = 0
        
        # Research/study mention
        if 'study' in claim.lower() or 'research' in claim.lower():
            bonus += 1
        
        # Data/statistics
        if re.search(r'\d+%|\d+\s*(percent|million|billion)', claim):
            bonus += 0.5
        
        # Expert quote (not self-promotional)
        if source_type in ['academic', 'news'] and 'according to' in claim.lower():
            bonus += 1
        
        # Independent validation
        if 'independent' in context.lower() or 'peer-reviewed' in context.lower():
            bonus += 1.5
        
        return min(bonus, 3)  # Max 3 point bonus
    
    def explain_score(self, claim_text, source_type, context, score):
        """Generate explanation for credibility score"""
        prompt = PromptTemplate(
            template="""Explain why this claim has credibility score {score}/10:

Claim: {claim}
Source Type: {source_type}
Context: {context}

Provide brief explanation focusing on bias, language, and source reliability.""",
            input_variables=["claim", "source_type", "context", "score"]
        )
        
        result = self.llm.invoke(
            prompt.format(
                claim=claim_text,
                source_type=source_type,
                context=context,
                score=score
            )
        )
        
        return result.content