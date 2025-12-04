# Just Code Editor - File Browser Panel
# Auto-hiding file tree panel

from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QLabel, QHBoxLayout, QPushButton,
    QMenu, QComboBox
)
from PyQt6.QtCore import Qt, QDir, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFileSystemModel, QFont, QAction


class FileBrowserPanel(QWidget):
    """Auto-hiding file browser panel with directory tree."""

    # Signal emitted when a file is double-clicked
    file_opened = pyqtSignal(str)

    # Signal emitted when bookmarks change (for saving to settings)
    bookmarks_changed = pyqtSignal(list)

    # Signal emitted when default directory changes
    default_directory_changed = pyqtSignal(str)

    # Signal emitted when the current directory changes (for terminal sync)
    directory_changed = pyqtSignal(str)

    # Signal emitted when a file/folder is selected (single click)
    item_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize the file browser panel."""
        super().__init__(parent)

        self.current_directory: Optional[Path] = None
        self._font_size = 11
        self._bookmarks: List[str] = []
        self._default_directory: str = ""
        # Initialize theme colors before _setup_ui (which calls _get_button_style)
        self._theme_colors = {
            'background': '#1e1e1e',
            'foreground': '#cccccc',
            'panel_background': '#252526',
            'panel_border': '#3c3c3c',
            'line_highlight': '#2a2a2a',
            'selection': '#37373d'
        }
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with navigation buttons
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(4, 4, 4, 4)
        header_layout.setSpacing(4)

        # Up button (go to parent directory)
        self.up_button = QPushButton("↑")
        self.up_button.setFixedSize(24, 24)
        self.up_button.setToolTip("Go to parent directory")
        self.up_button.setStyleSheet(self._get_button_style())
        self.up_button.clicked.connect(self._go_up)
        self.up_button.setEnabled(False)
        header_layout.addWidget(self.up_button)

        # Bookmark button
        self.bookmark_button = QPushButton("★")
        self.bookmark_button.setFixedSize(24, 24)
        self.bookmark_button.setToolTip("Bookmarks")
        self.bookmark_button.setStyleSheet(self._get_button_style())
        self.bookmark_button.clicked.connect(self._show_bookmark_menu)
        header_layout.addWidget(self.bookmark_button)

        # Header label
        self.header_label = QLabel("NO FOLDER")
        self.header_label.setStyleSheet("""
            QLabel {
                padding: 4px;
                font-weight: bold;
                background-color: #252526;
                color: #cccccc;
            }
        """)
        header_layout.addWidget(self.header_label, 1)

        header_widget.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border-bottom: 1px solid #3c3c3c;
            }
        """)
        layout.addWidget(header_widget)

        # File tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)

        # Style the tree view
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: #1e1e1e;
                color: #cccccc;
                border: none;
                outline: none;
            }
            QTreeView::item:hover {
                background-color: #2a2a2a;
            }
            QTreeView::item:selected {
                background-color: #37373d;
                color: #ffffff;
            }
        """)

        # File system model
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)

        # Hide all columns except name
        self.tree_view.setModel(self.model)
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)

        # Connect signals
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.tree_view.clicked.connect(self._on_item_clicked)

        layout.addWidget(self.tree_view)

        # Set default size
        self.setMinimumWidth(200)
        self.setMaximumWidth(400)

    def apply_ui_theme(self, theme_data: dict):
        """
        Apply UI theme colors to the file browser.

        Args:
            theme_data: Dictionary of theme color names to hex values
        """
        if theme_data.get('use_system_theme', False):
            return

        bg = theme_data.get('background', '#1e1e1e')
        fg = theme_data.get('foreground', '#cccccc')
        panel_bg = theme_data.get('panel_background', '#252526')
        panel_border = theme_data.get('panel_border', '#3c3c3c')
        line_highlight = theme_data.get('line_highlight', '#2a2a2a')
        selection = theme_data.get('selection', '#37373d')

        # Store for button styling
        self._theme_colors = {
            'background': bg,
            'foreground': fg,
            'panel_background': panel_bg,
            'panel_border': panel_border,
            'line_highlight': line_highlight,
            'selection': selection
        }

        # Header styling
        self.header_label.setStyleSheet(f"""
            QLabel {{
                padding: 4px;
                font-weight: bold;
                background-color: {panel_bg};
                color: {fg};
            }}
        """)

        # Header widget
        self.header_label.parentWidget().setStyleSheet(f"""
            QWidget {{
                background-color: {panel_bg};
                border-bottom: 1px solid {panel_border};
            }}
        """)

        # Tree view styling
        self.tree_view.setStyleSheet(f"""
            QTreeView {{
                background-color: {bg};
                color: {fg};
                border: none;
                outline: none;
            }}
            QTreeView::item:hover {{
                background-color: {line_highlight};
            }}
            QTreeView::item:selected {{
                background-color: {selection};
                color: #ffffff;
            }}
        """)

        # Update button styles
        button_style = self._get_button_style()
        self.up_button.setStyleSheet(button_style)
        self.bookmark_button.setStyleSheet(button_style)

    def _get_button_style(self) -> str:
        """Get the stylesheet for header buttons."""
        bg = self._theme_colors.get('panel_border', '#3c3c3c')
        fg = self._theme_colors.get('foreground', '#cccccc')
        panel_bg = self._theme_colors.get('panel_background', '#252526')
        hover = self._theme_colors.get('line_highlight', '#505050')

        return f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {panel_bg};
            }}
            QPushButton:disabled {{
                background-color: {panel_bg};
                color: #666666;
            }}
        """

    def set_directory(self, directory: str):
        """
        Set the root directory to display.

        Args:
            directory: Path to the directory
        """
        self.current_directory = Path(directory)

        # Set the model root path
        self.model.setRootPath(directory)

        # Show ONLY this directory and its contents (not parent directories)
        index = self.model.index(directory)
        self.tree_view.setRootIndex(index)

        # Update header label to show just the folder name
        self.header_label.setText(self.current_directory.name)

        # Enable/disable up button based on whether we can go up
        # Disable if we're at root (/)
        self.up_button.setEnabled(self.current_directory.parent != self.current_directory)

        # Emit signal for terminal sync
        self.directory_changed.emit(directory)

    def set_font_size(self, size: int):
        """
        Set the font size for the file browser.

        Args:
            size: Font size in points
        """
        self._font_size = size
        font = QFont()
        font.setPointSize(size)
        self.tree_view.setFont(font)

    def set_bookmarks(self, bookmarks: List[str]):
        """
        Set the list of bookmarks.

        Args:
            bookmarks: List of directory paths
        """
        self._bookmarks = bookmarks if bookmarks else []

    def add_bookmark(self, path: str):
        """
        Add a bookmark.

        Args:
            path: Directory path to bookmark
        """
        if path and path not in self._bookmarks:
            self._bookmarks.append(path)
            self.bookmarks_changed.emit(self._bookmarks)

    def remove_bookmark(self, path: str):
        """
        Remove a bookmark.

        Args:
            path: Directory path to remove from bookmarks
        """
        if path in self._bookmarks:
            self._bookmarks.remove(path)
            self.bookmarks_changed.emit(self._bookmarks)

    def _show_bookmark_menu(self):
        """Show the bookmark menu."""
        menu = QMenu(self)

        # Add current directory to bookmarks action
        if self.current_directory:
            current_path = str(self.current_directory)
            if current_path in self._bookmarks:
                remove_action = QAction(f"Remove '{self.current_directory.name}' from bookmarks", self)
                remove_action.triggered.connect(lambda: self.remove_bookmark(current_path))
                menu.addAction(remove_action)
            else:
                add_action = QAction(f"Bookmark '{self.current_directory.name}'", self)
                add_action.triggered.connect(lambda: self.add_bookmark(current_path))
                menu.addAction(add_action)
            menu.addSeparator()

        # List existing bookmarks with submenus
        if self._bookmarks:
            for bookmark in self._bookmarks:
                bookmark_path = Path(bookmark)

                # Create submenu for this bookmark
                submenu = QMenu(bookmark_path.name, self)
                submenu.setToolTip(bookmark)

                # Go to this bookmark
                go_action = QAction("Open", self)
                go_action.triggered.connect(lambda checked, p=bookmark: self.set_directory(p))
                submenu.addAction(go_action)

                # Set as default directory
                default_action = QAction("Set as Default Directory", self)
                if bookmark == self._default_directory:
                    default_action.setText("✓ Default Directory")
                    default_action.setEnabled(False)
                default_action.triggered.connect(lambda checked, p=bookmark: self._set_default_directory(p))
                submenu.addAction(default_action)

                submenu.addSeparator()

                # Remove bookmark
                remove_action = QAction("Remove Bookmark", self)
                remove_action.triggered.connect(lambda checked, p=bookmark: self.remove_bookmark(p))
                submenu.addAction(remove_action)

                menu.addMenu(submenu)
        else:
            no_bookmarks = QAction("No bookmarks", self)
            no_bookmarks.setEnabled(False)
            menu.addAction(no_bookmarks)

        # Show menu below the bookmark button
        menu.exec(self.bookmark_button.mapToGlobal(self.bookmark_button.rect().bottomLeft()))

    def _set_default_directory(self, path: str):
        """
        Set the default directory.

        Args:
            path: Directory path to set as default
        """
        self._default_directory = path
        self.default_directory_changed.emit(path)

    def set_default_directory(self, path: str):
        """
        Set the default directory (from settings, without emitting signal).

        Args:
            path: Directory path
        """
        self._default_directory = path

    def _show_context_menu(self, position):
        """Show context menu for tree items."""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        path = Path(file_path)

        menu = QMenu(self)

        if path.is_dir():
            # Add bookmark option for directories
            if file_path in self._bookmarks:
                action = QAction(f"Remove from bookmarks", self)
                action.triggered.connect(lambda: self.remove_bookmark(file_path))
            else:
                action = QAction(f"Add to bookmarks", self)
                action.triggered.connect(lambda: self.add_bookmark(file_path))
            menu.addAction(action)

        if menu.actions():
            menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def _go_up(self):
        """Go up to parent directory."""
        if self.current_directory and self.current_directory.parent != self.current_directory:
            parent = str(self.current_directory.parent)
            self.set_directory(parent)

    def _on_item_double_clicked(self, index):
        """
        Handle double-click on tree item.

        Args:
            index: QModelIndex of the clicked item
        """
        file_path = self.model.filePath(index)
        path = Path(file_path)

        if path.is_dir():
            # Navigate into the directory
            self.set_directory(file_path)
        elif path.is_file():
            # Open the file
            self.file_opened.emit(file_path)

    def _on_item_clicked(self, index):
        """
        Handle single-click on tree item - emit selected path for terminal sync.

        Args:
            index: QModelIndex of the clicked item
        """
        file_path = self.model.filePath(index)
        path = Path(file_path)

        # Emit the directory containing the selected item
        if path.is_dir():
            self.item_selected.emit(file_path)
        elif path.is_file():
            # For files, emit the parent directory
            self.item_selected.emit(str(path.parent))
