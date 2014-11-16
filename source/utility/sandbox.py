import sys, os
import autopath
from pypy.translator.sandbox.sandlib import SimpleIOSandboxedProc
from pypy.translator.sandbox.sandlib import VirtualizedSandboxedProc
from pypy.translator.sandbox.vfs import Dir, RealDir, RealFile
import pypy


LIB_ROOT = os.path.dirname(os.path.dirname(pypy.__file__))

class PyPySandboxedProc(VirtualizedSandboxedProc, SimpleIOSandboxedProc):
	argv0 = '/bin/pypy-c'
	virtual_cwd = '/tmp'
	virtual_env = {}
	virtual_console_isatty = True
	arguments = ['../goal/pypy-c', '-u']

	def __init__(self, executable, arguments, tmpdir=None, debug=True):
		self.executable = executable = os.path.abspath(executable)
		self.tmpdir = tmpdir
		self.debug = debug
	  	super(PyPySandboxedProc, self).__init__([self.argv0] + arguments,
			  executable=executable)

	def build_virtual_root(self):
	# build a virtual file system:
	# * can access its own executable
	# * can access the pure Python libraries
	# * can access the temporary usession directory as /tmp
		exclude = ['.pyc', '.pyo']
		if self.tmpdir is None:
			tmpdirnode = Dir({})
		else:
			tmpdirnode = RealDir(self.tmpdir, exclude=exclude)
		libroot = str(LIB_ROOT)

		return Dir({
			'bin': Dir({
				'pypy-c': RealFile(self.executable),
				'lib-python': RealDir(os.path.join(libroot, 'lib-python'),
					exclude=exclude),
				'lib_pypy': RealDir(os.path.join(libroot, 'lib_pypy'),
					exclude=exclude),
				}),
			'tmp': tmpdirnode,
			})

# run test
arguments = ['../goal/pypy-c', '-u']

sandproc = PyPySandboxedProc(arguments[0], arguments[1:],
		tmpdir=None, debug=True)

#start the proc
code1 = "print 'started'\na = 5\nprint a"
code2 = "b = a\nprint b\nprint 'code 2 was run'"

output, error = sandproc.communicate(code1)
print "output: %s\n error: %s\n" % (output, error)

output, error = sandproc.communicate(code2)
print "output: %s\n error: %s\n" % (output, error)
