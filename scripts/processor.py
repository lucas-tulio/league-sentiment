#!/usr/bin/env python
#Text Processor (tagging, etc) - Data means each post
import nltk
import re
import time
import pymysql
import urllib2
import json
import collections
import types
import time
import datetime
import sys
from pprint import pprint
from textblob import TextBlob

# Processor function
def processor(id_comment_local, id_comment, data):

  try:

    # Split into sentences
    utf8_data = data.decode("utf-8")
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(utf8_data.strip())

    # Tokenize sentence. For POS tags info, refer to http://www.monlp.com/2011/11/08/part-of-speech-tags/
    for sentence in sentences:
      
      # Get the Named Entity
      tokenized = nltk.word_tokenize(sentence)
      tagged = nltk.pos_tag(tokenized)
      entities = nltk.ne_chunk (tagged, binary = True) # Will return a tree, with the Named Entity tagged as "NE"
      namedEntity = ""
      for item in entities:
        if type(item) is nltk.tree.Tree and item.node == 'NE':
          namedEntity = item[0][0]
          break

      # No Named Entities found, skip
      if namedEntity == "":
        continue

      # Find the descriptives (adjectives, comparative and superlative adverbs)
      tb = TextBlob(sentence)
      words = tb.tags
      descriptives = []
      for word in words:
        if word[1] in ('JJ', 'JJR', 'JJS', 'RBR', 'RBS'):
          descriptives.append(word[0])

      # Insert
      for desc in descriptives:

        score = tb.sentiment.polarity
        sub = tb.sentiment.subjectivity
        cur.execute("INSERT INTO entities (id_comment_local, id_comment, entity, word, score, sub) VALUES (%s,%s,%s,%s,%s,%s)", 
        (str(id_comment_local), str(id_comment), str(namedEntity), str(desc), score, sub))

  except Exception, e:
    print 'Error classifying'
    print str(e)

# Script --------------------------------------------------------------------------------------

print "Processing entities..."

conn = pymysql.connect(host='127.0.0.1', port=3306, user='processor', passwd='processor', db='sentiment', charset='utf8')
cur = conn.cursor()
cur1 = conn.cursor()

cur.execute("SELECT c.id, c.id_comment, c.comment FROM comments c inner join threads t on c.id_thread = t.id where t.created >= adddate(now(), INTERVAL -1 DAY);")

for row in cur.fetchall():
  
  id_comment_local = row[0]
  id_comment = row[1]
  comment = row[2]
  s = comment.encode('utf8')
  cur1.execute("SELECT * FROM entities where id_comment_local = %s", str(id_comment_local))
  data = cur1.fetchone()
  
  if data is None:
    # Sometimes an already classified Comment enters where because that comment didn't have any Entities.
    # Hence, it was not inserted in the 'processor' function above.
    processor (id_comment_local, id_comment, s)
  else:
    print "Comment already there"

conn.commit()
cur.close()
