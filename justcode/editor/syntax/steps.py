# Just Code Editor - Steps Language Syntax Support
# Syntax highlighting for the Steps programming language

from typing import Dict, Optional
from PyQt6.Qsci import QsciLexerCustom
from PyQt6.QtGui import QColor, QFont

from ...utils import get_monospace_font


class StepsStyles:
    """Style indices for Steps syntax elements."""
    DEFAULT = 0
    KEYWORD_STRUCTURE = 1   # building:, floor:, step:, riser:
    KEYWORD_CONTROL = 2     # if, otherwise, repeat, while, for each
    KEYWORD_ACTION = 3      # call, return, display, input, set
    KEYWORD_OPERATOR = 4    # is equal to, and, or, not, added to
    KEYWORD_TYPE = 5        # number, text, boolean, list, table
    STRING = 6              # "text literals"
    NUMBER = 7              # 42, 3.14
    COMMENT = 8             # note: comments
    IDENTIFIER = 9          # variable names
    LITERAL = 10            # true, false, nothing
    PUNCTUATION = 11        # :, ,, [], ()
    MATH_OPERATOR = 12      # +, -, *, /


# Default Steps syntax colors (cyberpunk-inspired dark theme)
DEFAULT_STEPS_COLORS = {
    "structure": "#ff79c6",      # Pink - building, floor, step
    "control": "#bd93f9",        # Purple - if, repeat, while
    "action": "#50fa7b",         # Green - call, return, display
    "operator": "#8be9fd",       # Cyan - is equal to, and, or
    "type": "#ffb86c",           # Orange - number, text, boolean
    "string": "#f1fa8c",         # Yellow - strings
    "number": "#ff79c6",         # Pink - numbers
    "comment": "#6272a4",        # Gray - comments
    "identifier": "#f8f8f2",     # White - variables
    "literal": "#bd93f9",        # Purple - true, false, nothing
    "punctuation": "#f8f8f2",    # White - punctuation
    "math_operator": "#ff79c6",  # Pink - +, -, *, /
}


# Multi-word keywords - sorted by length (longest first) for correct matching
MULTI_WORD_KEYWORDS = [
    # Long phrases
    ("is greater than or equal to", StepsStyles.KEYWORD_OPERATOR),
    ("is less than or equal to", StepsStyles.KEYWORD_OPERATOR),
    ("storing result in", StepsStyles.KEYWORD_ACTION),
    ("if unsuccessful:", StepsStyles.KEYWORD_CONTROL),
    ("is not equal to", StepsStyles.KEYWORD_OPERATOR),
    ("then continue:", StepsStyles.KEYWORD_CONTROL),
    ("is greater than", StepsStyles.KEYWORD_OPERATOR),
    ("is less than", StepsStyles.KEYWORD_OPERATOR),
    ("is equal to", StepsStyles.KEYWORD_OPERATOR),
    ("character at", StepsStyles.KEYWORD_OPERATOR),
    ("otherwise if", StepsStyles.KEYWORD_CONTROL),
    ("note block:", StepsStyles.COMMENT),
    ("belongs to:", StepsStyles.KEYWORD_STRUCTURE),
    ("starts with", StepsStyles.KEYWORD_OPERATOR),
    ("ends with", StepsStyles.KEYWORD_OPERATOR),
    ("length of", StepsStyles.KEYWORD_OPERATOR),
    ("for each", StepsStyles.KEYWORD_CONTROL),
    ("added to", StepsStyles.KEYWORD_OPERATOR),
    ("split by", StepsStyles.KEYWORD_OPERATOR),
    ("end note", StepsStyles.COMMENT),
    ("is in", StepsStyles.KEYWORD_OPERATOR),
]

