import os
import json
import re
from openai import OpenAI
import anthropic
import astor
# Set up your OpenAI and Anthropic API keys
anthropic.api_key = 'your_anthropic_api_key'
project_path = '/mnt/c/camline/source/git/CodeToLlm/example'
model = 'gpt-3.5-turbo'
# Output JSON file
output_json_file = 'react_code_dataset.json'

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def extract_code_snippets(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # code_snippets = re.findall(r'```([\s\S]*?)```', content)
        return content.strip()

def generate_user_role(code_snippet, model):
    prompt = f"Given the following code snippet:\n\n```{code_snippet}```\n\nHow would a user typically ask a question about this code?"
    print(prompt)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    print(response)
    user_role = response.choices[0].message.content.strip()
    return user_role

def generate_assistant_role(code_snippet, model):
    prompt = f"Given the following code snippet:\n\n{code_snippet}\n\nHow would an AI assistant typically explain this code?"
    print(prompt)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    print(response)
    assistant_role = response.choices[0].message.content.strip()
    return assistant_role


def create_dataset(code_snippets, model) :
    dataset = []
    
    user_role = generate_user_role(code_snippets, model)
    assistant_role = generate_assistant_role(code_snippets, model)
        
    dataset.append({
        'role': 'user',
        'content': user_role
    })
    dataset.append({
        'role': 'assistant',
        'content': assistant_role
    })
    
    return dataset

def process_directory(directory, model):
    dataset = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.ts') or file.endswith('.tsx'):
                file_path = os.path.join(root, file)
                print("processing..." + file_path)
                code_snippets = extract_code_snippets(file_path)
                dataset.extend(create_dataset(code_snippets, model))
    
    return dataset


def extract_code_and_comments(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regular expression to find component-like structures
    components = content # re.findall(r'/\*\*(.*?)\*/\s*(const|function|class) (\w+) = (.*?);', content, re.DOTALL)
    
    data = []
    for comment, _, func_name, code in components:
        # Clean and format the comment
        user_prompt = ' '.join(comment.strip().split())
        assistant_content = f"{func_name} = {code};"

        data.append({"role": "user", "content": user_prompt})
        data.append({"role": "assistant", "content": assistant_content})
    
    return data

def scan_directory(path):
    dataset = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(('.ts', '.tsx')):
                full_path = os.path.join(root, file)
                extracted_data = extract_code_and_comments(full_path)
                dataset.extend(extracted_data)
    
    return dataset

def save_to_json(data, output_file):
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)



# Process the project directory
dataset = process_directory(project_path, model)
# Save the dataset to a JSON file
save_to_json(dataset, output_json_file)

print(f"Dataset created with {len(dataset)//2} entries.")

 