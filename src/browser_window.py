from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLineEdit, QMainWindow, QToolBar

from search import build_url_from_input
from settings import load_settings


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        
        self.setWindowTitle("Personal Browser")
        self.resize(1200, 800)

        self.web_view = QWebEngineView()
        self.web_view.urlChanged.connect(self.update_address_bar)
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

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Type your search or url here")
        self.address_bar.returnPressed.connect(self.load_address_bar_url)
        navigation_bar.addWidget(self.address_bar)

    def go_home(self):
        homepage = self.settings["homepage"]
        self.web_view.load(QUrl(homepage))

    def load_address_bar_url(self):
        user_input = self.address_bar.text()
        search_engine = self.settings["default_search_engine"]
        url = build_url_from_input(user_input, search_engine)
        self.web_view.load(QUrl(url))

    def update_address_bar(self, url: QUrl):
        self.address_bar.setText(url.toString())