# Single-word keywords mapped to styles
KEYWORDS = {
    # Structure keywords (followed by colon)
    "building": StepsStyles.KEYWORD_STRUCTURE,
    "floor": StepsStyles.KEYWORD_STRUCTURE,
    "step": StepsStyles.KEYWORD_STRUCTURE,
    "riser": StepsStyles.KEYWORD_STRUCTURE,
    "expects": StepsStyles.KEYWORD_STRUCTURE,
    "returns": StepsStyles.KEYWORD_STRUCTURE,
    "declare": StepsStyles.KEYWORD_STRUCTURE,
    "do": StepsStyles.KEYWORD_STRUCTURE,
    "attempt": StepsStyles.KEYWORD_STRUCTURE,
    "exit": StepsStyles.KEYWORD_STRUCTURE,
    
    # Control flow
    "if": StepsStyles.KEYWORD_CONTROL,
    "otherwise": StepsStyles.KEYWORD_CONTROL,
    "repeat": StepsStyles.KEYWORD_CONTROL,
    "times": StepsStyles.KEYWORD_CONTROL,
    "in": StepsStyles.KEYWORD_CONTROL,
    "while": StepsStyles.KEYWORD_CONTROL,
    
    # Action keywords
    "as": StepsStyles.KEYWORD_ACTION,
    "fixed": StepsStyles.KEYWORD_ACTION,
    "set": StepsStyles.KEYWORD_ACTION,
    "to": StepsStyles.KEYWORD_ACTION,
    "call": StepsStyles.KEYWORD_ACTION,
    "with": StepsStyles.KEYWORD_ACTION,
    "return": StepsStyles.KEYWORD_ACTION,
    "display": StepsStyles.KEYWORD_ACTION,
    "input": StepsStyles.KEYWORD_ACTION,
    "add": StepsStyles.KEYWORD_ACTION,
    "remove": StepsStyles.KEYWORD_ACTION,
    "from": StepsStyles.KEYWORD_ACTION,
    
    # Boolean operators
    "and": StepsStyles.KEYWORD_OPERATOR,
    "or": StepsStyles.KEYWORD_OPERATOR,
    "not": StepsStyles.KEYWORD_OPERATOR,
    "contains": StepsStyles.KEYWORD_OPERATOR,
    "of": StepsStyles.KEYWORD_OPERATOR,
    "equals": StepsStyles.KEYWORD_OPERATOR,
    
    # Literals
    "true": StepsStyles.LITERAL,
    "false": StepsStyles.LITERAL,
    "nothing": StepsStyles.LITERAL,
    
    # Types
    "number": StepsStyles.KEYWORD_TYPE,
    "text": StepsStyles.KEYWORD_TYPE,
    "boolean": StepsStyles.KEYWORD_TYPE,
    "list": StepsStyles.KEYWORD_TYPE,
    "table": StepsStyles.KEYWORD_TYPE,
    
    # Comment keyword
    "note": StepsStyles.COMMENT,
}


