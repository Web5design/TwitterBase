import tweetcouch
import couchdb.design

tc = tweetcouch.TweetCouch('twdb')
#tc.delete()
#print 'TWEETS: %d' % tc.tweet_count()
#print 'USERS: %d' % tc.user_count()

"""
for id in tc.db:
	if tc.db[id]['type'] == 'TWITTER_STATUS':
		print tc.db[id]['text']
"""

get_tweets = '''function(doc) {
	if (doc.type == "TWITTER_STATUS")
		emit(doc.id, doc);
}'''

get_users = '''function(doc) {
	if (doc.type == "TWITTER_USER")
		emit(doc.id, doc);
}'''

get_tweets_with_user = '''function(doc) {
	if (doc.type == "TWITTER_STATUS")
		emit([doc.user_id, doc.id], doc);
	else if (doc.type == "TWITTER_USER")
		emit([doc.id, 0], doc);
}'''

count_tweets_map = '''function(doc) {
	if (doc.type == "TWITTER_STATUS")
		emit(doc.id, 1);
}'''

count_tweets_reduce = '''function(keys, values) {
	return sum(values);
}'''

count_type_map = '''function(doc) {
	emit([doc.type, doc.id], 1);
}'''

count_type_reduce = '''function(keys, values) {
	return sum(values);
}'''


"""
# GET TWEET COUNT
for row in tc.db.query(count_tweets_map, count_tweets_reduce):
	print row['value']
"""

"""
# GET TWEET COUNT AND USER COUNT
for row in tc.db.query(count_type_map, count_type_reduce, 
	               group=True, group_level=1, 
	               startkey=['TWITTER_STATUS'], endkey=['TWITTER_STATUS',{}]):
	print row['value']
for row in tc.db.query(count_type_map, count_type_reduce, 
	               group=True, group_level=1, 
	               startkey=['TWITTER_USER'], endkey=['TWITTER_USER',{}]):
	print row['value']
"""

"""
# PERMINANT VIEW
view = couchdb.design.ViewDefinition('twitter', 'count_type', count_type_map, reduce_fun=count_type_reduce)
view.sync(tc.db)
for row in tc.db.view('twitter/count_type', group=True, group_level=1):
	print row
"""


# GET TWEETS SORTED WITH TWO DB CALLS
for row in tc.db.query(get_tweets, limit=10, endkey=376824582130647040-1):
	user_id = row['value']['user_id']
	text = row['value']['text']
	id = row['value']['id']
	for user in tc.db.query(get_users, startkey=user_id, endkey=user_id):
		print '[%s] %s: %s' % (id, user.value['screen_name'], text)


"""
# GET TWEETS UNSORTED WITH ONE DB CALL (JOIN)
#tweets = tc.db.query(get_tweets_with_user)
tweets = tc.db.query(get_tweets_with_user, startkey=[0, 376370854952980500])
#tweets = tc.db.query(get_tweets_with_user, startkey=[0, 376370854952980500], endkey=[0, 376370854952980500])

user = None
for row in tweets:
	type = row['value']['type']
	if type == 'TWITTER_STATUS':
		print '%s: %s' % (user, row['value']['text'])
	elif type == 'TWITTER_USER':
		user =  row['value']['screen_name']
"""
