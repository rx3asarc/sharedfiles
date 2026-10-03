# Autonomous Ads — spec version history

**Canonical file:** `AUTONOMOUS-ADS-ARCHITECTURE2.md` — **always the current version.**
Frozen prior versions are kept alongside under an explicit `-vX.Y` name so any previously-cited
md5 remains retrievable. Do not delete a frozen version while it is referenced anywhere.

---

## Current

| File | Version | md5 | Role |
|---|---|---|---|
| `AUTONOMOUS-ADS-ARCHITECTURE2.md` | **v2.4.7** (2026-10-03) | `0df8be10af748a36eed41c41af830656` | **Canonical spec.** Withdraws v2.4.6's `lang="en"` / translation-count evidence as non-discriminative (every layout emits `lang="{{ request.locale.iso_code }}"`, and the Swedish-authored `torr-hud-efter-duschen-duschfilter` serves `lang="en"` too), keeps the conclusion on the sound basis (the page's title tag is *"V1 Itchy Skin Angle English"*), and **completes Q20's violation set: 5 of 22, not 3** — 2 more ENABLED ads land on that English page and were tracked nowhere. Records that the language fix has **no Swedish counterpart page** to target. Also records that the two hidden `nr-test-*` pages are the **only** surface for the still-open G17/G18 gates and must not be deleted yet. |
| `AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.6.md` | v2.4.6 (2026-10-03) | `6e88750107cdb7b735d196f1f0eec4de` | Frozen copy, preserved so the v2.4.6 md5 still verifies. Corrected the kit-reference inventory; carried the `lang`-attribute evidence that v2.4.7 withdraws. |
| `AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.5.md` | v2.4.5 (2026-10-02) | `6daf57d4030e279c5f363d20180dcd58` | Frozen copy, preserved so the v2.4.5 md5 still verifies. Resolved Q19 (canonical kit) and gave Q16 hard evidence; carried the undercounted cleanup scope that v2.4.6 corrects. |
| `AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.4.md` | v2.4.4 (2026-10-02) | `6d99630a98a02fd8dcc3ec14d7e68e50` | Frozen copy, preserved so the v2.4.4 md5 still verifies. Ruled the funnel contract as a purchase-intent rule. |
| `AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.3.md` | v2.4.3 (2026-10-02) | `c4175548d919c9aafac03b7cf667e30e` | Frozen copy, preserved so the v2.4.3 md5 still verifies. Recorded Q19/Q20 as open. |
| `AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.2.md` | v2.4.2 (2026-10-02) | `29919d11bc45de98b199a1bd90ed5809` | Frozen copy, preserved so the v2.4.2 md5 still verifies. |
| `AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.1.md` | v2.4.1 (2026-10-01) | `80bd2dc9450825c0dff4f601062593ac` | Frozen copy, preserved so the v2.4.1 md5 still verifies. §1.6 blockers resolved; predates the §23 evidence rows. |
| `AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.md` | v2.4 (2026-09-24) | `50adf9fd920be5e2464a4a68b34e9007` | Frozen copy of the pre-fix spec, preserved so the v2.4 md5 still verifies. Superseded by v2.4.1. |
| `AUTONOMOUS-ADS-GENERATIVE-LAYER.md` | **v1.0.1** (2026-10-02) | `6997f1b14ca771346f11b3afbab1ed7a` | **Companion extension** — Phase 1c (UNIT 1.19–1.23). GL.4.7 / GL.10 Q1 resolved: the "zero-inventory" condition is not a stock condition. Deliberately not merged; see its §GL.0. |
| `AUTONOMOUS-ADS-GENERATIVE-LAYER-v1.0.md` | v1.0 (2026-09-24) | `13cfe9a23bcb5798c9e31cf5a9e209ea` | Frozen copy, preserved so the v1.0 md5 still verifies. |
| `HANDOFF-ads-cli-and-spec.md` | 2026-09-24, updated 2026-10-02 | — | Transition state: Google Ads CLI status, both workstreams, open owner decisions, and the canonical-handle question. |

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

## What v2.4.1 changed (2026-10-01)

The two §1.6 blockers from `HANDOFF-ads-cli-and-spec.md` are resolved in the canonical file:

