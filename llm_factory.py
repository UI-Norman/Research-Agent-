from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from config import LLM_CONFIGS
import os

class LLMFactory:
    @staticmethod
    def create_llm(provider, model_name=None):
        if provider == 'gemini':
            return ChatGoogleGenerativeAI(
                model=LLM_CONFIGS['gemini']['model'],
                temperature=LLM_CONFIGS['gemini']['temperature'],
                google_api_key=os.getenv('GOOGLE_API_KEY'),
                max_output_tokens=4096
            )
        elif provider == 'groq':
            if not model_name:
                model_name = 'llama-3.3-70b-versatile'
            return ChatGroq(
                model=model_name,
                temperature=LLM_CONFIGS['groq']['temperature'],
                groq_api_key=os.getenv('GROQ_API_KEY'),
                max_tokens=4096
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @staticmethod
    def get_available_models(config):
        models = []
        if 'gemini' in config['available_llms']:
            models.append({
                'provider': 'gemini',
                'model': 'gemini-2.5-flash',
                'display': LLM_CONFIGS['gemini']['display_name']
            })
        if 'groq' in config['available_llms']:
            for model_id, display_name in LLM_CONFIGS['groq']['models'].items():
                models.append({
                    'provider': 'groq',
                    'model': model_id,
                    'display': f'Groq - {display_name}'
                })
        return models