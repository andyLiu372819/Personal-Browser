from PySide6.QtCore import Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QTabWidget

from .internal_pages import (
    extract_internal_search_request,
    extract_internal_settings_request,
    is_internal_home_request,
)


class BrowserPage(QWebEnginePage):
    """A web page that handles browser-owned internal navigation."""

    internal_home_requested = Signal()
    internal_search_requested = Signal(str, int)
    internal_settings_requested = Signal()
    internal_settings_save_requested = Signal(dict)

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        if is_main_frame and is_internal_home_request(url):
            self.internal_home_requested.emit()
            return False

        request = extract_internal_search_request(url)

        if is_main_frame and request is not None:
            if request.query:
                self.internal_search_requested.emit(
                    request.query,
                    request.result_limit,
                )
            return False

        settings_request = extract_internal_settings_request(url)

        if is_main_frame and settings_request is not None:
            if settings_request.should_save:
                self.internal_settings_save_requested.emit(settings_request.values)
            else:
                self.internal_settings_requested.emit()
            return False

        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)


class BrowserView(QWebEngineView):
    """A web view that opens pop-up requests in a browser tab."""

    internal_home_requested = Signal()
    internal_search_requested = Signal(str, int)
    internal_settings_requested = Signal()
    internal_settings_save_requested = Signal(dict)

    def __init__(self, tab_manager):
        super().__init__()
        self.tab_manager = tab_manager
        self.browser_page = BrowserPage(self)
        self.browser_page.internal_home_requested.connect(
            self.internal_home_requested.emit
        )
        self.browser_page.internal_search_requested.connect(
            self.internal_search_requested.emit
        )
        self.browser_page.internal_settings_requested.connect(
            self.internal_settings_requested.emit
        )
        self.browser_page.internal_settings_save_requested.connect(
            self.internal_settings_save_requested.emit
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
