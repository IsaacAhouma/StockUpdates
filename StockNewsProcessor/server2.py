# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 22:17:50 2017

@author: Isaac
"""

from flask import Flask, request
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAAcCbEp6ZBLoBANkNr9skqcyoLbv41fGwVkl2PZC6jhWAXchfKPGWU9unhTQ0lA1hzbc2s5yEYAQ8C4uYXDsZCypRM3bPZCkoVYLWrHszGaHquBxOyqodAZCgY1hikBTzY7P1kPyBm7ZBTAEcS0qbaFqmYT8SxyYzbzdInZA09ZAlwZDZD"


def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)


@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']['text']
    reply(sender, message[::-1])

    return "ok"


if __name__ == '__main__':
    app.run(debug=True)