"""
INLAND shared web renderer — the canonical Kashmir-quality HTML deck.

Every edition's pitch + overview HTML is produced here so each one looks like
INLAND. Do NOT hand-roll minified CSS in an edition's generate_web.py; import
this module instead. The visual gold standard is REFERENCE_INLAND_pitch.html
in this folder (the original Kashmir pitch).

Output is fully self-contained: Google Fonts via CDN, inline CSS + JS, inline
INLAND logo SVG. The pitch is a full-screen scroll-snap slide deck (reveal
animations, animated stat counters, per-story Story/Proposal toggle on mobile,
nav counter + progress bar). The overview is a print/A4 single document in the
same house style (it feeds the Overview PDF).

────────────────────────────────────────────────────────────────────────────
Data contract — `cfg` dict passed to build_pitch / build_overview / write_edition
────────────────────────────────────────────────────────────────────────────
  territory         str   e.g. "Rwanda"  (used in headings, filenames, title)
  intro             dict  keys: about, about_method, research, research_scope,
                          angle, angle_why, categories  (categories = list of
                          (name, count) tuples)  — exactly the INTRO dict an
                          edition's build_presentation.py already defines.
  stories           list  of Story dataclass instances with attributes:
                          headline, subtitle, hook, proposal, category, tags
                          (list[str]), pull_quote, places, reference.
  tracks            list  of dicts: name, stories, desc, geography, season,
                          story_count.
  partners          list  of (heading, body) tuples.
  leads_researched  int   total leads researched (the big stat; "selected"
                          defaults to len(stories)).
  subtitle          str   optional, default "An Africa–Europe Cultural Co-Production".
  meta              str   optional title-slide meta line; sensible default.
  breaker_sub       str   optional storylines breaker blurb; sensible default.
  tracks_note       str   optional HTML rendered under the tracks (Angola uses
                          this for its "Signature:" line). Omit for none.
  title             str   optional <title>; default "INLAND <territory> — …".

Editions consume it via a thin shim (see editions/*/generate_web.py).
"""

import html
import pathlib

FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Cormorant:ital,wght@0,600;1,600&'
    'family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&'
    'family=Fraunces:wght@400;600&display=swap" rel="stylesheet">'
)

