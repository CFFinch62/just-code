# Just Code Editor - Markdown Preview Widget
# Renders markdown content as HTML with live preview

import re
from typing import Optional, Dict
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor


class MarkdownPreview(QTextBrowser):
    """Widget that renders markdown content as HTML."""

    def __init__(self, parent=None):
        """Initialize the markdown preview widget."""
        super().__init__(parent)
        
        # Default styling
        self._background = "#1e1e1e"
        self._foreground = "#d4d4d4"
        self._link_color = "#4ec9b0"
        self._code_background = "#2d2d2d"
        self._header_color = "#569cd6"
        self._blockquote_color = "#808080"
        
        self._setup_ui()
        
        # Debounce timer for live updates
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._do_update)
        self._pending_markdown = ""
        
    def _setup_ui(self):
        """Set up the preview UI."""
        self.setOpenExternalLinks(True)
        self.setReadOnly(True)
        self._apply_style()
    
    def _apply_style(self):
        """Apply CSS styling to the preview."""
        self.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {self._background};
                color: {self._foreground};
                border: none;
                padding: 10px;
            }}
        """)
        
    def apply_theme(self, theme: Dict[str, str]):
        """
        Apply a UI theme to the preview.
        
        Args:
            theme: Dictionary with color values (background, foreground, etc.)
        """
        self._background = theme.get("background", self._background)
        self._foreground = theme.get("foreground", self._foreground)
        self._link_color = theme.get("link", self._link_color)
        self._code_background = theme.get("code_background", self._code_background)
        self._header_color = theme.get("header", self._header_color)
        self._apply_style()
        
        # Re-render if we have content
        if self._pending_markdown:
            self._do_update()

    def update_preview(self, markdown: str, debounce_ms: int = 150):
        """
        Update the preview with new markdown content.
        
        Args:
            markdown: The markdown text to render
            debounce_ms: Milliseconds to wait before updating (for live typing)
        """
        self._pending_markdown = markdown
        self._update_timer.stop()
        self._update_timer.start(debounce_ms)
    
    def _do_update(self):
        """Actually perform the markdown rendering."""
        html = self._render_markdown(self._pending_markdown)
        self.setHtml(html)
    
    def _render_markdown(self, markdown: str) -> str:
        """
        Convert markdown to HTML with styling.
        
        This is a simple markdown renderer. For full compatibility,
        consider using a library like markdown or mistune.
        
        Args:
            markdown: The markdown text
            
        Returns:
            HTML string with embedded CSS
        """
        # Escape HTML first
        html = markdown.replace("&", "&amp;")
        html = html.replace("<", "&lt;")
        html = html.replace(">", "&gt;")
        
        # Process code blocks first (``` ... ```)
        html = re.sub(
            r'```(\w*)\n(.*?)```',
            lambda m: f'<pre style="background-color: {self._code_background}; padding: 10px; border-radius: 4px; overflow-x: auto;"><code>{m.group(2)}</code></pre>',
            html,
            flags=re.DOTALL
        )
        
        # Inline code (`code`)
        html = re.sub(
            r'`([^`]+)`',
            f'<code style="background-color: {self._code_background}; padding: 2px 4px; border-radius: 3px;">\\1</code>',
            html
        )
        
        # Headers (# ## ### etc.)
        for i in range(6, 0, -1):
            pattern = r'^' + '#' * i + r' (.+)$'
            size = 2.0 - (i - 1) * 0.2  # h1=2.0em, h2=1.8em, etc.
            html = re.sub(
                pattern,
                f'<h{i} style="color: {self._header_color}; font-size: {size}em; margin: 0.5em 0;">\\1</h{i}>',
                html,
                flags=re.MULTILINE
            )
        
        # Bold (**text** or __text__)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
        
        # Italic (*text* or _text_)
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        html = re.sub(r'_([^_]+)_', r'<em>\1</em>', html)
        
        # Strikethrough (~~text~~)
        html = re.sub(r'~~(.+?)~~', r'<del>\1</del>', html)
        
        # Links [text](url)
        html = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            f'<a href="\\2" style="color: {self._link_color};">\\1</a>',
            html
        )
        
        # Images ![alt](url)
        html = re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            r'<img src="\2" alt="\1" style="max-width: 100%;">',
            html
        )
        
        # Blockquotes (> text)
        html = re.sub(
            r'^&gt; (.+)$',
            f'<blockquote style="border-left: 3px solid {self._blockquote_color}; padding-left: 10px; margin: 5px 0; color: {self._blockquote_color};">\\1</blockquote>',
            html,
            flags=re.MULTILINE
        )

        # Horizontal rules (---, ***, ___)
        html = re.sub(
            r'^[-*_]{3,}$',
            f'<hr style="border: none; border-top: 1px solid {self._blockquote_color}; margin: 10px 0;">',
            html,
            flags=re.MULTILINE
        )

        # Unordered lists (- or * or +)
        html = re.sub(
            r'^[\-\*\+] (.+)$',
            r'<li>\1</li>',
            html,
            flags=re.MULTILINE
        )

        # Ordered lists (1. 2. etc.)
        html = re.sub(
            r'^\d+\. (.+)$',
            r'<li>\1</li>',
            html,
            flags=re.MULTILINE
        )

        # Wrap consecutive <li> items in <ul>
        html = re.sub(
            r'((?:<li>.*?</li>\n?)+)',
            r'<ul style="margin: 5px 0; padding-left: 20px;">\1</ul>',
            html,
            flags=re.DOTALL
        )

        # Convert remaining newlines to <br> (but not in pre blocks)
        # Split by pre tags, process non-pre parts
        parts = re.split(r'(<pre.*?</pre>)', html, flags=re.DOTALL)
        for i, part in enumerate(parts):
            if not part.startswith('<pre'):
                # Convert double newlines to paragraphs
                parts[i] = re.sub(r'\n\n+', '</p><p>', part)
                # Convert single newlines to <br>
                parts[i] = re.sub(r'\n', '<br>', parts[i])
        html = ''.join(parts)

        # Wrap in styled container
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: {self._foreground};
                    background-color: {self._background};
                    padding: 10px;
                }}
                p {{
                    margin: 0.5em 0;
                }}
                a {{
                    color: {self._link_color};
                }}
            </style>
        </head>
        <body>
            <p>{html}</p>
        </body>
        </html>
        """

        return styled_html

