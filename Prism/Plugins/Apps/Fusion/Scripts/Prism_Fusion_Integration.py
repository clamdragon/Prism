# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2018 Richard Frangenberg
#
# Licensed under GNU GPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.



try:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2.QtWidgets import *
	psVersion = 2
except:
	from PySide.QtCore import *
	from PySide.QtGui import *
	psVersion = 1

import os, sys
import traceback, time, platform, shutil, socket
from functools import wraps


class Prism_Fusion_Integration(object):
	def __init__(self, core, plugin):
		self.core = core
		self.plugin = plugin

		if platform.system() == "Windows":
			self.examplePath = os.path.join(os.environ["appdata"], "Blackmagic Design", "Fusion")
		elif platform.system() == "Linux":
			userName = os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ else os.environ['USER']
			self.examplePath = "/home/%s/.fusion/BlackmagicDesign/Fusion" % userName
		elif platform.system() == "Darwin":
			userName = os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ else os.environ['USER']
			self.examplePath = "/Users/%s/Library/Application Support/Blackmagic Design/Fusion" % userName


	def err_decorator(func):
		@wraps(func)
		def func_wrapper(*args, **kwargs):
			exc_info = sys.exc_info()
			try:
				return func(*args, **kwargs)
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				erStr = ("%s ERROR - Prism_Plugin_Fusion_Integration %s:\n%s\n\n%s" % (time.strftime("%d/%m/%y %X"), args[0].plugin.version, ''.join(traceback.format_stack()), traceback.format_exc()))
				if hasattr(args[0].core, "writeErrorLog"):
					args[0].core.writeErrorLog(erStr)
				else:
					QMessageBox.warning(args[0].core.messageParent, "Prism Integration", erStr)

		return func_wrapper


	@err_decorator
	def getExecutable(self):
		execPath = ""
		if platform.system() == "Windows":
			execPath = "C:\\Program Files\\Blackmagic Design\\Fusion 9\\Fusion.exe"

		return execPath


	@err_decorator
	def integrationAdd(self, origin):
		path = QFileDialog.getExistingDirectory(self.core.messageParent, "Select Fusion folder", self.examplePath)

		if path == "":
			return False

		result = self.writeFusionFiles(path)

		if result:
			QMessageBox.information(self.core.messageParent, "Prism Integration", "Prism integration was added successfully")
			return path

		return result


	@err_decorator
	def integrationRemove(self, origin, installPath):
		result = self.removeIntegration(installPath)

		if result:
			QMessageBox.information(self.core.messageParent, "Prism Integration", "Prism integration was removed successfully")

		return result


	def writeFusionFiles(self, fusionpath):
		try:
			if not os.path.exists(fusionpath):
				QMessageBox.warning(self.core.messageParent, "Prism Integration", "Invalid Fusion path: %s.\nThe path doesn't exist." % fusionpath, QMessageBox.Ok)
				return False

			integrationBase = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Integration")
			addedFiles = []

			# "PrismMenu.fu" add a Prism menu, but leads to freezes
			for i in ["PrismRenderStartEvent.fu"]:
				origFile = os.path.join(integrationBase, i)
				targetFile = os.path.join(fusionpath, "Config", i)

				if not os.path.exists(os.path.dirname(targetFile)):
					os.makedirs(os.path.dirname(targetFile))
					addedFiles.append(os.path.dirname(targetFile))

				if os.path.exists(targetFile):
					os.remove(targetFile)

				shutil.copy2(origFile, targetFile)
				addedFiles.append(targetFile)

				with open(targetFile, "r+") as init:
					initStr = init.read()
					initStr = initStr.replace("PRISMROOT", "\"%s\"" % self.core.prismRoot.replace("\\", "/"))
					init.seek(0)
					init.write(initStr)

			if platform.system() == "Windows":
				for i in ["PrismInit.scriptlib"]:
					origFile = os.path.join(integrationBase, i)
					targetFile = os.path.join(fusionpath, "Scripts", i)

					if not os.path.exists(os.path.dirname(targetFile)):
						os.makedirs(os.path.dirname(targetFile))
						addedFiles.append(os.path.dirname(targetFile))

					if os.path.exists(targetFile):
						os.remove(targetFile)

					shutil.copy2(origFile, targetFile)
					addedFiles.append(targetFile)

					with open(targetFile, "r+") as init:
						initStr = init.read()
						initStr = initStr.replace("PRISMROOT", "\"%s\"" % self.core.prismRoot.replace("\\", "/"))
						init.seek(0)
						init.write(initStr)

			for i in ["1 Save Version.py", "2 Save Comment.py", "3 Project Browser.py", "4 Update selected load nodes.py", "5 Settings.py"]:
				origFile = os.path.join(integrationBase, i)
				targetFile = os.path.join(fusionpath, "Scripts", "Comp", "Prism", i)

				if not os.path.exists(os.path.dirname(targetFile)):
					os.makedirs(os.path.dirname(targetFile))
					addedFiles.append(os.path.dirname(targetFile))

				if os.path.exists(targetFile):
					os.remove(targetFile)

				shutil.copy2(origFile, targetFile)
				addedFiles.append(targetFile)

				with open(targetFile, "r+") as init:
					initStr = init.read()
					initStr = initStr.replace("PRISMROOT", "\"%s\"" % self.core.prismRoot.replace("\\", "/"))
					init.seek(0)
					init.write(initStr)

			for i in ["WritePrism.setting"]:
				origFile = os.path.join(integrationBase, i)
				targetFile = os.path.join(fusionpath, "Macros", i)

				if not os.path.exists(os.path.dirname(targetFile)):
					os.makedirs(os.path.dirname(targetFile))
					addedFiles.append(os.path.dirname(targetFile))

				if os.path.exists(targetFile):
					os.remove(targetFile)

				shutil.copy2(origFile, targetFile)
				addedFiles.append(targetFile)

				with open(targetFile, "r+") as init:
					initStr = init.read()
					initStr = initStr.replace("PRISMROOT", "\"%s\"" % self.core.prismRoot.replace("\\", "/"))
					init.seek(0)
					init.write(initStr)

			if platform.system() in ["Linux", "Darwin"]:
				for i in addedFiles:
					os.chmod(i, 0o777)

			return True

		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()

			msgStr = "Errors occurred during the installation of the Fusion integration.\nThe installation is possibly incomplete.\n\n%s\n%s\n%s" % (str(e), exc_type, exc_tb.tb_lineno)
			msgStr += "\n\nRunning this application as administrator could solve this problem eventually."

			QMessageBox.warning(self.core.messageParent, "Prism Integration", msgStr)
			return False


	def removeIntegration(self, installPath):
		try:
			gizmo = os.path.join(installPath, "WritePrism.gizmo")

			for i in [gizmo]:
				if os.path.exists(i):
					os.remove(i)

			pFiles = []
			pFiles.append(os.path.join(installPath, "Config", "PrismRenderStartEvent.fu"))
			pFiles.append(os.path.join(installPath, "Scripts", "PrismInit.scriptlib"))
			pFiles.append(os.path.join(installPath, "Scripts", "Comp", "Prism", "1 Save Version.py"))
			pFiles.append(os.path.join(installPath, "Scripts", "Comp", "Prism", "2 Save Comment.py"))
			pFiles.append(os.path.join(installPath, "Scripts", "Comp", "Prism", "3 Project Browser.py"))
			pFiles.append(os.path.join(installPath, "Scripts", "Comp", "Prism", "4 Update selected load nodes.py"))
			pFiles.append(os.path.join(installPath, "Scripts", "Comp", "Prism", "5 Settings.py"))
			pFiles.append(os.path.join(installPath, "Scripts", "Macros", "WritePrism.setting"))

			for i in pFiles:
				if os.path.exists(i):
					os.remove(i)

			return True

		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()

			msgStr = "Errors occurred during the removal of the Fusion integration.\n\n%s\n%s\n%s" % (str(e), exc_type, exc_tb.tb_lineno)
			msgStr += "\n\nRunning this application as administrator could solve this problem eventually."

			QMessageBox.warning(self.core.messageParent, "Prism Integration", msgStr)
			return False


	def updateInstallerUI(self, userFolders, pItem):
		try:
			fusionItem = QTreeWidgetItem(["Fusion"])
			pItem.addChild(fusionItem)

			if platform.system() == "Windows":
				fusionPath = os.path.join(userFolders["AppData"], "Blackmagic Design", "Fusion")
			elif platform.system() == "Linux":
				userName = os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ else os.environ['USER']
				fusionPath = "/home/%s/.fusion/BlackmagicDesign/Fusion" % userName
			elif platform.system() == "Darwin":
				userName = os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ else os.environ['USER']
				fusionPath = "/Users/%s/Library/Application Support/Blackmagic Design/Fusion" % userName

			if os.path.exists(fusionPath):
				fusionItem.setCheckState(0, Qt.Checked)
				fusionItem.setText(1, fusionPath)
				fusionItem.setToolTip(0, fusionPath)
			else:
				fusionItem.setCheckState(0, Qt.Unchecked)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			msg = QMessageBox.warning(self.core.messageParent, "Prism Installation", "Errors occurred during the installation.\n The installation is possibly incomplete.\n\n%s\n%s\n%s\n%s" % (__file__, str(e), exc_type, exc_tb.tb_lineno))
			return False


	def installerExecute(self, fusionItem, result, locFile):
		try:
			installLocs = []

			if fusionItem.checkState(0) == Qt.Checked and os.path.exists(fusionItem.text(1)):
				result["Fusion integration"] = self.writeFusionFiles(fusionItem.text(1))
				if result["Fusion integration"]:
					installLocs.append(fusionItem.text(1))

			return installLocs
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			msg = QMessageBox.warning(self.core.messageParent, "Prism Installation", "Errors occurred during the installation.\n The installation is possibly incomplete.\n\n%s\n%s\n%s\n%s" % (__file__, str(e), exc_type, exc_tb.tb_lineno))
			return False