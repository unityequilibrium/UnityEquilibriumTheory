/**
 * main app.js - UET Harness UI Logic
 * Handles data fetching from run directories and triggers component updates.
 */

class UETDashboard {
    constructor() {
        this.currentRunDir = null;
        this.config = null;
        this.metrics = null;
        this.summary = null;
        this.gates = null;
        this.timeseries = null;
        this.chart = null;


        this.initEventListeners();

        // Auto-load if static data is present
        if (window.UET_STATIC_DATA) {
            this.loadRunData(null);
        }
    }

    initEventListeners() {
        document.getElementById('load-run-btn').addEventListener('click', () => this.toggleModal(true));
        document.getElementById('refresh-btn').addEventListener('click', () => this.reloadCurrentRun());
        document.getElementById('modal-cancel').addEventListener('click', () => this.toggleModal(false));
        document.getElementById('modal-load').addEventListener('click', () => this.handleLoadClick());
        document.getElementById('run-path-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLoadClick();
        });
    }

    toggleModal(show) {
        document.getElementById('load-modal').classList.toggle('hidden', !show);
        if (show) document.getElementById('run-path-input').focus();
    }

    handleLoadClick() {
        const path = document.getElementById('run-path-input').value.trim();
        if (path) {
            this.loadRunData(path);
            this.toggleModal(false);
        }
    }

    async reloadCurrentRun() {
        if (this.currentRunDir) {
            await this.loadRunData(this.currentRunDir);
        }
    }

    async loadRunData(runDir) {
        console.log(`Attempting to load run from: ${runDir}`);
        this.currentRunDir = runDir;

        // STATIC MODE: Check if data is already injected (for server-free reports)
        if (window.UET_STATIC_DATA) {
            console.log("Loading from STATIC DATA");
            const data = window.UET_STATIC_DATA;
            this.config = data.config;
            this.metrics = data.metrics;
            this.summary = data.summary;
            this.gates = data.gates;
            this.timeseries = this.parseCSV(data.timeseries);
            this.renderAll();
            return;
        }

        // DYNAMIC MODE: Fetch from server/file
        // unless opened with --allow-file-access-from-files or served via python -m http.server
        try {
            // Standardise path for fetch (handle Windows backslashes)
            const basePath = runDir.replace(/\\/g, '/');

            // Parallel fetch of all artifacts
            const [cfgRes, metRes, sumRes, gateRes, tsRes] = await Promise.all([
                fetch(`${basePath}/config.json`).then(r => r.ok ? r.json() : null).catch(() => null),
                fetch(`${basePath}/metrics.json`).then(r => r.ok ? r.json() : null).catch(() => null),
                fetch(`${basePath}/summary.json`).then(r => r.ok ? r.json() : null).catch(() => null),
                fetch(`${basePath}/gate_report.json`).then(r => r.ok ? r.json() : null).catch(() => null),
                fetch(`${basePath}/timeseries.csv`).then(r => r.ok ? r.text() : null).catch(() => null)
            ]);

            this.config = cfgRes;
            this.metrics = metRes;
            this.summary = sumRes;
            this.gates = gateRes;
            this.timeseries = this.parseCSV(tsRes);

            this.renderAll();
        } catch (err) {
            console.error("Failed to load artifacts:", err);
            alert("Failed to load run data. Check console for details. (Note: browser CORS may block local file access without a server)");
        }
    }

    parseCSV(csvText) {
        if (!csvText) return null;
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        return lines.slice(1).map(line => {
            const vals = line.split(',');
            const obj = {};
            headers.forEach((h, i) => {
                obj[h.trim()] = parseFloat(vals[i]);
            });
            return obj;
        });
    }

    renderAll() {
        this.renderHeader();
        this.renderConfig();
        this.renderMetrics();
        this.renderGates();
        this.renderChart();
        this.renderVisuals(); // NEW
        this.renderFooter();
    }

    renderVisuals() {
        const section = document.getElementById('visuals-section');
        const grid = document.getElementById('visuals-grid');
        const visuals = window.UET_STATIC_DATA?.visuals || [];

        if (visuals.length === 0) {
            section.classList.add('hidden');
            return;
        }

        section.classList.remove('hidden');
        let html = '';
        visuals.forEach(v => {
            html += `
                <div class="visual-item">
                    <img src="${v.url}" alt="${v.name}">
                    <div class="visual-label">${v.name}</div>
                </div>
            `;
        });
        grid.innerHTML = html;
    }

    renderHeader() {
        const runId = this.summary?.run_id || this.summary?.case_id || this.config?.run_id || "Unknown";
        document.getElementById('current-run-id').textContent = runId.substring(0, 16) + (runId.length > 16 ? '...' : '');

        const status = (this.summary?.status || this.summary?.grade || "N/A").toUpperCase();
        const badge = document.getElementById('overall-status');
        badge.textContent = status;
        badge.className = `status-badge status-${status}`;
    }

    renderConfig() {
        const container = document.getElementById('config-content');
        if (!this.config) {
            container.innerHTML = '<p class="placeholder">Config not found.</p>';
            return;
        }

        let html = '';
        const sections = [
            { label: 'Model', val: this.config.model },
            { label: 'Grid', val: `${this.config.grid?.N || '?'}×${this.config.grid?.N || '?'}` },
            { label: 'Domain', val: `L=${this.config.domain?.L || '?'}` },
            { label: 'Time Step (Δt)', val: `${this.config.time?.dt || '?'} s` },
            { label: 'Steps', val: this.config.time?.max_steps || '?' },
            { label: 'Integrator', val: this.config.integrator?.name || '?' }
        ];

        sections.forEach(s => {
            html += `
                <div class="config-item">
                    <span class="config-key">${s.label}:</span>
                    <span class="config-val">${s.val}</span>
                </div>
            `;
        });

        // Add params if available
        const params = this.config.params || {};
        if (Object.keys(params).length > 0) {
            html += '<h3 style="font-size: 0.9rem; margin-top: 1rem; opacity: 0.7;">Physical Parameters</h3>';

            // Flatten parameters for better display (e.g. pot, physics constants)
            const flat = {};
            for (const [k, v] of Object.entries(params)) {
                if (typeof v === 'object' && v !== null) {
                    for (const [subK, subV] of Object.entries(v)) {
                        flat[`${k}.${subK}`] = subV;
                    }
                } else {
                    flat[k] = v;
                }
            }

            for (const [k, v] of Object.entries(flat)) {
                html += `
                    <div class="config-item">
                        <span class="config-key">${k}:</span>
                        <span class="config-val">${typeof v === 'number' ? v.toFixed(4) : v}</span>
                    </div>
                `;
            }
        }

        container.innerHTML = html;
    }

    renderMetrics() {
        const container = document.getElementById('metrics-container');
        if (!this.metrics && !this.summary) {
            container.innerHTML = '<p class="placeholder">No metrics recorded.</p>';
            return;
        }

        // Official Metric Definitions (from uet_core/metrics.py)
        const SYMBOLS = {
            "Omega0": { label: "Ω₀", unit: "slm" },
            "OmegaT": { label: "Ω_T", unit: "slm" },
            "dt": { label: "Δt", unit: "s" },
            "dx": { label: "Δx", unit: "m" },
            "energy": { label: "E", unit: "slm" },
            "com": { label: "COM", unit: "slm" },
            "max_dt": { label: "max Δt", unit: "s" },
            "runtime_s": { label: "Runtime", unit: "s" },
            "steps_total": { label: "Steps", unit: "" },
            "max_abs_C": { label: "max |C|", unit: "" },
            "max_abs_I": { label: "max |I|", unit: "" }
        };

        const combined = {};

        // 1. Load metrics.json data
        if (this.metrics) {
            for (const [k, v] of Object.entries(this.metrics)) {
                const def = SYMBOLS[k] || { label: v.label || k, unit: v.unit || '' };
                combined[k] = { label: def.label, value: v.value, unit: def.unit };
            }
        }

        // 2. Fallback to summary.json data
        if (Object.keys(combined).length === 0 && this.summary) {
            Object.keys(SYMBOLS).forEach(k => {
                if (this.summary[k] !== undefined) {
                    combined[k] = { label: SYMBOLS[k].label, value: this.summary[k], unit: SYMBOLS[k].unit };
                }
            });
        }

        if (Object.keys(combined).length === 0) {
            container.innerHTML = `
                <div class="placeholder">
                    <span>No physics metrics recorded for this model variation.</span>
                    <small style="opacity: 0.5; font-size: 0.8rem;">(Check config for model specifics)</small>
                </div>
            `;
            return;
        }

        let html = '';
        for (const [key, data] of Object.entries(combined)) {
            html += `
                <div class="metric-card glass">
                    <span class="metric-label">${data.label}</span>
                    <div class="metric-body">
                        <span class="metric-value">${typeof data.value === 'number' ? data.value.toFixed(4) : data.value}</span>
                        <span class="metric-unit">${data.unit}</span>
                    </div>
                </div>
            `;
        }
        container.innerHTML = html;
    }

    renderGates() {
        const container = document.getElementById('gates-content');
        
        // Try 1: gate_report.json format (legacy)
        if (this.gates && this.gates.gates) {
            let html = '';
            this.gates.gates.forEach(gate => {
                html += `
                    <div class="gate-item gate-${gate.status}">
                        <div class="gate-header">
                            <span>${gate.id}</span>
                            <span class="status-badge status-${gate.status}">${gate.status}</span>
                        </div>
                        <div class="gate-msg">${gate.message}</div>
                        <div class="gate-meta" style="font-size: 0.7rem; opacity: 0.5; margin-top: 0.5rem">
                            val: ${gate.value.toFixed(6)} | tol: ${gate.tolerance}
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
            return;
        }
        
        // Try 2: verification_gates from summary.json (new format)
        const vGates = this.summary?.verification_gates;
        if (vGates && Object.keys(vGates).length > 0) {
            let html = '';
            for (const [name, status] of Object.entries(vGates)) {
                const statusClass = status === 'PASS' ? 'pass' : status === 'FAIL' ? 'fail' : 'warn';
                html += `
                    <div class="gate-item gate-${statusClass}" style="padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 8px; background: rgba(255,255,255,0.02); border-left: 3px solid ${status === 'PASS' ? '#10b981' : status === 'FAIL' ? '#ef4444' : '#f59e0b'};">
                        <div class="gate-header" style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600;">${name}</span>
                            <span class="status-badge status-${status}" style="font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; background: ${status === 'PASS' ? 'rgba(16,185,129,0.15)' : status === 'FAIL' ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)'}; color: ${status === 'PASS' ? '#34d399' : status === 'FAIL' ? '#f87171' : '#fbbf24'};">${status}</span>
                        </div>
                    </div>
                `;
            }
            // Also show reasons if available
            const reasons = this.summary?.reasons;
            if (reasons) {
                html += `<div style="margin-top: 1rem; padding: 0.75rem; background: rgba(239,68,68,0.1); border-radius: 8px; font-size: 0.8rem; color: #f87171;">⚠️ ${reasons}</div>`;
            }
            container.innerHTML = html;
            return;
        }
        
        // Fallback: No gates found
        container.innerHTML = `
            <div class="placeholder">
                <span>No gate reports found.</span>
                <small style="opacity: 0.5; font-size: 0.8rem; display: block; margin-top: 0.5rem;">Run grade_runs.py --write to generate verification gates.</small>
            </div>
        `;
    }

    renderChart() {
        const ctx = document.getElementById('omega-chart').getContext('2d');
        if (!this.timeseries) return;

        if (this.chart) this.chart.destroy();

        const labels = this.timeseries.map(d => d.t);
        const data = this.timeseries.map(d => d.Omega);

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Omega (Energy)',
                    data: data,
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                scales: {
                    x: {
                        display: true,
                        title: { display: true, text: 'Time (t)', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        display: true,
                        title: { display: true, text: 'Ω', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    renderFooter() {
        document.getElementById('model-label').textContent = this.config?.model || "-";
        document.getElementById('runtime-label').textContent = this.summary?.runtime_s ? `${this.summary.runtime_s.toFixed(3)}s` : "-";
    }
}

// Start app
window.addEventListener('DOMContentLoaded', () => {
    window.app = new UETDashboard();
});
