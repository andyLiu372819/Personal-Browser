from html import escape

from search_engine import (
    SEARCH_RESULT_LIMIT_OPTIONS,
    normalize_crawler_depth,
    normalize_crawler_page_limit,
    normalize_result_limit,
)
from settings import (
    EXTERNAL_SEARCH_ENGINE_OPTIONS,
    SEARCH_ENGINE_OPTIONS,
    normalize_settings,
)
from theme import (
    ACCENT_THEMES,
    APP_NAME,
    APP_TAGLINE,
    THEME_MODES,
    css_variables,
    render_brand_mark,
    selected_attribute,
)

from .internal_pages import INTERNAL_HOME_URL, INTERNAL_SETTINGS_SAVE_URL


def render_options(options, selected_value, labels=None):
    labels = labels or {}
    rendered_options = []

    for option in options:
        safe_option = escape(str(option), quote=True)
        safe_label = escape(str(labels.get(option, option)))
        selected = selected_attribute(option, selected_value)
        rendered_options.append(
            f'<option value="{safe_option}"{selected}>{safe_label}</option>'
        )

    return "\n".join(rendered_options)


def render_settings_page(settings, message=""):
    settings = normalize_settings(settings)
    safe_message = escape(message)
    message_html = (
        f'<p class="notice" role="status">{safe_message}</p>' if safe_message else ""
    )

    engine_labels = {
        "personal": "Nexus Search",
        "duckduckgo": "DuckDuckGo",
        "google": "Google",
        "bing": "Bing",
    }
    accent_labels = {
        key: value["label"]
        for key, value in ACCENT_THEMES.items()
    }

    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Settings - {APP_NAME}</title>
        <style>
            :root {{
                color-scheme: {settings["theme_mode"]};
                {css_variables(settings)}
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                min-height: 100vh;
                margin: 0;
                color: var(--text);
                background:
                    linear-gradient(var(--grid) 1px, transparent 1px),
                    linear-gradient(90deg, var(--grid) 1px, transparent 1px),
                    radial-gradient(circle at 20% 0%, var(--accent-glow), transparent 30rem),
                    radial-gradient(circle at 90% 12%, var(--accent-soft), transparent 28rem),
                    var(--background);
                background-size: 34px 34px, 34px 34px, auto, auto, auto;
                font-family:
                    Inter,
                    "Segoe UI",
                    system-ui,
                    -apple-system,
                    sans-serif;
            }}

            main {{
                width: min(980px, calc(100vw - 36px));
                margin: 0 auto;
                padding: 44px 0 72px;
            }}

            .hero {{
                display: grid;
                grid-template-columns: auto 1fr;
                align-items: center;
                gap: 22px;
                margin-bottom: 28px;
            }}

            .mark {{
                width: 82px;
                height: 82px;
                filter: drop-shadow(0 18px 34px var(--accent-glow));
            }}

            h1 {{
                margin: 0;
                font-size: clamp(2.2rem, 6vw, 4.8rem);
                letter-spacing: -0.08em;
                line-height: 0.95;
            }}

            .subtitle {{
                margin: 8px 0 0;
                color: var(--muted);
                font-size: 1rem;
            }}

            form {{
                display: grid;
                gap: 18px;
            }}

            fieldset {{
                margin: 0;
                padding: 24px;
                border: 1px solid var(--border);
                border-radius: 24px;
                background: var(--panel);
                box-shadow: 0 22px 60px var(--shadow);
                backdrop-filter: blur(18px);
            }}

            legend {{
                padding: 0 8px;
                color: var(--accent);
                font-size: 0.82rem;
                font-weight: 800;
                letter-spacing: 0.14em;
                text-transform: uppercase;
            }}

            .grid {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 16px;
            }}

            label {{
                display: grid;
                gap: 8px;
                color: var(--muted);
                font-size: 0.9rem;
                font-weight: 700;
            }}

            input,
            select {{
                width: 100%;
                min-height: 44px;
                border: 1px solid var(--border);
                border-radius: 13px;
                padding: 10px 12px;
                color: var(--text);
                background: var(--input);
                font: inherit;
                outline: none;
            }}

            input:focus,
            select:focus {{
                border-color: var(--accent);
                box-shadow: 0 0 0 4px var(--accent-soft);
            }}

            input[type="color"] {{
                padding: 5px;
            }}

            .hint {{
                margin: 6px 0 0;
                color: var(--muted);
                font-size: 0.84rem;
                line-height: 1.5;
            }}

            .notice {{
                margin: 0 0 18px;
                padding: 12px 14px;
                border: 1px solid var(--accent);
                border-radius: 14px;
                color: var(--text);
                background: var(--accent-soft);
                font-weight: 700;
            }}

            .actions {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                justify-content: flex-end;
            }}

            button,
            .button-link {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-height: 44px;
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0 18px;
                color: var(--text);
                background: var(--surface-2);
                text-decoration: none;
                font-weight: 800;
                cursor: pointer;
            }}

            button.primary {{
                border-color: transparent;
                color: #F8FAFC;
                background: linear-gradient(135deg, var(--accent), var(--accent-2));
                box-shadow: 0 14px 34px var(--accent-glow);
            }}

            @media (max-width: 720px) {{
                .hero,
                .grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <main>
            <section class="hero">
                {render_brand_mark(settings)}
                <div>
                    <h1>Nexus Control</h1>
                    <p class="subtitle">{escape(APP_TAGLINE)} Customize search, crawling, and the browser shell.</p>
                </div>
            </section>

            {message_html}

            <form action="{INTERNAL_SETTINGS_SAVE_URL}" method="get">
                <fieldset>
                    <legend>Browser</legend>
                    <div class="grid">
                        <label>
                            Homepage
                            <input name="homepage" type="text" value="{escape(settings["homepage"], quote=True)}">
                        </label>
                        <label>
                            Default search engine
                            <select name="default_search_engine">
                                {render_options(SEARCH_ENGINE_OPTIONS, settings["default_search_engine"], engine_labels)}
                            </select>
                        </label>
                        <label>
                            Fallback external search
                            <select name="fallback_search_engine">
                                {render_options(EXTERNAL_SEARCH_ENGINE_OPTIONS, settings["fallback_search_engine"], engine_labels)}
                            </select>
                        </label>
                        <label>
                            Results shown
                            <select name="search_results_limit">
                                {render_options(SEARCH_RESULT_LIMIT_OPTIONS, settings["search_results_limit"])}
                            </select>
                        </label>
                    </div>
                    <p class="hint">Use <code>{INTERNAL_HOME_URL}</code> to keep the Nexus homepage.</p>
                </fieldset>

                <fieldset>
                    <legend>Crawler</legend>
                    <div class="grid">
                        <label>
                            Max pages
                            <input
                                name="crawler_max_pages"
                                type="number"
                                min="1"
                                max="100"
                                value="{normalize_crawler_page_limit(settings["crawler_max_pages"])}"
                            >
                        </label>
                        <label>
                            Max depth
                            <input
                                name="crawler_max_depth"
                                type="number"
                                min="0"
                                max="4"
                                value="{normalize_crawler_depth(settings["crawler_max_depth"])}"
                            >
                        </label>
                    </div>
                    <p class="hint">Depth 2 is a good default: broad enough to be useful, still bounded.</p>
                </fieldset>

                <fieldset>
                    <legend>Theme</legend>
                    <div class="grid">
                        <label>
                            Light / dark mode
                            <select name="theme_mode">
                                {render_options(THEME_MODES, settings["theme_mode"], {"light": "Light", "dark": "Dark"})}
                            </select>
                        </label>
                        <label>
                            Accent theme
                            <select name="theme_accent">
                                {render_options(tuple(ACCENT_THEMES), settings["theme_accent"], accent_labels)}
                            </select>
                        </label>
                        <label>
                            Custom accent color
                            <input
                                name="custom_accent_color"
                                type="color"
                                value="{escape(settings["custom_accent_color"], quote=True)}"
                            >
                        </label>
                    </div>
                    <p class="hint">Choose Custom as the accent theme to use the custom color.</p>
                </fieldset>

                <section class="actions" aria-label="Settings actions">
                    <a class="button-link" href="{INTERNAL_HOME_URL}">Back home</a>
                    <button class="primary" type="submit">Save settings</button>
                </section>
            </form>
        </main>
    </body>
    </html>
    """
