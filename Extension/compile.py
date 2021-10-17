
# import Extension.spam
#
# print(spam.system("ls -l"))
#
import numpy

from distutils.core import setup, Extension
setup(name='cpdist', version='1.2',
      ext_modules=[Extension('cpdist', ['Extension/cpdist.c'],
                             extra_compile_args=[],
                             extra_link_args=[],
                             include_dirs=[numpy.get_include(),"/usr/local/include"],
                             library_dirs=["/usr/lib","/usr/local/lib","/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib"]
                             )
                   ])