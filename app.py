import json
import uuid
import traceback
from flask import Flask, jsonify, request
from faqbot import FAQBot

app = Flask(__name__)
app.debug = True
bot = FAQBot()
bot.set_debug(True)


def error(data):
    data['status'] = 'error'
    print(data)
    return jsonify(data), 500

def success(data):
    data['status'] = 'success'
    print(data)
    return jsonify(data), 200

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/ask', methods=['GET', 'POST'])
def ask_bot():
    api_id = str(uuid.uuid4())
    question = None
    try:
        if request.method == 'POST':
            question = request.form['question']
        elif request.method == 'GET':
            question = request.args['question']
        else:
            return error({'api_id': api_id,
                            'status': 'error', 
                            'error': 'Invalid request method'})
    except KeyError:
        return error({'api_id': api_id,
                        'status': 'error', 
                        'error': 'Invalid request, no question provided'})
    if not question:
        return error({'api_id': api_id,
                        'status': 'error', 
                        'error': 'Invalid request, question is empty'})
    
    print({'api_id': api_id, 'question': question})

    try:
        result = bot.ask(question=question)
        data = json.loads(result)
        if data['status'] == 'error':
            data['api_id'] = api_id
            print(data)
            return error(data)
        elif data['status'] == 'success':
            stats = data['response']['stats']
            print({'api_id': api_id, 'stats': stats})
            answer = data['response']['answer']
            sources = data['response']['sources']
            return success({'api_id': api_id,
                            'status': 'success', 
                            'answer': answer, 'sources': sources})
    except Exception as e:
        print({'api_id': api_id, 'error': str(e), 'traceback': traceback.format_exc()})

    return error({'api_id': api_id,
                    'status': 'error', 
                    'error': 'Unknown error'})


if __name__ == "__main__":
    app.run(debug=True)
