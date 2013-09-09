import couchdb
from couchdb.design import ViewDefinition


class TweetCouch(object):
	def __init__(self, dbname):
		self.server = couchdb.Server()
		try:
			self.db = self.server.create(dbname)
			self._create_views()
		except:
			self.db = self.server[dbname]

	def _create_views(self):
		# twitter/count_type
		count_type_map = 'function(doc) { emit([doc.type, doc.id], 1); }'
		count_type_reduce = 'function(keys, values) { return sum(values); }'
		view = ViewDefinition('twitter', 'count_type', count_type_map, reduce_fun=count_type_reduce)
		view.sync(self.db)

		# twitter/get_tweets
		get_tweets = 'function(doc) { if (doc.type == "TWITTER_STATUS") emit(doc.id, doc); }'
		view = ViewDefinition('twitter', 'get_tweet', get_tweets)
		view.sync(self.db)

		# twitter/get_users
		get_users = 'function(doc) { if (doc.type == "TWITTER_USER") emit(doc.id, doc); }'
		view = ViewDefinition('twitter', 'get_users', get_users)
		view.sync(self.db)

	def tweet_count(self):
		for row in self.db.view('twitter/count_type', group=True, group_level=1,
		                        startkey=['TWITTER_STATUS'], endkey=['TWITTER_STATUS',{}]):
        		return row['value']
		return -1

	def user_count(self):
		for row in self.db.view('twitter/count_type', group=True, group_level=1,
		                        startkey=['TWITTER_USER'], endkey=['TWITTER_USER',{}]):
        		return row['value']
		return -1

	def delete(self):
		self.server.delete(self.db.name)

	def tidy(self):
		self.db.compact()
		self.db.cleanup()

	def save_tweet(self, tw):
		if 'retweeted_status' in tw:
			self.save_tweet(tw['retweeted_status'])
		self.save_user(tw['user'])
		doc = {
			'type':                    'TWITTER_STATUS',
 			'coordinates':             tw['coordinates']['coordinates'] if tw['coordinates'] else None,
 			'creates_at':              tw['created_at'],
			'entities':                tw['entities'],
 			'favorite_count':          tw['favorite_count'],
			'id':                      tw['id'],
			'in_reply_to_screen_name': tw['in_reply_to_screen_name'],
			'in_reply_to_status_id':   tw['in_reply_to_status_id'],
			'in_reply_to_user_id':     tw['in_reply_to_user_id'],
			'lang':                    tw['lang'],
			'place':                   tw['place'],
			'retweet_count':           tw['retweet_count'],
			'retweeted_status_id':     tw['retweeted_status']['id'] if 'retweeted_status' in tw else None,
			'source':                  tw['source'],
			'text':                    tw['text'],
			'truncated':               tw['truncated'],
			'user_id':                 tw['user']['id']
		}
		self.db.save(doc)
		
	def save_user(self, user):
		doc = {
			'type':              'TWITTER_USER',
			'created_at':        user['created_at'],
			'description':       user['description'],
			'entities':          user['entities'] if 'entities' in user else None,
			'favourites_count':  user['favourites_count'],
			'followers_count':   user['followers_count'],
			'friends_count':     user['friends_count'],
			'geo_enabled':       user['geo_enabled'],
			'id':                user['id'],
			'lang':              user['lang'],
			'location':          user['location'],
			'name':              user['name'],
			'profile_image_url': user['profile_image_url'],
			'screen_name':       user['screen_name'],
			'statuses_count':    user['statuses_count'],
			'url':               user['url'],
			'utc_offset':        user['utc_offset'],
			'verified':          user['verified']
		}
		self.db.save(doc)
