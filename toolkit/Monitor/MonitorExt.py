import json
import time
import logging

# setup logging profile
logger = logging.getLogger(__name__)

class MonitorExt():
	'''Heartbeat reporting'''

	def __init__(self, ownerComp):
		
		''' operators '''
		self.ownerComp = ownerComp
		self.node = op.Node
		self.controller = op.Controller
		self.tcpip_controller = self.controller.op('tcpip_controller')
		self.info_controller = self.controller.op('info_controller')
		self.perform_monitor = self.ownerComp.op('perform_monitor')
		self.timer_monitor = self.ownerComp.op('timer_monitor')

		''' attributes '''
		self.connection = {False: 'disconnected', True: 'connected'}
		
		logger.info('Initialized...')

	@property
	def Monitor(self):
		return self.ownerComp.par.Monitor.eval()

	@Monitor.setter
	def Monitor(self, value):
		self.ownerComp.par.Monitor = value
		self.timer_monitor.par.start.pulse()
		if op.Node.Debug:
			logger.warning('Monitoring {}...'.format(self.connection[bool(value)]).title())


	def isConnected(self):
		''' Return controller connection - force reconnect if disconnected'''

		# check connection
		socket = bool(self.info_controller['connections'])
		
		# close and reconnect socket if disconnected
		if not socket:
			logger.critical('Controller Disconnected...')
			self.tcpip_controller.par.active = 0
			run("args[0].par.active = 1", self.tcpip_controller, fromOP=self.ownerComp, delayFrames=1)

		# return controller connection
		return self.connection[socket]


	def GetStatus(self):
		
		# pull heartbeat parameters from perform CHOP
		status = dict(zip([par.name for par in self.perform_monitor.chans()], 
							 [par[0] for par in self.perform_monitor.chans()]))
				
		return status


	def Heartbeat(self):
		'''Rms heartbeat'''

		# pull heartbeat parameters from perform CHOP
		heartbeat = dict(zip([par.name for par in self.perform_monitor.chans()], 
							 [par[0] for par in self.perform_monitor.chans()]))
		
		# pull controller connection
		heartbeat['controller'] = self.isConnected()
		
		logger.info(heartbeat)