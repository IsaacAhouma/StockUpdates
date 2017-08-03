from __future__ import division

from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from StockMarket import StockPortfolio
import urllib2
from twilio.rest import Client

app = Flask(__name__)

previous_received_message = ''

# Try adding your own number to this list!
callers = {
}

set_of_callers = set([])


calls = {}
for caller in callers:
    calls[caller] = 0

account_sid = "your account id"
auth_token = "your authorization token"
client = Client(account_sid, auth_token)


destination_number = "the number you want to text. "
s = ['RY']
sm = StockPortfolio(s,client,destination_number,account_type='twilio')


def send_price(destination_number,symbols=sm.symbols,extended=False,add_image=False):
    assert(type(symbols)==str or type(symbols)==list)
    if type(symbols)==str:
        symbols = [symbols]
    price_data = sm.get_latest_data_for_symbols(symbols,limit=1)
    
    def stringify_stock_price(stock):
        company = """Company: """ + str(stock['company'])
        symbol = """   Symbol: """ + str(stock['symbol'])
        current_price = """   Current Price: """ + str(stock['current price'])
        #change = ' % Change: ' + str(stock['change'])
        previous_close_price = """   Previous Close Price: """ + str(stock['previous close price'])
        change = """   Change: """ + str(round((stock['change'] / stock['previous close price']) * 100,2)) + ' %'
        date = """   Last Updated: """ + str(stock['date'])
        msg = company + symbol + current_price + change + previous_close_price + date
        
        return msg

    for i in price_data.index:
        print i
        message = stringify_stock_price(price_data.ix[i])
        
        #if add_image:
        #    if float(percentage_change) > float(5):
        #        imgurl = "Guess-Up-Emoji-Hot-Chick.png"
        #    elif float(percentage_change) < float(5):
        #        imgurl = "cold.jpeg"
        #    else:
        #        imgurl = "cold.jpeg"
        #    message = client.api.account.messages.create(to=sm.owner,
        #                                     from_="+12892748035",
        #                                     body=msg,
        #                                     media_url=[
        #                                           'https://demo.twilio.com/owl.png',
        #                                           'https://demo.twilio.com/logo.png'])
        sent = client.api.account.messages.create(to=destination_number,
                                             from_="+12892748035",
                                             body=message)
                                             
def send_stats(destination_number,symbols=sm.symbols,extended=False,add_image=False):
    assert(type(symbols)==str or type(symbols)==list)
    if type(symbols)==str:
        symbols = [symbols]
    stats_data = sm.daily_price_stats(symbols=symbols)
    
    def stringify_stock_stats(data,extended=extended):
        symbol = 'Company: ' + str(data['symbol'])
        current_price = ' Current Price: ' + str(data['current price'])
        change = ' Change: ' + str(data['change'])
        previous_close_price = ' Previous Day Close Price: ' + str(data['previous close price'])
        percentage_change = round((float(data['change']) / float(data['previous close price'])) * 100,2)
        percentage_change = ' Percentage Change: ' + str(percentage_change) + '%'
        daily_max = ' Daily Max: ' + str(data['daily max']) 
        daily_min = ' Daily Min: ' + str(data['daily min'])
        daily_average = ' Daily Average: ' + str(data['daily average'])
        daily_spread = ' Daily Spread: ' + str(data['daily spread'])
        daily_std = ' Daily Standard Deviation: ' + str(data['daily standard deviation'])
        date = ' Last Updated: ' + str(data['As of Date'])
        msg = symbol + current_price + previous_close_price + change + percentage_change  + daily_average + daily_max + daily_min + date
        if extended:
            msg += daily_std + daily_spread
        return msg
        
    for i in stats_data.index:
        
        message = stringify_stock_stats(stats_data.ix[i])
        
        sent = client.api.account.messages.create(to=destination_number,
                                             from_="+12892748035",
                                             body=message)

                                             

