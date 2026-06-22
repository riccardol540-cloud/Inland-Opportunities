import { isAuthed, readData, writeData, readBody } from "./_lib.js";

const EDITABLE = [
  "status", "owner", "notes", "fit", "fitRationale", "territory", "title", "deadline", "budget", "link",
  // user can toggle priority; Claude (Scout/Producer) sets these too (also via git)
  "flagged", "production", "documents", "requiredDocs", "channel", "eligibility", "researched",
];
const STATUSES = ["new", "pursuing", "archived"];
const PRODUCTION = ["none", "in_progress", "drafted"];

export default async function handler(req, res) {
  if (!isAuthed(req)) return res.status(401).json({ error: "Not authenticated" });

  try {
    if (req.method === "GET") {
      const { data } = await readData();
      return res.status(200).json(data);
    }

    if (req.method === "PATCH" || req.method === "POST" || req.method === "DELETE") {
      const body = await readBody(req);
      // simple optimistic retry to absorb concurrent edits
      for (let attempt = 0; attempt < 3; attempt++) {
        const { data, sha } = await readData();
        data.opportunities = data.opportunities || [];

        let message = "Update opportunities via dashboard";

        if (req.method === "POST") {
          const o = body.opportunity || {};
          o.id = o.id || `opp-${Date.now()}`;
          // Opportunities suggested via the dashboard are unresearched: they wait
          // for Claude (the Scout) to scan them before they can advance to Pursuing.
          o.status = "new";
          o.researched = false;
          o.fit = o.fit ?? null;
          o.flagged = o.flagged ?? false;
          o.production = "none";
          o.documents = o.documents || [];
          o.owner = o.owner || o.addedBy || "";
          o.history = o.history || [];
          o.addedBy = o.addedBy || "dashboard";
          o.addedAt = o.addedAt || new Date().toISOString().slice(0, 10);
          data.opportunities.unshift(o);
          message = `Suggest opportunity: ${o.title || o.id}`;
        } else {
          const idx = data.opportunities.findIndex((x) => x.id === body.id);
          if (idx === -1) return res.status(404).json({ error: "Opportunity not found" });

          if (req.method === "DELETE") {
            const removed = data.opportunities.splice(idx, 1)[0];
            message = `Remove opportunity: ${removed.title || removed.id}`;
          } else {
            const o = data.opportunities[idx];
            const changes = body.changes || {};
            // Lock: an unresearched (user-suggested) opportunity cannot advance to
            // Pursuing until the Scout has scanned it. Archiving it is still allowed.
            if (changes.status === "pursuing" && o.researched === false) {
              return res.status(400).json({ error: "Locked: needs research first" });
            }
            const applied = {};
            for (const key of Object.keys(changes)) {
              if (!EDITABLE.includes(key)) continue;
              if (key === "status" && !STATUSES.includes(changes[key])) continue;
              if (key === "production" && !PRODUCTION.includes(changes[key])) continue;
              applied[key] = changes[key];
              o[key] = changes[key];
            }
            o.history = o.history || [];
            o.history.push({
              at: new Date().toISOString(),
              by: body.actor || "dashboard",
              changes: applied,
            });
            message = `Update ${o.title || o.id}: ${Object.keys(applied).join(", ") || "no-op"}`;
          }
        }

        try {
          await writeData(data, sha, message);
          return res.status(200).json(data);
        } catch (e) {
          // 409 = sha conflict; retry with a fresh read
          if (String(e.message).includes("409") && attempt < 2) continue;
          throw e;
        }
      }
      return res.status(409).json({ error: "Conflict — please retry" });
    }

    res.setHeader("Allow", "GET, POST, PATCH, DELETE");
    return res.status(405).json({ error: "Method not allowed" });
  } catch (e) {
    return res.status(500).json({ error: String(e.message || e) });
  }
}
