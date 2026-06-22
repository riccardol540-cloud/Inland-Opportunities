# PRODUCER — turn a chosen opportunity into a full INLAND application

*This is the on-demand playbook. Run it when collaborators have moved one or more
opportunities to **Pursuing** in the dashboard. It reads the shared JSON, picks up what
people chose, runs deep research, and produces the same asset set as Rwanda/Kashmir.*

## Steps

1. **Read context**: `_inland/about-inland.md`, `_inland/research-angle.md`,
   `_inland/deliverables.md`, `_inland/opportunity-criteria.md`. `research-angle.md` is the
   territory-agnostic blueprint of the editorial angle — apply it to **whatever territory
   this opportunity makes relevant**. Rwanda and Kashmir are blueprints of the angle, not
   templates of the subject; never transplant their stories onto a new country.
2. **Find the work**: read `data/opportunities.json` and select every opportunity with
   `status === "pursuing"`. The `owner` and `notes` fields tell you who asked and any
   steer they left.
3. **Prioritise**: do **`flagged: true` opportunities first**, then by deadline urgency,
   then by `fit`. If more than one is pursuing, confirm with the user which to build now.
   Note the `requiredDocs` — those are mandatory outputs.
4. **Mark in-progress**: set that opportunity's `production` to `"in_progress"` and
   commit, so the dashboard shows "Producing…" while you work.
5. **Deep research** the chosen territory/angle following INLAND's method: named,
   locatable custodians; specific places; living traditions; sources/links throughout.
6. **Produce the asset set** into the repo at **`editions/<territory>/`** (so the files
   live in GitHub and every collaborator can open them from the dashboard), per
   `_inland/deliverables.md`:
   - deep-research report (`.md`)
   - selected story leads (`.md`)
   - Topics + Contacts spreadsheet (`.xlsx`, two sheets)
   - pitch presentation (`.pptx` + `.html`) in INLAND house style
   - overview PDF
   - **the opportunity's required application documents** (concept note, budget,
     timeline, CVs, letters — whatever `requiredDocs` lists)
7. **Link the documents**: set the opportunity's `production` to `"drafted"` and add each
   file to its `documents` array as `{ "label": "...", "url": "..." }`. Use the file's
   GitHub URL, e.g.
   `https://github.com/riccardol540-cloud/Inland-Opportunities/blob/main/editions/<territory>/<file>`.
   Append a `history` entry, then commit and push. The card now shows "✓ Docs drafted"
   with working links.
8. **Hand back**: present the drafted assets for review before anything is submitted.
   Leave `status` to the collaborators (they move it to Archived once submitted).

## Notes

- The Producer is **on-demand**, not scheduled — it's expensive and needs your judgment.
  Best invoked as a skill/command or a working session.
- House style, boilerplate, and the exact deliverable formats live in
  `_inland/deliverables.md`. Follow them so every edition looks like INLAND.
