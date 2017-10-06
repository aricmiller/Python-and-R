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
consumer_key = '0k9u7aRiUdQOB6Z856FRiWXon'
consumer_secret = '9GQQVz3J7IqESvO2gfL2ZaEpg6Au9ELQuQsmHvZsKf0QHx7G52'
access_token = '311255648-BIs4gRnMre7qfmA3WRjOF8BRR812RsQAy80ZNveR'
access_token_secret = 'ja9XpuW98L9LJWo9QKv4dpdZ4GxMW7e3kKqKTtHzKOT2S'

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
    
    
    
    
    
    
    
    
    
    