| Area | v2.4 position | v2.4.1 position | Why |
|---|---|---|---|
| **§1.6 paid CVR** | Scenario row: 3,500 clicks/month at 1.5% (52 paid orders) while break-even paragraph demanded ≥ 2.3% — by its own math the paid pillar lost −2,549 AUD/month and collided with §8.5 D21 | Scenario row: 2,600 clicks/month at ≈ 2.0% ≥ break-even; break-even recomputed from measured margin; D21 gate stated as a precondition | The 1.5%-vs-2.3% contradiction made the 100-order headline internally inconsistent. With measured COGS the real break-even is ≈ 1.7–1.9%, so 2.0% is a viable scenario value — and every ramp step must still clear D21 |
| **§1.6 contribution margin** | Assumed 45–50% contribution → `C_new` ≈ 540–600 SEK | **Measured 63.2% gross margin** (HyperSKU supplier export, 18,257 SEK revenue vs 6,711 SEK cost, 2026-09-24) → `C_new` ≈ 700–780 SEK ≈ 111–124 AUD | §0.2 discipline forbade the assumed number; the measured one is cited and entered as `NO_DATA` until UNIT 1.5's stored query reproduces it |

## What v2.4.2 changed (2026-10-02)

### 1 — A version-integrity defect, found and repaired

Commit `029cb48` (*"Spec §23: record Q11/Q13 live-verification evidence"*, 2026-10-01) edited the canonical
file but **neither bumped the header version nor updated this tracker**. The md5 chain shows it plainly:

| Commit | Header says | Actual md5 | Matches this tracker? |
|---|---|---|---|
| `1c37fe1` | v2.4.1 | `80bd2dc9450825c0dff4f601062593ac` | ✅ yes |
| `029cb48`, `f85f617` (HEAD) | v2.4.1 | `04249f9caebb71d174d960dd39e9c3a3` | ❌ **no** |

v2.4.2 folds that undeclared edit into the record: the §23 Q11/Q13 evidence rows are now part of a
versioned revision, and the v2.4.1 md5 remains retrievable via the frozen copy below. No content was
lost or altered by this repair.

### 2 — `P-STOCK` removed, and Q11 closed

| Area | v2.4.1 position | v2.4.2 position | Why |
|---|---|---|---|
| **§6.10 / §13 pre-flight `P-STOCK`** | `P-STOCK (target variant inventory ≥ 5)` — one of the all-must-pass gates before any ad is submitted | **Gate removed.** The `inventory` ingest is retained as a diagnostic snapshot only, explicitly marked "not a gate" | The gate read `variants[].inventory_quantity` — a field that is permanently inert on this store: **every variant is untracked** (`tracked = FALSE`; verified 2026-10-02 across all 9 Wellness-Kit-family products and 49 of 50 store variants). An untracked variant has no stock ceiling, so the value never reflects a limit and the gate would have failed closed on every Wellness-Kit lander forever. §0.1 forbids acting on an unmeasured number |
| **§23 Q11** | "VERIFIED 2026-10-01 — condition NOT real; owner confirmation solicited" | **RESOLVED 2026-10-02 — owner-confirmed by Maestro** | Same finding, now with the owner's decision recorded, the correct product count (9, not 7), the store-wide scope (49/50 untracked), and the consequence (P-STOCK removed). Theme-repo gap **G21 closed** |

**Loose end, not a blocker — but the shape was mis-stated in v2.4.2's first pass.** It is not three
competing handles and *not* a duplicate pile: there are **nine** Wellness-Kit records in two groups,
and only one group is a genuine choice.

**Group A — six localized records (legitimate, must not be merged).** Shopify cannot vary product
images per locale, so a localized product image forces a separate product record. Each of these six
carries a complete ten-image set in its own language:

| Handle | Locale of imagery | SEK | Published |
|---|---|---|---|
| `nordisk-kit-ien-etre` | French (`French_*`) | 2,211 | 2026-09-02 |
| `nordisk-welcome-kit` | English | 2,211 | 2026-09-02 |
| `nordisk-wellness-kit-1` → **`nr-nordisk-wellness-kit-1`** | German | 2,211 | 2026-09-02 |
| `nordisk-wellness-saet` | Danish (`Danish_*`) | 2,211 | 2026-09-02 |
| `nordisk-welness-kit` | Dutch/LU (`Luxembourgish_*`) | 2,211 | 2026-09-02 |
| `nordisk-welness-pakket` | Dutch/BE (`Flemish_*`) | 2,211 | 2026-09-02 |