# INLAND wordmark — inline so the deck has no external image dependency.
_LOGO_PATHS = (
    '<g transform="translate(0, 0.14)"><path d="M2.17623 0C2.09433 0.198902 2.04753 0.391954 2.03583 0.579156C2.02413 0.766358 2.01828 0.906759 2.01828 1.00036V11.6709C2.01828 12.0453 2.02413 12.3495 2.03583 12.5835C2.05923 12.8175 2.08848 13.0047 2.12358 13.1451H0.0526506C0.0760509 13.0398 0.0936013 12.8935 0.105301 12.7063C0.117002 12.5074 0.122852 12.2208 0.122852 11.8464V1.24606C0.122852 0.91846 0.111151 0.661057 0.0877512 0.473854C0.0643508 0.274953 0.0351005 0.117001 0 0H2.17623Z"/></g>'
    '<g transform="translate(4.73, 0.017)"><path d="M0 0H2.36928L10.0036 10.4073V13.2855L0 0ZM0 13.2679H1.42157C1.11737 13.0339 0.848262 12.7707 0.614259 12.4782C0.380255 12.1857 0.175502 11.8873 0 11.5831V13.2679ZM10.0036 0H8.58207C8.88627 0.234002 9.15538 0.497255 9.38938 0.789759C9.62338 1.08226 9.82813 1.38062 10.0036 1.68482V0Z"/></g>'
    '<g transform="translate(17.56, 0.035)"><path d="M2.19378 0C2.11188 0.198902 2.06508 0.397805 2.05338 0.596707C2.04168 0.783909 2.03583 0.92431 2.03583 1.01791V11.7586C2.03583 12.133 2.04168 12.4372 2.05338 12.6712C2.06508 12.9052 2.08848 13.0983 2.12358 13.2504H0.0526505C0.0760508 13.1451 0.0936009 12.993 0.105301 12.7941C0.117001 12.5952 0.122853 12.3085 0.122853 11.9341V1.26361C0.122853 0.924311 0.111151 0.661058 0.0877509 0.473855C0.0643506 0.274953 0.0351005 0.117001 0 0H2.19378ZM8.52942 13.2504H7.1254C7.4296 13.0164 7.69286 12.759 7.91516 12.4782C8.14916 12.1857 8.35392 11.8815 8.52942 11.5656V13.2504Z"/></g>'
    '<g transform="translate(27.93, 0)"><path d="M7.93271 13.2855C7.93271 13.2738 7.93856 13.2562 7.95026 13.2328C7.96196 13.2094 7.96781 13.186 7.96781 13.1626C7.95611 13.1041 7.93856 13.0105 7.91516 12.8818C7.89176 12.7531 7.8157 12.484 7.687 12.0745L7.24825 10.7232C7.20145 10.5945 7.14295 10.419 7.07274 10.1967C7.00254 9.97436 6.91479 9.69941 6.80949 9.3718L6.54624 8.54694C6.52284 8.51184 6.47019 8.37144 6.38828 8.12574C6.24788 7.71624 6.10163 7.30088 5.94953 6.87968C5.80913 6.45847 5.66872 6.06067 5.52832 5.68626C5.39962 5.30016 5.28262 4.955 5.17732 4.6508C5.07202 4.3466 4.98427 4.1126 4.91407 3.94879C4.89067 3.86689 4.85557 3.76159 4.80877 3.63289C4.76197 3.50419 4.70931 3.35209 4.65081 3.17658L4.29981 2.24643L4.82632 0.807309C4.86142 0.713708 4.90237 0.596707 4.94917 0.456305C5.00767 0.315904 5.06617 0.163802 5.12467 0C5.22997 0.315904 5.39377 0.783909 5.61607 1.40402C5.85008 2.02412 6.13088 2.77293 6.45849 3.65044C6.78609 4.51625 7.15465 5.49906 7.56415 6.59887C7.98536 7.69868 8.44167 8.8804 8.93307 10.144C9.07347 10.5184 9.21387 10.8928 9.35428 11.2672C9.49468 11.6299 9.62923 11.9985 9.75793 12.3729C9.82813 12.5484 9.89833 12.718 9.96854 12.8818C10.0504 13.0339 10.1265 13.1685 10.1967 13.2855H7.93271ZM0.754661 11.3725V11.355L0 13.2855H0.754661H1.31627H2.42193C2.04753 13.0164 1.72577 12.718 1.45667 12.3904C1.18757 12.0628 0.953563 11.7235 0.754661 11.3725Z"/></g>'
    '<g transform="translate(40.59, 0.017)"><path d="M0 0H2.36928L10.0036 10.4073V13.2855L0 0ZM0 13.2679H1.42157C1.11737 13.0339 0.848263 12.7707 0.614259 12.4782C0.380256 12.1857 0.175502 11.8873 0 11.5831V13.2679ZM10.0036 0H8.58207C8.88627 0.234002 9.15538 0.497255 9.38938 0.789759C9.62338 1.08226 9.82814 1.38062 10.0036 1.68482V0Z"/></g>'
    '<g transform="translate(51.96, 0)"><path d="M9.02082 1.49177C10.5535 2.67348 11.3199 4.3583 11.3199 6.54622C11.3199 8.02044 10.9864 9.28405 10.3195 10.3371C9.64093 11.4486 8.64642 12.2559 7.336 12.759C7.3126 12.7707 7.29505 12.7765 7.28335 12.7765C7.28335 12.7765 7.27165 12.7824 7.24825 12.7941C7.75136 12.2325 8.16086 11.4544 8.47676 10.4599C8.79267 9.45371 8.95062 8.14914 8.95062 6.54622C8.95062 4.10089 8.57037 2.29322 7.80986 1.12321C7.71625 0.971111 7.59925 0.813159 7.45885 0.649357C8.06726 0.85996 8.58792 1.14076 9.02082 1.49177ZM2.19378 0C2.11188 0.198902 2.06508 0.397805 2.05338 0.596706C2.04168 0.783909 2.03583 0.92431 2.03583 1.01791V11.7937C2.03583 12.1681 2.04168 12.4723 2.05338 12.7063C2.07678 12.9403 2.10603 13.1334 2.14113 13.2855H0.0526505C0.0760508 13.1802 0.0936009 13.0281 0.105301 12.8292C0.117001 12.6186 0.122854 12.3261 0.122854 11.9517V1.26361C0.122854 0.92431 0.111151 0.661057 0.0877509 0.473855C0.0643506 0.274953 0.0351005 0.117001 0 0H2.19378Z"/></g>'
)

ACCENT_ABOUT = "Intimacy with custodians, not thematic surveys."
TRACK_COLOR_CLASSES = ["blue", "green", "purple"]

