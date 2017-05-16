#!/usr/bin/env python

"""pip setup file"""

from setuptools import setup, find_packages

setup(
    # Basic description of package
    name='lolbot',
    version='1',
    description='Discord bot',
    
    # License for use
    license='GPLv3',
    
    # Author details
    author='S Tayck',
    author_email='tayck@tayck.com',
    
    # Packages provided
    #packages=find_packages(),
    
    # Requirements for this package
    install_requires=['requests', 'websocket-client'],
    )
