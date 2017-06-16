from __future__ import division
from StockMarket import StockPortfolio, list_of_available_symbols
import time
tic = time.time()
s = []
sm2 = StockPortfolio(s)
#sm2.add_symbols([x for x in list_of_available_symbols[-10:] if len(x)< 5])
sm2.add_symbols(list_of_available_symbols)
news, stock,historical = sm2.refresh_portfolio()

#sm2.get_latest_news_for_symbols('TSLA')
#
#sm2.add_symbols(['RY','MsFT'])


#sm2.get_latest_news_for_symbols(sm2.symbols,limit=2)
#
#
#sm2.daily_price_stats(symbols=sm2.symbols)
#
#
#news,stock_data,historical_data = sm2.refresh_portfolio()



toc = time.time()

print 'runtime = ' + str((toc - tic)/60) + ' minutes'