# HANDOFF — Google Ads CLI state + Autonomous Ads Spec review

Paste this whole file into a fresh session. It assumes shell access to the production box
and no other prior context.

---

## 0. Who / what

Owner = Maestro, ecommerce manager, Nordisk Renhet (Swedish water-filtration D2C, Shopify).
You are the assistant with shell access to the production box at `/root` and
`/mnt/HC_Volume_105587324/nordisk`.

Two workstreams are open:

- **A. Google Ads CLI** — repaired last session, live and verified. A few cosmetic openers remain.
- **B. Autonomous-ads spec review** — an external builder produced a very large spec
  (`AUTONOMOUS-ADS-ARCHITECTURE2.md`, v2.3) for a self-optimising Google Ads system.
  We reviewed it three times. It is **not yet applied**. One arithmetic contradiction and
  one assumed number block it.

Engrane is a separate project — do not touch it in this session.

---

## 1. HARD RULES (non-negotiable, apply to everything you do)

1. **Google Ads account 8479789152 is denominated in AUD, NOT SEK.** Shopify is SEK.
   Never conflate them. `cost_micros` = AUD micros.
2. **Never discuss paused campaigns.** Only ENABLED. You may learn from paused data
   (negatives, search terms, copy) but must not present paused campaigns as live.
3. **Shopify theme guard:** NEVER write to or publish the live theme
   (locked id `195492381006`). All theme work on a duplicate unpublished theme only.
   Duplicate creation failure = STOP and ask, never fall back to live.
4. **100-day money-back guarantee** — never 60.
5. **Filtration specs are hardcoded truth:** inline filter = KDF-55 + CaSO3 + GAC
   (triple media); shower head = activated carbon fibre ONLY (no KDF-55, no CaSO3, no GAC).
6. **Copy vocabulary:** only spec-sheet / site claims. Banned: "oberoende tester", "TEWL",
   "clinical research". Never fabricate customer quotes in product copy.
7. **Every ad landing URL must return HTTP 200, HTTPS, www canonical**, and the page
   language must match the campaign language (SV→SV, EN→EN).
8. **Secrets:** if a real credential appears in a transcript it is burned and goes on the
   rotate-today list. Values live in `/root/.secrets.env` (chmod 600), read via
   `secrets get NAME` in command substitution. Never echo a value.

---

## 2. WORKSTREAM A — Google Ads CLI (state: FIXED, LIVE)

### What was broken

| # | Problem | Cause |
|---|---------|-------|
| 1 | `go` broken globally | `/root/go/bin` (entire GOPATH dir) had been deleted |
| 2 | OAuth refresh token dead | `invalid_grant`; nobody had a re-auth path |
| 3 | API 403 | **Not auth.** config `login-customer-id = 9768229544` — an account Maestro's Google user has ZERO access to. Correct id is `8479789152` |
| 4 | Dead code | `refresh-ads-token.sh` parsed with `cut -d'"'` while config uses single quotes; grepped `developer_token` when the key is `ads_developer_token`. Nothing referenced it |

### What was fixed

- Recreated `/mnt/HC_Volume_105587324/go-path`; reinstalled `google-ads-pp-cli`
  **v2026.9.1** → `/root/go/bin/google-ads-pp-cli` (20 MB).
- Built `/mnt/HC_Volume_105587324/nordisk/bin/gads-auth.py` (re-auth + refresh + check).
  Re-auth completed by Maestro in browser; refresh token live and verified by a fresh
  `refresh_token` grant returning a valid access token.
