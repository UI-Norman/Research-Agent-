import os
import requests
import json
from urllib.parse import urlparse
from system_prompts import CLAIM_EXTRACTION_PROMPT
from concurrent.futures import ThreadPoolExecutor

def search_web(query, num_results=10):
    api_key = os.getenv('SERPER_API_KEY')
    if not api_key:
        return _mock_search(query)
    
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
            json={"q": query, "num": num_results},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('organic', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'content': item.get('snippet', ''),
                'source_type': classify_source(item.get('link', ''))
            })
        return results
    except:
        return _mock_search(query)

def classify_source(url):
    domain = urlparse(url).netloc.lower()
    if any(x in domain for x in ['.edu', '.ac.', 'scholar', 'arxiv', 'pubmed', 'researchgate']):
        return 'academic'
    if any(x in domain for x in ['.gov', '.mil', 'who.int', 'europa.eu']):
        return 'government'
    if any(x in domain for x in ['reuters', 'apnews', 'bbc', 'nytimes', 'wsj', 'economist']):
        return 'news'
    if any(x in domain for x in ['blog', 'medium.com', 'wordpress', 'substack']):
        return 'blog'
    if any(x in domain for x in ['twitter', 'facebook', 'instagram', 'reddit', 'tiktok']):
        return 'social'
    if any(x in domain for x in ['shop', 'buy', 'store', 'product', 'amazon']):
        return 'commercial'
    return 'corporate'

def extract_claims(content, source, llm):
    try:
        prompt = CLAIM_EXTRACTION_PROMPT.format(content=content[:3000])
        result = llm.invoke(prompt)
        claims_data = json.loads(result.content)
        for claim in claims_data:
            claim['source'] = source
            claim['source_type'] = classify_source(source) if source.startswith('http') else 'document'
            claim['source_context'] = content[:200]
        return claims_data[:12]
    except:
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 30]
        return [{
            'text': sent,
            'context': content[:200],
            'potential_bias': 'unknown',
            'verifiable': True,
            'importance': 'medium',
            'source': source,
            'source_type': classify_source(source) if source.startswith('http') else 'document',
            'source_context': content[:200]
        } for sent in sentences[:12]]

def validate_with_search(claim, serper_key=None):
    if not serper_key:
        return "No evidence available"
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={'X-API-KEY': serper_key, 'Content-Type': 'application/json'},
            json={"q": claim[:100], "num": 5},
            timeout=5
        )
        results = response.json().get('organic', [])
        return "\n".join([f"- {r.get('snippet', '')} ({classify_source(r.get('link', ''))})" for r in results[:5]])
    except:
        return "Validation failed"

def batch_validate_claims(claims, serper_key):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda c: validate_with_search(c, serper_key), claims))
    return results

def _mock_search(query):
    return [
        {
            'title': f'Study: {query}',
            'url': 'https://scholar.google.com/1',
            'content': f'Independent research on {query} with 3,000 participants shows significant results.',
            'source_type': 'academic'
        },
        {
            'title': f'News: {query}',
            'url': 'https://reuters.com/1',
            'content': f'Experts report {query} development. Data shows 20% growth.',
            'source_type': 'news'
        },
        {
            'title': f'CEO: {query}',
            'url': 'https://company.com/blog',
            'content': f'Our innovative {query} solution leads the industry.',
            'source_type': 'corporate'
        },
        {
            'title': f'Ad: {query}',
            'url': 'https://shop.com/product',
            'content': f'Buy the ultimate {query}! Limited offer.',
            'source_type': 'commercial'
        }
    ]