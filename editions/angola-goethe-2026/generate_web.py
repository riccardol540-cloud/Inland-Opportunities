"""Generate the INLAND Angola pitch + overview HTML from the deck data.

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
    ("African partner", "An Angolan cultural organisation (lead candidate: Lueji A’Nkonde University, Lunda Norte — which coordinated the sona UNESCO nomination) — co-creation, community access, custodian liaison, presentation in Angola."),
    ("Funding path", "Mobility grant (≤€4,000) funds the scouting trip; the Visual Arts grant funds collaborative production and a public presentation in Angola and Europe."),
    ("The principle", "Made with custodians, not about them — equitable Africa–Europe co-creation, exactly the dialogue the Goethe programme exists to fund."),
]

CFG = {
    "territory": "Angola",
    "intro": INTRO,
    "stories": STORIES,
    "tracks": TRACKS,
    "partners": PARTNERS,
    "leads_researched": 17,
    "breaker_sub": (
        "Twelve selected stories across art, ritual, governance, food, pastoral "
        "life and memory. Each centres a custodian, a specific place, and a "
        "practice that can still be witnessed."
    ),
    "tracks_note": (
        "Signature: <b>Offerings to Kianda</b> (Festa da Ilha, November) runs "
        "across the project; the <b>Mbanza Kongo lumbu</b> and <b>Njinga’s "
        "footprints</b> form a Kingdoms-and-Memory strand."
    ),
}

if __name__ == "__main__":
    write_edition(CFG, outdir=str(_HERE.parent))
