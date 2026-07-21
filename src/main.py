import sys
from PySide6.QtWidgets import QApplication
from browser import BrowserWindow
from theme import APP_NAME


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Nexus")

    window = BrowserWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
