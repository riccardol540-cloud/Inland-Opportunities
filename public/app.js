// INLAND Opportunities — dashboard client.
const $ = (s) => document.querySelector(s);
let STATE = { opportunities: [], meta: {} };

const STATUSES = ["new", "pursuing", "archived"];
const FIT_CLASS = { 5: "f5", 4: "f4", 3: "f3", 2: "f2", 1: "f1" };
const STATUS_LABEL = { new: "Inbox", pursuing: "Pursuing", archived: "Archived" };
const LIST_STATUS = { ready: "new", awaiting: "new", pursuing: "pursuing", archived: "archived" };

const EXPANDED = new Set();   // ids of currently-open cards (survives re-render)
let revealed = false;          // first-paint reveal flag

// Per-card staged edits for typed fields (owner, notes). Each entry is a map of
// changed fields not yet committed. Discrete actions (flag/move/delete) stay immediate.
const STAGED_FIELDS = ["owner", "notes"];
const DRAFTS = new Map();      // id -> { field: value }
let saving = 0;                // count of in-flight commits

const isResearched = (o) => o.researched !== false;

const PROD_LABEL = { none: "Awaiting production", in_progress: "Producing…", drafted: "Docs drafted" };

// SVG glyphs
const GRIP = '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><circle cx="5" cy="3" r="1.4"/><circle cx="11" cy="3" r="1.4"/><circle cx="5" cy="8" r="1.4"/><circle cx="11" cy="8" r="1.4"/><circle cx="5" cy="13" r="1.4"/><circle cx="11" cy="13" r="1.4"/></svg>';
const CHEV = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6l4 4 4-4"/></svg>';
const THUMB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M2 9.5h3.2V21H2zM21.6 11.1c0-1.05-.86-1.9-1.9-1.9h-5.13l.77-3.71.024-.26c0-.39-.16-.75-.42-1.01L13.96 3l-6.02 6.03c-.35.35-.56.83-.56 1.36V19c0 1.05.86 1.9 1.9 1.9h7.6c.76 0 1.42-.46 1.7-1.12l2.55-5.95c.08-.2.12-.4.12-.63z"/></svg>';
const DL = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 2.5v8M4.5 7L8 10.5 11.5 7M3 13.5h10"/></svg>';

// ---------- auth ----------
async function checkAuth() {
  const r = await fetch("/api/login", { cache: "no-store" });
  const j = await r.json();
  return j.authed;
}
$("#gate-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("#gate-error").textContent = "";
  const r = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: $("#gate-pw").value }),
  });
  if (r.ok) { boot(); }
  else { $("#gate-error").textContent = "Incorrect password"; }
});
$("#logout").addEventListener("click", async () => {
  if (DRAFTS.size && !confirm("You have unsaved changes. Sign out and discard them?")) return;
  await fetch("/api/login", { method: "DELETE" });
  location.reload();
});

// ---------- data ----------
async function load() {
  let r;
  try {
    r = await fetch("/api/opportunities", { cache: "no-store" });
  } catch {
    showLoadError("Network error — couldn't reach the server. Check your connection and Refresh.");
    return;
  }
  if (r.status === 401) { showGate(); return; }
  if (!r.ok) {
    let msg = `Failed to load opportunities — HTTP ${r.status}`;
    try { const j = await r.json(); if (j && j.error) msg += ` · ${j.error}`; } catch {}
    showLoadError(msg);
    return;
  }
  let data;
  try { data = await r.json(); } catch { data = null; }
  if (!data || !Array.isArray(data.opportunities)) {
    showLoadError("Loaded, but the data was empty or malformed. Try Refresh; if it persists, check the server.");
    return;
  }
  hideLoadError();
  STATE = data;
  render();
}
async function patch(id, changes) {
  saving++; renderSaveState();
  let r;
  try {
    r = await fetch("/api/opportunities", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, changes, actor: actor() }),
    });
  } catch {
    saving--; renderSaveState(); toast("Network error — not saved"); return false;
  }
  saving--;
  if (!r.ok) {
    let msg = "Save failed";
    try { const j = await r.json(); if (j.error) msg = j.error; } catch {}
    toast(msg);
    load();   // resync DOM with server (e.g. after a blocked drag)
    return false;
  }
  STATE = await r.json();
  render();
  return true;
}