# ── Pitch CSS (ported verbatim from the Kashmir deck, plus a partner grid) ──
PITCH_CSS = """
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  :root {
    --bg: #F9F4EE; --fg: #000000; --accent: #400505;
    --muted: rgba(0,0,0,0.58); --muted-soft: rgba(0,0,0,0.38);
    --divider: rgba(0,0,0,0.18); --divider-light: rgba(0,0,0,0.1);
    --dark-bg: #0e0e0e; --dark-fg: #ffffff; --tag-border: #B0A89E;
    --font-heading: 'Cormorant', Georgia, serif;
    --font-body: 'Cormorant Garamond', Georgia, serif;
    --font-label: 'Fraunces', sans-serif;
    --track-blue: #1B4965; --track-green: #3A5A40; --track-purple: #5B2C6F;
  }
  html { scroll-snap-type: y mandatory; overflow-x: hidden; background: var(--bg);
    -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
  body { background: var(--bg); color: var(--fg); font-family: var(--font-body); }

  .slide { width: 100vw; height: 100vh; scroll-snap-align: start; display: flex;
    flex-direction: column; justify-content: center; padding: 60px 80px;
    position: relative; overflow: hidden; }
  .slide--dark { background: var(--dark-bg); color: var(--dark-fg); }

  .reveal { opacity: 0; transform: translateY(36px);
    transition: opacity 0.7s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
  .reveal.visible { opacity: 1; transform: translateY(0); }
  .reveal-title { opacity: 0; clip-path: inset(0 0 100% 0); transform: translateY(24px);
    transition: clip-path 0.8s cubic-bezier(0.77, 0, 0.175, 1),
      transform 0.8s cubic-bezier(0.77, 0, 0.175, 1), opacity 0.6s ease; }
  .reveal-title.visible { opacity: 1; clip-path: inset(0 0 0% 0); transform: translateY(0); }
  .reveal-line { transform: scaleX(0); transform-origin: left;
    transition: transform 1s cubic-bezier(0.16, 1, 0.3, 1); }
  .reveal-line.visible { transform: scaleX(1); }
  .reveal-scale { opacity: 0; transform: scale(0.82);
    transition: opacity 0.9s ease, transform 1.1s cubic-bezier(0.16, 1, 0.3, 1); }
  .reveal-scale.visible { opacity: 1; transform: scale(1); }
  .reveal-vline { transform: scaleY(0); transform-origin: top;
    transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
  .reveal-vline.visible { transform: scaleY(1); }
  .d1{transition-delay:.08s}.d2{transition-delay:.16s}.d3{transition-delay:.24s}
  .d4{transition-delay:.32s}.d5{transition-delay:.4s}.d6{transition-delay:.5s}
  .d7{transition-delay:.6s}.d8{transition-delay:.7s}.d9{transition-delay:.8s}
  .d10{transition-delay:.9s}

  .label { font-family: var(--font-label); font-size: 11px; font-weight: 400;
    text-transform: uppercase; letter-spacing: 0.14em; color: var(--muted); }
  .heading-xl { font-family: var(--font-heading); font-weight: 600;
    font-size: clamp(52px, 5.5vw, 72px); line-height: 1.05; }
  .heading-lg { font-family: var(--font-heading); font-weight: 600;
    font-size: clamp(32px, 3.2vw, 42px); line-height: 1.15; }
  .heading-story { font-family: var(--font-heading); font-weight: 600;
    font-size: clamp(30px, 3.2vw, 42px); line-height: 1.15; }
  .subtitle-story { font-family: var(--font-heading); font-weight: 600; font-style: italic;
    font-size: clamp(18px, 2vw, 26px); line-height: 1.3; color: var(--muted); margin-top: 8px; }
  .body-text { font-family: var(--font-body); font-weight: 400;
    font-size: clamp(16px, 1.4vw, 20px); line-height: 1.65; max-width: 720px; }
  .body-secondary { font-family: var(--font-body); font-weight: 400;
    font-size: clamp(15px, 1.2vw, 18px); line-height: 1.6; color: var(--muted);
    max-width: 720px; margin-top: 20px; }
  .accent-text { font-family: var(--font-heading); font-weight: 600; font-style: italic;
    color: var(--accent); font-size: clamp(20px, 2vw, 26px); line-height: 1.35; }
  .divider { width: 100%; height: 1px; background: var(--divider); margin: 24px 0; }
  .divider--short { width: 160px; margin: 24px auto; }
  .divider--white { background: rgba(255,255,255,0.2); }

  .stat-num { font-family: var(--font-heading); font-weight: 600; font-size: 80px;
    line-height: 1; color: var(--accent); }
  .stat-label { font-family: var(--font-label); font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--muted); margin-top: 6px; }

  .story-num { font-family: var(--font-heading); font-weight: 600;
    font-size: clamp(48px, 5vw, 68px); color: var(--accent); line-height: 1;
    position: absolute; top: 56px; right: 80px; }

  .tag-row { display: flex; gap: 8px; flex-wrap: wrap; }
  .tag { font-family: var(--font-label); font-size: 9px; font-weight: 400;
    text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted);
    border: 1px solid var(--tag-border); border-radius: 20px; padding: 4px 14px; white-space: nowrap; }

  .logo-svg { width: clamp(180px, 18vw, 240px); height: auto; display: block; }
  .logo-svg--sm { width: clamp(100px, 10vw, 140px); height: auto; display: block; margin: 0 auto; }

  .slide--title { text-align: center; align-items: center; }
  .slide--title .subtitle { font-family: var(--font-body); font-size: clamp(16px, 1.3vw, 20px);
    color: var(--muted); margin-top: 8px; }
  .slide--title .meta { font-family: var(--font-label); font-size: 11px; letter-spacing: 0.12em;
    color: var(--muted-soft); text-transform: uppercase; margin-top: 48px; }

  .slide--breaker { text-align: center; align-items: center; background: var(--dark-bg); color: var(--dark-fg); }
  .breaker-label { font-family: var(--font-label); font-size: 11px; font-weight: 400;
    text-transform: uppercase; letter-spacing: 0.2em; color: rgba(255,255,255,0.35); }
  .breaker-heading { font-family: var(--font-heading); font-weight: 600;
    font-size: clamp(40px, 4.5vw, 60px); line-height: 1.1; color: var(--dark-fg); margin-top: 12px; }
  .breaker-sub { font-family: var(--font-body); font-size: clamp(16px, 1.3vw, 20px);
    color: rgba(255,255,255,0.45); max-width: 600px; line-height: 1.55; margin-top: 20px; }

  .intro-layout { display: flex; gap: 80px; align-items: flex-start; width: 100%; }
  .intro-main { flex: 1; min-width: 0; }
  .intro-side { flex: 0 0 300px; padding-top: 4px; }
  .category-list { display: flex; flex-direction: column; }
  .category-item { font-family: var(--font-body); font-size: 17px; padding: 10px 0;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--divider-light); opacity: 0; transform: translateX(-20px);
    transition: opacity 0.5s ease, transform 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
  .category-item:first-child { border-top: 1px solid var(--divider); }
  .category-item:last-child { border-bottom: 1px solid var(--divider); }
  .category-item.visible { opacity: 1; transform: translateX(0); }
  .category-count { font-family: var(--font-body); font-weight: 600; font-size: 17px; color: var(--accent); }
  .stat-block { display: flex; flex-direction: column; gap: 40px; }

  .index-list { list-style: none; width: min(700px, 80%); margin-top: 16px; }
  .index-item { display: flex; align-items: baseline; gap: 24px; padding: 16px 0;
    border-bottom: 1px solid var(--divider-light); }
  .index-item:last-child { border-bottom: none; }
  .index-num { font-family: var(--font-heading); font-weight: 600; font-size: 28px;
    color: var(--accent); min-width: 40px; }
  .index-title { font-family: var(--font-body); font-size: 22px; color: var(--fg); }

  .slide--story { justify-content: flex-start; padding-top: 72px; }
  .story-header { margin-top: 20px; }
  .story-content { display: flex; gap: 48px; width: 100%; align-items: flex-start; }
  .story-main { flex: 1; min-width: 0; }
  .story-quote { flex: 0 0 280px; display: flex; gap: 16px; align-items: stretch; padding-top: 4px; }
  .quote-bar { width: 2px; min-height: 60px; background: var(--accent); flex-shrink: 0; align-self: stretch; }
  .quote-text { font-family: var(--font-heading); font-weight: 600; font-style: italic;
    font-size: clamp(17px, 1.5vw, 21px); line-height: 1.4; color: var(--accent); }
  .story-angle { font-family: var(--font-body); font-size: clamp(15px, 1.3vw, 18px);
    line-height: 1.65; color: var(--fg); margin-top: 28px; }
  .story-angle-pill { display: inline-block; font-family: var(--font-label); font-size: 9px;
    text-transform: uppercase; letter-spacing: 0.1em; color: rgba(0,0,0,0.5);
    background: rgba(0,0,0,0.06); border: 1px solid rgba(0,0,0,0.15); border-radius: 3px;
    padding: 3px 8px; margin-bottom: 8px; white-space: nowrap; }
  .story-places { font-family: var(--font-label); font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--muted); margin-top: 20px; }
  .story-toggle { display: none; gap: 8px; margin-bottom: 12px; }
  .story-toggle-btn { font-family: var(--font-label); font-size: 9px; text-transform: uppercase;
    letter-spacing: 0.1em; color: rgba(0,0,0,0.4); background: rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.12); border-radius: 3px; padding: 5px 12px; cursor: pointer;
    transition: all 0.2s ease; }
  .story-toggle-btn.active { color: #ffffff; background: #0e0e0e; border-color: #0e0e0e; }
  .story-footer { position: absolute; bottom: 48px; left: 80px; right: 80px;
    display: flex; justify-content: space-between; align-items: flex-end; }
  .story-ref { font-family: var(--font-label); font-size: 9px; letter-spacing: 0.08em; color: var(--muted-soft); }

  .tracks-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; width: 100%; margin-top: 8px; }
  .track-card { border-top: 3px solid var(--accent); padding: 28px 0 0; }
  .track-card--blue { border-color: var(--track-blue); }
  .track-card--green { border-color: var(--track-green); }
  .track-card--purple { border-color: var(--track-purple); }
  .track-name { font-family: var(--font-heading); font-weight: 600; font-size: clamp(22px, 2.2vw, 28px);
    line-height: 1.2; margin-bottom: 4px; }
  .track-card--blue .track-name { color: var(--track-blue); }
  .track-card--green .track-name { color: var(--track-green); }
  .track-card--purple .track-name { color: var(--track-purple); }
  .track-stories { font-family: var(--font-label); font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--muted); margin-top: 12px; }
  .track-desc { font-family: var(--font-body); font-size: clamp(15px, 1.2vw, 17px); line-height: 1.55;
    color: var(--fg); margin-top: 14px; }
  .track-meta { font-family: var(--font-label); font-size: 9px; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--muted-soft); margin-top: 18px; line-height: 1.7; }
  .track-note { font-family: var(--font-body); font-size: 14px; color: var(--muted-soft);
    text-align: center; max-width: 100%; margin-top: 28px; }

  .partner-grid { display: grid; grid-template-columns: 220px 1fr; gap: 18px 40px;
    width: 100%; max-width: 920px; margin-top: 8px; }
  .partner-h { font-family: var(--font-label); text-transform: uppercase; letter-spacing: 0.08em;
    font-size: 12px; color: var(--accent); font-weight: 600; padding-top: 4px; }
  .partner-b { font-family: var(--font-body); font-size: clamp(15px, 1.2vw, 18px); line-height: 1.55; }

  .slide--closing { text-align: center; align-items: center; }
  .closing-headline { font-family: var(--font-heading); font-weight: 600;
    font-size: clamp(36px, 4vw, 52px); line-height: 1.2; color: var(--dark-fg); }
  .closing-tagline { font-family: var(--font-label); font-size: 14px; font-weight: 400;
    letter-spacing: 0.12em; color: rgba(255,255,255,0.4); text-transform: uppercase; }

  .nav-counter { position: fixed; bottom: 24px; right: 32px; font-family: var(--font-label);
    font-size: 11px; color: var(--muted-soft); letter-spacing: 0.08em; z-index: 100;
    transition: color 0.4s ease; }
  .nav-counter--dark { color: rgba(255,255,255,0.3); }
  .progress-bar { position: fixed; top: 0; left: 0; height: 2px; background: var(--accent);
    width: 0%; z-index: 100; transition: width 0.35s ease; }

  @media (max-width: 768px) {
    .slide { padding: 40px 24px; height: auto; min-height: 100vh; }
    .slide--story { padding-top: 56px; padding-bottom: 80px; }
    .intro-layout { flex-direction: column; gap: 40px; }
    .intro-side { flex: none; width: 100%; }
    .story-num { top: 40px; right: 24px; font-size: 40px; }
    .story-content { flex-direction: column; gap: 0; }
    .story-quote { display: none; }
    .story-ref { display: none; }
    .story-places { display: none; }
    .body-text { font-size: 18px; }
    .story-angle { font-size: 18px; display: none; margin-top: 0; }
    .story-angle-pill { display: none; }
    .body-text .story-angle-pill { display: none; }
    .story-toggle { display: flex; margin-bottom: 6px; }
    .story-toggle-active .body-text { display: none; }
    .story-toggle-active .story-angle { display: block; }
    .story-footer { position: absolute; bottom: 24px; left: 24px; right: 24px;
      justify-content: flex-start; flex-wrap: wrap; gap: 8px; }
    .tracks-grid { grid-template-columns: 1fr; gap: 32px; }
    .partner-grid { grid-template-columns: 1fr; gap: 6px 0; }
    .partner-h { padding-top: 14px; }
    .nav-counter { bottom: 16px; right: 16px; }
    .stat-num { font-size: 56px; }
  }
  ::-webkit-scrollbar { width: 0; background: transparent; }
  html { scrollbar-width: none; }
"""

