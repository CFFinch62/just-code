# Just Code Editor - Tab Widget
# Multi-file editing with tabs

from pathlib import Path
from typing import Dict, Optional, List, Union

from PyQt6.QtWidgets import QTabWidget, QMessageBox, QMenu
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction

from .editor_widget import EditorWidget
from .markdown_editor import MarkdownEditorWidget
from ..config import EditorSettings


class TabEditorWidget(QTabWidget):
    """Tab widget that manages multiple editor instances."""

    # Signals
    current_file_changed = pyqtSignal(object)  # Path or None
    file_modified_changed = pyqtSignal(bool)   # Modified state changed
    file_saved = pyqtSignal(object)            # Path of saved file
    cursor_position_changed = pyqtSignal(int, int)  # line, column (0-based)
    file_info_changed = pyqtSignal(str, str, str)   # file_type, encoding, line_ending

    def __init__(self, parent=None):
        """Initialize the tab widget."""
        super().__init__(parent)

        # Track files by path -> tab index
        self._file_tabs: Dict[Path, int] = {}

        # Track file metadata (encoding, line endings) per tab index
        self._file_metadata: Dict[int, Dict[str, str]] = {}

        # Settings reference
        self._settings: Optional[EditorSettings] = None
        self._syntax_theme: Optional[Dict] = None
        self._ui_theme: Optional[Dict] = None

        self._setup_ui()
        self._connect_signals()

        # Create initial untitled tab
        self._create_untitled_tab()
    
    def _setup_ui(self):
        """Set up the tab widget UI."""
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # Default dark styling (will be overridden by theme)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 6px 12px;
                border: none;
                border-right: 1px solid #3c3c3c;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #383838;
            }
            QTabBar::close-button {
                image: none;
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
                background-color: #5a5a5a;
            }
        """)
        
        # Enable context menu on tabs
        self.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self._show_tab_context_menu)
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.tabCloseRequested.connect(self._close_tab)
        self.currentChanged.connect(self._on_tab_changed)
    
    def _create_untitled_tab(self) -> EditorWidget:
        """Create a new untitled tab."""
        editor = EditorWidget(self)
        editor.modificationChanged.connect(self._on_modification_changed)
        editor.cursorPositionChanged.connect(self._on_cursor_position_changed)

        if self._settings:
            editor.apply_settings(self._settings)
        if self._syntax_theme:
            editor.set_syntax_theme(self._syntax_theme)
        if self._ui_theme:
            editor.apply_ui_theme(self._ui_theme)

        index = self.addTab(editor, "untitled")

        # Set default metadata for untitled files
        self._file_metadata[index] = {
            'file_type': 'Plain Text',
            'encoding': 'UTF-8',
            'line_ending': 'LF'
        }

        self.setCurrentIndex(index)
        return editor

    def _on_cursor_position_changed(self, line: int, col: int):
        """Handle cursor position change in any editor."""
        # Only emit if the sender is the current editor
        sender = self.sender()
        current = self.current_editor()
        # For MarkdownEditorWidget, compare the underlying editor
        if hasattr(current, '_editor'):
            current = current._editor
        if sender == current:
            self.cursor_position_changed.emit(line, col)

    def _on_tab_changed(self, index: int):
        """Handle tab change."""
        if index >= 0:
            # Find the file path for this tab
            file_path = None
            for path, tab_index in self._file_tabs.items():
                if tab_index == index:
                    file_path = path
                    break
            self.current_file_changed.emit(file_path)

            # Emit file info for the new tab
            self._emit_current_file_info()

            # Emit current cursor position
            editor = self.current_editor()
            if editor:
                line, col = editor.getCursorPosition()
                self.cursor_position_changed.emit(line, col)
    
    def _on_modification_changed(self, modified: bool):
        """Handle editor modification state change."""
        editor = self.sender()
        if not editor:
            return

        index = self.indexOf(editor)
        if index < 0:
            return

        # Update tab title with modified indicator
        title = self.tabText(index)
        if modified and not title.endswith(" •"):
            self.setTabText(index, title + " •")
        elif not modified and title.endswith(" •"):
            self.setTabText(index, title[:-2])

        # Emit signal if this is the current tab
        if index == self.currentIndex():
            self.file_modified_changed.emit(modified)

    def _emit_current_file_info(self):
        """Emit file info signal for the current tab."""
        index = self.currentIndex()
        if index >= 0 and index in self._file_metadata:
            meta = self._file_metadata[index]
            self.file_info_changed.emit(
                meta.get('file_type', 'Plain Text'),
                meta.get('encoding', 'UTF-8'),
                meta.get('line_ending', 'LF')
            )
        else:
            # Default for unknown tabs
            self.file_info_changed.emit('Plain Text', 'UTF-8', 'LF')

    def _detect_file_type(self, file_path: Path) -> str:
        """Detect file type/language from file extension."""
        ext = file_path.suffix.lower()
        filename = file_path.name.lower()

        # Map extensions to display names
        type_map = {
            '.py': 'Python', '.pyw': 'Python',
            '.js': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
            '.ts': 'TypeScript', '.tsx': 'TypeScript',
            '.jsx': 'JSX',
            '.rb': 'Ruby', '.rake': 'Ruby', '.gemspec': 'Ruby',
            '.c': 'C', '.h': 'C',
            '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++', '.hh': 'C++', '.hxx': 'C++',
            '.cs': 'C#',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.sh': 'Shell', '.bash': 'Bash', '.zsh': 'Zsh',
            '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass', '.less': 'Less',
            '.html': 'HTML', '.htm': 'HTML', '.xhtml': 'XHTML',
            '.xml': 'XML', '.svg': 'SVG', '.xsl': 'XSL',
            '.json': 'JSON', '.jsonc': 'JSON',
            '.sql': 'SQL',
            '.yaml': 'YAML', '.yml': 'YAML',
            '.lua': 'Lua',
            '.pl': 'Perl', '.pm': 'Perl',
            '.php': 'PHP', '.phtml': 'PHP',
            '.md': 'Markdown', '.markdown': 'Markdown',
            '.txt': 'Plain Text',
            '.toml': 'TOML',
            '.ini': 'INI', '.cfg': 'Config',
            '.mk': 'Makefile',
        }

        # Check for special filenames
        if filename in ['makefile', 'gnumakefile']:
            return 'Makefile'
        if filename in ['dockerfile']:
            return 'Dockerfile'
        if filename in ['.gitignore', '.dockerignore']:
            return 'Ignore File'

        return type_map.get(ext, 'Plain Text')

    def _detect_encoding(self, raw_bytes: bytes) -> str:
        """Detect file encoding from raw bytes."""
        # Check for BOM markers
        if raw_bytes.startswith(b'\xef\xbb\xbf'):
            return 'UTF-8 BOM'
        if raw_bytes.startswith(b'\xff\xfe'):
            return 'UTF-16 LE'
        if raw_bytes.startswith(b'\xfe\xff'):
            return 'UTF-16 BE'

        # Try to decode as UTF-8
        try:
            raw_bytes.decode('utf-8')
            return 'UTF-8'
        except UnicodeDecodeError:
            pass

        # Try Latin-1 (always succeeds, but may not be correct)
        try:
            raw_bytes.decode('latin-1')
            return 'Latin-1'
        except:
            pass

        return 'Binary'

    def _detect_line_ending(self, content: str) -> str:
        """Detect line ending type from file content."""
        if '\r\n' in content:
            return 'CRLF'
        elif '\r' in content:
            return 'CR'
        else:
            return 'LF'

    def _get_tab_title(self, file_path: Path) -> str:
        """Get display title for a tab."""
        return file_path.name

    def toggle_markdown_preview(self) -> bool:
        """
        Toggle the markdown preview for the current tab.

        Returns:
            True if preview is now visible, False if hidden,
            None if current tab is not a markdown file.
        """
        editor = self.current_editor()
        if isinstance(editor, MarkdownEditorWidget):
            return editor.toggle_preview()
        return False

    def is_markdown_preview_visible(self) -> bool:
        """Check if markdown preview is visible for current tab."""
        editor = self.current_editor()
        if isinstance(editor, MarkdownEditorWidget):
            return editor.is_preview_visible()
        return False

    def is_current_file_markdown(self) -> bool:
        """Check if current file is a markdown file."""
        return isinstance(self.current_editor(), MarkdownEditorWidget)

    def _update_file_tabs_after_removal(self, removed_index: int):
        """Update _file_tabs indices after a tab is removed."""
        updated = {}
        for path, index in self._file_tabs.items():
            if index > removed_index:
                updated[path] = index - 1
            elif index < removed_index:
                updated[path] = index
            # Skip the removed tab
        self._file_tabs = updated

    def _update_file_metadata_after_removal(self, removed_index: int):
        """Update _file_metadata indices after a tab is removed."""
        updated = {}
        for index, metadata in self._file_metadata.items():
            if index > removed_index:
                updated[index - 1] = metadata
            elif index < removed_index:
                updated[index] = metadata
            # Skip the removed tab
        self._file_metadata = updated

    def open_file(self, file_path: Path) -> bool:
        """
        Open a file in a new tab or switch to existing tab.

        Returns True if file was opened successfully.
        """
        file_path = Path(file_path).resolve()

        # Check if file is already open
        if file_path in self._file_tabs:
            self.setCurrentIndex(self._file_tabs[file_path])
            return True

        # Try to read the file (first as raw bytes for encoding detection)
        try:
            raw_bytes = file_path.read_bytes()
            encoding = self._detect_encoding(raw_bytes)

            # Decode content
            if encoding.startswith('UTF-16'):
                content = raw_bytes.decode('utf-16')
            elif encoding == 'Latin-1':
                content = raw_bytes.decode('latin-1')
            else:
                # UTF-8 or UTF-8 BOM
                content = raw_bytes.decode('utf-8-sig')  # Handles BOM

            # Detect line endings before normalization
            line_ending = self._detect_line_ending(content)

        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Could not open file:\n{e}"
            )
            return False

        # Check if this is a markdown file
        is_markdown = file_path.suffix.lower() in ['.md', '.markdown']

        # Check if current tab is untitled and empty (and same type)
        current_editor = self.current_editor()
        current_index = self.currentIndex()
        current_is_markdown = isinstance(current_editor, MarkdownEditorWidget)
        reuse_tab = (
            current_editor is not None and
            current_index not in self._file_tabs.values() and
            current_editor.text() == "" and
            not current_editor.isModified() and
            current_is_markdown == is_markdown  # Only reuse if same type
        )

        if reuse_tab:
            # Reuse the current untitled tab
            editor = current_editor
            index = current_index
        else:
            # Create new tab - use MarkdownEditorWidget for markdown files
            if is_markdown:
                editor = MarkdownEditorWidget(self)
            else:
                editor = EditorWidget(self)

            editor.modificationChanged.connect(self._on_modification_changed)
            # Connect cursor position signal
            if isinstance(editor, MarkdownEditorWidget):
                editor._editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
            else:
                editor.cursorPositionChanged.connect(self._on_cursor_position_changed)

            if self._settings:
                editor.apply_settings(self._settings)
            if self._syntax_theme and not is_markdown:
                editor.set_syntax_theme(self._syntax_theme)
            if self._ui_theme:
                editor.apply_ui_theme(self._ui_theme)

            index = self.addTab(editor, self._get_tab_title(file_path))

        # Set content and configure
        editor.setText(content)
        editor.setModified(False)

        # Set up syntax highlighting based on extension (skip for markdown - already done)
        if not is_markdown:
            self._setup_syntax_for_file(editor, file_path)

        # Store file metadata
        self._file_metadata[index] = {
            'file_type': self._detect_file_type(file_path),
            'encoding': encoding,
            'line_ending': line_ending
        }

        # Update tracking
        self._file_tabs[file_path] = index
        self.setTabText(index, self._get_tab_title(file_path))
        self.setTabToolTip(index, str(file_path))
        self.setCurrentIndex(index)

        self.current_file_changed.emit(file_path)
        return True

    def _setup_syntax_for_file(self, editor: EditorWidget, file_path: Path):
        """Set up syntax highlighting based on file extension."""
        ext = file_path.suffix.lower()
        filename = file_path.name.lower()

        # Get background/foreground from UI theme
        bg = "#1e1e1e"
        fg = "#d4d4d4"
        if self._ui_theme:
            bg = self._ui_theme.get('background', bg)
            fg = self._ui_theme.get('foreground', fg)

        lexer = None

        # Use our custom themed lexers for Python (has full theme support)
        if ext in ['.py', '.pyw']:
            from .syntax import PythonLexer
            lexer = PythonLexer(editor, self._syntax_theme, background=bg, foreground=fg)

        # Use QScintilla's built-in lexers for other languages
        else:
            lexer = self._get_builtin_lexer(ext, filename, editor)

        if lexer:
            # Apply basic theming to built-in lexers
            self._apply_basic_lexer_theme(lexer, bg, fg)
            editor.setLexer(lexer)

    def _get_builtin_lexer(self, ext: str, filename: str, editor):
        """Get the appropriate QScintilla built-in lexer for a file extension."""
        from PyQt6.Qsci import (
            QsciLexerRuby, QsciLexerJavaScript, QsciLexerCPP,
            QsciLexerJava, QsciLexerBash, QsciLexerCSS, QsciLexerHTML,
            QsciLexerJSON, QsciLexerSQL, QsciLexerYAML, QsciLexerLua,
            QsciLexerPerl, QsciLexerMakefile, QsciLexerXML
        )

        # Map extensions to lexer classes
        lexer_map = {
            # Ruby
            '.rb': QsciLexerRuby,
            '.rake': QsciLexerRuby,
            '.gemspec': QsciLexerRuby,
            # JavaScript/TypeScript
            '.js': QsciLexerJavaScript,
            '.mjs': QsciLexerJavaScript,
            '.cjs': QsciLexerJavaScript,
            '.ts': QsciLexerJavaScript,  # TypeScript uses JS lexer
            '.tsx': QsciLexerJavaScript,
            '.jsx': QsciLexerJavaScript,
            # C/C++
            '.c': QsciLexerCPP,
            '.h': QsciLexerCPP,
            '.cpp': QsciLexerCPP,
            '.cc': QsciLexerCPP,
            '.cxx': QsciLexerCPP,
            '.hpp': QsciLexerCPP,
            '.hh': QsciLexerCPP,
            '.hxx': QsciLexerCPP,
            # C#
            '.cs': QsciLexerCPP,  # C# uses CPP lexer
            # Java
            '.java': QsciLexerJava,
            # Go (uses CPP lexer as closest match)
            '.go': QsciLexerCPP,
            # Rust (uses CPP lexer as closest match)
            '.rs': QsciLexerCPP,
            # Shell/Bash
            '.sh': QsciLexerBash,
            '.bash': QsciLexerBash,
            '.zsh': QsciLexerBash,
            # CSS/SCSS
            '.css': QsciLexerCSS,
            '.scss': QsciLexerCSS,
            '.sass': QsciLexerCSS,
            '.less': QsciLexerCSS,
            # HTML
            '.html': QsciLexerHTML,
            '.htm': QsciLexerHTML,
            '.xhtml': QsciLexerHTML,
            # XML
            '.xml': QsciLexerXML,
            '.svg': QsciLexerXML,
            '.xsl': QsciLexerXML,
            # JSON
            '.json': QsciLexerJSON,
            '.jsonc': QsciLexerJSON,
            # SQL
            '.sql': QsciLexerSQL,
            # YAML
            '.yaml': QsciLexerYAML,
            '.yml': QsciLexerYAML,
            # Lua
            '.lua': QsciLexerLua,
            # Perl
            '.pl': QsciLexerPerl,
            '.pm': QsciLexerPerl,
            # PHP (uses HTML lexer which includes PHP support)
            '.php': QsciLexerHTML,
            '.phtml': QsciLexerHTML,
        }

        # Check for Makefile by name
        if filename in ['makefile', 'gnumakefile'] or ext == '.mk':
            return QsciLexerMakefile(editor)

        lexer_class = lexer_map.get(ext)
        if lexer_class:
            return lexer_class(editor)

        return None

    def _apply_basic_lexer_theme(self, lexer, bg: str, fg: str):
        """Apply syntax theme colors to a lexer."""
        from PyQt6.QtGui import QColor, QFont

        bg_color = QColor(bg)
        fg_color = QColor(fg)

        # Get syntax theme colors (fall back to defaults)
        theme = self._syntax_theme or {}
        colors = {
            'keyword': theme.get('keyword', '#569cd6'),
            'string': theme.get('string', '#ce9178'),
            'number': theme.get('number', '#b5cea8'),
            'comment': theme.get('comment', '#6a9955'),
            'function': theme.get('function', '#dcdcaa'),
            'class': theme.get('class', '#4ec9b0'),
            'operator': theme.get('operator', fg),
        }

        # Set default colors and background for all styles
        lexer.setDefaultPaper(bg_color)
        lexer.setDefaultColor(fg_color)
        for style in range(128):
            lexer.setPaper(bg_color, style)
            lexer.setColor(fg_color, style)

        # Apply themed colors based on lexer type
        self._apply_lexer_style_colors(lexer, colors)

    def _apply_lexer_style_colors(self, lexer, colors: dict):
        """
        Apply syntax theme colors to lexer style constants.

        Each QScintilla lexer has style constants for different token types.
        We map our theme colors (keyword, string, comment, etc.) to these.
        """
        from PyQt6.QtGui import QColor
        from PyQt6.Qsci import (
            QsciLexerRuby, QsciLexerJavaScript, QsciLexerCPP,
            QsciLexerJava, QsciLexerBash, QsciLexerCSS, QsciLexerHTML,
            QsciLexerJSON, QsciLexerSQL, QsciLexerYAML, QsciLexerLua,
            QsciLexerPerl, QsciLexerMakefile, QsciLexerXML, QsciLexerCSharp
        )

        # Helper to set color for a style
        def set_color(style, color_name):
            if color_name in colors:
                lexer.setColor(QColor(colors[color_name]), style)

        # Ruby
        if isinstance(lexer, QsciLexerRuby):
            set_color(QsciLexerRuby.Comment, 'comment')
            set_color(QsciLexerRuby.Keyword, 'keyword')
            set_color(QsciLexerRuby.DoubleQuotedString, 'string')
            set_color(QsciLexerRuby.SingleQuotedString, 'string')
            set_color(QsciLexerRuby.Number, 'number')
            set_color(QsciLexerRuby.ClassName, 'class')
            set_color(QsciLexerRuby.FunctionMethodName, 'function')
            set_color(QsciLexerRuby.Operator, 'operator')
            set_color(QsciLexerRuby.Symbol, 'keyword')

        # JavaScript
        elif isinstance(lexer, QsciLexerJavaScript):
            set_color(QsciLexerJavaScript.Comment, 'comment')
            set_color(QsciLexerJavaScript.CommentLine, 'comment')
            set_color(QsciLexerJavaScript.CommentDoc, 'comment')
            set_color(QsciLexerJavaScript.Keyword, 'keyword')
            set_color(QsciLexerJavaScript.DoubleQuotedString, 'string')
            set_color(QsciLexerJavaScript.SingleQuotedString, 'string')
            set_color(QsciLexerJavaScript.Number, 'number')
            set_color(QsciLexerJavaScript.Operator, 'operator')

        # C/C++/C#
        elif isinstance(lexer, (QsciLexerCPP, QsciLexerCSharp)):
            set_color(QsciLexerCPP.Comment, 'comment')
            set_color(QsciLexerCPP.CommentLine, 'comment')
            set_color(QsciLexerCPP.CommentDoc, 'comment')
            set_color(QsciLexerCPP.Keyword, 'keyword')
            set_color(QsciLexerCPP.DoubleQuotedString, 'string')
            set_color(QsciLexerCPP.SingleQuotedString, 'string')
            set_color(QsciLexerCPP.Number, 'number')
            set_color(QsciLexerCPP.Operator, 'operator')
            set_color(QsciLexerCPP.PreProcessor, 'keyword')

        # Java
        elif isinstance(lexer, QsciLexerJava):
            set_color(QsciLexerJava.Comment, 'comment')
            set_color(QsciLexerJava.CommentLine, 'comment')
            set_color(QsciLexerJava.CommentDoc, 'comment')
            set_color(QsciLexerJava.Keyword, 'keyword')
            set_color(QsciLexerJava.DoubleQuotedString, 'string')
            set_color(QsciLexerJava.SingleQuotedString, 'string')
            set_color(QsciLexerJava.Number, 'number')
            set_color(QsciLexerJava.Operator, 'operator')

        # Bash
        elif isinstance(lexer, QsciLexerBash):
            set_color(QsciLexerBash.Comment, 'comment')
            set_color(QsciLexerBash.Keyword, 'keyword')
            set_color(QsciLexerBash.DoubleQuotedString, 'string')
            set_color(QsciLexerBash.SingleQuotedString, 'string')
            set_color(QsciLexerBash.Number, 'number')
            set_color(QsciLexerBash.Operator, 'operator')

        # Lua
        elif isinstance(lexer, QsciLexerLua):
            set_color(QsciLexerLua.Comment, 'comment')
            set_color(QsciLexerLua.LineComment, 'comment')
            set_color(QsciLexerLua.Keyword, 'keyword')
            set_color(QsciLexerLua.String, 'string')
            set_color(QsciLexerLua.Number, 'number')
            set_color(QsciLexerLua.Operator, 'operator')
            set_color(QsciLexerLua.BasicFunctions, 'function')

        # Perl
        elif isinstance(lexer, QsciLexerPerl):
            set_color(QsciLexerPerl.Comment, 'comment')
            set_color(QsciLexerPerl.Keyword, 'keyword')
            set_color(QsciLexerPerl.DoubleQuotedString, 'string')
            set_color(QsciLexerPerl.SingleQuotedString, 'string')
            set_color(QsciLexerPerl.Number, 'number')
            set_color(QsciLexerPerl.Operator, 'operator')

        # SQL
        elif isinstance(lexer, QsciLexerSQL):
            set_color(QsciLexerSQL.Comment, 'comment')
            set_color(QsciLexerSQL.CommentLine, 'comment')
            set_color(QsciLexerSQL.Keyword, 'keyword')
            set_color(QsciLexerSQL.DoubleQuotedString, 'string')
            set_color(QsciLexerSQL.SingleQuotedString, 'string')
            set_color(QsciLexerSQL.Number, 'number')
            set_color(QsciLexerSQL.Operator, 'operator')

        # JSON
        elif isinstance(lexer, QsciLexerJSON):
            set_color(QsciLexerJSON.String, 'string')
            set_color(QsciLexerJSON.Number, 'number')
            set_color(QsciLexerJSON.Keyword, 'keyword')  # true/false/null
            set_color(QsciLexerJSON.Operator, 'operator')

        # YAML
        elif isinstance(lexer, QsciLexerYAML):
            set_color(QsciLexerYAML.Comment, 'comment')
            set_color(QsciLexerYAML.Keyword, 'keyword')
            set_color(QsciLexerYAML.Number, 'number')
            set_color(QsciLexerYAML.Operator, 'operator')

        # HTML
        elif isinstance(lexer, QsciLexerHTML):
            set_color(QsciLexerHTML.HTMLComment, 'comment')
            set_color(QsciLexerHTML.Tag, 'keyword')
            set_color(QsciLexerHTML.Attribute, 'function')
            set_color(QsciLexerHTML.HTMLDoubleQuotedString, 'string')
            set_color(QsciLexerHTML.HTMLSingleQuotedString, 'string')
            set_color(QsciLexerHTML.HTMLNumber, 'number')

        # CSS
        elif isinstance(lexer, QsciLexerCSS):
            set_color(QsciLexerCSS.Comment, 'comment')
            set_color(QsciLexerCSS.Tag, 'keyword')
            set_color(QsciLexerCSS.ClassSelector, 'class')
            set_color(QsciLexerCSS.IDSelector, 'function')
            set_color(QsciLexerCSS.DoubleQuotedString, 'string')
            set_color(QsciLexerCSS.SingleQuotedString, 'string')
            set_color(QsciLexerCSS.Operator, 'operator')

        # XML
        elif isinstance(lexer, QsciLexerXML):
            set_color(QsciLexerXML.HTMLComment, 'comment')
            set_color(QsciLexerXML.Tag, 'keyword')
            set_color(QsciLexerXML.Attribute, 'function')
            set_color(QsciLexerXML.HTMLDoubleQuotedString, 'string')
            set_color(QsciLexerXML.HTMLSingleQuotedString, 'string')

        # Makefile
        elif isinstance(lexer, QsciLexerMakefile):
            set_color(QsciLexerMakefile.Comment, 'comment')
            set_color(QsciLexerMakefile.Target, 'function')
            set_color(QsciLexerMakefile.Operator, 'operator')

    def save_current_file(self) -> bool:
        """Save the current file. Returns True if saved successfully."""
        editor = self.current_editor()
        if not editor:
            return False

        # Find current file path
        current_index = self.currentIndex()
        file_path = None
        for path, index in self._file_tabs.items():
            if index == current_index:
                file_path = path
                break

        if file_path is None:
            # Untitled - need Save As
            return False

        return self._save_file(editor, file_path)

    def save_file_as(self, file_path: Path) -> bool:
        """Save current editor content to specified path."""
        editor = self.current_editor()
        if not editor:
            return False

        file_path = Path(file_path).resolve()
        current_index = self.currentIndex()

        # Remove old path mapping if exists
        old_path = None
        for path, index in list(self._file_tabs.items()):
            if index == current_index:
                old_path = path
                break

        if old_path:
            del self._file_tabs[old_path]

        # Save and update mapping
        if self._save_file(editor, file_path):
            self._file_tabs[file_path] = current_index
            self.setTabText(current_index, self._get_tab_title(file_path))
            self.setTabToolTip(current_index, str(file_path))
            self._setup_syntax_for_file(editor, file_path)
            self.current_file_changed.emit(file_path)
            return True
        return False

    def _save_file(self, editor: EditorWidget, file_path: Path) -> bool:
        """Write editor content to file."""
        try:
            file_path.write_text(editor.text(), encoding='utf-8')
            editor.setModified(False)
            # Emit signal for plugins
            self.file_saved.emit(file_path)
            return True
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Could not save file:\n{e}"
            )
            return False

    def _close_tab(self, index: int) -> bool:
        """
        Close a tab, prompting to save if modified.
        Returns True if tab was closed.
        """
        if self.count() <= 1:
            # Don't close the last tab, just clear it
            editor = self.widget(index)
            if editor and editor.isModified():
                if not self._prompt_save(index):
                    return False

            # Reset to untitled
            if editor:
                editor.clear()
                editor.setModified(False)

            # Remove from file tracking
            for path, tab_index in list(self._file_tabs.items()):
                if tab_index == index:
                    del self._file_tabs[path]
                    break

            # Reset metadata to defaults
            self._file_metadata[index] = {
                'file_type': 'Plain Text',
                'encoding': 'UTF-8',
                'line_ending': 'LF'
            }

            self.setTabText(index, "untitled")
            self.setTabToolTip(index, "")
            self.current_file_changed.emit(None)
            self._emit_current_file_info()
            return True

        editor = self.widget(index)
        if editor and editor.isModified():
            if not self._prompt_save(index):
                return False

        # Remove from file tracking before removing tab
        for path, tab_index in list(self._file_tabs.items()):
            if tab_index == index:
                del self._file_tabs[path]
                break

        # Remove metadata for this tab
        if index in self._file_metadata:
            del self._file_metadata[index]

        self.removeTab(index)
        self._update_file_tabs_after_removal(index)
        self._update_file_metadata_after_removal(index)
        return True

    def _prompt_save(self, index: int) -> bool:
        """
        Prompt user to save modified file.
        Returns True if user chose Save/Don't Save, False if cancelled.
        """
        title = self.tabText(index).rstrip(" •")
        reply = QMessageBox.question(
            self, "Save Changes?",
            f"'{title}' has unsaved changes.\n\nDo you want to save them?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return False
        elif reply == QMessageBox.StandardButton.Save:
            # Try to save
            file_path = None
            for path, tab_index in self._file_tabs.items():
                if tab_index == index:
                    file_path = path
                    break

            if file_path:
                editor = self.widget(index)
                return self._save_file(editor, file_path)
            else:
                # Untitled - would need Save As dialog
                # Return False to indicate we can't save automatically
                return False

        return True  # Discard

    def close_current_tab(self) -> bool:
        """Close the current tab."""
        return self._close_tab(self.currentIndex())

    def close_other_tabs(self):
        """Close all tabs except the current one."""
        current = self.currentIndex()
        # Close tabs from right to left to maintain indices
        for i in range(self.count() - 1, -1, -1):
            if i != current:
                if not self._close_tab(i):
                    break  # User cancelled
                # Update current index if needed
                if i < current:
                    current -= 1

    def close_all_tabs(self) -> bool:
        """Close all tabs. Returns True if all closed."""
        while self.count() > 1:
            if not self._close_tab(self.count() - 1):
                return False
        # Close/reset the last one
        return self._close_tab(0)

    def _show_tab_context_menu(self, pos):
        """Show context menu for tab bar."""
        tab_index = self.tabBar().tabAt(pos)
        if tab_index < 0:
            return

        menu = QMenu(self)

        close_action = menu.addAction("Close")
        close_action.triggered.connect(lambda: self._close_tab(tab_index))

        close_others_action = menu.addAction("Close Others")
        close_others_action.triggered.connect(self.close_other_tabs)
        close_others_action.setEnabled(self.count() > 1)

        close_all_action = menu.addAction("Close All")
        close_all_action.triggered.connect(self.close_all_tabs)

        menu.exec(self.tabBar().mapToGlobal(pos))

    def current_editor(self) -> Optional[EditorWidget]:
        """Get the current editor widget."""
        return self.currentWidget()

    def current_file_path(self) -> Optional[Path]:
        """Get the current file path, or None if untitled."""
        index = self.currentIndex()
        for path, tab_index in self._file_tabs.items():
            if tab_index == index:
                return path
        return None

    def is_current_modified(self) -> bool:
        """Check if current editor has unsaved changes."""
        editor = self.current_editor()
        return editor.isModified() if editor else False

    def get_open_files(self) -> List[Path]:
        """Get list of all open file paths."""
        return list(self._file_tabs.keys())

    def get_current_tab_index(self) -> int:
        """Get the current tab index."""
        return self.currentIndex()

    def new_file(self):
        """Create a new untitled tab."""
        self._create_untitled_tab()

    def apply_settings(self, settings: EditorSettings):
        """Apply settings to all editors."""
        self._settings = settings
        for i in range(self.count()):
            editor = self.widget(i)
            if editor:
                editor.apply_settings(settings)

    def set_syntax_theme(self, theme: Dict):
        """Set syntax theme for all editors."""
        self._syntax_theme = theme
        for i in range(self.count()):
            editor = self.widget(i)
            if editor:
                editor.set_syntax_theme(theme)

    def apply_ui_theme(self, theme: Dict):
        """Apply UI theme to tab bar and all editors."""
        self._ui_theme = theme

        bg = theme.get('background', '#1e1e1e')
        fg = theme.get('foreground', '#d4d4d4')
        panel_bg = theme.get('panel_background', '#252526')
        panel_border = theme.get('panel_border', '#3c3c3c')
        selection = theme.get('selection', '#264f78')

        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {bg};
            }}
            QTabBar::tab {{
                background-color: {panel_bg};
                color: {fg};
                padding: 6px 12px;
                border: none;
                border-right: 1px solid {panel_border};
            }}
            QTabBar::tab:selected {{
                background-color: {bg};
                color: {fg};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {selection};
            }}
            QTabBar::close-button {{
                image: none;
                subcontrol-position: right;
            }}
            QTabBar::close-button:hover {{
                background-color: {panel_border};
            }}
        """)

        # Apply to all editors
        for i in range(self.count()):
            editor = self.widget(i)
            if editor:
                editor.apply_ui_theme(theme)

    # Session management methods

    def has_unsaved_changes(self) -> bool:
        """Check if any tab has unsaved changes."""
        for i in range(self.count()):
            editor = self.widget(i)
            if editor and editor.isModified():
                return True
        return False

    def save_all(self):
        """Save all modified files."""
        for i in range(self.count()):
            editor = self.widget(i)
            if editor and editor.isModified():
                file_path = editor.property("file_path")
                if file_path:
                    self._save_editor_to_file(editor, file_path)

    def get_all_file_paths(self) -> List[Path]:
        """Get list of all open file paths (excluding untitled)."""
        paths = []
        for i in range(self.count()):
            editor = self.widget(i)
            if editor:
                file_path = editor.property("file_path")
                if file_path:
                    paths.append(file_path)
        return paths

    def _save_editor_to_file(self, editor: EditorWidget, file_path: Path) -> bool:
        """Save editor content to file."""
        try:
            content = editor.text()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            editor.setModified(False)
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file:\n{e}"
            )
            return False

