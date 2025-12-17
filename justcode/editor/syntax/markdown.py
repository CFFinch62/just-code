# Just Code Editor - Markdown Lexer
# Syntax highlighting for Markdown files

from typing import Dict, Optional
from PyQt6.Qsci import QsciLexerMarkdown
from PyQt6.QtGui import QColor, QFont

from ...utils import get_monospace_font


# Default Markdown syntax colors (dark theme)
DEFAULT_MARKDOWN_COLORS = {
    "default": "#d4d4d4",
    "header": "#569cd6",           # Headers (# ## ###)
    "emphasis": "#ce9178",          # *italic* **bold**
    "strong": "#dcdcaa",           # **bold**
    "link": "#4ec9b0",             # [text](url)
    "code": "#b5cea8",             # `inline code`
    "code_block": "#6a9955",       # ```code blocks```
    "list": "#c586c0",             # - * 1.
    "blockquote": "#808080",       # > quoted
    "horizontal_rule": "#858585",  # ---
}


class MarkdownLexer(QsciLexerMarkdown):
    """Markdown lexer with Just Code theming support."""

    def __init__(self, parent=None, syntax_theme: Optional[Dict[str, str]] = None,
                 background: str = "#1e1e1e", foreground: str = "#d4d4d4"):
        """
        Initialize the Markdown lexer with theme colors.

        Args:
            parent: Parent widget (usually the QsciScintilla editor)
            syntax_theme: Dictionary of syntax element names to hex colors
            background: Background color hex string
            foreground: Default foreground color hex string
        """
        super().__init__(parent)
        self._background = background
        self._foreground = foreground
        self._apply_theme(parent, syntax_theme, background, foreground)

    def _apply_theme(self, editor, syntax_theme: Optional[Dict[str, str]] = None,
                     background: str = "#1e1e1e", foreground: str = "#d4d4d4"):
        """Apply theme colors to the lexer."""
        # Merge provided theme with defaults
        colors = DEFAULT_MARKDOWN_COLORS.copy()
        if syntax_theme:
            colors.update(syntax_theme)

        # Get font from editor or use default
        if editor:
            font = editor.font()
        else:
            font = get_monospace_font(12)

        # Set default font for all styles
        for style in range(20):  # QScintilla markdown styles
            self.setFont(font, style)

        # Set background for all styles
        bg_color = QColor(background)
        self.setDefaultPaper(bg_color)
        self.setDefaultColor(QColor(foreground))

        for style in range(20):
            self.setPaper(bg_color, style)

        # Apply colors to specific styles
        # QsciLexerMarkdown style numbers:
        # 0 = Default
        # 1 = Special (like escape chars)
        # 2 = Strong emphasis 1 (**bold**)
        # 3 = Strong emphasis 2 (__bold__)
        # 4 = Emphasis 1 (*italic*)
        # 5 = Emphasis 2 (_italic_)
        # 6 = Header 1 (#)
        # 7 = Header 2 (##)
        # 8 = Header 3 (###)
        # 9 = Header 4 (####)
        # 10 = Header 5 (#####)
        # 11 = Header 6 (######)
        # 12 = Prechar (leading whitespace before list markers)
        # 13 = Unordered list item
        # 14 = Ordered list item
        # 15 = Blockquote
        # 16 = Strikeout
        # 17 = Horizontal rule
        # 18 = Link
        # 19 = Code/code block (backticks)
        # 20 = Code block double backtick
        # 21 = Code block triple backtick

        self.setColor(QColor(colors["default"]), 0)  # Default
        self.setColor(QColor(colors["strong"]), 2)   # Strong **
        self.setColor(QColor(colors["strong"]), 3)   # Strong __
        self.setColor(QColor(colors["emphasis"]), 4) # Emphasis *
        self.setColor(QColor(colors["emphasis"]), 5) # Emphasis _
        
        # Headers - all use header color
        header_color = QColor(colors["header"])
        for i in range(6, 12):
            self.setColor(header_color, i)
            # Make headers bold
            bold_font = QFont(font)
            bold_font.setBold(True)
            self.setFont(bold_font, i)

        self.setColor(QColor(colors["list"]), 12)           # Prechar
        self.setColor(QColor(colors["list"]), 13)           # Unordered list
        self.setColor(QColor(colors["list"]), 14)           # Ordered list
        self.setColor(QColor(colors["blockquote"]), 15)     # Blockquote
        self.setColor(QColor(colors["emphasis"]), 16)       # Strikeout
        self.setColor(QColor(colors["horizontal_rule"]), 17) # HR
        self.setColor(QColor(colors["link"]), 18)           # Link
        self.setColor(QColor(colors["code"]), 19)           # Code
        self.setColor(QColor(colors["code_block"]), 20)     # Code block 2
        self.setColor(QColor(colors["code_block"]), 21)     # Code block 3


def create_markdown_lexer(
    parent=None,
    syntax_theme: Optional[Dict[str, str]] = None,
    background: str = "#1e1e1e",
    foreground: str = "#d4d4d4"
):
    """
    Create and configure a Markdown lexer with theme colors.

    Args:
        parent: Parent widget (usually the QsciScintilla editor)
        syntax_theme: Dictionary of syntax element names to hex colors
        background: Background color hex string
        foreground: Default foreground color hex string

    Returns:
        Configured QsciLexerMarkdown instance
    """
    # Merge with defaults
    colors = DEFAULT_MARKDOWN_COLORS.copy()
    colors["default"] = foreground
    if syntax_theme:
        colors.update(syntax_theme)

    lexer = MarkdownLexer(parent, colors)
    return lexer

