# Nexus Browser

Nexus Browser is a desktop web browser built with Python, PySide6, and Qt WebEngine. The goal is to create a clean, tech-forward personal browsing environment with tabs, bookmarks, history, settings, custom themes, crawling, and a custom search experience.

This repository currently contains the project design skeleton. The first implementation milestone is a simple browser window that opens a custom local homepage and accepts either URLs or search queries from the homepage or address bar.

## Planned Features

- Desktop browser window
- Address bar that supports URLs and search terms
- Back, forward, reload, and home navigation
- Multiple tabs
- Local bookmarks
- Local browsing history
- Settings saved as JSON
- Nexus Search over crawled pages and web results, with history-based ranking boosts
- Bounded crawler for indexing selected websites
- User-selectable search result counts up to 100 results
- Proper in-browser settings page
- Light/dark mode plus selectable accent themes and a custom accent color

## Project Structure

```text
src/
  browser/        Window, tabs, and browser-interface modules
  search_engine/  Query routing, local ranking, web search, result rendering, and crawling
  *.py            Storage and application services
data/             Local JSON data for settings, history, and bookmarks
assets/           Icons, theme files, and visual assets
docs/             Design notes, milestones, and feature planning
```

## First Milestone

Build a desktop browser that:

- Opens a main window
- Loads the custom Nexus Browser homepage
- Lets the user type a URL or search query
- Lets the user choose how many search results to display
- Supports basic navigation controls
- Uses Nexus Search as the default search engine, including live web results
- Boosts results from sites the user has already visited

## Building an Executable

The project includes a PyInstaller spec and build script:

```powershell
.\scripts\build_exe.ps1
```

The packaged app is produced under `dist/NexusBrowser/`.
