# Just Code Editor - Editor Widget
# QScintilla wrapper and customization

from typing import Dict, Optional
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from ..config import EditorSettings


class EditorWidget(QsciScintilla):
    """Custom QScintilla editor widget with Just Code styling."""
    
    def __init__(self, parent=None):
        """Initialize the editor widget."""
        super().__init__(parent)
        
        # Will be configured after creation
        self._settings = None
        self._setup_default_style()
    
    def _setup_default_style(self):
        """Set up basic editor styling."""
        # Use a monospace font - use system default monospace
        font = QFont("Monospace", 12)
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        font.setFixedPitch(True)
        self.setFont(font)

        # Basic editor settings
        self.setUtf8(True)
        self.setEolMode(QsciScintilla.EolMode.EolUnix)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(False)
        self.setAutoIndent(True)

        # Line numbers (will be updated from settings)
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, "00000")

        # Dark theme colors
        self.setPaper(QColor("#1e1e1e"))  # Background
        self.setColor(QColor("#d4d4d4"))  # Foreground text

        # Cursor - white for dark background
        self.setCaretWidth(2)
        self.setCaretForegroundColor(QColor("#ffffff"))

        # Current line highlighting - off by default
        self.setCaretLineVisible(False)

        # Selection colors
        self.setSelectionBackgroundColor(QColor("#264f78"))

        # Margins - dark background
        self.setMarginsBackgroundColor(QColor("#1e1e1e"))
        self.setMarginsForegroundColor(QColor("#858585"))

        # No word wrap by default
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        
    def apply_settings(self, settings: EditorSettings):
        """
        Apply editor settings.

        Args:
            settings: EditorSettings instance
        """
        self._settings = settings

        # Font - ensure it's monospace/fixed pitch
        font = QFont(settings.font_family, settings.font_size)
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Tabs and indentation
        self.setIndentationsUseTabs(not settings.use_spaces)
        self.setTabWidth(settings.tab_width)
        self.setAutoIndent(settings.auto_indent)
        
        # Line numbers
        if settings.line_numbers:
            self.setMarginLineNumbers(0, True)
            self.setMarginWidth(0, "00000")
        else:
            self.setMarginLineNumbers(0, False)
            self.setMarginWidth(0, 0)
        
        # Current line highlighting
        self.setCaretLineVisible(settings.highlight_current_line)
        
        # Word wrap
        if settings.word_wrap:
            self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        else:
            self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
    
    def apply_ui_theme(self, theme_data: Dict[str, str]):
        """
        Apply UI theme colors to the editor.

        Args:
            theme_data: Dictionary of theme color names to hex values
        """
        if theme_data.get('use_system_theme', False):
            return

        bg = theme_data.get('background', '#1e1e1e')
        fg = theme_data.get('foreground', '#d4d4d4')
        selection = theme_data.get('selection', '#264f78')
        cursor = theme_data.get('cursor', '#ffffff')
        line_highlight = theme_data.get('line_highlight', '#2a2a2a')

        # Apply colors to editor (used when no lexer is set)
        self.setPaper(QColor(bg))
        self.setColor(QColor(fg))
        self.setCaretForegroundColor(QColor(cursor))
        self.setSelectionBackgroundColor(QColor(selection))
        self.setCaretLineBackgroundColor(QColor(line_highlight))

        # Margins
        self.setMarginsBackgroundColor(QColor(bg))
        self.setMarginsForegroundColor(QColor("#858585"))

        # If a lexer is set, update its background colors too
        lexer = self.lexer()
        if lexer:
            lexer.setDefaultPaper(QColor(bg))
            lexer.setDefaultColor(QColor(fg))
            # Update paper for all styles
            for style in range(128):
                lexer.setPaper(QColor(bg), style)

    def set_python_lexer(
        self,
        syntax_theme: Optional[Dict[str, str]] = None,
        background: str = "#1e1e1e",
        foreground: str = "#d4d4d4"
    ):
        """
        Set Python lexer for syntax highlighting.

        Args:
            syntax_theme: Dictionary of syntax element names to hex colors
            background: Background color hex string
            foreground: Default foreground color hex string
        """
        from ..editor.syntax.python import create_python_lexer
        lexer = create_python_lexer(
            self,
            syntax_theme=syntax_theme,
            background=background,
            foreground=foreground
        )
        self.setLexer(lexer)

    def set_syntax_theme(self, theme: Dict[str, str]):
        """
        Set syntax theme colors.

        Note: This is a no-op for base EditorWidget. The lexer is set
        when files are opened based on file type. UI theme background
        is applied separately via apply_ui_theme().

        Args:
            theme: Dictionary of syntax element names to hex colors
        """
        # For plain text files, there's no lexer to update
        # For files with lexers, the lexer was already created with colors
        # and apply_ui_theme() handles background updates
        pass
