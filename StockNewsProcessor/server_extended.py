# -*- coding: utf-8 -*-
from flask import Flask, request
import requests
from StockMarket import StockPortfolio
 
app = Flask(__name__)

ACCESS_TOKEN = "EAAcCbEp6ZBLoBAHcxaDU15sFrax4SSOcsiUHWZAR9SZCUOChnlHUXhGPCUZBFp6ZBmZCAOvnwq84iYW3aqIs92IF8L53c7ZA4guBDTy0WgbCC6rzQuQLS5enidfMMZA0f4p3c5gZBTQBhwqx7MlTKekZAmLx6GHYuGBUShRr406YcwdgZDZD"
VERIFY_TOKEN = "secret"

s = []
sm = StockPortfolio(s,None,None,None)
news, stock,historical = sm.refresh_portfolio()

def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)


@app.route('/', methods=['GET'])
def handle_verification():
    if request.args['hub.verify_token'] == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return "Invalid verification token"


@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']['text']
    #if message.lower()=='y' or message.lower()=='yes':
    print type(message)
    reply(sender, 'badass')
    if (sm.check_symbol_is_valid(message.upper().strip())):
        symbol = message.upper()
        answer = "what would you like to do for this stock? \
        0) Add it to your portfolio? 1)News, 2)Data, 3)News and Data, or 4)Real Time Stats for this stock?"
        news = 'news'
        data = 'data'
        stats = 'stats'
        reply(sender, answer)
    elif message.lower().strip() == "add" or message==0 or message.lower.strip()=="portfolio":
        reply(sender,symbol + ' was added to your portfolio')
    elif message.lower().strip() == "news" or message==1:
        reply(sender, news)
    elif message.lower().strip() == "data" or message == 2:
        reply(sender, data)
    elif message.lower().strip() == "news and data" or message.lower().strip() == "news&data" or message.lower().strip() == "3":
        reply(sender, news)
        reply(sender, data)
    elif message.lower().strip() == "daily stats" or message.lower().strip() == "4" or message.lower().strip() == "stats" or message.lower().strip() == "real time stats":
        reply(sender,stats)
    else:
        reply(sender,'please enter valid input')

    return "ok"


if __name__ == '__main__':
    app.run(debug=True)