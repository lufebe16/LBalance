
import os
import logging

class LConfigDir(object):
	def __init__(self):
		self.path = None
		try:
			from android.storage import app_storage_path
			pth = app_storage_path()
			os.environ['HOME'] = pth
			logging.info("ConfigDir: android HOME = {0:}".format(pth))
		except ImportError:
			logging.info("ConfigDir: platform is not android")

		storage = os.environ['HOME']+"/.config/lbalance"
		os.makedirs(storage,exist_ok=True)

		self.path = storage

		logging.info("LConfigDir: storage dir = {0:}".format(self.path))

	def get(self):
		return self.path

ConfigDir = LConfigDir()
