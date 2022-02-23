"""Pasty API wrapper in Python."""
from .asyncio import AsyncPaste
from .sync import Paste

__version__ = "1.0.0"
__all__ = [AsyncPaste, Paste]
