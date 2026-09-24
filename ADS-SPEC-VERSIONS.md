# Autonomous Ads — spec version history

**Canonical file:** `AUTONOMOUS-ADS-ARCHITECTURE2.md` — **always the current version.**
Frozen prior versions are kept alongside under an explicit `-vX.Y` name so any previously-cited
md5 remains retrievable. Do not delete a frozen version while it is referenced anywhere.

---

## Current

| File | Version | md5 | Role |
|---|---|---|---|
| `AUTONOMOUS-ADS-ARCHITECTURE2.md` | **v2.4** (2026-09-24) | `50adf9fd920be5e2464a4a68b34e9007` | **Canonical spec.** Amended in place. |
| `AUTONOMOUS-ADS-GENERATIVE-LAYER.md` | v1.0 (2026-09-24) | `13cfe9a23bcb5798c9e31cf5a9e209ea` | **Companion extension** — Phase 1c (UNIT 1.19–1.23). Deliberately not merged; see its §GL.0. |
| `HANDOFF-ads-cli-and-spec.md` | 2026-09-24 | — | Transition state: Google Ads CLI status, both workstreams, open owner decisions. |

## Frozen / superseded

| File | Version | md5 | Note |
|---|---|---|---|
| `AUTONOMOUS-ADS-ARCHITECTURE2-v2.3.md` | v2.3 (2026-09-23) | `0902b5370e40421e92bafa934b22b1dd` | Builder-authored. Preserved so the md5 cited in prior review rounds still verifies. Superseded by v2.4. |
| `AUTONOMOUS-ADS-ARCHITECTURE_1.md` | — (2026-09-23) | — | Builder upload; earlier variant. Untouched. |
| `AUTONOMOUS-ADS-ARCHITECTURE-PROMPT.md` | — | — | Original handoff prompt to the builder. Untouched. |

---

## What v2.4 changed

Four sections were amended and one phase was added. Full detail in
`AUTONOMOUS-ADS-GENERATIVE-LAYER.md` §GL.12.

| Area | v2.3 position | v2.4 position | Why |
|---|---|---|---|
| **§12.5 imagery** | Generated imagery banned outright | Classify + disclose (AI-1…AI-7); **stylised by default** | EU AI Act **Art. 50 applies from 2 Aug 2026 — already in force**. The operative test is whether content "would falsely appear authentic", which stylised work does not meet. Stylised is also the better-performing choice for feed pattern-disruption |
| **§13.1 archetypes** | `lander_class` = 8 values, all existing-template selectors | + `LISTICLE`, `ADVERTORIAL`, `AUTHORITY`, `REPORT` as **content templates** | The autonomous path was always the page *body* (`body_html` rendered via `{{ closest.page.content }}`), not a theme template. This is unbounded-variety and needs **no theme approval** |
| **§12.1 / §12.4 inputs and gates** | Inputs entirely internal; T4 persuasion folklore unbounded | + research brief + tiered persuasion corpus; T4 blocklist as an **output** lint; **GL-R3: only a *verified* entry may BLOCK** | A corpus that launders folklore as evidence makes the system more confident and less correct. The corpus is a *decaying* asset (audiences learn and resist tactics), so tiers must be testable in-account |
| **§22.3 display** | "before Stage 4 — no measurable path at this volume" | Same reasoning, **explicit measurable unlock**: ≥30 store orders/month × 2 consecutive months AND R1≥0.90/R2≥0.85 × 14 days | Display is blocked by *statistics*, not capability. The reasoning was kept; the threshold was made falsifiable — and it is flagged as sitting at the optimistic ceiling of the 20–30/month forecast |
| **§21** | Phases 0–7 | + **Phase 1c** (generative layer) | The generative work is not a prerequisite for the ads machinery and does not belong inside its phases |

## What v2.4 deliberately did NOT change

- **§1.6's CVR contradiction (1.5% vs 2.3%) is still there.** It is listed as a fix in the handoff and
  is a 5-minute edit, but it governs a spend decision, not the system — so it did not block this work.
- **No economic claim was made or resolved.** v2.4 makes no assertion about profitability.
- The spend governor, cap layer, ledger, inverse operations and the five gates are untouched.

---

## Verification status (important)

The extension's **§GL.9 carries an evidence & provenance register** that labels every normative clause
as either grounded in a retrieved source, measured on this box, or `UNVERIFIED` with an obligation
attached. Read it before quoting anything as fact.

Two research passes commissioned for this work **returned knowledge-only briefs with no web access**
and self-flagged as unverified. Their content was **not** used to write any normative clause, and that
failure is recorded in the document rather than hidden. The Art. 50 findings were retrieved
separately, after the failure was detected.

**Open verification items** are listed in `AUTONOMOUS-ADS-GENERATIVE-LAYER.md` Appendix A (V1–V14).
The highest-value ones are V13 (whether any part of Art. 50(2) *marking* was deferred for
interactive-generative systems) and V4 (marknadsföringslagen's consolidated text).

## Review status

Both documents were adversarially reviewed. The review found **3 CRITICAL, 15 MAJOR** and several
MINOR defects — including one that inverted the extension's own central claim about archetype cost,
and one where an *unverified* blocklist was acting as a hard gate (the safety valve was inverted).
All were fixed and re-verified. The review is not reproduced here; the corrections are in the
documents and the two largest are logged as gaps **GL-G15** and **GL-G16**.

## Outstanding owner decisions

See `AUTONOMOUS-ADS-ARCHITECTURE2.md` §23 **Q11–Q18**. The two that gate work:

1. **Q11 — is the `Nordisk Wellness Kit` zero-inventory condition real?** (theme-repo gap register G21).
   Nothing generates until answered: if real, the highest-value routing target in the account cannot
   be fulfilled.
2. **Q14 — brand vs activation policy.** A per-ad optimiser converges on most-aware direct-response
   angles. Correct for the spec's stated objective, wrong as a description of how a brand grows.
   Default applied: activation-only, **explicitly labelled as such in the digest** so the limitation
   is visible rather than silent.
