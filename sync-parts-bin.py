#!/usr/bin/env python3
"""Inject gamemaker-relevant tools from ~/code/aihotsource/data/ into index.html.

Re-run after aihotsource data updates:  python3 sync-parts-bin.py
Idempotent: replaces everything between the PARTS-BIN markers.
"""
import json, html, os, pathlib, re

SITE = pathlib.Path(os.environ.get("FRANKENSITE_DIR", pathlib.Path(__file__).parent))
DATA = pathlib.Path(os.environ.get("AIHOTSOURCE_DATA",
                                   pathlib.Path.home() / "code" / "aihotsource" / "data"))
START, END = "<!--PARTS-BIN-START-->", "<!--PARTS-BIN-END-->"

# Files whose entries are all gamemaker-relevant vs. filtered by category keyword.
TAKE_ALL = {"animation.json"}
KEYWORDS = re.compile(
    r"3d|video|voice|tts|stt|audio|speech|image|music|creative|anim|mocap|rig|"
    r"local|2d|game|godot|mesh|texture", re.I)
SOURCES = ["hot-picks.json", "animation.json", "free-inference.json",
           "workflows-skills.json", "agent-tools.json"]
EXCLUDE = re.compile(r"hackathon|bount|affiliate|crm|outreach|prospect", re.I)

GROUP_ORDER = ["3D & Mesh", "Animation & Motion", "Video", "Audio & Voice",
               "Image & Creative", "Local Inference", "Other Parts"]

def group_of(e):
    blob = f"{e.get('category','')} {e.get('name','')} {e.get('best_for','')}".lower()
    if re.search(r"anim|mocap|rig|inbetween|interpolat|pose", blob): return "Animation & Motion"
    if re.search(r"3d|mesh|sculpt|gltf|usd", blob): return "3D & Mesh"
    if re.search(r"video", blob): return "Video"
    if re.search(r"voice|tts|stt|speech|audio|whisper|music", blob): return "Audio & Voice"
    if re.search(r"image|creative|flux|diffusion|art", blob): return "Image & Creative"
    if re.search(r"local|ollama|llama|inference|runtime", blob): return "Local Inference"
    return "Other Parts"

def rating_int(n):
    if isinstance(n, str) and "\U0001F525" in n:
        n = n.count("\U0001F525")
    try: return max(1, min(5, int(n)))
    except (TypeError, ValueError): return 3

def flames(n):
    return "&#128293;" * rating_int(n)

def card(e):
    name, url = html.escape(str(e.get("name",""))), html.escape(str(e.get("url","#")))
    free = html.escape(str(e.get("free_tier","")))
    best = html.escape(str(e.get("best_for","")))
    got = html.escape(str(e.get("gotchas","")))
    gline = f'<p class="pb-gotcha">&#9888; {got}</p>' if got else ""
    return (f'<div class="pb-card"><div class="pb-head"><a href="{url}" target="_blank" '
            f'rel="noopener">{name}</a><span class="pb-fl">{flames(e.get("rating"))}</span></div>'
            f'<p class="pb-free">{free}</p><p class="pb-best">{best}</p>{gline}</div>')

def main():
    seen, groups = set(), {g: [] for g in GROUP_ORDER}
    for fname in SOURCES:
        p = DATA / fname
        if not p.exists():
            print(f"  (skip, missing: {fname})"); continue
        for e in json.loads(p.read_text()):
            blob = f"{e.get('category','')} {e.get('name','')}"
            if e.get("name") in seen: continue
            if fname not in TAKE_ALL and not KEYWORDS.search(blob): continue
            if EXCLUDE.search(blob): continue
            seen.add(e.get("name"))
            groups[group_of(e)].append(e)

    parts = []
    for g in GROUP_ORDER:
        if not groups[g]: continue
        cards = "\n".join(card(e) for e in sorted(groups[g], key=lambda e: -rating_int(e.get("rating"))))
        parts.append(f'<div class="pb-group"><h3 class="pb-group-title">{g}</h3>'
                     f'<div class="pb-grid">{cards}</div></div>')

    parts_html = "\n".join(parts)
    section = f'''{START}
<section class="parts-bin" id="parts-bin" style="padding:4rem 1.5rem;max-width:1200px;margin:0 auto;">
  <div class="section-title">The Parts Bin</div>
  <p style="text-align:center;font-size:0.72rem;color:#666;max-width:560px;margin:-0.8rem auto 2.2rem;line-height:1.8;">
    Every monster starts as parts. Free and open tools for stitching games together &mdash;
    ranked by heat, flagged for gotchas. Full board at
    <a href="https://aihotsource.vercel.app" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none;">aihotsource.vercel.app</a>.
  </p>
  <style>
    .pb-group{{margin-bottom:2.2rem}}
    .pb-group-title{{font-family:'Orbitron',monospace;font-size:0.75rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--accent);margin-bottom:0.9rem}}
    .pb-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}}
    .pb-card{{border:1px solid #1a1a2e;background:var(--bg2);padding:12px 14px;transition:border-color .3s}}
    .pb-card:hover{{border-color:#f9731640}}
    .pb-head{{display:flex;justify-content:space-between;gap:8px;align-items:baseline}}
    .pb-head a{{color:#c8c8d0;font-size:0.78rem;font-weight:700;text-decoration:none}}
    .pb-head a:hover{{color:var(--accent)}}
    .pb-fl{{font-size:0.55rem;white-space:nowrap}}
    .pb-free{{font-size:0.65rem;color:#888;margin-top:5px;line-height:1.5}}
    .pb-best{{font-size:0.62rem;color:#555;margin-top:4px;line-height:1.5}}
    .pb-gotcha{{font-size:0.6rem;color:#b08440;margin-top:6px;border-top:1px dashed #1a1a2e;padding-top:6px;line-height:1.5}}
  </style>
{parts_html}
</section>
{END}'''.replace("{{", "{").replace("}}", "}")

    idx = SITE / "index.html"
    src = idx.read_text()
    if START in src:
        src = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: section, src, flags=re.S)
    else:
        anchor = '<!-- PHILOSOPHY: DON\'T BUILD THE MONSTER -->'
        src = src.replace(anchor, section + "\n\n" + anchor)
    idx.write_text(src)
    n = sum(len(v) for v in groups.values())
    print(f"parts bin synced: {n} tools in {sum(1 for v in groups.values() if v)} groups")

if __name__ == "__main__":
    main()
