import tweepy
from textblob import TextBlob
import csv
import os
import io
import numpy

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

searchTerm = 'syria'

if not os.path.exists('twitterData'):
    os.makedirs('twitterData')

consumer_key = 'X97LPOOOrNAAJMXoqEgwRK2V7'
consumer_secret = 'JLtzGigHUSYvuDasItILwnhXpVGsbH97MulswuxCjUi963rIYW'

access_token = '821278473453006849-BGqNrsFjS1OsOyIppvu143k0Z0Kbari'
access_token_secret = 	'uJX0d14vXGJrF5vA7PJBAN1u8V6MZDvMYEgQJYvHLbLAr'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.search(searchTerm, count=100)

polList = []
subList = []
idList = []
nTweets = 0
idMax = -1

maxTweets = 5000
with io.open('twitterData\%s.csv'%(searchTerm), 'w', newline = '', encoding="utf-8") as output:
    fileOut = csv.writer(output)
    header = ['Tweet', 'Polarity', 'Subjectivity']
    fileOut.writerow(header)
    
    while nTweets <= maxTweets:
        if idMax > 0:
            public_tweets = api.search(searchTerm, count=100, max_id = str(idMax-1))
        else:
            public_tweets = api.search(searchTerm, count=100)
    
        for tweet in public_tweets:
            analysis = TextBlob(tweet.text)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
        
            fileOut.writerow([tweet.text, polarity, subjectivity])
        
            polList.append(polarity)
            subList.append(subjectivity)
            idList.append(tweet.id)
            nTweets += 1
    idMax = numpy.ndarray.min(numpy.asarray(idList))

polArray = numpy.asarray(polList,dtype='float')
nonZeroPol = polArray[numpy.nonzero(polArray)]
avgPolarity = numpy.mean(nonZeroPol)
print('Average Polarity: %f'%(avgPolarity))