"""Package for slatium"""
# System
import sys

__project__ = 'Slatium'
__version__ = '1.0.0'

CLI = 'slatium'
MAIN = 'slatium.main:main'
VERSION = '{0} v{1}'.format(__project__, __version__)
DESCRIPTION = 'Bridge chat between Initium and Slack'

MIN_PYTHON_VERSION = 3, 3

if not sys.version_info >= MIN_PYTHON_VERSION:
    exit("Python {}.{}+ is required.".format(*MIN_PYTHON_VERSION))

import logging

logger = logging.getLogger(__name__)

# Local
try:
    from .sides import Side, SlackSide
    from dicts import Bidict, Dualdict
except ImportError:
    pass
