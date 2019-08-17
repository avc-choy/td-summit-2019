from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
import json
import os
import socket
import sys
import traceback
import logging

# setup logging profile
logger = logging.getLogger(__name__)


class NodeExt:
	'''Handles the loading of server/client networks based off of system config file - if applicable.'''
	
	def __init__(self, ownerComp):

		''' operators '''
		self.ownerComp = ownerComp

		''' properties '''
		self.ownerComp.unstore('NodeExtStored')
		self.NodeStored = StorageManager(self, ownerComp, self.storeConfig(self.loadConfig()))
		
		# node network info
		hostname =socket.gethostname()
		self.Node['hostname'] = hostname
		self.Node['ip'] = socket.gethostbyname(socket.gethostname())
		self.Node['host'] = self.Hosts.get(hostname, self.Hosts.get('default'))
		logger.info('Node Configuration: {}'.format(hostname.upper()))

		logger.info('Initialized...')

	@property
	def Reinitialize(self):
		return self.ownerComp.par.Reinitialize.eval()

	@Reinitialize.setter
	def Reinitialize(self, pulse):
		self.ownerComp.par.reinitextensions.pulse()
		self.Initialize()

	@property
	def Debug(self):
		return self.ownerComp.par.Debug.eval()


	def loadConfig(self):
		
		try:
			config = {'config': '{}/config.json'.format(project.folder)}
			for key, val in config.items():
				return json.loads(open(val, 'r').read())
		
		except ValueError as e:
			logger.critical(traceback.format_exc())

 
	def storeConfig(self, config):

		nodeStored = []
		for key, val in config.items():
			nodeStored.append({'name': key.title(), 'default': val})
		nodeStored.append({'name':'Node', 'default': config['activations'][int(var('NODE'))], 'dependable':True})

		return nodeStored


	def Initialize(self):
		
		try:
			self.loadNode()
			run("args[0]()", self.initNode, fromOP=self.ownerComp, delayFrames=me.time.rate)
		except Exception as e:
			logger.critical(traceback.format_exc())


	def loadNode(self):
		'''Loads network based off local node config.'''

		# destroy existing network
		network = parent().findChildren(type=COMP, depth=1)
		[op(node).destroy() for node in network]

		# load network
		for tox in range(len(self.Node['tox'])):
			parent.node.loadTox('tox/' + self.Node['tox'][tox][0])
			node = op(self.Node['tox'][tox][0].split('.')[0])
			node.nodeX = self.Node['tox'][tox][1]
			node.nodeY = self.Node['tox'][tox][2]

		# set window size
		self.ownerComp.par.w = self.Node.get('resolution', 1920)[0]
		self.ownerComp.par.h = self.Node.get('resolution', 1080)[1]

		# handle realtime
		project.realTime = self.Node.get('realtime', True)


	def initNode(self):
		''' Manually initialize components '''

		# search for INIT tag and reinit extensions
		initComps = self.ownerComp.findChildren(tags=['INIT'])
		[comp.par.reinitextensions.pulse() for comp in initComps]
