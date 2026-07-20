from html import escape
from urllib.parse import quote_plus

from .hybrid_search import (
    DEFAULT_SEARCH_RESULT_LIMIT,
    SEARCH_RESULT_LIMIT_OPTIONS,
    normalize_result_limit,
)


SOURCE_LABELS = {
    "crawl": "Crawled page",
    "web": "Web result",
}


def external_search_url(query, provider="duckduckgo"):
    encoded_query = quote_plus(query.strip())
    urls = {
        "duckduckgo": f"https://duckduckgo.com/?q={encoded_query}",
        "google": f"https://www.google.com/search?q={encoded_query}",
        "bing": f"https://www.bing.com/search?q={encoded_query}",
    }
    return urls.get(provider, urls["duckduckgo"])


def pluralize_result(count):
    return "result" if count == 1 else "results"


def render_result_limit_options(selected_limit):
    selected_limit = normalize_result_limit(selected_limit)
    options = []

    for option in SEARCH_RESULT_LIMIT_OPTIONS:
        selected = " selected" if option == selected_limit else ""
        options.append(f'<option value="{option}"{selected}>{option} results</option>')

    return "\n".join(options)


def render_results_page(query, results, result_limit=DEFAULT_SEARCH_RESULT_LIMIT):
    result_limit = normalize_result_limit(result_limit)
    safe_query = escape(query)
    safe_query_attribute = escape(query, quote=True)
    result_limit_options = render_result_limit_options(result_limit)
    result_items = []

    for score, document in results:
        safe_title = escape(document.title)
        safe_url = escape(document.url)
        safe_content = escape(document.content[:240].strip())
        snippet_html = f'<p class="snippet">{safe_content}</p>' if safe_content else ""
        source_label = SOURCE_LABELS.get(document.source, document.source.title())
        safe_source_label = escape(source_label)

        if document.source == "web":
            metadata_html = f'<span class="source-chip web">{safe_source_label}</span>'
        else:
            metadata_html = (
                f'<span class="source-chip local">{safe_source_label}</span>'
                f'<span class="score">Score {score}</span>'
            )

        if document.visited_at:
            metadata_html += '<span class="source-chip visited">Visited before</span>'

            if document.source == "web":
                metadata_html += f'<span class="score">Score {score}</span>'

        result_items.append(
            f"""
        <article class="result-card">
            <a class="result-url" href="{safe_url}">{safe_url}</a>
            <h2><a href="{safe_url}">{safe_title}</a></h2>
            {snippet_html}
            <div class="metadata">{metadata_html}</div>
        </article>
        """
        )

    if result_items:
        results_html = "\n".join(result_items)
        summary_html = (
            f"Showing {len(results)} {pluralize_result(len(results))} from "
            f"your browser and the web. Display limit: {result_limit}."
        )
    else:
        safe_duckduckgo_url = escape(external_search_url(query, "duckduckgo"), quote=True)
        safe_google_url = escape(external_search_url(query, "google"), quote=True)
        results_html = f"""
        <section class="empty-state">
            <div class="empty-icon" aria-hidden="true">?</div>
            <h2>No results found yet</h2>
            <p>
                Personal Search could not find local or live web results for this query.
                Try a different phrase, or open a provider search page directly.
            </p>
            <div class="empty-actions">
                <a href="{safe_duckduckgo_url}">Search DuckDuckGo</a>
                <a href="{safe_google_url}">Search Google</a>
            </div>
        </section>
        """
        summary_html = f"No matching results were found. Display limit: {result_limit}."

    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Search results for {safe_query}</title>
        <style>
            :root {{
                --background: #f8faf6;
                --surface: #ffffff;
                --surface-soft: #eef5ea;
                --border: #dce6d5;
                --text: #172016;
                --muted: #66715f;
                --link: #1a5cc8;
                --url: #2f7147;
                --green: #668357;
                --green-dark: #48683c;
                --shadow: rgba(42, 68, 35, 0.1);
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                color: var(--text);
                background:
                    radial-gradient(circle at 12% 0%, rgba(229, 191, 104, 0.24), transparent 24rem),
                    radial-gradient(circle at 90% 8%, rgba(143, 179, 126, 0.28), transparent 28rem),
                    var(--background);
                font-family:
                    Inter,
                    "Segoe UI",
                    system-ui,
                    -apple-system,
                    sans-serif;
            }}

            header {{
                position: sticky;
                top: 0;
                z-index: 1;
                border-bottom: 1px solid var(--border);
                background: rgba(248, 250, 246, 0.92);
                backdrop-filter: blur(18px);
            }}

            .topbar {{
                display: grid;
                grid-template-columns: auto minmax(260px, 720px);
                align-items: center;
                gap: 28px;
                max-width: 1120px;
                margin: 0 auto;
                padding: 22px 28px;
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 10px;
                color: var(--green-dark);
                font-weight: 800;
                letter-spacing: -0.04em;
                text-decoration: none;
                white-space: nowrap;
            }}

            .brand-mark {{
                display: grid;
                place-items: center;
                width: 36px;
                height: 36px;
                border-radius: 12px;
                color: white;
                background: linear-gradient(135deg, var(--green), var(--green-dark));
                box-shadow: 0 8px 22px var(--shadow);
            }}

            form {{
                display: flex;
                gap: 10px;
                min-height: 48px;
                padding: 6px;
                border: 1px solid var(--border);
                border-radius: 999px;
                background: var(--surface);
                box-shadow: 0 14px 34px var(--shadow);
            }}

            input {{
                width: 100%;
                border: 0;
                outline: 0;
                padding: 0 16px;
                border-radius: 999px;
                color: var(--text);
                background: transparent;
                font-size: 1rem;
            }}

            button {{
                border: 0;
                border-radius: 999px;
                padding: 0 22px;
                color: white;
                background: linear-gradient(135deg, var(--green), var(--green-dark));
                font-weight: 700;
                cursor: pointer;
            }}

            select {{
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0 10px;
                color: var(--text);
                background: var(--surface-soft);
                font-weight: 700;
            }}

            main {{
                display: grid;
                grid-template-columns: minmax(0, 760px) minmax(220px, 280px);
                gap: 36px;
                max-width: 1120px;
                margin: 0 auto;
                padding: 30px 28px 64px;
            }}

            .summary {{
                margin: 0 0 22px;
                color: var(--muted);
                font-size: 0.95rem;
            }}

            .result-card {{
                padding: 0 0 26px;
                margin: 0 0 26px;
                border-bottom: 1px solid var(--border);
            }}

            .result-url {{
                display: block;
                max-width: 100%;
                overflow: hidden;
                color: var(--url);
                font-size: 0.92rem;
                text-decoration: none;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}

            h1 {{
                height: 1px;
                margin: 0;
                overflow: hidden;
                position: absolute;
                width: 1px;
            }}

            h2 {{
                margin: 6px 0 8px;
                font-size: 1.35rem;
                font-weight: 500;
                line-height: 1.28;
            }}

            h2 a {{
                color: var(--link);
                text-decoration: none;
            }}

            h2 a:hover,
            .result-url:hover,
            .empty-actions a:hover {{
                text-decoration: underline;
            }}

            .snippet {{
                margin: 0;
                color: #3d4738;
                font-size: 0.98rem;
                line-height: 1.58;
            }}

            .metadata {{
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 10px;
            }}

            .source-chip,
            .score {{
                display: inline-flex;
                align-items: center;
                min-height: 24px;
                padding: 3px 9px;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
            }}

            .source-chip.web {{
                color: #174ea6;
                background: #eaf1ff;
            }}

            .source-chip.local {{
                color: var(--green-dark);
                background: var(--surface-soft);
            }}

            .source-chip.visited {{
                color: #7a4d00;
                background: #fff4d8;
            }}

            .score {{
                color: var(--muted);
                background: #f0f2ee;
            }}

            aside {{
                align-self: start;
                padding: 20px;
                border: 1px solid var(--border);
                border-radius: 22px;
                background: rgba(255, 255, 255, 0.72);
                box-shadow: 0 16px 40px var(--shadow);
            }}

            aside h2 {{
                margin: 0 0 10px;
                color: var(--text);
                font-size: 1rem;
                font-weight: 800;
            }}

            aside p {{
                margin: 0;
                color: var(--muted);
                line-height: 1.55;
            }}

            .empty-state {{
                padding: 42px;
                border: 1px solid var(--border);
                border-radius: 28px;
                background: var(--surface);
                box-shadow: 0 18px 44px var(--shadow);
                text-align: center;
            }}

            .empty-icon {{
                display: grid;
                place-items: center;
                width: 58px;
                height: 58px;
                margin: 0 auto 16px;
                border-radius: 20px;
                color: white;
                background: linear-gradient(135deg, var(--green), var(--green-dark));
                font-size: 1.6rem;
                font-weight: 900;
            }}

            .empty-actions {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 12px;
                margin-top: 22px;
            }}

            .empty-actions a {{
                padding: 10px 14px;
                border: 1px solid var(--border);
                border-radius: 999px;
                color: var(--link);
                background: var(--surface-soft);
                text-decoration: none;
                font-weight: 700;
            }}

            @media (max-width: 820px) {{
                .topbar,
                main {{
                    grid-template-columns: 1fr;
                }}

                aside {{
                    display: none;
                }}

                form {{
                    flex-wrap: wrap;
                    border-radius: 26px;
                }}

                select,
                button {{
                    min-height: 40px;
                }}
            }}
        </style>
    </head>
    <body>
        <header>
            <div class="topbar">
                <a class="brand" href="personal-browser://home" aria-label="Personal Browser home">
                    <span class="brand-mark" aria-hidden="true">P</span>
                    <span>Personal Search</span>
                </a>
                <form action="personal-browser://search" method="get">
                    <input
                        name="q"
                        type="search"
                        value="{safe_query_attribute}"
                        aria-label="Search query"
                        autofocus
                    >
                    <select name="limit" aria-label="Number of search results">
                        {result_limit_options}
                    </select>
                    <button type="submit">Search</button>
                </form>
            </div>
        </header>

        <main>
            <section aria-label="Search results">
                <h1>Search results for {safe_query}</h1>
                <p class="summary">{summary_html}</p>
                {results_html}
            </section>
            <aside>
                <h2>How this search works</h2>
                <p>
                    Personal Search blends crawled pages and live web results,
                    then boosts sites that appear in your history.
                </p>
            </aside>
        </main>
    </body>
    </html>
    """
