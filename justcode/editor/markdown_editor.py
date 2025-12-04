# Just Code Editor - Markdown Editor Widget
# Combines editor with split preview pane for markdown files

from typing import Optional, Dict
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal

from .editor_widget import EditorWidget
from .markdown_preview import MarkdownPreview
from .syntax.markdown import MarkdownLexer


class MarkdownEditorWidget(QWidget):
    """
    Editor widget for markdown files with split preview support.
    
    Wraps an EditorWidget and a MarkdownPreview in a horizontal splitter.
    The preview can be toggled on/off.
    """
    
    # Forward signals from the editor
    modificationChanged = pyqtSignal(bool)
    textChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the markdown editor widget."""
        super().__init__(parent)
        
        # Preview visibility state
        self._preview_visible = False
        self._syntax_theme: Optional[Dict] = None
        self._ui_theme: Optional[Dict] = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter for editor and preview
        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        
        # Create editor
        self._editor = EditorWidget(self._splitter)
        self._splitter.addWidget(self._editor)
        
        # Create preview (initially hidden)
        self._preview = MarkdownPreview(self._splitter)
        self._splitter.addWidget(self._preview)
        self._preview.hide()
        
        # Set initial splitter sizes (50/50 when preview is shown)
        self._splitter.setSizes([500, 500])
        
        # Style splitter handle
        self._splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3c3c3c;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #569cd6;
            }
        """)
        
        layout.addWidget(self._splitter)
        
        # Apply markdown lexer to editor
        self._apply_markdown_lexer()
    
    def _connect_signals(self):
        """Connect internal signals."""
        # Forward editor signals
        self._editor.modificationChanged.connect(self.modificationChanged.emit)
        self._editor.textChanged.connect(self._on_text_changed)
    
    def _on_text_changed(self):
        """Handle text changes - update preview if visible."""
        self.textChanged.emit()
        if self._preview_visible:
            self._preview.update_preview(self._editor.text())
    
    def _apply_markdown_lexer(self):
        """Apply markdown syntax highlighting to the editor."""
        # Get background/foreground from UI theme
        bg = "#1e1e1e"
        fg = "#d4d4d4"
        if self._ui_theme:
            bg = self._ui_theme.get('background', bg)
            fg = self._ui_theme.get('foreground', fg)

        lexer = MarkdownLexer(self._editor, self._syntax_theme, background=bg, foreground=fg)
        self._editor.setLexer(lexer)
    
    # === Editor interface passthrough ===
    
    def text(self) -> str:
        """Get editor text."""
        return self._editor.text()
    
    def setText(self, text: str):
        """Set editor text."""
        self._editor.setText(text)
        if self._preview_visible:
            self._preview.update_preview(text, debounce_ms=0)
    
    def isModified(self) -> bool:
        """Check if editor has unsaved changes."""
        return self._editor.isModified()
    
    def setModified(self, modified: bool):
        """Set modification state."""
        self._editor.setModified(modified)
    
    def insert(self, text: str):
        """Insert text at cursor."""
        self._editor.insert(text)
    
    def getCursorPosition(self):
        """Get cursor position."""
        return self._editor.getCursorPosition()
    
    def setCursorPosition(self, line: int, col: int):
        """Set cursor position."""
        self._editor.setCursorPosition(line, col)
    
    def selectedText(self) -> str:
        """Get selected text."""
        return self._editor.selectedText()
    
    def replaceSelectedText(self, text: str):
        """Replace selected text."""
        self._editor.replaceSelectedText(text)
    
    def selectAll(self):
        """Select all text."""
        self._editor.selectAll()
    
    def hasSelectedText(self) -> bool:
        """Check if text is selected."""
        return self._editor.hasSelectedText()
    
    def setFocus(self):
        """Set focus to editor."""
        self._editor.setFocus()
    
    def setLexer(self, lexer):
        """Set lexer (ignored for markdown - always uses markdown lexer)."""
        # We always use the markdown lexer for this widget
        pass
    
    def font(self):
        """Get editor font."""
        return self._editor.font()

    def paper(self):
        """Get editor background color."""
        return self._editor.paper()

    # === Preview control ===

    def toggle_preview(self) -> bool:
        """
        Toggle the preview pane visibility.

        Returns:
            True if preview is now visible, False otherwise
        """
        self._preview_visible = not self._preview_visible

        if self._preview_visible:
            # Show preview and update content
            self._preview.show()
            self._preview.update_preview(self._editor.text(), debounce_ms=0)
            # Restore splitter sizes to 50/50
            total = self._splitter.width()
            self._splitter.setSizes([total // 2, total // 2])
        else:
            self._preview.hide()

        return self._preview_visible

    def is_preview_visible(self) -> bool:
        """Check if preview is currently visible."""
        return self._preview_visible

    def show_preview(self):
        """Show the preview pane."""
        if not self._preview_visible:
            self.toggle_preview()

    def hide_preview(self):
        """Hide the preview pane."""
        if self._preview_visible:
            self.toggle_preview()

    # === Settings and theming ===

    def apply_settings(self, settings):
        """
        Apply editor settings.

        Args:
            settings: EditorSettings instance
        """
        self._editor.apply_settings(settings)
        # Re-apply markdown lexer after settings
        self._apply_markdown_lexer()

    def set_syntax_theme(self, theme: Dict[str, str]):
        """
        Set syntax theme colors.

        Args:
            theme: Dictionary of syntax element names to hex colors
        """
        self._syntax_theme = theme
        self._apply_markdown_lexer()

    def apply_ui_theme(self, theme: Dict[str, str]):
        """
        Apply UI theme to editor and preview.

        Args:
            theme: Dictionary with color values
        """
        self._ui_theme = theme

        # Apply to editor
        if hasattr(self._editor, 'apply_ui_theme'):
            self._editor.apply_ui_theme(theme)

        # Apply to preview
        self._preview.apply_theme(theme)

        # Re-apply lexer with new theme
        self._apply_markdown_lexer()

    # === Direct editor access ===

    @property
    def editor(self) -> EditorWidget:
        """Get the underlying EditorWidget."""
        return self._editor

    @property
    def preview(self) -> MarkdownPreview:
        """Get the preview widget."""
        return self._preview

