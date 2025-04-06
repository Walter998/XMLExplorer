import sys
from PyQt5.QtWidgets import QApplication
from controller.xml_controller import XMLController
from view.qt_view import XMLExplorerView
from DefineConst import *

def main():
    """
    Main entry point for the XML Explorer application.
    
    Creates the application, controller, and view, and starts the event loop.
    """
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # Create controller and viewd
    controller = XMLController()
    view = XMLExplorerView(controller)
    
    # Restore application state
    view.restore_state()
    
    # Show window
    view.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()