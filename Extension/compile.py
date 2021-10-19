import numpy

from distutils.core import setup, Extension
setup(name='cpdist', version='1.3',
      ext_modules=[Extension('cpdist', ['Extension/cpdist.c'],
                             include_dirs=[numpy.get_include()])
                   ])