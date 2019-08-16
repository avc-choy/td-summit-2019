import logging
import json
import traceback
import os
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

# setup logging profile
logger = logging.getLogger(__name__)

class Player:
	''' Modular A/B player with ability to adjust number of unique decks '''
	
	def __init__(self, ownerComp):
		
		''' operators '''
		self.ownerComp = parent()
		self.player = ownerComp

		''' storage manager '''
		self.PlayerStored = StorageManager(self, ownerComp, locked=False)

		''' attributes '''
		self.DefaultMedia = self.ownerComp.par.Defaultmedia.eval()
		self._defaultLength = 100
		self._assetPath = self.ownerComp.par.Assetpath.eval()
		self.Demomedia = os.listdir(self._assetPath)

		''' properties '''
		self._Crossfadeduration = tdu.Dependency(self.ownerComp.par.Crossfadeduration)
		self._Imageduration = tdu.Dependency(self.ownerComp.par.Imageduration)
		
		self._decks = self.ownerComp.par.Decks.eval()
		self.Decks = self.ownerComp.par.Decks.eval()
		
		logger.info('Initialized...')
		
	@property
	def Decks(self):
		return self.ownerComp.par.Decks.eval()

	@Decks.setter
	def Decks(self, value):
		if value < self._decks:
			[self.removeDeck(value+deck) for deck in range(self._decks-value)]		
		else:
			[self.addDeck(deck) for deck in range(value)]

		self._decks = value

	@property
	def Crossfadeduration(self):
		return self._Crossfadeduration*me.time.rate

	@property
	def Imageduration(self):
		return self._Imageduration*me.time.rate


	def addDeck(self, value):
		''' Update StorageManager decks '''
		
		# add item to storage manager
		self.PlayerStored._addItem({'name': 'Slot_{}'.format(value), 'default': 0})

	
		self.PlayerStored._addItem({'name': 'Deck_{}_Slot_0'.format(value), 
											'default': {'file': self.DefaultMedia, 
														'length': self._defaultLength}, 
											'dependable': True})
	
		self.PlayerStored._addItem({'name': 'Deck_{}_Slot_1'.format(value), 
											'default': {'file': self.DefaultMedia, 
														'length': self._defaultLength}, 
											'dependable': True})
										
		self.PlayerStored._sync()

	def removeDeck(self, value):

		del self.PlayerStored._items['Slot_{}'.format(value)]
		del self.PlayerStored._items['Deck_{}_Slot_0'.format(value)]
		del self.PlayerStored._items['Deck_{}_Slot_1'.format(value)]

		self.PlayerStored._sync()


	def LoadMedia(self, payload):
		''' Parse 'on-demand' message message from 'Conductor' extension '''

		try:

			for key, value in payload.items():

				# load args
				media = value[0]
				deck = value[1]
				group = 'deck_{}'.format(deck)

				# kill active run delays
				self.killRuns(group)

				# preload incoming media
				self.preloadMedia(group, media, deck)

		except:
			if op.Node.Debug:
				logger.error(traceback.format_exc()) 


	def preloadMedia(self, group, media, deck, playlist=None, frame=0):
		''' preload slot '''

		try:

			# get next slot for deck 
			slot = abs(getattr(self, 'Slot_{}'.format(deck))-1)
	
			# next timer / player
			timer = self.ownerComp.op('deck_{}/timer_slot_{}'.format(deck,slot))
			player = self.ownerComp.op('deck_{}/mov_slot_{}'.format(deck,slot))

			# load remote if sent - otherwise load locally
			if 'http' in media:
				filepath = media
			else:
				# full filepath and filetype of incoming media 
				filepath = '{}{}'.format(self._assetPath, media)
			
			filetype = str(filepath).split('.')[-1]
		
			# if valid media present
			if media and self.validateFile(filepath, filetype):
				
				# set filepath and length attributes for next slot
				setattr(self, "Deck_{}_Slot_{}".format(deck, slot), {'file' : filepath, 'length': self._defaultLength})

				# cue upcoming timer preload upcoming media slot
				op(timer).par.cue = 1
				op(player).preload()

				# not fully preread - run preload check
				if not op(player).isFullyPreRead:
					run("args[0](args[1], args[2], args[3], args[4], args[5], args[6])", 
						self.checkPreload, player, timer, deck, slot, group, filepath, fromOP=me, group=group, delayFrames=1)
				
				# fully preread - play media
				else:
					self.playMedia(deck, slot, player, timer, filepath, group)
	
			else:
				if op.Node.Debug:
					logger.error('Invalid Media: {}'.format(traceback.format_exc()))

		except:
			if op.Node.Debug:
				logger.error(traceback.format_exc())


	def checkPreload(self, player, timer, deck, slot, group, filepath, frame=1):
		''' check preload status '''

		try:

			#  not fully preread - rerun preload check
			if not op(player).isFullyPreRead:
				
				# failed preload - force play anyway - can affect output, use with caution
				if op(player).isInvalid or frame >= me.time.rate:
					self.playMedia(deck, slot, player, timer, filepath, group)
					
					if op.Node.Debug:
						logger.error('Preload Failed: {}'.format(traceback.format_exc()))

				# re-run preload check
				else:
					frame+=1
					run("args[0](args[1], args[2], args[3], args[4], args[5], args[6], args[7])", 
						self.checkPreload, player, timer, deck, slot, group, filepath, frame, fromOP=me, group=group, delayFrames=1)
			
			# fully preread - play media
			else:
				self.playMedia(deck, slot, player, timer, filepath, group)

		except:
			if op.Node.Debug:
				logger.error(traceback.format_exc())

	
	def playMedia(self, deck, slot, player, timer, filepath, group):
		'''play media'''

		try:

			# grab file extension
			extension = filepath.split('.')[-1]

			# set length for movie/image
			length = op(player).numImages
			rate = op(player).rate
			length = length * (me.time.rate/rate)
			if extension in tdu.fileTypes['image']:
				length = self.Image

			# set length
			setattr(self, "Deck_{}_Slot_{}".format(deck, slot), {'file' : filepath, 'length': length})

			# cue deck
			self.ownerComp.op('deck_{}/timer_slot_{}'.format(deck, slot)).par.cue = 0
			self.ownerComp.op('deck_{}/timer_slot_{}'.format(deck, slot)).par.start.pulse()
			run("args[0].op('deck_{}/timer_slot_{}'.format(args[1], args[2])).par.cue = 1", 
				self.ownerComp, deck, abs(slot-1), fromOP=me, group=group, delayFrames=self._Crossfadeduration*me.time.rate)

			# swap deck slot
			setattr(self, 'Slot_{}'.format(deck), slot)

			if op.Node.Debug:
				logger.info('Playing {}'.format(filepath))
					
		except:
			if op.Node.Debug:
				logger.error(traceback.format_exc())


	def validateFile(self, filepath, filetype):
		''' check media file validity '''

		try:
			
			if 'http' not in filepath:
				# does it exist on local drive
				if os.path.isfile(filepath):
					# is it a valid image or movie file
					if filetype in (tdu.fileTypes['image'] + tdu.fileTypes['movie']):
						return True
				else:
					return False
			else:
				return True

		except:
			if op.Node.Debug:
				logger.error(traceback.format_exc())


	def killRuns(self, group):
		''' kill grouped runs '''

		try:
			for i in runs:
				if i.group == group:
					i.kill()
					# logger.info('kill: ' + str(group))
	
		except:
			if op.Node.Debug:
				logger.error(traceback.format_exc())			