PITCH_JS = """
(function() {
  const slides = document.querySelectorAll('.slide');
  const counter = document.getElementById('navCounter');
  const progressBar = document.getElementById('progressBar');
  const total = slides.length;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const slide = entry.target;
        slide.querySelectorAll('.reveal, .reveal-title, .reveal-line, .reveal-scale, .reveal-vline')
          .forEach(el => el.classList.add('visible'));
        slide.querySelectorAll('.category-item').forEach(el => el.classList.add('visible'));
        const idx = Array.from(slides).indexOf(slide);
        counter.textContent = (idx + 1) + ' / ' + total;
        const isDark = slide.dataset.theme === 'dark';
        counter.classList.toggle('nav-counter--dark', isDark);
        progressBar.style.width = (((idx + 1) / total) * 100) + '%';
        progressBar.style.background = isDark ? 'rgba(255,255,255,0.3)' : 'var(--accent)';
        slide.querySelectorAll('[data-count]').forEach(el => {
          if (!el.dataset.counted) { el.dataset.counted = 'true'; animateCounter(el, parseInt(el.dataset.count)); }
        });
      } else {
        entry.target.querySelectorAll('.reveal, .reveal-title, .reveal-line, .reveal-scale, .reveal-vline')
          .forEach(el => el.classList.remove('visible'));
        entry.target.querySelectorAll('.category-item').forEach(el => el.classList.remove('visible'));
        entry.target.querySelectorAll('[data-count]').forEach(el => { el.dataset.counted = ''; el.textContent = '0'; });
      }
    });
  }, { threshold: 0.35 });
  slides.forEach(s => observer.observe(s));
  function animateCounter(el, target, duration) {
    duration = duration || 1200; var start = null;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  let current = 0;
  function goTo(i) { if (i < 0 || i >= total) return; current = i; slides[current].scrollIntoView({ behavior: 'smooth' }); }
  document.addEventListener('keydown', (e) => {
    if (['ArrowDown','ArrowRight',' '].includes(e.key)) { e.preventDefault(); goTo(current + 1); }
    else if (['ArrowUp','ArrowLeft','Backspace'].includes(e.key)) { e.preventDefault(); goTo(current - 1); }
  });
  const scrollObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => { if (entry.isIntersecting) current = Array.from(slides).indexOf(entry.target); });
  }, { threshold: 0.55 });
  slides.forEach(s => scrollObs.observe(s));
  document.querySelectorAll('.story-toggle-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const main = this.closest('.story-main');
      main.querySelectorAll('.story-toggle-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      main.classList.toggle('story-toggle-active', this.dataset.show === 'proposal');
    });
  });
})();
"""


