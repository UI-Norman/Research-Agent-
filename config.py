import os
from dotenv import load_dotenv

def setup_environment():
    """Load environment variables and validate configuration"""
    load_dotenv()
    
    # Required API keys
    gemini_key = os.getenv('GOOGLE_API_KEY')
    serper_key = os.getenv('SERPER_API_KEY')
    
    if not gemini_key:
        print("⚠️ WARNING: GOOGLE_API_KEY not set!")
        print("Get it from: https://makersuite.google.com/app/apikey")
        print("Set it: export GOOGLE_API_KEY='your-key'\n")
    
    if not serper_key:
        print("⚠️ WARNING: SERPER_API_KEY not set (optional)")
        print("Get it from: https://serper.dev/")
        print("Set it: export SERPER_API_KEY='your-key'")
        print("Will use mock data for testing.\n")
    
    return {
        'gemini_key': gemini_key,
        'serper_key': serper_key
    }

# Credibility thresholds
CREDIBILITY_THRESHOLDS = {
    'HIGH': 7.0,
    'MEDIUM': 4.0,
    'LOW': 0.0
}

# KPIs to track
KPIS = {
    'avg_credibility_score': 'Average credibility across all claims',
    'high_credibility_ratio': 'Percentage of high-credibility claims',
    'sources_diversity': 'Number of unique source types',
    'processing_time': 'Time to complete research',
    'update_overhead': 'Additional time for updates vs full research'
}