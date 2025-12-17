# Just Code Editor - Python Syntax Support
# Python lexer configuration

from typing import Dict, Optional
from PyQt6.Qsci import QsciLexerPython
from PyQt6.QtGui import QColor, QFont

from ...utils import get_monospace_font


# Default syntax colors (VS Code dark theme) - used if no theme provided
DEFAULT_SYNTAX_COLORS = {
    "keyword": "#569cd6",
    "string": "#ce9178",
    "number": "#b5cea8",
    "comment": "#6a9955",
    "function": "#dcdcaa",
    "class": "#4ec9b0",
    "operator": "#d4d4d4",
    "identifier": "#d4d4d4",
}


class PythonLexer(QsciLexerPython):
    """Python lexer with Just Code theming support."""

    def __init__(self, parent=None, syntax_theme: Optional[Dict[str, str]] = None,
                 background: str = "#1e1e1e", foreground: str = "#d4d4d4"):
        """
        Initialize the Python lexer with theme colors.

        Args:
            parent: Parent widget (usually the QsciScintilla editor)
            syntax_theme: Dictionary of syntax element names to hex colors
            background: Background color hex string
            foreground: Default foreground color hex string
        """
        super().__init__(parent)
        self._apply_theme(parent, syntax_theme, background, foreground)

    def _apply_theme(self, parent, syntax_theme: Optional[Dict[str, str]] = None,
                     background: str = "#1e1e1e", foreground: str = "#d4d4d4"):
        """Apply theme colors to the lexer."""
        # Merge provided theme with defaults
        colors = DEFAULT_SYNTAX_COLORS.copy()
        if syntax_theme:
            colors.update(syntax_theme)

        # Use the parent editor's font if available, otherwise use a default
        if parent:
            font = parent.font()
        else:
            font = get_monospace_font(10)

        self.setDefaultFont(font)

        # Background and default foreground
        self.setDefaultPaper(QColor(background))
        self.setDefaultColor(QColor(foreground))

        # Set the same font for all styles to ensure proper cursor positioning
        for style in range(128):  # QScintilla uses style numbers 0-127
            self.setFont(font, style)
            self.setPaper(QColor(background), style)

        # Apply syntax colors from theme
        # Keywords (def, class, if, etc.)
        self.setColor(QColor(colors["keyword"]), QsciLexerPython.Keyword)

        # Strings
        string_color = QColor(colors["string"])
        self.setColor(string_color, QsciLexerPython.SingleQuotedString)
        self.setColor(string_color, QsciLexerPython.DoubleQuotedString)
        self.setColor(string_color, QsciLexerPython.TripleSingleQuotedString)
        self.setColor(string_color, QsciLexerPython.TripleDoubleQuotedString)

        # Numbers
        self.setColor(QColor(colors["number"]), QsciLexerPython.Number)

        # Comments
        comment_color = QColor(colors["comment"])
        self.setColor(comment_color, QsciLexerPython.Comment)
        self.setColor(comment_color, QsciLexerPython.CommentBlock)

        # Function/method names
        function_color = QColor(colors["function"])
        self.setColor(function_color, QsciLexerPython.FunctionMethodName)
        self.setColor(function_color, QsciLexerPython.Decorator)

        # Class names
        self.setColor(QColor(colors["class"]), QsciLexerPython.ClassName)

        # Operators
        self.setColor(QColor(colors["operator"]), QsciLexerPython.Operator)

        # Identifiers (default text color)
        identifier_color = colors.get("identifier", foreground)
        self.setColor(QColor(identifier_color), QsciLexerPython.Identifier)


def create_python_lexer(
    parent=None,
    syntax_theme: Optional[Dict[str, str]] = None,
    background: str = "#1e1e1e",
    foreground: str = "#d4d4d4"
):
    """
    Create and configure a Python lexer with theme colors.

    Args:
        parent: Parent widget (usually the QsciScintilla editor)
        syntax_theme: Dictionary of syntax element names to hex colors
        background: Background color hex string
        foreground: Default foreground color hex string

    Returns:
        Configured QsciLexerPython instance
    """
    lexer = QsciLexerPython(parent)

    # Merge provided theme with defaults
    colors = DEFAULT_SYNTAX_COLORS.copy()
    if syntax_theme:
        colors.update(syntax_theme)

    # Use the parent editor's font if available, otherwise use a default
    if parent:
        font = parent.font()
    else:
        font = get_monospace_font(10)

    lexer.setDefaultFont(font)

    # Background and default foreground
    lexer.setDefaultPaper(QColor(background))
    lexer.setDefaultColor(QColor(foreground))

    # Set the same font for all styles to ensure proper cursor positioning
    for style in range(128):  # QScintilla uses style numbers 0-127
        lexer.setFont(font, style)
        lexer.setPaper(QColor(background), style)

    # Apply syntax colors from theme
    # Keywords (def, class, if, etc.)
    lexer.setColor(QColor(colors["keyword"]), QsciLexerPython.Keyword)

    # Strings
    string_color = QColor(colors["string"])
    lexer.setColor(string_color, QsciLexerPython.SingleQuotedString)
    lexer.setColor(string_color, QsciLexerPython.DoubleQuotedString)
    lexer.setColor(string_color, QsciLexerPython.TripleSingleQuotedString)
    lexer.setColor(string_color, QsciLexerPython.TripleDoubleQuotedString)

    # Numbers
    lexer.setColor(QColor(colors["number"]), QsciLexerPython.Number)

    # Comments
    comment_color = QColor(colors["comment"])
    lexer.setColor(comment_color, QsciLexerPython.Comment)
    lexer.setColor(comment_color, QsciLexerPython.CommentBlock)

    # Function/method names
    function_color = QColor(colors["function"])
    lexer.setColor(function_color, QsciLexerPython.FunctionMethodName)
    lexer.setColor(function_color, QsciLexerPython.Decorator)

    # Class names
    lexer.setColor(QColor(colors["class"]), QsciLexerPython.ClassName)

    # Operators
    lexer.setColor(QColor(colors["operator"]), QsciLexerPython.Operator)

    # Identifiers (default text color)
    identifier_color = colors.get("identifier", foreground)
    lexer.setColor(QColor(identifier_color), QsciLexerPython.Identifier)

    return lexer
