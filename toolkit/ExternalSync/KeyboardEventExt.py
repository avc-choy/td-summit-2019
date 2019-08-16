import logging

# setup logging profile
logger = logging.getLogger(__name__)

class KeyboardEventExt:

	def __init__(self, ownerComp):
		
		# operators
		self.ownerComp = ownerComp
		
		self.keyCallbacks = {}
		run("args[0].keyCallbacks = {'e': args[1].ExternalizeFile,'s': args[1].ExternalizeTox, 'd': args[1].ExternalizeDirtyTox}",
					    			 self, self.ownerComp, fromOP=self.ownerComp, delayFrames=1)
		
		logger.info('Initialized...')
		
		
	def OnKey(self, state, ctrl, alt, key):
		''' Lookup function call on key event '''
				
		# lookup callback
		if state and ctrl and alt and key:
			self.keyCallbacks[key]()