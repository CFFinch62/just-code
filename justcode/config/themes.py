# Just Code Editor - Themes
# Theme management and application

from typing import Dict
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """Manages UI themes and applies them to the application."""
    
    def __init__(self, theme_data: Dict[str, str]):
        """
        Initialize theme manager with theme data.
        
        Args:
            theme_data: Dictionary of color names to hex values
        """
        self.theme_data = theme_data
        
    def apply_to_app(self, app: QApplication):
        """
        Apply the theme to the QApplication.

        Args:
            app: The QApplication instance
        """
        # If using system theme, don't apply custom palette
        if self.theme_data.get('use_system_theme', False):
            return

        # Create a dark palette
        palette = QPalette()

        # Map theme colors to palette roles
        if 'background' in self.theme_data:
            bg_color = QColor(self.theme_data['background'])
            palette.setColor(QPalette.ColorRole.Window, bg_color)
            palette.setColor(QPalette.ColorRole.Base, bg_color)

        if 'foreground' in self.theme_data:
            fg_color = QColor(self.theme_data['foreground'])
            palette.setColor(QPalette.ColorRole.WindowText, fg_color)
            palette.setColor(QPalette.ColorRole.Text, fg_color)

        if 'selection' in self.theme_data:
            selection_color = QColor(self.theme_data['selection'])
            palette.setColor(QPalette.ColorRole.Highlight, selection_color)

        if 'panel_background' in self.theme_data:
            panel_bg = QColor(self.theme_data['panel_background'])
            palette.setColor(QPalette.ColorRole.AlternateBase, panel_bg)

        app.setPalette(palette)
    
    def get_stylesheet(self) -> str:
        """
        Get Qt stylesheet for additional styling.

        Returns:
            CSS-like stylesheet string
        """
        # If using system theme, return minimal stylesheet
        if self.theme_data.get('use_system_theme', False):
            return ""

        bg = self.theme_data.get('background', '#1e1e1e')
        fg = self.theme_data.get('foreground', '#d4d4d4')
        panel_bg = self.theme_data.get('panel_background', '#252526')
        panel_border = self.theme_data.get('panel_border', '#3c3c3c')

        return f"""
            QMainWindow {{
                background-color: {bg};
                color: {fg};
            }}
            QMenuBar {{
                background-color: {panel_bg};
                color: {fg};
                border-bottom: 1px solid {panel_border};
            }}
            QMenuBar::item:selected {{
                background-color: {panel_border};
            }}
            QMenu {{
                background-color: {panel_bg};
                color: {fg};
                border: 1px solid {panel_border};
            }}
            QMenu::item:selected {{
                background-color: {panel_border};
            }}
            QStatusBar {{
                background-color: {panel_bg};
                color: {fg};
                border-top: 1px solid {panel_border};
            }}
        """
