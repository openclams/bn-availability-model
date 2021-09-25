
# import Extension.spam
#
# print(spam.system("ls -l"))
#

from distutils.core import setup, Extension
setup(name='bnlearn', version='1.1',  \
      ext_modules=[Extension('bnlearn', ['Extension/cpdist.c'])])