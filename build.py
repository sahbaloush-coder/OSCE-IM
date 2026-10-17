import re, html, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(ROOT, "content")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "index.html")

ORDER = [
    ("Cardiology", "#c0392b"), ("Pulmonology", "#2471a3"), ("Gastroenterology", "#b9770e"),
    ("Nephrology", "#7d3c98"), ("Endocrinology", "#148f77"), ("Hematology-Oncology", "#a93226"),
    ("Infectious-Diseases", "#1e8449"), ("Neurology", "#5b2c6f"), ("Rheumatology", "#ca6f1e"),
    ("General", "#566573"), ("Miscellaneous", "#7f8c8d"),
    ("Communication", "#2e86c1"), ("Data-Interpretation", "#117a65"),
]

def split_top(s, sep):
    parts, depth, cur, i = [], 0, "", 0
    while i < len(s):
        c = s[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if depth == 0 and s.startswith(sep, i):
            parts.append(cur); cur = ""; i += len(sep); continue
        cur += c; i += 1
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]

def items_of(text):
    text = text.strip().rstrip(".")
    text = re.sub(r"\. (?=[A-Z][A-Za-z0-9 /()-]{1,30}: )", "; ", text)
    parts = split_top(text, "; ")
    if len(parts) == 1:
        parts = split_top(text, ", ")
    return [p.rstrip(".") for p in parts]

def esc(s):
    return html.escape(s, quote=False)

FIGS = os.path.join(ROOT, "figures")
def img_uri(name):
    # images live next to index.html in images/
    if not os.path.exists(os.path.join(ROOT, "images", name + ".jpg")):
        sys.exit(f"missing image: images/{name}.jpg")
    return f"images/{name}.jpg"

def fig_lines(key):
    p = os.path.join(FIGS, key + ".txt")
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8").read().splitlines():
        m = re.match(r"^@ (\S+) \| (.*)$", line)
        if m:
            out += ["", f"#### {m.group(2)}", f"![{m.group(2)}]({m.group(1)})"]
        elif line.strip():
            out.append(line)
    return out

def render(path):
    src = open(path, encoding="utf-8").read().splitlines()
    key = os.path.basename(path)[:-3]
    fl = fig_lines(key)
    if fl:
        nums = [int(m.group(1)) for l in src for m in [re.match(r"^## (\d+)\.", l)] if m]
        n = (max(nums) + 1) if nums else 1
        src = src + ["", f"## {n}. Data interpretation", "", "Images from the checklists, grouped by station, with the finding and the diagnosis."] + fl
    body, stack, title = [], [], ""
    def close_to(level):
        while stack and stack[-1] >= level:
            stack.pop(); body.append("</div></details>")
    for line in src:
        if not line.strip():
            continue
        m = re.match(r"^(#{1,4}) (.*)$", line)
        if m:
            lvl = len(m.group(1))
            if lvl == 1:
                title = m.group(2); continue
            close_to(lvl)
            body.append(f'<details class="h{lvl}" open><summary>{esc(m.group(2))}</summary><div class="inner">')
            stack.append(lvl); continue
        m = re.match(r"^!\[(.*)\]\((\S+)\)$", line)
        if m:
            body.append(f'<figure><img loading="lazy" src="{img_uri(m.group(2))}" alt="{html.escape(m.group(1))}"></figure>')
            continue
        m = re.match(r"^- \*\*(.+?)\*\*\s*(.*)$", line)
        if m:
            label, rest = m.group(1).rstrip(":"), m.group(2)
            lis = "".join(f"<li dir=\"auto\">{esc(i)}</li>" for i in items_of(rest))
            body.append(f'<div class="pt"><div class="label">{esc(label)}</div><ul class="box">{lis}</ul></div>')
            continue
        body.append(f'<p class="lead" dir="auto">{esc(line)}</p>')
    close_to(0)
    cases = sum(1 for l in src if re.match(r"^#### \d+\.", l))
    imgs = sum(1 for l in src if l.startswith("!["))
    return title, cases, imgs, "".join(body)

