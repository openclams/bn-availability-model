
# import Extension.spam
#
# print(spam.system("ls -l"))
#
import numpy

from distutils.core import setup, Extension
setup(name='bnlearn', version='1.1',  \
      ext_modules=[Extension('bnlearn', ['Extension/cpdist.c'],
                             include_dirs=[numpy.get_include()])])