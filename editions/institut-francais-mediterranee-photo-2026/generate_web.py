"""Generate the INLAND Tunisia pitch + overview HTML from the deck data.

Thin shim: all house style and markup live in the shared renderer
`_inland/templates/inland_web.py`. This file only supplies the edition data.
Run from this directory: `python3 generate_web.py`
"""
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent))                                  # local build_presentation
sys.path.insert(0, str(_HERE.parents[2] / "_inland" / "templates"))   # shared renderer

from build_presentation import STORIES, INTRO, TRACKS  # noqa: E402
from inland_web import write_edition  # noqa: E402

# Repurposed for the Institut français Mediterranean grant: the closing
# institutional slide presents the edition's two strands, not a co-production.
PARTNERS = [
    ("The publication", "INLAND — yearly publication (Italy / EU). A finished Tunisia edition (~170–240 pp) on the Mediterranean theme, in the register of Issue 03, Isole Minori. The Institut français publication aid covers editing and printing in full."),
    ("The production", "The field shoot across three coastal-and-island clusters — Kerkennah, Cap Bon–Sahel, the green north — funded by the production strand for new Mediterranean photographic work."),
    ("Why the Mediterranean", "Tunisia is a Mediterranean palimpsest — Phoenician, Roman, Amazigh, Andalusian, Jewish, Ibadi and sub-Saharan — read through living custodians on its shores and islands, exactly the ‘monde méditerranéen’ the programme funds."),
    ("The principle", "Named custodians, locatable places, seasonal scenes — made with the people who keep these traditions, not about them. The loud Tunisia of revolution and migration stays as context; the quieter country is the subject."),
]

CFG = {
    "territory": "Tunisia",
    "intro": INTRO,
    "stories": STORIES,
    "tracks": TRACKS,
    "partners": PARTNERS,
    "leads_researched": 17,
    "subtitle": "A Mediterranean Edition",
    "meta": "12 Selected Stories · Institut français — Mediterranean Photography Support · 2026",
    "title": "INLAND Tunisia — A Mediterranean Edition",
    "partners_label": "THE EDITION",
    "partners_heading": "Two Strands, One Edition",
    "closing_tagline": "A Mediterranean photographic edition by INLAND",
    "breaker_sub": (
        "Twelve selected stories across the shore and the islands — craft, ritual, "
        "fishing, food, language and landscape. Each centres a custodian, a "
        "specific place, and a practice that can still be witnessed."
    ),
    "tracks_note": (
        "Signature: <b>The Charfia of Kerkennah</b> (autumn net-setting) runs "
        "across the project as its recurring image; <b>El Ghriba</b> (spring "
        "pilgrimage) and the <b>Stambeli</b> nights anchor a faith-and-memory strand."
    ),
}

if __name__ == "__main__":
    write_edition(CFG, outdir=str(_HERE.parent))
