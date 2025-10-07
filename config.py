import os
from dotenv import load_dotenv

def setup_environment():
    load_dotenv()
    config = {
        'gemini_key': os.getenv('GOOGLE_API_KEY'),
        'serper_key': os.getenv('SERPER_API_KEY'),
        'groq_key': os.getenv('GROQ_API_KEY'),
    }
    available_llms = []
    if config['gemini_key']:
        available_llms.append('gemini')
    if config['groq_key']:
        available_llms.append('groq')
    
    if not available_llms:
        print("❌ ERROR: No LLM API keys found!")
        exit(1)
    
    if not config['serper_key']:
        print("⚠️ SERPER_API_KEY not set - using mock data")
    
    config['available_llms'] = available_llms
    return config

CREDIBILITY_PARAMS = {
    "thresholds": {"high": 7.5, "medium": 4.5, "low": 0.0},
    "validation_required": 4.5,
    "auto_exclude": 3.0,
    "max_claims_per_source": 12,
    "update_merge_strategy": "highest_credibility"
}

PERFORMANCE_CONFIG = {
    "cache_ttl": 7200,
    "batch_size": 10,
    "parallel_validation": True,
    "incremental_update": True,
    "max_concurrent_requests": 10
}

LLM_CONFIGS = {
    'gemini': {
        'model': 'gemini-2.5-flash',
        'temperature': 0.2,
        'display_name': 'Gemini 2.5 Flash'
    },
    'groq': {
        'models': {
            'llama-3.3-70b-versatile': 'llama-3.3-70b-versatile'
        },
        'temperature': 0.2
    }
}