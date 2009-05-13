"""The application's Globals object"""

import lucullus.lib.pyseq.ondemand as ondemand
import lucullus.lib.pyseq.config as config


class Globals(object):

	"""Globals acts as a container for objects available throughout the
	life of the application

	"""

	def __init__(self):
		"""One instance of Globals is created during application
		initialization and is available during requests via the
		'app_globals' variable
		"""
		# Maps Ressource ID to Object
		self.sessions = {}
		
		
		
		#fs = ondemand.FileStore(config.savepath)
		#mc = ondemand.MemCache(config.memcache)
		#tc = ondemand.TimedCache(60*10)
		#self.cache = ondemand.MultiStore(fs, (tc, mc))