- Built `/mnt/HC_Volume_105587324/nordisk/bin/gads-env.sh` — **single source of truth**
  for auth + customer id. Every other script now sources it. This makes customer-id
  drift structurally impossible (the drift was the root cause of #3 spread over 3 files).
- Customer id corrected to `8479789152` in config and all callers.
- Developer token moved out of plaintext into the secrets store.
- `bin/harvesters/ads-monitor.sh` rewritten **ENABLED-driven**. The old hardcoded
  campaign-id list included one campaign id that does not exist and two paused ones —
  guaranteed false alerts and a violation of rule 1.2.
- Parser hardening so a malformed API response can't kill a run. `TOKEN_REFRESHED` /
  `inserted` grep contract preserved for downstream consumers.
- Dead `refresh-ads-token.sh` deleted (backup kept).
- **Verified live:** query returns `Nordisk Renhet`, currency `AUD`, 4 campaigns.

### Damage the bad customer id had been causing (silently)

| Job | Schedule | Failure |
|-----|----------|---------|
| `bin/harvesters/ads-monitor.sh` | daily 06:37 | **115 failures** in its log |
| `bin/weekly-ads-checkpoint.sh` | Mon 07:07 | failed **8 of the last 9** runs |

The single "successful" run (Sep 14) wrote **all zeros** and then a confident
recommendation: *"Minimal spend this week. No conversion data yet — normal for
low-traffic period."* A broken job produced a plausible all-clear, and that file was the
live ads checkpoint. Lesson: an all-clear from a job whose success path was never
exercised is not evidence.

### Open items in workstream A

1. **Developer token is burned** — it appeared in a transcript while diagnosing. By rule 1.8
   it must be rotated at Google. It had also been sitting in plaintext in 3 scripts + `.env`
   + a stale `.env.pretokbak`.
2. **A cleanup rule is a dormant landmine.** `DELETE ... WHERE status='PAUSED' AND
   impressions=0 AND clicks=0 AND cost_micros>0` destroys real paused history. It matches
   0 rows today, but the account holds ~187 paused rows / ~2,270 AUD that Maestro's own
   rules say may still be mined for learnings.
3. **`token_expiry` is never updated** by any script (the `sed` writes only the token),
   so that field drifts.
4. `sed -i` token injection is fragile — an `&` or `/` in a token corrupts `config.toml`.
5. `weekly-ads-checkpoint.sh` was historically a 280-line divergent near-copy of
   `refresh-ads-data.sh`. That divergence is *how* the customer id drifted. Verify the
   shared-bootstrap refactor fully closed this.

### Key paths

```
CLI binary     /root/go/bin/google-ads-pp-cli
env bootstrap  /mnt/HC_Volume_105587324/nordisk/bin/gads-env.sh
auth tool      /mnt/HC_Volume_105587324/nordisk/bin/gads-auth.py
harvester      /mnt/HC_Volume_105587324/nordisk/bin/refresh-ads-data.sh
monitor        /mnt/HC_Volume_105587324/nordisk/bin/harvesters/ads-monitor.sh
weekly         /mnt/HC_Volume_105587324/nordisk/bin/weekly-ads-checkpoint.sh
databases      /mnt/HC_Volume_105587324/nordisk/db/{nordisk,ads_decisions,
               pixel_track,keyword-intel}.db
```

---

## 3. WORKSTREAM B — Autonomous Ads spec review

### What the spec is

`AUTONOMOUS-ADS-ARCHITECTURE2.md` v2.3 — ~3,400 lines, 98 build units, 8 phases, ~11 weeks.
Goal: a self-learning, self-healing, self-propelling Google Ads environment that launches
campaigns/ad groups/ads itself, manages keywords + negatives, respects language and landing
pages, optimises and scales budget.

Sources:
- Local handoff written for the builder:
  `/root/.nordisk/handoffs/opus-autonomous-ads-architect.md` (512 lines)
- Pushed to GitHub: `rx3asarc/sharedfiles` → `AUTONOMOUS-ADS-ARCHITECTURE-PROMPT.md`
- Spec v2.3 raw:
  `https://raw.githubusercontent.com/rx3asarc/sharedfiles/main/AUTONOMOUS-ADS-ARCHITECTURE2.md`
  md5 claimed `0902b5370e40421e92bafa934b22b1dd` — **verify with `curl -sL <url> | md5sum`
  and stop if it differs.** (v2.2 md5 `3d176479…` also matched its claim when checked.)

### The review loop, and the mistake in it

- **v1 verdict:** A-grade spec, **D-grade scope discipline.**
- **I (the assistant) made a typo** — wrote "273 orders / 90 days = ~9/month", which is
  internally incoherent. The real query returns **27 orders / 90 days = ~9 orders/month.**
  The builder caught this and correctly refused to build on it.
- **The builder then built a scope argument on "91 a month, already close to your first
  target of 100"** — off by **11x** — and used "at ~91 orders/month the email and offer tests
  have real traffic" to justify scope. That premise is false.
- **I conceded one point fully:** my "CTR prior strength 200 is too strong" criticism was
  wrong. 200 pseudo-impressions against 2,145 real impressions is ~9% of the evidence —
  a sane prior, not an overconfident one.

**Verified baseline (measured, not quoted):**

| Metric | Value |
|--------|-------|
| Orders, 90 days | 27 (web 23, subscription 3, one stray) — ~9/month |
| Orders, 6 months | 33 — ~5.5/month |
| Orders, lifetime | 111 (95 paid) |
| AOV 90d | 1,562 SEK (30d 1,497) |
| GSC 30d | 992 clicks / 43,858 impressions, 871 queries |
| Top article | 663 clicks = **67% of ALL organic clicks**, ranked 1.3–2.6 |
| Ads 30d ENABLED only | 39 clicks / 48.24 AUD / 0.61 conversions |
| Ads 30d all-in | 223 clicks / 470 AUD (bulk = recently-paused legacy rows) |
| No draft/test orders in window | 36 drafts are all zero-value, all 2024–25 |

### The two findings that survived every round

1. **67% of all organic clicks land on ONE article** — `jamfor-duschfilter-bast-i-test-2026`,
   663 of 992 clicks, on "bäst i test" comparison intent. The highest-EV surface in the store
   is comparison content on a pipeline that already exists and already has gates.
   *Calibration:* the live page already has 12 product links and 12 CTA components; it
   lacks price (1 mention) and has 0 add-to-cart forms. So raising its commercialisation is
   a small CTA upgrade, not an editorial rewrite.
2. **COGS was found** — HyperSKU supplier export: 18,257 SEK revenue vs 6,711 SEK cost
   = **63.2% gross margin**. This kills the *assumed* 45–50% margin that the spec's entire
   paid-business case rested on.

### The blockers — why the spec is NOT applied yet

**Blocker 1 — §1.6 contradicts itself within three paragraphs.** It sets paid click
conversion at **1.5%**, then two paragraphs later states paid needs **2.3%** to break even.
The 100-order headline depends on it.

```
3,500 clicks x 2.09 AUD =  7,315 AUD spend
  52 orders x 91 AUD    =  4,766 AUD contribution
                          ─────────────────────
NET                        -2,549 AUD/month
breakeven needs 81 orders, not 52
```

At 1.5% CVR you don't buy 52 profitable orders — you buy 52 orders at 139 AUD each against
91 AUD of contribution. The paid pillar of the 10× path is loss-making by its own numbers,
~16,000 SEK/month.

It also collides with **§8.5 D21** (the marginal rule: incremental CM ≥ floor × incremental
spend), which would refuse exactly this spend. §1.6 and D21 disagree about the same money.
Note: the *governor* is revenue-linked, not contribution-linked, so it permits loss-making
spend as long as revenue rises — the governor is not the protection it looks like.

**Blocker 2 — the margin was ASSUMED while the spec's own new rule forbids that.** §1.6 does
arithmetic on a 45–50% contribution while **§0.2** (a rule the builder just adopted, at our
request) says a number supplied by a person or pasted from chat enters as `NO_DATA` until a
named, stored query reproduces it. §1.6 is precisely such a number. The go/no-go must run
**before** §1.6 becomes a target.

### Spec strengths (keep, largely as written)

- **"Zero is a claim that must be earned"** — `MEASURED_ZERO` requires a complete coverage
  record + eligibility, one accessor, one lint test. Best single idea in the doc; it targets
  a bug that has been lying to this account for months.
- **Phase 0 = Repair the lies.** Fix tracking before optimising. Correct call.
- **Governor replaces fixed 35%** — `r = contribution_ratio − profit_target`, bounded
  0.10–0.50.
- **Refund-discounted contribution in SEK, not platform ROAS**, with AUD/SEK FX discipline.
- **Honest power notes (§20.6)** — refuses to fake statistics at 39 clicks.
- **Real failure semantics** — inverse ops, idempotency keys, read-back verification,
  fail-closed to NO_ACTION, pause-only cap process the optimiser cannot write.
- **Rule-compliant** — respects the theme guard, AUD rule, paused-campaign rule, filtration
  specs, 100-day guarantee, claims vocabulary.

### Spec problems (beyond the two blockers)

- **Density mismatch.** Hierarchical shrinkage, 20k-draw posteriors, 100-idea banks, conquest
  scoreboards, market-entry packets — for an account where every posterior collapses to the
  parent. The doc admits this (§8.2) then builds it anyway.
- **The 350 currency ambiguity.** §3.5 says "350 SEK/day (≈55.6 AUD)"; the same section's
  ceiling row says 350 **AUD**/day. Both arithmetically right, semantically opposite,
  6.3x apart — in a doc whose thesis is currency discipline.
- **T3 conflicts with its own ceiling.** 100 orders/day at ~1,000 SEK AOV inside a
  350 AUD/day ceiling is not reachable via paid. State that T3 is a *total-store* target.
- **Ramp cadence presented as plan, not forecast** — label it "not a forecast."
- **Over-broad autonomy where blast radius ≠ spend.** Autonomous discounts/bundles (20%
  depth) and autonomous email broadcasts. The guard protects *margin*, not price integrity
  or sender reputation. Gate those to approval. **Broadcasts must never be autonomous —
  you cannot unsend an email.** A discount depth cap the system can raise itself is not a
  cap; it must be owner-only.
- **Self-granted rule exception** (§Q7 rewrites the paused-campaign rule as an "open
  question"). Reasonable reading, but flag it as a rule change request.
- **Unproven assertion in §1.5** — "the 0.61 Ads conversions are an artefact of broken
  tracking, not the sales rate." Elsewhere the doc is careful; here it pre-commits to the
  good branch. Phase 0's job is to distinguish broken tracking from "ads genuinely don't
  convert."
- **97 units is a second job.** No build-cost estimate beside eight rows of "Money: none."
  "Money: none" ≠ "cost: none." Needs a named maintainer.
- Housekeeping: §4 header appears twice.

### Verdict and priority order

```
APPLY   Phase 0, Phase 1, Phase 1b
FIX     §1.6 CVR conflict (1.5% vs 2.3%), reconcile with D21
        Run the go/no-go BEFORE §1.6 becomes a target
ADD     GSC rank guard on the 67% article (rollback as a
        promotion condition, not just an option)
```

**Do these in this order:**

1. Run the **Phase-1 go/no-go** — cheap, decides everything. §1.5 already computes it: at
   CPC 13.17 SEK, break-even needs C_new ≥ 658 SEK at 2% CVR — only **Wellness Kit (2,189)**
   and **Full Home Filtration (4,283)** clear it. So the real finding is: *route all non-brand
   to those two products, or don't run non-brand.* It is buried in prose; it should be the
   output of Phase 1.
2. Fix §1.6 (5 minutes of editing).
3. Rotate the burned developer token.
4. Build Phase 0.

Note the corrected economics cut the other way from the spec's pessimism: 90-day AOV is
**1,562 SEK** (the spec used a ~400 SEK illustrative placeholder), so at ~45–50%
contribution C_new ≈ 700–780 SEK, which *clears* the 658 SEK break-even at 2% CVR. Combined
with the real 63.2% margin, the go/no-go may well come back **"go on non-brand"** — worth
knowing before spending 11 weeks building the machinery to find out.

### STOP RULE (pre-agreed, do not relitigate)

The spec has been reviewed three times. Review cycles now produce diminishing diffs at real
cost. **Apply the fixes, then stop judging and build Phase 0.** Do not open a fourth review
round unless a specific section's arithmetic is found wrong.

---

## 4. Files to read before acting

| Purpose | Path |
|---|---|
| Spec review answer (the cheapest-path analysis) | `/root/prompts/cheapest-path-100-orders-answer.md` |
| The prompt that produced it | `/root/prompts/cheapest-path-100-orders.md` |
| Builder handoff (512 lines) | `/root/.nordisk/handoffs/opus-autonomous-ads-architect.md` |
| This handoff | `/root/.nordisk/handoffs/HANDOFF-ads-cli-and-spec.md` |

DBs: `db/nordisk.db` (29 MB, orders/traffic/ads), `db/ads_decisions.db`,
`db/pixel_track.db`, `db/keyword-intel.db` — all read-only unless told otherwise.

---

## 5. Your first move

1. Run `bin/gads-env.sh` → confirm auth + customer id work (expect `Nordisk Renhet`, AUD).
2. `curl -sL <spec v2.3 url> | md5sum` → confirm `0902b5370e40421e92bafa934b22b1dd`.
   If it differs, say so and stop.
3. Read `/root/prompts/cheapest-path-100-orders-answer.md`.
4. Then ask Maestro which of these to do first — **do not start building unprompted**:
   - run the Phase-1 go/no-go
   - fix §1.6
   - rotate the dev token
   - or something else

---

## 6. UPDATE 2026-09-24 — spec amended to v2.4, generative layer added

### What was produced

| File | What |
|---|---|
| `/root/.nordisk/specs/AUTONOMOUS-ADS-ARCHITECTURE2-v2.3.md` | Frozen original (md5 verified `0902b537…22b1dd` against GitHub) |
| `/root/.nordisk/specs/AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.md` | **Amended parent spec** — md5 `50adf9fd920be5e2464a4a68b34e9007` |
| `/root/.nordisk/specs/AUTONOMOUS-ADS-GENERATIVE-LAYER-v1.0.md` | **New extension** — md5 `13cfe9a23bcb5798c9e31cf5a9e209ea` |

The parent was amended in place; the extension is a companion, deliberately not merged (§24.0) so that
grounded-vs-unverified stays visible.

### The reframe that drove it

Maestro's goal is **the system**, not just orders: a self-propelling ads environment. Reading §12 properly
(which the previous session did not do) shows the loop — winner cascade, idea bank, pattern library,
diagnosis table — **is already specified**. What was narrow was the *vocabulary it may emit*: no topic
research, no lander archetypes beyond an existing-template selector, generated imagery banned outright,
display parked. Hence "I don't know what's missing" was really "the doc says no in sections I haven't read".

### Findings that changed the work

1. **EU AI Act Art. 50 APPLIES FROM 2 AUG 2026 — in force 53 days at time of writing.** The Digital
   Omnibus deferred only Annex III high-risk. Guidelines final 20 Jul 2026. A realistic synthetic person
   IS a deepfake — "we invented the face" is not an exemption. Stylised imagery sits outside the
   "appears authentic" prong, which is why **stylised-by-default is both the compliant and the
   higher-performing choice** (pattern disruption). Replaces v2.3's blanket ban.
2. **The `nr-*` archetype library is a design asset, NOT a generator.** 12 native sections + 7 snippets +
   2 designed listicle templates exist in `theme-repo` — but all 27 files are absent from the live theme,
   AND the templates are fully-authored fixed pages (zero `nr-*` sections render `page.content`, zero read
   metafields), so instantiating one twice yields a byte-identical clone. One theme push **per page**, not
   per class. An earlier draft of this extension asserted the opposite; it was wrong and is corrected in
   §GL.4.1 and logged as gap GL-G15.
3. **There is a fully-autonomous content path that needs no theme work.** `page.json`,
   `page.contact.json`, `page.water-report.json`, `page.science.json` all render
   `{{ closest.page.content }}` (as a `text` block *setting*). So the archetype is a **content template**
   written into `body_html` — unbounded variety, zero marginal theme cost. This is what §12.6 always
   described. Archetypes are therefore generatable today.
4. **`page.science` / `page.water-report` are GemPages-derived** and §12.6 says GemPages pages are
   routable but **never created by adsys**. Rendering shells, not inherited artefacts (gap GL-G16).
5. **Image gen is feasible on OpenAI** (`OPENAI_API_KEY` present, SDK installed); `GEMINI_API_KEY` is
   **absent**, so the `gemini-imagegen`/`nrvision` path the v2.3 spec assumed cannot run without a key.
6. **Two platform defects block autonomous landing pages** (theme-repo G17, G18): interactive components
   only checked statically, add-to-cart never tested end-to-end. A page factory that has never proven a
   purchase can complete is generating pages of unknown commerce value.

### Owner decisions outstanding (parent §23 Q11–Q18)

1. **Q11 — is the `Nordisk Wellness Kit` zero-inventory condition real?** (theme-repo G21). Nothing
   generates until answered. If real, the highest-value routing target is unfulfillable.
2. **Q12 — publish the `nr-*` library?** Now **not** on the critical path for generation. Buys two fixed
   showcase pages + a design reference, not a page factory.
3. **Q13 — which image provider?**
4. **Q14 — brand vs activation policy** (the corpus's purpose depends on it).
5. **Q15–Q17 — display unlock, advertorial, corpus citation-vs-injection.**
6. **Q18 — Art. 50 amendments / marknadsföringslagen confirmation.**

### Review status

Both documents were adversarially reviewed by the `oracle` agent. It found 3 CRITICAL (fixed templates,
GemPages-not-creatable, §22 duplicate numbering), 15 MAJOR and several MINOR — **all fixed and
re-verified**. Notably it caught that the extension's own evidence register needed splitting (retrieved
external vs measured-on-box), that an unverified T4 blocklist was a hard gate (now GL-R3: unverified may
only `WARN`, never `BLOCK`), and that the theme-publish recommendation omitted the mandatory R3/R4/R5/R7
guard preconditions (now stated in full in §GL.8).

### First move if resuming

Unchanged from §5: `bin/gads-env.sh` → verify auth (account `Nordisk Renhet`, AUD) → then ask Maestro
which of go/no-go, §1.6 fix, token rotation, or Phase 0/1c first. **Do not start building unprompted.**

---

## 4. WORKSTREAM A UPDATE — 2026-10-01 (verified live on the box)

Re-verified every item from §2 "Open items in workstream A" against the live scripts. New state:

| # | Open item (from §2) | Status 2026-10-01 | Evidence |
|---|---|---|---|
| 1 | Developer token burned (appeared in a transcript) | Still **OPEN — provider action required** | Now stored only in `/root/.secrets.env` (exported via `gads-env.sh`), no plaintext in scripts/config. Rotation itself must happen at Google's API center; box-side hygiene is done. |
| 2 | Dormant `DELETE ... status='PAUSED' ...` landmine | **CLOSED** | Removed from `refresh-ads-data.sh` with an explanatory comment; the only remaining DELETE is a scoped id+date-window purge used by the upsert. No live script contains the junk-cleanup DELETE (verified by grep of `bin/` + `harvesters/`; only `ads-monitor.sh.bak-20260908` retains it, and no cron references any `.bak`). |
| 3 | `token_expiry` never updated (field drift) | **CLOSED (code) — live verification blocked on OAuth re-auth** | `gads-auth.py::save_access_token()` writes `token_expiry` (TOML datetime, unquoted) on every token mint, and `cmd_token()` documents the side effect. The drift cannot recur from the writer. NOTE: the live config's `token_expiry` was the LAST field the broken chain updated (2026-09-30) — the access token is stale because the refresh token expired, not because the writer is broken. |
| 4 | `sed -i` token injection fragility | **CLOSED** | `write_config()` is atomic (tmp → chmod 600 → `os.replace`), regex-replaces only known keys, preserves order, and keeps `token_expiry` unquoted. No `sed -i` remains in any live script. Unit-testable (see note below). |
| 5 | Weekly-checkpoint divergence / customer-id drift | **CLOSED** | `weekly-ads-checkpoint.sh` rewritten (header documents the incident), sources `gads-env.sh` exclusively, contains zero inline auth logic (verified: 0 matches for refresh/oauth/client_id), hard-fails on unparseable API output instead of emitting a confident all-clear. |

### NEW finding — why auth is down again (2026-10-01)

The refresh grant returns `invalid_grant` ("Token has been expired or revoked"). The last browser
re-auth was 2026-09-23; seven days later the refresh token dies — the signature of a Google OAuth
app still in **testing mode** (refresh tokens live ~7 days until the app is verified/published).
Two consequences:

- Re-auth by Maestro in the browser is required now (same flow as Sep 23).
- Until the OAuth app is moved from Testing to Production in Google Cloud Console, this will
  recur **every ~7 days**. Moving it to production is the durable fix and should be scheduled.

### CONFIG INCIDENT (2026-10-01, recorded honestly)

While unit-testing `write_config()`, the test harness imported `gads-auth.py` and a default
parameter bound `CONFIG` at import time, so the first test write hit the **real**
`/root/.config/google-ads-pp-cli/config.toml` with a synthetic token. Detected immediately;
repaired by restoring `config.toml.bak-20260923-193648` and re-applying the single source-of-truth
customer id (`8479789152`, verified present after restore). The OAuth client secret additionally
appeared in a transcript during diagnosis — by rule 1.8 it is **burned** and joins the developer
token on the rotate list. Lesson added: always pass `path=` explicitly in tests; never rely on
the module default against a live config.

---

## 5. PHASE-0 BUILD PROGRESS — 2026-10-01 (verified on the box)

The autonomy ladder is being built unit-by-unit with `run_guard_tests.sh` as the
gate. Phase 0 status:

| Unit | Status 2026-10-01 | Evidence |
|---|---|---|
| 0.1 skeleton + gads wrapper | **COMMITTED** (7b5b3b0) | 9 tests; gads-ping fails clean AUTH class live |
| 0.2 measurement state | **COMMITTED** (ee8e515) | 9 fixtures per §4.4; migration applied to NDB |
| 0.3 ads-monitor budget fix | **COMMITTED** (3500233) | A2/A3 query split (the §5.1 400 bug); budget_aud in output |
| 0.4 auth probe | **COMMITTED** (952539b) | incident inc-cce5d32256 opened on the real dead token |
| 0.5 Composio removal | **COMMITTED** (19a11aa) | 0 composio refs in Ads path; legacy parity tests |
| 0.7 Shopify ingest | **COMMITTED** (bdac81e) | 114 orders, 0 R7 failures, token out of scripts → secrets |
| 0.8 GA4 ingest | **COMMITTED** (00794ff) | 5 tables live, currency=AUD from metadata (answers §5.2) |
| 0.10 GA4-join diagnosis | **COMMITTED** (680fff1) | VERDICT CONFIRMED: 15/15 empty client_id → paid tx = 0 |
| 0.12 disk + temp hygiene | **COMMITTED** (b93a536) | sev-2 DISK_HIGH incident opened (root 92%) |
| 0.6 multi-grain ingest | NOT BUILT | blocked on live OAuth acceptance; code is buildable |
| 0.9 / 0.11 / 0.13 | NOT BUILT | depend on 0.6 / live API |

Phase-0 exit criteria status: Composio removed (DONE); zero/measured-zero
semantics (PASS); ads-monitor budget query (code DONE, live verify pending
re-auth); G-CONV-1 (pending owner action); 7 consecutive COMPLETE days
(pending OAuth re-auth — auth has been dead since 2026-09-30).

**The single unblocker for Phase 0 exit is the Google Ads OAuth re-consent**
(testing-mode app → refresh token expired; move app to Production or re-consent
weekly). Same re-auth unlocks the CLI dev-token rotation tracking.

---

## 6. UPDATE 2026-10-02 — Q11 closed, `P-STOCK` removed, tracker repaired

All verification below was **read-only** against Shopify and Google Ads. Nothing in the store, the
account, or any theme was changed. Spec edits are documentation only.

### 6.1 Q11 answered — the "zero-inventory" condition is not a stock condition

**Owner-confirmed by Maestro, 2026-10-02.** Live Shopify Admin API check (read-only):

| Check | Result |
|---|---|
| Wellness-Kit-family inventory items | **all 9 have every variant `tracked = FALSE`** (SE/DK/NL/LU/FR/EN + 3 legacy records) |
| `available` at the only linked location (`Smedsuddsvägen 23`) | `null` — never set; `Hypersku` holds no levels for these items |
| Store-wide control | **49 of 50 variants are untracked**; only `nordisk-duschhuvud-copy` is tracked |
| Live cart behaviour | buys the item — exactly what untracked means (no stock ceiling) |

An untracked variant has no stock limit, so `inv=0` is a static placeholder rather than a constraint.
Theme-repo gap **G21 is closed**. (Direct `.js` storefront probing returned HTTP 429 — Shopify bot
protection; the Admin API is the authoritative source and G21's own note already recorded that the
cart form buys it.)

### 6.2 `P-STOCK` removed from the pre-flight (canonical spec → v2.4.2)

The gate required `target variant inventory ≥ 5`, read from that same dead field, so it would have
failed closed on **every** Wellness-Kit lander — permanently. It is removed from the §13 pre-flight
chain. The `inventory` ingest is **retained** as a diagnostic snapshot and explicitly marked
"not a gate". §23 Q11 now reads **RESOLVED — owner-confirmed**.

### 6.3 Version-integrity defect found and repaired

`029cb48` ("Spec §23: record Q11/Q13 live-verification evidence", 2026-10-01) edited the canonical
file **without bumping the header version or updating `ADS-SPEC-VERSIONS.md`**. The md5 chain proved
it: `1c37fe1` → `80bd2dc9…` (declared) vs `029cb48`/HEAD → `04249f9c…` (actual). v2.4.2 folds that
undeclared edit into the version record, and v2.4.1 is frozen as
`AUTONOMOUS-ADS-ARCHITECTURE2-v2.4.1.md` so its md5 remains retrievable. The companion doc is bumped
to **v1.0.1** (GL.4.7 / GL.10 Q1 resolved) with v1.0 frozen likewise. No content was altered by this
repair.

### 6.4 Owner decision — which Wellness Kit is canonical? **→ now spec §23 Q19, PENDING ARBITRATION**

**This section is superseded by `AUTONOMOUS-ADS-ARCHITECTURE2.md` v2.4.3 §23 Q19.** It is kept for
the record, but its recommendation and its counts are both out of date — do not act on it.

Two candidates remain live after the 2026-10-02 repointing (the third was renamed, see below):

| Handle | id | Media | SEK | Why it is a candidate |
|---|---|---|---|---|
| `nordisk-renhet-wellness-kit` | `10161700766030` | **10** | 2,189 | CTA target of the live lander `/pages/duschfilter-jamforelse-bast-i-test` (SKU `NR-DOUBLE-FILTRATION`); created 2025-03-03 (oldest) |
| `nordisk-wellness-kit` | `10246605144398` | **1** | 2,189 | The handle `nordisk_ads_context.json` carried; **referenced by 9 theme files / 14 references**, so it is what most live landers buy |

**Renamed 2026-10-02:** `nordisk-wellness-kit-1` → `nr-nordisk-wellness-kit-1` (and
`nordisk-renhet-welcome-kit` → `nr-nordisk-renhet-welcome-kit`), via REST `/redirects.json`.

**Three corrections to this section's earlier form:**

1. **The recommendation was wrong.** It picked `nordisk-wellness-kit` — the **1-media stub** — and
described the 10-media record as "legacy". The evidence points the other way: the 10-media record is
the older one, the better-equipped one, and the one the comparison advertorial already buys.
2. **"The seven 2,211 SEK duplicates should be drafted or consolidated" is wrong and dangerous.**
   There are **six** localized records, not seven, and they are **not duplicates**: Shopify cannot vary
   product images per locale, so a localized image set forces a separate record. Consolidating one
   destroys that locale's entire image set. Only the Swedish group was ever a real choice.
3. **No ad final URL points at any Wellness Kit** (verified across all 22 ENABLED ads, 2026-10-02), so
   this decision moves no live ad — the kit is reached from a lander's **CTA**.

**Sales cannot break the tie:** all three original Swedish records are at **zero units sold ever**. The
single sale in the family belongs to the renamed third record, whose intended market is itself
unresolved (per Q11 / handoff §U2).

**Provisional state:** `nordisk_ads_context.json` was repointed to the 10-media record on 2026-10-02,
and that edit reverts in one line. It is *not* recorded as settled.

### 6.5 What still blocks

1. **Google Ads OAuth re-consent** — unchanged; still the single Phase-0 exit blocker and the precondition for §6.6 live verification and the CLI workstream.
2. **Q12** — publish the `nr-*` library under the §R3 gated path. This is now the **first** blocker on UNIT 1.21 (it previously sat behind Q11). It is a theme write, so the live-theme guardrail governs the path.
3. **Q13** — image-provider pick. The working path is OpenRouter `google/gemini-3-pro-image`.
4. **Canonical handle** — §6.4, now spec §23 **Q19**, pending arbitration.
5. **Funnel-contract scope** — spec §23 **Q20**: the owner's *never an ad → product page* rule conflicts
   with §13.2's `PRODUCT` lander class and §13.3's `"Klor & Vatten" → product page` bucket. 5 of the
   22 ENABLED ads violate it today and are left in place pending the ruling.

---

## 7. UPDATE 2026-10-02 (later) — OAuth re-consented: auth LIVE, first real data since 2026-09-30

**The Phase-0 exit blocker is cleared.** Maestro completed the browser consent; the code was exchanged
on the box and verified live. Nothing in the ad account was changed — read + local ingest only.

### 7.1 Verification chain (all green)

| Step | Result |
|---|---|
| `gads-auth.py finish <callback>` | exchanged; tokens saved |
| `gads-auth.py check` → live API | **OK** — `customers/8479789152`, descriptiveName `Nordisk Renhet` |
| `token_expiry` in config | written as `2026-10-02T13:12:37+02:00` |
| `gads-auth.py refresh` (durable path) | **OK** — fresh access token minted from the stored refresh token |
| `refresh-ads-data.sh` | `TOKEN_REFRESHED`, `{"ok": true, "inserted": 59, "campaign_count": 4, "date_range": "2026-09-02 to 2026-10-01", "stale_rows_deleted": 58}` |
| `harvesters/ads-monitor.sh` | ran clean (this job had **115 failures** under the bad customer id) |

Workstream-A open item **#3 (`token_expiry` drift) is now live-verified**, not merely code-closed: the
writer updates the field on every mint, and the field is correct after a real refresh.

### 7.2 First real campaign data since 2026-09-30 — ENABLED only (rule 1.2)

Spend in **AUD** (account 8479789152), window 2026-09-02 → 2026-10-01:

| Campaign | AUD | impressions | clicks | conversions |
|---|---|---|---|---|
| **EU EN \| Discovery \| Broad Match** | **455.82** | 3195 | 164 | **0.0** |
| SV SE \| Brand - Search | 76.58 | 167 | 59 | **0.618** |
| SV SE \| Search \| Investigative | 47.81 | 453 | 36 | 0.0 |
| SV SE \| Discovery \| Broad Match | 17.67 | 167 | 9 | 0.0 |

Two observations, recorded as findings rather than actions (no change was made):

1. **Brand search carries the only measured conversions in the account** (0.618) — materially different
   from the 0.009/90d figure the whole spec was briefed against. Confirm the conversion action behind
   it before treating it as a signal (§0.1: an unverified number is `NO_DATA`).
2. **The EN discovery broad-match campaign is ~76% of enabled spend with zero conversions.** It is
   also broad match, and the standing rule requires ≥20 effective negatives on any broad campaign
   before it runs — check `P-NEG20` against it before drawing conclusions. No bid, budget, keyword or
   negative was altered.

### 7.3 Durability — the recurring break is NOT yet fixed

Auth died three times on the same ~7-day cycle (last re-auths: 2026-09-23 → 2026-09-30 → 2026-10-02).
That is the signature of the OAuth app still being in **Testing** mode, where refresh tokens expire in
about seven days.

**The durable fix is publishing the app** (OAuth consent screen → Publish app; or set User type
**Internal** if the Google account is on a Workspace domain). **Not yet confirmed done.** Until it is,
expect to repeat this re-consent weekly — and note that Phase-0's exit criterion of *7 consecutive
COMPLETE days* is exactly the interval the token survives.

### 7.4 Still outstanding in workstream A

- **Developer token rotation** — provider action at Google's API center (item #2, §2). Box-side
  hygiene is done: it now lives only in `/root/.secrets.env`, via `gads-env.sh`.
- **OAuth client secret** — burned in a transcript on 2026-10-01; rotate at Google Cloud.
- **OAuth app → Production**, per §7.3.

---

## 8. CORRECTION 2026-10-02 — the Wellness Kit "duplicates" are localized records, not duplicates

**Raised by Maestro; verified against the Admin API.** The `ADS-SPEC-VERSIONS.md` §6.4 loose end was
framed as "three handles claim the Wellness Kit". That was wrong on the count and wrong on the cause.
There are **nine** records in **two** groups:

- **Six localized records** (`nordisk-kit-ien-etre` FR, `nordisk-welcome-kit` EN,
  `nordisk-wellness-kit-1` DE, `nordisk-wellness-saet` DA, `nordisk-welness-kit` NL/LU,
  `nordisk-welness-pakket` NL/BE). Each carries a **complete ten-image set in its own language**
  (`French_*`, `Danish_*`, `Luxembourgish_*`, `Flemish_*`, …). **Shopify cannot vary images per
  locale, so these must stay separate products** — consolidating one product with localized text
  would destroy six sets of localized imagery. They are legitimate.
- **Three Swedish records** (`nordisk-renhet-wellness-kit` 10 img, `nordisk-renhet-welcome-kit` 8 img,
  `nordisk-wellness-kit` **1 img / stub**). All 2,189 SEK. This is the real decision.

**Three defects found in the localized group (recorded, not acted on):**

1. **Only `en`, `fr`, `sv` are published store locales.** The DE, DA, LU and NL records therefore sell
   in languages the storefront does not serve — they cannot be reached by a language-matched shopper
   until those locales are added.
2. **Narrow channel set.** All six are published to *Online Store + AI channels only* — **not** to
   Google & YouTube, Shop, Facebook & Instagram or Pinterest. So they cannot appear in Shopping or
   paid-social feeds. The Swedish records carry the full channel set.
3. **Price drift.** The six carry **2,211 SEK**; the spec's hardcoded truth is **2,189** (= 990 + 1,199)
   and the Swedish records use 2,189.

**Two factual corrections to my own earlier record:**

- **No ad final URL points at any Wellness Kit.** Live-verified 2026-10-02 across all **22 enabled ads
  in the three delivering campaigns**. The kit is reached from the **lander's CTA** (e.g.
  `/pages/duschfilter-jamforelse-bast-i-test`), not from the ad's landing URL. No live ad moves
  whichever handle is chosen.
- `nordisk-wellness-kit-1` has **five** localized siblings, not seven.

**Consequence for the spec — the real gap.** The single-canonical-handle assumption is the defect. Since
localized imagery forces separate records, **§6's CTA/product resolution must be locale-aware**: an `en`
or `fr` campaign must not be routed to a Swedish record. Left as an open decision.

**Also observed while verifying:** only **three** campaigns have enabled ads (`SV SE | Brand - Search`
3 URLs, `SV SE | Conquest | Competitors` 10, `SV SE | Discovery | Broad Match` 7). The two zero-conversion
spenders — **`EU EN | Discovery | Broad Match` (455.82 AUD)** and **`SV SE | Search | Investigative`
(47.81 AUD)** — have **no enabled ads at all**, i.e. they spent and then stopped. Not touched.

---

## 9. UPDATE 2026-10-08 — goal-pool state mirror (`push-status`)

**Read this section first if you are resuming.** It is the current state of the executing goal; everything
above it is history that is still accurate but no longer current. Nothing in this section changes the spec —
`AUTONOMOUS-ADS-ARCHITECTURE2.md` is still v2.4.7 (`0df8be10af748a36eed41c41af830656`) and the companion is
still v1.0.1 (`6997f1b14ca771346f11b3afbab1ed7a`).

### 9.1 Where Phase 0 stands (4 of 5 MET)

`docs/PHASE0-EXIT.md` in the code repo (commits `c62bb05`, `03114cb`) is the authority; evidence paths there
are relative to `/root/handoffs/nordisk-goal/`.

- **MET:** criterion 1 (hot daily gads grains 7/7 COMPLETE, 2026-10-02..08), criterion 2 (guard gate,
  24 PASS / 0 FAIL at this measurement — see 9.2), criterion 3 (2026-10-08 06:07 run returned budget data),
  criterion 5 (`G-CONV-1` gate row sent with its payload).
- **PENDING:** criterion 4 (Composio out of the Ads path, 3 consecutive days). The fix landed 2026-10-08
  07:48, after that day's 06:07 run, so the three qualifying days are **2026-10-09/10/11** and the earliest
  possible close is **after 2026-10-11 06:20**. Do not close on a bare "OK" log line — the A20 trap — and do
  not close on one day.

### 9.2 Two numbers you must not quote from memory

- The code repo's suite count has moved repeatedly this shift (259 → 273 → 275 → 290 → **303**). The
  **measured** state for this mirror is: guard `./run_guard_tests.sh` → **24 PASS / 0 FAIL**;
  full suite → **303 tests, 1 failure**.
- That single failure is a **false positive in a hygiene test**, not a product defect:
  `adsys.tests.capture_fire_tests.ReadOnlyAndHygieneTests.test_never_runs_at_or_dumps_the_environment`
  asserts `assertNotIn("at -c", self.src)` over the whole module source, and `bin/adsys-capture-fire.py`
  names that prohibition **in its own docstring (line 18)** — it never executes `at -c`. Consequence:
  criterion 2's PASS currently rests on the guard gate alone, and the 2026-10-11 close must re-measure a
  green suite or explicitly disposition this failure. **Close condition, explicit:** criterion 2's acceptance
  is closed on a re-measured GREEN suite, or this failure is explicitly dispositioned at the close. Fix belongs
  to the code repo's owner (assigned to helper-1).

### 9.3 Landed since the last pushed update

- **UNIT 0.13** — read-only recon landed (no write path).
- **§15.3 weekly cadence** — `adsys/weekly_selftest.py` + tests + `selftest.broken_inject` in
  `adsys/config/schedule.toml`; live at `/etc/cron.d/adsys-selftest` (`30 4 * * 1`); commit `df9c7dc`.
- **Closed:** 0.6, 0.7 (`0.7a` landed; `0.7b` held until the Phase-0 close), A7, C6, F7, W-1.

### 9.4 Phase 1c — where the plan side is

- `docs/plans/2026-10-08-GENLAYER-1C-PLAN.md` **v1.3** — md5 `1faed3426dbd39b3860150c1d338efa2` (UNIT 1.19–1.23).
- `docs/plans/2026-10-08-A13-STAGE-RUNG-RULING.md` — md5 `81d0aa98474b7d5fa87aaa6f7fd562d2` (576 lines).
  §12.6 **L1720 is the account-stage gate** (a different axis from the surface entry rung); new page
  archetypes enter at **surface Stage 1** (GL-R2a + scope L87), imagery/display at **Stage 0** (L1722); no
  surface above the account stage; the parent's L1722 archetype sentence and §21 UNIT 1.21 L2916 get a dated
  amendment to Stage 1. **Until that amendment lands, no generation, routing or publish on 1.21.**
- `docs/plans/2026-10-08-PHASE1-OWNERSHIP.md` — commit `f5f08d0` (one owner per unit and per file).

### 9.5 Still open

1. **Q13** image-generation provider/key; 2. **Q12** acceptance 1.21 #1 as written is false today
(theme repo 816 vs live 794 files) and `THEME_PUBLISH` stays human-gated; 3. **criterion 4** to 2026-10-11;
4. the false-positive suite test in 9.2.

### 9.6 First move on resume

Read `docs/PHASE0-EXIT.md` (it is short and it carries the close procedure), then check the three
`criterion4-<day>.json` files for 2026-10-09/10/11 before touching anything else. Do not re-run an ingest by
hand and count it.
