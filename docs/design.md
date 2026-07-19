# Design

## Product Goal

Personal Browser should be a small desktop browser for everyday use and learning. It should feel simple, private, and understandable: local files store user data, the interface stays minimal, and each feature is built in clear layers.

## Version 1 Scope

The first version should focus on a functional browsing loop:

- Start the application.
- Open a main browser window.
- Load a custom local homepage.
- Accept either a URL or a search query.
- Navigate backward, forward, reload, and home.
- Record visited pages in local history.

## Recommended Stack

- Python for the application code.
- PySide6 for the desktop interface.
- PySide6-WebEngine for Chromium-based page rendering.
- JSON files for early local data storage.

## Code Architecture

- `src/browser/` owns the Qt window, tab manager, navigation, and address-bar UI.
- Internal browser pages, including home, history, and search results, are
  rendered as local HTML files to avoid browser security blocks on `data:` URLs.
- `src/search_engine/` owns query routing, local ranking, result rendering, and
  bounded crawling for selected websites.
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
- Theme

## Search Behavior

The address bar should decide whether the input is a URL or a search query.

- Inputs starting with `http://` or `https://` open directly.
- Domain-like inputs such as `example.com` become `https://example.com`.
- Other text uses the configured search engine.
- When the configured engine is Personal Search, local history, bookmarks, and
  crawled pages are searched first.
- If Personal Search has no local results, the query falls back to the configured
  external search engine.
- The homepage search box submits through an internal browser URL, which the Qt
  page intercepts and routes into the same Personal Search flow as the address
  bar.
