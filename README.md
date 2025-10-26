# Credibility-Aware Research Agent for RND 

## 📋 System Overview

This system evaluates information credibility in real-time, assigns scores, and takes dynamic actions to ensure factual accuracy in LLM research. It uses a hybrid approach combining heuristic analysis with LLM-based deep validation for optimal performance.

## 🎯 Core Requirements Met

### ✅ Context-Specific Credibility
- **LOW** (self-interest bias detection)
- **MEDIUM** (valid insider info, context-aware)
- **LOW** (promotional language penalty)
- **HIGH** (evidence bonus, peer-reviewed)
- source consideration: Built into bias detection with adjustment range -4.0 to +2.0

### ✅ Dynamic Actions (LLM-Driven Final Decision)
- **Score ≥7.5**: INCLUDE (high credibility)
- **Score 4.5-7.4**: WARN (verification needed)
- **Score <4.5**: (low credibility)
- Final action determined by LLM considering score, source type, validation status, and context

### ✅ Incremental Updates (LLM-Guided Strategy)
- Conflict resolution based on credibility scores (highest priority)
- LLM analyzes update strategy (regenerate vs incremental)
- Smart merge with reconciliation for conflicts, reinforcements, and new info

### 📁 Folder Architecture
credibility-research-agent/
│
├── app.py                      # Streamlit web interface
├── agent.py                    # Core ResearchAgent class
├── credibility.py              # CredibilityAnalyzer with scoring logic
├── tools.py                    # Search, extraction, validation utilities
├── llm_factory.py              # LLM provider management (Gemini/Groq)
├── config.py                   # Configuration and environment setup
├── system_prompts.py           # All LLM prompts and system config
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys)              
├── .gitignore                  # Git ignore rules
├── README.md                   # This file                  
└── research_ai_ethics.txt

## 🏗️ Solution Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              USER INTERFACE (app.py)                         │
│         Streamlit Web App for research & updates             │
│  - Model Selection (Gemini/Groq)                             │
│  - Research Execution                                        │
│  - File Upload for Updates                                   │
│  - Report Display & Download                                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              RESEARCH AGENT (agent.py)                       │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ LLM Integration via LLMFactory                       │    │
│  │ - Dynamic model selection (Gemini/Groq)              │    │
│  │ - System prompts for all operations                  │    │
│  │ - Caching with TTL (7200s)                           │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Research Flow:                                              │
│  1. Web Search (tools.py) - Serper API or mock               │
│  2. Claim Extraction (LLM-based with prompt)                 │
│  3. Credibility Scoring (hybrid heuristic + LLM)             │
│  4. Batch Validation (parallel for low-medium scores)        │
│  5. Action Determination (LLM final decision)                │
│  6. Report Generation (LLM-based with prompt)                │
│                                                              │
│  Update Flow (LLM-Guided Incremental):                       │
│  1. Load cached claims                                       │
│  2. Extract new claims from uploaded file                    │
│  3. LLM analyzes update strategy                             │
│  4. Smart reconciliation (conflicts/reinforcements)          │
│  5. Merge with highest credibility priority                  │
│  6. Generate updated report                                  │
└────────────┬──────────────┬──────────────────────────────┬───┘
             │              │                              │
             ▼              ▼                              ▼
    ┌────────────┐  ┌──────────────┐         ┌──────────────────┐
    │  TOOLS     │  │ CREDIBILITY  │         │ SYSTEM PROMPTS   │
    │ (tools.py) │  │(credibility  │         │(system_prompts   │
    │            │  │    .py)      │         │     .py)         │
    │ - Search   │  │              │         │                  │
    │ - Extract  │  │ - Score      │         │ - Claim extract  │
    │ - Classify │  │ - LLM Decide │         │ - Validation     │
    │ - Validate │  │ - Bias LLM   │         │ - Bias detect    │
    │ - Batch    │  │ - Validate   │         │ - Final action   │
    │            │  │ - Action LLM │         │ - Reconcile      │
    │            │  │ - Heuristics │         │ - Report gen     │
    │            │  │ - Cache      │         │ - Update analyze │
    └────────────┘  └──────────────┘         └──────────────────┘
         │                  │                         │
         └──────────────────┴─────────────────────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │    External Services     │
              │  - Serper API (search)   │
              │  - Google Gemini API     │
              │  - Groq API              │
              └──────────────────────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │   Configuration Layer    │
              │  - config.py             │
              │  - llm_factory.py        │
              │  - Environment vars      │
              └──────────────────────────┘
