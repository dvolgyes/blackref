#!/usr/bin/env python3
"""An uncompromising BibTeX/BibLaTeX reference list formatter."""

try:
    from importlib.metadata import version

    __version__ = version("blackref")
except ImportError:
    # Fallback for older Python versions or when package is not installed
    __version__ = "unknown"

__author__ = "David Völgyes"
__email__ = "david.volgyes@ieee.org"
__license__ = "AGPLv3"
__summary__ = "An uncompromising BibTeX/BibLaTeX reference list formatter."
__description__ = __summary__

# Import the main CLI function for backward compatibility
from .cli import main

# Public API exports
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__summary__",
    "__description__",
    "main",
]
