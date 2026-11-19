# Research Throughput Workflow

This standard defines the token-saving workflow for repeated UET hardening work.

It does not lower the evidence standard. It reduces repeated context reconstruction so AI
sessions spend more effort on physics, formulas, verifier behavior, and claim boundaries.

## Purpose

Use this workflow when progress feels slow because every topic pass requires rereading many
files before the actual blocker is clear.

The goal is to turn the current audit state into a compact research wave packet before any
deep topic reading begins.

## Core Rule

Use a current, identity-matched generated packet first when one exists for the
requested scope. It is a navigation aid, not the scientific controller. If absent,
stale or unrelated, inspect the existing contract and bounded work card directly;
do not generate new artifacts merely to answer an analytical question.

Do not open a whole topic folder if the packet already names the controlling blocker, the
recommended files, and the stop condition.

## Standard Sequence

1. Generate the current packet queue.

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_core_research_hardening.py --json --top 5
```

2. Honor the user's question and the earliest unresolved dependency of its intended
   claim under standard 32. Queue rank is a suggestion only when no scope is chosen;
   verify current evidence identities and prerequisites before adopting it.

3. Read only the files listed in that topic packet.

4. Complete one hardening wave for one blocker.

5. Stop when the packet stop condition is satisfied.

6. Rerun the relevant verifier or audit only when the evidence-producing state changed.

7. Record the wave in the topic `UPDATE_LOG.md` when the work spans repeated passes.

## Single-Topic Packet

Use this command when a user names a specific topic or when an agent needs a compact handoff:

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_core_research_hardening.py --topic 0.4_Superconductivity_Superfluids --emit-packets
```

The packet should be enough to answer:

- what currently blocks the topic
- which files should be opened first
- which verifier command or artifact matters
- what one next action is allowed
- when the wave should stop

## What To Automate

Use scripts for:

- queue ordering
- status summaries
- template or checklist generation
- repeated artifact inventory
- stale-priority detection
- JSON packet generation

Use AI reasoning for:

- physics interpretation
- formula provenance and unit analysis
- model failure diagnosis
- threshold and baseline meaning
- claim class and limitation wording

## Wave Scope

One wave should narrow one blocker.

Do not combine data provenance repair, verifier repair, formula audit review, and public
wording upgrades unless they are required to close the same named blocker.

If a topic has several blockers, pick the one named by the latest packet or the latest stable
machine-readable artifact.

## Future-Concept Rule

Do not spend throughput budget on `0.27+` future-concept topics in this phase unless the user
explicitly names one.

Future-concept topics remain exploratory until a separate standards pass adds real data
provenance, runnable verification, formula audit coverage, and limitations.

## Token-Saving Reading Rule

Default reading order for a packet-driven pass:

1. `docs/meta/core_research_next_actions.json`
2. the selected packet's recommended files
3. the latest verifier artifact named by the packet
4. `UPDATE_LOG.md` only if the topic has repeated waves
5. broader topic docs only if the blocker cannot be understood from the packet files

This keeps hardening auditable without paying the full topic-reading cost every turn.

## Completion Check

A throughput-focused wave is complete when:

- the declared decision is answered or the controlling prerequisite is narrowed
  with evidence; a proof, counterexample, equivalence or rejected route is valid
  closure under standard 32 profile applicability
- the narrower blocker is visible in an artifact, manifest, gate, or topic doc
- the relevant packet stop condition is satisfied
- claim wording did not get stronger without stronger evidence
- the next packet or update-log entry makes the next controller clear

