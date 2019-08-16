import logging 

# setup logging profile
logger = logging.getLogger(__name__)

class OutputExt:

	def __init__(self, ownerComp):

		self.ownerComp = ownerComp
		
		logger.info('Initialized...')