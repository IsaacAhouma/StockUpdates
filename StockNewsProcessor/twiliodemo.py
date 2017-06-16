# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 06:09:51 2017

@author: Isaac
"""

from __future__ import division
from StockMarket import StockPortfolio
import time
import urllib2
import fbchat
import pandas as pd
from twilio.rest import Client

# Find these values at https://twilio.com/user/account
account_sid = "AC8febe4d45f903125ae718a6bd6b05301"
auth_token = "c980b4b4fe0a13b6f469a852ac5bd935"
client = Client(account_sid, auth_token)
message = client.api.account.messages.create(to="+17788888732",
                                             from_="+12892748035",
                                             body="Hello there!")

destination_number = "+17788888732"
s = []
sm = StockPortfolio(s,client,destination_number,account_type='twilio')
news, stock,historical = sm.refresh_portfolio()
s = ['TSLA','SNAP']
sm = StockPortfolio(s,client,destination_number)
news, stock,historical = sm.refresh_portfolio()

def send_stats(destination_number,symbols=sm.symbols,extended=False,local=False,add_image=False):
    assert(type(symbols)==str or type(symbols)==list)
    if type(symbols)==str:
        symbols = [symbols]
    stats = sm.daily_price_stats(symbols=symbols)
    for symbol in symbols:
        if symbol.upper() not in sm.symbols:
            if local:
                answer = input(symbol.upper() + " is not in your portfolio. Would you like to add it to your portfolio?")
            else:
                msg = "Warning, " + symbol.upper() + " is not in your portfolio. Would you like to add it?"
                sent = client.api.account.messages.create(to=sm.owner,
                                             from_="+12892748035",
                                             body=msg)
                answer = 'y'
            if answer.lower() == 'y' or answer.lower() == 'yes':
                sm.symbols.append(symbol)
    for i in range(len(stats)):
        symbol = 'Company: ' + str(stats['symbol'][i])
        current_price = ' Current Price: ' + str(stats['current price'][i])
        change = ' Change: ' + str(stats['change'][i])
        previous_close_price = ' Previous Day Close Price: ' + str(stats['previous close price'][i])
        percentage_change = (float(stats['change'][i]) / float(stats['previous close price'][i])) * 100
        daily_max = ' Daily Max: ' + str(stats['daily max'][i]) 
        daily_min = ' Daily Min: ' + str(stats['daily min'][i])
        daily_average = ' Daily Average: ' + str(stats['daily average'][i])
        daily_spread = ' Daily Spread: ' + str(stats['daily spread'][i])
        daily_std = ' Daily Standard Deviation: ' + str(stats['daily standard deviation'][i])
        date = ' Last Updated: ' + str(stats['As of Date'][i])
        msg = symbol + current_price + change + previous_close_price + daily_average + daily_max + daily_min + date
        if extended:
            msg += daily_std + daily_spread
        if add_image:
            if float(percentage_change) > float(5):
                imgurl = "Guess-Up-Emoji-Hot-Chick.png"
            elif float(percentage_change) < float(5):
                imgurl = "cold.jpeg"
            else:
                imgurl = "cold.jpeg"
            message = client.api.account.messages.create(to=sm.owner,
                                             from_="+12892748035",
                                             body=msg,
                                             media_url=[
                                                   'https://demo.twilio.com/owl.png',
                                                   'https://demo.twilio.com/logo.png'])
        else:
            sent = client.api.account.messages.create(to=sm.owner,
                                             from_="+12892748035",
                                             body=msg)


def send_news(symbols=sm.symbols,extended=False,limit=1):
    assert(type(symbols)==str or type(symbols)==list)
    news = sm.get_latest_news_for_symbols(symbols,limit)
    for i in news.index:
        symbol = 'Company: ' + str(news['symbol'][i])
        headline = ' Headline: ' + str(news['headline'][i])
        source = ' Source: ' + str(news['source'][i]) 
        url = ' Link' + str(news['url'][i])
        date = ' Date: ' + str(news['date'][i])
        text = ' Text: ' + str(news['date'][i])
        msg = symbol + headline + date + source + urllib2.quote(url)
        if extended:
            msg +=   text + source
        sent = client.api.account.messages.create(to=sm.owner,
                                             from_="+12892748035",
                                             body=msg)


send_stats(sm.owner)
send_stats(sm.owner,add_image=True)
send_stats(sm.owner,symbols='FB')
send_news(symbols='FB')