class StepsLexer(QsciLexerCustom):
    """Custom QScintilla lexer for the Steps programming language.
    
    This lexer provides syntax highlighting for Steps code in the editor.
    It uses the token definitions from the Steps language to colorize:
    - Structure keywords (building, floor, step, etc.)
    - Control flow (if, otherwise, repeat, while)
    - Action keywords (call, return, display, set)
    - Operators (is equal to, and, or)
    - Types (number, text, boolean, list, table)
    - Literals (strings, numbers, true, false, nothing)
    - Comments (note:)
    """

    def __init__(self, parent=None, syntax_theme: Optional[Dict[str, str]] = None,
                 background: str = "#1e1e1e", foreground: str = "#f8f8f2"):
        """Initialize the Steps lexer with theme colors.
        
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

    def language(self) -> str:
        """Return the language name."""
        return "Steps"

    def description(self, style: int) -> str:
        """Return a description for each style."""
        descriptions = {
            StepsStyles.DEFAULT: "Default",
            StepsStyles.KEYWORD_STRUCTURE: "Structure Keyword",
            StepsStyles.KEYWORD_CONTROL: "Control Flow",
            StepsStyles.KEYWORD_ACTION: "Action Keyword",
            StepsStyles.KEYWORD_OPERATOR: "Operator",
            StepsStyles.KEYWORD_TYPE: "Type",
            StepsStyles.STRING: "String",
            StepsStyles.NUMBER: "Number",
            StepsStyles.COMMENT: "Comment",
            StepsStyles.IDENTIFIER: "Identifier",
            StepsStyles.LITERAL: "Literal",
            StepsStyles.PUNCTUATION: "Punctuation",
            StepsStyles.MATH_OPERATOR: "Math Operator",
        }
        return descriptions.get(style, "")

    def styleText(self, start: int, end: int) -> None:
        """Tokenize and apply styles to the text.
        
        This is called by QScintilla whenever text needs to be highlighted.
        """
        editor = self.parent()
        if editor is None:
            return

        # Get the text to style
        source = editor.text()
        text = source[start:end]
        
        if not text:
            return
            
        self.startStyling(start)
        
        i = 0
        in_note_block = False
        
        while i < len(text):
            ch = text[i]
            
            # Check for note block (multi-line comment)
            if self._match_ahead(text, i, "note block:"):
                in_note_block = True
                length = len("note block:")
                self.setStyling(length, StepsStyles.COMMENT)
                i += length
                continue
            
            # End of note block
            if in_note_block:
                if self._match_ahead(text, i, "end note"):
                    in_note_block = False
                    length = len("end note")
                    self.setStyling(length, StepsStyles.COMMENT)
                    i += length
                    continue
                else:
                    # Everything inside note block is a comment
                    self.setStyling(1, StepsStyles.COMMENT)
                    i += 1
                    continue
            
            # Single-line comment (note:)
            if self._match_ahead(text, i, "note:"):
                # Style "note:" and rest of line as comment
                line_end = text.find('\n', i)
                if line_end == -1:
                    line_end = len(text)
                self.setStyling(line_end - i, StepsStyles.COMMENT)
                i = line_end
                continue
            
            # String literals
            if ch == '"':
                j = i + 1
                while j < len(text):
                    if text[j] == '\\' and j + 1 < len(text):
                        j += 2  # Skip escape sequence
                    elif text[j] == '"':
                        j += 1
                        break
                    elif text[j] == '\n':
                        break  # Unterminated string
                    else:
                        j += 1
                self.setStyling(j - i, StepsStyles.STRING)
                i = j
                continue
            
            # Numbers (including negative)
            if ch.isdigit() or (ch == '-' and i + 1 < len(text) and text[i + 1].isdigit()):
                j = i
                if text[j] == '-':
                    j += 1
                while j < len(text) and text[j].isdigit():
                    j += 1
                # Decimal part
                if j < len(text) and text[j] == '.' and j + 1 < len(text) and text[j + 1].isdigit():
                    j += 1
                    while j < len(text) and text[j].isdigit():
                        j += 1
                self.setStyling(j - i, StepsStyles.NUMBER)
                i = j
                continue
            
            # Check multi-word keywords first
            matched = False
            for keyword, style in MULTI_WORD_KEYWORDS:
                if self._match_ahead(text, i, keyword):
                    self.setStyling(len(keyword), style)
                    i += len(keyword)
                    matched = True
                    break
            if matched:
                continue
            
            # Identifiers and single-word keywords
            if ch.isalpha() or ch == '_':
                j = i
                while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                    j += 1
                word = text[i:j]
                word_lower = word.lower()
                
                # Check if it's a keyword
                if word_lower in KEYWORDS:
                    style = KEYWORDS[word_lower]
                    # Check for colon after structure keywords
                    k = j
                    while k < len(text) and text[k] == ' ':
                        k += 1
                    if k < len(text) and text[k] == ':':
                        # Include spaces and colon in the styling
                        self.setStyling(j - i, style)
                        i = j
                    else:
                        self.setStyling(j - i, style)
                        i = j
                else:
                    self.setStyling(j - i, StepsStyles.IDENTIFIER)
                    i = j
                continue
            
            # Math operators
            if ch in '+-*/':
                self.setStyling(1, StepsStyles.MATH_OPERATOR)
                i += 1
                continue
            
            # Punctuation
            if ch in ':,[]()':
                self.setStyling(1, StepsStyles.PUNCTUATION)
                i += 1
                continue
            
            # Whitespace and anything else
            self.setStyling(1, StepsStyles.DEFAULT)
            i += 1

    def _match_ahead(self, text: str, pos: int, pattern: str) -> bool:
        """Check if the text at position matches the pattern.
        
        For word patterns, ensures we're not matching a partial word.
        """
        end = pos + len(pattern)
        if end > len(text):
            return False
        
        if text[pos:end].lower() != pattern.lower():
            return False
        
        # If pattern ends with a letter, check that next char isn't alphanumeric
        if pattern[-1].isalpha():
            if end < len(text) and (text[end].isalnum() or text[end] == '_'):
                return False
        
        return True

    def _apply_theme(self, parent, syntax_theme: Optional[Dict[str, str]] = None,
                     background: str = "#1e1e1e", foreground: str = "#f8f8f2") -> None:
        """Apply theme colors to all styles."""
        colors = DEFAULT_STEPS_COLORS.copy()
        if syntax_theme:
            colors.update(syntax_theme)

        font = parent.font() if parent else get_monospace_font(10)
        self.setDefaultFont(font)
        self.setDefaultPaper(QColor(background))
        self.setDefaultColor(QColor(foreground))

        # Set font and background for all styles
        for style in range(15):
            self.setFont(font, style)
            self.setPaper(QColor(background), style)

        # Apply colors to each style
        self.setColor(QColor(foreground), StepsStyles.DEFAULT)
        self.setColor(QColor(colors["structure"]), StepsStyles.KEYWORD_STRUCTURE)
        self.setColor(QColor(colors["control"]), StepsStyles.KEYWORD_CONTROL)
        self.setColor(QColor(colors["action"]), StepsStyles.KEYWORD_ACTION)
        self.setColor(QColor(colors["operator"]), StepsStyles.KEYWORD_OPERATOR)
        self.setColor(QColor(colors["type"]), StepsStyles.KEYWORD_TYPE)
        self.setColor(QColor(colors["string"]), StepsStyles.STRING)
        self.setColor(QColor(colors["number"]), StepsStyles.NUMBER)
        self.setColor(QColor(colors["comment"]), StepsStyles.COMMENT)
        self.setColor(QColor(colors["identifier"]), StepsStyles.IDENTIFIER)
        self.setColor(QColor(colors["literal"]), StepsStyles.LITERAL)
        self.setColor(QColor(colors["punctuation"]), StepsStyles.PUNCTUATION)
        self.setColor(QColor(colors["math_operator"]), StepsStyles.MATH_OPERATOR)


def create_steps_lexer(
    parent=None,
    syntax_theme: Optional[Dict[str, str]] = None,
    background: str = "#1e1e1e",
    foreground: str = "#f8f8f2"
) -> StepsLexer:
    """Create and configure a Steps lexer with theme colors.
    
    Args:
        parent: Parent widget (usually the QsciScintilla editor)
        syntax_theme: Dictionary of syntax element names to hex colors
        background: Background color hex string
        foreground: Default foreground color hex string
    
    Returns:
        Configured StepsLexer instance
    """
    return StepsLexer(parent, syntax_theme, background, foreground)
