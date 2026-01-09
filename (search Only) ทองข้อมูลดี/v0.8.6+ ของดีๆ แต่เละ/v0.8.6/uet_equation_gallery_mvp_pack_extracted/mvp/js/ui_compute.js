import { LocalRunner } from "./local_runner.js";
import { ApiRunner } from "./api_runner.js";
import { addRunRecord, exportLedger, importLedgerFromFile, clearLedger, loadLedger } from "./ledger.js";

function nowIso() { return new Date().toISOString(); }
function makeRunId() { return "run_" + Math.random().toString(16).slice(2) + "_" + Date.now(); }

function pickRunner(equationDef) {
  const kind = equationDef?.runner?.kind || "local";
  if (kind === "api") return new ApiRunner("");
  return new LocalRunner();
}

export function renderComputePanel(containerEl, equationDef, onAfterRun) {
  // Build inputs
  const inputs = equationDef.inputs || [];
  const outputs = equationDef.outputs || [];

  const inputHtml = inputs.map(inp => {
    const step = (typeof inp.step === "number") ? `step="${inp.step}"` : `step="any"`;
    const min = (typeof inp.min === "number") ? `min="${inp.min}"` : "";
    const max = (typeof inp.max === "number") ? `max="${inp.max}"` : "";
    const unit = inp.unit ? `<span class="unit">${inp.unit}</span>` : "";
    return `
      <label class="field">
        <span class="label">${escapeHtml(inp.label)}</span>
        <span class="row">
          <input data-key="${escapeAttr(inp.key)}" type="number" ${step} ${min} ${max} value="${escapeAttr(String(inp.default ?? 0))}">
          ${unit}
        </span>
      </label>`;
  }).join("");

  const outputHtml = outputs.map(out => `
      <div class="kv">
        <span class="k">${escapeHtml(out.label)}</span>
        <span class="v" data-out="${escapeAttr(out.key)}">—</span>
      </div>`).join("");

  containerEl.innerHTML = `
    <details open class="compute">
      <summary>🧮 Compute</summary>
      <div class="compute-grid">
        <div class="panel">
          <div class="panel-title">Inputs</div>
          <div class="fields">${inputHtml}</div>
          <div class="actions">
            <button class="btn primary" id="btn-run">Run</button>
            <span class="status" id="run-status"></span>
          </div>
        </div>
        <div class="panel">
          <div class="panel-title">Outputs</div>
          <div class="outputs">${outputHtml}</div>
          <div class="actions">
            <button class="btn" id="btn-export">Export Ledger</button>
            <label class="btn filelike">
              Import Ledger
              <input type="file" id="file-import" accept="application/json" style="display:none;">
            </label>
            <button class="btn" id="btn-clear">Clear Ledger</button>
          </div>
          <div class="ledger-mini" id="ledger-mini"></div>
        </div>
      </div>
      <div class="hint">
        Backup: every run auto-saves to localStorage as a RunRecord. Use Export/Import to move runs.
      </div>
    </details>
  `;

  const btnRun = containerEl.querySelector("#btn-run");
  const runStatus = containerEl.querySelector("#run-status");

  const btnExport = containerEl.querySelector("#btn-export");
  const fileImport = containerEl.querySelector("#file-import");
  const btnClear = containerEl.querySelector("#btn-clear");
  const ledgerMini = containerEl.querySelector("#ledger-mini");

  refreshLedgerMini(ledgerMini);

  btnExport.addEventListener("click", () => exportLedger());
  fileImport.addEventListener("change", async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await importLedgerFromFile(file);
      refreshLedgerMini(ledgerMini);
      runStatus.textContent = "Imported ✓";
    } catch (err) {
      runStatus.textContent = String(err?.message || err);
    } finally {
      fileImport.value = "";
    }
  });

  btnClear.addEventListener("click", () => {
    clearLedger();
    refreshLedgerMini(ledgerMini);
    runStatus.textContent = "Cleared ✓";
  });

  btnRun.addEventListener("click", async () => {
    runStatus.textContent = "Running…";
    btnRun.disabled = true;
    try {
      const params = readParams(containerEl);
      const runner = pickRunner(equationDef);
      const result = await runner.run(equationDef, params);
      writeOutputs(containerEl, result);

      const record = {
        run_id: makeRunId(),
        created_at: nowIso(),
        equation_id: equationDef.id,
        params,
        result,
        source: equationDef?.runner?.kind === "api" ? "api" : "local"
      };
      addRunRecord(record);
      refreshLedgerMini(ledgerMini);

      runStatus.textContent = "Saved ✓";
      onAfterRun?.(record);
    } catch (err) {
      runStatus.textContent = String(err?.message || err);
    } finally {
      btnRun.disabled = false;
    }
  });
}

function readParams(root) {
  const inputs = root.querySelectorAll("input[data-key]");
  const params = {};
  inputs.forEach(el => {
    const k = el.getAttribute("data-key");
    params[k] = el.value;
  });
  return params;
}

function writeOutputs(root, result) {
  const outEls = root.querySelectorAll("[data-out]");
  outEls.forEach(el => {
    const k = el.getAttribute("data-out");
    const v = (result && Object.prototype.hasOwnProperty.call(result, k)) ? result[k] : undefined;
    el.textContent = (typeof v === "number" && Number.isFinite(v)) ? formatNum(v) : (v ?? "—");
  });
}

function refreshLedgerMini(el) {
  const ledger = loadLedger().slice(0, 6);
  if (!ledger.length) {
    el.innerHTML = `<div class="mini-empty">No runs yet.</div>`;
    return;
  }
  el.innerHTML = ledger.map(r => `
    <div class="mini-row">
      <span class="mini-eq">${escapeHtml(r.equation_id)}</span>
      <span class="mini-time">${escapeHtml(r.created_at.slice(0,19).replace("T"," "))}</span>
    </div>
  `).join("");
}

function formatNum(x) {
  // readable, stable for demos
  const abs = Math.abs(x);
  if (abs !== 0 && (abs < 1e-4 || abs >= 1e6)) return x.toExponential(6);
  return String(Math.round(x * 1e6) / 1e6);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}
function escapeAttr(s) { return escapeHtml(s).replace(/`/g, "&#96;"); }
