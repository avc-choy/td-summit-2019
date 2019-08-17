from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
import json
import logging
import traceback

# setup logging profile
logger = logging.getLogger(__name__)

class ControllerExt():
	''' Handles incoming messages.'''

	def __init__(self, ownerComp):
		
		''' operators '''
		self.ownerComp = ownerComp
		self.node = op.Node
		self.tcpip_controller = self.ownerComp.op('tcpip_controller')

		''' properties '''	
		self.ownerComp.unstore('*')
		storedController = [{'name':'Commands', 'default':  {'show': self.routeMessage}}]
		self.ControllerStored = StorageManager(self, ownerComp, storedController)


	def OnReceive(self, message):
		''' Routes incoming messages, logs messages and handles exceptions. '''

		if len(message) > 0:

			# load Controller message/command
			payload = json.loads(message)
			command = payload.get('command', None)

			# raw message dump/display
			self.ownerComp.op('text_controller').text = json.dumps(payload, sort_keys=True, indent=4)

			# handle message
			try:
				if type(payload) is dict:

					# route Controller message to handler
					if command in self.Commands:
						run("args[0]", self.Commands[command](**payload))
					else:
						if self.node.Debug:
							logger.error('Invalid Command: {}'.format(traceback.format_exc()))
				else:
					if self.node.Debug:
						logger.error('Invalid Type: {}'.format(traceback.format_exc()))

			# handle exception
			except:
				if self.node.Debug:
					logger.error('Invalid JSON or parsing exception: {}'.format(traceback.format_exc()))

		else:
			if self.node.Debug:
				logger.info('Empty JSON: {}'.format(traceback.format_exc()))


	def OnConnect(self, peer):
		''' Log controller connections '''

		onConnect = 'Controller CONNECTED to {} - {}:{}'.format(peer.owner,
					 											peer.address,
																peer.port)
		if self.node.Debug:
			logger.warning(onConnect)


	def OnClose(self, peer):
		''' Log controller disconnections '''

		onClose = 'Controller DISCONNECTED from {} - {}:{}'.format(peer.owner,
					 											     peer.address,
																     peer.port)
		if self.node.Debug:
			logger.warning(onClose)
	

	def routeMessage(self, **kwargs):
		''' Process command '''

		# show data
		data = kwargs.get('parameters', None)
		
		# route data to module
		mode = self.node.Node['mode'].title()

		# run 'Setup' for Player
		run("args[0].{}(args[1])".format('Run'), op('/Node/{}'.format(mode)), data)
		
		if self.node.Debug:
			logger.info(json.dumps(data, sort_keys=True, indent=4))