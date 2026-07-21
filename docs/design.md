# Design

## Product Goal

Nexus Browser should be a small desktop browser for everyday use and learning. It should feel simple, private, tech-forward, and understandable: local files store user data, the interface stays minimal, and each feature is built in clear layers.

## Version 1 Scope

The first version should focus on a functional browsing loop:

- Start the application.
- Open a main browser window.
- Load a custom local homepage.
- Accept either a URL or a search query.
- Navigate backward, forward, reload, and home.
- Record visited pages in local history.
- Let users edit browser/search/crawler/theme settings in the app.

## Recommended Stack

- Python for the application code.
- PySide6 for the desktop interface.
- PySide6-WebEngine for Chromium-based page rendering.
- JSON files for early local data storage.

## Code Architecture

- `src/browser/` owns the Qt window, tab manager, navigation, and address-bar UI.
- Internal browser pages, including home, history, and search results, are
  rendered as local HTML files to avoid browser security blocks on `data:` URLs.
- `src/search_engine/` owns query routing, local ranking, integrated web search,
  result rendering, and bounded crawling for selected websites.
- Root-level `src` modules own local storage and application services such as
  bookmarks, history, and settings.
- Search-engine modules should not import Qt browser-window classes. The browser
  calls the search engine through small functions and renders the returned data.

## Main Interface

The first layout should have:

- A top navigation bar.
- Back, forward, reload, and home controls.
- A combined address and search bar.
- A tab strip.
- A central web view that opens to a custom homepage with a centered search box.

## Data Model

Bookmarks should store:

- Page title
- URL
- Date added

History should store:

- Page title
- URL
- Visit timestamp

Settings should store:

- Homepage
- Default search engine
- Fallback external search engine
- Search result display limit
- Crawler page and depth limits
- Theme
- Theme mode
- Theme accent
- Custom accent color

## Search Behavior

The address bar should decide whether the input is a URL or a search query.

- Inputs starting with `http://` or `https://` open directly.
- Domain-like inputs such as `example.com` become `https://example.com`.
- Other text uses the configured search engine.
- When the configured engine is Nexus Search, crawled pages are searched
  alongside live web results. History is only used as a ranking signal: results
  from previously visited URLs or sites receive a small score boost.
- If Nexus Search cannot load integrated web results, the internal results
  page still renders and offers direct links to external provider searches.
- The homepage search box submits through an internal browser URL, which the Qt
  page intercepts and routes into the same Nexus Search flow as the address
  bar.
- Search requests can include a `limit` parameter. The browser clamps this to a
  safe 1-100 range and carries it from the homepage to the results page.
- The crawler defaults to a broader but bounded crawl of 75 pages at depth 2,
  with a hard page cap of 100.

## Packaging Behavior

When running from source, local data is stored in the repository `data/` folder.
When running as a packaged executable, user data is stored under the user's app
data directory while bundled assets are loaded from the packaged resources.
