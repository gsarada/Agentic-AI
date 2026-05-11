import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from joblib import Parallel, delayed
from anthropic import Anthropic

load_dotenv()
models_key_list = [#{'name': 'openai', 'key': None, 'base_url': None, 'model_name': 'gpt-5-mini'},
                   #{'name': 'anthropic', 'model_name': 'claude-sonnet-4-5'},
                   #{'name': 'gemini', 'key': 'GOOGLE_API_KEY', 'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/', 'model_name': 'gemini-2.5-flash'},
                   #{'name': 'deepseek', 'key': 'OLLAMA_API_KEY', 'base_url': 'https://ollama.com/api', 'model_name': 'deepseek-v3.2:cloud'},
                   {'name': 'groq', 'key': 'GROQ_API_KEY', 'base_url': 'https://api.groq.com/openai/v1', 'model_name': 'openai/gpt-oss-120b'},
                   {'name': 'ollama-local', 'key': 'OLLAMA', 'base_url': 'http://localhost:11434/v1/', 'model_name': 'llama3.2'}]
def get_model(name):
    if name == 'anthropic':
        model = Anthropic()
    else:
        api_key = next((item['key'] for item in models_key_list if item['name'] == name), None)
        if api_key:
            api_key = os.getenv(api_key)
        base_url = next((item['base_url'] for item in models_key_list if item['name'] == name), None)
        model = OpenAI(api_key=api_key, base_url=base_url)
    return model

def invoke_model(name, messages):
    model_name = next((item['model_name'] for item in models_key_list if item['name'] == name), None)
    print(f'Invoking Model - {model_name}')
    try:
        model = get_model(name)
        if name == 'anthropic':
            response = model.messages.create(model=model_name, messages=messages, max_tokens=1000)
            answer = response.content[0].text
        else:
            response = model.chat.completions.create(model=model_name, messages=messages)
            answer = response.choices[0].message.content
    except Exception as e:
        print(f'Exception {e} has occured')
        answer = ''

    return answer


def get_question(name):
    request = "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. "
    request += "Answer only with the question, no explanation."
    messages = [{"role": "user", "content": request}]
    question = invoke_model(name, messages)
    return question

def judge_answers(name, question, responses):
    judge = f"""You are judging a competition between {len(models_key_list)} competitors.
    Each model has been given this question:
    
    {question}
    
    Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
    Respond with JSON, and only JSON, with the following format:
    {{"results": ["best competitor number", "second best competitor number", "third best competitor number", ...]}}
    
    Here are the responses from each competitor:
    
    {responses}
    
    Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""

    judge_messages = [{"role": "user", "content": judge}]
    results = invoke_model(name, judge_messages)
    results_dict = json.loads(results)
    ranks = results_dict["results"]
    return ranks

def parallel_workflow(question_generator, judging_model):
    question = get_question(question_generator)
    #question = 'Why is the sky blue'
    print(f'Question is {question}')
    answers = []
    together = ''
    messages = [{"role": "user", "content": question}]
    answers = Parallel(n_jobs=-1)(delayed(invoke_model)(m['name'], messages) for m in models_key_list)
    for index, answer in enumerate(answers):
        together += f"# Response from competitor {index+1}\n\n"
        together += answer + "\n\n"
    ranks = judge_answers(judging_model, question, together)
    print(ranks)
    print(f'Best Model - {models_key_list[int(ranks[0])-1]["name"]}')
    answer = answers[int(ranks[0])-1]
    return question, answer


if __name__ == "__main__":
    question_generator = 'groq'
    judging_model = 'groq'
    question, answer = parallel_workflow(question_generator, judging_model)
    print(f'The question generated is: \n {question}\n\n and the best answer is: \n {answer}')
