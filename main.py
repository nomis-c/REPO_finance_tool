"""
REPO Finance Manager - Main Application Entry Point

This is the main entry point for the REPO Finance Manager application.
Run this file to start the GUI application.
"""

import tkinter as tk
import sys

try:
    from repo_finance_gui import RepoFinanceGUI
except ImportError as e:
    print(f"Error importing GUI module: {e}")
    print("Make sure 'repo_finance_gui.py' is in the same directory as this file.")
    sys.exit(1)


def main():
    """
    Main function to launch the REPO Finance Manager application.

    Creates the main tkinter window, initializes the GUI, and starts the
    application event loop. Handles basic error cases and provides user
    feedback if something goes wrong.
    """
    try:
        # Create the main tkinter window
        root = tk.Tk()

        # Initialize the GUI application
        app = RepoFinanceGUI(root)

        # Start the main event loop<
        root.mainloop()

    except Exception as e:
        print(f"Error starting REPO Finance Manager: {e}")
        print("Please make sure all required files are present and Python/tkinter are properly installed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
