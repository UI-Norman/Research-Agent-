import os
import requests
from langchain.prompts import PromptTemplate
from urllib.parse import urlparse
import json

def search_web(query, num_results=10):
    """Search web using Serper API"""
    api_key = os.getenv('SERPER_API_KEY')
    if not api_key:
        print("⚠️ SERPER_API_KEY not set, using mock data")
        return _mock_search(query)
    
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "q": query,
        "num": num_results
    })
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('organic', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'content': item.get('snippet', ''),
                'source_type': _classify_source(item.get('link', ''))
            })
        
        return results
    except Exception as e:
        print(f"⚠️ Search error: {e}. Using mock data.")
        return _mock_search(query)

def _classify_source(url):
    """Classify source type from URL"""
    domain = urlparse(url).netloc.lower()
    
    if any(x in domain for x in ['.edu', '.ac.', 'scholar', 'arxiv', 'pubmed']):
        return 'academic'
    elif any(x in domain for x in ['.gov', '.mil']):
        return 'government'
    elif any(x in domain for x in ['reuters', 'apnews', 'bbc', 'nytimes', 'wsj']):
        return 'news'
    elif any(x in domain for x in ['blog', 'medium', 'wordpress']):
        return 'blog'
    elif any(x in domain for x in ['twitter', 'facebook', 'instagram', 'reddit']):
        return 'social'
    elif any(x in domain for x in ['shop', 'buy', 'store', 'product']):
        return 'commercial'
    else:
        return 'corporate'

def extract_claims(content, source, llm):
    """Extract individual claims from content"""
    prompt = PromptTemplate(
        template="""Extract factual claims from this text. Return JSON list.

Text: {content}

Extract clear, specific claims. Return format:
[{{"text": "claim text", "context": "surrounding context"}}]

Max 10 claims. Focus on verifiable facts.""",
        input_variables=["content"]
    )
    
    try:
        result = llm.invoke(prompt.format(content=content[:2000]))
        claims_data = json.loads(result.content)
        
        # Add source info
        for claim in claims_data:
            claim['source'] = source
            claim['source_type'] = _classify_source(source) if source.startswith('http') else 'document'
        
        return claims_data
    except:
        # Fallback: simple sentence splitting
        sentences = content.split('.')[:10]
        return [{
            'text': s.strip(),
            'context': content[:200],
            'source': source,
            'source_type': _classify_source(source) if source.startswith('http') else 'document'
        } for s in sentences if len(s.strip()) > 20]

def _mock_search(query):
    """Mock search results for testing"""
    return [
        {
            'title': f'Academic Study on {query}',
            'url': 'https://scholar.google.com/study1',
            'content': f'Research shows that {query} has significant implications. Independent peer-reviewed study with 1000+ participants.',
            'source_type': 'academic'
        },
        {
            'title': f'News Report: {query}',
            'url': 'https://reuters.com/article1',
            'content': f'According to experts, {query} is a developing topic. Data shows mixed results across studies.',
            'source_type': 'news'
        },
        {
            'title': f'Company Blog: {query}',
            'url': 'https://company.com/blog/post1',
            'content': f'Our revolutionary approach to {query} is the best solution available. We guarantee amazing results.',
            'source_type': 'blog'
        },
        {
            'title': f'CEO Interview: {query}',
            'url': 'https://company.com/ceo-interview',
            'content': f'I am an expert in {query}. Our company always delivers perfect solutions. We never fail.',
            'source_type': 'corporate'
        },
        {
            'title': f'Government Report on {query}',
            'url': 'https://gov.example/report',
            'content': f'Official data indicates that {query} affects 15% of the population. Study conducted over 5 years.',
            'source_type': 'government'
        }
    ]