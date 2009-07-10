#!/usr/bin/env python
 
from setuptools import setup
import lucullus

setup(name='lucullus',
      version=lucullus.__version__,
      description='Lucullus is a framework to manage and visualize scientific data in a browser.',
      long_description='The server is based on bottle (python) and uses cairo to render 2d image tiles in realtime. On client-side a custom JavaScript library based on jQuery allows easy navigation through huge amounts of data with a google-maps-like interface.',
      author='Marcel Hellkamp',
      author_email='marc@gsites.de',
      url='http://github.com/defnull/lucullus',
      packages=['lucullus','lucullus.plugins','lucullus.base'],
	  include_package_data=True,
	  zip_safe = False,
	  entry_points = { 'console_scripts': ['lucullus-serve = lucullus.server:serve'] },
      install_requires=['bottle >= 0.4.9',
                		'pycairo >= 1.8.6',
                		'paste >= 1.7.2',
						'simplejson >= 2.0.9',
						'biopython >= 1.5'],
      provides=['lucullus'],
      #license='MIT',
      classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: No Input/Output (Daemon)',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'License :: Free For Educational Use',
		'License :: Free for non-commercial use',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.5',
		'Programming Language :: Python :: 2.6',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
		'Topic :: Multimedia :: Graphics :: Viewers',
		'Topic :: Scientific/Engineering :: Bio-Informatics',
		'Topic :: Scientific/Engineering :: Visualization',
		'Topic :: Software Development :: Libraries :: Application Frameworks']
     )
