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