All six were **created March 2025** and **published 2026-09-02**. Three defects attach to them:
(1) the store publishes only **`en`, `fr`, `sv`** locales, so the DE/DA/LU/NL records sell in
languages the storefront does not serve; (2) all six are published to **Online Store + AI channels
only** — not to Google & YouTube, Shop, Facebook & Instagram or Pinterest, so they cannot surface in
Shopping or paid-social feeds; (3) they carry **2,211 SEK** against the spec's hardcoded truth of
2,189 (= 990 + 1,199).

**Group B — three Swedish records (this is the actual decision).**

| Handle | SEK | Imgs | Created | Evidence of use |
|---|---|---|---|---|
| `nordisk-renhet-wellness-kit` | 2,189 | 10 | 2025-03-03 | CTA target of the live lander `/pages/duschfilter-jamforelse-bast-i-test`; SKU `NR-DOUBLE-FILTRATION` |
| `nordisk-renhet-welcome-kit` → **`nr-nordisk-renhet-welcome-kit`** | 2,189 | 8 | 2025-03-25 | full channel set |
| `nordisk-wellness-kit` | 2,189 | **1** | 2025-03-11 | the handle in `nordisk_ads_context.json`; looks like an unfinished stub — one image only |

One of Group B must be named canonical before paid routing is finalised, otherwise the lander CTA and
the adsys product registry can address different records. **Correction to the first pass:** no ad
final URL points at any Wellness Kit — live-verified 2026-10-02 across all 22 enabled ads in the three
delivering campaigns. The kit is reached from the lander's **CTA**, not from the ad's landing URL, so
this decision does not move any live ad. Also corrected: `nordisk-wellness-kit-1` has **five** localized
siblings, not seven. The only sale ever recorded is order `#NR_SE_1104` (1,711 SEK, 2026-09-03, SKU
`NR-WELLNESS-KIT-SE-1`). Recorded in `HANDOFF-ads-cli-and-spec.md`.

**Consequence for the spec:** the single-canonical-handle assumption is itself the defect. Because
localized imagery forces separate records, **CTA resolution must be locale-aware** — an `en` or `fr`
campaign cannot be routed to a Swedish record. This is a real gap in §6's product routing, tracked as
an open decision rather than silently patched.

## What v2.4.3 changed (2026-10-02)

Two things were recorded, and **neither is a decision this document is entitled to make.** One is an
arbitration between two agents; the other is a conflict between an owner instruction and the spec's
own routing table. Both are written up with evidence and left open.

### 1 — The canonical Wellness-Kit handle is an arbitration, not a settled fact (§23 Q19)

v2.4.2's carry-over note said three handles claim the product and one must be named canonical. On
2026-10-02 two agents independently picked **opposite** candidates from the same live reads, which is
why this row does not name a winner.

| | Candidate 1 | Candidate 2 |
|---|---|---|
| Handle | `nordisk-renhet-wellness-kit` | `nordisk-wellness-kit` |
| Product id | `10161700766030` | `10246605144398` |
| SKU | `NR-DOUBLE-FILTRATION` | `NR-WELLNESS-RENHET` |
| Media | **10** | **1** |
| Created | **2025-03-03** (oldest) | 2025-03-11 |
| Status / channels | active, all 7 | active, all 7 |
| Theme references | **0 files** | **9 files / 14 references** |
| Live evidence | CTA target of `/pages/duschfilter-jamforelse-bast-i-test`, an ENABLED ad's own `final_url` | what most live landers actually buy |

**The tie-break that was supposed to settle it, failed.** All three original Swedish records are tied
at **zero units sold ever**, so sales cannot separate these two candidates.

**Why candidate 1 was mis-reported as non-existent.** Its title is "Duschfilter startpaket – dubbel
filtrering. 3+3 media." — it contains no token matching `*wellness*` or `*kit*`, so a title-based
search cannot find it, while candidate 2 is titled "Nordisk Renhet Wellness Kit". A search matching
on title and a search matching on handle do not return the same set, and this row is the first place
that is written down.

