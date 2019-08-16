import logging
import json

# setup logging profile
logger = logging.getLogger(__name__)

class CommunicationExt:
	''' Handles project communication and environment.'''

	def __init__(self, ownerComp):
		
		''' operators '''
		self.ownerComp = ownerComp
		self.controller = self.ownerComp.op('Controller')
		self.tcpip_development = self.controller.op('tcpip_development')
		self.tcpip_controller = self.controller.op('tcpip_controller')
		self.payload = self.ownerComp.op('payload')
		
		''' properties '''
		self.Environment = self.ownerComp.par.Environment
		
		logger.info('Initialized...')

	@property
	def Environment(self):
		return self.ownerComp.par.Environment.eval()

	@Environment.setter
	def Environment(self, value):
		self.ownerComp.par.Environment = str(value)
		self.tcpip_controller.par.active = 0
		run("args[0].par.active = 1", self.tcpip_controller, fromOP=me, delayFrames=1)

	@property
	def Sendpayload(self):
		return self.ownerComp.par.Sendpayload.eval()

	@Sendpayload.setter
	def Sendpayload(self, value):
		self.sendMessage()

	
	def sendMessage(self):
		''' Send message to controller via network device'''
		
		message = json.loads(self.payload.op('null_payload').text)
		self.tcpip_development.send(json.dumps(message), terminator='\r\n')