cards, panels = [], []
for key, color in ORDER:
    title, cases, imgs, body = render(os.path.join(MD, key + ".md"))
    sub = (f"{cases} cases" if cases else "") + (" · " if cases and imgs else "") + (f"{imgs} images" if imgs else "")
    cards.append(f'<a class="card" href="#{key}" style="--c:{color}"><span class="cname">{esc(title)}</span>'
                 f'<span class="ccount">{sub}</span></a>')
    panels.append(f'<section class="panel" id="p-{key}" data-title="{esc(title)}" hidden>'
                  f'<h1 style="--c:{color}">{esc(title)}</h1>{body}</section>')

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Qassim IM OSCE Summary</title>
<style>
:root {{ --bg:#fafaf8; --fg:#1d1d1b; --muted:#666; --line:#cfcfc8; --box:#fff; --h2:#e9eef5; --h3:#f1f1ec; --h4:#f7f7f3; --mark:#fff176; --hit:#ffd54f; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#18191a; --fg:#e8e8e3; --muted:#a0a09a; --line:#3d3f42; --box:#222427; --h2:#24303d; --h3:#2a2c2f; --h4:#25272a; --mark:#7a6a00; --hit:#9c6d00; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
.wrap {{ max-width:1100px; margin:0 auto; padding:16px; }}
h1 {{ font-size:22px; margin:8px 0 12px; }}
.panel h1 {{ border-left:6px solid var(--c); padding-left:10px; }}
.sub {{ color:var(--muted); margin:-6px 0 18px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:12px; }}
.card {{ display:flex; flex-direction:column; justify-content:space-between; min-height:96px; padding:14px; border-radius:10px;
  background:var(--box); border:1px solid var(--line); border-top:6px solid var(--c); color:var(--fg); text-decoration:none; }}
.card:hover {{ border-color:var(--c); box-shadow:0 2px 10px rgba(0,0,0,.08); }}
.cname {{ font-weight:700; font-size:17px; }}
.ccount {{ color:var(--muted); font-size:13px; }}
.bar {{ position:sticky; top:0; background:var(--bg); padding:8px 0; z-index:5; display:flex; gap:8px; flex-wrap:wrap; align-items:center; border-bottom:1px solid var(--line); margin-bottom:12px; }}
button, select, input {{ font:inherit; padding:6px 12px; border:1px solid var(--line); background:var(--box); color:var(--fg); border-radius:6px; }}
button {{ cursor:pointer; }}
button:hover {{ border-color:var(--muted); }}
input[type=search] {{ flex:1 1 180px; min-width:0; }}
#count {{ color:var(--muted); font-size:13px; }}
details {{ border:1px solid var(--line); border-radius:8px; margin:8px 0; background:var(--box); }}
summary {{ cursor:pointer; padding:8px 12px; font-weight:600; list-style:none; display:flex; gap:8px; align-items:baseline; }}
summary::-webkit-details-marker {{ display:none; }}
summary::before {{ content:"▸"; display:inline-block; width:1em; transition:transform .15s; color:var(--muted); }}
details[open] > summary::before {{ transform:rotate(90deg); }}
details.h2 > summary {{ font-size:18px; background:var(--h2); border-radius:8px; }}
details.h3 > summary {{ font-size:16px; background:var(--h3); border-radius:8px; }}
details.h4 > summary {{ font-size:15px; background:var(--h4); border-radius:8px; }}
details[open] > summary {{ border-bottom:1px solid var(--line); border-radius:8px 8px 0 0; }}
.inner {{ padding:6px 12px 10px; }}
.lead {{ color:var(--muted); margin:6px 0 10px; }}
.pt {{ margin:10px 0; }}
.label {{ font-weight:700; margin-bottom:4px; }}
mark {{ background:var(--mark); color:inherit; padding:0 3px; border-radius:3px; }}
ul.box {{ margin:0; padding:8px 12px 8px 30px; border:1px solid var(--line); border-radius:6px; background:var(--bg);
  display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); column-gap:28px; row-gap:2px; }}
ul.box li {{ padding-left:2px; }}
figure {{ margin:8px 0 4px; }} figure img {{ max-width:100%; max-height:560px; height:auto; border:1px solid var(--line); border-radius:6px; background:#fff; display:block; }}
.pt.hit ul.box {{ border-color:var(--hit); border-width:2px; }}
.hide {{ display:none !important; }}
#home[hidden], .panel[hidden], #specbar[hidden] {{ display:none; }}
@media (max-width:600px) {{ ul.box {{ grid-template-columns:1fr; }} }}
@media print {{ .bar {{ display:none; }} details {{ break-inside:avoid-page; }} }}
</style></head>
<body><div class="wrap">
<div id="home">
<h1>Qassim Internal Medicine OSCE — Summary</h1>
<p class="sub">Pick a specialty. Each one has the core history, history add-ons, the exam, exam add-ons, then the cases.</p>
<div class="grid">{''.join(cards)}</div>
</div>
<div class="bar" id="specbar" hidden>
<button onclick="location.hash=''">← All specialties</button>
<select id="jump" onchange="location.hash=this.value">{''.join(f'<option value="{k}">{k.replace("-", " ")}</option>' for k,_ in ORDER)}</select>
<button onclick="setAll(true)">Expand all</button>
<button onclick="setAll(false)">Collapse all</button>
<button onclick="setLevel(2)">Sections only</button>
<button onclick="setLevel(3)">Sections + subsections</button>
<input type="search" id="q" placeholder="Search this specialty…" oninput="search(this.value)">
<span id="count"></span>
</div>
{''.join(panels)}
</div>
<script>
let cur = null;
function panel() {{ return cur ? document.getElementById('p-' + cur) : null; }}
function show() {{
  const key = decodeURIComponent(location.hash.slice(1));
  const p = key && document.getElementById('p-' + key);
  document.querySelectorAll('.panel').forEach(x => x.hidden = true);
  document.getElementById('home').hidden = !!p;
  document.getElementById('specbar').hidden = !p;
  cur = p ? key : null;
  if (p) {{ p.hidden = false; document.getElementById('jump').value = key; document.title = p.dataset.title + ' — OSCE'; }}
  else document.title = 'Qassim IM OSCE Summary';
  document.getElementById('q').value = ''; search('');
  window.scrollTo(0, 0);
}}
function setAll(o) {{ const p = panel(); if (p) p.querySelectorAll('details').forEach(d => d.open = o); }}
function setLevel(n) {{
  const p = panel(); if (!p) return;
  p.querySelectorAll('details').forEach(d => {{ d.open = parseInt(d.className.slice(1), 10) < n; }});
}}
function search(q) {{
  const p = panel(); const c = document.getElementById('count');
  if (!p) return;
  q = q.trim().toLowerCase();
  p.querySelectorAll('.hide').forEach(e => e.classList.remove('hide'));
  p.querySelectorAll('.pt.hit').forEach(e => e.classList.remove('hit'));
  if (!q) {{ c.textContent = ''; return; }}
  let n = 0;
  p.querySelectorAll('.pt, .lead').forEach(e => {{
    const m = e.textContent.toLowerCase().includes(q);
    e.classList.toggle('hide', !m);
    if (m && e.classList.contains('pt')) {{ e.classList.add('hit'); n++; }}
  }});
  [...p.querySelectorAll('details')].reverse().forEach(d => {{
    const titleHit = d.querySelector(':scope > summary').textContent.toLowerCase().includes(q);
    if (titleHit) {{ d.querySelectorAll('.hide').forEach(e => e.classList.remove('hide')); }}
    const any = titleHit || d.querySelector('.pt:not(.hide), .lead:not(.hide)');
    d.classList.toggle('hide', !any);
    if (any) d.open = true;
  }});
  c.textContent = n + ' match' + (n === 1 ? '' : 'es');
}}
window.addEventListener('hashchange', show);
show();
</script>
</body></html>"""
open(OUT, "w", encoding="utf-8").write(page)
print("ok", len(page))
