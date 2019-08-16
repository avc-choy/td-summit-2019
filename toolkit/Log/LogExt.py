import json
import os
import socket
import datetime
import logging
from logging import Formatter, handlers, config

# setup logging profile
logger = logging.getLogger(__name__)

class LogExt:
	''' LogExt handles loading root loggers for use project wide'''

	def __init__(self, ownerComp):
		
		# operators
		self.ownerComp = ownerComp

		# load logging dictionary config from JSON file
		# with open('log/config.json') as f:
		# 	configDict = json.load(f)
		# 	logging.config.dictConfig(configDict)
		
		# logging dictionary config
		LOGGERS = { 
			'version': 1,
			'disable_existing_loggers': False,
			'formatters': { 
				'textport': { 
					'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
					'datefmt': '%y-%m-%d %H:%M:%S'
					},
				'file': { 
					'()': JsonFormatter,
					'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
					'datefmt': '%y-%m-%d %H:%M:%S'
				}
			},
			
			'handlers': { 
				'textport':{
			 		'class': 'logging.StreamHandler',
			 		'formatter': 'textport',
			 		'stream' : 'ext://sys.stdout',
			 		'level': 'DEBUG'
				},
				'file': { 
					'class': 'logging.handlers.TimedRotatingFileHandler',
					# '()': CustomTimedRotatingFileHandler,
					'formatter': 'file',
					'filename': 'log/{}'.format(datetime.date.today().strftime('%Y-%m-%d_%H-%M-%S')),
					'when': self.ownerComp.par.When.eval(),
					'interval': self.ownerComp.par.Interval.eval(),
					'backupCount': self.ownerComp.par.Backupcount.eval(),
					'level': self.ownerComp.par.Level.eval()
				}
			},
			'loggers': { 
				'': {  # root
					'handlers': ['textport', 'file'],
					'level': 'DEBUG'
				}
			} 
		}
		
		# configure logger
		logging.config.dictConfig(LOGGERS)
		# run("args[0](args[1])", logging.config.dictConfig, LOGGERS, fromOP=self.ownerComp, delayFrames=me.time.rate)
		
		logger.info('Initialized...')


class JsonFormatter(logging.Formatter):
	''' JSONFormatter class formatter outputs Python log records in JSON format '''

	def __init__(self, fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s', 
					   datefmt='%y-%m-%d %H:%M:%S'):

		self.fmt = fmt
		self.datefmt = datefmt

	def _formatJson(self, record):
		''' Convert to JSON '''

		# add attribute to record if included in format string
		formatRecord = {attr: getattr(record, attr) for attr in vars(record) if attr in self.fmt}
		formatRecord['timestamp'] = formatRecord.pop('asctime')
		
		# add heartbeat info
		formatRecord['machine'] = op.Node.Node.get('hostname', socket.gethostname())
		formatRecord['role'] = op.Node.Node.get('name', '')
		formatRecord['heartbeat'] = op.Monitor.GetStatus()

		return formatRecord

	def format(self, record):
		''' Overridde from native class to take a log record and output a JSON formatted string '''

		# convert record to JSON
		jsonRecord = self._formatJson(record)
		return json.dumps(jsonRecord, sort_keys=True, indent=4)