def esc(s):
    return html.escape(str(s))


def _logo(cls):
    return (
        f'<svg class="{cls}" viewBox="0 0 63.28 13.29" fill="currentColor" '
        f'xmlns="http://www.w3.org/2000/svg">{_LOGO_PATHS}</svg>'
    )


def _story_slide(i, s):
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in s.tags)
    quote = ""
    if getattr(s, "pull_quote", ""):
        quote = (
            '<div class="story-quote">'
            '<div class="quote-bar reveal-vline d4"></div>'
            f'<div class="quote-text reveal d5">“{esc(s.pull_quote)}”</div></div>'
        )
    return f"""
<section class="slide slide--story" data-theme="light">
  <div class="story-num reveal d1">{i + 1:02d}</div>
  <div class="label reveal">{esc(s.category)}</div>
  <div class="story-header">
    <h2 class="heading-story reveal reveal-title d1">{esc(s.headline)}</h2>
    <div class="subtitle-story reveal d2">{esc(s.subtitle)}</div>
  </div>
  <div class="divider reveal-line d3"></div>
  <div class="story-content">
    <div class="story-main">
      <div class="story-toggle"><button class="story-toggle-btn active" data-show="story">The Story</button><button class="story-toggle-btn" data-show="proposal">Our Proposal</button></div>
      <div class="body-text reveal d4"><span class="story-angle-pill">The Story</span><br>{esc(s.hook)}</div>
      <div class="story-angle reveal d4"><span class="story-angle-pill">Our Proposal</span><br>{esc(s.proposal)}</div>
      <div class="story-places reveal d5">Places: {esc(s.places)}</div>
    </div>
    {quote}
  </div>
  <div class="story-footer">
    <div class="story-ref reveal d6">Sources: {esc(s.reference)}</div>
    <div class="tag-row reveal d5">{tags}</div>
  </div>
</section>"""


