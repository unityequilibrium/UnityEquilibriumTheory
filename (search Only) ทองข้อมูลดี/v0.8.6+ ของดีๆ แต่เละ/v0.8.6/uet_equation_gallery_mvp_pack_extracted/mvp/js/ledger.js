// Ledger: simple backup/replay layer for runs (localStorage + export/import)
// Key idea: every Run becomes a RunRecord and can be exported as JSON.

const LEDGER_KEY = "uet_ledger_v1";

export function loadLedger() {
  try {
    const raw = localStorage.getItem(LEDGER_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveLedger(records) {
  localStorage.setItem(LEDGER_KEY, JSON.stringify(records));
}

export function addRunRecord(record) {
  const ledger = loadLedger();
  ledger.unshift(record);
  // keep last N (small MVP)
  const trimmed = ledger.slice(0, 200);
  saveLedger(trimmed);
  return trimmed;
}

export function exportLedger() {
  const ledger = loadLedger();
  const blob = new Blob([JSON.stringify(ledger, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const ts = new Date().toISOString().slice(0,19).replace(/[:T]/g, "-");
  a.href = url;
  a.download = `uet_runs_${ts}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function importLedgerFromFile(file) {
  const text = await file.text();
  const parsed = JSON.parse(text);
  if (!Array.isArray(parsed)) throw new Error("Invalid ledger JSON (expected array).");
  saveLedger(parsed);
  return parsed;
}

export function clearLedger() {
  localStorage.removeItem(LEDGER_KEY);
}
