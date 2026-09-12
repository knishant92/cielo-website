#!/usr/bin/env python3
"""Build design/*.template.html into design/*.html with shared head/scripts and inlined assets."""
import pathlib, re, base64, sys
D = pathlib.Path(__file__).parent; A = D.parent / "assets"
head = (D/"_head.html").read_text(); scripts = (D/"_scripts.html").read_text(); nav = (D/"_nav.html").read_text(); foot = (D/"_foot.html").read_text()
roots = [A/"shoot", A/"work", A]  # drive/ resolves via A
def find(name):
    for r in roots:
        if (r/name).exists(): return r/name
    raise FileNotFoundError(name)
def img(m):
    f = find(m.group(1)); mime = "image/png" if f.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64,"+base64.b64encode(f.read_bytes()).decode()
def vid(m): return "data:video/mp4;base64,"+base64.b64encode((A/"video"/m.group(1)).read_bytes()).decode()
names = sys.argv[1:] or [p.name[:-len(".template.html")] for p in D.glob("*.template.html") if not p.name.startswith("home-v")]
for n in names:
    t = (D/f"{n}.template.html").read_text()
    t = re.sub(r"\{\{HEAD:([^}]+)\}\}", lambda m: head.replace("{{TITLE}}", m.group(1)), t).replace("{{SCRIPTS}}", scripts).replace("{{NAV}}", nav).replace("{{FOOT}}", foot)
    out = re.sub(r"\{\{IMG:([^}]+)\}\}", img, t); out = re.sub(r"\{\{VID:([^}]+)\}\}", vid, out)
    (D/f"{n}.html").write_text(out); print(f"{n}.html  {len(out)//1024} KB")