```

## 🔧 Component Connections

### How System Prompts Connect to Files:

```
system_prompts.py
    │
    ├─► agent.py
    │   └─ Uses: RECONCILIATION_PROMPT, REPORT_GENERATION_PROMPT, 
    │            UPDATE_ANALYSIS_PROMPT, SUMMARY_PROMPT
    │   └─ Method: Format strings with context
    │
    ├─► tools.py
    │   └─ Uses: CLAIM_EXTRACTION_PROMPT
    │   └─ Method: LLM invoke with formatted prompt
    │
    └─► credibility.py
        └─ Uses: VALIDATION_DECISION_PROMPT, BIAS_DETECTION_PROMPT,
                 CLAIM_VALIDATION_PROMPT, FINAL_ACTION_PROMPT
        └─ Method: LLM invoke with JSON response parsing
```

### File Interactions:

```
app.py (Streamlit UI)
  └─► config.py (setup_environment)
       ├─► Load .env variables
       ├─► Validate API keys
       └─► Return config dict
  └─► llm_factory.py (LLMFactory)
       ├─► create_llm(provider, model)
       └─► get_available_models(config)
  └─► agent.py (ResearchAgent)
       ├─► research(topic)
       │    ├─► tools.search_web()
       │    ├─► tools.extract_claims() → system_prompts.py
       │    ├─► credibility.score_claim() → system_prompts.py
       │    ├─► tools.batch_validate_claims()
       │    ├─► credibility.validate_claim() → system_prompts.py
       │    ├─► credibility.get_final_action() → system_prompts.py
       │    └─► _generate_report() → system_prompts.py
       └─► update_research(filepath)
            ├─► tools.extract_claims()
            ├─► credibility.score_claim()
            ├─► _llm_update_strategy() → system_prompts.py
            ├─► _smart_merge() → system_prompts.py
            └─► _generate_report() → system_prompts.py
```

## 📊 Agent Design

### Research Agent States:
1. **IDLE**: Waiting for query
2. **SEARCHING**: Fetching web sources (Serper API)
3. **EXTRACTING**: LLM-based claim extraction (parallel processing)
4. **SCORING**: Hybrid credibility evaluation
5. **VALIDATING**: Batch validation for low-medium scores
6. **DECIDING**: LLM determines final actions
7. **REPORTING**: LLM-generated comprehensive report
8. **UPDATING**: Incremental research with LLM-guided strategy

### Credibility Scoring Flow:
```
Claim → Source Classification (tools.py)
  ↓
Base Score (source weight × 10)
  ↓
Heuristic Analysis (credibility.py)
  ├─ Promotional Detection (-1.5 per pattern, max -4)
  ├─ Absolute Language (-0.7 per word, max -3)
  ├─ Self-Interest Detection (-3.0 to -5.0)
  └─ Evidence Bonus (+1.0 to +4.0)
  ↓
LLM Decision (needs_deep_analysis?)
  ├─ High (>7.5) or Low (<3.5): Skip deep analysis
  ├─ Borderline (3.5-7.5): Deep analysis required
  └─ Conflicting signals: Deep analysis required
  ↓
If Deep Analysis:
  └─ LLM Bias Detection → Adjustment (-4.0 to +2.0)
  ↓
Final Score (0-10, clamped)
  ↓
Validation (if score < 4.5)
  └─ Cross-reference with search evidence
  └─ LLM verdict: SUPPORTS/CONTRADICTS/NEUTRAL
  └─ Score adjustment (-4.0 to +2.0)
  ↓
LLM Final Action Decision
  ├─ INCLUDE (≥7.5)
  └─ WARN (4.5-7.4)
