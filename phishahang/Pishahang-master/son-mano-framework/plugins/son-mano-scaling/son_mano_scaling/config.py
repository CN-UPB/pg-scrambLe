PARENT_IP = "vm-hadik3r-06.cs.uni-paderborn.de"
NETDATA_PORT = 19999

DUMMY_INSTANCE_IP = "vm-hadik3r-07.cs.uni-paderborn.de"

OSM_DEFAULT_USERNAME = "admin"
OSM_DEFAULT_PASSWORD = "admin"
PISHAHANG_DEFAULT_USERNAME = "sonata"
PISHAHANG_DEFAULT_PASSWORD = "1234"

def run_async(func):
	"""
		run_async(func)
			function decorator, intended to make "func" run in a separate
			thread (asynchronously).
			Returns the created Thread object
	"""
	from threading import Thread
	from functools import wraps

	@wraps(func)
	def async_func(*args, **kwargs):
		func_hl = Thread(target = func, args = args, kwargs = kwargs)
		func_hl.start()
		return func_hl

	return async_func