"""
cdar-contracts — CDAR shared interface definitions.
Single source of truth for schemas, ViewDefinitions, SQL, and EXT metadata
shared between dqar-client-kit and dqar-aidbox.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("cdar-contracts")
except PackageNotFoundError:
    __version__ = "1.0.0-dev"
