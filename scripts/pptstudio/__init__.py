"""pptstudio — designer-grade PPTX generation for research / daily / competition decks.

    import sys; sys.path.insert(0, r'<skill>/scripts')
    from pptstudio import Deck
"""
from .deck import Deck  # noqa: F401
from .canvas import Canvas, Box  # noqa: F401
from . import theme as themes  # noqa: F401
from . import components as K  # noqa: F401
from . import images  # noqa: F401
from . import icons  # noqa: F401
from . import fonts  # noqa: F401

__version__ = '0.1.0'
