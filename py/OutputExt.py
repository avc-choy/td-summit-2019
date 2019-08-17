import logging 

# setup logging profile
logger = logging.getLogger(__name__)

class OutputExt:

	def __init__(self, ownerComp):

		# operators
		self.ownerComp = ownerComp
		self.node = op.Node
		
		# configure output for mode
		self.setupOutput()
		
		logger.info('Initialized...')


	def setupOutput(self):
		''' Setup output based on activation '''

		# player
		if self.node.Node['mode'] == 'player':
			for deck in range(4):
				self.ownerComp.op('select_player_{}'.format(deck)).par.top = '../Player/deck_{}/null_deck'.format(deck)
			self.ownerComp.op('select_messager').par.top = ''

		# messager
		elif self.node.Node['mode'] == 'messager':
			for deck in range(4):
				self.ownerComp.op('select_player_{}'.format(deck)).par.top = ''
			self.ownerComp.op('select_messager').par.top = '../Messager/null_messager'