import { renderComputePanel } from "./ui_compute.js";

async function loadEquations() {
  const res = await fetch("./data/equations.json");
  if (!res.ok) throw new Error("Failed to load equations.json");
  return await res.json();
}

function makeThumbSvg(text) {
  const safe = String(text).replace(/[<>&"]/g, (c)=>({ "<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;" }[c]));
  const svg = `
  <svg xmlns="http://www.w3.org/2000/svg" width="640" height="360">
    <defs>
      <linearGradient id="g" x1="0" x2="1">
        <stop offset="0" stop-color="#12121a"/>
        <stop offset="1" stop-color="#16161f"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" rx="24" fill="url(#g)"/>
    <text x="50%" y="45%" text-anchor="middle" font-family="Inter, system-ui, sans-serif" font-size="28" fill="#e6e6e6">${safe}</text>
    <text x="50%" y="62%" text-anchor="middle" font-family="Inter, system-ui, sans-serif" font-size="16" fill="#8b8b9a">Interactive Equation</text>
  </svg>`;
  return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
}

function byId(id) { return document.getElementById(id); }

function createEquationCard(eq) {
  const card = document.createElement("div");
  card.className = "card";
  card.onclick = () => openEquationModal(eq);

  const img = document.createElement("img");
  img.src = makeThumbSvg(eq.title);
  img.alt = eq.title;

  const info = document.createElement("div");
  info.className = "info";

  const h3 = document.createElement("h3");
  h3.textContent = eq.title;

  const p = document.createElement("p");
  p.className = "desc";
  p.textContent = eq.description || "";

  const tags = document.createElement("div");
  tags.className = "tags";
  tags.innerHTML = `<span class="tag pass">RUNNABLE</span>`;

  info.appendChild(h3);
  info.appendChild(p);
  info.appendChild(tags);
  card.appendChild(img);
  card.appendChild(info);
  return card;
}

function openEquationModal(eq) {
  // reuse existing modal DOM
  byId("modal-gif").src = makeThumbSvg(eq.formula_text || eq.title);
  byId("modal-title").textContent = eq.title;
  byId("modal-desc").textContent = eq.description || "";

  // show compute; hide params/metrics + fallback
  const pm = byId("params-metrics-grid");
  const fb = byId("fallback-details");
  if (pm) pm.style.display = "none";
  if (fb) fb.style.display = "none";

  const compute = byId("compute-panel");
  compute.style.display = "block";
  renderComputePanel(compute, eq);

  // actions (keep small)
  byId("modal-actions").innerHTML = `
    <button class="btn" onclick="window.scrollTo({top:0,behavior:'smooth'})">Back to Top</button>
  `;

  byId("modal").classList.add("active");
  document.body.style.overflow = "hidden";
}

// Bootstrap
(async function init() {
  const eqs = await loadEquations();

  // Create a new section under existing content
  const host = byId("uet-equations-host");
  if (!host) return;
  eqs.forEach(eq => host.appendChild(createEquationCard(eq)));
})();
