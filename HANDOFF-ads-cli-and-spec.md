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
