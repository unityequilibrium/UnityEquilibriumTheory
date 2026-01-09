// ApiRunner stub (optional future): switch runner.kind to "api" and provide endpoint.
// Endpoint suggestion: POST /api/run { equation_id, params } -> { result, run_id? }

export class ApiRunner {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
  }

  async run(equationDef, params) {
    const endpoint = equationDef?.runner?.endpoint || "/api/run";
    const res = await fetch(this.baseUrl + endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ equation_id: equationDef.id, params })
    });
    if (!res.ok) throw new Error(`API run failed: ${res.status}`);
    const data = await res.json();
    if (!data || typeof data !== "object") throw new Error("Invalid API response");
    return data.result ?? data;
  }
}
