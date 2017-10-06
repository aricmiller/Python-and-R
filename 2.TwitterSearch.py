# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:00:31 2017

@author: amill_000
"""

import twitter


#Consumer keys and access tokens, used for OAuth
api = twitter.Api(
 consumer_key = '0k9u7aRiUdQOB6Z856FRiWXon',
 consumer_secret = '9GQQVz3J7IqESvO2gfL2ZaEpg6Au9ELQuQsmHvZsKf0QHx7G52',
 access_token_key = '311255648-BIs4gRnMre7qfmA3WRjOF8BRR812RsQAy80ZNveR',
 access_token_secret = 'ja9XpuW98L9LJWo9QKv4dpdZ4GxMW7e3kKqKTtHzKOT2S')

search = api.GetSearch(term=('Starbucks','coffee'), lang='en', result_type='', max_id='', count=100, include_entities=False)
status_ID=[]

output1 = open('C:\\Users\\amill_000\\Documents\\Fintech\\Twitter_info1.csv', 'a')
for t in search:
    status_ID.append(t.id)
    output1.write(str(t.user.id)+";    "+t.user.screen_name.encode('utf-8')+";    "+t.user.location.encode('utf-8')+";    "
                    +str(t.id)+";    "+str(t.created_at)+";    "+t.text.encode('utf-8')+"\n")
lowestID = min(status_ID)-1
for i in range(20):
#TwitterError: [{u'message': u'Rate limit exceeded', u'code': 88}]
    search = api.GetSearch(term=('Starbucks','coffee'), lang='en', result_type='', max_id=lowestID, count=100, include_entities=False)
    status_ID=[]
    for t in search:       
        status_ID.append(t.id)
        output1.write(str(t.user.id)+";    "+t.user.screen_name.encode('utf-8')+";    "+t.user.location.encode('utf-8')+";    "
                    +str(t.id)+";    "+str(t.created_at)+";    "+t.text.encode('utf-8')+"\n")
    lowestID = min(status_ID)-1
    #print status_ID
    #print lowestID
output1.close()



