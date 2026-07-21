from html import escape

from search_engine import (
    DEFAULT_SEARCH_RESULT_LIMIT,
    SEARCH_RESULT_LIMIT_OPTIONS,
    normalize_result_limit,
)
from theme import APP_NAME, APP_TAGLINE, css_variables, render_brand_mark

from .internal_pages import INTERNAL_SEARCH_URL, INTERNAL_SETTINGS_URL


def render_result_limit_options(selected_limit):
    selected_limit = normalize_result_limit(selected_limit)
    options = []

    for option in SEARCH_RESULT_LIMIT_OPTIONS:
        selected = " selected" if option == selected_limit else ""
        options.append(f'<option value="{option}"{selected}>{option} results</option>')

    return "\n".join(options)


def render_home_page(
    app_name=APP_NAME,
    result_limit=DEFAULT_SEARCH_RESULT_LIMIT,
    settings=None,
):
    safe_app_name = escape(app_name)
    safe_tagline = escape(APP_TAGLINE)
    result_limit_options = render_result_limit_options(result_limit)

    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{safe_app_name}</title>
        <style>
            :root {{
                {css_variables(settings)}
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                min-height: 100vh;
                margin: 0;
                display: grid;
                place-items: center;
                overflow: hidden;
                color: var(--text);
                font-family:
                    Inter,
                    "Segoe UI",
                    system-ui,
                    -apple-system,
                    sans-serif;
                background:
                    linear-gradient(var(--grid) 1px, transparent 1px),
                    linear-gradient(90deg, var(--grid) 1px, transparent 1px),
                    radial-gradient(circle at 18% 18%, var(--accent-glow), transparent 30%),
                    radial-gradient(circle at 84% 24%, var(--accent-soft), transparent 32%),
                    linear-gradient(135deg, var(--background) 0%, var(--background-2) 100%);
                background-size: 34px 34px, 34px 34px, auto, auto, auto;
            }}

            .orb {{
                position: fixed;
                width: 34rem;
                height: 34rem;
                border-radius: 999px;
                filter: blur(2px);
                opacity: 0.4;
                pointer-events: none;
            }}

            .orb.one {{
                left: -11rem;
                top: -9rem;
                background: conic-gradient(from 120deg, var(--accent), var(--accent-2), transparent);
            }}

            .orb.two {{
                right: -12rem;
                bottom: -13rem;
                background: conic-gradient(from 260deg, transparent, var(--accent-soft), var(--accent));
            }}

            main {{
                position: relative;
                width: min(860px, calc(100vw - 40px));
                padding: 52px;
                border: 1px solid var(--border);
                border-radius: 36px;
                background: var(--panel);
                box-shadow:
                    0 28px 80px var(--shadow),
                    inset 0 1px 0 var(--accent-soft);
                backdrop-filter: blur(22px);
            }}

            .mark {{
                width: 128px;
                height: 128px;
                margin: 0 auto 18px;
                display: block;
                filter: drop-shadow(0 18px 26px var(--accent-glow));
            }}

            h1 {{
                margin: 0;
                text-align: center;
                font-size: clamp(3rem, 9vw, 6.6rem);
                line-height: 0.92;
                letter-spacing: -0.08em;
                text-transform: uppercase;
            }}

            .subtitle {{
                max-width: 560px;
                margin: 18px auto 34px;
                text-align: center;
                color: var(--muted);
                font-size: 1.08rem;
                line-height: 1.6;
            }}

            form {{
                display: flex;
                gap: 12px;
                width: min(680px, 100%);
                margin: 0 auto;
                padding: 9px;
                border: 1px solid var(--border);
                border-radius: 999px;
                background: var(--panel);
                box-shadow: 0 20px 48px var(--shadow);
            }}

            input {{
                width: 100%;
                border: 0;
                outline: 0;
                padding: 16px 20px;
                border-radius: 999px;
                color: var(--text);
                background: transparent;
                font-size: 1rem;
            }}

            input::placeholder {{
                color: var(--muted);
            }}

            button {{
                border: 0;
                border-radius: 999px;
                padding: 0 26px;
                color: #F8FAFC;
                background:
                    linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 10px 22px var(--accent-glow);
            }}

            select {{
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0 12px;
                color: var(--text);
                background: var(--input);
                font-weight: 700;
            }}

            button:hover {{
                transform: translateY(-1px);
            }}

            .hint-row {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 10px;
                margin-top: 28px;
                color: var(--muted);
                font-size: 0.92rem;
            }}

            .hint {{
                padding: 8px 12px;
                border: 1px solid var(--border);
                border-radius: 999px;
                background: var(--surface-2);
            }}

            .settings-link {{
                position: absolute;
                right: 24px;
                top: 24px;
                color: var(--muted);
                text-decoration: none;
                font-weight: 800;
            }}

            .settings-link:hover {{
                color: var(--accent);
            }}

            @media (max-width: 640px) {{
                main {{
                    padding: 34px 20px;
                    border-radius: 28px;
                }}

                form {{
                    flex-direction: column;
                    border-radius: 26px;
                }}

                button {{
                    min-height: 48px;
                }}

                select {{
                    min-height: 48px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="orb one"></div>
        <div class="orb two"></div>

        <main aria-label="{safe_app_name} home">
            <a class="settings-link" href="{INTERNAL_SETTINGS_URL}">Settings</a>
            {render_brand_mark(settings)}

            <h1>{safe_app_name}</h1>
            <p class="subtitle">
                {safe_tagline} Search crawled pages and the wider web from one
                command bar. Sites you have visited before get a subtle boost.
            </p>

            <form action="{INTERNAL_SEARCH_URL}" method="get">
                <input
                    name="q"
                    type="search"
                    placeholder="Search or enter a website"
                    aria-label="Search or enter a website"
                    autofocus
                    required
                >
                <select name="limit" aria-label="Number of search results">
                    {result_limit_options}
                </select>
                <button type="submit">Search</button>
            </form>

            <section class="hint-row" aria-label="Search features">
                <span class="hint">Web results</span>
                <span class="hint">History boost</span>
                <span class="hint">Crawled pages</span>
                <span class="hint">Result limit</span>
            </section>
        </main>
    </body>
    </html>
    """
