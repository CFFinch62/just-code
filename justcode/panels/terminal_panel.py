# Just Code Editor - Terminal Panel
# Real bash terminal panel with persistent shell

import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QMenu
)
from PyQt6.QtCore import Qt, QProcess, QTimer, QProcessEnvironment, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat, QAction


class TerminalPanel(QWidget):
    """Terminal panel with real bash shell."""

    # Signal emitted when terminal process finishes
    process_finished = pyqtSignal(int, str)

    # Regex to strip ANSI escape codes
    ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def __init__(self, parent=None):
        """Initialize the terminal panel."""
        super().__init__(parent)

        self.process = QProcess(self)
        self.working_directory = os.path.expanduser("~")
        self.is_running = False
        self.history = []
        self.history_index = -1
        # Initialize theme colors before _setup_ui (which calls _get_button_style)
        self._theme_colors = {
            'background': '#1e1e1e',
            'foreground': '#d4d4d4',
            'panel_background': '#252526',
            'panel_border': '#3c3c3c',
            'line_highlight': '#2a2a2a'
        }
        self._setup_ui()
        self._setup_process()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with controls
        self.header_widget = QWidget()
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(4, 4, 4, 4)
        header_layout.setSpacing(4)

        # Terminal label
        self.terminal_label = QLabel("Terminal")
        self.terminal_label.setStyleSheet("color: #cccccc; padding: 2px; font-weight: bold;")
        header_layout.addWidget(self.terminal_label)

        header_layout.addStretch(1)

        # Restart button
        self.restart_button = QPushButton("Restart")
        self.restart_button.setStyleSheet(self._get_button_style())
        self.restart_button.clicked.connect(self._restart_shell)
        header_layout.addWidget(self.restart_button)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet(self._get_button_style())
        self.clear_button.clicked.connect(self._clear_output)
        header_layout.addWidget(self.clear_button)

        self.header_widget.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border-bottom: 1px solid #3c3c3c;
            }
        """)
        layout.addWidget(self.header_widget)

        # Output area (using QTextEdit for better formatting)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.output_text.customContextMenuRequested.connect(self._show_context_menu)

        # Set monospace font (platform-appropriate)
        from ..utils import get_monospace_font
        self.font = get_monospace_font(10)
        self.output_text.setFont(self.font)

        # Dark theme
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
        """)
        layout.addWidget(self.output_text)

        # Input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(4, 4, 4, 4)
        input_layout.setSpacing(4)

        # Prompt
        self.prompt_label = QLabel("$")
        self.prompt_label.setStyleSheet("color: #4ec9b0; font-weight: bold; padding: 2px;")
        input_layout.addWidget(self.prompt_label)

        # Command input
        self.command_input = QLineEdit()
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 4px;
            }
        """)
        self.command_input.setFont(self.font)
        self.command_input.returnPressed.connect(self._send_command)
        self.command_input.installEventFilter(self)
        input_layout.addWidget(self.command_input)

        input_widget.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border-top: 1px solid #3c3c3c;
            }
        """)
        layout.addWidget(input_widget)

        # Set default size
        self.setMinimumHeight(200)

    def apply_ui_theme(self, theme_data: dict):
        """
        Apply UI theme colors to the terminal.

        Args:
            theme_data: Dictionary of theme color names to hex values
        """
        if theme_data.get('use_system_theme', False):
            return

        bg = theme_data.get('background', '#1e1e1e')
        fg = theme_data.get('foreground', '#d4d4d4')
        panel_bg = theme_data.get('panel_background', '#252526')
        panel_border = theme_data.get('panel_border', '#3c3c3c')
        line_highlight = theme_data.get('line_highlight', '#2a2a2a')

        # Store for button styling
        self._theme_colors = {
            'background': bg,
            'foreground': fg,
            'panel_background': panel_bg,
            'panel_border': panel_border,
            'line_highlight': line_highlight
        }

        # Output text styling
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                border: none;
            }}
        """)

        # Command input styling
        self.command_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg};
                color: {fg};
                border: none;
                padding: 4px;
            }}
        """)

        # Header styling
        self.header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {panel_bg};
                border-bottom: 1px solid {panel_border};
            }}
        """)

        # Input widget styling
        self.command_input.parentWidget().setStyleSheet(f"""
            QWidget {{
                background-color: {panel_bg};
                border-top: 1px solid {panel_border};
            }}
        """)

        # Terminal label styling
        self.terminal_label.setStyleSheet(f"color: {fg}; padding: 2px; font-weight: bold;")

        self.prompt_label.setStyleSheet(f"color: #4ec9b0; font-weight: bold; padding: 2px;")

        # Update button styles
        button_style = self._get_button_style()
        self.restart_button.setStyleSheet(button_style)
        self.clear_button.setStyleSheet(button_style)

    def _get_button_style(self) -> str:
        """Get the stylesheet for header buttons."""
        bg = self._theme_colors.get('panel_border', '#3c3c3c')
        fg = self._theme_colors.get('foreground', '#cccccc')
        hover = self._theme_colors.get('line_highlight', '#505050')

        return f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """

    def _setup_process(self):
        """Set up the shell process."""
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)

        # Start the shell
        self._start_shell()

    def _start_shell(self):
        """Start the bash shell process."""
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()
            self.process.waitForFinished(1000)

        # Use bash shell
        shell_path = "/bin/bash"
        if not os.path.exists(shell_path):
            shell_path = "/usr/bin/bash"
            if not os.path.exists(shell_path):
                self._append_output("Bash shell not found", color="#ff6b6b")
                return

        # Set up environment
        env = QProcessEnvironment.systemEnvironment()
        env.insert("TERM", "dumb")  # Disable fancy terminal features
        self.process.setProcessEnvironment(env)

        # Set working directory
        if self.working_directory:
            self.process.setWorkingDirectory(self.working_directory)
            self._update_terminal_label(self.working_directory)

        # Start the shell
        self.process.start(shell_path, [])
        self.is_running = True

        # Show welcome message
        self._append_output(f"Working directory: {self.working_directory}\n", color="#6a9955")

    def _restart_shell(self):
        """Restart the shell process."""
        self._clear_output()
        self._start_shell()

    def _update_terminal_label(self, path):
        """Update the terminal label with current directory."""
        # Shorten path if it's in home directory
        home = os.path.expanduser("~")
        display_path = path
        if path.startswith(home):
            display_path = "~" + path[len(home):]
        
        self.terminal_label.setText(f"Terminal - {display_path}")

    def _send_command(self):
        """Send command to the running shell."""
        command = self.command_input.text()
        if not command:
            return

        # Add to history
        if command.strip() and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = len(self.history)

        self.command_input.clear()

        if self.process.state() == QProcess.ProcessState.Running:
            # Send command to shell with directory tracking
            # We append a hidden echo command that prints the new directory with a marker
            full_command = f'{command}; echo -e "\\n___JC_PWD:$PWD"'
            self.process.write((full_command + "\n").encode())
        else:
            self._append_output("Shell not running. Click 'Restart' to start.", color="#ff6b6b")

    def _handle_stdout(self):
        """Handle standard output from process."""
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        
        # Check for directory marker
        if "___JC_PWD:" in data:
            lines = data.split('\n')
            clean_lines = []
            for line in lines:
                if "___JC_PWD:" in line:
                    try:
                        # Extract directory
                        pwd_part = line.split("___JC_PWD:")[1].strip()
                        self.working_directory = pwd_part
                        self._update_terminal_label(self.working_directory)
                        # Show confirmation in terminal body to match file browser behavior
                        self._append_output(f"Changed directory to: {self.working_directory}", color="#6a9955")
                    except IndexError:
                        pass
                else:
                    clean_lines.append(line)
            data = '\n'.join(clean_lines)

        # Strip ANSI escape codes
        clean_data = self.ANSI_ESCAPE.sub('', data)
        self._append_output_raw(clean_data)

    def _handle_stderr(self):
        """Handle standard error from process."""
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        # Strip ANSI escape codes
        clean_data = self.ANSI_ESCAPE.sub('', data)
        self._append_output_raw(clean_data, color="#ff6b6b")

    def _handle_finished(self, exit_code, exit_status):
        """Handle process completion."""
        self.is_running = False
        self._append_output(f"\n[Shell exited with code {exit_code}]", color="#ff6b6b")
        self.command_input.setFocus()

    def _append_output(self, text, color="#d4d4d4"):
        """Append text to output area with optional color and newline."""
        self._append_output_raw(text + "\n", color)

    def _append_output_raw(self, text, color="#d4d4d4"):
        """Append text to output area with optional color (no automatic newline)."""
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Set color
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)

        # Insert text
        cursor.insertText(text)

        # Scroll to end
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()

    def _clear_output(self):
        """Clear the output text area and show current working directory."""
        self.output_text.clear()
        self._append_output(f"Working directory: {self.working_directory}", color="#6a9955")

    def _show_context_menu(self, position):
        """Show context menu for output area."""
        menu = QMenu(self)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.output_text.copy)
        menu.addAction(copy_action)

        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self._clear_output)
        menu.addAction(clear_action)

        menu.exec(self.output_text.mapToGlobal(position))

    def eventFilter(self, obj, event):
        """Handle key events for command history."""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent

        if obj == self.command_input and event.type() == QEvent.Type.KeyPress:
            key = event.key()

            # Up arrow - previous command
            if key == Qt.Key.Key_Up:
                if self.history and self.history_index > 0:
                    self.history_index -= 1
                    self.command_input.setText(self.history[self.history_index])
                return True

            # Down arrow - next command
            elif key == Qt.Key.Key_Down:
                if self.history and self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.command_input.setText(self.history[self.history_index])
                elif self.history_index >= len(self.history) - 1:
                    self.history_index = len(self.history)
                    self.command_input.clear()
                return True

            # Ctrl+L - clear screen
            elif key == Qt.Key.Key_L and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self._clear_output()
                return True

            # Ctrl+C - send interrupt
            elif key == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if self.process.state() == QProcess.ProcessState.Running:
                    # Send Ctrl+C (SIGINT) to the process
                    self.process.write(b'\x03')
                return True

        return super().eventFilter(obj, event)

    def set_working_directory(self, directory: str):
        """
        Set the working directory for the shell.

        Args:
            directory: Path to the directory
        """
        self.working_directory = directory
        if self.process.state() == QProcess.ProcessState.Running:
            # Change directory in the running shell
            self.process.write(f'cd "{directory}"\n'.encode())
            self._append_output(f"Changed directory to: {directory}", color="#6a9955")
        
        # Always update the label
        self._update_terminal_label(directory)

    def execute_command(self, command: str, show_command: bool = True):
        """
        Execute a command in the terminal programmatically.

        Args:
            command: The command to execute
            show_command: Whether to echo the command in the output
        """
        if not command:
            return

        if self.process.state() == QProcess.ProcessState.Running:
            if show_command:
                self._append_output(f"$ {command}", color="#569cd6")
            self.process.write((command + "\n").encode())
        else:
            self._append_output("Shell not running. Click 'Restart' to start.", color="#ff6b6b")

    def cleanup(self):
        """Clean up terminal resources."""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()
            self.process.waitForFinished(1000)
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.kill()
