# Jonas Geduldig - 9.sep.2013
# TwitterBaseService.py

"""
	To install and run the service from the command line:
	> python twitterbaseservice.py install

	To stop and uninstall the service from the command line:
	> python twitterbaseservice.py stop
	> sc delete twitterbase
"""


import argparse
import WinService
import twitterbase


class TwitterBaseService(WinService.Service):
	def start(self):
		self.runflag=True
		twitterbase.run(self)

	def stop(self):
		self.runflag=False


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Stream twitter to database')
	parser.add_argument('-action', metavar='ACTION', type=str, help='service action (install, start, stop, restart, status)')
	args = parser.parse_args()	
	
	if args.action == 'install':
		WinService.install(TwitterBaseService, 'twitterbase')
	elif args.action == 'start':
		WinService.start('twitterbase')
	elif args.action == 'stop':
		WinService.stop('twitterbase')
	elif args.action == 'restart':
		WinService.restart('twitterbase')
	elif args.action == 'status':
		WinService.status('twitterbase')
	else:
		WinService.status('twitterbase')