**State applied, provisionally:** `nordisk_ads_context.json` now points at candidate 1, on the
grounds that it is the record the comparison advertorial already buys. That edit reverts in one line
if the owner rules otherwise, and nothing else was changed — no product was edited, merged,
unpublished or deleted.

### 2 — The owner's funnel contract conflicts with §13 as written (§23 Q20)

The owner's stated contract: *ads → lander → CTA target \{product page \| sales page \| VSL \|
advertorial\}, never an ad pointing directly at a product page.*

This is not a clarification of §13 — it is a change to it, in two places:

| §13 says | The contract says | Consequence |
|---|---|---|
| `SOLUTION_AWARE`, `PRODUCT_AWARE`, `MOST_AWARE` → `lander_class = PRODUCT` (§13.2) | a product page is a CTA target, never an ad destination | three rows of the stage table stop being routable as written |
| bucket `"Klor & Vatten" → product page` (§13.3) | same | the seeded taxonomy row is a live violation |
| `lander_class` has no `VSL`, no `SALES_PAGE` | both are named valid CTA targets | the enum needs values before routing can address them |

**Recorded as a conflict, with a strict and a narrow reading, both written out in §13.2.** The
unresolved part is specifically **whether "never" includes brand and most-aware traffic** — the
`MOST_AWARE` row exists so that a brand searcher reaches the product, and routing them through an
advertorial is arguably worse than what they asked for.

**Default applied so work is not blocked:** the **strict** reading governs *new* routing only — no new
or modified ad may carry a `final_url` under `/products/`. **The 5 existing violations are left in
place**, because repointing live ads on a reading an agent guessed is the expensive failure mode and
the strict reading can be relaxed in one write whereas the reverse cannot.

### 3 — Corrections this revision folds in

- **The renames are real and the redirects exist.** `nordisk-renhet-welcome-kit` →
  `nr-nordisk-renhet-welcome-kit` and `nordisk-wellness-kit-1` → `nr-nordisk-wellness-kit-1`,
  applied 2026-10-02 through **REST** `/redirects.json` — GraphQL `urlRedirectCreate` returns
  `ACCESS_DENIED` on this token (it holds `write_content`, not `write_online_store_navigation`).
  Four redirects, sv + `/en` each; both products kept their ids (`10364884517198`,
  `10379616911694`). Verified live 2026-10-02.
- **v2.4.2's Group A / Group B tables are stale** for those two rows — corrected above.
- **The kit-handle inventory was under-counted by every earlier pass.** It is **39 files holding 6
distinct kit handles across 86 references**, not 5 sections. Every reference is paired with a numeric
  `productId` and falls back to an id scan when the handle lookup misses, which is **why the renames
  did not break any CTA** — the fallback, not the handle, is what keeps those blocks working today.
  Totals by handle: `nordisk-welcome-kit` 46, `nordisk-wellness-saet` 16, `nordisk-wellness-kit` 14,
  `nordisk-wellness-kit-1` 14, `nordisk-kit-ien-etre` 12, `nordisk-renhet-welcome-kit` 2.
- **A corollary the renames expose:** because the fallback fires only when the handle *misses*, the 3
  sections holding the 1-media stub's id (`10246605144398`) will keep buying the stub even after
  their handle string is corrected, unless the paired `productId` is updated in the same edit.
  Fixing the handle alone is therefore a **no-op** for those blocks. This is recorded here so the
  lander-CTA cleanup is not attempted as a string replace.
- **Nothing in the store, theme or ads account was modified by this version.** Every read behind it was
  read-only; the only write anywhere in this workstream was the single `nordisk_ads_context.json`
  handle field (backup retained), and it is provisional per Q19.

## What v2.4.4 changed (2026-10-02)

### The funnel rule is ruled — and the ruling changed what it *is*

v2.4.3 recorded the owner's contract as a conflict it was not entitled to resolve. The owner ruled on
2026-10-02, and the answer is not a scope choice between the two readings that were offered:

> *"most aware should go to product page . but … this is where those users should go, whomfrom we can
> see there is clea[r] inten[t] to purchase, aka, we have tracked them over a few ads, and then send
> them to product page"*

