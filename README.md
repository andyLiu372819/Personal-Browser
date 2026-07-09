# Personal Browser

Personal Browser is a planned desktop web browser built with Python, PySide6, and Qt WebEngine. The goal is to create a clean personal browsing environment with tabs, bookmarks, history, settings, and a custom search experience.

This repository currently contains the project design skeleton. The first implementation milestone is a simple browser window that opens a homepage and accepts either URLs or search queries from one address bar.

## Planned Features

- Desktop browser window
- Address bar that supports URLs and search terms
- Back, forward, reload, and home navigation
- Multiple tabs
- Local bookmarks
- Local browsing history
- Settings saved as JSON
- Custom homepage and search flow
- Future local search over history and bookmarks

## Project Structure

```text
src/
  browser/        Window, tabs, and browser-interface modules
  search_engine/  Query routing and future indexing/ranking modules
  *.py            Storage and application services
data/             Local JSON data for settings, history, and bookmarks
assets/           Icons, theme files, and visual assets
docs/             Design notes, milestones, and feature planning
```

## First Milestone

Build a desktop browser that:

- Opens a main window
- Loads the configured homepage
- Lets the user type a URL or search query
- Supports basic navigation controls
