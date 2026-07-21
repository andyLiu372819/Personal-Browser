import re


APP_NAME = "Nexus Browser"
APP_SHORT_NAME = "Nexus"
APP_SLUG = "NexusBrowser"
APP_TAGLINE = "Personal search, tuned for your web."

THEME_MODES = ("light", "dark")
DEFAULT_THEME_MODE = "dark"
DEFAULT_THEME_ACCENT = "cyber"
DEFAULT_CUSTOM_ACCENT_COLOR = "#38BDF8"

ACCENT_THEMES = {
    "cyber": {
        "label": "Cyber Blue",
        "accent": "#38BDF8",
        "accent_2": "#8B5CF6",
    },
    "violet": {
        "label": "Plasma Violet",
        "accent": "#A855F7",
        "accent_2": "#EC4899",
    },
    "emerald": {
        "label": "Matrix Emerald",
        "accent": "#22C55E",
        "accent_2": "#14B8A6",
    },
    "amber": {
        "label": "Solar Amber",
        "accent": "#F59E0B",
        "accent_2": "#EF4444",
    },
    "custom": {
        "label": "Custom",
        "accent": DEFAULT_CUSTOM_ACCENT_COLOR,
        "accent_2": "#8B5CF6",
    },
}

HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def normalize_theme_mode(value):
    return value if value in THEME_MODES else DEFAULT_THEME_MODE


def normalize_theme_accent(value):
    return value if value in ACCENT_THEMES else DEFAULT_THEME_ACCENT


def normalize_hex_color(value, default=DEFAULT_CUSTOM_ACCENT_COLOR):
    if isinstance(value, str):
        value = value.strip()
        if HEX_COLOR_PATTERN.match(value):
            return value.upper()

    return default


def resolve_accent(settings=None):
    settings = settings or {}
    accent_name = normalize_theme_accent(settings.get("theme_accent"))

    if accent_name == "custom":
        return {
            "name": accent_name,
            "label": ACCENT_THEMES[accent_name]["label"],
            "accent": normalize_hex_color(settings.get("custom_accent_color")),
            "accent_2": ACCENT_THEMES[accent_name]["accent_2"],
        }

    return {"name": accent_name, **ACCENT_THEMES[accent_name]}


def theme_palette(settings=None):
    settings = settings or {}
    mode = normalize_theme_mode(settings.get("theme_mode", settings.get("theme")))
    accent = resolve_accent(settings)

    if mode == "light":
        palette = {
            "mode": "light",
            "background": "#F6F8FC",
            "background_2": "#E8F1FF",
            "surface": "#FFFFFF",
            "surface_2": "#EEF4FF",
            "panel": "rgba(255, 255, 255, 0.82)",
            "border": "#D5DEEA",
            "text": "#101827",
            "muted": "#60708A",
            "input": "#FFFFFF",
            "shadow": "rgba(15, 23, 42, 0.12)",
            "toolbar": "#F8FBFF",
            "toolbar_hover": "#E6F0FF",
            "toolbar_pressed": "#D6E6FF",
            "icon": "#111827",
            "grid": "rgba(30, 64, 175, 0.08)",
        }
    else:
        palette = {
            "mode": "dark",
            "background": "#060B16",
            "background_2": "#0D1628",
            "surface": "#0F172A",
            "surface_2": "#162033",
            "panel": "rgba(15, 23, 42, 0.82)",
            "border": "#233047",
            "text": "#E5F0FF",
            "muted": "#94A3B8",
            "input": "#111B2F",
            "shadow": "rgba(0, 0, 0, 0.36)",
            "toolbar": "#081120",
            "toolbar_hover": "#132238",
            "toolbar_pressed": "#1C3352",
            "icon": "#E5F0FF",
            "grid": "rgba(56, 189, 248, 0.08)",
        }

    palette["accent"] = accent["accent"]
    palette["accent_2"] = accent["accent_2"]
    palette["accent_name"] = accent["name"]
    palette["accent_label"] = accent["label"]
    palette["accent_soft"] = hex_to_rgba(accent["accent"], 0.16)
    palette["accent_glow"] = hex_to_rgba(accent["accent"], 0.32)
    return palette


