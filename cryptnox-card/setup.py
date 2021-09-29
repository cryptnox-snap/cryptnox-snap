"""
Configuration for setting up CryptnoxCard CLI application
"""
import sys

from setuptools import setup
from cryptnoxcard.version import __version__
dependencies = [
    "argparse",
    "appdirs",
    "base58",
    "ecdsa",
    "colander",
    "cryptnoxpy",
    "lazy-import",
    "pytz",
    "requests",
    "tabulate",
    "stdiomask",
    "config",
    "eth-account",
    "cython",
    "web3"
]

if sys.platform.startswith("win"):
    dependencies.append("winrt")

setup(name='cryptnoxcard',
      version=__version__,
      platforms=['any'],
      python_requires=">=3.6,<3.10",
      install_requires=dependencies,
      entry_points={
          'console_scripts': ['cryptnoxcard=cryptnoxcard.main:main'],
      }
      )
