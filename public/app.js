// INLAND Opportunities — dashboard client.
const $ = (s) => document.querySelector(s);
let STATE = { opportunities: [], meta: {} };

const STATUSES = ["new", "pursuing", "archived"];
const FIT_CLASS = { 5: "f5", 4: "f4", 3: "f3", 2: "f2", 1: "f1" };

// ---------- auth ----------
async function checkAuth() {
  const r = await fetch("/api/login");
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
  await fetch("/api/login", { method: "DELETE" });
  location.reload();
});

// ---------- data ----------
async function load() {
  const r = await fetch("/api/opportunities");
  if (r.status === 401) { showGate(); return; }
  STATE = await r.json();
  render();
}
async function patch(id, changes) {
  toast("Saving…");
  const r = await fetch("/api/opportunities", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, changes, actor: actor() }),
  });
  if (!r.ok) { toast("Save failed"); return; }
  STATE = await r.json();
  render();
  toast("Saved");
}
async function removeOpp(id) {
  if (!confirm("Delete this opportunity permanently?")) return;
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
async function addOpp() {
  const title = prompt("Opportunity title?");
  if (!title) return;
  const funder = prompt("Funder / host?") || "";
  const r = await fetch("/api/opportunities", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ opportunity: { title, funder, fit: 3, status: "new", addedBy: actor() } }),
  });
  if (!r.ok) { toast("Add failed"); return; }
  STATE = await r.json();
  render();
  toast("Added");
}

function actor() {
  let a = localStorage.getItem("inland_actor");
  if (!a) { a = prompt("Your name (for the edit log)?") || "anon"; localStorage.setItem("inland_actor", a); }
  return a;
}

// ---------- render ----------
function daysUntil(d) {
  if (!d) return null;
  const ms = new Date(d).getTime() - Date.now();
  return Math.ceil(ms / 86400000);
}
function esc(s) { return (s ?? "").toString().replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

function card(o) {
  const fitClass = FIT_CLASS[o.fit] || "f3";
  const dleft = daysUntil(o.deadline);
  const urgent = dleft !== null && dleft <= 21 && o.status !== "archived";
  const deadlineRow = o.deadline
    ? `<div class="card-row ${urgent ? "urgent" : ""}"><span class="k">Deadline:</span> ${esc(o.deadline)}${dleft !== null ? ` (${dleft}d${urgent ? " — URGENT" : ""})` : ""}</div>`
    : "";
  const docs = (o.requiredDocs && o.requiredDocs.length)
    ? `<div class="docs">Required: <ul>${o.requiredDocs.map((d) => `<li>${esc(d)}</li>`).join("")}</ul></div>`
    : "";
  const moveButtons = STATUSES.filter((s) => s !== o.status)
    .map((s) => `<button class="mini" data-move="${s}" data-id="${o.id}">→ ${s}</button>`).join("");

  return `<div class="card" data-id="${o.id}">
    <div class="card-top">
      <div>
        <div class="card-title">${esc(o.title)}</div>
        <div class="card-funder">${esc(o.funder)}${o.channel ? " · " + esc(o.channel) : ""}</div>
      </div>
      <span class="fit-badge ${fitClass}">FIT ${esc(o.fit ?? "?")}</span>
    </div>
    ${o.fitRationale ? `<div class="card-row"><span class="k">Why:</span> ${esc(o.fitRationale)}</div>` : ""}
    ${o.territory ? `<div class="card-row"><span class="k">Territory:</span> ${esc(o.territory)}</div>` : ""}
    ${o.budget ? `<div class="card-row"><span class="k">Budget:</span> ${esc(o.budget)}</div>` : ""}
    ${deadlineRow}
    ${o.link ? `<div class="card-row"><a href="${esc(o.link)}" target="_blank" rel="noopener">Open call ↗</a></div>` : ""}
    ${docs}
    <div class="card-row"><span class="k">Owner:</span>
      <input data-field="owner" data-id="${o.id}" value="${esc(o.owner)}" placeholder="unassigned" />
    </div>
    <div class="card-row"><span class="k">Notes:</span>
      <textarea data-field="notes" data-id="${o.id}" placeholder="Add a note…">${esc(o.notes)}</textarea>
    </div>
    <div class="card-actions">
      ${moveButtons}
      <button class="mini danger" data-del="${o.id}">Delete</button>
    </div>
  </div>`;
}

function render() {
  for (const st of STATUSES) {
    const items = STATE.opportunities.filter((o) => (o.status || "new") === st)
      .sort((a, b) => (b.fit || 0) - (a.fit || 0));
    $("#col-" + st).innerHTML = items.map(card).join("") || `<div class="docs">Nothing here.</div>`;
    $("#count-" + st).textContent = items.length;
  }
  const lu = STATE.meta && STATE.meta.lastUpdated;
  $("#updated").textContent = lu ? "Updated " + new Date(lu).toLocaleString() : "";
  bindCards();
}

function bindCards() {
  document.querySelectorAll("[data-move]").forEach((b) =>
    b.addEventListener("click", () => patch(b.dataset.id, { status: b.dataset.move })));
  document.querySelectorAll("[data-del]").forEach((b) =>
    b.addEventListener("click", () => removeOpp(b.dataset.del)));
  document.querySelectorAll("[data-field]").forEach((el) =>
    el.addEventListener("change", () => patch(el.dataset.id, { [el.dataset.field]: el.value })));
}

// ---------- chrome ----------
$("#refresh").addEventListener("click", load);
$("#add").addEventListener("click", addOpp);
let toastTimer;
function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.remove("hidden");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.add("hidden"), 1600);
}
function showGate() { $("#gate").classList.remove("hidden"); $("#app").classList.add("hidden"); }
function showApp() { $("#gate").classList.add("hidden"); $("#app").classList.remove("hidden"); }

async function boot() { showApp(); await load(); }

(async function init() {
  if (await checkAuth()) boot();
  else showGate();
})();
