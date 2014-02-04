from setuptools import setup
# setuptools used instead of distutils.core so that 
# dependencies can be handled automatically

# Extract version number from resync/_version.py. Here we 
# are very strict about the format of the version string 
# as an extra sanity check. (Thanks for comments in 
# http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package )
import re
VERSIONFILE="rjpres/_version.py"
verfilestr = open(VERSIONFILE, "rt").read()
match = re.search(r"^__version__ = '(\d+\.\d+)'", verfilestr, re.MULTILINE)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))

setup(
    name='rjpres',
    version=version,
    packages=['rjpres'],
    package_data={'rjpres': ['data/*/*.*','data/*/*/*.*','data/*/*/*/*.*','templates/*']},
    scripts=['rjp'],
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent", #is this true? know Linux & OS X ok
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Environment :: Web Environment"],
    author='Simeon Warner',
    author_email='simeon.warner@cornell.edu',
    description='Reveal-JS Presenter tool - web server and libraries combined',
    long_description=open('README').read(),
    url='http://github.com/zimeon/rjpres',
    #install_requires=[],
    #test_suite="rjpres.test",
)
