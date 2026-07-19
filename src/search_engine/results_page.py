from html import escape


def render_results_page(query, results):
    safe_query = escape(query)
    result_items = []

    for score, document in results:
        safe_title = escape(document.title)
        safe_url = escape(document.url)
        safe_content = escape(document.content[:240].strip())
        snippet_html = f"<p>{safe_content}</p>" if safe_content else ""

        result_items.append(
            f"""
        <article>
            <h2><a href="{safe_url}">{safe_title}</a></h2>
            <p>{safe_url}</p>
            {snippet_html}
            <small>Score: {score}</small>
        </article>
        """
        )

    if result_items:
        results_html = "\n".join(result_items)
    else:
        results_html = "<p>No local results found</p>"

    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Search results for {safe_query}</title>
    </head>
    <body>
        <h1>Search results for {safe_query}</h1>
        {results_html}
    </body>
    </html>
    """