// ---------- staged per-card edits ----------
function stageField(id, field, value) {
  const o = (STATE.opportunities || []).find((x) => x.id === id) || {};
  const d = DRAFTS.get(id) || {};
  if ((o[field] || "") === value) delete d[field];
  else d[field] = value;
  if (Object.keys(d).length) DRAFTS.set(id, d); else DRAFTS.delete(id);
  const cardEl = document.querySelector(`.card[data-id="${id}"]`);
  if (cardEl) {
    const dirty = DRAFTS.has(id);
    cardEl.classList.toggle("dirty", dirty);
    const bar = cardEl.querySelector(".card-savebar");
    if (bar) bar.classList.toggle("show", dirty);
  }
  renderSaveState();
}
async function saveCard(id) {
  const d = DRAFTS.get(id);
  if (!d || !Object.keys(d).length) return;
  const ok = await patch(id, { ...d });
  if (ok) { DRAFTS.delete(id); }   // render() already ran; drafts now clean
  renderSaveState();
}
function discardCard(id) {
  DRAFTS.delete(id);
  render();
}
function renderSaveState() {
  const el = $("#savestate");
  if (!el) return;
  const n = DRAFTS.size;
  if (saving > 0) { el.textContent = "Saving…"; el.className = "savestate saving"; }
  else if (n > 0) { el.textContent = `Unsaved · ${n}`; el.className = "savestate unsaved"; }
  else { el.textContent = "All changes saved"; el.className = "savestate ok"; }
}
async function duplicateOpp(id) {
  saving++; renderSaveState();
  let r;
  try {
    r = await fetch("/api/opportunities", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ duplicateFrom: id, actor: actor() }),
    });
  } catch { saving--; renderSaveState(); toast("Network error — not duplicated"); return; }
  saving--;
  if (!r.ok) {
    let msg = "Duplicate failed";
    try { const j = await r.json(); if (j.error) msg = j.error; } catch {}
    toast(msg); return;
  }
  STATE = await r.json();
  render();
  toast("Duplicated — set its country");
}
async function removeOpp(id) {
  const r = await fetch("/api/opportunities", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id }),
  });
  if (!r.ok) { toast("Delete failed"); return; }
  STATE = await r.json();
  render();
  toast("Deleted");
}

// ---------- download edition (client-side zip) ----------
// GitHub blob URL -> raw URL (the public repo serves raw files with permissive CORS,
// so the browser can fetch each document and zip them with no server round-trip):
//   https://github.com/<owner>/<repo>/blob/<branch>/<path>
//   -> https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>
function blobToRaw(url) {
  return url.replace(
    /^https:\/\/github\.com\/([^/]+)\/([^/]+)\/blob\/(.+)$/,
    "https://raw.githubusercontent.com/$1/$2/$3",
  );
}

// Derive the edition slug (zip name) and each file's path relative to that slug, so the
// zip preserves subfolders (e.g. application/) under a single edition root.
function editionPaths(docs) {
  const rels = docs.map((d) => {
    const m = d.url.match(/\/editions\/(.+)$/);
    return m ? decodeURIComponent(m[1]) : (d.label || d.url).replace(/[^\w.-]+/g, "_");
  });
  const slug = rels[0].split("/")[0] || "edition";
  const paths = rels.map((r) => (r.startsWith(slug + "/") ? r.slice(slug.length + 1) : r));
  return { zipName: slug, paths };
}

