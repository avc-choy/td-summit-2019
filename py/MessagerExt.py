import logging
import json

# setup logging profile
logger = logging.getLogger(__name__)


class MessagerExt:
	''' Basic text messager using modular and extensible GLSL system '''

	def __init__(self, ownerComp):
		
		# operators
		self.ownerComp = ownerComp
		self.geo_message = self.ownerComp.op('geo_message')

	@property
	def Swapmessage(self):
		return self.ownerComp.par.Swapmessage.eval()

	@Swapmessage.setter
	def Swapmessage(self, pulse):
		index = abs(self.geo_message.op('switch_array').par.index-1)
		self.switchMessage(index)


	def Run(self, message):
		''' Handle incoming messages '''
	
		# pull message index
		index = message['messager'].get('message', 0)
		
		# switch message
		self.switchMessage(index)

	
	def switchMessage(self, index):
		''' Switch to message new message via index '''
		
		# switch operators
		self.geo_message.op('switch_array').par.index = index
		self.geo_message.op('switch_text').par.input = index