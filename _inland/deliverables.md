# Deliverables — what the Producer builds

*When an opportunity moves to `pursuing/` and you start a Producer session, this is the
asset set to generate, mirroring what already exists for Rwanda and Kashmir. Follow the
formats and house style below so every edition looks and reads like INLAND.*

## The standard edition asset set

1. **Deep-research report** (`.md`)
   - The substantive desk-research brief on the territory's living traditions.
   - Structure (from Kashmir): a TL;DR, numbered **Key Findings**, and a **"Where to
     Embed"** section with concrete, named places, people, dates, and access notes.
   - Every claim grounded in named people, specific places, and sources/links.

2. **Selected story leads** (`.md`)
   - The curated subset chosen for editorial development, each as a "story lead" with:
     **Place**, **Angle**, **Practices**, and **Status**, preserving source links.

3. **Topics + Contacts spreadsheet** (`.xlsx`) — two sheets:
   - **Sheet 1 — Topics**: `Topic | Description | Category | Links | Contacts |
     Interesting for | Ideas for development | Notes`. Description = 3–5 sentence
     narrative pitch, specific and visual, naming real places/people.
   - **Sheet 2 — Contacts**: `Name | What they do | Useful for | Contact | Status |
     (To be) Contacted by | Notes`.
   - **Categories**: `Arts&Culture`, `Geopolitics`, `Local communities`, `History`,
     `Myth&Religion`, `Nature`, `Food`. (Kashmir grouped as Communities, Borderlands,
     Food, Nature & Ecology, Music & Performance — pick category language to fit the
     territory but keep the two-sheet structure.)
   - **Topic quality bar**: specific (tied to a real place/person/community/event),
     surprising (something most Europeans wouldn't know), visual, story-driven.
   - Use Armenia / Uzbekistan / Rwanda Topics files as format references.

4. **Pitch presentation** (`.pptx`, plus `.html` version)
   - Audience: institutional / embassy collaborators and funders.
   - Established sections (from the Kashmir builder): **About INLAND**, **Method**,
     **Research overview**, **Research scope** (e.g. "X leads identified, Y selected"),
     **Angle / why this matters**, **Category breakdown**, then one slide per selected
     **story** (headline, subtitle, hook, proposal, category, tags, pull-quote,
     places, reference).
   - **HTML: always render via the shared module `_inland/templates/inland_web.py`.
     Do NOT hand-roll or minify CSS in an edition.** That module owns the canonical
     house style and produces a Kashmir-quality, self-contained deck: Google Fonts
     (Cormorant / Cormorant Garamond / Fraunces), a full-screen **scroll-snap** slide
     deck, reveal animations + animated stat counters, per-story **Story / Proposal**
     toggle, nav counter + progress bar, and the inline INLAND logo. The visual gold
     standard is `_inland/templates/REFERENCE_INLAND_pitch.html` (the original Kashmir
     pitch) — match it.
   - The edition's `generate_web.py` is a **thin shim**: it imports
     `STORIES / INTRO / TRACKS` from its own `build_presentation.py`, defines edition
     `PARTNERS` + `leads_researched` (+ optional `breaker_sub`, `tracks_note`), and
     calls `inland_web.write_edition(cfg)`. See `editions/goethe-africa-europe-2026/`
     or `editions/angola-goethe-2026/` for the pattern, and the `inland_web.py`
     docstring for the full `cfg` data contract.

5. **Overview PDF** (e.g. `INLAND_<Territory>_Overview.pdf`)
   - A concise, designed one-document summary of the edition for sharing.
   - Built from `INLAND_<Territory>_Overview.html` — also produced by
     `_inland/templates/inland_web.py` (print/A4 layout in the same house style).
     Export that HTML to PDF; don't author the overview separately.

6. **Application-specific documents** — whatever the opportunity's brief lists as
   required (concept note, budget, timeline, CVs, letters of support). Build these from
   the opportunity brief in `pursuing/` plus the research above.

## House style (from the Kashmir pitch builder)

*For HTML/PDF deliverables the source of truth is `_inland/templates/inland_web.py`
(palette, fonts, layout, animations). The values below are the reference it encodes —
use them for the `.pptx` and any other asset.*

- **Palette**: background `#F9F4EE`, foreground `#000000`, accent `#400505`; dark mode
  background `#0e0e0e` / foreground `#FFFFFF`.
- **Fonts**: headings *Cormorant*; body *Cormorant Garamond*; labels *Fraunces*.
- **Tone in copy**: slow, intimate, restrained; custodian-led; continuity over crisis;
  always name people and places.

## Standard "About INLAND" boilerplate (reuse in pitches)

> INLAND is a yearly publication documenting the soul of countries before they change.
> Each issue embeds with named, locatable custodians of living traditions — artisans,
> pastoralists, cooks, singers, border families — whose stories have not yet been
> narrated internationally. Previous issues have covered the Faroe Islands, Georgia and
> Italy's minor islands.

> The editorial method is slow, place-based and built on trust. We spend months in
> pre-production research, identify specific custodians and communities, then commission
> photographers, writers and filmmakers to embed with them over extended field periods.

## Where editions live

Each edition gets its own folder at the workspace root (`../Rwanda/`, `../Kashmir/`,
`../<NewTerritory>/`) with `Research Reports/` (or research `.md` files), a selected-
leads doc, and a `Created Assets/` folder for the Excel, pitch, and PDF. Keep a per-
edition `instructions.md` + `memory.md` (as Rwanda does) so a session can resume.
