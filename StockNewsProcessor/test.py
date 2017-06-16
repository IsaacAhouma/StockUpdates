from __future__ import division
from StockMarket import StockPortfolio
import time
tic = time.time()
s = []
sm = StockPortfolio(s)
news, stock,historical = sm.refresh_portfolio()
s = ['TSLA','SNAP']
sm = StockPortfolio(s)
news, stock,historical = sm.refresh_portfolio()
#
sm.get_latest_data_for_symbols('TSLA',3)
sm.get_latest_data_for_symbols(['TSLA'])
sm.get_latest_data_for_symbols(['TSLA','SNAP'],2)

sm.get_latest_news_for_symbols('TSLA')
sm.get_latest_news_for_symbols('TSLA',10000)
sm.get_latest_news_for_symbols(['TSLA','SNAP'],3)



sm.add_symbols(['RY','MsFT'])


sm.get_latest_news_for_symbols(sm.symbols,limit=2)

sm.get_latest_news_for_symbols(['BMO'],2)
sm.get_latest_data_for_symbols(['BMO'],1)

#
sm.get_latest_news_for_symbols(['FB','LNKD','AMZN'],2)


sm.daily_price_stats(symbols=sm.symbols)



sm.add_symbols(['EBAY','YHOO','GOOG','AMZN','FB','TD'])

news,stock_data,historical_data = sm.refresh_portfolio()

sm.add_symbols('TWTR')

toc = time.time()

print 'runtime = ' + str((toc - tic)/60) + ' minutes'