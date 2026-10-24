#!/usr/bin/env python3
"""Build index.html from cv.json. Standard library only.

    python3 build.py

index.html is generated; edit cv.json (content) or this file (layout/style).
The output is deterministic: no timestamps, entries sorted by date.
"""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE_URL = "https://mthudaa.github.io/whoami/"
PHOTO = "Huda-formal-640.jpg"
PHOTO_SIZE = 640
SAFE_URL = ("https://", "http://", "mailto:", "tel:")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# (key in project["metrics"], unit shown next to the value, tile label)
METRICS = [
    ("power_uW", "µW", "Power"),
    ("conversion_time_us", "µs", "Conversion time"),
    ("enob_bits", "bit", "ENOB"),
    ("snr_dB", "dB", "SNR"),
]

SECTIONS = [
    ("education", "Education"),
    ("experience", "Experience"),
    ("projects", "Projects"),
    ("recognition", "Publication & Awards"),
    ("skills", "Skills"),
    ("contact", "Contact"),
]

# 24x24 stroke icons (fill none, stroke currentColor)
ICONS = {
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "lab": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4a2 2 0 0 0 1.8-3l-5-9V3"/><path d="M7.5 15h9"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    "out": '<path d="M7 17 17 7M8 7h9v9"/>',
}


def esc(value):
    return escape(str(value), quote=True)


def url(value):
    if not value.startswith(SAFE_URL):
        raise ValueError(f"refusing unsafe URL in cv.json: {value!r}")
    return esc(value)


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="18" height="18" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def month(value):
    m = re.fullmatch(r"(\d{4})-(\d{2})", value)
    return f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m else value


def span(start, end=None, expected_end=None):
    if end:
        tail = month(end)
    elif expected_end:
        tail = f"{month(expected_end)} (expected)"
    else:
        tail = "Present"
    return f"{month(start)} – {tail}"


def slash_range(value):
    a, _, b = value.partition("/")
    return f"{month(a)} – {month(b)}" if b else month(a)


def bullets(items):
    if not items:
        return ""
    return '<ul class="hl">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def chips(items):
    return '<ul class="chips">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def status_class(status):
    s = status.lower()
    if "did not complete" in s:
        return "warn"
    if s in ("tapeout completed", "fabricated"):
        return "ok"
    return ""


def section(idx, sid, title, body):
    return (f'<section id="{sid}" aria-labelledby="{sid}-h">\n'
            f'  <div class="wrap">\n'
            f'    <div class="sec-head"><span class="idx" aria-hidden="true">{idx:02d}</span>'
            f'<h2 id="{sid}-h">{esc(title)}</h2></div>\n{body}\n  </div>\n</section>')


# ---------------------------------------------------------------- sections

def render_hero(cv):
    p = cv["profile"]
    links = p["links"]
    role, _, focus = p["headline"].partition(" | ")
    proj = next((x for x in cv["selected_projects"] if "metrics" in x), None)
    current = cv["education"][0]

    tiles = ""
    caption = ""
    if proj:
        m = proj["metrics"]
        tiles = "".join(
            f'<div class="metric"><div class="v">{m[key]:g}<span class="u">{unit}</span></div>'
            f'<div class="l">{label}</div></div>'
            for key, unit, label in METRICS if key in m)
        basis = proj.get("metrics_basis", "design metrics")
        caption = (f'<p class="metrics-cap">{esc(proj["name"])} · {esc(proj["program"])} '
                   f'({esc(proj["technology"])}) — {esc(basis)}</p>')
        tiles = f'<div class="metrics" role="group" aria-label="Design metrics">{tiles}</div>'

    focus_html = f'<p class="focus">{esc(focus)}</p>' if focus else ""
    return f"""<section class="hero" id="about" aria-labelledby="name">
  <svg class="trace" viewBox="0 0 360 120" width="360" height="120" aria-hidden="true">
    <line class="target" x1="0" y1="56" x2="360" y2="56"/>
    <path class="step" d="M0 104 H34 V28 H68 V76 H102 V46 H136 V62 H170 V52 H204 V58 H238 V55 H360"/>
  </svg>
  <div class="wrap">
    <div class="hero-grid">
      <img class="photo" src="{PHOTO}" width="{PHOTO_SIZE}" height="{PHOTO_SIZE}" alt="Portrait of {esc(p['name'])}" fetchpriority="high">
      <div>
        <p class="prompt" aria-hidden="true">$ whoami</p>
        <h1 id="name">{esc(p['name'])}</h1>
        <p class="role">{esc(role)}</p>
        {focus_html}
        <p class="meta-row"><span>{icon('pin')} {esc(p['location'])}</span><span>{icon('lab')} {esc(current['lab'])}</span></p>
        <p class="summary">{esc(p['summary'])}</p>
        <div class="btns">
          <a class="btn primary" href="mailto:{esc(p['contact']['email'])}">{icon('mail')} Email</a>
          <a class="btn" href="{url(links['github'])}" target="_blank" rel="noopener">GitHub {icon('out')}</a>
          <a class="btn" href="{url(links['linkedin'])}" target="_blank" rel="noopener">LinkedIn {icon('out')}</a>
          <a class="btn" href="{url(links['google_scholar'])}" target="_blank" rel="noopener">Google Scholar {icon('out')}</a>
        </div>
      </div>
    </div>
    {tiles}
    {caption}
    <div class="research-card">
      <p class="group-label">Current research</p>
      <p class="research-line">{esc(current['research'])}</p>
      <p class="mono-meta">{esc(current['lab'])} · {esc(current['institution'])}</p>
    </div>
  </div>
</section>"""


