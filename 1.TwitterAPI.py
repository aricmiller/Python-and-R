# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 10:27:07 2017

@author: amill_000
"""

import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy import StreamListener

#Consumer keys and access tokens, used for OAuth
consumer_key = '' #removed for security
consumer_secret = ''#removed for security
access_token = ''#removed for security
access_token_secret = ''#removed for security

# Class below handles data received from the twitter stream
class StdOutListener(StreamListener):
    
    def on_status(self,status):
        #prints the text of tweet
        print('Tweet text: ' + status.text)
        return True
    
    #to report an error if an error shows
    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
        return True
    
    #to report if Internet is disconnected
    def on_timeout(self):
        print('Timeout...')
        return True
    
#Main program below
#identification and access
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
#streaming and filtering below
lis = StdOutListener()
stream = Stream(auth, lis)
stream.filter(track=['dog'])
    
    
    
    
    
    
    
    
    
    
