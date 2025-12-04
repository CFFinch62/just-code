#!/usr/bin/env python3
# Just Code Editor - Entry Point

import sys
from .app import JustCodeApplication, MainWindow


def main():
    """Main entry point for Just Code."""
    # Create the application
    app = JustCodeApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow(app.config_loader)
    window.show()
    
    # Run the event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
