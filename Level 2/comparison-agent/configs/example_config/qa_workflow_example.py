import requests
import json

url = 'https://platform.gensee.ai/execute/serve'
data = {
    'workflow_id':
        '[Fill in Workflow ID from launch page for QA example]',
    'workflow_secret':
        '[Fill in Workflow Secret from launch page]',
    'workflow_input': {
        'question': 'Question to test',
    }
}

response = requests.post(url, json=data)
