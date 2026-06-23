"""Generate the INLAND Rwanda pitch + overview HTML from the deck data.

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

PARTNERS = [
    ("European partner", "INLAND — yearly publication (Italy / EU). Editorial, photography and publishing; presentation of the work in Europe."),
    ("African partner", "A Rwandan cultural organisation (lead candidate: Red Rocks Initiatives, Musanze) — co-creation, community access, custodian liaison, presentation in Rwanda."),
    ("Funding path", "Mobility grant (≤€4,000) funds the scouting trip; the Visual Arts grant funds collaborative production and a public presentation in Rwanda and Europe."),
    ("The principle", "Made with custodians, not about them — equitable Africa–Europe co-creation, exactly the dialogue the Goethe programme exists to fund."),
]

CFG = {
    "territory": "Rwanda",
    "intro": INTRO,
    "stories": STORIES,
    "tracks": TRACKS,
    "partners": PARTNERS,
    "leads_researched": 20,
    "breaker_sub": (
        "Twelve selected stories across communities, ritual, food, ecology, craft "
        "and music. Each centres a named custodian, a specific place, and a "
        "practice that can still be witnessed."
    ),
}

if __name__ == "__main__":
    write_edition(CFG, outdir=str(_HERE.parent))
