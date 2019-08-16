import os
import logging

# setup logging profile
logger = logging.getLogger(__name__)

class ExternalFileExt:

	def __init__(self, ownerComp):

		# operators
		self.ownerComp = ownerComp
		
		# external file attributes
		self.Tag = 'EXT'
		self.Extensions = ['.py', '.glsl', '.json', '.xml', '.txt', None] 
		self.filePath = ''
		self.fileName = ''
		self.fileType = ''

		# message box info
		self.externalDat = 'This DAT is not yet externalized...\n\nWould you like to create a new file or reference an existing file?'
		self.externalType = 'What type of file would you like to externalize?'
		self.externalOverwrite =  'Would you like to overwrite the existing external file?'
		self.externalExists = 'This DAT is already externalized. Would you like to create a new external file?'
		self.buttonsConfirm = ['Yes', 'No']
		self.buttonsReference = ['New', 'Existing']
		
		logger.info('Initialized...')


	def ExternalizeFile(self):
		''' Externalize currently selected DAT to file '''

		# file information
		if len(ui.panes.current.owner.children) > 0:
			dat = op(ui.panes.current.owner.currentChild)
			if dat.OPType == 'textDAT':
				name = dat.name
				text = dat.text
				file = dat.par.file

				# not currently externalized
				if file == '':

					# prompt user to handle externalization
					reference = ui.messageBox('Externalize File', self.externalDat, 
											   buttons=self.buttonsReference)	

					# create new file
					if not reference:
						ext = ui.messageBox('File Type', self.externalType, buttons=self.Extensions[:-1])				

						# generate file info
						self.fileType = self.Extensions[ext]
						if self.fileType:
							self.filePath = '{}/{}/'.format(project.folder, self.fileType.strip('.'))
							self.fileName = '{}{}'.format(name, self.fileType)
							
							# handle if file already exists
							fileExists = os.path.exists(self.filePath + self.fileName)
							if fileExists:
								fileExists = ui.messageBox('File Exists', self.externalOverwrite +
															'\n\n{}'.format(self.filePath + self.fileName), 
															buttons=self.buttonsConfirm)
							if not fileExists:

									# create external file
									self.createFile(text)

									# update externalized DAT
									self.initDat(dat, self.filePath + self.fileName)

					# reference existing file
					else:

						# prompt user to select file
						if reference > 0:
							file = ui.chooseFile(start=project.folder, fileTypes=self.Extensions, 
												 title='Choose File...')
							
							# udpate externalized DAT
							if file:
								self.fileType = file.split('.')[-1]
								self.initDat(dat, file)

				# DAT referencing an external file
				else:
					# match on filesystem - prompt user
					if os.path.exists(tdu.expandPath(file)):
						duplicate = ui.messageBox('Externalize File', self.externalExists + 
												  '\n\n{}'.format(file), buttons=self.buttonsConfirm)
						if not duplicate:
						
							# recurse to handle file externalization
							dat.par.file = ''
							run("args[0]()", self.ExternalizeFile, fromOP=self.ownerComp, delayFrames=1)

					# no file match on filesystem 
					else:

						# recurse to handle file externalization
						dat.par.file = ''
						run("args[0]()", self.ExternalizeFile, fromOP=self.ownerComp, delayFrames=1)
	

	def initDat(self, dat, file, ext=True):
		''' Initialize newly externalized DAT '''

		# setup text DAT
		dat.par.file = tdu.collapsePath(file)
		dat.par.loadonstart = True
		dat.par.write = True
		dat.par.loadonstartpulse.pulse()
		dat.par.syncfile = True
		dat.par.extension = 'customext'
		dat.par.customext = self.fileType
		dat.tags.add(self.Tag)
		dat.color = (parent().par.Externalfilecolorr.val, 
					 parent().par.Externalfilecolorg.val, 
					 parent().par.Externalfilecolorb.val)

		# force cook OP
		dat.cook(force=True)

		# flash network background
		self.confirmExternalization()


	def confirmExternalization(self):
		''' Visually flash network background to confirm successful externalization '''

		# flash color
		ui.colors['worksheet.bg'] = (parent().par.Externalfilecolorr.val, 
									 parent().par.Externalfilecolorg.val, 
									 parent().par.Externalfilecolorb.val)
		
		# reset to default
		defaultWorksheet = (0.10000000149011612, 0.10499999672174454, 0.11999999731779099)
		run("ui.colors['worksheet.bg'] = args[0][0], args[0][1], args[0][2]", 
										 defaultWorksheet, fromOP=self.ownerComp, 
										 delayFrames=1)


	def createFile(self, text):
		''' Create file on local filesystem '''

		# check directory exists - create if necessary
		if not os.path.exists(self.filePath):
			os.mkdir(self.filePath)
	
		# save file
		with open(self.filePath + self.fileName, 'w') as file:
			file.write(text)
			file.close()