from pathlib import Path

from PySide6.QtCore import QByteArray, QSize, Qt, QUrl
from PySide6.QtGui import QAction, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QLineEdit,
    QMainWindow,
    QMenu,
    QSizePolicy,
    QToolBar,
    QToolButton,
)

from bookmarks import add_bookmark, is_bookmarked, load_bookmarks, remove_bookmark
from history import add_history_entry, load_history
from search_engine import (
    DEFAULT_CRAWLER_MAX_DEPTH,
    DEFAULT_CRAWLER_MAX_PAGES,
    DEFAULT_SEARCH_RESULT_LIMIT,
    crawl_and_store,
    normalize_crawler_depth,
    normalize_crawler_page_limit,
    normalize_result_limit,
    render_results_page,
)
from settings import load_settings, save_settings
from theme import APP_NAME, qt_stylesheet, theme_palette

from .address_bar import resolve_address_bar_input
from .home_page import render_home_page
from .history_page import render_history_page
from .internal_pages import (
    INTERNAL_HOME_URL,
    INTERNAL_SETTINGS_URL,
    is_internal_page_url,
    write_internal_page,
)
from .settings_page import render_settings_page
from .tabs import TabManager
from paths import resource_path


ICONS_DIR = resource_path("assets", "icons")


def load_icon(name, color=None):
    icon_path = ICONS_DIR / f"{name}.svg"
    if color:
        svg = icon_path.read_text(encoding="utf-8")
        svg = svg.replace("#283125", color)
        renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    else:
        renderer = QSvgRenderer(str(icon_path))

    if not renderer.isValid():
        raise RuntimeError(f"Could not load icon: {icon_path}")

    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


