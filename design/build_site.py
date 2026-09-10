#!/usr/bin/env python3
"""Production build: design/*.template.html -> site/ with real asset files, page links, and shared partials."""
import pathlib, re, shutil, hashlib, base64
D = pathlib.Path(__file__).parent; ROOT = D.parent; A = ROOT/"assets"; OUT = ROOT/"site"
head = (D/"_head.html").read_text(); scripts = (D/"_scripts.html").read_text()
PAGES = {"home":"index.html","ai-shoot":"ai-shoot/index.html","creatives":"creatives/index.html","listings":"listings/index.html","pdp":"complete-pdp/index.html","work":"work/index.html","start-a-pilot":"start-a-pilot/index.html"}
LINKS = {  # label -> path (site nav + footer)
 "Services":"/#services","Work":"/work/","Projects":"/projects/","How we work":"/#how","Why Cielo":"/#outcomes",
 "AI Shoot":"/ai-shoot/","Creatives and films":"/creatives/","Listings":"/listings/","Post Production":"/#post","The complete PDP":"/complete-pdp/","Start a pilot":"/start-a-pilot/","Home":"/",
}
roots = [A/"shoot", A/"work", A]
def find(name):
    for r in roots:
        if (r/name).exists(): return r/name
    raise FileNotFoundError(name)
if OUT.exists(): shutil.rmtree(OUT)
(OUT/"media").mkdir(parents=True)
used = {}
def copy_asset(src):
    if src in used: return used[src]
    h = hashlib.md5(src.read_bytes()).hexdigest()[:8]
    dst = OUT/"media"/f"{src.stem}-{h}{src.suffix}"; shutil.copy2(src, dst)
    used[src] = "/media/" + dst.name; return used[src]
def img(m): return copy_asset(find(m.group(1)))
def vid(m): return copy_asset(A/"video"/m.group(1))
def links(html):
    for label, path in LINKS.items():
        html = html.replace(f'<a href="#">{label}</a>', f'<a href="{path}">{label}</a>')
        html = html.replace(f'href="#">{label}</a>', f'href="{path}">{label}</a>')
    html = html.replace('<a class="brand" href="#"', '<a class="brand" href="/"')
    html = html.replace('<a class="btn btn-red" href="#pilot">Start a pilot</a>', '<a class="btn btn-red" href="/start-a-pilot/">Start a pilot</a>')
    html = html.replace('<a href="#pilot">Start a pilot</a>', '<a href="/start-a-pilot/">Start a pilot</a>')
    MORE = {"How it works →":"/ai-shoot/","How an AI shoot works, what we need from you →":"/ai-shoot/","Formats and turnarounds →":"/creatives/","Formats, adapts and turnarounds →":"/creatives/","Marketplaces and package →":"/listings/","Marketplaces, package, what we need →":"/listings/","What an audit covers →":"/complete-pdp/","What an audit and a revamp cover →":"/complete-pdp/","Audit or revamp your PDPs →":"/complete-pdp/","Read the project →":"/projects/","All work, by service and category":"/work/","All work: shoots, reels, A+, listings":"/work/","Ask for references":"/start-a-pilot/"}
    for label, path in MORE.items():
        html = html.replace(f'href="#">{label}</a>', f'href="{path}">{label}</a>')
        html = html.replace(f'href="#" style="font-weight:600;font-size:14px">{label}</a>', f'href="{path}" style="font-weight:600;font-size:14px">{label}</a>')
    html = html.replace('<a class="tile" href="#">', '<a class="tile" href="/work/">').replace('<a href="#"><img', '<a href="/work/"><img').replace('<a href="#" class="wide"><img', '<a href="/work/" class="wide"><img')
    html = re.sub(r'<a class="btn btn-red" href="#">Start (a|the) pilot', r'<a class="btn btn-red" href="/start-a-pilot/">Start \1 pilot', html)
    html = html.replace('<a class="btn btn-red" href="#pilot">', '<a class="btn btn-red" href="/start-a-pilot/">').replace('<a class="btn btn-ghost" href="#">', '<a class="btn btn-ghost" href="/work/">')
    return html
