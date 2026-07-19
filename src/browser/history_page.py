from html import escape


def render_history_page(history_entries):
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
        <article>
            <h2><a href="{safe_url}">{safe_title}</a></h2>
            <p>{safe_url}</p>
            <small>Visited: {safe_visited_at}</small>
        </article>
        """
        )

    if items:
        history_html = "\n".join(items)
    else:
        history_html = "<p>No browsing history yet</p>"

    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>History</title>
    </head>
    <body>
        <h1>History</h1>
        {history_html}
    </body>
    </html>
    """
