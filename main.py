"""
REPO Finance Manager - Main Application Entry Point

This is the main entry point for the REPO Finance Manager application.
Run this file to start the GUI application.
"""

import sys

try:
    from nicegui import ui
    from repo_finance_gui import create_ui
except ImportError as e:
    print(f"Error importing module: {e}")
    print("Make sure nicegui is installed: pip install nicegui")
    sys.exit(1)


def main():
    """
    Main function to launch the REPO Finance Manager application.

    Initializes the NiceGUI interface and starts the local web server.
    The application opens automatically in the default browser at
    http://localhost:8080
    """
    try:
        create_ui()
        ui.run(title="REPO Finance Manager", dark=True, port=8080, reload=False)
    except Exception as e:
        print(f"Error starting REPO Finance Manager: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🤖 Starting REPO Finance Manager...")
    print("Opening in browser at http://localhost:8080")
    print("-" * 50)
    main()