SEO = {
 "home": ("Cielo E-Commerce · Ecommerce content experts", "AI shoots, creatives, listings and films for D2C and marketplace brands. Content that gets every SKU live sooner, and keeps it selling."),
 "ai-shoot": ("AI Shoot · Cielo E-Commerce", "Shoot-quality stills, lifestyle and video from a flatlay or mannequin. Required angles, every SKU, checked by people."),
 "creatives": ("Creatives and films · Cielo E-Commerce", "A+ pages, RPDs, infographics, banners, brand stores, campaign films and reels, adapted to every marketplace."),
 "listings": ("Listings · Cielo E-Commerce", "Listings built to be found, understood and approved first time. Copy, structure, images and upload, on every major marketplace."),
 "pdp": ("The complete PDP · Cielo E-Commerce", "Audit, revamp and marketplace PDP content. A PDP that sells is all three services, assembled."),
 "work": ("Work · Cielo E-Commerce", "Stills, films, creatives, listings and retouching, by service and category."),
 "start-a-pilot": ("Start a pilot · Cielo E-Commerce", "One real batch of your SKUs through the full pipeline. Quote comes with the plan."),
}
def wrap(title, desc, body, canonical):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://cieloecommerce.com{canonical}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:type" content="website"><meta property="og:url" content="https://cieloecommerce.com{canonical}"><meta property="og:image" content="https://cieloecommerce.com/media/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.png" type="image/png">
<meta name="theme-color" content="#0B0E17">
{body}
</html>"""
for n, outpath in PAGES.items():
    t = (D/f"{n}.template.html").read_text()
    t = re.sub(r"\{\{HEAD:([^}]+)\}\}", lambda m: head, t).replace("{{SCRIPTS}}", scripts)
    # head partial starts with meta charset/viewport/title/link fonts + <style>; strip the meta/title lines (we write our own) but keep fonts + style
    t = re.sub(r'<meta charset="utf-8">\n<meta name="viewport"[^>]*>\n<title>\{\{TITLE\}\}</title>\n', '', t, count=1)
    t = re.sub(r"\{\{IMG:([^}]+)\}\}", img, t); t = re.sub(r"\{\{VID:([^}]+)\}\}", vid, t)
    t = links(t)
    title, desc = SEO[n]
    # split head-ish part (fonts+style) from body
    style_end = t.index("</style>") + len("</style>")
    headpart, bodypart = t[:style_end], t[style_end:]
    page = wrap(title, desc, headpart + "\n</head>\n<body>" + bodypart + "\n</body>", "/" + outpath.replace("index.html","")) 
    dst = OUT/outpath; dst.parent.mkdir(parents=True, exist_ok=True); dst.write_text(page)
    print(f"{outpath:26s} {len(page)//1024} KB")
# coming-soon pages
for slug, title in [("projects","Projects")]:
    t = (D/"coming-soon.template.html").read_text().replace("{{PAGE}}", title)
    t = re.sub(r"\{\{HEAD:([^}]+)\}\}", lambda m: head, t).replace("{{SCRIPTS}}", scripts)
    t = re.sub(r'<meta charset="utf-8">\n<meta name="viewport"[^>]*>\n<title>\{\{TITLE\}\}</title>\n', '', t, count=1)
    t = re.sub(r"\{\{IMG:([^}]+)\}\}", img, t); t = links(t)
    style_end = t.index("</style>") + len("</style>")
    page = wrap(f"{title} · Cielo E-Commerce", "Coming soon.", t[:style_end] + "\n</head>\n<body>" + t[style_end:] + "\n</body>", f"/{slug}/")
    (OUT/slug).mkdir(parents=True, exist_ok=True); (OUT/slug/"index.html").write_text(page); print(f"{slug}/index.html  {len(page)//1024} KB")
# favicon + og
shutil.copy2(A/"logo"/"mark-light.png", OUT/"favicon.png")
from PIL import Image, ImageDraw, ImageFont
og = Image.new("RGB", (1200, 630), (11, 14, 23)); d = ImageDraw.Draw(og)
try:
    fb = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 64); fs = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 26)
except Exception:
    fb = ImageFont.load_default(); fs = ImageFont.load_default()
hero = Image.open(A/"shoot"/"bralette-beige-out1.jpg").convert("RGB"); hero = hero.resize((int(630*hero.width/hero.height), 630)); og.paste(hero, (1200-hero.width, 0))
mark = Image.open(A/"logo"/"mark-dark.png").convert("RGBA"); mark.thumbnail((110, 84)); og.paste(mark, (72, 60), mark)
d.text((72, 200), "Content that gets", font=fb, fill=(242, 239, 233)); d.text((72, 275), "every SKU live sooner,", font=fb, fill=(242, 239, 233)); d.text((72, 350), "and keeps it selling.", font=fb, fill=(224, 8, 8))
d.text((72, 470), "AI shoots · creatives · listings · films", font=fs, fill=(154, 163, 184)); d.text((72, 508), "cieloecommerce.com", font=fs, fill=(154, 163, 184))
og.save(OUT/"media"/"og.jpg", quality=88)
(OUT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://cieloecommerce.com/sitemap.xml\n")
urls = ["/"] + [f"/{p.replace('index.html','')}" for p in PAGES.values() if p != "index.html"] + ["/projects/"]
(OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>https://cieloecommerce.com{u}</loc></url>" for u in urls) + "\n</urlset>\n")
(OUT/"_headers").write_text("/media/*\n  Cache-Control: public, max-age=31536000, immutable\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
print(f"media files: {len(used)} · site total: {total//1024//1024} MB")
