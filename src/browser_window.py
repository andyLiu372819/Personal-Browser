from PySide6.QtWidgets import QMainWindow, QToolBar
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction

from settings import load_settings


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        
        self.setWindowTitle("Personal Browser")
        self.resize(1200, 800)

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        self.create_navigation_bar()

        homepage = self.settings["homepage"]
        self.web_view.load(QUrl(homepage))

    def create_navigation_bar(self):
        navigation_bar = QToolBar("Navigation")
        self.addToolBar(navigation_bar)

        back_action = QAction("Back", self)
        back_action.triggered.connect(self.web_view.back)
        navigation_bar.addAction(back_action)

        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(self.web_view.forward)
        navigation_bar.addAction(forward_action)

        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(self.web_view.reload)
        navigation_bar.addAction(reload_action)

        home_action = QAction("Home", self)
        home_action.triggered.connect(self.go_home)
        navigation_bar.addAction(home_action)

    def go_home(self):
        homepage = self.settings["homepage"]
        self.web_view.load(QUrl(homepage))
