import logging 
import random
import traceback
import json
import os

# setup logging profile
logger = logging.getLogger(__name__)

# inherit modules
Player = mod(op.PlayerMod.op('PlayerMod')).Player

class PlayerExt(Player):

	def __init__(self, ownerComp):

		# inherit base player constructor
		Player.__init__(self, ownerComp)
		
		# operators
		self.ownerComp = ownerComp
		self.node = op.Node

		# setup op parameters
		self.setupPars()
		run("args[0]()", self.initTimers, fromOP=self.ownerComp, delayFrames=1)
		
		logger.info('Initialized...')

	@property
	def Demo(self):
		return self.ownerComp.par.Demo.eval()

	@Demo.setter
	def Demo(self, pulse):
		self.DemoMedia(self.Demomedia)

	@property
	def Debug(self):
		return self.ownerComp.par.Debug.eval()

	@Debug.setter
	def Debug(self, value):
		self.ownerComp.par.Deubg = value
		

	def Run(self, data):
		''' Handler for incoming messages to Player '''

		# pull media from payload
		media = data.get('player')

		# call base call media loader
		self.LoadMedia(media)


	def setupPars(self):
		''' Load each deck op parameters from config file '''

		try:

			# pull player config
			player = self.node.Node.get('player')
			
			# each deck
			for key in player.keys():
				
				# pulled tagged ops for parameter editing
				tags = self.ownerComp.op(key).findChildren(tags=['PLAYER'])
				
				# pull key matching op type from config
				for operator in tags:
					params = player[key].get(operator.type)
					
					# set each op parameter in key to config value
					for par in params:
						setattr(operator.par, par, params.get(par))
						# print(operator.par, par, params.get(par))

			if self.node.Debug:
				logger.info('Player Pars Setup...')

		except:
			if self.node.Debug:
				logger.error(traceback.format_exc())
	

	def initTimers(self):
		''' Initialize all player timers '''

		tags = self.ownerComp.findChildren(tags=['TIMER'], depth=2)
		[timer.par.initialize.pulse() for timer in tags]
	

	def DemoMedia(self, demoMedia):
		''' Play random selection of assets from default asset path '''		
		
		try:
	
			# generate demo payload
			player = {}
			for deck in range(random.randint(1,4)):
				player[deck] = [demoMedia[random.randint(0,4)], deck]

			payload = {
				"parameters": {
					"player": player
				}
			}

			# pull player media
			data = payload.get('parameters').get('player')
		
			# call base call media loader
			self.LoadMedia(data)

			if self.node.Debug:
				logger.info(json.dumps(payload, sort_keys=True, indent=4))

		except:
			if self.node.Debug:
				logger.error(traceback.format_exc())