def render_education(cv):
    cards = []
    for e in sorted(cv["education"], key=lambda x: x["start"], reverse=True):
        facts = [("Advisor", e.get("advisor")), ("GPA", e.get("gpa")), ("Thesis", e.get("thesis"))]
        dl = "".join(f"<dt>{k}</dt><dd>{esc(v)}</dd>" for k, v in facts if v)
        cards.append(
            f'<article class="card"><h3>{esc(e["degree"])} in {esc(e["field"])}</h3>'
            f'<p class="sub">{esc(e["institution"])} · {esc(e["location"])}</p>'
            f'<p class="mono-meta">{span(e["start"], e.get("end"), e.get("expected_end"))}</p>'
            f'<dl class="facts">{dl}</dl></article>')
    return '<div class="cards two">' + "".join(cards) + "</div>"


def render_experience(cv):
    items = []
    for x in sorted(cv["experience"], key=lambda x: x["start"], reverse=True):
        items.append(
            f'<li><h3>{esc(x["role"])}</h3>'
            f'<p class="sub">{esc(x["organization"])} · {esc(x["location"])}</p>'
            f'<p class="mono-meta">{span(x["start"], x.get("end"))}</p>'
            f'{bullets(x.get("highlights"))}</li>')
    return '<ol class="timeline">' + "".join(items) + "</ol>"


def render_projects(cv):
    cards = []
    for p in cv["selected_projects"]:
        tags = [f'<span class="badge">{esc(p["program"])}</span>']
        if p.get("role"):
            tags.append(f'<span class="badge">{esc(p["role"])}</span>')
        tags.append(f'<span class="badge">{esc(p["technology"])}</span>')
        if p.get("dates"):
            tags.append(f'<span class="badge">{esc(slash_range(p["dates"]))}</span>')
        status = (f'<p><span class="badge status {status_class(p["status"])}">{esc(p["status"])}</span></p>'
                  if p.get("status") else "")
        m = p.get("metrics")
        metric_chips = ""
        if m:
            parts = [f'{m["resolution_bits"]}-bit'] + [
                f'{label} {m[key]:g} {unit}' if unit != "bit" else f'{label} {m[key]:g} bit'
                for key, unit, label in METRICS if key in m]
            basis = p.get("metrics_basis", "design metrics")
            metric_chips = f'<p class="mono-meta metric-basis">{esc(basis[:1].upper() + basis[1:])}</p>' + chips(parts)
        buttons = [
            f'<a class="btn" href="{url(p[key])}" target="_blank" rel="noopener">{label} {icon("out")}</a>'
            for key, label in (("tinytapeout_url", "Tiny Tapeout page"), ("url", "Source repository"))
            if p.get(key)]
        link = f'<div class="btns">{"".join(buttons)}</div>' if buttons else ""
        cards.append(
            f'<article class="card"><h3>{esc(p["name"])}</h3>'
            f'<p class="tags">{"".join(tags)}</p>{status}{bullets(p.get("highlights"))}'
            f'{metric_chips}{link}</article>')
    return '<div class="cards">' + "".join(cards) + "</div>"


