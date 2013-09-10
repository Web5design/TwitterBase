# Jonas Geduldig - march.16.2010
# WinService.py
# Manages a Windows service.  Use it this way:

'''
import WinService
class MyService(WinService.Service):
	def start(self):
		self.runflag=True
		# START YOUR APP HERE
	def stop(self):
		self.runflag=False
WinService.install(MyService, 'MyService')
'''

from os.path import splitext, abspath
from sys import executable
from sys import modules
import servicemanager
import win32serviceutil
import win32service
import win32event
import win32api


class Service(win32serviceutil.ServiceFramework):
	_svc_name_ = '_unNamed'
	_svc_display_name_ = '_Service Template'
	
	def __init__(self, *args):
		win32serviceutil.ServiceFramework.__init__(self, *args)
		self.log('init')
		self.stop_event = win32event.CreateEvent(None, 0, 0, None)
		
	def write(self, msg):
		msg = msg.strip()
		if msg != '':
			self.log(msg)
		
	def log(self, msg):
		servicemanager.LogInfoMsg(str(msg))

	def sleep(self, sec):
		win32api.Sleep(sec*1000, True)
				
	def SvcDoRun(self):
		self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
		try:
			self.ReportServiceStatus(win32service.SERVICE_RUNNING)
			self.log('starting')
			self.start()
			self.log('started')
			win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
			self.log('done')
		except Exception, x:
			self.log('Exception: %s' % x)
			self.SvcStop()
			
	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.log('stopping')
		self.stop()
		self.log('stopped')
		win32event.SetEvent(self.stop_event)
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)
		
	# to be overridden
	def start(self): pass
	def stop(self): pass

	
def install(cls, name, display_name=None, stay_alive=True):
	cls._svc_name_ = name
	cls._svc_display_name_ = display_name or name
	try:
		module_path = modules[cls.__module__].__file__
	except AttributeError:
		module_path=executable
	module_file = splitext(abspath(module_path))[0]
	cls._svc_reg_class_ = '%s.%s' % (module_file, cls.__name__)
	if stay_alive: 
		win32api.SetConsoleCtrlHandler(lambda x: True, True)
	try:
		win32serviceutil.InstallService(
			cls._svc_reg_class_,
			cls._svc_name_,
			cls._svc_display_name_,
			startType=win32service.SERVICE_AUTO_START
		)
		print 'Install ok'
		win32serviceutil.StartService(cls._svc_name_)
		print 'Start ok'
	except Exception, x:
		print str(x)
		
def start(display_name):
	try:
		win32serviceutil.StartService(display_name)
		print 'Start ok'
	except Exception, x:
		print str(x)
		
def stop(display_name):
	try:
		win32serviceutil.StopService(display_name)
		print 'Stop ok'
	except Exception, x:
		print str(x)
		
def restart(display_name):
	try:
		win32serviceutil.RestartService(display_name)
		print 'Restart ok'
	except Exception, x:
		print str(x)
		
def status(display_name):
	try:
		if win32serviceutil.QueryServiceStatus(display_name)[1] == 4:
			print '%s is running' % display_name
		else:
			print '%s is NOT running' % display_name
	except Exception, x:
		print str(x)
