import os
import logging

# setup logging profile
logger = logging.getLogger(__name__)

class ExternalToxExt:

	def __init__(self, ownerComp):

		# operators
		self.ownerComp = ownerComp
		
		# tox attributes
		self.externalTox = []
		self.dirtyTox = []

		# message box info
		self.externalOverwrite = 'Would you like to overwrite the existing external TOX?'
		self.externalCreate = 'Would you like to create a new external TOX?'
		self.externalConfirm = 'Which TOX from the component tree would you like to save?'
		self.dirtyTox = 'There are no dirty external TOX to save...'
		self.buttonsConfirm = ['Yes', 'No']
		
		logger.info('Initialized...')
	
	# properties 
	@property
	def externalToxDirectory(self):
		return self.ownerComp.par.Externaltoxdirectory.eval()


	def ExternalizeTox(self):
		''' Externalize single TOX from COMP tree '''

		# search COMP tree
		self.toxTree(ui.panes.current.owner)

		# prompt user to save
		tox = ui.messageBox('Confirm TOX', self.externalConfirm, 
							buttons=['{}.tox'.format(tox[0]) for tox in self.externalTox])
		if tox >= 0:
			self.saveTox(self.externalTox[tox][0], self.externalTox[tox][1])


	def ExternalizeDirtyTox(self):
		''' Search entire network COMP tree and save any dirty external TOX '''

		# find dirty external COMPs from root
		self.dirtyTree = [self.saveTox(op(tox.path), tox.par.externaltox) 
						  for tox in root.findChildren(type=COMP) 
					  	  if tox.par.externaltox and tox.dirty]

		# no dirty TOX
		if self.dirtyTree == []:
			ui.messageBox('Dirty TOX', self.dirtyTox)
		

	def toxTree(self, parent):
		''' Search COMP tree hierachy for all external TOX '''

		# reset external TOX list
		if parent == ui.panes.current.owner:
			self.externalTox = []

		# recurse to root
		if parent is not root:
	
			# parent external tox file
			externalTox = parent.par.externaltox

			# external tox found or current COMP
			if externalTox or parent == ui.panes.current.owner:
				
				# current tox not externalized - use default TOX directory
				if parent == ui.panes.current.owner and not externalTox:
					externalTox = '{}/{}.tox'.format(self.externalToxDirectory, parent.name)
				
				# add to external comp tree
				self.externalTox.append([parent.path, externalTox])

			# recurse comp tree to root
			self.toxTree(parent.parent())

		# root
		else:
			return
			

	def saveTox(self, comp, tox):

		# handle tox state
		toxExists = os.path.exists(tdu.expandPath(tox))
		if toxExists:
			toxExists = ui.messageBox('TOX Exists', self.externalOverwrite +
									  '\n\n{}'.format(tox), 
								      buttons=self.buttonsConfirm)
		else:
			toxExists = ui.messageBox('TOX Create', self.externalCreate +
								      '\n\n{}'.format(tox), 
									  buttons=self.buttonsConfirm)
	
		# creating new or overriding existing tox
		if not toxExists:
			
			# make directory if tox reference non-existing directory
			directory = os.path.dirname(tdu.expandPath(tox))
			if not os.path.exists(directory):
				os.mkdir(directory)

			# save external tox
			op(comp).par.externaltox = tox
			op(comp).save(tox)
			op(comp).color = (parent().par.Externaltoxcolorr.val, 
							  parent().par.Externaltoxcolorg.val, 
						      parent().par.Externaltoxcolorb.val)

			# flash network background
			self.confirmExternalization()


	def confirmExternalization(self):
		''' Visually flash network background to confirm successful externalization '''

		# flash color
		ui.colors['worksheet.bg'] = (parent().par.Externaltoxcolorr.val, 
									 parent().par.Externaltoxcolorg.val, 
									 parent().par.Externaltoxcolorb.val)
		
		# reset to default
		defaultWorksheet = (0.10000000149011612, 0.10499999672174454, 0.11999999731779099)
		run("ui.colors['worksheet.bg'] = args[0][0], args[0][1], args[0][2]", 
										 defaultWorksheet, fromOP=self.ownerComp, 
										 delayFrames=1)