def render_recognition(cv):
    pubs = []
    for pub in cv["publication"]:
        authors = ", ".join(
            f"<strong>{esc(a)}</strong>" if "Huda" in a else esc(a) for a in pub["authors"])
        pubs.append(
            f'<article class="card"><h3>{esc(pub["title"])}</h3>'
            f'<p class="sub">{authors}</p>'
            f'<p class="mono-meta">{esc(pub["venue"])}'
            f'{"" if str(pub["year"]) in pub["venue"] else ", " + esc(pub["year"])}</p></article>')
    awards = []
    for a in sorted(cv["awards"], key=lambda x: x["year"], reverse=True):
        head = " · ".join(str(v) for v in (a.get("event"), a["year"]) if v)
        body = a.get("project") or a.get("result") or ""
        awards.append(
            f'<article class="card"><h3>{esc(a["name"])}</h3>'
            f'<p class="mono-meta">{esc(head)}</p>'
            f'{f"<p>{esc(body)}</p>" if body else ""}</article>')
    scholar = cv["profile"]["links"]["google_scholar"]
    return ('<p class="group-label">Publication</p><div class="cards">' + "".join(pubs) + "</div>"
            f'<p class="more"><a href="{url(scholar)}" target="_blank" rel="noopener">All publications on Google Scholar {icon("out")}</a></p>'
            '<p class="group-label spaced">Awards</p><div class="cards three">' + "".join(awards) + "</div>")


def render_skills(cv):
    s = cv["skills"]
    groups = [
        ("Analog & mixed-signal", s["analog_mixed_signal"]),
        ("EDA — open source", s["eda"]["open_source"]),
        ("EDA — commercial", s["eda"]["commercial"]),
        ("Design & verification", s["design_and_verification"]),
        ("Programming & HDL", s["programming_and_description"]),
        ("PDK experience", s["pdk_experience"]),
        ("Lab equipment", s["lab_equipment"]),
        ("Languages", [f'{l["language"]} ({l["level"]})' for l in cv["languages"]]),
    ]
    return ('<div class="skills">' + "".join(
        f'<div><p class="group-label">{esc(label)}</p>{chips(items)}</div>' for label, items in groups)
        + "</div>")


def render_contact(cv):
    p = cv["profile"]
    c, links = p["contact"], p["links"]
    return f"""<div class="card contact">
      <ul class="contact-list">
        <li>{icon('mail')} <a href="mailto:{esc(c['email'])}">{esc(c['email'])}</a></li>
        <li>{icon('pin')} {esc(p['location'])}</li>
      </ul>
      <div class="btns">
        <a class="btn primary" href="mailto:{esc(c['email'])}">{icon('mail')} Send an email</a>
        <a class="btn" href="{url(links['github'])}" target="_blank" rel="noopener">GitHub {icon('out')}</a>
        <a class="btn" href="{url(links['linkedin'])}" target="_blank" rel="noopener">LinkedIn {icon('out')}</a>
        <a class="btn" href="{url(links['google_scholar'])}" target="_blank" rel="noopener">Google Scholar {icon('out')}</a>
      </div>
    </div>"""


RENDER = {
    "education": render_education,
    "experience": render_experience,
    "projects": render_projects,
    "recognition": render_recognition,
    "skills": render_skills,
    "contact": render_contact,
}


# ---------------------------------------------------------------- page

LIGHT_VARS = """--bg:#f4f7f9; --bg-soft:#eaf0f4; --card:#ffffff; --line:#d5dee5; --line-strong:#b7c5d0;
    --text:#14212b; --muted:#475a69; --accent:#0a7771; --accent-ink:#ffffff; --accent-soft:rgba(10,119,113,.10);
    --warn:#8a5a00; --ok:#1f7a45; --grid:rgba(10,119,113,.09); --shadow:0 1px 2px rgba(20,33,43,.06);"""

