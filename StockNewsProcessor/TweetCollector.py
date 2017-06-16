import tweepy
import pandas as pd

from tinydb import TinyDB, where

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import string
import re
import time
from datetime import datetime

import threading


class TweetCollector(object):
    def __init__(self, agencies, token, token_secret, consumer, consumer_secret):
        self.agencies = agencies
        self.access_token = token
        self.tweets_dict = {}
        self.tweets_list = []
        self.latest_tweets = {}
        self.access_token_secret = token_secret
        self.consumer_key = consumer
        self.consumer_secret = consumer_secret
        self._refresh = 10 * 60
        self._tweets = TinyDB('./tweets.json')
        self._tweets.purge()
        self._auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self._auth.set_access_token(self.access_token, self.access_token_secret)
        self._api = tweepy.API(self._auth)
        self.tweets = pd.DataFrame()
        self.tweets_columns = []

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def get_status(self, handle):
        try:
            user = self._api.get_user(handle)
        except tweepy.TweepError as e:
            print('Tweeter server error ', e.response, ' for handle: ', handle)
            return []

        if hasattr(user, 'status'):
            return user.status
        else:
            return []

    @staticmethod
    def _process(status):
        clean_status = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', status._json['text'],
                                flags=re.MULTILINE)
    
        clean_status = re.sub('@[\w.]+', '', clean_status, flags=re.MULTILINE)
    
        tokenized_docs = word_tokenize(clean_status)
    
        regex = re.compile('[%s]' % re.escape(string.punctuation))
    
        tokenized_docs_no_punctuation = []
    
        for token in tokenized_docs:
            new_token = regex.sub(u'', token)
            if not new_token == u'':
                if new_token not in stopwords.words('english') and new_token != 'RT' and new_token != '...':
                    tokenized_docs_no_punctuation.append(new_token)
    
        status._json['tokens'] = tokenized_docs_no_punctuation
        

        #tweet['source'] = status.source
        

        return status
        
#    def _process(status):
#        clean_status = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', status._json['text'],
#                               flags=re.MULTILINE)
#
#        clean_status = re.sub('@[\w.]+', '', clean_status, flags=re.MULTILINE)
#
#        tokenized_docs = word_tokenize(clean_status)
#
#        regex = re.compile('[%s]' % re.escape(string.punctuation))
#
#        tokenized_docs_no_punctuation = []
#
#        for token in tokenized_docs:
#            new_token = regex.sub(u'', token)
#            if not new_token == u'':
#                if new_token not in stopwords.words('english') and new_token != 'RT' and new_token != '...':
#                    tokenized_docs_no_punctuation.append(new_token)
#
#        status._json['tokens'] = tokenized_docs_no_punctuation
#
#        return status

    def get_tweet(self, handle):
        status = self.get_status(handle)
        status = self._process(status)
        tweet = {}
        tweet['author'] = '@' + handle
        tweet['text'] = status.text
        tweet['tweet date'] = str(status.created_at)
        tweet['# of times favorited'] = status.favorite_count
        tweet['hashtags'] = status.entities['hashtags']
        tweet['retweets'] = status.retweet_count
        tweet['url'] = status.entities['urls'][0]['url']
            
        return tweet
    
    def get_latest_tweets(self):
        self.latest_tweets = {}
        for agency in self.agencies:
            self.latest_tweets[agency] = self.get_tweet(agency)
        return self.latest_tweets
    
    def check_tweet_not_already_there(self,tweet,agency):
        if agency in self.tweets_dict.keys():
            for i in range(len(self.tweets_dict[agency])):
                if tweet == self.tweets_dict[agency][i]:
                    return False
                elif tweet['text'] == self.tweets_dict[agency][i]['text']:
                    self.tweets_dict[agency][i] = tweet
                    return False
        return True
    
        
    def get_tweets(self):
        for agency in self.agencies:
            if not agency in self.tweets_dict.keys():
                    self.tweets_dict[agency] = [self.get_tweet(agency)]
                    self.tweets_list.append(self.get_tweet(agency))
            else:
                if self.check_tweet_not_already_there(self.get_tweet(agency),agency):
                    self.tweets_dict[agency].append(self.get_tweet(agency))
                    self.tweets_list.append(self.get_tweet(agency))
                
        return self.tweets_list
        
    def clear_tweets(self):
        self.tweets_dict = {}
        self.tweets_list = []

    def process_data(self):
        self.get_tweets()
        self.tweets = pd.DataFrame(self.tweets_list)
        #self.tweets.columns = self.tweets_columns
        
        return self.tweets


    def _single_execute(self):
        print(datetime.now().time())
        for agency in self.agencies.search(where('handle')):
            tweeter_handle = agency['handle']
            status = self.get_status(tweeter_handle)
            if status:
                status_p = self._process(status)
                if not self._tweets.search(where('id') == status_p._json['id']) or not self._tweets.all():
                    self._tweets.insert(status_p._json)
            else:
                continue

    def run(self):
        while True:
            self._single_execute()
            time.sleep(self._refresh)