def _track_cards(tracks):
    cards = []
    for j, t in enumerate(tracks):
        cls = TRACK_COLOR_CLASSES[j % len(TRACK_COLOR_CLASSES)]
        cards.append(f"""
    <div class="track-card track-card--{cls} reveal d{min(j + 3, 10)}">
      <div class="track-name">{esc(t['name'])}</div>
      <div class="track-stories">{esc(t['stories'])}</div>
      <div class="track-desc">{esc(t['desc'])}</div>
      <div class="track-meta">Geography: {esc(t['geography'])}<br>Season: {esc(t['season'])}<br>{esc(t['story_count'])}</div>
    </div>""")
    return "".join(cards)


def _contents_items(territory, n_stories, has_partners):
    items = [
        "About INLAND",
        f"{territory} — What Survived",
        "Our Angle & Categories",
        f"The {n_stories} Storylines",
        "Production Tracks",
    ]
    if has_partners:
        items.append("An Equitable Co-Production")
    rows = "".join(
        f'<li class="index-item reveal d{min(i + 3, 10)}">'
        f'<span class="index-num">{i + 1:02d}</span>'
        f'<span class="index-title">{esc(t)}</span></li>'
        for i, t in enumerate(items)
    )
    return rows


def build_pitch(cfg):
    """Return the full Kashmir-quality scroll-snap pitch deck as an HTML string."""
    territory = cfg["territory"]
    intro = cfg["intro"]
    stories = cfg["stories"]
    tracks = cfg["tracks"]
    partners = cfg.get("partners", [])
    n_sel = len(stories)
    n_leads = cfg.get("leads_researched", n_sel)
    subtitle = cfg.get("subtitle", "An Africa–Europe Cultural Co-Production")
    meta = cfg.get(
        "meta",
        f"{n_sel} Selected Stories · Goethe-Institut Africa–Europe Partnerships for Culture · 2026",
    )
    breaker_sub = cfg.get(
        "breaker_sub",
        f"{n_sel} selected stories, each centred on a named custodian, a specific "
        "place, and a practice that can still be witnessed.",
    )
    tracks_note = cfg.get("tracks_note", "")
    title = cfg.get("title", f"INLAND {territory} — Africa–Europe Co-Production")

    cats = "".join(
        f'<div class="category-item d{min(i + 5, 10)}"><span>{esc(c)}</span>'
        f'<span class="category-count">{n}</span></div>'
        for i, (c, n) in enumerate(intro["categories"])
    )

    partner_rows = "".join(
        f'<div class="partner-h reveal d{min(i + 3, 10)}">{esc(h)}</div>'
        f'<div class="partner-b reveal d{min(i + 3, 10)}">{esc(b)}</div>'
        for i, (h, b) in enumerate(partners)
    )
    partner_slide = ""
    if partners:
        partner_slide = f"""
<section class="slide" data-theme="light">
  <div class="label reveal">THE PARTNERSHIP</div>
  <h2 class="heading-lg reveal reveal-title d1" style="margin-top:16px;">An Equitable Co-Production</h2>
  <div class="divider reveal-line d2"></div>
  <div class="partner-grid">{partner_rows}</div>
</section>"""

    track_note_html = f'<div class="track-note reveal d8">{tracks_note}</div>' if tracks_note else ""

    head = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f"<title>{esc(title)}</title>"
        f"{FONTS_LINK}<style>{PITCH_CSS}</style></head><body>"
    )

    body = f"""
<div class="progress-bar" id="progressBar"></div>

<section class="slide slide--title" data-theme="light">
  <div class="reveal reveal-scale" style="margin-bottom:12px;">{_logo("logo-svg")}</div>
  <div class="heading-xl reveal reveal-title d2" style="margin-top:8px;">{esc(territory)}</div>
  <div class="divider divider--short reveal-line d3"></div>
  <div class="subtitle reveal d4">{esc(subtitle)}</div>
  <div class="meta reveal d5">{esc(meta)}</div>
</section>

<section class="slide" data-theme="light">
  <div class="label reveal">CONTENTS</div>
  <h2 class="heading-lg reveal reveal-title d1" style="margin-top:16px;">Overview</h2>
  <div class="divider reveal-line d2"></div>
  <ul class="index-list">{_contents_items(territory, n_sel, bool(partners))}</ul>
</section>

<section class="slide" data-theme="light">
  <div class="label reveal">ABOUT</div>
  <h2 class="heading-lg reveal reveal-title d1" style="margin-top:16px;">About INLAND</h2>
  <div class="divider reveal-line d2"></div>
  <div class="intro-layout">
    <div class="intro-main">
      <div class="body-text reveal d3">{esc(intro["about"])}</div>
      <div class="body-secondary reveal d4">{esc(intro["about_method"])}</div>
    </div>
    <div class="intro-side"><div class="accent-text reveal-scale d5">{esc(ACCENT_ABOUT)}</div></div>
  </div>
</section>

<section class="slide" data-theme="light">
  <div class="label reveal">THE RESEARCH</div>
  <h2 class="heading-lg reveal reveal-title d1" style="margin-top:16px;">{esc(territory)} — What Survived</h2>
  <div class="divider reveal-line d2"></div>
  <div class="intro-layout">
    <div class="intro-main">
      <div class="body-text reveal d3">{esc(intro["research"])}</div>
      <div class="body-secondary reveal d4">{esc(intro["research_scope"])}</div>
    </div>
    <div class="intro-side">
      <div class="stat-block">
        <div class="stat-item reveal-scale d4"><div class="stat-num" data-count="{n_leads}">0</div><div class="stat-label">Story leads researched</div></div>
        <div class="stat-item reveal-scale d6"><div class="stat-num" data-count="{n_sel}">0</div><div class="stat-label">Selected for this round</div></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-theme="light">
  <div class="label reveal">EDITORIAL ANGLE</div>
  <h2 class="heading-lg reveal reveal-title d1" style="margin-top:16px;">Our Angle</h2>
  <div class="divider reveal-line d2"></div>
  <div class="intro-layout">
    <div class="intro-main">
      <div class="body-text reveal d3">{esc(intro["angle"])}</div>
      <div class="body-secondary reveal d4">{esc(intro["angle_why"])}</div>
    </div>
    <div class="intro-side">
      <div class="label reveal d5" style="margin-bottom:8px;">CATEGORIES</div>
      <div class="category-list">{cats}</div>
    </div>
  </div>
</section>

<section class="slide slide--breaker" data-theme="dark">
  <div class="breaker-label reveal">PART TWO</div>
  <div class="breaker-heading reveal reveal-title d1">The Storylines</div>
  <div class="divider divider--short divider--white reveal-line d2"></div>
  <div class="breaker-sub reveal d3">{esc(breaker_sub)}</div>
</section>
{"".join(_story_slide(i, s) for i, s in enumerate(stories))}

<section class="slide" data-theme="light">
  <div class="label reveal">THREE TRACKS</div>
  <h2 class="heading-lg reveal reveal-title d1" style="margin-top:16px;">Production Tracks</h2>
  <div class="divider reveal-line d2"></div>
  <div class="tracks-grid">{_track_cards(tracks)}</div>
  {track_note_html}
</section>
{partner_slide}

<section class="slide slide--closing slide--dark" data-theme="dark">
  <div class="closing-headline reveal reveal-title">{n_sel} Storylines.<br>One {esc(territory)}.</div>
  <div class="divider divider--short divider--white reveal-line d1"></div>
  <div class="reveal reveal-scale d2" style="margin-bottom:8px;color:var(--dark-fg);">{_logo("logo-svg--sm")}</div>
  <div class="closing-tagline reveal d3">An Africa–Europe co-production proposal by INLAND</div>
</section>

<div class="nav-counter" id="navCounter">1 / 1</div>
<script>{PITCH_JS}</script>
</body></html>"""
    return head + body


