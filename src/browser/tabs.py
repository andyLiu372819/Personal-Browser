from PySide6.QtCore import Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QTabWidget


class BrowserView(QWebEngineView):
    """A web view that opens pop-up requests in a browser tab."""

    def __init__(self, tab_manager):
        super().__init__()
        self.tab_manager = tab_manager

    def createWindow(self, window_type):
        return self.tab_manager.add_tab()


class TabManager(QTabWidget):
    tab_created = Signal(object)
    last_tab_close_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def add_tab(self, url=None, label="New Tab"):
        web_view = BrowserView(self)
        index = self.addTab(web_view, label)

        web_view.titleChanged.connect(
            lambda title, view=web_view: self.update_tab_title(view, title)
        )

        self.setCurrentIndex(index)
        self.tab_created.emit(web_view)

        if url is not None:
            web_view.load(url)

        return web_view

    def close_tab(self, index):
        if self.count() == 1:
            self.last_tab_close_requested.emit()
            return

        web_view = self.widget(index)
        self.removeTab(index)
        web_view.deleteLater()

    def close_current_tab(self):
        self.close_tab(self.currentIndex())

    def current_web_view(self):
        return self.currentWidget()

    def update_tab_title(self, web_view, title):
        index = self.indexOf(web_view)
        if index == -1:
            return

        tab_title = title.strip() or "New Tab"
        self.setTabText(index, tab_title[:30])