def hex_to_rgba(color, alpha):
    color = normalize_hex_color(color).lstrip("#")
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red}, {green}, {blue}, {alpha})"


def css_variables(settings=None):
    palette = theme_palette(settings)
    variables = {
        "background": palette["background"],
        "background-2": palette["background_2"],
        "surface": palette["surface"],
        "surface-2": palette["surface_2"],
        "panel": palette["panel"],
        "border": palette["border"],
        "text": palette["text"],
        "muted": palette["muted"],
        "input": palette["input"],
        "accent": palette["accent"],
        "accent-2": palette["accent_2"],
        "accent-soft": palette["accent_soft"],
        "accent-glow": palette["accent_glow"],
        "shadow": palette["shadow"],
        "grid": palette["grid"],
    }

    return "\n".join(f"--{name}: {value};" for name, value in variables.items())


def selected_attribute(value, selected_value):
    return " selected" if value == selected_value else ""


def checked_attribute(value, selected_value):
    return " checked" if value == selected_value else ""


def render_brand_mark(settings=None, class_name="mark"):
    palette = theme_palette(settings)
    accent = palette["accent"]
    accent_2 = palette["accent_2"]

    return f"""
    <svg class="{class_name}" viewBox="0 0 140 140" role="img" aria-label="{APP_NAME} logo">
        <defs>
            <linearGradient id="nexusGradient" x1="20" y1="120" x2="124" y2="18">
                <stop offset="0" stop-color="{accent}" />
                <stop offset="0.58" stop-color="{accent_2}" />
                <stop offset="1" stop-color="#E0F2FE" />
            </linearGradient>
            <filter id="nexusGlow" x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="5" result="blur" />
                <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                </feMerge>
            </filter>
        </defs>
        <rect x="18" y="18" width="104" height="104" rx="30" fill="url(#nexusGradient)" filter="url(#nexusGlow)" />
        <path d="M42 93V47L98 93V47" fill="none" stroke="#F8FAFC" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" />
        <path d="M42 47L98 93" fill="none" stroke="#020617" stroke-opacity="0.38" stroke-width="4" stroke-linecap="round" />
        <circle cx="42" cy="47" r="7" fill="#F8FAFC" />
        <circle cx="98" cy="93" r="7" fill="#F8FAFC" />
    </svg>
    """


def qt_stylesheet(settings=None):
    palette = theme_palette(settings)

    return f"""
    QMainWindow {{
        background: {palette["background"]};
    }}
    QToolBar {{
        background: {palette["toolbar"]};
        border: none;
        border-bottom: 1px solid {palette["border"]};
        spacing: 4px;
        padding: 6px;
    }}
    QToolButton {{
        background: transparent;
        color: {palette["text"]};
        border: none;
        border-radius: 6px;
        padding: 5px;
    }}
    QToolButton:hover {{
        background: {palette["toolbar_hover"]};
    }}
    QToolButton:pressed {{
        background: {palette["toolbar_pressed"]};
    }}
    QLineEdit {{
        background: {palette["input"]};
        color: {palette["text"]};
        border: 1px solid {palette["border"]};
        border-radius: 8px;
        padding: 6px 10px;
        selection-background-color: {palette["accent"]};
    }}
    QLineEdit:focus {{
        border-color: {palette["accent"]};
    }}
    QMenu {{
        background: {palette["surface"]};
        color: {palette["text"]};
        border: 1px solid {palette["border"]};
        padding: 6px;
    }}
    QMenu::item {{
        border-radius: 4px;
        padding: 6px 28px 6px 10px;
    }}
    QMenu::item:selected {{
        background: {palette["toolbar_hover"]};
    }}
    QMenu::item:disabled {{
        color: {palette["muted"]};
    }}
    QMenu::separator {{
        background: {palette["border"]};
        height: 1px;
        margin: 5px;
    }}
    QTabWidget::pane {{
        border-top: 1px solid {palette["border"]};
    }}
    QTabBar::tab {{
        background: {palette["surface_2"]};
        color: {palette["muted"]};
        border: 1px solid {palette["border"]};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 7px 12px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {palette["surface"]};
        color: {palette["text"]};
    }}
    QStatusBar {{
        background: {palette["toolbar"]};
        color: {palette["muted"]};
        border-top: 1px solid {palette["border"]};
    }}
    """
