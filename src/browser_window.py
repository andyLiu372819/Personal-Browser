from pathlib import Path

from PySide6.QtCore import QSize, Qt, QUrl
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
from history import add_history_entry
from search import build_url_from_input
from settings import load_settings
from tab_manager import TabManager


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = PROJECT_ROOT / "assets" / "icons"


def load_icon(name):
    icon_path = ICONS_DIR / f"{name}.svg"
    renderer = QSvgRenderer(str(icon_path))

    if not renderer.isValid():
        raise RuntimeError(f"Could not load icon: {icon_path}")

    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


def create_icon_action(icon_name, tooltip, parent):
    action = QAction(load_icon(icon_name), "", parent)
    action.setObjectName(f"{icon_name}_action")
    action.setToolTip(tooltip)
    action.setStatusTip(tooltip)
    return action


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()

        self.setWindowTitle("Personal Browser")
        self.resize(1200, 800)

        self.tab_manager = TabManager()
        self.setCentralWidget(self.tab_manager)

        self.create_navigation_bar()

        self.tab_manager.tab_created.connect(self.connect_tab)
        self.tab_manager.currentChanged.connect(self.on_current_tab_changed)
        self.tab_manager.last_tab_close_requested.connect(self.close)

        self.add_new_tab(QUrl(self.settings["homepage"]), focus_address=False)

    def create_navigation_bar(self):
        navigation_bar = QToolBar("Navigation")
        navigation_bar.setIconSize(QSize(24, 24))
        navigation_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        navigation_bar.setStyleSheet(
            """
            QToolBar {
                background: #F3F5F0;
                border: none;
                border-bottom: 1px solid #C8D0C3;
                spacing: 4px;
                padding: 6px;
            }
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QToolButton:hover {
                background: #DFE6DA;
            }
            QToolButton:pressed {
                background: #C9D5C3;
            }
            QLineEdit {
                background: #FFFFFF;
                color: #20271E;
                border: 1px solid #B7C1B1;
                border-radius: 7px;
                padding: 6px 10px;
                selection-background-color: #A9BE9B;
            }
            QLineEdit:focus {
                border-color: #668357;
            }
            """
        )
        self.addToolBar(navigation_bar)

        self.back_action = create_icon_action("back", "Back", self)
        self.back_action.triggered.connect(self.go_back)
        navigation_bar.addAction(self.back_action)

        self.forward_action = create_icon_action("forward", "Forward", self)
        self.forward_action.triggered.connect(self.go_forward)
        navigation_bar.addAction(self.forward_action)

        reload_action = create_icon_action("reload", "Reload", self)
        reload_action.setShortcut("Ctrl+R")
        reload_action.triggered.connect(self.reload_page)
        navigation_bar.addAction(reload_action)

        home_action = create_icon_action("home", "Home", self)
        home_action.triggered.connect(self.go_home)
        navigation_bar.addAction(home_action)

        new_tab_action = create_icon_action("new_tab", "New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        navigation_bar.addAction(new_tab_action)

        close_tab_action = create_icon_action("close_tab", "Close Tab", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(self.tab_manager.close_current_tab)
        navigation_bar.addAction(close_tab_action)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Type a search or URL")
        self.address_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.address_bar.returnPressed.connect(self.load_address_bar_url)
        navigation_bar.addWidget(self.address_bar)

        focus_address_action = create_icon_action(
            "focus_address", "Focus Address Bar", self
        )
        focus_address_action.setShortcut("Ctrl+L")
        focus_address_action.triggered.connect(self.focus_address_bar)
        self.address_bar.addAction(focus_address_action, QLineEdit.LeadingPosition)

        self.bookmark_action = create_icon_action(
            "bookmark", "Add Bookmark", self
        )
        self.bookmark_action.setShortcut("Ctrl+D")
        self.bookmark_action.setEnabled(False)
        self.bookmark_action.triggered.connect(self.toggle_current_bookmark)
        self.address_bar.addAction(self.bookmark_action, QLineEdit.TrailingPosition)

        self.bookmarks_menu = QMenu(self)
        self.bookmarks_menu.setStyleSheet(
            """
            QMenu {
                background: #FFFFFF;
                color: #20271E;
                border: 1px solid #B7C1B1;
                padding: 6px;
            }
            QMenu::item {
                border-radius: 4px;
                padding: 6px 28px 6px 10px;
            }
            QMenu::item:selected {
                background: #DFE6DA;
            }
            QMenu::item:disabled {
                color: #8A9286;
            }
            QMenu::separator {
                background: #D5DBD1;
                height: 1px;
                margin: 5px;
            }
            """
        )
        self.bookmarks_menu.aboutToShow.connect(self.rebuild_bookmarks_menu)

        self.bookmarks_button = QToolButton(self)
        self.bookmarks_button.setIcon(load_icon("bookmarks"))
        self.bookmarks_button.setToolTip("Bookmarks")
        self.bookmarks_button.setPopupMode(QToolButton.InstantPopup)
        self.bookmarks_button.setMenu(self.bookmarks_menu)
        navigation_bar.addWidget(self.bookmarks_button)

    def connect_tab(self, web_view):
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
        target_url = url or QUrl(self.settings["homepage"])
        self.tab_manager.add_tab(target_url)

        if focus_address:
            self.focus_address_bar()

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
            web_view.load(QUrl(self.settings["homepage"]))

    def load_address_bar_url(self):
        user_input = self.address_bar.text().strip()
        if not user_input:
            return

        search_engine = self.settings["default_search_engine"]
        url = build_url_from_input(user_input, search_engine)
        self.current_web_view().load(QUrl(url))

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

        self.address_bar.setText(url.toString())
        self.address_bar.setCursorPosition(0)
        self.update_navigation_actions()
        self.update_bookmark_action()

    def update_window_title(self, web_view, title):
        if web_view is self.current_web_view():
            page_title = title.strip() or "New Tab"
            self.setWindowTitle(f"{page_title} - Personal Browser")

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
        can_bookmark = bool(url and url != "about:blank")

        self.bookmark_action.setEnabled(can_bookmark)

        if can_bookmark and is_bookmarked(url):
            self.bookmark_action.setIcon(load_icon("bookmark_filled"))
            self.bookmark_action.setToolTip("Remove Bookmark")
            self.bookmark_action.setStatusTip("Remove Bookmark")
        else:
            self.bookmark_action.setIcon(load_icon("bookmark"))
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

    def remove_bookmark_from_menu(self, url):
        remove_bookmark(url)
        self.update_bookmark_action()

    def record_history(self, web_view, success):
        if not success:
            return

        title = web_view.title()
        url = web_view.url().toString()

        if url and url != "about:blank":
            add_history_entry(title, url)
