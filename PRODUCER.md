# PRODUCER — turn a chosen opportunity into a full INLAND application

*This is the on-demand playbook. Run it when collaborators have moved one or more
opportunities to **Pursuing** in the dashboard. It reads the shared JSON, picks up what
people chose, runs deep research, and produces the same asset set as Rwanda/Kashmir.*

## Steps

1. **Read context**: `_inland/about-inland.md`, `_inland/deliverables.md`,
   `_inland/opportunity-criteria.md`.
2. **Find the work**: read `data/opportunities.json` and select every opportunity with
   `status === "pursuing"`. These are the collaborators' decisions — the `owner` and
   `notes` fields tell you who asked and any steer they left.
3. **Confirm scope**: if more than one is `pursuing`, confirm with the user which to
   build now (or do the highest-fit first). Note the `requiredDocs` for that
   opportunity — those are mandatory outputs.
4. **Deep research** the chosen territory/angle following INLAND's method: named,
   locatable custodians; specific places; living traditions; sources/links throughout.
5. **Produce the edition asset set** into a new edition folder
   (`../<Territory>/Created Assets/`), per `_inland/deliverables.md`:
   - deep-research report (`.md`)
   - selected story leads (`.md`)
   - Topics + Contacts spreadsheet (`.xlsx`, two sheets)
   - pitch presentation (`.pptx` + `.html`) in INLAND house style
   - overview PDF
   - **the opportunity's required application documents** (concept note, budget,
     timeline, CVs, letters — whatever `requiredDocs` lists)
6. **Record progress**: append a `history` entry to that opportunity in
   `opportunities.json` (e.g. "assets drafted"), optionally set `owner`, and commit. Do
   not change `status` to anything the dashboard doesn't use — leave status decisions to
   the collaborators, or, if agreed, move to `archived` once submitted.
7. **Hand back**: present the drafted assets for review before anything is submitted.

## Notes

- The Producer is **on-demand**, not scheduled — it's expensive and needs your judgment.
  Best invoked as a skill/command or a working session.
- House style, boilerplate, and the exact deliverable formats live in
  `_inland/deliverables.md`. Follow them so every edition looks like INLAND.
