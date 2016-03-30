__author__ = 'Peeratham'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Code Smell Result Analysis',
    'author': 'Peeratham',
    'author_email': 'tpeera4@vt.edu',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'Code Smell Result Analysis'
}

setup(**config)