CSS = """
:root{
  color-scheme:dark;
  --bg:#0a1016; --bg-soft:#0e161e; --card:#101a23; --line:#1d2b37; --line-strong:#2a3d4d;
  --text:#dde7ee; --muted:#93a8b8; --accent:#4fd1c5; --accent-ink:#04201e; --accent-soft:rgba(79,209,197,.10);
  --warn:#f2b45c; --ok:#6fd49a; --grid:rgba(79,209,197,.07); --shadow:0 8px 24px rgba(0,0,0,.25);
  --mono:ui-monospace,"SF Mono","JetBrains Mono",Menlo,Consolas,"DejaVu Sans Mono",monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
}
@media (prefers-color-scheme:light){:root:not([data-theme]){color-scheme:light;%%LIGHT%%}}
:root[data-theme="light"]{color-scheme:light;%%LIGHT%%}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 var(--sans);overflow-wrap:anywhere}
a{color:var(--accent);text-underline-offset:3px}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
img{max-width:100%}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-999px;top:8px;z-index:100;background:var(--accent);color:var(--accent-ink);padding:8px 14px;border-radius:6px;font-weight:600}
.skip:focus{left:8px}
.ic{flex:none;vertical-align:-3px}

/* nav */
.nav{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--line)}
@supports (background:color-mix(in srgb,red,blue)){
  .nav{background:color-mix(in srgb,var(--bg) 88%,transparent);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
}
.nav .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:2px 16px;padding-top:8px;padding-bottom:6px}
.brand{margin-right:auto;font:600 14px var(--mono);color:var(--text);text-decoration:none}
.brand b{color:var(--accent);font-weight:600}
.links{order:3;flex:1 0 100%;display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}
.links::-webkit-scrollbar{display:none}
.links a{white-space:nowrap;font:13px var(--mono);color:var(--muted);text-decoration:none;padding:6px 10px;border-radius:6px}
.links a:hover{color:var(--text)}
.links a[aria-current="true"]{color:var(--accent);background:var(--accent-soft)}
.themebtn{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;border:1px solid var(--line-strong);background:var(--card);color:var(--text);cursor:pointer}
.themebtn:hover{border-color:var(--accent);color:var(--accent)}
.themebtn[hidden]{display:none}
.t-moon{display:none}
:root[data-theme="light"] .t-sun{display:none}
:root[data-theme="light"] .t-moon{display:inline}
@media (min-width:900px){.links{order:0;flex:0 1 auto}.nav .wrap{flex-wrap:nowrap;padding-top:8px;padding-bottom:8px}}

/* hero */
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line);padding:48px 0 40px;scroll-margin-top:90px}
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:32px 32px;-webkit-mask-image:linear-gradient(180deg,#000 35%,transparent);mask-image:linear-gradient(180deg,#000 35%,transparent)}
.hero .wrap{position:relative}
.trace{display:none;position:absolute;right:24px;top:34px;opacity:.55;pointer-events:none}
.trace .step{fill:none;stroke:var(--accent);stroke-width:2;stroke-dasharray:900;stroke-dashoffset:900;animation:draw 2.4s ease-out .3s forwards}
.trace .target{stroke:var(--muted);stroke-width:1;stroke-dasharray:3 5;opacity:.7}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes blink{50%{opacity:0}}
@media (min-width:1240px){.trace{display:block}}
.hero-grid{display:grid;gap:26px;align-items:center}
.photo{width:152px;height:152px;border-radius:50%;object-fit:cover;object-position:50% 20%;background:#fff;
  border:2px solid var(--line-strong);box-shadow:0 0 0 6px var(--accent-soft)}
@media (min-width:760px){.hero-grid{grid-template-columns:auto 1fr;gap:44px}.photo{width:204px;height:204px}}
.prompt{margin:0 0 6px;font:14px var(--mono);color:var(--accent)}
.prompt::after{content:"▍";margin-left:6px;animation:blink 1.1s steps(1) infinite}
h1{margin:0 0 8px;font-size:clamp(2rem,5.2vw,3.2rem);line-height:1.1;letter-spacing:-.02em}
.role{margin:0;font-size:1.1rem}
.focus{margin:4px 0 12px;font:600 15px var(--mono);color:var(--accent)}
.meta-row{display:flex;flex-wrap:wrap;gap:4px 20px;margin:0 0 14px;color:var(--muted);font-size:14px}
.summary{max-width:64ch;margin:0}
.btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:9px 14px;border-radius:8px;border:1px solid var(--line-strong);
  background:var(--card);color:var(--text);text-decoration:none;font:600 14px var(--sans)}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.btn.primary:hover{filter:brightness(1.1);color:var(--accent-ink)}
.metrics{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:34px}
@media (min-width:760px){.metrics{grid-template-columns:repeat(4,1fr)}}
.metric{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;box-shadow:var(--shadow)}
.metric .v{font:700 clamp(1.4rem,3.4vw,1.9rem)/1.1 var(--mono);color:var(--accent)}
.metric .u{margin-left:4px;font-size:.55em;font-weight:600;color:var(--muted)}
.metric .l{margin-top:6px;font:12px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.metrics-cap{margin:10px 0 0;font:12px/1.5 var(--mono);color:var(--muted)}
.research-card{margin-top:26px;padding:18px 22px;border:1px solid var(--line-strong);border-left:3px solid var(--accent);border-radius:10px;background:var(--card)}
.research-card .group-label{margin:0 0 6px}
.research-line{margin:0 0 6px;font-size:1.15rem;font-weight:600;line-height:1.4}

/* sections */
section{padding:54px 0 0;scroll-margin-top:96px}
.hero{padding-top:48px}
.sec-head{display:flex;align-items:baseline;gap:12px;margin:0 0 22px}
.sec-head h2{margin:0;font-size:1.5rem;letter-spacing:-.01em}
.sec-head .idx{font:13px var(--mono);color:var(--accent)}
.sec-head::after{content:"";flex:1;height:1px;background:var(--line);align-self:center;order:3}
.cards{display:grid;gap:16px}
@media (min-width:760px){.cards.two{grid-template-columns:1fr 1fr}.cards.three{grid-template-columns:repeat(3,1fr)}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px;box-shadow:var(--shadow)}
.card h3,.timeline h3{margin:0 0 4px;font-size:1.06rem;line-height:1.4}
.card p{margin:6px 0 0}
.sub{color:var(--muted);font-size:15px}
.mono-meta{font:13px/1.5 var(--mono);color:var(--muted)}
.facts{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:14px 0 0;font-size:15px}
.facts dt{padding-top:3px;font:12px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.facts dd{margin:0}
ul.hl{margin:12px 0 0;padding-left:1.1rem}
ul.hl li{margin:4px 0}
.timeline{list-style:none;margin:0;padding:0 0 0 24px;border-left:1px solid var(--line-strong);display:grid;gap:26px}
.timeline>li{position:relative}
.timeline>li::before{content:"";position:absolute;left:-30px;top:.45rem;width:11px;height:11px;border-radius:50%;background:var(--bg);border:2px solid var(--accent)}
.timeline p{margin:2px 0 0}
.tags{display:flex;flex-wrap:wrap;gap:8px}
.badge{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;border:1px solid var(--line-strong);font:12px var(--mono);color:var(--muted)}
.badge.status{align-items:flex-start;border-radius:14px;color:var(--text)}
.badge.status::before{content:"";flex:none;width:7px;height:7px;margin-top:6px;border-radius:50%;background:var(--muted)}
.badge.ok{color:var(--ok);border-color:var(--ok)}.badge.ok::before{background:var(--ok)}
.badge.warn{color:var(--warn);border-color:var(--warn)}.badge.warn::before{background:var(--warn)}
.group-label{margin:0 0 10px;font:600 12px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.group-label.spaced{margin-top:30px}
.more{margin:14px 0 0;font-size:15px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0;padding:0;list-style:none}
.metric-basis{margin:14px 0 -2px}
.skills .chips{margin-top:0}
.chips li{padding:4px 10px;border-radius:6px;border:1px solid var(--line);background:var(--bg-soft);font:13px/1.5 var(--mono)}
.skills{display:grid;gap:26px 32px}
@media (min-width:760px){.skills{grid-template-columns:1fr 1fr}}
.contact-list{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.contact-list .ic{margin-right:6px;color:var(--accent)}

footer{margin-top:64px;padding:26px 0 34px;border-top:1px solid var(--line);color:var(--muted);font:13px var(--mono)}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 20px}
footer a{color:var(--muted)}

@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation:none!important;transition:none!important}
  .trace .step{stroke-dashoffset:0}
}
@media (max-width:420px){.wrap{padding:0 16px}.card{padding:18px}}
@media print{
  :root,:root[data-theme]{--bg:#fff;--bg-soft:#fff;--card:#fff;--line:#ccc;--line-strong:#999;--text:#000;--muted:#333;--accent:#000;--accent-soft:transparent;--grid:transparent;--shadow:none}
  .nav,.trace,.skip,.btns,.prompt,.hero::before{display:none!important}
  body{font-size:11pt}
  section{padding-top:18px}
  .card,.timeline>li,.metric,.research-card{break-inside:avoid}
  a{color:#000;text-decoration:none}
}
"""

