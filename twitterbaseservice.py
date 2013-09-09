# Jonas Geduldig - 9.sep.2013
# TwitterBaseService.py
# 1. run to install and start the service
# 2. stop service and run "sc delete twitterbase" to remove the service

import WinService
import twitterbase

class TwitterBaseService(WinService.Service):
	def start(self):
		self.runflag=True
		twitterbase.run(self)

	def stop(self):
		self.runflag=False
		
WinService.install(TwitterBaseService, 'twitterbase')