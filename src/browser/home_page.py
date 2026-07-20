from html import escape

from search_engine import (
    DEFAULT_SEARCH_RESULT_LIMIT,
    SEARCH_RESULT_LIMIT_OPTIONS,
    normalize_result_limit,
)

from .internal_pages import INTERNAL_SEARCH_URL


def render_result_limit_options(selected_limit):
    selected_limit = normalize_result_limit(selected_limit)
    options = []

    for option in SEARCH_RESULT_LIMIT_OPTIONS:
        selected = " selected" if option == selected_limit else ""
        options.append(f'<option value="{option}"{selected}>{option} results</option>')

    return "\n".join(options)


def render_home_page(app_name="Personal Browser", result_limit=DEFAULT_SEARCH_RESULT_LIMIT):
    safe_app_name = escape(app_name)
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
                color-scheme: light;
                --ink: #172016;
                --muted: #5b6656;
                --panel: rgba(255, 255, 255, 0.76);
                --panel-border: rgba(255, 255, 255, 0.9);
                --green: #6f925d;
                --green-dark: #49683d;
                --gold: #e5bf68;
                --mist: #eef4ea;
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
                color: var(--ink);
                font-family:
                    Inter,
                    "Segoe UI",
                    system-ui,
                    -apple-system,
                    sans-serif;
                background:
                    radial-gradient(circle at 18% 18%, #fff8da 0, transparent 28%),
                    radial-gradient(circle at 84% 24%, #c8e1ba 0, transparent 30%),
                    radial-gradient(circle at 50% 105%, #9bbf88 0, transparent 42%),
                    linear-gradient(135deg, #f8fbf4 0%, #e9f1e4 47%, #dce9d4 100%);
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
                background: conic-gradient(from 120deg, #f4d77c, #8fb37e, #ffffff);
            }}

            .orb.two {{
                right: -12rem;
                bottom: -13rem;
                background: conic-gradient(from 260deg, #ffffff, #bfd7b2, #6f925d);
            }}

            main {{
                position: relative;
                width: min(860px, calc(100vw - 40px));
                padding: 52px;
                border: 1px solid var(--panel-border);
                border-radius: 36px;
                background: var(--panel);
                box-shadow:
                    0 28px 80px rgba(42, 68, 35, 0.16),
                    inset 0 1px 0 rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(22px);
            }}

            .mark {{
                width: 128px;
                height: 128px;
                margin: 0 auto 18px;
                display: block;
                filter: drop-shadow(0 18px 26px rgba(56, 86, 48, 0.22));
            }}

            h1 {{
                margin: 0;
                text-align: center;
                font-size: clamp(3rem, 9vw, 6.6rem);
                line-height: 0.92;
                letter-spacing: -0.08em;
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
                border: 1px solid rgba(73, 104, 61, 0.18);
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.82);
                box-shadow: 0 20px 48px rgba(54, 82, 47, 0.14);
            }}

            input {{
                width: 100%;
                border: 0;
                outline: 0;
                padding: 16px 20px;
                border-radius: 999px;
                color: var(--ink);
                background: transparent;
                font-size: 1rem;
            }}

            input::placeholder {{
                color: #829079;
            }}

            button {{
                border: 0;
                border-radius: 999px;
                padding: 0 26px;
                color: white;
                background:
                    linear-gradient(135deg, var(--green) 0%, var(--green-dark) 100%);
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 10px 22px rgba(73, 104, 61, 0.24);
            }}

            select {{
                border: 1px solid rgba(73, 104, 61, 0.16);
                border-radius: 999px;
                padding: 0 12px;
                color: var(--ink);
                background: rgba(255, 255, 255, 0.72);
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
                border: 1px solid rgba(73, 104, 61, 0.12);
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.46);
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
            <svg class="mark" viewBox="0 0 140 140" role="img" aria-label="Personal search compass">
                <defs>
                    <linearGradient id="leafGradient" x1="22" x2="118" y1="116" y2="18">
                        <stop offset="0" stop-color="#49683d" />
                        <stop offset="0.56" stop-color="#7fa46d" />
                        <stop offset="1" stop-color="#e5bf68" />
                    </linearGradient>
                </defs>
                <circle cx="70" cy="70" r="58" fill="rgba(255,255,255,0.68)" />
                <circle cx="70" cy="70" r="49" fill="none" stroke="#49683d" stroke-width="5" opacity="0.18" />
                <path
                    d="M93 31 C68 38 47 57 40 86 C66 80 87 63 100 38 C103 33 99 29 93 31Z"
                    fill="url(#leafGradient)"
                />
                <path
                    d="M43 96 C57 78 75 61 99 38"
                    fill="none"
                    stroke="white"
                    stroke-linecap="round"
                    stroke-width="7"
                    opacity="0.82"
                />
                <circle cx="44" cy="98" r="9" fill="#e5bf68" />
            </svg>

            <h1>{safe_app_name}</h1>
            <p class="subtitle">
                Search crawled pages and the wider web from one calm place. Sites
                you have visited before get a small ranking boost.
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