async function downloadEdition(btn, id) {
  const o = (STATE.opportunities || []).find((x) => x.id === id);
  if (!o || !o.documents || !o.documents.length || btn.dataset.busy) return;

  const label = btn.querySelector("span");
  const original = label ? label.textContent : "";
  btn.dataset.busy = "1";
  btn.disabled = true;
  if (label) label.textContent = "Zipping…";

  const { zipName, paths } = editionPaths(o.documents);
  const zip = new JSZip();
  const failed = [];
  await Promise.all(o.documents.map(async (d, i) => {
    try {
      const res = await fetch(blobToRaw(d.url));
      if (!res.ok) throw new Error(String(res.status));
      zip.file(paths[i], await res.blob());
    } catch {
      failed.push(d.label || paths[i]);
    }
  }));

  const got = o.documents.length - failed.length;
  if (!got) { toast("Download failed — no files could be fetched"); resetDlBtn(btn, label, original); return; }

  try {
    const blob = await zip.generateAsync({ type: "blob" });
    const href = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = href;
    a.download = `${zipName}.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(href), 4000);
    toast(failed.length
      ? `Downloaded ${got} of ${o.documents.length} — skipped: ${failed.join(", ")}`
      : `Downloaded ${got} ${got === 1 ? "file" : "files"}`);
  } catch {
    toast("Could not build the zip");
  }
  resetDlBtn(btn, label, original);
}

function resetDlBtn(btn, label, original) {
  delete btn.dataset.busy;
  btn.disabled = false;
  if (label) label.textContent = original;
}

// ---------- identity ----------
function actor() { return localStorage.getItem("inland_actor") || "anon"; }
function setActor(name) {
  const n = (name || "").trim();
  if (n) localStorage.setItem("inland_actor", n);
  renderIdentity();
}
function renderIdentity() {
  const a = localStorage.getItem("inland_actor");
  $("#identity").innerHTML = a ? `You: <b>${esc(a)}</b>` : "Set your name";
}

// ---------- render ----------
function daysUntil(d) {
  if (!d) return null;
  const ms = new Date(d).getTime() - Date.now();
  return Math.ceil(ms / 86400000);
}
function esc(s) { return (s ?? "").toString().replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

// Team rating helpers — net score across all users' votes; the current user's vote.
function score(o) { return Object.values(o.votes || {}).reduce((a, b) => a + (Number(b) || 0), 0); }
function myVote(o) { return (o.votes || {})[actor()] || 0; }

// Country options: blank (none), "Multiple / Open", then full country list.
const COUNTRIES = ["", "Multiple / Open",
  "Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan",
  "Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi",
  "Cambodia","Cameroon","Canada","Cape Verde","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo","Congo (DRC)","Costa Rica","Côte d’Ivoire","Croatia","Cuba","Cyprus","Czechia",
  "Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia",
  "Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana",
  "Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan",
  "Kazakhstan","Kenya","Kiribati","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg",
  "Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar",
  "Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Korea","North Macedonia","Norway","Oman",
  "Pakistan","Palau","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Rwanda",
  "Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino","São Tomé and Príncipe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Sweden","Switzerland","Syria",
  "Taiwan","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan",
  "Vanuatu","Vatican City","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"];
function countryOptions(cur) {
  return COUNTRIES.map((c) => `<option value="${esc(c)}"${c === (cur || "") ? " selected" : ""}>${c === "" ? "— (none)" : esc(c)}</option>`).join("");
}
function countrySelect(o) { return `<select class="card-field country-select" data-country data-id="${o.id}">${countryOptions(o.country)}</select>`; }

function moveButtons(o, researched) {
  const cur = o.status || "new";
  let targets = [];
  if (cur === "new") targets = researched ? ["pursuing", "archived"] : ["archived"];
  else if (cur === "pursuing") targets = ["new", "archived"];
  else if (cur === "archived") targets = researched ? ["new", "pursuing"] : ["new"];
  return targets.map((t) => `<button class="mini" data-move="${t}" data-id="${o.id}">→ ${STATUS_LABEL[t]}</button>`).join("");
}

function card(o) {
  const researched = isResearched(o);
  const awaiting = !researched;
  const compact = o.status === "archived";   // archived cards get a slimmer collapsed head
  const open = EXPANDED.has(o.id);
  const sc = score(o);
  const mv = myVote(o);
  const draft = DRAFTS.get(o.id) || {};
  const dirty = Object.keys(draft).length > 0;
  const ownerVal = draft.owner !== undefined ? draft.owner : (o.owner || "");
  const notesVal = draft.notes !== undefined ? draft.notes : (o.notes || "");
  const fitClass = FIT_CLASS[o.fit] || "f3";
  const dleft = daysUntil(o.deadline);
  const urgent = dleft !== null && dleft <= 21 && o.status !== "archived";

  const chips = [];
  if (o.funder) chips.push(`<span class="grant-chip">${esc(o.funder)}</span>`);
  if (o.country) chips.push(`<span class="country-chip">${esc(o.country)}</span>`);
  const chipsRow = chips.length ? `<div class="card-chips">${chips.join("")}</div>` : "";
  const subText = awaiting ? `Suggested by ${esc(o.addedBy || "—")}` : (o.channel ? esc(o.channel) : "");

  const prod = o.production || "none";
  const metaBits = [];
  if (o.deadline) metaBits.push(`<span class="m-deadline ${urgent ? "urgent" : ""}">Due ${esc(o.deadline)}${dleft !== null ? ` (${dleft}d${urgent ? " · urgent" : ""})` : ""}</span>`);
  if (o.owner) metaBits.push(`<span class="m-owner">Owner: <b>${esc(o.owner)}</b></span>`);
  if (o.status === "pursuing") metaBits.push(`<span class="prod-badge ${prod}">${PROD_LABEL[prod] || PROD_LABEL.none}</span>`);
  const meta = metaBits.length ? `<div class="card-meta">${metaBits.join("")}</div>` : "";

  const votes = `<div class="votes">
      <button class="vote-btn up ${mv === 1 ? "on" : ""}" data-vote="1" data-id="${o.id}" title="Upvote priority" aria-label="Upvote" aria-pressed="${mv === 1}">${THUMB}</button>
      <span class="vote-score ${sc > 0 ? "pos" : sc < 0 ? "neg" : ""}" title="Net team score">${sc > 0 ? "+" + sc : sc}</span>
      <button class="vote-btn down ${mv === -1 ? "on" : ""}" data-vote="-1" data-id="${o.id}" title="Downvote priority" aria-label="Downvote" aria-pressed="${mv === -1}">${THUMB}</button>
    </div>`;

  const badge = awaiting
    ? `<span class="badge-awaiting">Awaiting</span>`
    : `<span class="fit-badge ${fitClass}">FIT ${esc(o.fit ?? "?")}</span>`;

  // body
  const docs = (o.requiredDocs && o.requiredDocs.length)
    ? `<div class="docs"><span class="k">Required</span><ul>${o.requiredDocs.map((d) => `<li>${esc(d)}</li>`).join("")}</ul></div>`
    : "";
  const lockNote = awaiting ? `<span class="badge-awaiting">Needs research to pursue</span>` : "";

  const documents = (o.documents && o.documents.length)
    ? `<div class="documents">
        <div class="documents-head">
          <span class="k">Documents</span>
          <button class="mini doc-dl" data-download="${o.id}" title="Download all ${o.documents.length} files as a zip" aria-label="Download all documents as a zip">${DL}<span>Download all</span></button>
        </div>
        <ul>${o.documents.map((d) => `<li><a href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.label || d.url)} ↗</a></li>`).join("")}</ul>
      </div>`
    : "";

  const body = `<div class="card-body"><div class="card-body-inner"><div class="card-body-pad">
    ${o.fitRationale ? `<div class="card-row"><span class="k">Why it fits</span>${esc(o.fitRationale)}</div>` : ""}
    ${o.territory ? `<div class="card-row"><span class="k">Territory</span>${esc(o.territory)}</div>` : ""}
    ${o.budget ? `<div class="card-row"><span class="k">Budget</span>${esc(o.budget)}</div>` : ""}
    ${o.eligibility ? `<div class="card-row"><span class="k">Eligibility</span>${esc(o.eligibility)}</div>` : ""}
    ${o.link ? `<div class="card-link"><a href="${esc(o.link)}" target="_blank" rel="noopener">Open call ↗</a></div>` : ""}
    ${docs}
    ${documents}
    <div class="card-row"><span class="k">Country</span>
      ${countrySelect(o)}
    </div>
    <div class="card-row"><span class="k">Owner</span>
      <input class="card-field" data-field="owner" data-id="${o.id}" value="${esc(ownerVal)}" placeholder="unassigned" />
    </div>
    <div class="card-row"><span class="k">Notes</span>
      <textarea class="card-field" data-field="notes" data-id="${o.id}" placeholder="Add a note…">${esc(notesVal)}</textarea>
    </div>
    <div class="card-savebar ${dirty ? "show" : ""}">
      <span class="savebar-note">Unsaved changes to this card</span>
      <button class="mini" data-save-card="${o.id}">Save</button>
      <button class="mini subtle" data-discard-card="${o.id}">Discard</button>
    </div>
    <div class="card-actions">
      ${moveButtons(o, researched)}
      ${researched ? `<button class="mini" data-duplicate="${o.id}">Duplicate</button>` : ""}
      ${lockNote}
      <button class="mini danger" data-del="${o.id}">Delete</button>
    </div>
  </div></div></div>`;

  // Compact (archived) cards show only title + FIT + chevron in the collapsed head;
  // the full body (incl. votes via expand) is unchanged.
  const headMain = compact
    ? `<div class="card-headmain"><div class="card-title">${esc(o.title)}</div></div>`
    : `<div class="card-headmain">
        <div class="card-title">${esc(o.title)}</div>
        ${chipsRow}
        ${subText ? `<div class="card-sub">${subText}</div>` : ""}
        ${meta}
      </div>`;
  const headAside = compact
    ? `<div class="card-aside">${badge}<span class="chevron">${CHEV}</span></div>`
    : `<div class="card-aside">${votes}${badge}<span class="chevron">${CHEV}</span></div>`;

  return `<div class="card ${awaiting ? "awaiting" : ""} ${compact ? "compact" : ""} ${dirty ? "dirty" : ""} ${open ? "open" : ""} ${revealed ? "" : "reveal"}" data-id="${o.id}" data-researched="${researched}">
    <div class="card-head" data-toggle="${o.id}">
      <span class="drag-handle" title="Drag to move" aria-label="Drag to move">${GRIP}</span>
      ${headMain}
      ${headAside}
    </div>
    ${body}
  </div>`;
}

function fillList(id, items) {
  const el = document.getElementById(id);
  el.innerHTML = items.length ? items.map(card).join("") : "";
}

function render() {
  const all = STATE.opportunities || [];
  // priority order: highest net team vote first, then higher fit
  const byPriority = (a, b) => (score(b) - score(a)) || ((b.fit || 0) - (a.fit || 0));

  const inbox = all.filter((o) => (o.status || "new") === "new");
  const ready = inbox.filter(isResearched).sort(byPriority);
  const awaiting = inbox.filter((o) => !isResearched(o)).sort(byPriority);
  const pursuing = all.filter((o) => o.status === "pursuing").sort(byPriority);
  const archived = all.filter((o) => o.status === "archived").sort(byPriority);

  fillList("col-new-ready", ready);
  fillList("col-new-awaiting", awaiting);
  fillList("col-pursuing", pursuing);
  fillList("col-archived", archived);

  // empty-state teaching copy
  if (!ready.length) $("#col-new-ready").innerHTML = `<div class="empty">Researched opportunities ready to pursue appear here.</div>`;
  if (!awaiting.length) $("#col-new-awaiting").innerHTML = `<div class="empty">Suggest one with “+ Suggest”. It waits here for the next research session.</div>`;
  if (!pursuing.length) $("#col-pursuing").innerHTML = `<div class="empty">Move a ready opportunity here once you commit to it.</div>`;
  if (!archived.length) $("#col-archived").innerHTML = `<div class="empty">Passed-on and closed opportunities rest here.</div>`;

  $("#count-new").textContent = ready.length + awaiting.length;
  $("#count-pursuing").textContent = pursuing.length;
  $("#count-archived").textContent = archived.length;

  const lu = STATE.meta && STATE.meta.lastUpdated;
  $("#updated").textContent = lu ? "Updated " + new Date(lu).toLocaleString() : "";

  bindCards();
  initSortables();
  doReveal();
  renderSaveState();
}

function bindCards() {
  document.querySelectorAll(".card-head").forEach((h) =>
    h.addEventListener("click", (e) => {
      if (e.target.closest(".drag-handle")) return;
      const id = h.dataset.toggle;
      const cardEl = h.closest(".card");
      if (EXPANDED.has(id)) { EXPANDED.delete(id); cardEl.classList.remove("open"); }
      else { EXPANDED.add(id); cardEl.classList.add("open"); }
    }));
  document.querySelectorAll(".drag-handle").forEach((h) =>
    h.addEventListener("click", (e) => e.stopPropagation()));
  document.querySelectorAll("[data-vote]").forEach((b) =>
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = b.dataset.id;
      const o = (STATE.opportunities || []).find((x) => x.id === id);
      const cur = (o && o.votes && o.votes[actor()]) || 0;
      const want = Number(b.dataset.vote);
      patch(id, { vote: cur === want ? 0 : want });   // click again to clear your vote
    }));
  document.querySelectorAll("[data-country]").forEach((el) =>
    el.addEventListener("change", (e) => { e.stopPropagation(); patch(el.dataset.id, { country: el.value }); }));
  document.querySelectorAll("[data-duplicate]").forEach((b) =>
    b.addEventListener("click", (e) => { e.stopPropagation(); duplicateOpp(b.dataset.duplicate); }));
  document.querySelectorAll("[data-download]").forEach((b) =>
    b.addEventListener("click", (e) => { e.stopPropagation(); downloadEdition(b, b.dataset.download); }));
  document.querySelectorAll("[data-move]").forEach((b) =>
    b.addEventListener("click", () => patch(b.dataset.id, { status: b.dataset.move })));
  document.querySelectorAll("[data-del]").forEach((b) =>
    b.addEventListener("click", () => askDelete(b.dataset.del)));
  // typed fields stage locally (commit on Save), not on every change
  document.querySelectorAll("[data-field]").forEach((el) =>
    el.addEventListener("input", () => stageField(el.dataset.id, el.dataset.field, el.value)));
  document.querySelectorAll("[data-save-card]").forEach((b) =>
    b.addEventListener("click", (e) => { e.stopPropagation(); saveCard(b.dataset.saveCard); }));
  document.querySelectorAll("[data-discard-card]").forEach((b) =>
    b.addEventListener("click", (e) => { e.stopPropagation(); discardCard(b.dataset.discardCard); }));
}

function doReveal() {
  if (revealed) return;
  const cards = document.querySelectorAll(".card.reveal");
  requestAnimationFrame(() => cards.forEach((c, i) => setTimeout(() => c.classList.add("visible"), i * 40)));
  revealed = true;
}

// ---------- drag and drop ----------
let sortables = [];
function destroySortables() { sortables.forEach((s) => { try { s.destroy(); } catch {} }); sortables = []; }
function initSortables() {
  if (typeof Sortable === "undefined") return;   // buttons still work
  destroySortables();
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  ["col-new-ready", "col-new-awaiting", "col-pursuing", "col-archived"].forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    sortables.push(new Sortable(el, {
      group: "board",
      handle: ".drag-handle",
      animation: reduce ? 0 : 160,
      delayOnTouchOnly: true,
      delay: 120,
      fallbackTolerance: 4,
      ghostClass: "sortable-ghost",
      chosenClass: "sortable-chosen",
      dragClass: "sortable-drag",
      onMove: onDragMove,
      onEnd: onDragEnd,
    }));
  });
}
function onDragMove(evt) {
  const to = evt.to.dataset.list;
  const researched = evt.dragged.dataset.researched === "true";
  if (to === "awaiting") return false;            // can't drop into awaiting (no un-research)
  if (to === "pursuing" && !researched) return false;  // lock: needs research
  if (to === "ready" && !researched) return false;     // can't self-promote to ready
  return true;
}
function onDragEnd(evt) {
  const from = evt.from.dataset.list, to = evt.to.dataset.list;
  if (from === to) return;                          // reorder within a list — not persisted
  patch(evt.item.dataset.id, { status: LIST_STATUS[to] });
}

// ---------- dialogs ----------
function openDialog(d) { d.showModal(); }
function closeDialog(d) { d.close(); }
document.querySelectorAll("dialog [data-close]").forEach((b) =>
  b.addEventListener("click", () => b.closest("dialog").close()));
document.querySelectorAll("dialog").forEach((d) =>
  d.addEventListener("click", (e) => { if (e.target === d) d.close(); }));   // backdrop click

// add / suggest
$("#add").addEventListener("click", () => {
  $("#add-error").textContent = "";
  if ($("#add-country") && !$("#add-country").options.length) $("#add-country").innerHTML = countryOptions("");
  $("#add-form").reset();
  $("#add-by").value = localStorage.getItem("inland_actor") || "";
  openDialog($("#add-dialog"));
  setTimeout(() => $("#add-title").focus(), 50);
});
$("#add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = $("#add-title").value.trim();
  const link = $("#add-link").value.trim();
  const addedBy = $("#add-by").value.trim();
  const country = $("#add-country") ? $("#add-country").value : "";
  if (!title) { $("#add-error").textContent = "Give the opportunity a name."; return; }
  if (!addedBy) { $("#add-error").textContent = "Add your name so it’s tagged to you."; return; }
  setActor(addedBy);
  const r = await fetch("/api/opportunities", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ opportunity: { title, link, addedBy, country } }),
  });
  if (!r.ok) { $("#add-error").textContent = "Could not save — try again."; return; }
  STATE = await r.json();
  render();
  closeDialog($("#add-dialog"));
  toast("Suggested — awaiting research");
});

// delete confirm
let pendingDelete = null;
function askDelete(id) {
  pendingDelete = id;
  const o = (STATE.opportunities || []).find((x) => x.id === id);
  $("#confirm-text").innerHTML = o
    ? `Delete <b>${esc(o.title)}</b>? This removes it permanently and commits the change.`
    : "This removes it permanently and commits the change.";
  openDialog($("#confirm-dialog"));
}
$("#confirm-yes").addEventListener("click", async () => {
  closeDialog($("#confirm-dialog"));
  if (pendingDelete) { await removeOpp(pendingDelete); pendingDelete = null; }
});

// name capture
$("#identity").addEventListener("click", () => {
  $("#name-input").value = localStorage.getItem("inland_actor") || "";
  openDialog($("#name-dialog"));
  setTimeout(() => $("#name-input").focus(), 50);
});
$("#name-form").addEventListener("submit", (e) => {
  e.preventDefault();
  setActor($("#name-input").value);
  closeDialog($("#name-dialog"));
});

// ---------- chrome ----------
$("#refresh").addEventListener("click", () => {
  if (DRAFTS.size && !confirm("Refresh and discard your unsaved changes?")) return;
  DRAFTS.clear();
  load();
});
window.addEventListener("beforeunload", (e) => {
  if (DRAFTS.size) { e.preventDefault(); e.returnValue = ""; }
});
let toastTimer;
function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.remove("hidden");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.add("hidden"), 1800);
}
function showGate() { $("#gate").classList.remove("hidden"); $("#app").classList.add("hidden"); }
function showApp() { $("#gate").classList.add("hidden"); $("#app").classList.remove("hidden"); }
function showLoadError(msg) { const el = $("#load-error"); if (!el) return; el.textContent = msg; el.classList.remove("hidden"); }
function hideLoadError() { const el = $("#load-error"); if (!el) return; el.textContent = ""; el.classList.add("hidden"); }

async function boot() { showApp(); renderIdentity(); await load(); }

(async function init() {
  if (await checkAuth()) boot();
  else showGate();
})();
