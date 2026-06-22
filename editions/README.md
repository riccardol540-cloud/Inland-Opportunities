# editions/

Produced documents live here, one folder per territory (e.g. `editions/rwanda/`,
`editions/kashmir/`). Both Claude routines write into this folder so the files sit in the
GitHub repo and any collaborator can open them straight from the dashboard:

- **Scout** writes a short `research-brief.md` per opportunity it researches.
- **Producer** writes the full asset set for a pursued opportunity — deep-research
  report, selected story leads, Topics/Contacts `.xlsx`, pitch `.pptx`/`.html`, overview
  PDF, and the application's required documents.

Each file is linked back on its opportunity card via the `documents` array in
`../data/opportunities.json`, using its GitHub URL
(`.../blob/main/editions/<territory>/<file>`).

Heavy edition working folders elsewhere (e.g. the original Rwanda/Kashmir asset folders)
can stay where they are; what matters is that anything the dashboard links to lives in
this repo.
