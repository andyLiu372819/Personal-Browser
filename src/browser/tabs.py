from PySide6.QtCore import Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QTabWidget

from .internal_pages import extract_internal_search_query


class BrowserPage(QWebEnginePage):
    """A web page that handles browser-owned internal navigation."""

    internal_search_requested = Signal(str)

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        query = extract_internal_search_query(url)

        if is_main_frame and query is not None:
            if query:
                self.internal_search_requested.emit(query)
            return False

        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)


class BrowserView(QWebEngineView):
    """A web view that opens pop-up requests in a browser tab."""

    internal_search_requested = Signal(str)

    def __init__(self, tab_manager):
        super().__init__()
        self.tab_manager = tab_manager
        self.browser_page = BrowserPage(self)
        self.browser_page.internal_search_requested.connect(
            self.internal_search_requested.emit
        )
        self.setPage(self.browser_page)

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
