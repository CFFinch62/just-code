# Just Code Editor - Application Class
# QApplication subclass, manages app lifecycle

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

from ..config import ConfigLoader, ThemeManager


class JustCodeApplication(QApplication):
    """Custom QApplication for Just Code."""
    
    def __init__(self, argv):
        """
        Initialize the application.
        
        Args:
            argv: Command line arguments
        """
        super().__init__(argv)
        
        self.setApplicationName("Just Code")
        self.setOrganizationName("JustCode")
        
        # Load configuration
        self.config_loader = ConfigLoader()
        
        # Apply application-wide theme
        self._apply_global_theme()
        
    def _apply_global_theme(self):
        """Apply the global application theme."""
        settings = self.config_loader.load_settings()
        theme_data = self.config_loader.load_ui_theme(settings.ui.theme)
        
        theme_manager = ThemeManager(theme_data)
        theme_manager.apply_to_app(self)
