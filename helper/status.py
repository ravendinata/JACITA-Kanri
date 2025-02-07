import json

def get_status(code):
    with open('helper/status.json') as f:
        data = json.load(f)
        return { 'status': data[code].get('status'), 'message': data[code].get('message')}