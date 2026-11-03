# UET Work Areas

Use these area ids in `WORK_LEDGER/YYYY/YYYY-MM-DD.md` entries before starting a
substantial section of work.

| Area id | Primary paths | Use for |
| --- | --- | --- |
| `research-core` | `docs/topics/`, `docs/meta/` | Numbered UET research topics, topic status, verifier artifacts, evidence gates |
| `research-standards` | `docs/topics/For Work/`, `AGENTS.md` | Research workflow rules, claim discipline, AI-agent operating standards |
| `documentation-system` | `docs/UET_Documentation_Details/`, `README.md`, `CONTRIBUTING.md` | Project documentation architecture, public explanation, style guidance |
| `theory-history` | Removed from Harness on 2026-11-03 | Historical area id retained for earlier ledger entries; no destination access from Harness |
| `book-writing` | Removed from Harness on 2026-11-03 | Historical area id retained; ongoing book work is outside this repository |
| `thai-policy` | `thailand_proposals/` | Thailand proposal work, policy framing, public-project concepts, source manifests |
| `services-tools` | `services_and_experiments/` | Local services, experiments, MCP, GraphQL, search, embeddings, automation tools |
| `result-artifacts` | `Result/`, topic `Result/` folders | Small reproducible outputs, reports, figures, verifier outputs |
| `repo-ops` | `.github/`, `.gitignore`, `_config.yml`, root manifests | CI, GitHub Pages, branch hygiene, repo recovery, public-safe publishing rules |
| `raw-private` | local-only raw assets, transcripts, chat exports, audio, PDFs | Source material that needs review or manifest treatment before public commit |

## Classification Rule

`Stream` and `Area` answer different questions. Stream separates research,
historical book work and supporting operations; Area identifies the primary
workspace/responsibility. See [the stream views and source rules](README.md).

- `research-core`, `research-standards` and legacy `data-provenance` map to
  `research`; a topic result-artifact record may use its explicit research path.
- Historical `book-writing` and `theory-history` map to `book-history`, even
  when they contain literature review, science explanations or source audits.
- Other primary areas map to `operations`. Secondary research/book areas explain
  dependencies, not additional accomplishments or permission to cross projects.
- For new Harness work, select research or operations. book-history is reserved
  for archival/migration records; new manuscript production belongs outside
  Harness and must not be initiated or inspected by a Harness agent.

If a task touches more than one area, record the primary area first and list the
secondary area in the entry body. If the work contains private or raw material,
mark public safety as `partial`, `private`, or `blocked` even when some markdown
outputs are safe to commit.
