# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 21:57:51 2017

@author: Isaac
"""

from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""

    resp = MessagingResponse().message("Hello, Mobile Monkey")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