That is a **purchase-intent rule, not a stage rule.** The stage table describes what a user *knows*; the
ruling conditions the destination on what a user *does*. The two are not interchangeable, and the
practical consequences differ in both directions:

| | Effect |
|---|---|
| Product page permitted as an ad destination | brand / `MOST_AWARE` search, or a user tracked across prior ad touches — **evidence of intent** |
| Product page banned as an ad destination | cold non-brand acquisition — still absolute |
| Product page as a lander **CTA target** | always permitted; unchanged, and the kit's normal path |
| **§13.2's `SOLUTION_AWARE` / `PRODUCT_AWARE` → `PRODUCT`** | **left in place, still flagged.** The ruling does not address them, and deleting two awareness rows would silently re-route more than the ad change it was meant to enable |

**The violation count from v2.4.3 was wrong, and the ruling shows why: it is 2 of 22, not 5.** The
three `BRAND` ads that v2.4.3 listed as violations are the exact case the ruling permits. The two real
violations are the non-brand product-page ads (`818400446073`, `816987228238`). A fifth ad
(`812545048936`) is flagged for a different reason — it points at `/collections/all`, which is neither
a product page nor a lander, and under this ruling brand traffic has purchase intent, so a collection
index is a worse destination than the product page that *is* permitted.

**Recorded as a working rule, not settled doctrine — the owner says so himself:** *"i am personal[ly]
not yet educated enough with google remartketing across display and youtube and pmax and so on"* and
*"this can be different, thats just what im thinking is currenltyy perhaps the best"*. Two consequences
follow, and both are load-bearing:

1. **The multi-touch half is not executable today.** *"Tracked them over a few ads"* presumes a
   retargeting layer, and **§22.3 blocks Display until ≥30 store orders/month for 2 consecutive
   months** against a measured baseline of **9 orders/month**. The intent is recorded so it is not
   lost; **it is not a build ticket, and the display gate is not to be worked around.**
2. **`VSL` and `SALES_PAGE` still do not exist in §13.1's `lander_class`.** The owner named both as
   valid CTA-target surfaces; the enum cannot address them yet. Open.

**No live ad was changed by this revision.** Read-only throughout.

### Q19 status at v2.4.4

The canonical Wellness-Kit handle is **still pending arbitration** (§23 Q19), and the owner has
**sequenced it deliberately**: it waits until the current gated theme-publish cycle finishes, so the
ruling is made with both candidates' real state visible rather than mid-flight. `nordisk_ads_context.json`
continues to point provisionally at `nordisk-renhet-wellness-kit`, with the backup retained.

## What v2.4.5 changed (2026-10-02)

### Q19 resolved — and it closed the same way three independent checks had already pointed

The canonical Wellness-Kit handle had been left as an **arbitration** in v2.4.3 precisely because two agents had reached opposite conclusions. It is now resolved by the owner, and the resolution is the stronger of the two candidates:

| | Winner | Withdrawn |
|---|---|---|
| Handle | **`nordisk-renhet-wellness-kit`** | `nordisk-wellness-kit` |
| Media | **10** | **1** |
| Variant | **`51167026741582`** | — |
| SKU | `NR-DOUBLE-FILTRATION` | `NR-WELLNESS-RENHET` |
| Created | **2025-03-03** | 2025-03-11 |
| Theme refs | 0 | 9 files / 14 refs |

**The notable part is how it closed.** The rival candidate was not out-voted or overridden — it was **withdrawn by the agent who had proposed it**, after confirming it is a **1-media stub** that should not be canonical for anything. That is the outcome an arbitration is for, and it is worth recording that the process worked: the contested claim was found to be *checkable*, not opinion-dependent. The decider was the media count and the creation date, both of which were already in the record and neither of which needed a judgement call.

**Sales could not break the tie, and that is now a standing fact rather than a gap:** every Swedish record in the family sits at **zero units sold ever**. Anyone re-deriving this decision later should not expect sales data to resolve it.

**`nordisk_ads_context.json` stops being provisional.** It already pointed at the winner, so no edit was needed — the provisional flag is retired and the retained one-line-revert backup is no longer needed for this purpose.

