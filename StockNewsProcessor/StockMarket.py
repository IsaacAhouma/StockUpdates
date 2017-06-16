"""
Created on Tue Jun 13 10:17:06 2017

@author: Isaac
"""

import googlefinance as gf
import json
import pandas as pd
import numpy as np
import logging
import traceback
import fbchat

# Build a dataframe containing information for all the companies that are trading on AMEX,NYSE, and NASDAQ exchanges
data = pd.read_csv('AMEX_stocks.csv')
data = data.append(pd.read_csv('NYSE_stocks.csv'))
data = data.append(pd.read_csv('NASDAQ_stocks.csv'))
### Usually symbols with 5 or more letters are not available through the googlefinance api
data = data[data['Symbol'].apply(lambda x: len(x) < 5)]
data['Symbol'] = data['Symbol'].apply(lambda x : x.upper().strip())
data['Name'] = data['Name'].apply(lambda x : x.upper().strip())

### Get the list of all available companies and symbols. Useful so that instead of entering symbols only, users could enter the full name of the company.
### Also useful to help us check which symbols/companies are currently available.
list_of_available_companies = list(data['Name'])
list_of_available_symbols = list(data['Symbol'])

#email = pd.read_csv('email.csv').columns[0]
#password = pd.read_csv('password.csv').columns[0]
#client = fbchat.Client(email, password)


class StockPortfolio(object):
    def __init__(self,symbols,client,user_account,account_type = 'messenger'):
        self.symbols = symbols #list of all the symbols currently in the portolio
        self.news_list = [] #list of the available news for the stocks
        self.stock_data_list = [] #list of the most recent data for the stocks
        self.news_dict = {} #dict of the available news for the stocks
        self.stock_data_dict ={} #dict of the most recent data for the stocks
        self.historical_stock_data = []  #list of all the available data for the stocks since the portfolio was created
        self.news_frame = pd.DataFrame()
        self.news_frame_columns = ['date','headline','source','symbol','text','url']
        self.stock_data_frame = pd.DataFrame()
        self.stock_data_frame_columns = ['price','date','index','symbol','yield']
        self.client = client
        self.owner = user_account  # should a be a phone number or fb messenger account id
        self.account_type = account_type
        for i in range(len(self.symbols)):
            self.symbols[i] = self.symbols[i].upper()
    
    
    def check_symbol_is_valid(self,symbol):
        """   check that the symbol is in the list of available symbols. If not, check if symbol is in the list of available companies (ie; is it the name of a company).
             If symbol is a valid company/symbol then we return the tuple (True, symbol), else we return (False, None).
             Input type is string.
        """
        assert(type(symbol)==str)
        symbol = symbol.upper()
        if not symbol in list_of_available_symbols:
            if symbol in list_of_available_companies:
                symbol = list_of_available_symbols[list_of_available_companies.index(symbol)]
            else:
                print symbol + " is not a valid company/symbol. " + "Please enter the name of a valid company or it's symbol."
                return False, None
        return True, symbol
    
    
    def add_symbols(self,symbol):
        """
        Add a valid symbol or a list of (valid) symbols to the portfolio.
        Input type: String
        Output Type: None
        """
        assert(type(symbol)==str or type(symbol)==list)
        if type(symbol)==list:
            for s in symbol:
                if not s.upper() in self.symbols and self.check_symbol_is_valid(s)[0]:
                    s = self.check_symbol_is_valid(s)[1]
                    self.symbols.append(s.upper())
            return       
        if not symbol.upper() in self.symbols and self.check_symbol_is_valid(symbol)[0]:
            symbol = self.check_symbol_is_valid(symbol)[1]
            self.symbols.append(symbol.upper())
    
    def remove_symbol(self,symbols):
        """
        Remove symbol or symbols from the portfolio if they were previously added.
        Input type: String or List of strings
        Output Type: None
        """
        assert(type(symbols)==str or type(symbols)==list)
        if type(symbols)==str:
            symbols = [symbols]
        for symbol in symbols:
            symbol = symbol.upper()
            if symbol in self.symbols:
                self.symbols.remove(symbol)
        
    
    def get_current_price(self,symbol,local=False):
        """
        Given a valid symbol, returns its most recent trading information (price, previous day close, yield, change, etc...)
        Input type: String
        Output Type: dictionary
        """
        assert(type(symbol)==str)
        stock = {}
        if self.check_symbol_is_valid(symbol)[0]:
            symbol = self.check_symbol_is_valid(symbol)[1]
            try:
                data = gf.getQuotes(symbol.upper())[0]
                stock['index'] =  data['Index']
                if 'Yield' in data.keys():
                    if data['Yield']=='':
                        stock['yield'] = 0.0
                    else:
                        stock['yield'] = float(data['Yield'])
                else:
                    stock['yield'] = 0.0
                if 'ChangePercent' in data.keys():
                    if data['ChangePercent']=='':
                        stock['change'] = 0.0
                    else:
                        stock['change'] = float(data['ChangePercent'])
                else:
                    stock['change'] = 'N/A'
                if 'PreviousClosePrice' in data.keys():
                    if data['PreviousClosePrice']=='':
                        stock['previous close price'] = 'N/A'
                    else:
                        stock['previous close price'] = float(data['PreviousClosePrice'])
                else:
                    stock['previous close price'] = 'N/A'
                stock['date'] =  str(data['LastTradeDateTimeLong'])
                stock['symbol'] =  data['StockSymbol']
                name = list_of_available_companies[list_of_available_symbols.index(stock['symbol'])]
                stock['Company'] = name
                    
                def remove_comma(string):
                    s = ''
                    for i in range(len(string)):
                        if not string[i]==',':
                            s += string[i]
                    return s
                    
                stock['current price'] =  float(remove_comma(data['LastTradePrice']))
                
                self.stock_data_dict[symbol] = stock
                
                if symbol.upper() not in self.symbols:
#                    if local:
#                        answer = input(symbol.upper() + " is not in your portfolio. Would you like to add it to your portfolio?")
#                    else:
#                        msg = "Warning, " + symbol.upper() + " is not in your portfolio."
#                        sent = self.client.send(self.owner.uid, msg)
#                        answer = 'y'
#                        self.historical_stock_data.append(stock)
#                        return stock
#                    if answer.lower() == 'y' or answer.lower() == 'yes':
#                        self.symbols.append(symbol)
#                        self.stock_data_list.append(stock)
#                        self.historical_stock_data.append(stock)
#                        return stock
#                    else:
                        self.historical_stock_data.append(stock)
                        return stock

                if self.symbols.index(symbol) in range(len(self.stock_data_list)):
                    self.stock_data_list[self.symbols.index(symbol)] = stock
                else:
                    self.stock_data_list.append(stock)
                self.historical_stock_data.append(stock)
                
            except Exception:
                self.remove_symbol(symbol)
        
        
        return stock
        
    
    def get_current_news(self,symbol):
        """
        Given a valid symbol, returns news stories about it.
        Input type: String
        Output Type: dictionary
        """
        assert(type(symbol)==str)
        try:
            data = gf.getNews(symbol.upper())
            for i in range(len(data)):
                stock_news = {}
                stock_news['symbol'] = symbol.upper()
                name = list_of_available_companies[list_of_available_symbols.index(stock_news['symbol'])]
                stock_news['Company'] = name
                stock_news['date'] = str(data[i]['d'])
                stock_news['text'] = data[i]['sp']
                stock_news['source'] = data[i]['s']
                stock_news['headline'] = data[i]['t']
                stock_news['url'] = data[i]['u']
                if not symbol in self.news_dict.keys():
                    self.news_dict[symbol] = [stock_news]
                else:
                    self.news_dict[symbol].append(stock_news)
                if stock_news not in self.news_list:
                    self.news_list.append(stock_news)
        except:
            self.remove_symbol(symbol)
            return {}
        return self.news_dict[symbol]
    
    def refresh_data(self,symbols):
        """
        Refresh all the available data for symbols and return its news ,most recent trading information (price, previous day close, yield, change, etc...)
        as well as all its available trading information since the portfolio was created.
        Input type: String or List of String.
        Output Type: (dictionary,dictionary,dictionary)
        """
        assert(type(symbols)==str or type(symbols)==list)
        if type(symbols)==str:
            symbols = [symbols]
        for symbol in symbols:
            if self.check_symbol_is_valid(symbol)[0]:
                symbol = self.check_symbol_is_valid(symbol)[1]
                _ = self.get_current_price(symbol)
                _ = self.get_current_news(symbol)
        self.news_frame = pd.DataFrame(self.news_list)
        self.current_stock_data_frame = pd.DataFrame(self.stock_data_list)
        self.historical_stock_data_frame = pd.DataFrame(self.historical_stock_data)
        self.news_frame = self.news_frame[['symbol','Company','headline','text','date','source','url']]
        self.current_stock_data_frame = self.current_stock_data_frame[['symbol','Company','current price','date','change','previous close price','yield','index']]
        self.historical_stock_data_frame = self.historical_stock_data_frame[['symbol','Company','current price','date','change','previous close price','yield','index']]
        self.news_frame = self.news_frame.sort_values(by='date',ascending=False)
        self.historical_stock_data_frame = self.historical_stock_data_frame.sort_values(by='date',ascending=False)
        return self.news_frame, self.current_stock_data_frame, self.historical_stock_data_frame
    
    def refresh_portfolio(self,local=False):
        """
        Refresh all the available data for all the symbols currently in the portfolio and return their news ,most recent trading information (price, previous day close, yield, change, etc...)
        as well as all their available trading information since the portfolio was created.
        Input type: String or List of String.
        Output Type: (dictionary,dictionary,dictionary)
        """
        if len(self.symbols)==0:
            if local:
                print "Warning, portfolio is currently empty. Please add valid stocks."
            else:
                msg = "Warning, your portfolio is currently empty. Please add valid stocks."
                if self.account_type == 'messenger':
                    sent = self.client.send(self.owner.uid, msg)
                elif self.account_type == 'twilio':
                    message = self.client.api.account.messages.create(to=self.owner,
                                             from_="+12892748035",
                                             body=msg)
            return None,None,None
        news,current_data,historical_data = self.refresh_data(self.symbols)
        return news, current_data, historical_data
    
    
    def get_latest_news_for_symbols(self,symbols,limit=None):
        """
        Returns the N=limit most recent news for each symbol in symbols. News are sorted from newest to oldest.
        Input type: String or List of String.
        Output Type: (dictionary,dictionary,dictionary)
        """
        assert(type(symbols)==str or type(symbols)==list)
        _,_,_ = self.refresh_data(symbols) 
        if type(symbols)==str:
            symbols = [symbols]
        results = pd.DataFrame()
        symbols = list(set(symbols))
        added = []
        for symbol in symbols:
            if not symbol in self.symbols and self.check_symbol_is_valid(symbol)[0]:
                symbol = self.check_symbol_is_valid(symbol)[1]
                added.append(symbol)       
        if limit==None:
            return self.news_frame[self.news_frame['symbol'].isin(symbols)].sort_values(by=['date'])
        for symbol in symbols:
            result = self.news_frame[self.news_frame['symbol'].isin([symbol])]
            limit = np.minimum(limit,len(result))
            if results.empty:
                results = result[-limit:]
            else:
                results = results.append(result[-limit:])
        return results.sort_values(by=['date'])
    
    
    def get_latest_data_for_symbols(self,symbols,limit=None):
            """
            Returns the N=limit most recent trading information for each symbol in symbols. Results are sorted from newest to oldest.
            Input type: String or List of String.
            Output Type: (dictionary,dictionary,dictionary)
            """
            assert(type(symbols)==str or type(symbols)==list)
            _,_,_=self.refresh_data(symbols)
            if type(symbols)==str:
                symbols = [symbols]
            results = pd.DataFrame()
            symbols = list(set(symbols))
            added = []
            for symbol in symbols:
                if not symbol in self.symbols and self.check_symbol_is_valid(symbol)[0]:
                    symbol = self.check_symbol_is_valid(symbol)[1]
                    added.append(symbol)
            if limit==None:
                    return self.historical_stock_data_frame[self.historical_stock_data_frame['symbol'].isin(symbols)]
            for symbol in symbols:
                result = self.historical_stock_data_frame[self.historical_stock_data_frame['symbol'].isin([symbol])].sort_values(by=['date'])
                limit = np.minimum(limit,len(result))
                if results.empty:
                    results = result[-limit:]
                else:
                    results = results.append(result[-limit:])
            return results.sort_values(by=['date'])
    
    #### This should eventually be moved to the analytics class later
    
    def daily_price_stats(self,symbols,sortby='change'):
        """
        Using historical data for each symbol in the portfolio, returns current summary (mean,max,min,spread = max - min, standard deviation, change) for each
        stock. Results are sorted in ascending order by change (ie, from the stock which gained the most montary value during the day, to the stock which lost the most).
        """
        #_,_,_=self.refresh_portfolio()
        assert(type(symbols)==str or type(symbols)==list)
        if type(symbols)==str:
            symbols = [symbols]
        symbols = list(set(symbols))
        results = self.get_latest_data_for_symbols(symbols)
        new_results = pd.DataFrame()
        res = []
        for symbol in symbols:
            current_price = self.stock_data_dict[symbol]['current price']
            mean = np.mean(results[results['symbol']==symbol]['current price'])
            minimum = np.min(results[results['symbol']==symbol]['current price'])
            maximum = np.max(results[results['symbol']==symbol]['current price'])
            spread = maximum - minimum
            std = np.std(results[results['symbol']==symbol]['current price'])
            date = self.stock_data_dict[symbol]['date']
            latest_change = self.stock_data_dict[symbol]['change']
            previous_day_close_price = self.stock_data_dict[symbol]['previous close price']
            res.append([symbol,current_price,latest_change,previous_day_close_price,mean,spread,maximum,minimum,std,date])
            new_results = pd.DataFrame(res)
            new_results.columns = ['symbol','current price','change','previous close price','daily average','daily spread','daily max','daily min','daily standard deviation','As of Date']
        return new_results.sort_values(by=sortby,ascending=False)
            
            


        