```
## 🎯 Goals & KPIs

### Primary Goals:
1. **Accuracy**: >80% of included claims should be verifiable
2. **Efficiency**: <60s for initial research, <20s for updates
3. **Reliability**: Average credibility score >6.5/10
4. **Source Diversity**: ≥3 different source types per research
5. **Update Efficiency**: <30% overhead vs full research

### Measurable KPIs:

| KPI | Target | Implementation |
|-----|--------|----------------|
| Avg Credibility Score | ≥6.5 | `_calc_avg(claims)` in agent.py |
| High-Cred Ratio | ≥60% | Claims with score ≥7.5 |
| Processing Time | <60s | Tracked via `time.time()` |
| Update Overhead | <30% | `overhead_ratio` calculation |
| Source Diversity | ≥3 types | `classify_source()` tracking |
| Cache Hit Rate | ≥40% | TTLCache in credibility & agent |
| Parallel Efficiency | ≥50% speedup | ThreadPoolExecutor usage |

### Performance Metrics Tracked:
- **research_time**: Initial research duration
- **update_time**: Incremental update duration
- **overhead_ratio**: Update time / research time
- **sources_count**: Number of sources analyzed
- **overall_credibility**: Weighted average of included claims

## 🚨 Edge Cases Handled

### 1. Conflicting Claims
**Scenario**: New source contradicts existing high-credibility claim  
**Solution**: LLM reconciliation with `RECONCILIATION_PROMPT`, prioritizes highest credibility score

### 2. Biased High-Authority Source
**Scenario**: .edu domain but funded by interested party  
**Solution**: 
- `_detect_self_interest()` applies -3.5 penalty for 'sponsored'
- LLM bias detection overrides source weight bonus
- Adjustment range: -4.0 to +2.0

### 3. Context Ambiguity
**Scenario**: Unclear if CEO statement is self-promotional  
**Solution**: 
- `VALIDATION_DECISION_PROMPT` triggers deep analysis for borderline scores
- LLM evaluates context with confidence scoring
- Conservative fallback if parsing fails

### 4. No Web Access
**Scenario**: Serper API fails or SERPER_API_KEY not set  
**Solution**: 
- `_mock_search()` provides fallback data
- Warning message in config setup
- Graceful degradation with mock academic/news/corporate/commercial sources

### 5. Malformed Claims
**Scenario**: LLM returns invalid JSON  
**Solution**: 
- Try-except blocks with fallback to sentence splitting
- Basic scoring applied (source weight only)
- Logged for debugging, no crash

### 6. Update Conflicts
**Scenario**: New file has 100% contradictory claims  
**Solution**: 
- `UPDATE_ANALYSIS_PROMPT` evaluates conflict percentage
- >25% conflicts triggers 'regenerate' strategy
- `_smart_merge()` keeps both, user sees reasoning
- Higher credibility scores prioritized in report

### 7. Source Classification Failure
**Scenario**: Unknown domain type  
**Solution**: 
- Default to 'corporate' (0.5 weight)
- Maintains system stability
- Prevents zero-score edge case

### 8. Cache Expiry During Update
**Scenario**: Cache TTL expires between research and update  
**Solution**:
- 7200s (2 hour) TTL sufficient for typical workflows
- Cache miss triggers re-research with warning
- User can re-run initial research if needed

## 💰 Strategy Review

### Scaling Strategy

#### Phase 1: Single Instance (Current)
- **Handles**: ~100 requests/day
- **Cost**: ~$15/month (Gemini Flash + Serper API)
- **Infrastructure**: Single Streamlit instance
- **Cache**: In-memory TTLCache (7200s)

#### Phase 2: Horizontal Scaling (Month 2-3)
- **Add**: Redis cache (60% API call reduction)
- **Add**: PostgreSQL (persist research history)
- **Add**: Nginx load balancer
- **Handles**: ~10K requests/day
- **Cost**: ~$150/month
- **Deploy**: Docker Compose

#### Phase 3: Microservices (Month 4-6)
```
┌─────────────┐
│   API GW    │
│  (FastAPI)  │
└──────┬──────┘
       │
   ┌───┴────┬────────┬─────────┬──────────┐
   ▼        ▼        ▼         ▼          ▼
Search  Extract  Score   Validate  Report
Service Service Service  Service   Service
(Serper) (LLM)  (Hybrid)  (LLM)    (LLM)
   │        │        │         │          │
   └────────┴────────┴─────────┴──────────┘
              ▼
    Redis Cache + PostgreSQL
         (Persistent Storage)