**The forward consequence is the same one the arbitration row predicted, and it survives the ruling intact:** the 3 gempages sections paired with the stub's id must be repointed to **handle + variant `51167026741582` in the same edit**, because the paired `productId` is the authority whenever the handle misses. Changing the handle string alone remains a no-op. Separately, the `nr-*` lander templates were corrected off a **third** record (`nordisk-welcome-kit`, 2,211 SEK) — 7 references, commit `2cbf3cf`, duplicate theme only, zero live drift.

### Q16 gains hard evidence: a live surface is already expecting the `ADVERTORIAL` archetype

Found while verifying the ruling, and independently confirmed: **7 live published pages carry `templateSuffix: advertorial-1`, and no `advertorial` template exists among the live theme's 306 template assets.** Those 7 pages therefore **silently fall back to the default page template today**:

- `how-a-shower-filter-transformed-my-skin-and-hair`
- `duschfilter-jamforelse-bast-i-test`
- `torr-hud-efter-duschen-duschfilter`
- `pfas-i-duschvattnet`
- `tungmetaller-i-duschvatten`
- `jamforelse-nordisk-renhet-vs-tappwater`
- `jamforelse-nordisk-renhet-vs-onlinefilter`

This matters beyond Q16. **One of those pages is an ENABLED ad's own `final_url`** — the comparison advertorial — so a surface that is actively receiving paid traffic is rendering through a template it was not designed for. Three consequences, none of which require adsys to act:

1. **The missing template is a pre-existing defect** and is worth fixing on its own merits, independent of the generative layer. It is not caused by, and does not wait on, any adsys work.
2. **The cost calculus of Q16 improves.** `ADVERTORIAL` has a live consumer already declaring intent for it, so building it is closer to *fulfilling a declared intent* than to *adding a new surface*. That is a different proposition from the one Q16 was written against.
3. **Reading an advertorial for content today is unsafe** — until the template exists, any analysis of those 7 pages is analysis of the fallback layout, not of an advertorial.

**Nothing was written to the live theme, and no live page or ad was touched.** Every read behind this section was read-only.

## What v2.4.7 changed (2026-10-03)

### v2.4.6's language evidence was wrong, even though its conclusion was right

v2.4.6 recorded that `/pages/itchy-skin` is English *"because the served HTML carries `lang="en"` and the
page has 0 `en` translation records"*. Both signals were tested again and both fail:

| signal | why it fails | counterexample |
|---|---|---|
| `lang="en"` in served HTML | every layout emits `lang="{{ request.locale.iso_code }}"` and the store publishes `en`/`fr`/`sv` with no URL-prefixed locales, so the attribute tracks the **request** locale, not the content | `/pages/torr-hud-efter-duschen-duschfilter` is Swedish-authored and also serves `lang="en"` |
| 0 `en` translation records | tracks whether the merchant translated the page, not what language it was authored in | the same Swedish page has **0** `en` records; `se-4` (Swedish default title) has **3** |

**The conclusion survives on different evidence.** The page's `<title>` is literally *"V1 Itchy Skin Angle
English"* and its H1 is English, so it is deliberately-authored English-angle content — and the project
rules name this exact URL as one that must not carry Swedish-campaign traffic. Same finding, premises that
hold up.

### Q20's violation set was incomplete: 5 of 22, not 3

Two more ENABLED ads in the same campaign land on that English page and are tracked nowhere in the spec:

```
ad 816987228364  SV SE | Discovery | Broad Match / Discovery Broad Match      -> /pages/itchy-skin
ad 818400446070  SV SE | Discovery | Broad Match / Problem: Torr Hud & Kliande -> /pages/itchy-skin
```

Both verified ENABLED by live GAQL (customer `8479789152`). Q20's own ad ids were re-verified at the same
time and are **correct** (`818400446073`, `816987228238` → `/products/nordisk-duschvattenfilter`).

**The fix is not mechanical.** No Swedish counterpart page to `itchy-skin` exists, and the nearest by
topic (`/pages/torr-hud-efter-duschen-duschfilter`, live, HTTP 200, Swedish title) **carries the phantom
`advertorial-1` suffix** that Q16 records. Repointing there would trade a language mismatch for a
template mismatch. Destination is the owner's call, not an agent guess.

### The `nr-test-*` pages must not be deleted yet

