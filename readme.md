# cielo-website

Marketing site for Cielo E-Commerce. Static HTML built from `design/*.template.html` with shared partials, deployed on Cloudflare Pages.

## Layout
- `design/` — page templates, shared `_head.html` (styles) and `_scripts.html`, `build.py` (single-file previews) and `build_site.py` (production).
- `assets/` — source images and clips. `site/` — the built site, committed, served by Pages.
- `functions/api/lead.js` — Pages Function for the pilot form. Set `LEAD_WEBHOOK` in the Pages project to forward leads.

## Build
```bash
python3 design/build_site.py
```
Local run with the function: `npx wrangler@4 pages dev site --port 8788`

## Cloudflare Pages settings
Build command: none. Build output directory: `site`. Functions are picked up from `functions/`.
