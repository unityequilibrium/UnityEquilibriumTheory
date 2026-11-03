# UET Social Publishing Workflow

This workflow turns verified work records into controlled public updates. It does not
replace research artifacts, proposal drafts, book manuscripts, or the daily work ledger.

## Core rule

Keep research, supporting operations and historical book records distinct using
the views in [README.md](README.md). Book literature reviews are not automatically
research milestones. Since the 2026-11-03 relocation, this repository's book
records describe history only; do not present them as current Superapp progress
or access that separate project to assemble a Harness update.

One source pack may produce many channel versions, but every version must point back to the
same source pack and must preserve its process stage and claim boundary.

```text
Work record
  ↓
Monthly update pack / weekly research pulse
  ↓
AI channel drafts
  ↓
Human claim and privacy review
  ↓
Asset preparation
  ↓
Approval
  ↓
Manual publish, scheduler, or approved API
  ↓
Publish log and response notes
```

## Source-of-truth order

1. Research artifact, manifest, gate, or topic `UPDATE_LOG.md`
2. Proposal source file and its evidence notes
3. Book blueprint, chapter draft, or source notes
4. `monthly_update_pack.md` or a weekly research pulse
5. Channel-specific drafts

Channel drafts are adaptations, never the source of truth.

## Content classes

| Code | Content class | Use | Default review |
| --- | --- | --- | --- |
| `PROCESS_UPDATE` | routine work update | show current stage, change, blocker, next gate | self-check, then human approval before publish |
| `MILESTONE` | meaningful artifact change | verifier, blueprint, chapter, proposal version | human review |
| `INSIGHT` | explanation from existing work | explain one concept or lesson | source and claim check |
| `REVIEW_REQUEST` | ask for critique | request a specific review or question | human review |
| `RELEASE` | finished public artifact | paper, book, proposal, or major public result | publication gate; never auto-publish |

## Channel and account map

The project should distinguish the account/profile from the format published inside it.
Create only the accounts that have an actual role; the table is a complete operating map,
not a requirement to post everywhere at the same frequency.

| Platform / surface | Account or page type | Primary role | Formats | Default cadence | Main source |
| --- | --- | --- | --- | --- | --- |
| Facebook | public Page / profile | broad project visibility | long text, image, link, video, monthly digest | monthly + milestone | monthly pack |
| Facebook | Group / Community | discussion and critique | process note, question, file/link | when discussion is useful | monthly pack + drafts |
| Instagram | Professional profile | visual project identity | feed image, carousel, Reel | monthly + milestone | channel drafts + assets |
| Instagram | Stories | lightweight continuity | reshare, short note, poll, behind-the-scenes | weekly or when a real update exists | Threads / feed / pulse |
| Threads | profile | frequent short research pulse | short note, reply, mini-thread, question | 1–3 times/week when work changes | research pulse |
| LinkedIn | personal profile / organization Page | professional credibility | structured text, image, document, article, video | 1–4 times/month | monthly pack |
| X | profile | short-form ideas and research thread | short post, thread, link, image | optional pulse / milestone | research pulse |
| YouTube | channel | durable explanation and major work | long video, short video, playlist | milestone or monthly/quarterly | released artifact |
| YouTube | Community tab | announcement and question | text, image, poll | when channel has a reason to respond | monthly pack |
| TikTok | profile | short visual explanation | short video, process clip | milestone only at first | approved script + asset |
| GitHub / Blog | repository or site | canonical archive | markdown, artifact link, changelog | every stable milestone | source artifacts |
| Discord / private community | server and channels | collaboration and critique | full note, file, question, review thread | ongoing | source pack + drafts |

Platform features and permissions change. The current implementation should use the visible
account UI or the platform's official API documentation before adding automation.

## Recommended cadence for this project

### Research pulse

- Review research work once per week.
- Post to Threads or X only when the pulse contains a real change, observation, blocker, or
  question.
- Reshare a useful pulse to Instagram Stories when appropriate.
- Do not create a fake update to maintain a streak.

### Monthly four-stream pack

Prepare one pack for `R`, `P`, `T`, and `B`, then adapt it as:

- Facebook: one monthly digest or four scheduled cards
- Instagram Feed: one visual card or carousel per stream
- LinkedIn: the strongest one or two professional cards
- Community: the full detail and a specific question
- GitHub / Blog: the canonical links and artifact references

### Major work

When a work item reaches a real milestone, create one `MILESTONE` or `RELEASE` package and
adapt it to all relevant channels. A big release is not the same as a routine process update.

## Approval levels

| Level | Content | Automation rule |
| --- | --- | --- |
| `GREEN` | process update with no new numerical or scientific claim | AI may draft; human still presses publish |
| `YELLOW` | numbers, formulas, policy implications, external sources, or public recommendations | human reviews source, wording, and stage |
| `RED` | `solved`, `verified`, `exact`, prediction, external commitment, political/financial claim, or publication announcement | no unattended automation; explicit human approval required |

## Publish packet schema

Every channel draft should carry this metadata:

```text
post_id: 2026-07-R-THREADS-01
source_pack: WORK_LEDGER/2026/monthly_updates/2026-07_update_pack.md
stream: R | P | T | B
content_class: PROCESS_UPDATE | MILESTONE | INSIGHT | REVIEW_REQUEST | RELEASE
stage: INBOX | FRAMING | BLUEPRINT | DRAFT / BUILD | REVIEW | READY | PUBLISHED
platform: Facebook | Instagram | Threads | LinkedIn | X | YouTube | TikTok | Community
caption_file: [draft path]
asset_file: [asset path or n/a]
source_links: [artifact or manuscript paths]
claim_boundary: [current allowed wording]
risk_level: GREEN | YELLOW | RED
approval: PENDING | APPROVED | REJECTED
scheduled_at: [timestamp or n/a]
published_url: [fill after publish]
notes: [post-publish observations]
```

## Tooling decision

### Phase 1 — human-in-the-loop (recommended now)

AI writes channel variants; Canva or another design tool creates assets; the owner reviews
and manually publishes. This is the default because the project currently has a low monthly
volume and high claim sensitivity.

### Phase 2 — scheduler

Use a platform-native or third-party scheduler only after the draft is approved. The scheduler
may handle timing, but it must not decide whether a scientific or policy claim is safe.

### Phase 3 — official API

Add one platform at a time only when volume justifies maintenance. Keep OAuth credentials and
tokens outside the repository, add retry/idempotency handling, and write a publish-log entry
after every successful or failed attempt. Never place secrets in markdown, Git history, or
the public repository.

### Browser automation

Browser control is a fallback for a signed-in session and explicit user instruction. It is
not the primary publishing system because UI changes, authentication, and accidental clicks
make unattended publishing fragile.

## Quality gate before publish

- [ ] The source file or artifact exists.
- [ ] The process stage is named correctly.
- [ ] The post says what changed, what remains open, and what comes next.
- [ ] Claim wording stays within the source evidence layer.
- [ ] No private raw material, credentials, or unreviewed personal data is exposed.
- [ ] The asset has a source or is marked as generated.
- [ ] The post has an explicit risk level and approval state.
- [ ] The final URL will be written to `publish_log.md` after publishing.