Q12's row recommended deleting `nr-test-8-reasons-20261002` / `nr-test-4-reasons-20261002`. Reversed here:
they are the **only** surface on which the 12 new sections and 2 new templates render, and the still-open
gates **G17 (interactive components exercised)** and **G18 (add-to-cart end-to-end)** are precisely the
tests that need such a page. Deleting them before those gates pass removes the only harness for the
components just published. They are visitor-invisible (`isPublished=false`) and no ENABLED ad points at
them (verified live).

### What was NOT done

No ad, campaign, keyword, budget, theme, product or order write. The 2 language-mismatch ads are
**identified, not repointed** — the destination decision is open.

## What v2.4.6 changed (2026-10-03)

### The parked cleanup's scope was wrong, and it was about to be executed

§23 Q19 handed the next agent an execution list: repoint *"the 3 gempages sections"* paired with the
stub's id. That list was measured again, read-only, against live theme `195492381006` (794 assets) and
the theme repo. It is an undercount on both axes.

**The stub pair (`all_products['nordisk-wellness-kit']` + id `10246605144398`) occupies 7 live files,
not 3 sections.**

```
gp-section-558624190018618611   -> /pages/skin-absorbs-more-than-you-think   [live]
gp-section-558613996182176670   -> /pages/skin-absorbs-more-than-you-think   [live]
gp-section-558773340425815144   -> /pages/itchy-skin  (+ snippet ...-0)       [live]
gp-section-558773340425946216   -> /pages/itchy-skin                          [live]
gp-section-558933907576587157   -> page.gp-template-558933907441976213 (0 pages) [inert]
gp-section-558933907576718229   -> page.gp-template-558933907441976213 (0 pages) [inert]
```

Only **4** of the six sections are wired to published pages. The two inert ones share a template with
**zero** pages — almost certainly where "3 sections" came from. The published row's 3-name list also
**omits `gp-section-558613996182176670`**, which is live. A faithful execution of the recorded list
would have fixed `/pages/itchy-skin` (mostly), left the stub live on a published page, and told the
tracker the cleanup was done. That failure mode is why this revision exists.

Repo-side, the kit universe is **9 handles across 134 `all_products[]` references** in the `theme/`
tree, not 6 handles / 86 references. The canonical record itself is referenced **0** times.

### The repoint is not a string swap

Both records are 2,189 SEK, so price does not move. The sections render `product.media`,
`featured_image` and `featured_media`, and they gate a `gp-carousel` on `product.media.size > 1`. The
stub has **1 media**; the canonical has **10**. Repointing therefore switches those live product
blocks from a single static image to a carousel. Per §R2b that is a real-browser test change, and no
browser test has yet been run on this theme — the 2026-10-02 publish shipped without one.

### It lands on an existing violation instead of fixing one

The canonical record's title is Swedish (`Duschfilter startpaket – dubbel filtrering. 3+3 media.`).
`/pages/itchy-skin` is English content — the served HTML carries `lang="en"` and the page has **0
`en` translation records** against default content that is already English — and it is the final URL
of **2 ENABLED ads** in `SV SE | Discovery | Broad Match`. The project rules name `/pages/itchy-skin`
explicitly as an EN page that must not carry Swedish-campaign traffic. Language is therefore a
**precondition** on this cleanup, not a footnote: if those ads move, the kit work on that page is
moot.

### Also corrected

- The paired id for `nordisk-renhet-welcome-kit` is `10364884517198`; v2.4.3's `10384517198` is a
  typo. **Every** paired id resolves, so the 2026-10-02 renames cause **no live breakage** — the
  id-scan fallback covers both renamed handles.
- **§23 Q12 is closed, by deviation.** The `nr-*` library is on live (767 → 794, 0 errors, 0
  overwrites), owner-approved, after `nrtheme push` refused under R1 and `theme_guard.py` proved to
  have no apply-to-live verb — the write used `themeFilesUpsert` directly. The R2b browser test never
  ran; **G17/G18 remain open**, and `nr-sticky-cta`'s inline JS is inert only because nothing
  references it.

### What was NOT done

No theme, product, order, campaign, ad, keyword or budget write. No live-theme guardrail gate was
exercised beyond read-only `check`. The cleanup remains blocked pending the owner's decision, because
the only paths to a live theme file are a §R3 snapshot-and-approve cycle or another explicit Option-B
deviation, and neither should be taken to fix an inventory count.

