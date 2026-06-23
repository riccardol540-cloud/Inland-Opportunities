"""Generate the INLAND Angola pitch HTML and overview HTML from the deck data."""
import html
from build_presentation import STORIES, INTRO, TRACKS

CSS = """
:root{--bg:#F9F4EE;--fg:#000;--accent:#400505;--muted:#5c5c5c;--ref:#857f76;--rule:#d8d2ca;--dark:#0e0e0e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:Baskerville,'Times New Roman',Georgia,serif;line-height:1.6}
.label{font-family:Fraunces,Georgia,serif;letter-spacing:.12em;text-transform:uppercase;font-size:.72rem;color:var(--muted)}
.wrap{max-width:1000px;margin:0 auto;padding:0 40px}
h1,h2,h3{font-weight:600;margin:0}
hr{border:0;border-top:1px solid var(--fg);margin:18px 0 30px}
.hero{min-height:78vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:60px 20px}
.hero .mark{font-family:Fraunces,Georgia,serif;font-weight:600;letter-spacing:.35em;font-size:2rem}
.hero h1{font-size:5rem;margin:.3em 0 .15em}
.hero .rule{width:120px;border-top:1px solid var(--fg);margin:14px 0 22px}
.hero .sub{font-size:1.4rem;color:var(--muted)}
.hero .meta{margin-top:34px}
section{padding:46px 0}
section.dark{background:var(--dark);color:#fff}
section.dark .label{color:#999}
.sec-h{font-size:2.4rem;margin:.2em 0}
.lead{font-size:1.18rem;max-width:46ch}
.muted{color:var(--muted)}
.cats{display:flex;flex-wrap:wrap;gap:10px 30px;margin-top:18px}
.cats div{display:flex;justify-content:space-between;min-width:240px;border-bottom:1px solid var(--rule);padding:6px 0}
.cats b{color:var(--accent)}
.stat{display:inline-block;margin-right:48px}
.stat .n{font-size:4.5rem;color:var(--accent);line-height:1}
.story{padding:30px 0;border-top:1px solid var(--rule)}
.story .top{display:flex;justify-content:space-between;align-items:baseline}
.story .num{font-size:2.6rem;color:var(--accent)}
.story h3{font-size:1.9rem}
.story .st{font-style:italic;color:var(--muted);font-size:1.2rem;margin:.1em 0 .2em}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:34px;margin-top:14px}
.cols .label{display:block;margin-bottom:6px}
.foot{margin-top:14px;font-size:.85rem;color:var(--ref)}
.tags{margin-top:8px}
.tag{font-family:Fraunces,Georgia,serif;font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);border:1px solid #b0a89e;border-radius:20px;padding:3px 10px;margin-right:8px;white-space:nowrap}
.tracks{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;margin-top:24px}
.track .bar{height:3px;margin-bottom:12px}
.track h3{font-size:1.4rem}
.track .ts{font-family:Fraunces,Georgia,serif;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:6px 0 10px}
.track .meta{margin-top:14px;font-family:Fraunces,Georgia,serif;font-size:.66rem;color:var(--ref);line-height:1.7}
.partner{display:grid;grid-template-columns:200px 1fr;gap:10px 28px;margin-top:20px}
.partner .h{font-family:Fraunces,Georgia,serif;text-transform:uppercase;letter-spacing:.08em;font-size:.8rem;color:var(--accent);font-weight:600;padding-top:3px}
.center{text-align:center}
.dark h2{font-size:3rem}
@media(max-width:760px){.cols,.tracks,.partner{grid-template-columns:1fr}.hero h1{font-size:3.2rem}}
"""

CATCOLORS = {0:"#2C5F2D",1:"#B85042",2:"#5B2C6F"}

def esc(s): return html.escape(str(s))

def story_html(i,s):
    tags="".join(f'<span class="tag">{esc(t)}</span>' for t in s.tags)
    return f"""<div class="story">
  <div class="top"><div><div class="label">{esc(s.category)}</div>
  <h3>{esc(s.headline)}</h3><div class="st">{esc(s.subtitle)}</div></div>
  <div class="num">{i+1:02d}</div></div>
  <div class="cols">
    <div><span class="label">The story</span>{esc(s.hook)}</div>
    <div><span class="label">Our proposal</span>{esc(s.proposal)}</div>
  </div>
  <div class="tags">{tags}</div>
  <div class="foot">Places: {esc(s.places)} &nbsp;·&nbsp; Sources: {esc(s.reference)}</div>
</div>"""

def tracks_html():
    out=[]
    for j,t in enumerate(TRACKS):
        out.append(f"""<div class="track">
  <div class="bar" style="background:{CATCOLORS[j]}"></div>
  <h3 style="color:{CATCOLORS[j]}">{esc(t['name'])}</h3>
  <div class="ts">{esc(t['stories'])}</div>
  <div>{esc(t['desc'])}</div>
  <div class="meta">Geography: {esc(t['geography'])}<br>Season: {esc(t['season'])}<br>{esc(t['story_count'])}</div>
</div>""")
    return "".join(out)

PARTNERS=[("European partner","INLAND — yearly publication (Italy / EU). Editorial, photography and publishing; presentation of the work in Europe."),
("African partner","An Angolan cultural organisation (lead candidate: Lueji A’Nkonde University, Lunda Norte — which coordinated the sona UNESCO nomination) — co-creation, community access, custodian liaison, presentation in Angola."),
("Funding path","Mobility grant (≤€4,000) funds the scouting trip; the Visual Arts grant funds collaborative production and a public presentation in Angola and Europe."),
("The principle","Made with custodians, not about them — equitable Africa–Europe co-creation, exactly the dialogue the Goethe programme exists to fund.")]

