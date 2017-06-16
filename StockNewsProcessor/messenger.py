# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 20:30:21 2017

@author: Isaac
"""
from __future__ import division
from StockMarket import StockPortfolio
import time
import urllib2
import fbchat
import pandas as pd

tic = time.time()

email = pd.read_csv('email.csv').columns[0]
password = pd.read_csv('password.csv').columns[0]

client = fbchat.Client(email, password)

#user_account = "otis dogpaw jenkins"
user_account = "Isaac Ahouma"

friends = client.getUsers(user_account)
friend = friends[0]

s = []
sm = StockPortfolio(s,client,friend)
news, stock,historical = sm.refresh_portfolio()
s = ['TSLA','SNAP']
sm = StockPortfolio(s,client,friend.uid)
news, stock,historical = sm.refresh_portfolio()

#msg = 'Company: ' + str(stock['symbol'][0]) + ' ' + 'current price: ' + str(stock['current price'][0])

def send_stats(friend,symbols=sm.symbols,extended=False,local=False,add_image=False):
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
                sent = sm.client.send(sm.owner, msg)
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
            sent = client.sendLocalImage(friend.uid,message=msg, image=imgurl)
        else:
            sent = client.send(friend.uid, msg)

        
#sent = client.send(friend.uid, msg)

def send_news(friend,symbols=sm.symbols,extended=False,limit=1):
    assert(type(symbols)==str or type(symbols)==list)
    news = sm.get_latest_news_for_symbols(symbols,limit)
    for i in news.index:
        symbol = 'Company: ' + str(news['symbol'][i])
        headline = ' Headline: ' + str(news['headline'][i])
        source = ' Source: ' + str(news['source'][i]) 
        url = ' Link' + str(news['url'][i])
        date = ' Date: ' + str(news['date'][i])
        text = ' Text: ' + str(news['date'][i])
#        msg = symbol + headline + date + source + urllib.quote_plus(url)
        msg = symbol + headline + date + source + urllib2.quote(url)
        if extended:
            msg +=   text + source
        sent = client.send(friend.uid, msg)

send_stats(friend)
send_stats(friend,add_image=True)
send_stats(friend,symbols='FB')
send_news(friend)

#client.sendLocalImage(friend.uid,message='<message text>',image='<path/to/image/file>') # send local image
imgurl = "http://i.imgur.com/LDQ2ITV.jpg"
msg = 'yo'
client.sendRemoteImage(friend.uid,message=msg, image=imgurl) # send image from image urlclient.sendRemoteImage(friend.uid,message=msg, image=imgurl)

msg = 'yo'
imgurl = "Guess-Up-Emoji-Hot-Chick.png"
client.sendLocalImage(friend.uid,message=msg, image=imgurl)
#subclass fbchat.Client and override required methods
#class EchoBot(fbchat.Client):
#
#    def __init__(self,email, password, debug=True, user_agent=None):
#        fbchat.Client.__init__(self,email, password, debug, user_agent)
#
#    def on_message(self, mid, author_id, author_name, message, metadata):
#        self.markAsDelivered(author_id, mid) #mark delivered
#        self.markAsRead(author_id) #mark read
#
#        print("%s said: %s"%(author_id, message))
#
#        #if you are not the author, echo
#        if str(author_id) != str(self.uid):
#            self.send(author_id,message)
#
#bot = EchoBot(email, password)
#bot.listen()



