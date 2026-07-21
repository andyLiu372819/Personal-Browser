from html import escape

from theme import APP_NAME, css_variables, render_brand_mark

from .internal_pages import INTERNAL_HOME_URL, INTERNAL_SETTINGS_URL


def render_history_page(history_entries, settings=None):
    items = []

    for entry in reversed(history_entries):
        title = entry.get("title", "").strip() or entry.get("url", "Untitled")
        url = entry.get("url", "")
        visited_at = entry.get("visited_at", "Unknown time")

        safe_title = escape(title)
        safe_url = escape(url)
        safe_visited_at = escape(visited_at)

        items.append(
            f"""
        <article class="history-card">
            <a class="url" href="{safe_url}">{safe_url}</a>
            <h2><a href="{safe_url}">{safe_title}</a></h2>
            <small>Visited: {safe_visited_at}</small>
        </article>
        """
        )

    if items:
        history_html = "\n".join(items)
    else:
        history_html = """
        <section class="empty-state">
            <h2>No browsing history yet</h2>
            <p>Once you browse the web, visited sites will appear here.</p>
        </section>
        """

    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>History - {APP_NAME}</title>
        <style>
            :root {{
                {css_variables(settings)}
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                color: var(--text);
                background:
                    linear-gradient(var(--grid) 1px, transparent 1px),
                    linear-gradient(90deg, var(--grid) 1px, transparent 1px),
                    radial-gradient(circle at 15% 0%, var(--accent-glow), transparent 26rem),
                    var(--background);
                background-size: 34px 34px, 34px 34px, auto, auto;
                font-family:
                    Inter,
                    "Segoe UI",
                    system-ui,
                    -apple-system,
                    sans-serif;
            }}

            main {{
                width: min(920px, calc(100vw - 36px));
                margin: 0 auto;
                padding: 44px 0 72px;
            }}

            header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 18px;
                margin-bottom: 28px;
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 14px;
            }}

            .mark {{
                width: 58px;
                height: 58px;
            }}

            h1 {{
                margin: 0;
                font-size: clamp(2.3rem, 6vw, 4.8rem);
                letter-spacing: -0.08em;
                text-transform: uppercase;
            }}

            nav {{
                display: flex;
                gap: 10px;
            }}

            nav a {{
                padding: 10px 13px;
                border: 1px solid var(--border);
                border-radius: 999px;
                color: var(--text);
                background: var(--surface-2);
                text-decoration: none;
                font-weight: 800;
            }}

            .history-card,
            .empty-state {{
                margin-bottom: 18px;
                padding: 22px;
                border: 1px solid var(--border);
                border-radius: 20px;
                background: var(--panel);
                box-shadow: 0 18px 46px var(--shadow);
            }}

            .url {{
                display: block;
                overflow: hidden;
                color: var(--muted);
                text-overflow: ellipsis;
                white-space: nowrap;
                text-decoration: none;
            }}

            h2 {{
                margin: 8px 0;
                font-size: 1.25rem;
            }}

            h2 a {{
                color: var(--accent);
                text-decoration: none;
            }}

            h2 a:hover,
            nav a:hover,
            .url:hover {{
                text-decoration: underline;
            }}

            small,
            p {{
                color: var(--muted);
            }}
        </style>
    </head>
    <body>
        <main>
            <header>
                <section class="brand">
                    {render_brand_mark(settings)}
                    <h1>History</h1>
                </section>
                <nav aria-label="Internal navigation">
                    <a href="{INTERNAL_HOME_URL}">Home</a>
                    <a href="{INTERNAL_SETTINGS_URL}">Settings</a>
                </nav>
            </header>
            {history_html}
        </main>
    </body>
    </html>
    """
