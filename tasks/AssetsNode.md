# Task: AssetsNode

## Objective
Extract the company’s logo URL and a 3–5 HEX color palette from a given webpage URL.

## Requirements
- Decorate with `@Node(retries=3)`.
- Fetch the page HTML using `httpx` with a 10-second timeout.
- Parse HTML with BeautifulSoup to locate, in order:
  1. `<meta property="og:image" content=...>`
  2. `<link rel="icon" href=...>`
  3. `<link rel="shortcut icon" href=...>`
  4. `<link rel="apple-touch-icon" href=...>`
- Resolve relative URLs against the page URL.
- If a logo URL is found:
  - Download the image via `httpx`.
  - On `image/svg+xml` or `.svg` URLs, convert SVG bytes to PNG via `cairosvg.svg2png`.
  - Use `colorthief.ColorThief` on the final image bytes to extract up to 5 dominant colors.
  - Convert RGB tuples to uppercase HEX strings (`#RRGGBB`) and return the first 3–5.
- If no logo is found or extraction fails, return `logo_url: None` and `palette: []`.

## Acceptance Criteria
- Returns a dict with:
  - `logo_url`: full absolute URL or `None`.
  - `palette`: list of 0–5 HEX color strings.
- Retries up to 3× on network/HTTP errors before failing.