# ── Overview: print/A4 single document, same house style (feeds the PDF) ──
OVERVIEW_CSS = """
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  :root { --bg:#F9F4EE; --fg:#000; --accent:#400505; --muted:rgba(0,0,0,0.6);
    --ref:#857f76; --rule:rgba(0,0,0,0.16);
    --font-heading:'Cormorant',Georgia,serif; --font-body:'Cormorant Garamond',Georgia,serif;
    --font-label:'Fraunces',sans-serif; }
  body { background: var(--bg); color: var(--fg); font-family: var(--font-body);
    line-height: 1.55; font-size: 11pt; }
  .wrap { max-width: 900px; margin: 0 auto; padding: 28px 32px; }
  .label { font-family: var(--font-label); text-transform: uppercase; letter-spacing: .12em;
    font-size: 8.5pt; color: var(--muted); }
  h1, h2, h3 { font-family: var(--font-heading); font-weight: 600; }
  hr { border: 0; border-top: 1px solid var(--fg); margin: 12px 0 18px; }
  .hero { text-align: center; padding: 8px 0 18px; }
  .hero .mark { font-family: var(--font-label); font-weight: 600; letter-spacing: .35em; font-size: 11pt; }
  .hero h1 { font-size: 34pt; margin: 6px 0 4px; }
  .hero .sub { color: var(--muted); font-size: 13pt; }
  .sec-h { font-size: 17pt; margin-top: 16px; }
  .lead { font-size: 12pt; }
  .muted { color: var(--muted); }
  .cats { display: flex; flex-wrap: wrap; gap: 6px 30px; margin-top: 12px; }
  .cats div { display: flex; justify-content: space-between; min-width: 230px;
    border-bottom: 1px solid var(--rule); padding: 4px 0; }
  .cats b { color: var(--accent); }
  .story { padding: 12px 0; border-top: 1px solid var(--rule); break-inside: avoid; }
  .story .top { display: flex; justify-content: space-between; align-items: baseline; }
  .story h3 { font-size: 14pt; }
  .story .num { font-family: var(--font-heading); font-size: 18pt; color: var(--accent); }
  .story .st { font-style: italic; color: var(--muted); font-size: 11.5pt; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 6px; font-size: 10pt; }
  .cols .label { display: block; margin-bottom: 3px; }
  .quote { font-family: var(--font-heading); font-style: italic; color: var(--accent);
    font-size: 11pt; margin-top: 6px; border-left: 2px solid var(--accent); padding-left: 10px; }
  .foot { margin-top: 8px; font-size: 8.5pt; color: var(--ref); font-family: var(--font-label); letter-spacing: .04em; }
  .tracks { display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; margin-top: 14px; }
  .track .bar { height: 3px; margin-bottom: 8px; }
  .track h3 { font-size: 12pt; }
  .track .ts { font-family: var(--font-label); font-size: 8pt; text-transform: uppercase;
    letter-spacing: .08em; color: var(--muted); margin: 4px 0 6px; }
  .track .meta { margin-top: 8px; font-family: var(--font-label); font-size: 8pt; color: var(--ref); line-height: 1.6; }
  .partner { display: grid; grid-template-columns: 180px 1fr; gap: 8px 24px; margin-top: 12px; }
  .partner .h { font-family: var(--font-label); text-transform: uppercase; letter-spacing: .08em;
    font-size: 9pt; color: var(--accent); font-weight: 600; }
  @page { size: A4; margin: 16mm 15mm; }
"""

