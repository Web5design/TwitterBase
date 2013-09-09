import argparse
import codecs
import os
import tweetcouch
import sys
from TwitterAPI.TwitterOAuth import TwitterOAuth
from TwitterAPI.TwitterAPI import TwitterAPI


# -dbname twdb2 -oauth credentials.txt -endpoint statuses/filter -parameters track=zzz
CONFIG = 'twitterbase.cfg'
LOG = None


def to_dict(param_list):
	"""Convert a list of key=value to dict[key]=value"""			
	if param_list:
		return {name: value for (name, value) in [param.split('=') for param in param_list]}
	else:
		return None


def run(log):
	global LOG
	LOG = log

	parser = argparse.ArgumentParser(description='Request any Twitter Streaming or REST API endpoint')
	parser.add_argument('-dbname', metavar='DBNAME', type=str, help='database name')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='file containing OAuth credentials')
	parser.add_argument('-endpoint', metavar='ENDPOINT', type=str, help='Twitter endpoint', required=True)
	parser.add_argument('-parameters', metavar='NAME_VALUE', type=str, help='parameter NAME=VALUE', nargs='+')

	with open(CONFIG) as f:
		args = f.read()
		args = parser.parse_args(args.split())	

	params = to_dict(args.parameters)
	o = TwitterOAuth.read_file(args.oauth)
	api = TwitterAPI(o.consumer_key, o.consumer_secret, o.access_token_key, o.access_token_secret)

	storage = tweetcouch.TweetCouch(args.dbname)

	while True:
		try:
			api.request(args.endpoint, params)
			iter = api.get_iterator()
		
			for item in iter:
				if 'message' in item:
					LOG.write('ERROR %s: %s\n' % (item['code'], item['message']))
				elif 'text' in item:
					storage.save_tweet(item)
				elif 'limit' in item:
					pass # count skipped tweets
						
		except KeyboardInterrupt:
			LOG.write('\nTerminated by user\n')
			break
		
		except Exception as e:
			LOG.write('*** STOPPED %s\n' % str(e))


if __name__ == '__main__':
	try:
		# python 3
		sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)
		
	except:
		# python 2
		sys.stdout = codecs.getwriter('utf8')(sys.stdout)
		
	run(sys.stdout)