def create_icon_action(icon_name, tooltip, parent, color=None):
    action = QAction(load_icon(icon_name, color), "", parent)
    action.setObjectName(f"{icon_name}_action")
    action.setToolTip(tooltip)
    action.setStatusTip(tooltip)
    return action


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.icon_actions = {}
        self.icon_widgets = {}

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(load_icon("app"))
        self.resize(1200, 800)

        self.tab_manager = TabManager()
        self.setCentralWidget(self.tab_manager)
        self.internal_address_text_by_view = {}

        self.create_navigation_bar()
        self.apply_browser_theme()

        self.tab_manager.tab_created.connect(self.connect_tab)
        self.tab_manager.currentChanged.connect(self.on_current_tab_changed)
        self.tab_manager.last_tab_close_requested.connect(self.close)

        self.add_new_tab(focus_address=False)

    def create_navigation_bar(self):
        self.navigation_bar = QToolBar("Navigation")
        self.navigation_bar.setIconSize(QSize(24, 24))
        self.navigation_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.addToolBar(self.navigation_bar)

        self.back_action = self.create_themed_icon_action("back", "Back")
        self.back_action.triggered.connect(self.go_back)
        self.navigation_bar.addAction(self.back_action)

        self.forward_action = self.create_themed_icon_action("forward", "Forward")
        self.forward_action.triggered.connect(self.go_forward)
        self.navigation_bar.addAction(self.forward_action)

        reload_action = self.create_themed_icon_action("reload", "Reload")
        reload_action.setShortcut("Ctrl+R")
        reload_action.triggered.connect(self.reload_page)
        self.navigation_bar.addAction(reload_action)

        home_action = self.create_themed_icon_action("home", "Home")
        home_action.triggered.connect(self.go_home)
        self.navigation_bar.addAction(home_action)

        new_tab_action = self.create_themed_icon_action("new_tab", "New Tab")
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        self.navigation_bar.addAction(new_tab_action)

        close_tab_action = self.create_themed_icon_action("close_tab", "Close Tab")
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(self.tab_manager.close_current_tab)
        self.navigation_bar.addAction(close_tab_action)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Type a search or URL")
        self.address_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.address_bar.returnPressed.connect(self.load_address_bar_url)
        self.navigation_bar.addWidget(self.address_bar)

        focus_address_action = self.create_themed_icon_action(
            "focus_address", "Focus Address Bar"
        )
        focus_address_action.setShortcut("Ctrl+L")
        focus_address_action.triggered.connect(self.focus_address_bar)
        self.address_bar.addAction(focus_address_action, QLineEdit.LeadingPosition)

        self.bookmark_action = self.create_themed_icon_action(
            "bookmark", "Add Bookmark"
        )
        self.bookmark_action.setShortcut("Ctrl+D")
        self.bookmark_action.setEnabled(False)
        self.bookmark_action.triggered.connect(self.toggle_current_bookmark)
        self.address_bar.addAction(self.bookmark_action, QLineEdit.TrailingPosition)

        self.bookmarks_menu = QMenu(self)
        self.bookmarks_menu.aboutToShow.connect(self.rebuild_bookmarks_menu)

        self.bookmarks_button = QToolButton(self)
        self.bookmarks_button.setIcon(self.themed_icon("bookmarks"))
        self.bookmarks_button.setToolTip("Bookmarks")
        self.bookmarks_button.setPopupMode(QToolButton.InstantPopup)
        self.bookmarks_button.setMenu(self.bookmarks_menu)
        self.icon_widgets["bookmarks"] = self.bookmarks_button
        self.navigation_bar.addWidget(self.bookmarks_button)

        history_action = self.create_themed_icon_action("history", "History")
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(self.open_history_page)
        self.navigation_bar.addAction(history_action)

        crawl_action = self.create_themed_icon_action("crawl", "Crawl Current Site")
        crawl_action.triggered.connect(self.crawl_current_site)
        self.navigation_bar.addAction(crawl_action)

        settings_action = self.create_themed_icon_action("settings", "Settings")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings_page)
        self.navigation_bar.addAction(settings_action)

    def themed_icon(self, icon_name):
        palette = theme_palette(self.settings)
        return load_icon(icon_name, palette["icon"])

    def create_themed_icon_action(self, icon_name, tooltip):
        action = create_icon_action(
            icon_name,
            tooltip,
            self,
            theme_palette(self.settings)["icon"],
        )
        self.icon_actions[icon_name] = action
        return action

    def apply_browser_theme(self):
        self.setStyleSheet(qt_stylesheet(self.settings))

        for icon_name, action in getattr(self, "icon_actions", {}).items():
            action.setIcon(self.themed_icon(icon_name))

        for icon_name, widget in getattr(self, "icon_widgets", {}).items():
            widget.setIcon(self.themed_icon(icon_name))

        self.update_bookmark_action()

    def connect_tab(self, web_view):
        web_view.internal_home_requested.connect(
            lambda view=web_view: self.load_home_page(view)
        )
        web_view.internal_search_requested.connect(
            lambda query, result_limit, view=web_view: self.load_search_query(
                view,
                query,
                result_limit,
            )
        )
        web_view.internal_settings_requested.connect(
            lambda view=web_view: self.open_settings_page(view)
        )
        web_view.internal_settings_save_requested.connect(
            lambda values, view=web_view: self.save_settings_from_request(view, values)
        )
        web_view.urlChanged.connect(
            lambda url, view=web_view: self.on_url_changed(view, url)
        )
        web_view.loadFinished.connect(
            lambda success, view=web_view: self.record_history(view, success)
        )
        web_view.titleChanged.connect(
            lambda title, view=web_view: self.update_window_title(view, title)
        )

    def add_new_tab(self, url=None, focus_address=True):
        web_view = self.tab_manager.add_tab()

        if url is None:
            self.load_home_page(web_view)
        else:
            web_view.load(url)

        if focus_address:
            self.focus_address_bar()

        return web_view

    def current_web_view(self):
        return self.tab_manager.current_web_view()

    def go_back(self):
        web_view = self.current_web_view()
        if web_view:
            web_view.back()

    def go_forward(self):
        web_view = self.current_web_view()
        if web_view:
            web_view.forward()

    def reload_page(self):
        web_view = self.current_web_view()
        if web_view:
            web_view.reload()

    def go_home(self):
        web_view = self.current_web_view()
        if web_view:
            self.load_home_page(web_view)

    def load_address_bar_url(self):
        user_input = self.address_bar.text().strip()
        if not user_input:
            return

        web_view = self.current_web_view()
        if web_view is None:
            return

        action = resolve_address_bar_input(
            user_input,
            self.settings["default_search_engine"],
            self.settings["fallback_search_engine"],
            self.search_result_limit(),
            render_function=getattr(
                self,
                "render_search_results_page",
                render_results_page,
            ),
        )

        self.load_address_bar_action(web_view, action, address_text=user_input)

    def load_search_query(self, web_view, query, result_limit=None):
        result_limit = self.search_result_limit(result_limit)
        self.address_bar.setText(query)
        action = resolve_address_bar_input(
            query,
            self.settings["default_search_engine"],
            self.settings["fallback_search_engine"],
            result_limit,
            render_function=getattr(
                self,
                "render_search_results_page",
                render_results_page,
            ),
        )

        self.load_address_bar_action(web_view, action, address_text=query)

    def load_address_bar_action(self, web_view, action, address_text=""):
        if action.kind == "url":
            web_view.load(QUrl(action.content))
        elif action.kind == "html":
            self.load_internal_html_page(
                web_view,
                "search-results",
                action.content,
                address_text=address_text,
            )

    def load_home_page(self, web_view):
        homepage = self.settings.get("homepage", INTERNAL_HOME_URL)

        if homepage == INTERNAL_HOME_URL:
            self.load_internal_html_page(
                web_view,
                "home",
                render_home_page(
                    result_limit=self.search_result_limit(),
                    settings=self.settings,
                ),
            )
            return

        web_view.load(QUrl(homepage))

    def load_internal_html_page(self, web_view, page_name, html, address_text=""):
        page_path = write_internal_page(page_name, html)
        page_url = QUrl.fromLocalFile(str(page_path))
        self.internal_address_text_by_view[web_view] = address_text
        web_view.load(page_url)

    def focus_address_bar(self):
        self.address_bar.setFocus()
        self.address_bar.selectAll()

    def on_current_tab_changed(self, index):
        web_view = self.tab_manager.widget(index)
        if web_view is None:
            return

        self.address_bar.setText(web_view.url().toString())
        self.update_window_title(web_view, web_view.title())
        self.update_navigation_actions()
        self.update_bookmark_action()

    def on_url_changed(self, web_view, url):
        if web_view is not self.current_web_view():
            return

        url_text = url.toString()
        if is_internal_page_url(url_text):
            self.address_bar.setText(self.internal_address_text_by_view.get(web_view, ""))
        else:
            self.internal_address_text_by_view.pop(web_view, None)
            self.address_bar.setText(url_text)
        self.address_bar.setCursorPosition(0)
        self.update_navigation_actions()
        self.update_bookmark_action()

    def update_window_title(self, web_view, title):
        if web_view is self.current_web_view():
            page_title = title.strip() or "New Tab"
            self.setWindowTitle(f"{page_title} - {APP_NAME}")

    def update_navigation_actions(self):
        web_view = self.current_web_view()
        if web_view is None:
            self.back_action.setEnabled(False)
            self.forward_action.setEnabled(False)
            return

        history = web_view.history()
        self.back_action.setEnabled(history.canGoBack())
        self.forward_action.setEnabled(history.canGoForward())

    def update_bookmark_action(self):
        web_view = self.current_web_view()
        url = web_view.url().toString() if web_view else ""
        can_bookmark = bool(
            url and url != "about:blank" and not is_internal_page_url(url)
        )

        self.bookmark_action.setEnabled(can_bookmark)

        if can_bookmark and is_bookmarked(url):
            self.bookmark_action.setIcon(self.themed_icon("bookmark_filled"))
            self.bookmark_action.setToolTip("Remove Bookmark")
            self.bookmark_action.setStatusTip("Remove Bookmark")
        else:
            self.bookmark_action.setIcon(self.themed_icon("bookmark"))
            self.bookmark_action.setToolTip("Add Bookmark")
            self.bookmark_action.setStatusTip("Add Bookmark")

    def toggle_current_bookmark(self):
        web_view = self.current_web_view()
        if web_view is None:
            return

        url = web_view.url().toString()
        if not url or url == "about:blank":
            return

        if is_bookmarked(url):
            remove_bookmark(url)
        else:
            add_bookmark(web_view.title(), url)

        self.update_bookmark_action()

    def rebuild_bookmarks_menu(self):
        self.bookmarks_menu.clear()
        bookmarks = load_bookmarks()

        if not bookmarks:
            empty_action = self.bookmarks_menu.addAction("No bookmarks saved")
            empty_action.setEnabled(False)
            return

        for bookmark in bookmarks:
            open_action = self.bookmarks_menu.addAction(bookmark["title"])
            open_action.setToolTip(bookmark["url"])
            open_action.triggered.connect(
                lambda checked=False, url=bookmark["url"]: self.open_bookmark(url)
            )

        self.bookmarks_menu.addSeparator()
        self.remove_bookmarks_menu = self.bookmarks_menu.addMenu("Remove bookmark")

        for bookmark in bookmarks:
            remove_action = self.remove_bookmarks_menu.addAction(bookmark["title"])
            remove_action.setToolTip(bookmark["url"])
            remove_action.triggered.connect(
                lambda checked=False, url=bookmark["url"]: (
                    self.remove_bookmark_from_menu(url)
                )
            )

    def open_bookmark(self, url):
        web_view = self.current_web_view()
        if web_view:
            web_view.load(QUrl(url))

    def open_history_page(self):
        web_view = self.current_web_view()
        if web_view is None:
            return

        html = render_history_page(
            load_history(),
            settings=getattr(self, "settings", {}),
        )
        self.load_internal_html_page(web_view, "history", html)

    def open_settings_page(self, web_view=None, message=""):
        if web_view is None:
            web_view = self.current_web_view()

        if web_view is None:
            return

        html = render_settings_page(self.settings, message)
        self.load_internal_html_page(
            web_view,
            "settings",
            html,
            address_text=INTERNAL_SETTINGS_URL,
        )

    def save_settings_from_request(self, web_view, values):
        self.settings = save_settings(self.settings | values)
        self.apply_browser_theme()
        BrowserWindow.open_settings_page(
            self,
            web_view,
            "Settings saved. Nexus has recalibrated.",
        )

    def crawl_current_site(self):
        web_view = self.current_web_view()
        if web_view is None:
            return

        url = web_view.url().toString()
        if not url.startswith(("http://", "https://")):
            self.statusBar().showMessage("Open a website before crawling.", 5000)
            return

        self.statusBar().showMessage("Crawling current site...")
        max_pages = normalize_crawler_page_limit(
            self.settings.get("crawler_max_pages", DEFAULT_CRAWLER_MAX_PAGES)
        )
        max_depth = normalize_crawler_depth(
            self.settings.get("crawler_max_depth", DEFAULT_CRAWLER_MAX_DEPTH)
        )

        try:
            pages = crawl_and_store(url, max_pages=max_pages, max_depth=max_depth)
        except Exception as error:
            self.statusBar().showMessage(f"Crawl failed: {error}", 8000)
            return

        self.statusBar().showMessage(
            f"Indexed {len(pages)} page(s) from this site.", 8000
        )

    def search_result_limit(self, value=None):
        return normalize_result_limit(
            self.settings.get("search_results_limit", DEFAULT_SEARCH_RESULT_LIMIT)
            if value is None
            else value
        )

    def render_search_results_page(self, query, results, result_limit):
        return render_results_page(
            query,
            results,
            result_limit=result_limit,
            settings=self.settings,
        )

    def remove_bookmark_from_menu(self, url):
        remove_bookmark(url)
        self.update_bookmark_action()

    def record_history(self, web_view, success):
        if not success:
            return

        title = web_view.title()
        url = web_view.url().toString()

        if (
            url
            and url != "about:blank"
            and not url.startswith("data:")
            and not is_internal_page_url(url)
        ):
            add_history_entry(title, url)
