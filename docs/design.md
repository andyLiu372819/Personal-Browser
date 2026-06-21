# Design

## Product Goal

Personal Browser should be a small desktop browser for everyday use and learning. It should feel simple, private, and understandable: local files store user data, the interface stays minimal, and each feature is built in clear layers.

## Version 1 Scope

The first version should focus on a functional browsing loop:

- Start the application.
- Open a main browser window.
- Load the configured homepage.
- Accept either a URL or a search query.
- Navigate backward, forward, reload, and home.
- Record visited pages in local history.

## Recommended Stack

- Python for the application code.
- PySide6 for the desktop interface.
- PySide6-WebEngine for Chromium-based page rendering.
- JSON files for early local data storage.

## Main Interface

The first layout should have:

- A top navigation bar.
- Back, forward, reload, and home controls.
- A combined address and search bar.
- A tab strip.
- A central web view.

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
- Theme

## Search Behavior

The address bar should decide whether the input is a URL or a search query.

- Inputs starting with `http://` or `https://` open directly.
- Domain-like inputs such as `example.com` become `https://example.com`.
- Other text becomes a search query using the configured search engine.
