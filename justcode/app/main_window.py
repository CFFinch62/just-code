# Just Code Editor - Main Window
# Main window class, coordinates panels

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QStatusBar, QFontDialog, QDockWidget, QWidget
)
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QEvent, QFileSystemWatcher

from ..editor import EditorWidget, TabEditorWidget
from ..config import Settings, ConfigLoader, ThemeManager, SessionManager
from ..panels import FileBrowserPanel, TerminalPanel
from ..plugins import PluginManager, ActionExecutor


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config_loader: ConfigLoader):
        """
        Initialize the main window.
        
        Args:
            config_loader: ConfigLoader instance
        """
        super().__init__()

        self.config_loader = config_loader
        self.settings: Optional[Settings] = None
        self.current_file: Optional[Path] = None

        # Session manager for remembering open files
        self.session_manager = SessionManager()

        # Panel visibility tracking
        self.file_browser_visible = False
        self.terminal_visible = False

        # Animation tracking
        self.file_browser_animation = None
        self.terminal_animation = None

        # Keybindings system
        self._actions: dict[str, QAction] = {}  # command_id -> QAction
        self._keybindings: dict[str, str] = {}  # command_id -> shortcut

        # Create the tab editor widget (multi-file support)
        self.tab_editor = TabEditorWidget(self)
        self.tab_editor.current_file_changed.connect(self._on_current_file_changed)
        self.tab_editor.file_modified_changed.connect(self._on_file_modified_changed)
        self.tab_editor.file_saved.connect(self._on_file_saved)
        self.setCentralWidget(self.tab_editor)

        # Alias for compatibility (some methods still use self.editor)
        self.editor = self.tab_editor.current_editor()

        # Create panels
        self._create_file_browser_panel()
        self._create_terminal_panel()

        # Setup plugin system
        self._setup_plugins()

        # Setup
        self._load_settings()
        self._setup_ui()
        self._create_menus()
        self._apply_theme()
        self._setup_file_watcher()

        # Restore session (open files from last session)
        self._restore_session()
        
    def _create_file_browser_panel(self):
        """Create the file browser panel."""
        # Create the file browser widget
        self.file_browser = FileBrowserPanel(self)
        self.file_browser.file_opened.connect(self._load_file)
        self.file_browser.bookmarks_changed.connect(self._on_bookmarks_changed)
        self.file_browser.default_directory_changed.connect(self._on_default_directory_changed)
        # Connect directory signals for terminal sync
        self.file_browser.directory_changed.connect(self._sync_terminal_directory)
        self.file_browser.item_selected.connect(self._sync_terminal_directory)

        # Create dock widget for file browser
        self.file_browser_dock = QDockWidget("Files", self)
        self.file_browser_dock.setWidget(self.file_browser)
        self.file_browser_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.file_browser_dock.setTitleBarWidget(QWidget())  # Hide title bar

        # Style the dock
        self.file_browser_dock.setStyleSheet("""
            QDockWidget {
                border: none;
                border-right: 1px solid #3c3c3c;
            }
        """)

        # Add to left side
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_browser_dock)

        # Start hidden
        self.file_browser_dock.hide()
        self.file_browser_visible = False

    def _on_bookmarks_changed(self, bookmarks: list):
        """Handle bookmarks changes from file browser."""
        if self.settings:
            self.settings.file_browser.bookmarks = bookmarks
            self.config_loader.save_settings(self.settings)

    def _on_default_directory_changed(self, directory: str):
        """Handle default directory changes from file browser."""
        if self.settings:
            self.settings.file_browser.default_directory = directory
            self.config_loader.save_settings(self.settings)

    def _sync_terminal_directory(self, directory: str):
        """
        Sync the terminal's working directory to match file browser/editor.

        Args:
            directory: Path to set as terminal working directory
        """
        if hasattr(self, 'terminal') and self.terminal:
            self.terminal.set_working_directory(directory)

    def _create_terminal_panel(self):
        """Create the terminal panel."""
        # Create the terminal widget
        self.terminal = TerminalPanel(self)

        # Create dock widget for terminal
        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setWidget(self.terminal)
        self.terminal_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.terminal_dock.setTitleBarWidget(QWidget())  # Hide title bar

        # Style the dock
        self.terminal_dock.setStyleSheet("""
            QDockWidget {
                border: none;
                border-top: 1px solid #3c3c3c;
            }
        """)

        # Add to bottom
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)

        # Start hidden
        self.terminal_dock.hide()
        self.terminal_visible = False

    def _setup_plugins(self):
        """Initialize the plugin system."""
        # Create plugin manager
        self.plugin_manager = PluginManager()

        # Create action executor with callbacks
        self.action_executor = ActionExecutor()
        self.action_executor.set_callbacks(
            notify=self._plugin_notify,
            get_editor_text=self._plugin_get_editor_text,
            set_editor_text=self._plugin_set_editor_text,
            get_selection=self._plugin_get_selection,
            replace_selection=self._plugin_replace_selection,
            insert_text=self._plugin_insert_text,
            get_cursor_position=self._plugin_get_cursor_position,
            set_cursor_position=self._plugin_set_cursor_position,
            get_file_path=self._plugin_get_file_path,
            get_language=self._get_current_language
        )

        # Connect plugin manager to action executor
        self.plugin_manager.set_action_executor(self.action_executor)

        # Load all plugins
        self.plugin_manager.load_plugins()

    def _load_settings(self):
        """Load application settings."""
        self.settings = self.config_loader.load_settings()
        if hasattr(self, 'tab_editor'):
            self.tab_editor.apply_settings(self.settings.editor)

        # Apply file browser settings
        if hasattr(self, 'file_browser'):
            self.file_browser.set_font_size(self.settings.file_browser.font_size)
            self.file_browser.set_bookmarks(self.settings.file_browser.bookmarks)
            self.file_browser.set_default_directory(self.settings.file_browser.default_directory)

            # Set default directory if specified and no directory is currently set
            if (self.settings.file_browser.default_directory
                and not self.file_browser.current_directory):
                default_dir = Path(self.settings.file_browser.default_directory)
                if default_dir.exists():
                    self.file_browser.set_directory(str(default_dir))

    def _load_keybindings(self):
        """Load keybindings from keybindings.json."""
        import json
        keybindings_path = self.config_loader.get_config_file_path("keybindings.json")

        try:
            if keybindings_path.exists():
                with open(keybindings_path, 'r') as f:
                    data = json.load(f)
                    # Filter out comments (keys starting with _)
                    self._keybindings = {k: v for k, v in data.items() if not k.startswith('_')}
            else:
                self._keybindings = {}
        except Exception as e:
            print(f"Error loading keybindings: {e}")
            self._keybindings = {}

    def _apply_keybindings(self):
        """Apply loaded keybindings to registered actions."""
        for command_id, shortcut in self._keybindings.items():
            if command_id in self._actions:
                action = self._actions[command_id]
                if shortcut:
                    action.setShortcut(shortcut)
                else:
                    action.setShortcut("")  # Clear shortcut if empty

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Just Code")
        self.resize(1200, 800)

        # Set application icon
        icon_path = self.config_loader.get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))

        # Status bar (minimal)
        if self.settings and self.settings.ui.show_status_bar:
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("Ready")

    def _create_menus(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # Load keybindings first
        self._load_keybindings()

        # File menu
        file_menu = menubar.addMenu("&File")

        # New
        new_action = QAction("&New", self)
        new_action.triggered.connect(self._file_new)
        file_menu.addAction(new_action)
        self._actions["file.new"] = new_action

        # Open
        open_action = QAction("&Open", self)
        open_action.triggered.connect(self._file_open)
        file_menu.addAction(open_action)
        self._actions["file.open"] = open_action

        # Open Folder
        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.triggered.connect(self._file_open_folder)
        file_menu.addAction(open_folder_action)
        self._actions["file.open_folder"] = open_folder_action

        file_menu.addSeparator()

        # Save
        save_action = QAction("&Save", self)
        save_action.triggered.connect(self._file_save)
        file_menu.addAction(save_action)
        self._actions["file.save"] = save_action

        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.triggered.connect(self._file_save_as)
        file_menu.addAction(save_as_action)
        self._actions["file.save_as"] = save_as_action

        file_menu.addSeparator()

        # Close
        close_action = QAction("&Close", self)
        close_action.triggered.connect(self._file_close)
        file_menu.addAction(close_action)
        self._actions["file.close"] = close_action

        # Close Others
        close_others_action = QAction("Close &Others", self)
        close_others_action.triggered.connect(self._file_close_others)
        file_menu.addAction(close_others_action)

        # Close All
        close_all_action = QAction("Close &All", self)
        close_all_action.triggered.connect(self._file_close_all)
        file_menu.addAction(close_all_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        self._actions["file.exit"] = exit_action

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Undo
        undo_action = QAction("&Undo", self)
        undo_action.triggered.connect(self._edit_undo)
        edit_menu.addAction(undo_action)
        self._actions["edit.undo"] = undo_action

        # Redo
        redo_action = QAction("&Redo", self)
        redo_action.triggered.connect(self._edit_redo)
        edit_menu.addAction(redo_action)
        self._actions["edit.redo"] = redo_action

        edit_menu.addSeparator()

        # Cut
        cut_action = QAction("Cu&t", self)
        cut_action.triggered.connect(self._edit_cut)
        edit_menu.addAction(cut_action)
        self._actions["edit.cut"] = cut_action

        # Copy
        copy_action = QAction("&Copy", self)
        copy_action.triggered.connect(self._edit_copy)
        edit_menu.addAction(copy_action)
        self._actions["edit.copy"] = copy_action

        # Paste
        paste_action = QAction("&Paste", self)
        paste_action.triggered.connect(self._edit_paste)
        edit_menu.addAction(paste_action)
        self._actions["edit.paste"] = paste_action

        # Run menu
        run_menu = menubar.addMenu("&Run")

        # Run File
        run_file_action = QAction("&Run File", self)
        run_file_action.triggered.connect(self._run_current_file)
        run_menu.addAction(run_file_action)
        self._actions["run.run_file"] = run_file_action

        # View menu
        view_menu = menubar.addMenu("&View")

        # Toggle File Browser
        toggle_browser_action = QAction("Toggle &File Browser", self)
        toggle_browser_action.triggered.connect(self._toggle_file_browser)
        view_menu.addAction(toggle_browser_action)
        self._actions["view.toggle_file_browser"] = toggle_browser_action

        # Toggle Terminal
        toggle_terminal_action = QAction("Toggle &Terminal", self)
        toggle_terminal_action.triggered.connect(self._toggle_terminal)
        view_menu.addAction(toggle_terminal_action)
        self._actions["view.toggle_terminal"] = toggle_terminal_action

        # Toggle Markdown Preview
        self._toggle_preview_action = QAction("Toggle &Markdown Preview", self)
        self._toggle_preview_action.triggered.connect(self._toggle_markdown_preview)
        self._toggle_preview_action.setEnabled(False)  # Disabled until a markdown file is open
        view_menu.addAction(self._toggle_preview_action)
        self._actions["view.toggle_markdown_preview"] = self._toggle_preview_action

        view_menu.addSeparator()

        # Font
        font_action = QAction("F&ont...", self)
        font_action.triggered.connect(self._select_font)
        view_menu.addAction(font_action)

        view_menu.addSeparator()

        # Zoom In
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.triggered.connect(self._view_zoom_in)
        view_menu.addAction(zoom_in_action)
        self._actions["view.zoom_in"] = zoom_in_action

        # Zoom Out
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.triggered.connect(self._view_zoom_out)
        view_menu.addAction(zoom_out_action)
        self._actions["view.zoom_out"] = zoom_out_action

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        # Open Settings
        open_settings_action = QAction("Open &Settings", self)
        open_settings_action.triggered.connect(lambda: self._open_config_file("settings.json"))
        settings_menu.addAction(open_settings_action)
        self._actions["settings.open"] = open_settings_action

        # Apply keybindings to all actions
        self._apply_keybindings()

        # Open UI Themes
        open_ui_themes_action = QAction("Open &UI Themes", self)
        open_ui_themes_action.triggered.connect(lambda: self._open_config_file("ui-themes.json"))
        settings_menu.addAction(open_ui_themes_action)

        # Open Syntax Themes
        open_syntax_themes_action = QAction("Open S&yntax Themes", self)
        open_syntax_themes_action.triggered.connect(lambda: self._open_config_file("syntax-themes.json"))
        settings_menu.addAction(open_syntax_themes_action)

        # Open Languages
        open_languages_action = QAction("Open &Languages", self)
        open_languages_action.triggered.connect(lambda: self._open_config_file("languages.json"))
        settings_menu.addAction(open_languages_action)

        # Open Keybindings
        open_keybindings_action = QAction("Open &Keybindings", self)
        open_keybindings_action.triggered.connect(lambda: self._open_config_file("keybindings.json"))
        settings_menu.addAction(open_keybindings_action)

        settings_menu.addSeparator()

        # UI Theme submenu (populated dynamically)
        self.theme_menu = settings_menu.addMenu("UI &Theme")
        self._populate_theme_menu()

        # Plugins menu
        self.plugins_menu = menubar.addMenu("&Plugins")
        self._populate_plugins_menu()

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _populate_theme_menu(self):
        """Populate the UI theme menu from ui-themes.json."""
        # Clear existing items
        self.theme_menu.clear()

        # Get available themes
        theme_names = self.config_loader.get_ui_theme_names()

        # Get current theme for checkmark
        current_theme = self.settings.ui.theme if self.settings else "default-dark"

        for theme_name in theme_names:
            # Create action for each theme
            action = QAction(theme_name, self)
            action.setCheckable(True)
            action.setChecked(theme_name == current_theme)
            # Use default argument to capture theme_name correctly in lambda
            action.triggered.connect(lambda checked, name=theme_name: self._switch_ui_theme(name))
            self.theme_menu.addAction(action)

    def _populate_plugins_menu(self):
        """Populate the Plugins menu with discovered plugin commands."""
        self.plugins_menu.clear()

        # Reload Plugins action
        reload_action = QAction("&Reload Plugins", self)
        reload_action.triggered.connect(self._reload_plugins)
        self.plugins_menu.addAction(reload_action)

        # Open Plugins Folder
        open_folder_action = QAction("&Open Plugins Folder", self)
        open_folder_action.triggered.connect(self._open_plugins_folder)
        self.plugins_menu.addAction(open_folder_action)

        self.plugins_menu.addSeparator()

        # Get all plugin commands
        commands = self.plugin_manager.get_all_commands()

        if not commands:
            # No plugins installed
            no_plugins_action = QAction("(No plugins installed)", self)
            no_plugins_action.setEnabled(False)
            self.plugins_menu.addAction(no_plugins_action)
        else:
            # Group commands by plugin
            plugins_with_commands = {}
            for cmd in commands:
                plugin_name = cmd['plugin_name']
                if plugin_name not in plugins_with_commands:
                    plugins_with_commands[plugin_name] = []
                plugins_with_commands[plugin_name].append(cmd)

            # Create submenus for each plugin
            for plugin_name, cmds in plugins_with_commands.items():
                if len(plugins_with_commands) > 1:
                    # Multiple plugins: create submenu
                    plugin_submenu = self.plugins_menu.addMenu(plugin_name)
                    menu_to_use = plugin_submenu
                else:
                    # Single plugin: add directly to plugins menu
                    menu_to_use = self.plugins_menu

                for cmd in cmds:
                    action = QAction(cmd['command_name'], self)
                    if cmd['shortcut']:
                        action.setShortcut(cmd['shortcut'])
                    # Capture values in lambda
                    action.triggered.connect(
                        lambda checked, pn=plugin_name, tid=cmd['trigger'].id:
                        self._execute_plugin_command(pn, tid)
                    )
                    menu_to_use.addAction(action)

    def _reload_plugins(self):
        """Reload all plugins."""
        self.plugin_manager.load_plugins()
        self._populate_plugins_menu()
        QMessageBox.information(self, "Plugins", "Plugins reloaded successfully.")

    def _open_plugins_folder(self):
        """Open the plugins folder in the file browser."""
        plugins_dir = Path.home() / ".config" / "justcode" / "plugins"
        plugins_dir.mkdir(parents=True, exist_ok=True)

        # Show in file browser
        self.file_browser.set_directory(str(plugins_dir))
        if not self.file_browser_visible:
            self._toggle_file_browser()

    def _execute_plugin_command(self, plugin_name: str, trigger_id: str):
        """Execute a plugin command."""
        # Build context
        context = {
            'file_path': self.tab_editor.current_file_path(),
            'language': self._get_current_language()
        }

        success = self.plugin_manager.execute_trigger(plugin_name, trigger_id, context)
        if not success:
            # Error already shown by action executor
            pass

    def _get_current_language(self) -> str:
        """Get the current file's language/type."""
        file_path = self.tab_editor.current_file_path()
        if file_path:
            ext = file_path.suffix.lower()
            # Map extensions to language names
            ext_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.md': 'markdown',
                '.sh': 'bash',
                '.c': 'c',
                '.cpp': 'cpp',
                '.h': 'c',
                '.hpp': 'cpp',
                '.java': 'java',
                '.rs': 'rust',
                '.go': 'go',
                '.rb': 'ruby',
                '.php': 'php',
            }
            return ext_map.get(ext, 'text')
        return 'text'

    def _apply_theme(self):
        """Apply the UI theme."""
        if not self.settings:
            return

        theme_data = self.config_loader.load_ui_theme(self.settings.ui.theme)
        theme_manager = ThemeManager(theme_data)

        # Apply stylesheet to window
        stylesheet = theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)

        # Apply theme to tab editor (and all editors)
        if hasattr(self, 'tab_editor'):
            self.tab_editor.apply_ui_theme(theme_data)

        # Apply theme to file browser
        if hasattr(self, 'file_browser'):
            self.file_browser.apply_ui_theme(theme_data)

        # Apply theme to terminal
        if hasattr(self, 'terminal'):
            self.terminal.apply_ui_theme(theme_data)

    def _switch_ui_theme(self, theme_name: str):
        """
        Switch to a different UI theme.

        Args:
            theme_name: Name of the theme to switch to
        """
        if not self.settings:
            return

        # Update settings in memory
        self.settings.ui.theme = theme_name

        # Apply the new theme
        self._apply_theme()

        # Re-apply lexer to update editor colors (background/foreground from UI theme)
        if self.current_file:
            self._apply_lexer_for_file(self.current_file)

        # Save to settings.json
        self.config_loader.save_settings(self.settings)

        # Update menu checkmarks
        self._populate_theme_menu()

        self._update_status(f"Switched to {theme_name} theme")

    def _setup_file_watcher(self):
        """Set up file watcher for config live reload."""
        # Create file watcher
        self.config_watcher = QFileSystemWatcher(self)

        # Get path to config directory
        config_dir = self.config_loader.get_config_file_path("").parent

        # Watch config files
        config_files = [
            "settings.json",
            "ui-themes.json",
            "syntax-themes.json",
            "languages.json",
            "keybindings.json",
        ]

        for filename in config_files:
            file_path = str(config_dir / filename)
            if Path(file_path).exists():
                self.config_watcher.addPath(file_path)

        # Connect file changed signal to reload handler
        self.config_watcher.fileChanged.connect(self._on_config_file_changed)

        self._update_status("Live config reload enabled")

    def _on_config_file_changed(self, path: str):
        """Handle config file changes for live reload."""
        file_name = Path(path).name
        self._update_status(f"Reloading {file_name}...")

        # Reload settings
        self._load_settings()

        # Re-apply theme
        self._apply_theme()

        # Apply editor settings
        if self.settings and hasattr(self, 'tab_editor'):
            self.tab_editor.apply_settings(self.settings.editor)

        # Rebuild theme menu if ui-themes.json changed
        if file_name == "ui-themes.json":
            self._populate_theme_menu()

        # Re-apply syntax highlighting if syntax-themes.json or languages.json changed
        if file_name in ["syntax-themes.json", "languages.json"]:
            current_file = self.tab_editor.current_file_path() if hasattr(self, 'tab_editor') else self.current_file
            if current_file:
                self._apply_lexer_for_file(current_file)

        # Re-apply keybindings if keybindings.json changed
        if file_name == "keybindings.json":
            self._load_keybindings()
            self._apply_keybindings()

        # Re-add the file to the watcher (it gets removed after modification)
        if not self.config_watcher.files() or path not in self.config_watcher.files():
            self.config_watcher.addPath(path)

        self._update_status(f"{file_name} reloaded")

    # File operations
    
    def _file_new(self):
        """Create a new file (new tab)."""
        self.tab_editor.new_file()
        self._update_status("New file")

    def _file_open(self):
        """Open a file in a new tab."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )

        if filename:
            self._load_file(filename)

    def _file_save(self):
        """Save the current file."""
        current_path = self.tab_editor.current_file_path()
        if current_path:
            if self.tab_editor.save_current_file():
                self._update_status(f"Saved {current_path.name}")
        else:
            self._file_save_as()

    def _file_save_as(self):
        """Save the current file with a new name."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )

        if filename:
            if self.tab_editor.save_file_as(Path(filename)):
                self._update_status(f"Saved {Path(filename).name}")

    def _file_close(self):
        """Close the current tab."""
        self.tab_editor.close_current_tab()
        self._update_status("File closed")

    def _file_close_others(self):
        """Close all tabs except the current one."""
        self.tab_editor.close_other_tabs()
        self._update_status("Closed other tabs")

    def _file_close_all(self):
        """Close all tabs."""
        self.tab_editor.close_all_tabs()
        self._update_status("Closed all tabs")

    def _load_file(self, filename: str):
        """
        Load a file into a new tab.

        Args:
            filename: Path to the file to load
        """
        file_path = Path(filename)
        if self.tab_editor.open_file(file_path):
            self._update_status(f"Loaded {file_path.name}")

            # Sync terminal to file's directory
            self._sync_terminal_directory(str(file_path.parent))

    def _apply_lexer_for_file(self, file_path: Path):
        """
        Apply the appropriate lexer and syntax theme for a file.
        NOTE: This is now handled by TabEditorWidget._setup_syntax_for_file

        Args:
            file_path: Path to the file
        """
        # Get current editor
        editor = self.tab_editor.current_editor()
        if not editor:
            return

        suffix = file_path.suffix.lower()

        # Get UI theme colors for background/foreground
        ui_theme = self.config_loader.load_ui_theme(self.settings.ui.theme) if self.settings else {}
        background = ui_theme.get("background", "#1e1e1e")
        foreground = ui_theme.get("foreground", "#d4d4d4")

        # Determine language from extension
        language = None
        if suffix in ['.py', '.pyw']:
            language = 'python'
        elif suffix in ['.js', '.mjs']:
            language = 'javascript'

        if language:
            # Load language config to get syntax theme name
            lang_config = self.config_loader.load_language_config(language)
            syntax_theme_name = lang_config.get('syntax_theme', 'default')

            # Load the syntax theme colors
            syntax_theme = self.config_loader.load_syntax_theme(syntax_theme_name)

            # Apply the appropriate lexer
            if language == 'python':
                editor.set_python_lexer(
                    syntax_theme=syntax_theme,
                    background=background,
                    foreground=foreground
                )

    def _update_status(self, message: str):
        """Update status bar message."""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, 3000)

    # Tab editor signal handlers

    def _on_current_file_changed(self, file_path):
        """Handle current file changed in tab editor."""
        self.current_file = file_path
        if file_path:
            self.setWindowTitle(f"Just Code - {file_path.name}")
        else:
            self.setWindowTitle("Just Code")

        # Update markdown preview action state
        is_markdown = self.tab_editor.is_current_file_markdown()
        self._toggle_preview_action.setEnabled(is_markdown)
        if is_markdown:
            if self.tab_editor.is_markdown_preview_visible():
                self._toggle_preview_action.setText("Hide &Markdown Preview")
            else:
                self._toggle_preview_action.setText("Show &Markdown Preview")
        else:
            self._toggle_preview_action.setText("Toggle &Markdown Preview")

    def _on_file_modified_changed(self, modified: bool):
        """Handle file modification state changed."""
        # Update window title with modification indicator
        title = self.windowTitle()
        if modified and not title.endswith(" •"):
            self.setWindowTitle(title + " •")
        elif not modified and title.endswith(" •"):
            self.setWindowTitle(title[:-2])

    def _on_file_saved(self, file_path: Path):
        """Handle file saved - trigger on_save plugins."""
        language = self._get_current_language()
        context = {
            'file_path': file_path,
            'language': language
        }
        self.plugin_manager.on_file_save(file_path, language, context)

    # Edit menu handlers (delegate to current editor)

    def _edit_undo(self):
        """Undo in current editor."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.undo()

    def _edit_redo(self):
        """Redo in current editor."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.redo()

    def _edit_cut(self):
        """Cut in current editor."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.cut()

    def _edit_copy(self):
        """Copy in current editor."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.copy()

    def _edit_paste(self):
        """Paste in current editor."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.paste()

    def _view_zoom_in(self):
        """Zoom in current editor."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.zoomIn()

    def _view_zoom_out(self):
        """Zoom out current editor."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.zoomOut()

    def _select_font(self):
        """Open font selection dialog."""
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        current_font = editor.font()
        font, ok = QFontDialog.getFont(current_font, self, "Select Editor Font")
        if ok:
            # Apply the selected font to all editors
            for i in range(self.tab_editor.count()):
                ed = self.tab_editor.widget(i)
                if ed:
                    ed.setFont(font)
                    # If a lexer is active, update it too
                    if ed.lexer():
                        lexer = ed.lexer()
                        lexer.setDefaultFont(font)
                        for style in range(128):
                            lexer.setFont(font, style)
            self._update_status(f"Font changed to {font.family()} {font.pointSize()}pt")

    def _file_open_folder(self):
        """Open a folder in the file browser."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Open Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if directory:
            self.file_browser.set_directory(directory)
            # Show the file browser if it's hidden
            if not self.file_browser_visible:
                self.file_browser_visible = True
                if self.settings and self.settings.ui.enable_panel_animations:
                    self._animate_panel_show(self.file_browser_dock, "left")
                else:
                    self.file_browser_dock.show()
            # Sync terminal working directory
            if hasattr(self, 'terminal'):
                self.terminal.set_working_directory(directory)
            self._update_status(f"Opened folder: {directory}")

    def _open_config_file(self, filename: str):
        """
        Open a config file in the editor.

        Args:
            filename: Name of the config file (e.g., 'settings.json')
        """
        # Config files are in resources/default_configs/
        config_path = Path(__file__).parent.parent / "resources" / "default_configs" / filename

        if config_path.exists():
            self._load_file(str(config_path))
        else:
            QMessageBox.warning(
                self,
                "Config File Not Found",
                f"Could not find config file at:\n{config_path}"
            )

    def _toggle_file_browser(self):
        """Toggle the file browser panel visibility."""
        if self.file_browser_visible:
            # Hide
            self.file_browser_visible = False
            if self.settings and self.settings.ui.enable_panel_animations:
                self._animate_panel_hide(self.file_browser_dock, "left")
            else:
                self.file_browser_dock.hide()
        else:
            # Show
            self.file_browser_visible = True
            if self.settings and self.settings.ui.enable_panel_animations:
                self._animate_panel_show(self.file_browser_dock, "left")
            else:
                self.file_browser_dock.show()

    def _toggle_terminal(self):
        """Toggle the terminal panel visibility."""
        if self.terminal_visible:
            # Hide
            self.terminal_visible = False
            if self.settings and self.settings.ui.enable_panel_animations:
                self._animate_panel_hide(self.terminal_dock, "bottom")
            else:
                self.terminal_dock.hide()
        else:
            # Show
            self.terminal_visible = True
            if self.settings and self.settings.ui.enable_panel_animations:
                self._animate_panel_show(self.terminal_dock, "bottom")
            else:
                self.terminal_dock.show()

    def _toggle_markdown_preview(self):
        """Toggle the markdown preview for the current file."""
        if self.tab_editor.is_current_file_markdown():
            is_visible = self.tab_editor.toggle_markdown_preview()
            # Update action text to reflect state
            if is_visible:
                self._toggle_preview_action.setText("Hide &Markdown Preview")
            else:
                self._toggle_preview_action.setText("Show &Markdown Preview")

    def _run_current_file(self):
        """Run the current file in the terminal."""
        # Get the current file path
        file_path = self.tab_editor.current_file_path()
        if not file_path:
            self._show_notification("Run", "No file to run. Save the file first.")
            return

        # Check if file exists (has been saved)
        if not file_path.exists():
            self._show_notification("Run", "File not saved. Save the file first.")
            return

        # Get the run command for this file type
        run_command = self._get_run_command(file_path)
        if not run_command:
            ext = file_path.suffix.lower()
            self._show_notification("Run", f"No run command configured for '{ext}' files.")
            return

        # Ensure terminal is visible
        if not self.terminal_visible:
            self._toggle_terminal()

        # Change to file's directory and run
        file_dir = str(file_path.parent)
        self.terminal.set_working_directory(file_dir)

        # Execute the run command
        self.terminal.execute_command(run_command)

    def _get_run_command(self, file_path: Path) -> str:
        """
        Get the appropriate run command for a file based on its extension.

        Args:
            file_path: Path to the file to run

        Returns:
            The command string to run the file, or empty string if not supported
        """
        ext = file_path.suffix.lower()
        filename = file_path.name

        # Map extensions to run commands
        run_commands = {
            # Python
            '.py': f'python3 "{filename}"',
            '.pyw': f'python3 "{filename}"',
            # JavaScript/Node
            '.js': f'node "{filename}"',
            '.mjs': f'node "{filename}"',
            # TypeScript (requires ts-node or similar)
            '.ts': f'npx ts-node "{filename}"',
            # Shell scripts
            '.sh': f'bash "{filename}"',
            '.bash': f'bash "{filename}"',
            '.zsh': f'zsh "{filename}"',
            # Ruby
            '.rb': f'ruby "{filename}"',
            # PHP
            '.php': f'php "{filename}"',
            # Perl
            '.pl': f'perl "{filename}"',
            '.pm': f'perl "{filename}"',
            # Lua
            '.lua': f'lua "{filename}"',
            # Go (run directly)
            '.go': f'go run "{filename}"',
            # Rust (compile and run)
            '.rs': f'rustc "{filename}" -o /tmp/rust_out && /tmp/rust_out',
            # C (compile and run)
            '.c': f'gcc "{filename}" -o /tmp/c_out && /tmp/c_out',
            # C++ (compile and run)
            '.cpp': f'g++ "{filename}" -o /tmp/cpp_out && /tmp/cpp_out',
            '.cc': f'g++ "{filename}" -o /tmp/cpp_out && /tmp/cpp_out',
            '.cxx': f'g++ "{filename}" -o /tmp/cpp_out && /tmp/cpp_out',
            # Java (compile and run)
            '.java': f'javac "{filename}" && java "{file_path.stem}"',
        }

        return run_commands.get(ext, '')

    def _show_notification(self, title: str, message: str):
        """Show a simple notification message box."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)

    def _animate_panel_show(self, dock_widget, position):
        """
        Animate panel sliding in with smooth geometry animation.

        Args:
            dock_widget: The QDockWidget to animate
            position: Panel position ("left" or "bottom")
        """
        # Make sure widget is visible for animation
        if not dock_widget.isVisible():
            dock_widget.show()

        # Get animation duration from settings
        duration = 250  # default
        if self.settings:
            duration = self.settings.ui.panel_animation_duration_ms

        # Get current geometry
        current_geometry = dock_widget.geometry()

        if position == "left":
            # Left panel: slide in from left
            start_geometry = QRect(-current_geometry.width(), current_geometry.y(),
                                 current_geometry.width(), current_geometry.height())
            end_geometry = current_geometry
        elif position == "bottom":
            # Bottom panel: slide up from bottom
            start_geometry = QRect(current_geometry.x(), self.height(),
                                 current_geometry.width(), current_geometry.height())
            end_geometry = current_geometry
        else:
            # Unknown position, just show without animation
            return

        # Create animation
        animation = QPropertyAnimation(dock_widget, b"geometry", self)
        animation.setDuration(duration)
        animation.setStartValue(start_geometry)
        animation.setEndValue(end_geometry)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Store animation reference and start
        if position == "left":
            self.file_browser_animation = animation
        else:
            self.terminal_animation = animation

        animation.start()

    def _animate_panel_hide(self, dock_widget, position):
        """
        Animate panel sliding out with smooth geometry animation.

        Args:
            dock_widget: The QDockWidget to animate
            position: Panel position ("left" or "bottom")
        """
        # Get animation duration from settings
        duration = 250  # default
        if self.settings:
            duration = self.settings.ui.panel_animation_duration_ms

        # Get current geometry
        current_geometry = dock_widget.geometry()
        start_geometry = current_geometry

        if position == "left":
            # Left panel: slide out to left
            end_geometry = QRect(-current_geometry.width(), current_geometry.y(),
                               current_geometry.width(), current_geometry.height())
        elif position == "bottom":
            # Bottom panel: slide down to bottom
            end_geometry = QRect(current_geometry.x(), self.height(),
                               current_geometry.width(), current_geometry.height())
        else:
            # Unknown position, just hide without animation
            dock_widget.hide()
            return

        # Create animation
        animation = QPropertyAnimation(dock_widget, b"geometry", self)
        animation.setDuration(duration)
        animation.setStartValue(start_geometry)
        animation.setEndValue(end_geometry)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Hide the widget after animation completes
        animation.finished.connect(dock_widget.hide)

        # Store animation reference and start
        if position == "left":
            self.file_browser_animation = animation
        else:
            self.terminal_animation = animation

        animation.start()

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Just Code",
            "<h3>Just Code</h3>"
            "<p>A minimalist code editor for developers who just want to write code.</p>"
            "<p>Version 0.1.0 </p>"
            "<p>Built with Python and PyQt6</p>"
            "<p>Author: Chuck Finch - Fragillidae Software</p>"
            "<p>License: MIT</p>"
        )
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Check for unsaved changes in all tabs
        if self.tab_editor.has_unsaved_changes():
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "There are unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                # Save all modified files
                self.tab_editor.save_all()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        # Save session before closing
        self._save_session()
        event.accept()

    def _restore_session(self):
        """Restore open files from last session."""
        if not self.settings or not self.settings.behavior.remember_open_files:
            return

        session = self.session_manager.load_session()
        if not session or not session.open_files:
            return

        # Open each file from the session
        for file_path_str in session.open_files:
            file_path = Path(file_path_str)
            if file_path.exists():
                self.tab_editor.open_file(file_path)

        # Restore active tab
        if session.active_tab_index < self.tab_editor.count():
            self.tab_editor.setCurrentIndex(session.active_tab_index)

    def _save_session(self):
        """Save current session (open files)."""
        if not self.settings or not self.settings.behavior.remember_open_files:
            return

        # Get all open file paths
        open_files = self.tab_editor.get_all_file_paths()
        active_index = self.tab_editor.currentIndex()

        self.session_manager.save_session(open_files, active_index)

    # -------------------------------------------------------------------------
    # Plugin System Callbacks
    # -------------------------------------------------------------------------

    def _plugin_notify(self, title: str, message: str):
        """Show a notification from a plugin."""
        QMessageBox.information(self, title, message)

    def _plugin_get_editor_text(self) -> str:
        """Get the current editor's text."""
        editor = self.tab_editor.current_editor()
        if editor:
            return editor.text()
        return ""

    def _plugin_set_editor_text(self, text: str):
        """Set the current editor's text."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.setText(text)

    def _plugin_get_selection(self) -> str:
        """Get the current selection."""
        editor = self.tab_editor.current_editor()
        if editor:
            return editor.selectedText()
        return ""

    def _plugin_replace_selection(self, text: str):
        """Replace the current selection with text."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.replaceSelectedText(text)

    def _plugin_insert_text(self, text: str):
        """Insert text at cursor position."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.insert(text)

    def _plugin_get_cursor_position(self) -> tuple:
        """Get cursor position (line, column)."""
        editor = self.tab_editor.current_editor()
        if editor:
            return editor.getCursorPosition()
        return (0, 0)

    def _plugin_set_cursor_position(self, line: int, col: int):
        """Set cursor position (line, column)."""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.setCursorPosition(line, col)

    def _plugin_get_file_path(self):
        """Get the current file path."""
        return self.tab_editor.current_file_path()
