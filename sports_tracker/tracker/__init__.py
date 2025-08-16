"""
tracker package initialization
Exposes the main SportsTracker class for easy importing
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

# Import the main class to make it available at package level
from .core import SportsTracker

# Define what gets imported with 'from tracker import *'
__all__ = [
    'SportsTracker',
    '__version__',
    '__author__'
]

# Package initialization code (optional)
def _initialize():
    """Package initialization function"""
    print(f"Initializing Sports Tracker v{__version__}")

# Run initialization when package is imported
_initialize()