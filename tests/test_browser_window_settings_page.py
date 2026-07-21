import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import browser.window as browser_window


class FakeWebView:
    pass


class FakeBrowserWindow:
    def __init__(self):
        self.web_view = FakeWebView()
        self.settings = {
            "homepage": "personal-browser://home",
            "default_search_engine": "personal",
            "fallback_search_engine": "duckduckgo",
            "search_results_limit": 10,
            "crawler_max_pages": 75,
            "crawler_max_depth": 2,
            "theme_mode": "dark",
            "theme_accent": "cyber",
            "custom_accent_color": "#38BDF8",
        }
        self.internal_pages = []
        self.theme_applied = False

    def current_web_view(self):
        return self.web_view

    def load_internal_html_page(self, web_view, page_name, html, address_text=""):
        self.internal_pages.append((web_view, page_name, html, address_text))

    def apply_browser_theme(self):
        self.theme_applied = True


class BrowserWindowSettingsPageTests(unittest.TestCase):
    def setUp(self):
        self.original_render_settings_page = browser_window.render_settings_page
        self.original_save_settings = browser_window.save_settings

    def tearDown(self):
        browser_window.render_settings_page = self.original_render_settings_page
        browser_window.save_settings = self.original_save_settings

    def test_open_settings_page_renders_into_current_tab(self):
        fake_window = FakeBrowserWindow()

        def fake_render(settings, message=""):
            self.assertEqual(settings, fake_window.settings)
            self.assertEqual(message, "")
            return "<html>settings</html>"

        browser_window.render_settings_page = fake_render

        browser_window.BrowserWindow.open_settings_page(fake_window)

        self.assertEqual(
            fake_window.internal_pages,
            [
                (
                    fake_window.web_view,
                    "settings",
                    "<html>settings</html>",
                    "personal-browser://settings",
                )
            ],
        )

    def test_save_settings_from_request_persists_and_rerenders(self):
        fake_window = FakeBrowserWindow()
        rendered_messages = []

        def fake_save(settings):
            self.assertEqual(settings["theme_mode"], "light")
            return settings

        def fake_render(settings, message=""):
            rendered_messages.append(message)
            return "<html>settings saved</html>"

        browser_window.save_settings = fake_save
        browser_window.render_settings_page = fake_render

        browser_window.BrowserWindow.save_settings_from_request(
            fake_window,
            fake_window.web_view,
            {"theme_mode": "light"},
        )

        self.assertEqual(fake_window.settings["theme_mode"], "light")
        self.assertTrue(fake_window.theme_applied)
        self.assertEqual(rendered_messages, ["Settings saved. Nexus has recalibrated."])


if __name__ == "__main__":
    unittest.main()
