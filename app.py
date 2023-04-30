import os
import json
import uuid
import traceback
from redis import Redis
from rq import Queue

import requests
from flask import Flask, jsonify, request
from faqbot import FAQBot

import settings

app = Flask(__name__)
app.debug = True

def enqueue(func, *args):
    q = Queue(connection=Redis())
    return q.enqueue(func, *args)


def get_uuid():
    return str(uuid.uuid4())

def error(data):
    data['status'] = 'error'
    print(data)
    return jsonify(data), 500

def denied(data):
    data['status'] = 'denied'
    data['error']: 'Access denied'
    print(data)
    return jsonify(data), 403

def success(data):
    data['status'] = 'success'
    print(data)
    return jsonify(data), 200

@app.route('/')
def index():
    api_id = get_uuid()
    return success({'api_id': api_id,
                    'message': 'Welcome to Plivo FAQBot API'})

@app.route('/ask', methods=['POST'])
def ask_bot():
    api_id = get_uuid()
    question = ''
    try:
        if request.method == 'POST':
            print({'api_id': api_id, 'message': str(request.form)})
            try:
                token_id = request.form['token']
            except KeyError:
                return denied({'api_id': api_id})
            if token_id != settings.SLACK_TOKEN_ID:
                return denied({'api_id': api_id})
            cmd = request.form['command']
            if cmd != '/askplivo':
                return error({'api_id': api_id,
                              'error': 'Invalid command'})
            question = request.form['text']
            response_url = request.form['response_url']
        else:
            return error({'api_id': api_id,
                          'error': 'Invalid request method'})
    except KeyError:
        return error({'api_id': api_id,
                      'error': 'Invalid request, no question provided'})
    question = question.strip()
    if not question:
        return error({'api_id': api_id,
                      'error': 'Invalid request, question is empty'})

    print({'api_id': api_id, 'question': question, 'response_url': response_url, 'message': 'Processing your question, please wait...'})
    enqueue(ask_bot_async, api_id, question, response_url)
    print({'api_id': api_id, 'message': f"started background job ask_bot_async"})
    
    return jsonify({
            "response_type": "in_channel",
            "text": f"_Processing your question, please wait..._\n*TicketID*: {api_id}\n"
    }), 200

def ask_bot_async(api_id, question, response_url):
    bot = None
    try:
        print({'api_id': api_id, 'question': question, 'response_url': response_url, 'message': 'started ask_bot_async'})
        print({'api_id': api_id, 'question': question, 'response_url': response_url, 'message': 'creating bot instance'})
        bot = FAQBot()
        bot.set_debug(True)
        print({'api_id': api_id, 'question': question, 'response_url': response_url, 'message': 'created bot instance'})
        result = bot.ask(question=question)
        print({'api_id': api_id, 'question': question, 'response_url': response_url, 'message': 'got result from bot'})
        data = json.loads(result)
        if data['status'] == 'error':
            data['api_id'] = api_id
            print(data)
            json_response = {
                "text": f"Oops, something went wrong: {data['error']}\n*TicketID*: {api_id}\n",
                "response_type": "in_channel"
            }
            print({'api_id': api_id, 'slack_response': json_response})
            r = requests.post(response_url, json=json_response)
            print(api_id, response_url, r.status_code)
            return
        elif data['status'] == 'success':
            stats = data['response']['stats']
            print({'api_id': api_id, 'stats': stats})
            # format code block for Slack
            _answer = data['response']['answer']
            answer = ''
            for line in _answer.split('\n'):
                if line.startswith('```'):
                    answer += line[:3] + '\n'
                else:
                    answer += line + '\n'
            # format sources for Slack
            sources = '\n'.join(' - '+ src for src in data['response']['sources'])
            # send response to slack
            json_response = {
                "text": f"*Question*: _{question}_\n*Answer*\n{answer}\n*Sources*\n{sources}\n*TicketID*: {api_id}\n",
                "response_type": "in_channel"
            }
            print({'api_id': api_id, 'slack_response': json_response})
            r = requests.post(response_url, json=json_response)
            print(api_id, response_url, r.status_code)
            return
    except Exception as e:
        print({'api_id': api_id, 'error': str(e), 'message': traceback.format_exc()})
        pass
    finally:
        del bot

    json_response = {"text": f"Oops, something went wrong: {str(e)}\n*TicketID*: {api_id}\n", "response_type": "in_channel"}
    print({'api_id': api_id, 'slack_response': json_response})
    r = requests.post(response_url, json=json_response)
    print(api_id, response_url, r.status_code)
    return



if __name__ == "__main__":
    app.run(debug=True)
