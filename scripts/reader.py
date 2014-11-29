#!/usr/bin/env python
import pymysql
import urllib2
import json
import collections
import types
import time
import datetime
import sys
from pprint import pprint

# ----------------------
# Functions 
# ----------------------

# Read threads
def readThreads(subredditUrl, conn, cur):

	threads = requestJson(subredditUrl)

	newThreads = 0
	existingThreads = 0
	for t in threads['data']['children']:

		# Get the thread info
		threadId = t['data']['id']
		title = t['data']['title']
		permalink = t['data']['permalink']
		score = t['data']['score']
		created = t['data']['created_utc']
		
		# Save it to the database. Duplicate threads will be ignored due to the UNIQUE KEY constraint
		try:
			cur.execute("""INSERT INTO threads (id_thread, id_sub, title, url, score, created) values (%s, 1, %s, %s, %s, from_unixtime(%s))""", (threadId, title, permalink, int(score), created))
			newThreads += 1
			print "got new thread"
			conn.commit()
		except pymysql.err.IntegrityError as e:
			existingThreads += 1

	# Print a summary
	print "Inserted " + str(newThreads) + " new threads"
	
	# Log totals
	global totalNewThreads
	totalNewThreads += newThreads
	global totalExistingThreads
	totalExistingThreads += existingThreads

# Recursive function to read comments
def readComments(obj, threadId, threadUrl, conn, cur):
	newComments = 0
	existingComments = 0
	
	for i in obj:

		# Basic info, present both in Title and Comment
		commentId = i['data']['id']
		content = ""
		url = ""
		score = 0
		created = 0
		if 'created_utc' in i['data']:
			created = i['data']['created_utc']
		else:
			print "*** WARNING: created_utc not found in this record -> " + commentId
			created = 0

		# Is it a comment?
		if 'body' in i['data']:

			url = threadUrl + commentId
			content = i['data']['body']
			ups = int(i['data']['ups'])
			downs = int(i['data']['downs'])
			score = ups - downs

		# Or is it the title post?
		elif 'selftext' in i['data']:

			url = i['data']['url']
			content = i['data']['selftext']
			score = i['data']['score']

		# Save!
		try:
			cur.execute("""INSERT INTO comments (id_comment, id_thread, comment, url, score, created) values (%s, %s, %s, %s, %s, from_unixtime(%s))""", (commentId, threadId, content, url, int(score), created))
			newComments += 1
			conn.commit()
		except pymysql.err.IntegrityError as e:
			existingComments += 1

		# Does it have a reply? Recursivity here
		if 'replies' in i['data'] and len(i['data']['replies']) > 0:
			readComments(i['data']['replies']['data']['children'], threadId, threadUrl, conn, cur)

	# Print a Summary
	print "Inserted " + str(newComments) + " new comments"
	
	# Log totals
	global totalNewComments
	totalNewComments += newComments
	global totalExistingComments
	totalExistingComments += existingComments

def requestJson(url):
	while True:
		try:

			req = urllib2.Request(url, headers=hdr)
			response = urllib2.urlopen(req)
			jsonFile = response.read()
			
			time.sleep(2)
			
			return json.loads(jsonFile)

		except Exception as e:
			print e

# Setup ------------------------------------------
hdr = {'User-Agent' : "<enter user agent here>"}
baseUrl = "http://www.reddit.com"
subreddit = "/r/leagueoflegends"
subredditUrl = baseUrl + subreddit + "/new/.json"

# We use this guy to detect when we've read too many comments. If that happens, we call readThreads() so we don't lose new ones
commentCount = 0
commentLimit = 10
threadCount = 0
threadLimit = 3

# Database connection
conn = pymysql.connect(host='127.0.0.1', port=3306, user='scripts', passwd='scripts', db='sentiment', charset='utf8')
cur = conn.cursor()

print
print "Starting crawler"
print "Press ctrl+c to stop"
print

# Start! -----------------------------------------
while True:

	# Log starting time
	startingTime = datetime.datetime.now()
	# Totals to log in the database
	totalNewThreads = 0
	totalExistingThreads = 0
	totalNewComments = 0
	totalExistingComments = 0

	# Read the Threads
	readThreads(subredditUrl, conn, cur)
	
	threadCount += 1
	print "Thread count is " + str(threadCount)
	print "Waiting 10 secs before another read"
	time.sleep(10)

	# Should we read Comments?
	if threadCount % threadLimit == 0:

		threadCount = 0

		# Get threads from the last 24 hours. Row[0] = thread, row[4] = comment
		threads = dict()
		cur.execute("SELECT * FROM threads where created >= adddate(now(), INTERVAL -1 DAY);")
		for row in cur.fetchall():
			threads[row[0]] = row[4]

		# Read them all! In here, k = thread, v = comment
		for k, v in threads.iteritems():

			# Prepare the http request
			print
			print "Requesting thread comments..."
			jsonData = requestJson(baseUrl + urllib2.quote(v.encode('utf8')) + ".json")
			
			# Read the Comments
			# 0 = title
			postData = jsonData[0]['data']['children']
			readComments(postData, k, v, conn, cur)
			# 1 = comments
			data = jsonData[1]['data']['children']
			readComments(data, k, v, conn, cur)

			# See if we're taking too long. If so, get threads so we don't lose the new ones
			commentCount += 1
			print
			print "commentCount = " + str(commentCount)
			print

			if commentCount >= commentLimit:
				commentCount = 0
				print
				print "enough reading comments. reading threads now"
				print
				readThreads(subredditUrl, conn, cur)

	# Finishing time
	endingTime = datetime.datetime.now()

	# Log this run in the database
	print
	print "Finishing up. Logging this run..."
	print "Total new threads: " + str(totalNewThreads)
	print "Total new comments: " + str(totalNewComments)
	print "---------------------------------------------------"
	print
	cur.execute("""INSERT INTO logs (startingTime, endingTime, newThreads, ignoredThreads, newComments, ignoredComments) values (%s, %s, %s, %s, %s, %s)""", (startingTime, endingTime, totalNewThreads, totalExistingThreads, totalNewComments, totalExistingComments))
	conn.commit()

# Close the connection
conn.commit()
cur.close()
conn.close()