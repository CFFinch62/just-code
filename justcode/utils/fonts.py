# Just Code Editor - Font Utilities
# Cross-platform monospace font handling

import sys
from PyQt6.QtGui import QFont, QFontDatabase


def get_monospace_font_family() -> str:
    """
    Get the appropriate monospace font family for the current platform.
    
    Returns:
        str: Font family name that exists on the current system
    """
    # Platform-specific preferred fonts
    if sys.platform == 'darwin':
        # macOS preferred fonts (in order of preference)
        preferred = ['Menlo', 'SF Mono', 'Monaco']
    elif sys.platform == 'win32':
        # Windows preferred fonts
        preferred = ['Cascadia Code', 'Consolas', 'Courier New']
    else:
        # Linux preferred fonts
        preferred = ['Monospace', 'DejaVu Sans Mono', 'Liberation Mono', 'Ubuntu Mono']
    
    # Check which fonts are available
    available_families = set(QFontDatabase.families())
    
    for font_name in preferred:
        if font_name in available_families:
            return font_name
    
    # Fallback: let Qt pick a monospace font
    fallback = QFont()
    fallback.setStyleHint(QFont.StyleHint.TypeWriter)
    fallback.setFixedPitch(True)
    return fallback.family()


def get_monospace_font(size: int = 12) -> QFont:
    """
    Get a properly configured monospace QFont for the current platform.
    
    Args:
        size: Font point size (default: 12)
        
    Returns:
        QFont: Configured monospace font
    """
    family = get_monospace_font_family()
    font = QFont(family, size)
    font.setStyleHint(QFont.StyleHint.TypeWriter)
    font.setFixedPitch(True)
    return font