_OV_TRACK_COLORS = {0: "#1B4965", 1: "#3A5A40", 2: "#5B2C6F"}


def _ov_story(i, s):
    quote = f'<div class="quote">“{esc(s.pull_quote)}”</div>' if getattr(s, "pull_quote", "") else ""
    return f"""<div class="story">
  <div class="top"><div><div class="label">{esc(s.category)}</div><h3>{esc(s.headline)}</h3>
  <div class="st">{esc(s.subtitle)}</div></div><div class="num">{i + 1:02d}</div></div>
  <div class="cols"><div><span class="label">The story</span>{esc(s.hook)}</div>
  <div><span class="label">Our proposal</span>{esc(s.proposal)}</div></div>
  {quote}
  <div class="foot">Places: {esc(s.places)} &nbsp;·&nbsp; Sources: {esc(s.reference)}</div>
</div>"""


def build_overview(cfg):
    """Return the print/A4 overview document (same house style) as an HTML string."""
    territory = cfg["territory"]
    intro = cfg["intro"]
    stories = cfg["stories"]
    tracks = cfg["tracks"]
    partners = cfg.get("partners", [])
    n_sel = len(stories)
    subtitle = cfg.get("subtitle", "An Africa–Europe Cultural Co-Production")
    meta = cfg.get(
        "meta",
        "Goethe-Institut Africa–Europe Partnerships for Culture · 2026",
    )
    title = cfg.get("title", f"INLAND {territory} — Overview")

    cats = "".join(f"<div><span>{esc(c)}</span><b>{n}</b></div>" for c, n in intro["categories"])
    track_cards = "".join(
        f"""<div class="track"><div class="bar" style="background:{_OV_TRACK_COLORS[j % 3]}"></div>
  <h3 style="color:{_OV_TRACK_COLORS[j % 3]}">{esc(t['name'])}</h3>
  <div class="ts">{esc(t['stories'])}</div><div>{esc(t['desc'])}</div>
  <div class="meta">Geography: {esc(t['geography'])}<br>Season: {esc(t['season'])}<br>{esc(t['story_count'])}</div></div>"""
        for j, t in enumerate(tracks)
    )
    partner_rows = "".join(f'<div class="h">{esc(h)}</div><div>{esc(b)}</div>' for h, b in partners)
    partner_block = ""
    if partners:
        partner_block = (
            f'<h2 class="sec-h">An Equitable Co-Production</h2><hr>'
            f'<div class="partner">{partner_rows}</div>'
        )

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>{esc(title)}</title>{FONTS_LINK}<style>{OVERVIEW_CSS}</style></head>
<body><div class="wrap">
<div class="hero"><div class="mark">INLAND</div><h1>{esc(territory)}</h1>
<div class="sub">{esc(subtitle)} · Overview</div>
<div class="label" style="margin-top:6px;">{esc(meta)}</div></div>
<hr>
<p class="lead">{esc(intro["research"])}</p>
<p class="muted" style="margin-top:8px;">{esc(intro["angle"])}</p>
<div class="cats">{cats}</div>
<h2 class="sec-h">The {n_sel} Storylines</h2><hr>
{"".join(_ov_story(i, s) for i, s in enumerate(stories))}
<h2 class="sec-h">Production Tracks</h2><hr>
<div class="tracks">{track_cards}</div>
{partner_block}
</div></body></html>"""


def write_edition(cfg, outdir="."):
    """Write INLAND_<territory>_Pitch.html and _Overview.html into outdir."""
    out = pathlib.Path(outdir)
    territory = cfg["territory"]
    pitch_path = out / f"INLAND_{territory}_Pitch.html"
    overview_path = out / f"INLAND_{territory}_Overview.html"
    pitch_path.write_text(build_pitch(cfg), encoding="utf-8")
    overview_path.write_text(build_overview(cfg), encoding="utf-8")
    print(f"wrote {pitch_path.name} + {overview_path.name}")
    return pitch_path, overview_path