def partner_html():
    return "".join(f'<div class="h">{esc(h)}</div><div>{esc(b)}</div>' for h,b in PARTNERS)

PITCH=f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>INLAND Angola — Africa–Europe Co-Production</title><style>{CSS}</style></head>
<body>
<div class="hero">
  <div class="mark">INLAND</div>
  <h1>Angola</h1><div class="rule"></div>
  <div class="sub">An Africa–Europe Cultural Co-Production</div>
  <div class="meta label">12 Selected Stories · Goethe-Institut Africa–Europe Partnerships for Culture · 2026</div>
</div>

<section><div class="wrap"><div class="label">About</div><h2 class="sec-h">About INLAND</h2><hr>
<p class="lead">{esc(INTRO['about'])}</p><p class="muted">{esc(INTRO['about_method'])}</p></div></section>

<section style="background:#fff"><div class="wrap"><div class="label">The Research</div><h2 class="sec-h">Angola — What Survived</h2><hr>
<p class="lead">{esc(INTRO['research'])}</p><p class="muted">{esc(INTRO['research_scope'])}</p>
<p><span class="stat"><span class="n">17</span><br><span class="label">story leads researched</span></span>
<span class="stat"><span class="n">12</span><br><span class="label">selected for this round</span></span></p></div></section>

<section><div class="wrap"><div class="label">Editorial Angle</div><h2 class="sec-h">Our Angle</h2><hr>
<p class="lead">{esc(INTRO['angle'])}</p><p class="muted">{esc(INTRO['angle_why'])}</p>
<div class="cats">{''.join(f'<div><span>{esc(c)}</span><b>{n}</b></div>' for c,n in INTRO['categories'])}</div></div></section>

<section class="dark center"><div class="wrap"><div class="label">Part Two</div><h2>The Storylines</h2>
<p class="lead" style="margin:14px auto 0;max-width:60ch">Twelve selected stories across art, ritual, governance, food, pastoral life and memory. Each centres a custodian, a specific place, and a practice that can still be witnessed.</p></div></section>

<section><div class="wrap">{''.join(story_html(i,s) for i,s in enumerate(STORIES))}</div></section>

<section style="background:#fff"><div class="wrap"><div class="label">Three Tracks</div><h2 class="sec-h">Production Tracks</h2><hr>
<div class="tracks">{tracks_html()}</div>
<p class="foot" style="margin-top:20px">Signature: <b>Offerings to Kianda</b> (Festa da Ilha, November) runs across the project; the <b>Mbanza Kongo lumbu</b> and <b>Njinga’s footprints</b> form a Kingdoms-and-Memory strand.</p></div></section>

<section><div class="wrap"><div class="label">The Partnership</div><h2 class="sec-h">An Equitable Co-Production</h2><hr>
<div class="partner">{partner_html()}</div></div></section>

<section class="dark center"><div class="wrap"><h2>12 Storylines. One Angola.</h2>
<div class="rule" style="margin:18px auto;width:120px;border-color:#fff"></div>
<div class="label">An Africa–Europe co-production proposal by INLAND</div></div></section>
</body></html>"""

OVERVIEW=f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>INLAND Angola — Overview</title><style>{CSS}
@page{{size:A4;margin:18mm 16mm}}
body{{font-size:10.5pt}} .hero{{min-height:auto;padding:0 0 14px}}
.hero h1{{font-size:3rem}} section{{padding:14px 0}} .wrap{{padding:0}}
.sec-h{{font-size:1.5rem}} .story{{padding:10px 0;break-inside:avoid}}
.story h3{{font-size:1.1rem}} .cols{{gap:18px;margin-top:6px;font-size:9.5pt}}
.lead{{font-size:11pt;max-width:none}} .num{{font-size:1.4rem!important}}
.tags{{display:none}} section.dark{{background:#fff;color:#000}} .dark h2{{font-size:1.5rem;color:var(--accent)}}
.dark .label{{color:var(--muted)}}
</style></head>
<body><div class="wrap">
<div class="hero"><div class="mark label" style="font-size:1rem">INLAND</div>
<h1>Angola</h1><div class="sub" style="font-size:1.1rem">An Africa–Europe Cultural Co-Production · Overview</div>
<div class="label">Goethe-Institut Africa–Europe Partnerships for Culture · 2026</div></div>
<hr>
<p class="lead">{esc(INTRO['research'])}</p>
<p class="muted" style="font-size:10pt">{esc(INTRO['angle'])}</p>
<div class="cats">{''.join(f'<div><span>{esc(c)}</span><b>{n}</b></div>' for c,n in INTRO['categories'])}</div>
<h2 class="sec-h" style="margin-top:18px">The 12 Storylines</h2><hr>
{''.join(story_html(i,s) for i,s in enumerate(STORIES))}
<h2 class="sec-h" style="margin-top:14px">Production Tracks</h2><hr>
<div class="tracks">{tracks_html()}</div>
<h2 class="sec-h" style="margin-top:16px">The Partnership</h2><hr>
<div class="partner">{partner_html()}</div>
</div></body></html>"""

open("INLAND_Angola_Pitch.html","w").write(PITCH)
open("INLAND_Angola_Overview.html","w").write(OVERVIEW)
print("wrote pitch + overview HTML")
