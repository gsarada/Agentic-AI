import os
from anthropic import Anthropic
from openai import AsyncOpenAI

models_key_list = [{'name': 'openai', 'key': None, 'base_url': None, 'model_name': 'gpt-5-mini'},
    {'name': 'anthropic', 'model_name': 'claude-sonnet-4-5'},
    {'name': 'gemini', 'key': 'GOOGLE_API_KEY', 'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/', 'model_name': 'gemini-3.1-flash-lite'},
    {'name': 'deepseek', 'key': 'OLLAMA', 'base_url': 'http://localhost:11434/v1/', 'model_name': 'deepseek-r1:8b'},
    {'name': 'groq', 'key': 'GROQ_API_KEY', 'base_url': 'https://api.groq.com/openai/v1', 'model_name': 'openai/gpt-oss-120b'},
    {'name': 'qwen', 'key': 'GROQ_API_KEY', 'base_url': 'https://api.groq.com/openai/v1', 'model_name': 'qwen/qwen3.6-27b'},
    {'name': 'groq-llama', 'key': 'GROQ_API_KEY', 'base_url': 'https://api.groq.com/openai/v1', 'model_name': 'llama-3.3-70b-versatile'},
    {'name': 'llama', 'key': 'OLLAMA', 'base_url': 'http://localhost:11434/v1/', 'model_name': 'llama3.2'}]

default_chat_model = "gemini"
default_eval_model = "groq"

def get_model(name):
    model_name = next((item['model_name'] for item in models_key_list if item['name'] == name), None)
    if name == 'anthropic':
        model = Anthropic()
    else:
        api_key = next((item['key'] for item in models_key_list if item['name'] == name), None)
        if api_key:
            api_key = os.getenv(api_key)
        base_url = next((item['base_url'] for item in models_key_list if item['name'] == name), None)
        model = AsyncOpenAI(api_key=api_key, base_url=base_url)
    return model, model_name
