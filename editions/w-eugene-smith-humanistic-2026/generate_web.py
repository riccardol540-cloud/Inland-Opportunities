"""Generate the INLAND Georgia pitch + overview HTML from the deck data.

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

# Repurposed for the W. Eugene Smith Grant: the closing institutional slide
# presents the application — applicant, past work, proposed project, why Smith —
# rather than a co-production partnership.
PARTNERS = [
    ("The applicant", "An INLAND-commissioned documentary photographer is the named applicant; INLAND is the editorial home that researches, embeds and publishes the work. The Smith Grant’s applicant is an individual photographer, and this is INLAND’s route."),
    ("Past work", "INLAND’s Georgia edition (Issue 02, 2024) is the prior cohesive body of work — long-form, humanistic, custodian-led — that this project carries deeper, alongside the Faroe Islands and Isole Minori editions."),
    ("Proposed project", "‘The Quiet Country’: a year among Georgia’s highland custodians — shepherds over the Abano Pass, the tower families of Ushguli, the shrine-priests of Khevsureti, the Pankisi zikr women, the Kakhetian winemakers — edited to up to 40 images."),
    ("Why Smith", "Concerned, compassionate documentary about the human condition, made with named custodians rather than about them: continuity over crisis, dignity over spectacle. The grant underwrites the extended field embedding the work needs."),
]

CFG = {
    "territory": "Georgia",
    "intro": INTRO,
    "stories": STORIES,
    "tracks": TRACKS,
    "partners": PARTNERS,
    "leads_researched": 16,
    "subtitle": "The Quiet Country — A Humanistic Documentary",
    "meta": "12 Selected Stories · W. Eugene Smith Grant in Humanistic Photography · 2026",
    "title": "INLAND Georgia — The Quiet Country",
    "partners_label": "THE APPLICATION",
    "partners_heading": "A Humanistic Project, in Smith’s Tradition",
    "closing_tagline": "A humanistic documentary project by INLAND, in the tradition of W. Eugene Smith",
    "breaker_sub": (
        "Twelve selected stories across pasture, song, faith, craft, food and "
        "memory. Each centres a named custodian, a specific place, and a practice "
        "that can still be witnessed — in the tradition of concerned photography."
    ),
    "tracks_note": (
        "Signature: <b>The Road in May</b> (the Abano Pass crossing) runs across "
        "the project as its recurring image; the <b>supra</b> and <b>Georgian "
        "polyphony</b> bind the clusters as the project’s social thread."
    ),
}

if __name__ == "__main__":
    write_edition(CFG, outdir=str(_HERE.parent))