HEAD_SCRIPT = (
    "(function(){var r=document.documentElement,t=null;"
    "try{t=localStorage.getItem('theme')}catch(e){}"
    "if(t!=='light'&&t!=='dark'){t=window.matchMedia&&matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'}"
    "r.dataset.theme=t})();"
)

BODY_SCRIPT = """
(function(){
  var root=document.documentElement,btn=document.getElementById('theme-toggle'),
      meta=document.querySelector('meta[name="theme-color"]'),COLORS={dark:'#0a1016',light:'#f4f7f9'};
  function apply(t){
    root.dataset.theme=t;
    if(meta)meta.setAttribute('content',COLORS[t]);
    if(btn)btn.setAttribute('aria-label','Switch to '+(t==='dark'?'light':'dark')+' theme');
  }
  if(btn){
    btn.hidden=false;
    apply(root.dataset.theme==='light'?'light':'dark');
    btn.addEventListener('click',function(){
      var t=root.dataset.theme==='light'?'dark':'light';
      apply(t);
      try{localStorage.setItem('theme',t)}catch(e){}
    });
  }
  var links=[].slice.call(document.querySelectorAll('.links a')),map={};
  links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a});
  function setCurrent(a){
    if(!a||a.getAttribute('aria-current')==='true')return;
    links.forEach(function(l){l.removeAttribute('aria-current')});
    a.setAttribute('aria-current','true');
    var box=a.parentNode;
    if(box.scrollWidth>box.clientWidth)box.scrollLeft=a.offsetLeft-(box.clientWidth-a.offsetWidth)/2;
  }
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(e){if(e.isIntersecting)setCurrent(map[e.target.id])});
    },{rootMargin:'-35% 0px -60% 0px'});
    Object.keys(map).forEach(function(id){var s=document.getElementById(id);if(s)io.observe(s)});
    /* the last section is short: at the very bottom it never reaches the band above */
    window.addEventListener('scroll',function(){
      if(window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-4)setCurrent(links[links.length-1]);
    },{passive:true});
  }
})();
"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='7' fill='%230a1016'/%3E%3Ctext x='16' y='22.5' "
           "font-family='monospace' font-size='18' font-weight='700' text-anchor='middle' "
           "fill='%234fd1c5'%3EH%3C/text%3E%3C/svg%3E")


def json_ld(cv):
    p = cv["profile"]
    e = cv["education"]
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": p["name"],
        "url": SITE_URL,
        "image": SITE_URL + PHOTO,
        "jobTitle": p["headline"].partition(" | ")[0],
        "address": {"@type": "PostalAddress", "addressLocality": p["location"]},
        "affiliation": {"@type": "CollegeOrUniversity", "name": e[0]["institution"]},
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": x["institution"]} for x in e[1:]],
        "sameAs": list(p["links"].values()),
    }
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def first_sentence(text):
    m = re.match(r".+?[.!?](?=\s|$)", text)
    return m.group(0) if m else text


def build(cv):
    p = cv["profile"]
    focus = p["headline"].partition(" | ")[2] or p["headline"]
    title = f'{p["name"]} — {focus}'
    desc = first_sentence(p["summary"])

    nav_links = '<a href="#about">About</a>' + "".join(
        f'<a href="#{sid}">{esc(label)}</a>' for sid, label in SECTIONS)
    body_sections = "\n".join(
        section(i, sid, label, RENDER[sid](cv)) for i, (sid, label) in enumerate(SECTIONS, start=1))

    css = CSS.replace("%%LIGHT%%", LIGHT_VARS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<!-- GENERATED by build.py from cv.json. Edit those, not this file. -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{esc(p['name'])}">
<meta name="theme-color" content="#0a1016">
<link rel="canonical" href="{SITE_URL}">
<link rel="icon" href="{FAVICON}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:image" content="{SITE_URL}{PHOTO}">
<meta name="twitter:card" content="summary">
<script>{HEAD_SCRIPT}</script>
<style>{css}</style>
<script type="application/ld+json">
{json_ld(cv)}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="#about"><b>huda</b>@whoami:~$</a>
    <nav class="links" aria-label="Sections">{nav_links}</nav>
    <button class="themebtn" id="theme-toggle" type="button" aria-label="Switch theme" hidden>
      <svg class="t-sun" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS['sun']}</svg>
      <svg class="t-moon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS['moon']}</svg>
    </button>
  </div>
</header>
<main id="main">
{render_hero(cv)}
{body_sections}
</main>
<footer>
  <div class="wrap">
    <span>© {esc(p['name'])} · {esc(p['location'])}</span>
    <a href="#about">Back to top ↑</a>
  </div>
</footer>
<script>{BODY_SCRIPT}</script>
</body>
</html>
"""


def main():
    cv = json.loads((ROOT / "cv.json").read_text(encoding="utf-8"))
    out = ROOT / "index.html"
    out.write_text(build(cv), encoding="utf-8", newline="\n")
    print(f"wrote {out.name} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    sys.exit(main())