```
- **Handles**: ~100K requests/day
- **Cost**: ~$600/month
- **Deploy**: Kubernetes (GKE/EKS)

#### Phase 4: Enterprise (Month 7+)
- Multi-region deployment (US, EU, Asia)
- Custom fine-tuned models
- White-label options
- **Handles**: ~1M requests/day
- **Cost**: ~$2.5K/month

### Cost Optimization

1. **Intelligent Caching** (60% API reduction)
   - `TTLCache` for claims (credibility.py)
   - `TTLCache` for research results (agent.py)
   - Redis for distributed caching
   - Cache source classifications

2. **Batch Processing** (50% time reduction)
   - `batch_validate_claims()` groups API calls
   - `ThreadPoolExecutor` for parallel extraction
   - Max 10 concurrent requests (PERFORMANCE_CONFIG)

3. **Smart LLM Usage**
   - Heuristics filter 40% of claims from deep analysis
   - Only borderline scores (3.5-7.5) get LLM bias detection
   - Validation only for scores <4.5
   - Estimated savings: 55% of LLM calls

4. **Model Selection**
   - Gemini Flash (cheaper, fast): Scoring & extraction
   - Llama 3.3 70B via Groq: Alternative with free tier
   - Temperature 0.2: Consistent, deterministic outputs

### Current API Usage Estimates:
- **Per Research** (10 sources):
  - Search: 1 Serper call ($0.002)
  - Extraction: 8 LLM calls ($0.008)
  - Scoring: ~5 deep analysis calls ($0.005)
  - Validation: ~3 calls + 3 search ($0.009)
  - Report: 1 LLM call ($0.002)
  - **Total**: ~$0.026/research

- **Per Update**:
  - Extraction: 1 LLM call ($0.001)
  - Scoring: ~2 calls ($0.002)
  - Strategy: 1 LLM call ($0.001)
  - Reconcile: 1 LLM call ($0.001)
  - Report: 1 LLM call ($0.002)
  - **Total**: ~$0.007/update

### Monetization

#### Pricing Tiers:

**Free Tier** ($0/month)
- 10 researches/month
- Basic credibility scoring (heuristics only)
- Standard reports
- Community support (GitHub issues)

**Pro Tier** ($29/month)
- Unlimited researches
- Full LLM-based validation
- Advanced bias detection
- Priority processing (dedicated queue)
- Email support (24h response)
- API access (1K calls/month)
- Export reports (MD/PDF)

**Team Tier** ($99/month)
- Everything in Pro
- 5 team members
- Shared research library
- 10K API calls/month
- Custom source weights
- Slack/Teams integration
- Priority support (4h response)

**Enterprise** (Custom pricing)
- Dedicated infrastructure
- White-label option
- Custom integrations (Salesforce, HubSpot)
- SLA guarantees (99.9% uptime)
- Unlimited API calls
- On-premise deployment
- Custom model fine-tuning
- 24/7 phone support

#### Revenue Projections:

| Month | Free Users | Pro | Team | Enterprise | MRR | Costs | Profit |
|-------|-----------|-----|------|------------|-----|-------|-------- |
| 1-3   | 500       | 20  | 2    | 0          | $778| $500  | $278    |
| 4-6   | 2000      | 100 | 10   | 1          | $4.4K| $1.5K | $2.9K  |
| 7-12  | 5000      | 300 | 30   | 5          | $19K | $5K   | $14K   |
| 13-18 | 10000     | 700 | 80   | 15         | $58K | $15K  | $43K   |


## 📈 Performance Optimization

### Current Performance:
- **Initial research**: 45-60s (depends on Serper latency)
- **Update with file**: 10-20s (75% faster)
- **Credibility scoring**: <1s per claim (heuristics + selective LLM)
- **Report generation**: 5-10s (LLM processing)
- **Cache hit rate**: ~40% (TTL 7200s)

### Future Optimizations:

1. **Model Optimization**
   - Fine-tune Gemini Flash on credibility tasks
   - Reduce temperature to 0.1 for consistency
   - Use streaming for long reports

2. **Database Layer**
   - PostgreSQL for persistent storage
   - Index on (topic, timestamp)
   - Materialized views for common queries

3. **Advanced Caching**
   - Redis cluster for distributed cache
   - Cache warming on popular topics
   - Predictive pre-caching

4. **Query Optimization**
   - Debounce research requests (prevent duplicates)
   - Query de-duplication
   - Smart query expansion

## 🔒 Security Considerations

1. **API Key Protection**
   - Environment variables only (`.env` file)
   - Never logged or exposed in UI
   - Rotation every 90 days

2. **Input Validation**
   - File upload type checking 
   - File size limits (10MB max)
   - Content sanitization (no code execution)

3. **Rate Limiting**
   - Per-user request limits (free: 10/month)
   - IP-based rate limiting (100/hour)
   - API key throttling (1K/month for Pro)

4. **Data Privacy**
   - No PII stored
   - Research results cached temporarily (2h TTL)
   - User can clear cache on demand

5. **Error Handling**
   - No sensitive data in error messages
   - Graceful degradation (fallbacks)
   - Logged errors sanitized


## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/research-agent
cd research-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env
# Edit .env with your API keys
```

### Running the Application
```bash
# Start Streamlit app
streamlit run app.py

# Open browser at http://localhost:8501
```

### Usage Flow
1. **Select LLM**: Choose Gemini or Groq model
2. **Enter Topic**: Type research query (e.g., "AI Ethics")
3. **Start Research**: Click "🔍 Start Research"
4. **View Report**: Review generated report with credibility scores
5. **Update (Optional)**: Upload .txt/.pdf/.docx file to add new information
6. **Download**: Export report as Markdown

## 📝 Dependencies

```txt
langchain                # LLM orchestration
langchain-google-genai   # Gemini integration
langchain-groq           # Groq integration
google-generativeai      # Gemini API
groq                     # Groq API
python-dotenv            # Environment variables
requests                 # HTTP requests (Serper)
streamlit                # Web UI
cachetools               # TTL caching
```

## 📄 License

MIT License - see LICENSE file for details

