"""
 Bucket is a 
"""
try:
	import cPickle as pickle
except ImportError:
	# Fallback to slower pickle
	import Pickle as pickle

"""
Example:
import ondemand

fs = ondemand.FileStore('/tmp', mkdir = True)
mc = ondemand.MemCache(['127.0.0.1:11211'])
tc = ondemand.TimedCache(60*10)
cache = ondemand.MultiCache(fs, (tc, mc))

# get and set methods
cache.set('session192837/object5', 5)
print cache.get('session192837/object5') # --> 5

# Cache is a callable
cache('session192837/object5', 5)
print cache('session192837/object5', default = 20)

# Save some memory
cache.pack()

"""


class Cache(object):
	""" A container for key-value pairs that are stored in a special way. Used as an API for key/value databases."""

	def __call__(self, key, value = None, default = None):
		if not value is None:
			return self.set(key, value)
		else:
			return self.get(key, default)

	def get(self, key, default = None):
		""" returns value of key, default or None """
		raise NotImplementedError
		
	def set(self, key, value):
		raise NotImplementedError
				
	def delete(self, key):
		raise NotImplementedError

	def pack(self):
		""" Reduce memory or disk usage by packing unused values (optional, only implemented by some Cache variants) """
		pass





class Store(Cache):
	""" Persistens version of Cache """
	pass






class MemCache(Cache):
	def __init__(self, server, debug=0):
		""" Creates a Cache frontend to a memcache server. Use memcache_connect() to activate memcaching """
		import memcache
		self.server = server
		self.mc = memcache.Client(server, debug=debug)
	
	def get(self, key, default = None):
		data = self.mc.get(key.encode('utf-8'))
		if data is None:
			return default
		return data
		
	def set(self, key, value):
		self.mc.put(key.encode('utf-8'), data)
		return value

	def delete(self, key):
		self.mc.delete(key.encode('utf-8'))






class FileStore(Store):
	def __init__(self, path, mkdirs = True):
		self.path = path
		self.mkdirs = mkdirs

	def get(self, key, default = None):
		filename = self.path + "/" + key + ".pkl"
		data = pickle.load(open(filename,'rb'))
		if data is None:
			return default
		return data

	def set(self, key, value):
		filename = self.path + "/" + key + ".pkl"
		if self.mkdirs:
			dirname = os.path.dirname(os.path.abspath(filename))
			if not os.path.isdir(dirname):
				os.makedirs(dirname)
		pickle.dump(filename, open(filename,'rb'), pickle.HIGHEST_PROTOCOL)
		return value

	def delete(self, key):
		filename = self.path + "/" + key + ".pkl"
		try:
			os.unlink(filename)
		except (IOError, OSError):
			pass






class TimedCache(Cache):
	""" Cache with aging local memory buffer """
	def __init__(self, timeout = 60):
		self.timeout = timeout
		self.cache = {}

	def __getstate__(self):
		return {'timeout': self.timeout, 'cache': {}}

	def get(self, key, default = None):
		data, timeout = self.cache.get(key, (None, 0))
		if timeout and time.time() > timeout:
			self.delete(key)
			return default
		if data is None:
			return default
		return data

	def set(self, key, value):
		self.cache[key] = (value, time.time() + self.timeout)
		return value

	def delete(self, key):
		if key in self.cache:
			del self.cache[key]

	def pack(self):
		ts = time.time()
		for k in self.cache:
			if self.cache[k][1] < ts:
				self.delete(k)
		




class MultiStore(Store):
	""" Cache with multible layers of sub-caches.  """
	def __init__(self, store, caches):
		self.store = store
		self.caches = caches

	def get(self, key, default = None):
		for c in self.caches:
			data = c.get(key)
			if not data is None:
				return data
		data = self.store.get(key)
		if not data is None:
			for c in self.caches:
				c.set(key, data)
			return data
		return default

	def set(self, key, value):
		for c in self.caches:
			c.delete(key)
		self.store.set(key, value)
		return value

	def delete(self, key):
		for c in self.caches:
			c.delete(key)
		self.store.delete(key)

	def pack(self):
		for c in self.caches:
			c.pack()
		self.store.pack()
		


import UserDict


class CacheDict(UserDict.DictMixin):
	""" A dict like wrapper for a Cache object with key tracking.
		Be careful. Automatic saving only happens on garbage collection (which could be to late).
		"""

	def __init__(self, cache):
		self.cache = cache
		self.keys = keys

	def __len__(self):
		return len(self.keys)
	
	def __getitem__(self, key):
		if key not in self.keys:
			raise KeyError
		data = self.cache.get(key)
		if data is None:
			self.keys.remove(key)
			self.cache.delete(key)
			raise KeyError
		return data

	def __setitem__(self, key, value):
		if key not in self.keys:
			self.keys.append(key)
		self.cache.set(key, value)

	def __delitem__(self, key):
		if key not in self.keys:
			raise KeyError
		self.keys.remove(key)
		self.cache.delete(key)

	def __contains__(self, key):
		return (key in self.keys)
		
	def keys(self):
		return self.keys
		
	def __del__(self):
		for key in self.keys:
			self.cache.delete(key)