## What v2.4 deliberately did NOT change

- **§1.6's CVR contradiction (1.5% vs 2.3%) — RESOLVED in v2.4.1** (2026-10-01): see above. It stayed open through v2.4 only because it governs a spend decision, not system structure; it is fixed now so the 10× path is internally consistent before any build.
- **No economic claim was made or resolved.** v2.4.1 fixes the *scenario arithmetic*; it still makes no profitability assertion — break-even and go/no-go remain decisions computed by UNIT 1.5 with real `C_new`.
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

See `AUTONOMOUS-ADS-ARCHITECTURE2.md` §23 **Q11–Q20**. The two that gate work:

1. **Q11 — is the `Nordisk Wellness Kit` zero-inventory condition real?** — **RESOLVED 2026-10-02** (owner-confirmed).
   It was never a stock condition: inventory tracking is off store-wide, so `inv=0` was a static
   placeholder and the product has no stock ceiling. G21 is closed and `P-STOCK` was removed in v2.4.2.
2. **Q12 — publish the `nr-*` library under the §R3 gated path? — CLOSED 2026-10-02, by deviation
   (recorded v2.4.6).** All 27 files are on live (`767 → 794`, 0 errors, 0 overwrites), owner-approved,
   after `nrtheme push` refused under R1 and `theme_guard.py` proved to have no apply-to-live verb — so
   the write went through `themeFilesUpsert` directly. **The R2b browser test never ran and G17/G18
   remain open**; the `nr-sticky-cta` inline JS is inert only because nothing references it yet. UNIT
   1.21 is unblocked for page instantiation.
3. **Q13 — image generation provider?** Facts corrected 2026-10-01 (OpenAI key absent; OpenRouter
   `google/gemini-3-pro-image` available). Owner pick still outstanding; determines §12.5 tooling.
4. **Canonical Wellness Kit handle — RESOLVED 2026-10-02 (§23 Q19).** `nordisk-renhet-wellness-kit` (variant `51167026741582`). The rival 1-media stub was **withdrawn by the agent who proposed it**. Sales could not break the tie (every Swedish record: zero units ever) and did not need to — media count and creation date decided it. `nordisk_ads_context.json` stops being provisional. **Carried forward, scope corrected v2.4.6:** the stub pair spans **7 live files (6 sections + 1 snippet)**, of which **4 sections are wired to published pages** — not "3 sections". Each needs handle + productId (`10246605144398` → `10161700766030`) **in the same edit**, since the paired `productId` is the authority whenever the handle misses and a handle-only change is a no-op. Two preconditions now sit in front of it: the move takes the product block from **1 media to 10**, which **turns the `gp-carousel` gallery on** (§R2b browser test required, never yet run on this theme), and the canonical record's **Swedish** title would land on `/pages/itchy-skin`, which is English and carries **2 ENABLED ads** in a Swedish campaign.
5. **Q20 — scope of the funnel contract — RULED 2026-10-02.** The owner's rule is a **purchase-intent
   rule, not a stage rule**: a product page is permitted as an ad destination where intent is
   demonstrated (brand / `MOST_AWARE`, or a user tracked across prior ad touches) and is never
   permitted for cold non-brand acquisition. This **halved the violation count to 2 of 22** — the three
   `BRAND` ads v2.4.3 listed are correct under the ruling; the 2 real violations are the non-brand
   product-page ads, and a fifth brand ad is flagged for pointing at `/collections/all`.
   `SOLUTION_AWARE` / `PRODUCT_AWARE` → `PRODUCT` were **left in §13.2, still flagged** — the ruling
   does not address them. The owner flags his own answer as provisional, and its multi-touch half is
   **not executable**: it presumes a retargeting layer that **§22.3's display gate blocks** until ≥30
   store orders/month × 2 against a measured 9/month. Recorded as intent, **not** a build ticket.
6. **Q14 — brand vs activation policy.** A per-ad optimiser converges on most-aware direct-response
   angles. Correct for the spec's stated objective, wrong as a description of how a brand grows.
   Default applied: activation-only, **explicitly labelled as such in the digest** so the limitation
   is visible rather than silent.