def send_news(destination_number,symbols=sm.symbols,extended=False,limit=1):
    assert(type(symbols)==str or type(symbols)==list)
    news_data = sm.get_latest_news_for_symbols(symbols,limit)
    
    def stringify_news(news,extended=extended):
        symbol = 'Company: ' + str(news['symbol'])
        headline = ' Headline: ' + str(news['headline'])
        source = ' Source: ' + str(news['source']) 
        url = ' Link' + str(news['url'])
        date = ' Date: ' + str(news['date'])
        text = ' Text: ' + str(news['date'])
        msg = symbol + headline + date + source + urllib2.quote(url)
        if extended:
            msg +=   text + source
            
        return msg
        
    for i in news_data.index:
        message = stringify_news(news_data.ix[i])
        
        sent = client.api.account.messages.create(to=destination_number,
                                            from_="+12892748035",
                                            body=message)                                     
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond and greet the caller by name."""
    
    global previous_received_message
    global set_of_callers
    from_number = request.values.get('From', None)
    content = request.values.get('Body', None)
    
    if from_number not in set_of_callers:
        set_of_callers.add(from_number)
        if from_number in callers:
            message = "Hello " + callers[from_number] + ", thanks for the message! I am your official stock bot. How can I help you today?"
        else:
            message = """Hello Stranger, thanks for the message! I am your official stock bot. How can I help you today?"""
        message += """ Please choose one of the following, '1':get stock data, '2':get stock news', '3':build your portfolio', '4': get portfolio statistics, '5':see your portfolio, '6': add symbol to your portfolio, '7': remove symbol from your portfolio"""

    
    else:
        
        if str(content)=='1' or str(content).lower()=='stock data' or str(content).lower()=='data' or str(content).lower()=='get stock data' or str(content).lower()=='price':
            message = """Please enter the company or symbol you would like to get data for. For multiple companies, please separate each company with ' , '"""
        elif str(content)=='2' or str(content).lower()=='stock news' or str(content).lower()=='news' or str(content).lower()=='get stock news':
            message = """Please enter the company or symbol you would like to get news for. For multiple companies, please separate each company with ' , '"""
        elif str(content)=='3' or str(content).lower()=='build portfolio' or str(content).lower()=='build my portfolio':
            message = """Please enter the company or symbol you would like to add to your portfolio. If you want to enter more than one company, please separate them by a period ' , '"""
        elif str(content)=='4' or str(content).lower()=='stats' or str(content).lower()=='statistics' or str(content).lower()=='get portfolio statistics':
            message = """Please enter the companies or symbols you would like to get statistics for. Enter 'p' or 'portfolio' to get statistics for your current portfolio."""
        elif (str(content)=='5' or str(content).lower()=='see portfolio' or str(content).lower()=='my portfolio' or str(content).lower()=='portfolio' or str(content).lower()=='p') and (not str(previous_received_message).lower() in ['4','get portfolio statistics','stats','statistics']):
            portfolio = '['
            for symbol in sm.symbols:
                portfolio += str(symbol) + ' '
            portfolio += ']'  
            message = 'Your portfolio consists of: '
            message += portfolio + ' .'
        elif str(content)=='6' or str(content).lower()=='add' or str(content).lower()=='add stock' or str(content).lower()=='add symbol':
            message = """Please enter the company or symbol you would like to add to your portfolio. If you want to add more than one company/symbol, please separate them by a period ','"""
        elif str(content)=='7' or str(content).lower()=='remove' or str(content).lower()=='remove stock' or str(content).lower()=='remove symbol':
            message = """Please enter the company or symbol you would like to remove from your portfolio. If you want to remove more than one company/symbol, please separate them by a period ','"""
        elif str(previous_received_message)=='1' or str(previous_received_message).lower()=='stock data' or str(previous_received_message).lower()=='data' or str(previous_received_message).lower()=='get stock data':
            symbols = str(content).split(',')
            symbols = [str(symbol).upper() for symbol in symbols if sm.check_symbol_is_valid(symbol)]
            news, stock,historical = sm.refresh_portfolio()
            #message = send_stats(from_number,symbols=symbols)
            message = send_price(from_number,symbols=symbols)
        elif str(previous_received_message)=='2' or str(previous_received_message).lower()=='stock news' or str(previous_received_message).lower()=='news' or str(previous_received_message).lower()=='get stock news':
            symbols = str(content).split(',')
            symbols = [str(symbol).upper() for symbol in symbols if sm.check_symbol_is_valid(symbol)]
            news, stock,historical = sm.refresh_portfolio()
            message = send_news(from_number,symbols)
        elif str(previous_received_message)=='3' or str(previous_received_message).lower()=='portfolio' or str(previous_received_message).lower()=='build portfolio' or str(previous_received_message).lower()=='p':
            symbols = str(content).split(',')
            symbols = [str(symbol).upper() for symbol in symbols if sm.check_symbol_is_valid(symbol)]
            sm.add_symbols(symbols)
            added = '['
            for symbol in symbols:
                if sm.check_symbol_is_valid(symbol):
                    added += str(symbol) + ' '
            added += ']'
            portfolio = '['
            for symbol in sm.symbols:
                portfolio += str(symbol) + ' '
            portfolio += ']'  
            message = 'These symbols were added to your portfolio: '
            message += added
            message += 'Your portfolio now consists of: '
            message += portfolio + ' .'
        elif str(previous_received_message)=='4' or str(previous_received_message).lower()=='stats' or str(previous_received_message).lower()=='statistics' or str(previous_received_message).lower()=='get portfolio statistics':
            if str(content).lower()=='p' or str(content).lower()=='portfolio':
                symbols = sm.symbols
            else:
                symbols = str(content).split(',')
                symbols = [str(symbol).upper() for symbol in symbols if sm.check_symbol_is_valid(symbol)]
            news, stock,historical = sm.refresh_portfolio()
            message = send_stats(from_number,symbols)
        elif str(previous_received_message)=='6' or str(previous_received_message).lower()=='add' or str(previous_received_message).lower()=='add symbols':
            symbols = str(content).split(',')
            symbols = [str(symbol).upper() for symbol in symbols if sm.check_symbol_is_valid(symbol)]
            sm.add_symbols(symbols)
            added = '['
            for symbol in symbols:
                if sm.check_symbol_is_valid(symbol):
                    added += str(symbol) + ' '
            added += ']'
            portfolio = '['
            for symbol in sm.symbols:
                portfolio += str(symbol) + ' '
            portfolio += ']'  
            message = 'These symbols were added to your portfolio: '
            message += added
            message += """ Your portfolio now consists of: """
            message += portfolio + ' .'
        elif str(previous_received_message)=='7' or str(previous_received_message).lower()=='remove' or str(previous_received_message).lower()=='remove symbols':
            symbols = str(content).split(',')
            symbols = [str(symbol).upper() for symbol in symbols if sm.check_symbol_is_valid(symbol)]
            sm.remove_symbol(symbols)
            removed = '['
            for symbol in symbols:
                if sm.check_symbol_is_valid(symbol):
                    if symbol in sm.symbols:
                        removed += str(symbol) + ' '
            removed += ']'
            portfolio = '['
            for symbol in sm.symbols:
                portfolio += str(symbol) + ' '
            portfolio += ']'  
            message = 'These symbols were removed from your portfolio: '
            message += removed
            message += """Your portfolio now consists of: """
            message += portfolio + ' .'
        else:
            message = "'" + str(content) + "'" + " is not a valid command. Please choose one of the following, '1':get stock data, '2':get stock news', '3':build your portfolio', '4': get portfolio statistics, '5':see your portfolio, '6': add symbol to your portfolio, '7': remove symbol from your portfolio"

    previous_received_message = content
    resp = MessagingResponse()
    resp.message(message)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
