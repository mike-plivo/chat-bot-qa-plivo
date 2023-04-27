from flask import Flask
import faqbot

app = Flask(__name__)
bot = FAQBot()
bot.set_debug(True)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/ask', methods=['POST'])
def ask_bot():
    return 'Hello, Bot!'


if __name__ == "__main__":
    app.run(debug=True)
