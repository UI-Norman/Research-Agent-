CLAIM_EXTRACTION_PROMPT = """You are a precise claim extraction system. Extract factual claims from text.

Text: {content}

RULES:
1. Extract only verifiable factual statements
2. Identify source context (who is making the claim, their role/affiliation)
3. Note bias indicators (self-interest, promotional intent, funding sources)
4. Assess if claim is verifiable
5. Prioritize claims by relevance and impact

Return JSON:
[
  {{
    "text": "specific factual claim",
    "context": "who said it, their role, and why",
    "potential_bias": "self-promotion/commercial/funded/neutral/unknown",
    "verifiable": true/false,
    "importance": "high/medium/low"
  }}
]

Extract up to 12 most important claims."""

VALIDATION_DECISION_PROMPT = """You are a credibility coordinator. Decide if this claim needs deeper LLM analysis.

Claim: {claim}
Source Type: {source_type}
Initial Score: {heuristic_score}/10
Context: {context}

Detected Signals:
- Promotional language: {promo_penalty}
- Absolute claims: {absolute_penalty}
- Self-interest: {self_interest_penalty}
- Evidence markers: {evidence_bonus}

DECIDE:
- High score (>7.5) or low score (<3.5): Skip deep analysis
- Borderline (3.5-7.5): Deep analysis needed
- Conflicting signals or suspicious context (CEO, commercial, funded): Deep analysis needed

Return JSON:
{{
  "needs_deep_analysis": true/false,
  "reasoning": "explain decision in 1-2 sentences",
  "confidence": 0-10
}}"""

BIAS_DETECTION_PROMPT = """You are a bias detection specialist. Analyze credibility issues.

Text: {text}
Context: {context}

Detect:
1. Self-serving bias (promoting own interests)
2. Commercial bias (selling products/services)
3. Authority bias (unqualified expertise claims)
4. Funding bias (sponsor conflicts)
5. Emotional manipulation
6. Exaggeration or selective reporting

Return JSON:
{{
  "bias_score": 0-10,
  "bias_types": ["list of detected biases"],
  "severity": "low/medium/high",
  "adjustment": -4.0 to +2.0
}}"""

CLAIM_VALIDATION_PROMPT = """You are a fact-checker. Cross-reference claim against evidence.

Claim: {claim}
Current Score: {score}/10

Evidence:
{evidence}

Determine:
- SUPPORTS: Evidence reinforces claim (+1 to +2)
- CONTRADICTS: Evidence challenges claim (-2 to -4)
- NEUTRAL: No clear support/contradiction (0)

Return JSON:
{{
  "verdict": "SUPPORTS/CONTRADICTS/NEUTRAL",
  "confidence": 0-10,
  "score_adjustment": -4.0 to +2.0,
  "explanation": "reasoning in 1-2 sentences"
}}"""

RECONCILIATION_PROMPT = """You are a research synthesizer. Compare existing and new claims.

Existing Claims:
{existing_claims}

New Claims:
{new_claims}

Identify:
1. CONFLICTS: New contradicts existing
2. REINFORCEMENTS: New supports existing
3. NEW: Novel information

For conflicts, prioritize HIGHER credibility scores or more recent sources.
For reinforcements, increase confidence of existing claims.
For new info, integrate if credible (score >4.5).

Return JSON:
{{
  "conflicts": [
    {{
      "existing_claim": "text",
      "new_claim": "text",
      "resolution": "keep_existing/replace_with_new/merge_both",
      "reason": "explanation in 1-2 sentences"
    }}
  ],
  "reinforcements": [
    {{
      "existing_claim": "text",
      "new_claim": "text",
      "action": "increase_confidence"
    }}
  ],
  "new_information": ["list of genuinely new claims"]
}}"""

FINAL_ACTION_PROMPT = """You are the final decision maker for claim actions.

Claim: {claim}
Final Credibility Score: {score}/10
Source Type: {source_type}
Validation Status: {validation_status}

DECIDE ACTION:
- Score ≥7.5: INCLUDE (high credibility)
- Score 4.5-7.4: WARN (needs verification)
- Score <4.5: EXCLUDE (low credibility)

Consider:
- Critical claims need higher standards
- Multiple high-credibility sources increase confidence
- Recent validation results
- Context-specific biases (e.g., CEO self-promotion, funded research)

Return JSON:
{{
  "action": "INCLUDE/WARN/EXCLUDE",
  "reasoning": "explain in 1-2 sentences",
  "confidence": 0-10
}}"""

REPORT_GENERATION_PROMPT = """You are a research report writer. Create a comprehensive credible report.

Topic: {topic}

HIGH CREDIBILITY (Score ≥7.5):
{high_credibility_claims}

MEDIUM CREDIBILITY (Score 4.5-7.4) - VERIFY:
{medium_credibility_claims}

Guidelines:
1. Lead with high-credibility claims, citing source type and reasoning
2. Mark medium claims with [⚠️ VERIFY], include reasoning
3. Note conflicts and resolutions explicitly
4. Professional, concise, comprehensive
5. Include source analysis (why each source was weighted)

Generate report in markdown format."""

UPDATE_ANALYSIS_PROMPT = """You are an update analyzer. Assess impact of new information.

Original Research Quality: {original_quality}/10
New Source Type: {new_source_type}
New Claims Count: {new_claims_count}

Analysis:
- Conflicts: {conflicts_count}
- Reinforcements: {reinforcements_count}
- New information: {new_info_count}

DECIDE:
- >25% conflicts or higher-credibility new source: regenerate
- Mostly reinforcements or new info: incremental update
- Low new claim count (<5) and low conflicts: incremental update

Return JSON:
{{
  "approach": "regenerate/incremental",
  "reasoning": "explain in 1-2 sentences",
  "estimated_quality_impact": "high/medium/low",
  "recommended_action": "description in 1-2 sentences"
}}"""

SUMMARY_PROMPT = """You are a research summarizer. Create a concise summary for the topic '{topic}'.

High Credibility Claims ({count_high}):
{high_claims}

Medium Credibility Claims ({count_med}):
{med_claims}

Guidelines:
1. Summarize key findings in 3-5 sentences
2. Focus on high-credibility claims
3. Highlight significant insights and their implications
4. Avoid medium-credibility claims unless critical
5. Use clear, professional language

Return plain text summary."""
SYSTEM_CONFIG = {
    "credibility_thresholds": {"high": 7.5, "medium": 4.5, "low": 0.0},
    "source_weights": {
        "academic": 1.0,
        "government": 0.95,
        "news": 0.85,
        "corporate": 0.5,
        "blog": 0.4,
        "social": 0.3,
        "commercial": 0.25,
        "document": 0.6
    },
    "validation_depth": {"high_priority": 4, "medium_priority": 2, "low_priority": 1}
}