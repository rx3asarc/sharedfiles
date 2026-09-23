# Autonomous Google Ads System — Handoff Pack

**What this is:** the design brief for a fully autonomous, self-learning, self-healing
Google Ads system for Nordisk Renhet, written by the implementing agent (OWL) for
Claude Opus 5 to architect, with the returned spec to be built on the production box.

## The file to hand off

```
google-ads-autonomy/HANDOFF-PROMPT-claude-opus5.md      (Revision 2, ~68KB)
```

Raw URL: https://raw.githubusercontent.com/rx3asarc/sharedfiles/main/google-ads-autonomy/HANDOFF-PROMPT-claude-opus5.md

Paste **the whole file** into Claude Opus 5. It is a prompt, not a report. Section 10 of
the file defines exactly what the architect must return (a 17-part technical architecture
and implementation spec), and Section 12 tells it who is building it and how.

## Status of the other file

`../AUTONOMOUS-ADS-ARCHITECTURE-PROMPT.md` is the **Revision-1 draft** — superseded, and
banner-marked as such. Its capability inventory was merged into Revision 2 (Sections
3.13–3.15). Do not hand it off.

## What Revision 2 contains

| Section | Content |
|---|---|
| 0–2 | How to read the brief, the mission in engineering terms, the business |
| 3 | **Verified current state** — every data source, credential, DB table, row count, CLI and cron on the box (3.1–3.15) |
| 4 | **What is actually broken or dark** — 16 live defects, each a prerequisite task |
| 5 | The core design problem (tiny account, near-zero conversion signal, broken linkage) |
| 6 | Hard constraints — safety, reversibility, truthfulness, the progressive trust ladder, launch envelope |
| 7 | The 22 explicit requirements the owner asked for |
| 8 | The implied requirements he did not know to ask for |
| 9 | Anti-patterns specific to this setup |
| 10 | The exact 17-part deliverable the architect must return |
| 11 | Fastest path to something real |
| 12 | Closing note: he holds veto, not approval |

## Verification standard

Every factual claim in Section 3 was read live off the production box on 2026-09-23 and
carries its own evidence (row counts, file paths, CLI output). Numbers the architect is
allowed to use are the ones in this document — it is explicitly forbidden from inventing
metrics. If a claim here is later found wrong, fix it here rather than in a downstream doc.
