from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
import json
import os
import socket
import time
import sys
import logging
import traceback

# setup logging profile
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ConductorExt():
	''' Handles incoming messages.'''

	def __init__(self, ownerComp):
		
		''' operators '''
		self.ownerComp = ownerComp
		self.node = parent.node
		self.conductor = parent.communication
		self.tcpip_conductor = self.conductor.op('tcpip_conductor')

		''' initializations '''
		self.ownerComp.unstore('*')
		
		''' attributes '''
	
		''' properties '''	
		
		''' stored items - persistent across saves and reinitializations '''
		storedConductor = [{'name':'Commands', 'default':  {'init': self.Init, 'show': self.Show}}]
		self.ConductorStored = StorageManager(self, ownerComp, storedConductor)


	def Route(self, message):
		''' Routes incoming messages, logs messages and handles exceptions. '''

		if len(message) > 0:

			# load conductor message/command
			payload = json.loads(message)
			command = payload.get('command', None)

			# raw message dump/display
			if command != 'init':
 				self.tcpip_conductor.text = json.dumps(payload, sort_keys=True, indent=4)

			# handle message
			try:
				if type(payload) is dict:

					# route conductor message to handler
					if command in self.Commands:
						run("args[0]", self.Commands[command](**payload))
					else:
						logger.error('Invalid Command: ' + str(command))
						# op.rms.Exception(traceback='Invalid Command: ' + str(command))
				else:
					logger.error('Invalid Type: ' + str(type(payload)))
					# op.rms.Exception(traceback='Invalid Type: ' + str(type(payload)))

			# handle exception
			except Exception as e:

				# log to local textport
				logger.exception(e)
				logger.error('Invalid JSON or parsing exception')

				# send exception to RMS
				# op.rms.Exception(traceback='Invalid JSON or parsing exception' + str(traceback.format_exc()))

		else:
			logger.info('Empty JSON')
			# op.rms.Exception(traceback='Empty JSON')


	def Init(self, **kwargs):
		''' Conductor initialization '''

		# init 
		init = {}
		init['command'] = 'init'
		init['client_id'] = self.node.Environments[parent.communication.Environment]['client_id']
		init['screen'] = self.node.Node['screen']

		# send init to conductor
		self.tcpip_conductor.send(json.dumps(init), terminator='\r\n')

		logger.info(json.dumps(init, sort_keys=True, indent=4))
	

	def Show(self, **kwargs):
		''' Process command '''

		# show data
		parameters = kwargs.get('parameters', None)
		
		# route data to module
		mode = self.node.Node['mode']
		run("args[0].{}(args[1])".format('Setup'), op('/node/{}'.format(mode)).upper(), parameters)
		
		# logger.info(json.dumps(parameters, sort_keys=True, indent=4))