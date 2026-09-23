# AUTONOMOUS-ADS-ARCHITECTURE.md

Spec for OWL (Builder). Responds to `HANDOFF-PROMPT-claude-opus5-rev3.md`. Version 2.3, 2026-09-23 — measured baseline (9 orders/month) and the 10× path (§1.6), Builder-run growth levers ahead of the autonomy ladder (Phase 1b), Phase 1 go/no-go, funding gates, cost of ownership, email broadcasts never autonomous; v2.2: full-funnel cascade autonomous (§12.11), 100-idea bank ranked by proven evidence (§12.12), Klaviyo clone-and-vary (§12.13), runtime independent of the agent harness (§17.9); v2.1: margin-derived spend governor, day-one import of existing Google Ads knowledge (§16.10), winner loop and funnel cascade (§12.11); v2.0: total-store growth target under a revenue-linked spend governor (§3.5, §3.7), proven-demand sourcing (§10.0), conquest layer: category scoreboard, answer engines, lander factory (§10.5–10.7), creative feedback loop and pattern library (§12.8–12.10), localized market entry (§14.7). Section 21 is the executable plan; everything else is its contract.

---

## 0. Design Principles

1. **Measurement integrity outranks optimisation aggressiveness.** An action taken on a wrong number costs money twice (the spend and the false lesson); an action not taken costs only time.
2. **Zero is a claim that must be earned — and so is every number.** A metric is `MEASURED_ZERO` only when a `COMPLETE` coverage record exists for that source, grain and window *and* the entity was eligible to serve; otherwise it is `NO_DATA` or `BROKEN`, and no consumer can read it as zero (enforced by one accessor and a lint test, §4.4). A number supplied by a person or pasted from a chat enters as `NO_DATA` until a named, stored query reproduces it.
3. **Deterministic code decides; LLMs classify, generate and explain.** Every spend-affecting decision is a reproducible function of stored inputs; LLM outputs enter policy only as enumerated labels that have passed schema validation and agreement checks.
4. **Shopify is revenue truth, the first-party tracker is the attribution spine, Google Ads and GA4 are diagnostics.** Shopify is the only source recording money that arrived; the tracker is the only transaction-keyed record this box controls.
5. **The objective is refund-discounted net contribution in SEK.** Not clicks, not revenue, not platform ROAS; brand is reported separately because it mostly harvests demand that already exists.
6. **Decide at the level where the data is.** Rates pool upward (keyword → ad group → campaign → role → account) with fixed-strength shrinkage; the system acts at the lowest level whose posterior is informative, which at low volume is the campaign and at 100+ orders/month increasingly the ad group.
7. **Relevance decisions need no statistics; profitability decisions do.** Negating "schampo" needs one impression; pausing a relevant keyword needs spend of at least one order's contribution with zero purchases and a posterior that says so.
8. **Bounded autonomy with veto, never approval.** Every autonomous act carries an envelope, a written hypothesis, a pre-committed kill rule and a stored inverse operation; only the five §4.13 gates block.
9. **The cap layer sits outside the optimiser.** A separate process with its own config file and its own pause-only write path; the optimiser can request budget, never grant it.
10. **Inaction and failure are logged assets.** Every cycle records what it considered and did not do and the condition that reopens it; every kill writes a fingerprinted failure record with a machine-checkable retry condition.
11. **Conquest in coverage, discipline in money.** The system tries far more queries, creatives, pages and markets than a human team could, and pays for each only inside the revenue-linked spend governor and the incubation envelope — optimistic about what to try, strict about what to fund.
12. **Extend the box's idioms.** `gads-env.sh` as single source of IDs, `product_facts` for truth, the MOE reviewer gate, observe → gate → heal → verify → log, append-only ledgers, `--agent` JSON CLIs; no parallel conventions.

---

## 1. System Overview

### 1.1 What it is

`adsys` is a Python package plus one cron-driven dispatcher on the Hetzner box. It reads Google Ads (API v22 through `google-ads-pp-cli`), GA4, Shopify, the first-party tracker, GSC, Klaviyo and Merchant Center into SQLite; reconciles them into one refund-discounted contribution ledger in SEK; runs a deterministic policy engine over Bayesian beliefs; executes bounded mutations through a single executor that validates, applies, reads back and records an inverse; and reports to Maestro on Telegram. LLMs sit at the edges: classifying search terms and keywords into the taxonomy, generating Swedish ad copy and landing-page drafts behind a claims whitelist and the existing 3-reviewer MOE gate, diagnosing incidents and narrating the digest.

### 1.2 How it decides — the loop

| Stage | Type | What happens |
|---|---|---|
| sense | D | Ingest every source at the declared grain; write a coverage record per (source, table, day). |
| validate | D | Freshness, completeness, auth and reconciliation checks; label every datum `MEASURED`/`MEASURED_ZERO`/`NO_DATA`/`BROKEN`; open incidents. A `BROKEN` input drops the dependent decision classes to no-action for that cycle. |
| interpret | D + L | D: update beliefs (Beta/Gamma posteriors with hierarchical shrinkage), compute contribution, detect anomalies. L: classify new search terms/keywords, tag stage/intent/pain, explain anomalies. |
| decide | D | Policy tables (§8) produce `ACT` / `NO_ACTION` / `ESCALATE` per candidate; every candidate is written to `decisions`, including the ones not acted on (counterfactual lane). |
| act | D (+H at 5 gates) | Executor: HALT check → capguard check → trust-stage check → precondition re-check → idempotency check → `--validate-only` → apply → record inverse. |
| verify | D | Read back the mutated entity; mismatch → auto-rollback + incident. Policy approval of new ads checked at +24h and +72h. |
| learn | D + L | At each decision's horizon, compare predicted vs realised; update calibration, beliefs, failure memory, trust ladder. L writes the human-readable lesson into MemPalace. |

```
                    ┌──────────────── OWNER (Telegram) ────────────────┐
                    │ digest ◄── narrator(L)      /ads halt|veto|cap ──┼──┐
                    └──────────────────────────────────────────────────┘  │
 SOURCES                                                                   ▼
 Ads(API v22) ─┐   ┌────────┐   ┌──────────┐   ┌───────────┐   ┌────────────────┐
 GA4 ──────────┤   │ SENSE  │   │ VALIDATE │   │ INTERPRET │   │ DECIDE (D)     │
 Shopify ──────┼──►│ ingest ├──►│ coverage ├──►│ beliefs   ├──►│ policy tables  │
 Tracker ──────┤   │ +cover │   │ recon    │   │ taxonomy  │   │ + counterfact. │
 GSC/KW-intel ─┤   └────────┘   │ auth     │   │ (L tags)  │   └───────┬────────┘
 Klaviyo/GMC ──┘                └────┬─────┘   └───────────┘           │ ACT cand.
                                     │ BROKEN ⇒ no-action              ▼
                         ┌───────────▼──────────┐   ┌─────────────────────────────┐
                         │ INCIDENTS / HEAL     │   │ EXECUTOR                    │
                         │ observe→gate→heal→   │   │ HALT? CAPGUARD? STAGE? PRE? │
                         │ verify→log           │   │ idem → validate → apply     │
                         └───────────▲──────────┘   └──────────────┬──────────────┘
                                     │ mismatch                    ▼
                         ┌───────────┴──────────┐   ┌─────────────────────────────┐
                         │ VERIFY (read-back)   ◄───┤ Google Ads account 8479789152│
                         └───────────┬──────────┘   └─────────────────────────────┘
                                     ▼
                         ┌──────────────────────┐    CAPGUARD (separate process,
                         │ LEARN: outcomes,     │    every 30 min, pause-only)
                         │ calibration, fail-   │    reads /root/.nordisk/guard/
                         │ memory, trust ladder │    ads_cap.json
                         └──────────────────────┘
```

### 1.3 What it will do on its own (once the stage is earned)

Add negatives (search-term and vocabulary-driven, with Swedish inflections); pause keywords, ads and ad groups; rotate creative; reallocate budget inside the cap; set CPC ceilings; switch campaigns off conversion-based bidding while conversion data is polluted; create keywords, RSAs, sitelinks/callouts, ad groups, Shopify *Pages* (not theme files) as landers, Search and Standard Shopping campaigns; kill its own launches on pre-committed rules; run switchback and sequential-swap experiments; write the lesson of every outcome.

### 1.4 What it will never do on its own

Raise the owner's spend ceiling (it ramps its own current cap inside that ceiling only when sales are profitable); change conversion goals, primary/secondary status, attribution settings or value rules; remove conversion actions or hard-delete anything; publish to the live Shopify theme `195492381006`; complete OAuth re-consent; apply Google recommendations through Google's auto-apply; bid on or mention competitor trademarks in ad text; write an outcome claim not present in `product_claims`; name a legacy paused campaign in any output.

### 1.5 Two facts the owner must hear up front

**Unit economics.** Historical non-brand CPC is 2.09 AUD (294.88 AUD / 141 clicks) ≈ 13.17 SEK at the planning rate. Break-even conversion rate is `CPC_sek / C_new_sek`. For a first-order contribution `C_new` of 400 SEK that is 3.3%; at 2% CVR, break-even needs `C_new` ≥ 658 SEK. Only Wellness Kit (2189 SEK) and Full Home Filtration (4283 SEK) plausibly clear that; the 990 SEK filter at typical e-commerce CVR does not. The system is therefore designed to (a) find cheaper clicks (long-tail, Shopping, CPC ceilings derived from contribution), (b) route non-brand traffic toward higher-AOV products and the Wellness Kit, and (c) say plainly if no profitable non-brand demand exists at this price level. `C_new` is computed in UNIT 1.5; the numbers here are illustrative until then.

**Growth target and time to get there.** The goal is **100 total store orders/month** (T1), then 100/week, then 100/day. Measured 2026-09-23 by the Builder (Shopify API, local DB and GA4, three reads agreeing; UNIT 1.10 re-runs and stores the queries): **27 orders in 90 days = 9/month** (best month 13; 111 lifetime), AOV ≈ 1,505 SEK, store revenue ≈ 72 AUD/day, ≈ 87 GA4 sessions/day, site conversion ≈ 0.34%, and 67% of organic clicks landing on one comparison article. T1 is therefore **an 11× increase**, not a tuning exercise. Ad spend follows revenue (governor, §3.5: at today's revenue it allows ≈ 25 AUD/day), so the first growth has to come from levers that don't need a big ad budget — conversion rate, the comparison traffic that already exists, and paid only where the maths works. §1.6 sets out that path; it is built by the Builder in Phase 1b, ahead of the autonomy ladder, and measured by adsys. The recorded 0.61 Ads conversions/30 d cannot yet be read either way. **100/day (T3) is out of reach for Google Ads alone within the ceiling;** it needs Meta and other channels outside this spec (N10).

### 1.6 The 10× path (scenario, not a forecast)

Orders = sessions × conversion rate. From 9/month:

| Lever | Today | T1 scenario | Why it is plausible / what proves it |
|---|---|---|---|
| Conversion rate (all traffic) | ≈ 0.34% | ≈ 1.2% | 0.34% is low; the comparison article gets most traffic but is an article, not a buying page. Big-swing changes on that path (product blocks in the comparison table, 100-day guarantee above the fold, bundle offer) — measured in UNIT 1.15 |
| Organic sessions | ≈ 2,600/month | ≈ 4,000/month | comparison intent already wins ("bäst i test" is the top query family); more comparison pages via the existing article pipeline |
| Paid clicks (comparison + product intent, Search + Shopping) | ≈ 0 non-brand | ≈ 3,500/month at ≈ 1.5% | only if break-even holds (below) |
| Orders | 9 | ≈ 48 organic + ≈ 52 paid ≈ 100 | |

**Paid break-even with real AOV:** 1,505 SEK AOV ≈ 1,204 SEK ex VAT; at an assumed 45–50% contribution before ads (UNIT 1.5 replaces this), `C_new` ≈ 540–600 SEK ≈ 86–95 AUD. Break-even CPA ≈ 90 AUD. At the historical 2.09 AUD CPC this needs ≥ 2.3% conversion on paid clicks; at site-average 0.34% one paid order costs ≈ 615 AUD. **So conversion rate is the lever that unlocks paid** — every point of conversion gained lowers the cost of every order from every channel.

**The governor is not a deadlock:** revenue for 100 orders ≈ 800 AUD/day, which permits ≈ 280 AUD/day of spend at r = 0.35 — enough for the scenario above. The path there is organic and conversion growth first (raising revenue, raising the governor), and `/ads invest` if Maestro chooses to front-load.

**What volume can prove:** at ≈ 2,600 sessions/month, a page test can only detect roughly a doubling of conversion within ~2 months; +20% effects need years. So Phase 1b makes a few large, obvious changes and measures before/after with stated uncertainty, rather than running fine-grained A/B tests.

### 1.7 Conventions

| Symbol | Meaning |
|---|---|
| `ROOT` | `/mnt/HC_Volume_105587324/nordisk` |
| `NDB` | `ROOT/db/nordisk.db` (absolute path only; the volume-root `nordisk.db` is a zero-byte decoy) |
| `ADB` | `ads_decisions.db` — location resolved by UNIT 0.1 (`find / -xdev -name ads_decisions.db` excluding `/dev/sdb`), pinned in `ROOT/adsys/config/paths.toml` |
| `PDB` | `ROOT/db/pixel_track.db` |
| `KDB` | `ROOT/db/keyword-intel.db` |
| `FDB` | the DB holding `product_facts`, resolved from `nodes/nordisk_self.py`'s own loader |
| `TMP` | `/mnt/HC_Volume_105573741/adsys-tmp` (never `/`, never `/tmp` for browser profiles) |
| `ART` | `/mnt/HC_Volume_105573741/adsys-artifacts` (screenshots, LLM transcripts) |
| Dates | `date_syd` = Google Ads account day (Australia/Sydney); `date_sto` = canonical day (Europe/Stockholm) |
| FX | planning rates **1 AUD = 6.30 SEK, 1 USD = 9.60 SEK**; replaced daily by ECB reference cross rates (§3.1); every persisted monetary fact stores `fx_to_sek` and `fx_date` |
| `C_new` | expected refund-discounted contribution (SEK) of a first order, before ad spend (§3.2) |

---

## 2. Capability Register

### 2.1 Capabilities used (all from §3 of the brief)

| Capability | Brief ref | Used for (section) | Precondition |
|---|---|---|---|
| `google-ads-pp-cli` / `gads --agent … search` GAQL | 3.2 | all Ads ingestion (§5.1), read-back (§9) | `source gads-env.sh`; auth probe green |
| Mutate families: campaigns, ad-groups, ad-group-ads, ad-group-criteria, campaign-criteria, customer-negative-criteria, shared-sets/criteria, campaign-budgets, bidding-strategies, assets, campaign/ad-group-assets | 3.2 | Action layer (§9) | exact verb/flag syntax pinned by UNIT 0.1 |
| `customers-conversion-actions` | 3.2 | create UPLOAD_CLICKS action as *secondary* (UNIT 1.7); goal changes are gated | Gate G-CONV for primary changes |
| `customers-keyword-plans*` | 3.2 | volume/CPC forecasts (§5.8) | verify whether CLI also exposes `generateKeywordIdeas`/`generateKeywordHistoricalMetrics` (UNIT 0.1) |
| `customers-experiments`, `-experiment-arms` | 3.2 | ad-copy/lander experiments at Stage 2+ (§16.6) | — |
| `customers-recommendations` (read) | 3.2 | signal source only (§10.1) | auto-apply subscriptions must be absent (UNIT 0.13) |
| Flags `--agent --dry-run --validate-only --idempotent --partial-failure --deliver` | 3.2 | executor (§9.1) | — |
| `gads-auth.py check/refresh/url/finish` | 3.2 | auth probe + re-auth escalation (§15) | human for `url`/`finish` |
| CLI local cache `data.db` | 3.2 | not used for decisions (sync never run; freshness unprovable). May be hydrated later as a read accelerator. | — |
| `ga4-read.py report/tx/realtime` | 3.4 | GA4 ingestion (§5.2), synthetic probe read (§15.3) | service-account key |
| GA4 Measurement Protocol (`GA4_MP_API_SECRET`) | 3.4, 3.12 | tracker forwarding (existing) + synthetic `nr_synthetic_probe` event | — |
| GSC `traffic_daily` | 3.5 | demand, cannibalisation, lander candidates (§10, §11) | freshness ≤ 3 days |
| `shopify-pp-cli`, Admin REST token, `resync-orders.py` | 3.6 | orders, line items, refunds, Pages API landers (§5.3, §12.6) | token moved to secrets (UNIT 0.7); scopes verified |
| Klaviyo data in NDB + REST with `KLAVIYO_TOKEN` | 3.7 | lagged/assisted value (§6.7); flow/template writes (§12.13) | write needs N12 |
| `gmc-feed.py` (feed push) | 3.8 | feed title/attribute loop (§12.7) | — |
| Tracker `tracker.py`, `pixel_track.db`, web pixel + runbook | 3.12 | attribution spine (§6) | extended, never replaced |
| `nordisk-infra-doctor.py`, `tracking-doctor.py`, `google-ads-conv-doctor.py` | 3.11, 3.12 | self-healing checks absorbed into §15 as probes | — |
| `keyword-intel.py`, `KDB` | 3.13 | demand, autosuggest, gaps (§10, §11) | — |
| `research` CLI, Serper, Exa, Firecrawl, local Chromium/Playwright | 3.14 | SERP snapshots, competitor pages (§10.1) | Tavily key resolution verified in pipeline env |
| `nrshot.js`, `nrmobile.js`, `nrtext.js`, `nrperf`, `nrvision`, `nrverify` | 3.14 | lander checks and creative screenshot judgement (§11.6, §12.6) | `TMPDIR=TMP` |
| OpenRouter / Orcarouter / OpenAI / Google AI Studio keys | 3.14 | reasoning roles R1–R8 (§7) | daily LLM budget (§7.4) |
| MOE: `judge-reasoning.py`, `judge-reliability.py`, 3-reviewer gate, `swedish_polish` node | 3.14, 3.11 | copy and lander gate (§12) | imported, not copied |
| `nodes/nordisk_self.py` + `product_facts` | 3.14 | claims whitelist (§12.4) | extended with `product_claims` |
| `ads_decisions.db` `ad_audit_*` | 3.10 | seed of ledger; archetype weights as creative priors (§16.1) | kept intact |
| MemPalace (`mempalace-cli kg-add/diary-write/search`), GBrain | 3.10 | lesson write-back, session-start context for R3/R6 (§16.7) | live palace `/root/.mempalace/palace` only |
| Telegram gateway (Hermes) | 3.18 | digest + gates + commands (§19) | inbound routing, see N5 |
| `bin/weekly-email.py` | 3.18 | secondary digest channel after DKIM fixed | N6 |
| `theme_guard.py` (17 tests) | 4.8 | theme lander path (§12.6) | — |
| cron + Hermes `cronjob`, harness-opt comb, gated credential-heal actor | 3.1, 3.11 | orchestration (§17), watcher-of-watcher (§15.4) | — |

### 2.2 REQUIRES NEW ACCESS

| # | Item | Provider | Cost | Grant needed | Blocking? |
|---|---|---|---|---|---|
| N1 | ECB daily reference rates (`https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml`, 90-day history file for backfill) | ECB, public | 0 | outbound HTTPS from box (verify egress) | No — fallback to planning rates marked `FX_ASSUMED`, which blocks money-dependent *mutations* but not ingestion |
| N2 | Merchant API (Reports + product status) read access. Content API for Shopping was scheduled for shutdown in 2026; target Merchant API, fall back to Content API only if it still answers | Google | 0 | Add the existing GCP service account (`/root/.nordisk/keys/google-service-account.json`) as a user on the Merchant Center account; enable Merchant API in the GCP project | Blocks Shopping launch (Stage 3) only |
| N3 | Google Ads "customer data terms" acceptance for enhanced conversions / user identifiers on click uploads | Google Ads UI | 0 | Owner clicks accept in UI once | No — click upload works on gclid alone |
| N4 | External dead-man switch (healthchecks.io free tier: 20 checks) with Telegram integration | healthchecks.io | 0 | Owner creates account, gives OWL two ping URLs | No, but without it "the box is dead" is undetectable |
| N5 | Inbound Telegram command routing: Hermes gateway handler that forwards messages beginning `/ads` from Maestro's chat_id to `adsys owner-cmd`. If the gateway cannot route, a second bot token from BotFather used only by adsys | Telegram | 0 | Gateway config change, or new bot token in `/root/.secrets.env` as `ADSYS_TG_BOT_TOKEN` | Blocks veto/halt by message (halt file still works) |
| N6 | DKIM TXT record for `vektal.systems` | DNS provider | 0 | Whoever holds DNS for `vektal.systems` | No — Telegram is primary channel |
| N7 | Google Ads API Auction Insights metrics (allowlisted fields) | Google | 0 | Allowlist application via Google Ads API support; outcome uncertain | No — fallback: Serper SERP snapshots (lower fidelity) |
| N8 | Shopify Admin scopes `read_orders` (line items, refunds — likely present), `write_content` (Pages; likely present since articles publish), `read_checkouts` (abandoned checkouts) | Shopify custom app | 0 | Verify with `GET /admin/oauth/access_scopes.json`; add missing scopes in app settings (owner, 2 min) | `write_content` blocks lander creation (Stage 2) |
| N9 | Developer-token access level confirmation (Explorer vs Basic) | Google | 0 | Read from API Center; design fits Explorer's lower daily operation budget (§17.8) | No |

| N10 | Meta Marketing API (only if the 100/day target is pursued) | Meta | 0 API; ad spend separate | Meta Business account, system user token, pixel/CAPI on the tracker | No — outside Google scope; required for T3 in practice |
| N11 | Video generation for YouTube/Demand Gen (e.g. Veo through the Gemini API on the existing `GOOGLE_AI_STUDIO_API_KEY`, if the key's tier includes it) | Google | per-second video pricing; budget cap 50 USD/month | verify model access on the key; else owner-shot product footage | No — Search/Shopping/landers don't need it |
| N12 | Klaviyo private API key with `flows:write`, `templates:write`, `flows:read`, `metrics:read` (unless `KLAVIYO_TOKEN` already has them) + 5 reference flows built once in the UI | Klaviyo | 0 | owner creates key → `secrets set KLAVIYO_PRIVATE_API_KEY`; builds the reference flows | Blocks cascade step 6 only |
| N13 | Shopify scopes for offers: `write_discounts`, `write_products` (bundles), plus whatever the store's upsell app/extension exposes | Shopify | 0 (app cost if an upsell app is added) | verify/add scopes in the custom app | Blocks cascade step 5 only |

No other new capability is assumed. Temporal/Postgres, Composio, Browser Use Cloud and `pi-moa` are not used (§17.1).

---

## 3. Objective Function

### 3.1 Unit of account, FX, time

- **Canonical currency: SEK.** Revenue, refunds, COGS and contribution are SEK-native or converted to SEK at order date. Ad spend is recorded in AUD (native) and converted at the Sydney spend date.
- **FX source:** ECB publishes EUR-based rates; `AUD→SEK = EURSEK / EURAUD`, `USD→SEK = EURSEK / EURUSD`. Weekends/holidays use the last published rate. Table `fx_rates`. Each money column is accompanied by `fx_to_sek` and `fx_date`.
- **Planning rates** (used only in this document and when ECB is unreachable, flagged `FX_ASSUMED`): 1 AUD = 6.30 SEK; 1 USD = 9.60 SEK. If an `FX_ASSUMED` rate is older than 3 days, budget and bid mutations are blocked (they depend on converting SEK economics to AUD ceilings).
- **Canonical timezone: Europe/Stockholm.** Google Ads cannot change an account's timezone, and the offset to Sydney moves between 8 h (Northern summer) and 10 h (Northern winter) because the two hemispheres switch DST in opposite directions. Campaign-level cost/clicks are ingested **hourly** (`segments.hour`) and re-bucketed to `date_sto`; tables whose resource does not support `segments.hour` keep `date_syd` and carry `tz_basis='Australia/Sydney'`. All decision windows are ≥ 7 days, so a 8–10 h edge misalignment is ≤ 6% of a window; rules that compare single days (circuit breakers) use hourly data only.

### 3.2 Per-order contribution (code-ready)

```
gross_sek(o)        = o.total_price × fx(o.currency→SEK, o.created_date_sto)
vat_rate(o)         = config.vat[o.shipping_country]            # SE 0.25; others from config table, EU OSS rates
net_rev_sek(o)      = (Σ_li (li.price×li.qty − li.total_discount) + shipping_charged(o)) × fx / (1 + vat_rate(o))
cogs_sek(o)         = hypersku.cost_sek(o)                       # per-order, from cogs_final.py output
                      else Σ_li unit_cogs_sek(li.sku) × li.qty   # unit_cogs = median over hypersku orders of that SKU
                      else  MISSING → order excluded from CM, counted in `cm_coverage` metric
fees_sek(o)         = config.payment_fee_rate × gross_sek(o)     # default 0.029 (ASSUMPTION A3, §23)
contrib0_sek(o)     = net_rev_sek − cogs_sek − fees_sek
```

**Refund adjustment — chosen method: confidence-discounted revenue.** Rejected alternatives: *cohort holdback* (waiting 100 days before counting an order) makes every decision 100 days late at one order a month — the system could not learn at all; *lag-aware hazard objective* needs a refund-timing curve the store does not have data for (111 orders lifetime). The chosen method discounts each order by the refund probability remaining, which is exact in expectation under the stated hazard assumption and self-corrects as refunds settle.

```
p_refund            ~ Beta(1 + R, 19 + N − R)    # R refunds among N orders aged ≥ 100 d; prior mean 5%, strength 20 orders
hazard              uniform over days 0..100     # conservative: early refunds would make it optimistic
r_rem(o, t)         = E[p_refund] × max(0, 1 − age_days(o, t)/100)      if o not refunded
refund_loss(o)      = net_rev_sek(o)             # money returned; COGS sunk (used shower filter is not resaleable) — ASSUMPTION A4
E_contrib(o, t)     = contrib0_sek(o) − r_rem(o, t) × refund_loss(o)     if o not refunded
                    = −cogs_sek(o) − fees_sek(o) + (net_rev_sek(o) − refunded_net_sek(o))   if refunded (partial handled)
```

**LTV uplift** (new customers only; cartridge is the repeat product):

```
ρ                   ~ Beta(2 + K, 8 + M − K)     # K of M new customers first-ordered ≥365 d ago bought again within 365 d; prior 20%, strength 10
repeat_contrib_sek  = median contrib0 of repeat orders (fallback: cartridge 398 SEK net of VAT and its unit COGS)
ltv_uplift(o)       = is_new(o) × min(0.5 × contrib0_sek(o), E[ρ] × repeat_contrib_sek)
```
The cap at 0.5 × `contrib0` holds until M ≥ 30; the system must not buy customers on imagined repeat revenue.

**Value of an order to the objective:** `V(o, t) = E_contrib(o, t) + ltv_uplift(o)`.

**`C_new`** (used in break-even rules) = posterior mean of `V` over new-customer web orders in the last 180 days, shrunk toward the product mix of the ad group's target product with strength 10 orders. Recomputed daily; the value used by each decision is stored in the decision record.

### 3.3 Entity-level objective

```
Spend_sek(e, W)     = Σ_d cost_aud(e, d) × fx(AUD→SEK, d)
CM_sek(e, W)        = Σ_{o ∈ attributed(e), o.created ∈ W} V(o, now)
Net_sek(e, W)       = CM_sek − Spend_sek
CM_ROAS(e, W)       = CM_sek / Spend_sek                      # reported with 80% credible interval (§8.2)
```
`attributed(e)` is the internal last-paid-click model (§6.4). Windows are 28 days, evaluated only on **settled** days (§6.6).

### 3.4 Headline metrics (in digest order)

1. **Non-brand Net_sek, trailing 28 settled days** — the money-making number.
2. **Non-brand CM_ROAS** with 80% interval and the count of attributed orders behind it.
3. **Brand** Spend, CM and click-capture ratio from the switchback experiment (§16.6), never pooled into 1–2.
4. **Learning-budget consumed** (§3.6) and trust stage.

### 3.5 Caps (enforced by capguard, §18.2)

| Cap | Default | Reasoning |
|---|---|---|
| Spend governor (key `max_spend_to_revenue`) | **7-day ad spend ≤ r × 7-day total store revenue**, with `r = contribution_ratio − profit_target`. `contribution_ratio` = Σ contrib0 ÷ Σ gross revenue over the last 90 days (real COGS, VAT, fees, refunds — UNIT 1.5), recomputed monthly, moving at most ±0.05 per month. `profit_target` = share of revenue Maestro wants left after ads (owner knob, default 0.15). Bounds: 0.10 ≤ r ≤ 0.50. Until UNIT 1.5 has 90 days of data, r = 0.35. | Replaces a fixed 35%: the allowed spend now follows the store's actual margin. Example: contribution 50% of gross, profit target 15% → r = 0.35; 350 AUD/day then needs 1,000 AUD/day revenue, matching the owner's original rule. |
| Absolute ceiling (owner, key `ceiling_aud_per_day`) | **350 AUD/day** | Hard stop regardless of revenue; raising it is Gate `CAP`. |
| Launch mode (owner, optional) | `/ads invest <r> <days>` raises r temporarily (≤ 0.60, ≤ 60 days) for a market launch or a proven winner | Deliberate, time-boxed overspend is the owner's call, never the system's. |
| Current cap (system-set, key `current_aud_per_day`) | `max(learning_floor, min(ramp_value, governor_7d/7, ceiling))`; ramp starts at 15 AUD | Ramp (D21) moves only when paid is profitable; the governor moves with store revenue daily. |
| Learning floor | **15 AUD/day**, allowed above the governor only while the learning budget (§3.6) lasts | Enough to prove tracking and find the first profitable ad groups even while revenue is small. |
| Cap semantics | rolling 7-day spend ≤ 7 × current cap; any single Sydney day ≤ 1.5 × current cap; current ≤ ceiling always | Google may deliver up to 2 × a campaign's daily budget on one day; strict daily enforcement would require intraday pausing on 3-hour-lagged cost data. |
| Sum of campaign daily budgets | ≤ 1.0 × current cap | Keeps Google's own monthly limit (30.4 × daily budget) at or below 30.4 × cap. |
| Brand campaign budget | ≤ max(3.00 AUD/day, 10% of current cap) | 30d brand spend was 38.45 AUD ≈ 1.28 AUD/day; brand demand does not grow with spend. |
| Any one non-brand campaign | ≤ 40% of current cap | No single hypothesis may consume the account. |
| Incubating entity (launch envelope N) | ≤ max(3.00 AUD/day, 5% of current cap) for M = 21 days (M = 14 d once current cap ≥ 60 AUD/day: more clicks per day reach the same sample sooner), total ≤ 21 × N | 63 AUD ≈ 30 clicks at 2.09 AUD — the minimum for the leading-indicator floor (§8.4) to discriminate. ≈ 397 SEK ≈ one order's contribution at risk per test. |
| Concurrent incubations | ≤ 2 at current cap < 60 AUD; ≤ 6 at ≥ 60 AUD; exploration ≤ 40% of current cap | More budget → more parallel tests → faster discovery. |

**The old pipeline's plan of 350 SEK/day (= 55.6 AUD/day — not to be confused with the 350 AUD/day ceiling above) is neither the start nor the goal.** Spend now follows revenue: it may be 55 AUD/day when the store makes ≥ 157 AUD/day, and 350 AUD/day only at ≥ 1,000 AUD/day — and only if paid is also profitable at the margin (D21).

### 3.6 Risk appetite and pull-back

- **Learning budget:** 1,200 AUD of cumulative *unrecovered spend* (`Spend − CM`) on entities that have **not** yet proven profitable, over the first 90 days after Stage 1 begins. Spend on entities that earn their keep does not consume it. This is the price of finding the first profitable demand. Owner may change it (`/ads learnbudget <AUD>`); silence keeps the default.
- **Retrench trigger:** 75% of the learning budget consumed (900 AUD) with no entity having met the Stage-3 promotion floor → **Retrench mode**: non-brand spend limited to one harvest ad group at ≤ 3 AUD/day plus brand; no new incubations for 30 days; digest leads with "no profitable non-brand demand found at current price/CPC; options: …" and lists the evidence.
- **Hard pull-back (automatic, notify):** trailing-28d non-brand CM_ROAS posterior P(CM_ROAS < 0.3) ≥ 0.9 with ≥ 150 non-brand clicks → exploration share drops from 40% to 20% of cap until the next Stage review.
- **Self-kill (HALT):** §18.6.

### 3.7 Growth objective (total store orders, under the governor and a profit floor)

```
maximise   total_store_orders_28d                         # all channels: paid, organic, AI assistant, email, direct
subject to spend_7d ≤ 0.35 × store_revenue_7d            # governor (hard, capguard)
           spend_day ≤ ceiling
           marginal paid CM_ROAS of each ramp step ≥ growth_floor (default 1.0)
```
- **Targets (`growth.toml`):** T1 = 100 store orders/month; T2 = 100/week (≈ 433/month); T3 = 100/day (≈ 3,000/month). `target_scope = TOTAL` (owner decision). Paid-attributed orders, organic, AI-assistant and email shares are reported beside it.
- **MER** (store revenue ÷ ad spend) is the blended health number; the governor is MER ≥ 2.86 on gross revenue. Paid CM_ROAS remains the paid-specific truth (§3.3), so paid cannot silently live off organic margin.
- **Incrementality check:** because the target is total store orders, paid that merely steals organic clicks shows up as flat total orders with rising spend. Weekly, the system regresses total orders on paid spend over 8 weeks (plus E-01 brand holdout) and reports "orders added per 100 AUD"; a ramp step whose total-order lift posterior is ≤ 0 is reversed.
- **Gap diagnosis (weekly, first line of the digest):** `gap = target − total_orders_28d`, classified by the binding constraint:

| Bottleneck | Test | What the system does |
|---|---|---|
| MEASUREMENT | R1/R4 out of tolerance or E2E red | fixes tracking first; no ramp |
| EFFICIENCY | no paid entity with `P(CM_ROAS ≥ floor) ≥ 0.7` | more incubations from proven demand, Quality-Score/CTR attack (§12.9), Shopping, higher-AOV routing, conversion-rate fixes on landers |
| GOVERNOR | paid is profitable and budget-limited but spend = 0.35 × revenue | grow revenue on free surfaces (§10.5–10.7: organic, answer engines, free listings), raise AOV/conversion rate, email flows; spend follows revenue automatically |
| SPEND | profitable, budget-limited, below governor and ceiling | ramp current cap (D21) |
| CEILING | at 350 AUD/day ceiling with governor headroom | Gate `CAP` with evidence |
| DEMAND | profitable, not budget-limited, impression share ≥ 80%, queue exhausted | localized market entry / new channel packet (§14.7) |


---

## 4. Data Model

### 4.1 Placement and relation to existing stores

| Store | Role | Change |
|---|---|---|
| `NDB` (`nordisk.db`) | **Facts** — every harvested number | New `gads_*`, `ga4_*`, `shop_*`, `gmc_*`, `fx_rates`, `fact_coverage`, `order_attribution`, `order_economics`. Existing `ads_campaigns`, `orders`, `products`, `customers`, `traffic_daily`, `klaviyo_*`, `daily_metrics` untouched; `ads_campaigns` keeps being written (compatibility view, UNIT 0.5). |
| `ADB` (`ads_decisions.db`) | **Control plane** — entities, taxonomy, ledger, beliefs, hypotheses, experiments, failure memory, incidents, run ledger, gates | New tables below. `ad_audit_*` and `gsc_archetype_mapping` untouched and read as creative priors. |
| `PDB` (`pixel_track.db`) | **Attribution spine** | `purchases` gains click-id/consent columns (ALTER ADD only); new `probes`, `gads_click_uploads`, `gads_adjustments`. |
| `KDB` (`keyword-intel.db`) | **Demand** | New `kw_planner_metrics`, `serp_snapshots`. Existing `kw_ideas`, `gsc_query`, `gap_ideas`, `competitor_pages` read-only for adsys. |
| `FDB` (product_facts DB) | **Truth** | New `product_claims`, `banned_phrases` beside `product_facts`; accessed only through `nordisk_self` loader extension. |

Cross-DB reads use `ATTACH DATABASE … AS …` inside `adsys/db.py`; no cross-DB foreign keys (SQLite does not enforce them across files) — referential checks run in the nightly integrity test (§15.3, T-INT). All DBs: `PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=15000`.

### 4.2 Provenance block (present verbatim on every fact table, marked `-- PROV`)

```sql
  run_id             TEXT NOT NULL,                 -- run_ledger.run_id that wrote the row
  source             TEXT NOT NULL,                 -- 'gads_api_v22','ga4_data_api','shopify_admin','tracker','gmc_merchant_api','ecb','kw_planner','serper','gsc'
  harvested_at       TEXT NOT NULL,                 -- UTC ISO-8601
  attribution_window TEXT NOT NULL,                 -- e.g. 'ADS_DEFAULT_CLICKDATE','ADS_BY_CONV_DATE','GA4_DDA','NONE'
  currency           TEXT NOT NULL,                 -- 'AUD','SEK','USD','EUR','NONE'
  fx_to_sek          REAL,                          -- NULL iff currency IN ('SEK','NONE')
  fx_date            TEXT,                          -- date of the rate used
  mstate             TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN'))
```

### 4.3 Facts DDL (`NDB`, migration `ROOT/adsys/migrations/ndb_001_facts.sql`)

```sql
-- FX. Grain: (date, base, quote). Retention: forever.
CREATE TABLE fx_rates (
  date TEXT NOT NULL, base TEXT NOT NULL, quote TEXT NOT NULL, rate REAL NOT NULL CHECK (rate > 0),
  is_assumed INTEGER NOT NULL DEFAULT 0, source TEXT NOT NULL, harvested_at TEXT NOT NULL, run_id TEXT NOT NULL,
  PRIMARY KEY (date, base, quote));

-- Coverage: the table that makes MEASURED_ZERO earnable. Grain: (fact_table, scope, day, run_id). Retention: 800 days.
CREATE TABLE fact_coverage (
  fact_table TEXT NOT NULL,                 -- e.g. 'gads_keyword_daily'
  scope      TEXT NOT NULL,                 -- 'customer:8479789152' | 'property:454852488' | 'shop' | ...
  day        TEXT NOT NULL,                 -- day in the table's native tz basis
  tz_basis   TEXT NOT NULL,                 -- 'Australia/Sydney' | 'Europe/Stockholm' | 'UTC'
  run_id     TEXT NOT NULL,
  state      TEXT NOT NULL CHECK (state IN ('COMPLETE','PARTIAL','BROKEN')),
  settled    INTEGER NOT NULL DEFAULT 0,    -- 1 once day is older than the source's settling window (§6.6)
  api_rows   INTEGER, rows_written INTEGER,
  error_class TEXT, error_detail TEXT, harvested_at TEXT NOT NULL,
  PRIMARY KEY (fact_table, scope, day, run_id));
CREATE INDEX ix_cov_latest ON fact_coverage(fact_table, scope, day, harvested_at);
CREATE VIEW v_coverage_latest AS
  SELECT c.* FROM fact_coverage c
  WHERE c.harvested_at = (SELECT MAX(harvested_at) FROM fact_coverage x
                          WHERE x.fact_table=c.fact_table AND x.scope=c.scope AND x.day=c.day);

-- Entity snapshots from Ads (status, settings, QS, policy). Grain: (snap_date_sto, entity_type, entity_id). Retention: 400 days.
CREATE TABLE gads_entity_snapshot (
  snap_date TEXT NOT NULL, entity_type TEXT NOT NULL CHECK (entity_type IN
    ('CUSTOMER','CAMPAIGN','BUDGET','AD_GROUP','AD','KEYWORD','CAMPAIGN_NEG','ADGROUP_NEG','SHARED_SET','SHARED_CRIT',
     'CUSTOMER_NEG','CONV_ACTION','ASSET','CAMPAIGN_ASSET','ADGROUP_ASSET','BIDDING_STRATEGY','GEO_CRIT','LANG_CRIT','RECOMMENDATION')),
  entity_id TEXT NOT NULL, parent_id TEXT, campaign_id TEXT, name TEXT, status TEXT,
  primary_status TEXT, primary_status_reasons TEXT,           -- JSON array
  attrs_json TEXT NOT NULL,                                   -- full GAQL row for the entity
  attrs_hash TEXT NOT NULL,                                   -- sha256(attrs_json) for change detection
  -- PROV
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (snap_date, entity_type, entity_id));
CREATE INDEX ix_snap_campaign ON gads_entity_snapshot(campaign_id, entity_type, snap_date);

-- Campaign hourly (for tz re-bucketing and circuit breakers). Grain: (date_syd, hour_syd, campaign_id). Retention: 400 days.
CREATE TABLE gads_campaign_hourly (
  date_syd TEXT NOT NULL, hour_syd INTEGER NOT NULL CHECK (hour_syd BETWEEN 0 AND 23),
  ts_utc TEXT NOT NULL, date_sto TEXT NOT NULL, hour_sto INTEGER NOT NULL,
  campaign_id TEXT NOT NULL, impressions INTEGER NOT NULL, clicks INTEGER NOT NULL, cost_micros INTEGER NOT NULL,
  conversions REAL NOT NULL, conversions_value REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, hour_syd, campaign_id));
CREATE INDEX ix_ch_sto ON gads_campaign_hourly(date_sto, campaign_id);

-- Campaign daily incl. impression share. Grain: (date_syd, campaign_id). Retention: 800 days.
CREATE TABLE gads_campaign_daily (
  date_syd TEXT NOT NULL, campaign_id TEXT NOT NULL,
  impressions INTEGER NOT NULL, clicks INTEGER NOT NULL, cost_micros INTEGER NOT NULL,
  conversions REAL NOT NULL, conversions_value REAL NOT NULL, all_conversions REAL NOT NULL,
  conv_by_conv_date REAL, conv_value_by_conv_date REAL,
  search_is REAL, search_budget_lost_is REAL, search_rank_lost_is REAL, search_abs_top_is REAL,  -- NULL = not reported (<10 impressions etc.)
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, campaign_id));

-- Ad group daily. Grain: (date_syd, ad_group_id). Retention: 800 days.
CREATE TABLE gads_adgroup_daily (
  date_syd TEXT NOT NULL, ad_group_id TEXT NOT NULL, campaign_id TEXT NOT NULL,
  impressions INTEGER NOT NULL, clicks INTEGER NOT NULL, cost_micros INTEGER NOT NULL,
  conversions REAL NOT NULL, conversions_value REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, ad_group_id));
CREATE INDEX ix_agd_c ON gads_adgroup_daily(campaign_id, date_syd);

-- Ad daily. Grain: (date_syd, ad_id). Retention: 800 days.
CREATE TABLE gads_ad_daily (
  date_syd TEXT NOT NULL, ad_id TEXT NOT NULL, ad_group_id TEXT NOT NULL, campaign_id TEXT NOT NULL,
  impressions INTEGER NOT NULL, clicks INTEGER NOT NULL, cost_micros INTEGER NOT NULL,
  conversions REAL NOT NULL, conversions_value REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, ad_id));
CREATE INDEX ix_add_ag ON gads_ad_daily(ad_group_id, date_syd);

-- Keyword daily. Grain: (date_syd, ad_group_id, criterion_id). Retention: 800 days.
CREATE TABLE gads_keyword_daily (
  date_syd TEXT NOT NULL, ad_group_id TEXT NOT NULL, criterion_id TEXT NOT NULL, campaign_id TEXT NOT NULL,
  impressions INTEGER NOT NULL, clicks INTEGER NOT NULL, cost_micros INTEGER NOT NULL,
  conversions REAL NOT NULL, conversions_value REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, ad_group_id, criterion_id));

-- Search terms. Grain: (date_syd, ad_group_id, search_term, matched_criterion_id, st_match_type). Retention: 1095 days (highest-value asset).
CREATE TABLE gads_search_term_daily (
  date_syd TEXT NOT NULL, campaign_id TEXT NOT NULL, ad_group_id TEXT NOT NULL,
  search_term TEXT NOT NULL, search_term_norm TEXT NOT NULL,    -- lowercased, NFC, whitespace-collapsed
  matched_criterion_id TEXT NOT NULL DEFAULT '', matched_keyword_text TEXT, matched_keyword_match_type TEXT,
  st_match_type TEXT NOT NULL DEFAULT '',                         -- segments.search_term_match_type
  st_status TEXT,                                                 -- ADDED / EXCLUDED / NONE ...
  impressions INTEGER NOT NULL, clicks INTEGER NOT NULL, cost_micros INTEGER NOT NULL,
  conversions REAL NOT NULL, conversions_value REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, ad_group_id, search_term, matched_criterion_id, st_match_type));
CREATE INDEX ix_st_norm ON gads_search_term_daily(search_term_norm);
CREATE INDEX ix_st_camp ON gads_search_term_daily(campaign_id, date_syd);

-- Geo (user location). Grain: (date_syd, campaign_id, geo_target_id, location_type). Retention: 800 days.
CREATE TABLE gads_geo_daily (
  date_syd TEXT NOT NULL, campaign_id TEXT NOT NULL, geo_target_id TEXT NOT NULL,   -- region/city criterion id
  geo_level TEXT NOT NULL CHECK (geo_level IN ('COUNTRY','REGION','CITY')),
  location_type TEXT NOT NULL,                                                      -- AREA_OF_INTEREST / LOCATION_OF_PRESENCE
  country_criterion_id TEXT,
  impressions INTEGER NOT NULL, clicks INTEGER NOT NULL, cost_micros INTEGER NOT NULL, conversions REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, campaign_id, geo_target_id, geo_level, location_type));

-- Device. Grain: (date_syd, campaign_id, device). Retention: 800 days.
CREATE TABLE gads_device_daily (
  date_syd TEXT NOT NULL, campaign_id TEXT NOT NULL, device TEXT NOT NULL,
  impressions INTEGER NOT NULL, clicks INTEGER NOT NULL, cost_micros INTEGER NOT NULL, conversions REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, campaign_id, device));

-- Conversions by action (hygiene + lag). Grain: (date_syd, campaign_id, conversion_action_id). Retention: 800 days.
CREATE TABLE gads_conv_action_daily (
  date_syd TEXT NOT NULL, campaign_id TEXT NOT NULL, conversion_action_id TEXT NOT NULL,
  conversions REAL NOT NULL, conversions_value REAL NOT NULL, all_conversions REAL NOT NULL,
  conv_by_conv_date REAL, conv_value_by_conv_date REAL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_syd, campaign_id, conversion_action_id));

-- Asset performance (RSA headlines/descriptions, sitelinks). Grain: (snap_date, ad_id, asset_id, field_type). Retention: 400 days.
CREATE TABLE gads_ad_asset_snapshot (
  snap_date TEXT NOT NULL, ad_id TEXT NOT NULL, asset_id TEXT NOT NULL, field_type TEXT NOT NULL,
  pinned_field TEXT, performance_label TEXT, asset_text TEXT,
  impressions_28d INTEGER, clicks_28d INTEGER,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (snap_date, ad_id, asset_id, field_type));

-- Click view (gclid → entity), used when a tracker purchase carries gclid but no nr_* params. Grain: gclid. Retention: 400 days.
CREATE TABLE gads_click_view (
  gclid TEXT PRIMARY KEY, date_syd TEXT NOT NULL, campaign_id TEXT, ad_group_id TEXT, criterion_id TEXT,
  keyword_text TEXT, keyword_match_type TEXT, device TEXT, geo_region_id TEXT,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')));

-- Change history (human edits detection). Grain: change event. Retention: 800 days.
CREATE TABLE gads_change_event (
  change_ts TEXT NOT NULL, resource_name TEXT NOT NULL, resource_type TEXT NOT NULL, client_type TEXT NOT NULL,
  operation TEXT NOT NULL, changed_fields TEXT, old_json TEXT, new_json TEXT, user_hash TEXT,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (change_ts, resource_name, operation));

-- GA4. Grain noted per table. Currency = GA4 response metadata.currencyCode (NOT assumed). Retention: 800 days.
CREATE TABLE ga4_daily_channel (
  date_sto TEXT NOT NULL, channel_group TEXT NOT NULL,
  sessions INTEGER NOT NULL, engaged_sessions INTEGER NOT NULL, add_to_carts INTEGER NOT NULL,
  checkouts INTEGER NOT NULL, transactions INTEGER NOT NULL, purchase_revenue REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_sto, channel_group));
CREATE TABLE ga4_daily_campaign (
  date_sto TEXT NOT NULL, session_campaign TEXT NOT NULL, session_source_medium TEXT NOT NULL,
  manual_ad_content TEXT NOT NULL DEFAULT '', manual_term TEXT NOT NULL DEFAULT '',   -- utm_content / utm_term
  sessions INTEGER NOT NULL, engaged_sessions INTEGER NOT NULL, add_to_carts INTEGER NOT NULL,
  checkouts INTEGER NOT NULL, transactions INTEGER NOT NULL, purchase_revenue REAL NOT NULL, advertiser_ad_cost REAL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_sto, session_campaign, session_source_medium, manual_ad_content, manual_term));
CREATE TABLE ga4_daily_landing (
  date_sto TEXT NOT NULL, landing_page TEXT NOT NULL, session_source_medium TEXT NOT NULL,
  sessions INTEGER NOT NULL, engaged_sessions INTEGER NOT NULL, add_to_carts INTEGER NOT NULL,
  transactions INTEGER NOT NULL, purchase_revenue REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_sto, landing_page, session_source_medium));
CREATE TABLE ga4_daily_item (
  date_sto TEXT NOT NULL, item_id TEXT NOT NULL, item_name TEXT NOT NULL,
  items_viewed INTEGER, items_added INTEGER, items_purchased INTEGER NOT NULL, item_revenue REAL NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date_sto, item_id));
CREATE TABLE ga4_transactions (
  transaction_id TEXT PRIMARY KEY, date_sto TEXT NOT NULL, revenue REAL NOT NULL,
  session_source_medium TEXT, session_campaign TEXT, first_user_source_medium TEXT,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')));

-- Shopify. Grain: line item. Retention: forever.
CREATE TABLE shop_line_items (
  line_item_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, product_id TEXT, variant_id TEXT, sku TEXT,
  handle TEXT, title TEXT, quantity INTEGER NOT NULL, price REAL NOT NULL, total_discount REAL NOT NULL DEFAULT 0,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')));
CREATE INDEX ix_li_order ON shop_line_items(order_id);
CREATE INDEX ix_li_handle ON shop_line_items(handle);
CREATE TABLE shop_order_ext (                         -- fields missing from existing `orders`
  order_id TEXT PRIMARY KEY, order_name TEXT, created_at_utc TEXT NOT NULL, created_date_sto TEXT NOT NULL,
  customer_id TEXT, email_sha256 TEXT, shipping_country TEXT, shipping_region TEXT,
  subtotal REAL, shipping_charged REAL, total_tax REAL, total_price REAL NOT NULL,
  presentment_currency TEXT, discount_codes TEXT, landing_site_full TEXT, referring_site TEXT,
  source_name TEXT, financial_status TEXT, cancelled_at TEXT, test INTEGER NOT NULL DEFAULT 0,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')));
CREATE TABLE shop_refunds (
  refund_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, created_at_utc TEXT NOT NULL,
  amount REAL NOT NULL, line_items_json TEXT, reason TEXT,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')));
CREATE INDEX ix_ref_order ON shop_refunds(order_id);
CREATE TABLE shop_inventory_snapshot (
  snap_date TEXT NOT NULL, variant_id TEXT NOT NULL, handle TEXT, available INTEGER,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (snap_date, variant_id));

-- Merchant Center. Retention: 400 days.
CREATE TABLE gmc_product_status (
  snap_date TEXT NOT NULL, offer_id TEXT NOT NULL, country TEXT NOT NULL, destination TEXT NOT NULL,
  status TEXT NOT NULL, issues_json TEXT,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (snap_date, offer_id, country, destination));
CREATE TABLE gmc_perf_daily (
  date TEXT NOT NULL, offer_id TEXT NOT NULL, program TEXT NOT NULL,     -- FREE_LISTINGS / SHOPPING_ADS
  impressions INTEGER NOT NULL, clicks INTEGER NOT NULL,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (date, offer_id, program));

-- Derived: order ↔ click join (§6.4). Grain: order. Retention: forever.
CREATE TABLE order_attribution (
  order_id TEXT PRIMARY KEY, tracker_tx_id TEXT, match_method TEXT NOT NULL CHECK (match_method IN
    ('TRACKER_ORDER_ID','TRACKER_ORDER_NAME','WEBHOOK_ONLY','LANDING_SITE','NONE')),
  click_id_type TEXT CHECK (click_id_type IN ('GCLID','GBRAID','WBRAID') OR click_id_type IS NULL),
  click_id TEXT, click_ts_utc TEXT, days_click_to_order REAL,
  lt_source TEXT, lt_medium TEXT, lt_campaign TEXT, lt_term TEXT, lt_content TEXT,
  ft_source TEXT, ft_medium TEXT, ft_campaign TEXT, ft_ts_utc TEXT,
  nr_c TEXT, nr_ag TEXT, nr_ad TEXT, nr_kw TEXT,                -- resolved Ads ids (params or click_view)
  entity_resolution TEXT CHECK (entity_resolution IN ('PARAMS','CLICK_VIEW','UTM_NAME','UNRESOLVED')),
  channel_last TEXT NOT NULL, channel_first TEXT,              -- PAID_SEARCH_BRAND / PAID_SEARCH_NONBRAND / PAID_SHOPPING / ORGANIC / EMAIL / DIRECT / REFERRAL / AI_ASSISTANT / UNKNOWN_CONSENT / UNKNOWN
  is_new_customer INTEGER NOT NULL, consent_marketing INTEGER, consent_analytics INTEGER,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')));
CREATE INDEX ix_oa_ag ON order_attribution(nr_ag);
CREATE INDEX ix_oa_c ON order_attribution(nr_c);

-- Derived: order economics (§3.2). Grain: (order_id, computed_date). Retention: forever. Latest row per order via view.
CREATE TABLE order_economics (
  order_id TEXT NOT NULL, computed_date TEXT NOT NULL, formula_version TEXT NOT NULL,
  gross_sek REAL NOT NULL, net_rev_sek REAL NOT NULL, vat_rate REAL NOT NULL,
  cogs_sek REAL, cogs_method TEXT CHECK (cogs_method IN ('HYPERSKU_ORDER','SKU_MEDIAN','MISSING')),
  fees_sek REAL NOT NULL, contrib0_sek REAL, refunded_net_sek REAL NOT NULL DEFAULT 0,
  age_days REAL NOT NULL, p_refund_mean REAL NOT NULL, r_rem REAL NOT NULL,
  e_contrib_sek REAL, ltv_uplift_sek REAL, value_sek REAL,     -- V(o,t)
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (order_id, computed_date));
CREATE VIEW v_order_value AS SELECT * FROM order_economics e
  WHERE computed_date = (SELECT MAX(computed_date) FROM order_economics x WHERE x.order_id = e.order_id);

-- Proven demand (§10.0). Grain: (window_end, page_path). Retention: 800 days.
CREATE TABLE page_value (
  window_end TEXT NOT NULL, page_path TEXT NOT NULL, lang TEXT,
  sessions_org INTEGER, sessions_all INTEGER, orders_org INTEGER NOT NULL, orders_all INTEGER NOT NULL,
  order_sources_json TEXT NOT NULL,              -- counts by evidence: TRACKER_FT, TRACKER_LT, SHOPIFY_LANDING_SITE, GA4_LANDING
  value_sek REAL NOT NULL, cvr_org_post_mean REAL, cvr_org_ci80_json TEXT, product_mix_json TEXT,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (window_end, page_path));
-- Grain: (window_end, query_norm, page_path). Retention: 800 days.
CREATE TABLE query_value (
  window_end TEXT NOT NULL, query_norm TEXT NOT NULL, page_path TEXT NOT NULL,
  gsc_clicks_90d INTEGER NOT NULL, gsc_impr_90d INTEGER NOT NULL, avg_position REAL,
  est_orders_90d REAL NOT NULL, est_value_sek_90d REAL NOT NULL,
  paid_orders_90d INTEGER NOT NULL DEFAULT 0,    -- direct evidence: tracker-attributed orders via Ads search term = this query
  tier TEXT NOT NULL CHECK (tier IN ('PROVEN','PROMISING','DEMAND_ONLY')),
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (window_end, query_norm, page_path));
CREATE INDEX ix_qv_tier ON query_value(window_end, tier, est_value_sek_90d);

-- Compatibility: legacy consumers of ads_campaigns keep working (UNIT 0.5 writes both).
```

### 4.4 The three-state guarantee (how conflation is made impossible)

- Fact rows are written only by ingest jobs, each of which writes a `fact_coverage` row for every (table, scope, day) it attempted, **including failed attempts** (`state='BROKEN'`).
- `adsys/metrics.py::get(metric, entity, window)` is the **only** read path for fact tables. It returns `Measure(value, state, coverage_run_ids)` where `state` is computed:
  - any day in window with latest coverage `BROKEN` or missing → `BROKEN` (value `None`);
  - all days `COMPLETE`, entity eligible (snapshot status `ENABLED` and primary_status not in {`REMOVED`,`PAUSED`,`NOT_ELIGIBLE`}) on ≥ 1 day, no rows → `MEASURED_ZERO`, value 0;
  - all days `COMPLETE`, entity not eligible on any day → `NO_DATA` (value `None`);
  - otherwise `MEASURED` with the sum.
- `PARTIAL` coverage yields `BROKEN` for decisions and "≥ value (partial)" in reports.
- **Lint test** `adsys/tests/no_raw_fact_reads_tests.py`: AST-scans every `.py` under `adsys/` and every `.sql`/`.sh` under `ROOT/bin`, `ROOT/google-ads/pipeline` that adsys invokes; any `SELECT … FROM gads_|ga4_|shop_|gmc_|order_` outside `adsys/metrics.py` and `adsys/ingest/` fails the suite.
- The digest renderer (`adsys/digest.py`) accepts only `Measure` objects; a `BROKEN` measure renders as `?` with the incident id. A raw float passed to the renderer raises `TypeError` (test `digest_types_tests.py`).

### 4.5 Control plane DDL (`ADB`, migration `ROOT/adsys/migrations/adb_001_control.sql`)

```sql
-- ===== Entities (one row per Google Ads entity adsys knows about; synced from snapshots) =====
CREATE TABLE ent_campaign (
  campaign_id TEXT PRIMARY KEY, name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('BRAND','NONBRAND','CONQUEST','SHOPPING','PMAX','DEMAND_GEN','VIDEO','HARVEST')),
  channel_type TEXT NOT NULL, language TEXT NOT NULL CHECK (language IN ('sv','en','fr')), market TEXT NOT NULL,
  created_by TEXT NOT NULL CHECK (created_by IN ('ADSYS','HUMAN','LEGACY')),
  lifecycle TEXT NOT NULL CHECK (lifecycle IN ('STAGED','INCUBATING','ACTIVE','SCALING','PAUSED_BY_SYSTEM','KILLED','LEGACY_PAUSED','REMOVED')),
  reportable INTEGER NOT NULL,          -- 0 for LEGACY_PAUSED/REMOVED forever; 0 for PAUSED_BY_SYSTEM/KILLED 14 d after pause (§18.1 C-4.7)
  human_lock_until TEXT,                -- set when change_event shows a UI edit (§8.3 R-HUMAN)
  bidding_policy TEXT, blueprint_ref TEXT, incubation_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE ent_ad_group (
  ad_group_id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL, name TEXT NOT NULL, theme_id TEXT,
  intent TEXT, awareness TEXT, journey TEXT, pain_point TEXT, product_handle TEXT, lander_id TEXT,
  created_by TEXT NOT NULL CHECK (created_by IN ('ADSYS','HUMAN','LEGACY')),
  lifecycle TEXT NOT NULL, reportable INTEGER NOT NULL, human_lock_until TEXT, incubation_id TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE ent_keyword (
  criterion_id TEXT NOT NULL, ad_group_id TEXT NOT NULL, text TEXT NOT NULL, text_norm TEXT NOT NULL,
  match_type TEXT NOT NULL CHECK (match_type IN ('EXACT','PHRASE','BROAD')), lang TEXT,
  intent TEXT, awareness TEXT, journey TEXT, pain_point TEXT,
  tag_source TEXT CHECK (tag_source IN ('RULE','LLM','HUMAN')), tag_conf REAL,
  created_by TEXT NOT NULL, lifecycle TEXT NOT NULL, human_lock_until TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY (ad_group_id, criterion_id));
CREATE INDEX ix_kw_norm ON ent_keyword(text_norm);
CREATE TABLE ent_negative (
  neg_id TEXT PRIMARY KEY,                -- sha1(scope_type|scope_id|text_norm|match_type)
  scope_type TEXT NOT NULL CHECK (scope_type IN ('ACCOUNT','SHARED_SET','CAMPAIGN','AD_GROUP')),
  scope_id TEXT NOT NULL, text TEXT NOT NULL, text_norm TEXT NOT NULL,
  match_type TEXT NOT NULL CHECK (match_type IN ('EXACT','PHRASE','BROAD')),
  category TEXT NOT NULL,                 -- neg_vocab.category or 'PERFORMANCE'
  origin TEXT NOT NULL CHECK (origin IN ('SEED_NEGATIVES_MD','VOCAB','ST_RELEVANCE','ST_PERFORMANCE','HUMAN','LEGACY')),
  gads_resource_name TEXT, status TEXT NOT NULL CHECK (status IN ('PLANNED','LIVE','REMOVED')),
  added_action_id TEXT, created_at TEXT NOT NULL);
CREATE INDEX ix_neg_scope ON ent_negative(scope_type, scope_id, status);
CREATE TABLE neg_vocab (                   -- managed vocabulary; replaces ads-monitor.sh hardcoded list
  term_norm TEXT NOT NULL, lang TEXT NOT NULL, category TEXT NOT NULL CHECK (category IN
    ('PRICE_SHOPPER','DIY','NON_BUYER_INTENT','WRONG_CATEGORY','PROFESSIONAL','WRONG_MECHANISM','COMPETITOR_BRAND',
     'OTHER_LANGUAGE','SPAM','JOBS_EDU','GEO_WRONG','REVIEW_ONLY')),
  match_type TEXT NOT NULL, inflections_json TEXT NOT NULL,   -- Swedish forms, see §11.4
  auto_apply INTEGER NOT NULL,            -- 0 for REVIEW_ONLY and stage-dependent categories
  stage_exempt_json TEXT,                 -- e.g. ["PROBLEM_AWARE"] for 'vad är'
  default_scope TEXT NOT NULL CHECK (default_scope IN ('ACCOUNT_LIST','CAMPAIGN')),
  origin TEXT NOT NULL, added_at TEXT NOT NULL, PRIMARY KEY (term_norm, lang, category));

CREATE TABLE ent_lander (
  lander_id TEXT PRIMARY KEY,             -- sha1(path)
  url_path TEXT NOT NULL UNIQUE, lang TEXT NOT NULL CHECK (lang IN ('sv','en','fr')),
  lander_class TEXT NOT NULL CHECK (lander_class IN ('PRODUCT','COMPARISON','PROBLEM','GUIDE','GEMPAGES','HOME','ARTICLE','COLLECTION')),
  awareness TEXT, journey TEXT, pain_points_json TEXT, icp_segment TEXT, product_handle TEXT,
  owning_article_id TEXT, theme_section TEXT, host_type TEXT NOT NULL CHECK (host_type IN ('SHOPIFY_PAGE','SHOPIFY_PRODUCT','SHOPIFY_ARTICLE','THEME','GEMPAGES')),
  descriptive_path INTEGER NOT NULL,      -- 0 for code-like paths such as /pages/se-4
  preferred_alias_id TEXT,                -- descriptive equivalent if this one is code-like
  created_by TEXT NOT NULL, status TEXT NOT NULL CHECK (status IN ('CANDIDATE','VERIFIED','DEGRADED','BROKEN','RETIRED')),
  last_http_status INTEGER, last_checked_at TEXT, last_200_at TEXT, redirect_to TEXT,
  html_lang TEXT, canonical_ok INTEGER, price_ok INTEGER, claims_ok INTEGER,
  perf_mobile INTEGER, lcp_ms INTEGER, relevance_json TEXT, updated_at TEXT NOT NULL);
CREATE TABLE lander_checks (                -- append-only history
  lander_id TEXT NOT NULL, checked_at TEXT NOT NULL, host TEXT NOT NULL, http_status INTEGER,
  location_header TEXT, html_lang TEXT, canonical_href TEXT, price_found_sek REAL, perf_mobile INTEGER, lcp_ms INTEGER,
  screenshot_path TEXT, verdict TEXT NOT NULL, run_id TEXT NOT NULL, PRIMARY KEY (lander_id, checked_at));

CREATE TABLE ent_creative (
  creative_id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK (kind IN ('RSA','SITELINK','CALLOUT','SNIPPET','IMAGE','PAGE')),
  ad_group_id TEXT, campaign_id TEXT, gads_resource_name TEXT, content_json TEXT NOT NULL,
  claim_ids_json TEXT NOT NULL, angle TEXT, generator_run TEXT, moe_verdict_json TEXT,
  lifecycle TEXT NOT NULL CHECK (lifecycle IN ('DRAFT','REJECTED','STAGED','LIVE','PAUSED','RETIRED')),
  policy_status TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);

-- ===== Taxonomy (§13) =====
CREATE TABLE tax_pain (pain_id TEXT PRIMARY KEY, label_sv TEXT NOT NULL, label_en TEXT NOT NULL,
  lexicon_sv_json TEXT NOT NULL, allowed_framing TEXT NOT NULL CHECK (allowed_framing IN ('PROBLEM_ONLY','PROBLEM_AND_CLAIM')),
  icp_ref TEXT NOT NULL);
CREATE TABLE tax_icp_segment (segment_id TEXT PRIMARY KEY, description TEXT NOT NULL, pains_json TEXT NOT NULL,
  voc_phrases_json TEXT NOT NULL, icp_ref TEXT NOT NULL);           -- voc = verbatim language from nordisk-icp.md, landers/ads only
CREATE TABLE content_assets (asset_id TEXT PRIMARY KEY, url_path TEXT NOT NULL, kind TEXT NOT NULL,
  lang TEXT NOT NULL, awareness TEXT, journey TEXT, pain_points_json TEXT, product_handle TEXT,
  tagged_by TEXT NOT NULL, tag_conf REAL, tagged_at TEXT NOT NULL);

-- ===== Ledger (append-only; enforced by triggers) =====
CREATE TABLE decisions (
  decision_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, cycle_ts TEXT NOT NULL,
  decision_class TEXT NOT NULL, rule_id TEXT NOT NULL, rule_version TEXT NOT NULL,
  entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
  stage_at_decision INTEGER NOT NULL, mode TEXT NOT NULL CHECK (mode IN ('SHADOW','LIVE')),
  outcome TEXT NOT NULL CHECK (outcome IN ('ACT','NO_ACTION','ESCALATE','BLOCKED')),
  blocked_reason TEXT,                     -- STAGE / CAP / HALT / DATA_BROKEN / VELOCITY / HUMAN_LOCK / GATE
  counterfactual INTEGER NOT NULL,         -- 1 if not executed (shadow, no_action, blocked)
  inputs_json TEXT NOT NULL, evidence_json TEXT NOT NULL, posterior_json TEXT,
  confidence REAL, predicted_json TEXT, horizon_days INTEGER, revisit_trigger TEXT,
  rationale TEXT NOT NULL, llm_call_ids_json TEXT, fx_to_sek REAL, c_new_sek REAL);
CREATE INDEX ix_dec_entity ON decisions(entity_type, entity_id, cycle_ts);
CREATE TABLE actions (
  action_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, idem_key TEXT NOT NULL UNIQUE,
  action_type TEXT NOT NULL, target_ref TEXT NOT NULL, payload_json TEXT NOT NULL,
  before_json TEXT, inverse_json TEXT NOT NULL, rollback_of TEXT, created_at TEXT NOT NULL);
CREATE TABLE action_events (              -- status transitions of actions
  action_id TEXT NOT NULL, ts TEXT NOT NULL, status TEXT NOT NULL CHECK (status IN
    ('PLANNED','VALIDATED','APPLIED','VERIFIED','FAILED','ROLLED_BACK','VETOED','BLOCKED_BY_CAP','BLOCKED_BY_HALT','BLOCKED_BY_STAGE')),
  detail_json TEXT, PRIMARY KEY (action_id, ts, status));
CREATE VIEW v_action_status AS SELECT a.*, (SELECT status FROM action_events e WHERE e.action_id=a.action_id
  ORDER BY ts DESC LIMIT 1) AS status FROM actions a;
CREATE TABLE outcomes (
  decision_id TEXT NOT NULL, evaluated_at TEXT NOT NULL, horizon_days INTEGER NOT NULL,
  predicted_json TEXT, realized_json TEXT NOT NULL, abs_error_json TEXT,
  verdict TEXT NOT NULL CHECK (verdict IN ('CONFIRMED','REFUTED','INCONCLUSIVE','UNMEASURABLE')),
  PRIMARY KEY (decision_id, evaluated_at));
CREATE TRIGGER t_dec_noupd BEFORE UPDATE ON decisions BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER t_dec_nodel BEFORE DELETE ON decisions BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER t_act_noupd BEFORE UPDATE ON actions BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER t_act_nodel BEFORE DELETE ON actions BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER t_ae_noupd BEFORE UPDATE ON action_events BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER t_ae_nodel BEFORE DELETE ON action_events BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER t_out_noupd BEFORE UPDATE ON outcomes BEGIN SELECT RAISE(ABORT,'append-only'); END;

-- ===== Beliefs =====
CREATE TABLE beliefs (
  belief_id TEXT PRIMARY KEY,              -- metric|scope_type|scope_id
  metric TEXT NOT NULL CHECK (metric IN ('CTR','CVR','ATC_RATE','ENGAGED_RATE','RELEVANT_SHARE','REFUND_RATE','REPEAT_RATE')),
  scope_type TEXT NOT NULL CHECK (scope_type IN ('ACCOUNT','ROLE','CAMPAIGN','AD_GROUP','KEYWORD','SEARCH_TERM','LANDER','CREATIVE','STAGE')),
  scope_id TEXT NOT NULL, parent_belief_id TEXT, k REAL NOT NULL,
  prior_a REAL NOT NULL, prior_b REAL NOT NULL, succ REAL NOT NULL, trials REAL NOT NULL,
  post_a REAL NOT NULL, post_b REAL NOT NULL, post_mean REAL NOT NULL, ci80_lo REAL NOT NULL, ci80_hi REAL NOT NULL,
  window_days INTEGER NOT NULL, as_of TEXT NOT NULL, evidence_state TEXT NOT NULL, evidence_hash TEXT NOT NULL);
CREATE TABLE belief_history (belief_id TEXT NOT NULL, as_of TEXT NOT NULL, post_a REAL, post_b REAL,
  post_mean REAL, trials REAL, PRIMARY KEY (belief_id, as_of));
CREATE TABLE value_beliefs (               -- Gamma/Normal beliefs on SEK quantities
  vb_id TEXT PRIMARY KEY, quantity TEXT NOT NULL CHECK (quantity IN ('C_NEW','CPC_SEK','REPEAT_CONTRIB')),
  scope_type TEXT NOT NULL, scope_id TEXT NOT NULL, n INTEGER NOT NULL, mean_sek REAL NOT NULL,
  sd_sek REAL, shrink_k REAL NOT NULL, as_of TEXT NOT NULL);

-- ===== Hypotheses, incubations, experiments, failure memory =====
CREATE TABLE hypotheses (
  hyp_id TEXT PRIMARY KEY, created_decision_id TEXT NOT NULL, statement TEXT NOT NULL,
  entity_type TEXT NOT NULL, entity_id TEXT, metric TEXT NOT NULL, predicted_value REAL, predicted_ci80_json TEXT,
  confidence REAL NOT NULL, floor_json TEXT NOT NULL, deadline TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('OPEN','CONFIRMED','REFUTED','INCONCLUSIVE','ABANDONED')),
  closed_at TEXT, verdict_evidence_json TEXT);
CREATE TABLE incubations (
  incubation_id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, hyp_id TEXT NOT NULL,
  envelope_aud_day REAL NOT NULL, envelope_aud_total REAL NOT NULL, start_date TEXT NOT NULL, deadline TEXT NOT NULL,
  extended INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL CHECK (status IN ('RUNNING','GRADUATED','KILLED','EXTENDED','VETOED')),
  verdict TEXT CHECK (verdict IN ('PASS','NO_DEMAND','TARGETING_LEAK','LANDER_MISMATCH','FUNNEL_DEAD','INCONCLUSIVE') OR verdict IS NULL),
  closed_at TEXT);
CREATE TABLE experiments (
  exp_id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK (kind IN ('SWITCHBACK','SEQUENTIAL_SWAP','GADS_EXPERIMENT','GEO_SPLIT','HOLDOUT')),
  question TEXT NOT NULL, design_json TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('PLANNED','RUNNING','ABORTED','COMPLETE')), abort_rule TEXT NOT NULL,
  result_json TEXT, honest_power_note TEXT NOT NULL);
CREATE TABLE fail_memory (
  fingerprint TEXT PRIMARY KEY,            -- sha1 of canonical tuple, §16.4
  tuple_json TEXT NOT NULL, kind TEXT NOT NULL, description TEXT NOT NULL,
  verdict TEXT NOT NULL CHECK (verdict IN ('LOSER','NO_DEMAND','INCONCLUSIVE','MEASURED_BADLY','POLICY','TARGETING_LEAK','LANDER_MISMATCH','FUNNEL_DEAD')),
  evidence_json TEXT NOT NULL, spend_sek REAL, created_at TEXT NOT NULL,
  retry_after TEXT, retry_conditions_json TEXT NOT NULL, source_hyp_id TEXT, source TEXT NOT NULL CHECK (source IN ('ADSYS','LEGACY_MINED','HUMAN')));

-- ===== Operations =====
CREATE TABLE run_ledger (
  run_id TEXT PRIMARY KEY, job TEXT NOT NULL, window_key TEXT NOT NULL,   -- e.g. '2026-09-23' or '2026-W39'
  started_at TEXT NOT NULL, ended_at TEXT,
  status TEXT NOT NULL CHECK (status IN ('RUNNING','OK','DEGRADED','STALE','BROKEN','SKIPPED_DEP','HALTED','TIMEOUT')),
  exit_code INTEGER, rows_in INTEGER, rows_out INTEGER, input_freshness_json TEXT,
  error_class TEXT, error_detail TEXT, git_rev TEXT, pid INTEGER, host TEXT);
CREATE INDEX ix_run_job ON run_ledger(job, window_key, started_at);
CREATE TABLE incidents (
  incident_id TEXT PRIMARY KEY, opened_at TEXT NOT NULL, severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 4),
  class TEXT NOT NULL, fingerprint TEXT NOT NULL, summary TEXT NOT NULL, detail_json TEXT,
  state TEXT NOT NULL CHECK (state IN ('OPEN','MITIGATED','RESOLVED')), auto_action TEXT,
  demoted_stage INTEGER, notified_at TEXT, resolved_at TEXT, resolution TEXT);
CREATE UNIQUE INDEX ux_inc_open ON incidents(fingerprint) WHERE state <> 'RESOLVED';
CREATE TABLE trust_state (
  ts TEXT PRIMARY KEY, stage INTEGER NOT NULL CHECK (stage BETWEEN 0 AND 4), prior_stage INTEGER,
  reason TEXT NOT NULL, evidence_json TEXT NOT NULL, changed_by TEXT NOT NULL CHECK (changed_by IN ('SYSTEM','OWNER')),
  restore_to INTEGER, restore_condition TEXT);   -- for externally-caused demotions (§18.4)
CREATE TABLE gate_requests (
  gate_id TEXT PRIMARY KEY, gate_class TEXT NOT NULL CHECK (gate_class IN ('CAP','CONV_GOALS','IRREVERSIBLE','OAUTH','THEME_PUBLISH')),
  created_at TEXT NOT NULL, payload_json TEXT NOT NULL, tg_message_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('PENDING','APPROVED','DENIED','EXPIRED','SUPERSEDED')),
  expires_at TEXT NOT NULL, decided_at TEXT, decided_by TEXT);
CREATE TABLE owner_commands (
  cmd_id TEXT PRIMARY KEY, received_at TEXT NOT NULL, chat_id TEXT NOT NULL, raw_text TEXT NOT NULL,
  parsed_json TEXT, status TEXT NOT NULL CHECK (status IN ('ACCEPTED','REJECTED','EXECUTED','FAILED')), result TEXT);
CREATE TABLE llm_calls (
  call_id TEXT PRIMARY KEY, role TEXT NOT NULL, model TEXT NOT NULL, prompt_version TEXT NOT NULL, prompt_hash TEXT NOT NULL,
  input_tokens INTEGER, output_tokens INTEGER, cost_usd REAL, latency_ms INTEGER,
  status TEXT NOT NULL CHECK (status IN ('OK','SCHEMA_FAIL','TIMEOUT','ERROR','BUDGET_DENIED')),
  schema_ok INTEGER NOT NULL, created_at TEXT NOT NULL, transcript_path TEXT);
CREATE INDEX ix_llm_day ON llm_calls(created_at);
CREATE TABLE growth_state (             -- weekly; one row per evaluation
  week TEXT PRIMARY KEY, target_orders_month INTEGER NOT NULL, paid_orders_28d INTEGER, total_orders_28d INTEGER, store_revenue_7d_aud REAL, spend_7d_aud REAL, mer_7d REAL, governor_aud_day REAL, orders_per_100aud_json TEXT,
  bottleneck TEXT NOT NULL CHECK (bottleneck IN ('MEASUREMENT','EFFICIENCY','GOVERNOR','SPEND','CEILING','DEMAND')),
  current_cap_aud REAL NOT NULL, ceiling_aud REAL NOT NULL, ramp_action TEXT, evidence_json TEXT NOT NULL,
  demand_ceiling_orders_month_json TEXT);   -- per market estimate (§14.7)
CREATE TABLE creative_reviews (          -- feedback loop (§12.8); append-only
  review_id TEXT PRIMARY KEY, creative_id TEXT NOT NULL, surface TEXT NOT NULL, reviewed_at TEXT NOT NULL,
  window_days INTEGER NOT NULL, metrics_json TEXT NOT NULL, baseline_json TEXT NOT NULL,
  bucket TEXT NOT NULL CHECK (bucket IN ('WINNER','HIGH_POTENTIAL','LOSER','INSUFFICIENT')),
  diagnosis TEXT, diagnosis_evidence_json TEXT, visual_review_json TEXT, next_step TEXT NOT NULL CHECK (next_step IN ('ITERATE','SCALE','GRAVEYARD','WAIT')),
  iteration_of TEXT, iteration_brief_json TEXT);
CREATE TABLE creative_attributes (       -- tags that make pooling possible
  creative_id TEXT NOT NULL, attr TEXT NOT NULL CHECK (attr IN ('ANGLE','HOOK_TYPE','PAIN','PROOF_TYPE','OFFER','CTA','FORMAT','LANDER_CLASS','PRODUCT','MARKET','LENGTH_BAND')),
  value TEXT NOT NULL, PRIMARY KEY (creative_id, attr));
CREATE TABLE creative_patterns (         -- pattern library: pooled posteriors per attribute value
  attr TEXT NOT NULL, value TEXT NOT NULL, surface TEXT NOT NULL, market TEXT NOT NULL, as_of TEXT NOT NULL,
  n_creatives INTEGER NOT NULL, impressions INTEGER, ctr_post_mean REAL, ctr_ci80_json TEXT,
  engaged_post_mean REAL, atc_post_mean REAL, win_rate REAL, PRIMARY KEY (attr, value, surface, market, as_of));
CREATE TABLE aeo_checks (                -- answer-engine citations (§10.6)
  check_id TEXT PRIMARY KEY, asked_at TEXT NOT NULL, engine TEXT NOT NULL, model TEXT NOT NULL, market TEXT NOT NULL,
  question TEXT NOT NULL, question_type TEXT NOT NULL, cited_domains_json TEXT NOT NULL, own_cited INTEGER NOT NULL,
  own_rank INTEGER, competitors_cited_json TEXT, answer_path TEXT);
CREATE TABLE conquest_scoreboard (       -- per query per week (§10.7)
  week TEXT NOT NULL, market TEXT NOT NULL, query_norm TEXT NOT NULL, tier TEXT,
  paid_is REAL, paid_abs_top_is REAL, organic_pos REAL, shopping_present INTEGER, free_listing_present INTEGER,
  ai_cited INTEGER, competitor_ads INTEGER, surfaces_owned INTEGER NOT NULL, PRIMARY KEY (week, market, query_norm));
CREATE TABLE lessons (                   -- §16.10
  lesson_id TEXT PRIMARY KEY, source_path TEXT NOT NULL, source_ref TEXT NOT NULL,   -- file + line range, or table + row ids
  kind TEXT NOT NULL CHECK (kind IN ('PRIOR','RULE','FAIL','HYPOTHESIS','CREATIVE_SEED','FACT')),
  statement TEXT NOT NULL, evidence_state TEXT NOT NULL CHECK (evidence_state IN ('MEASURED','MEASURED_BADLY','OPINION')),
  applied_to TEXT, status TEXT NOT NULL CHECK (status IN ('ACTIVE','VETOED','SUPERSEDED')), created_at TEXT NOT NULL);
CREATE TABLE themes (                    -- §12.11
  theme_id TEXT PRIMARY KEY, label TEXT NOT NULL, element_type TEXT NOT NULL, market TEXT NOT NULL,
  evidence_tier INTEGER NOT NULL CHECK (evidence_tier BETWEEN 1 AND 4), ev_score REAL NOT NULL, source_lesson_ids_json TEXT,
  slot_type TEXT NOT NULL CHECK (slot_type IN ('FREE_TRAFFIC','PAID_SLOT','QUEUED')),
  champion_variant_id TEXT, status TEXT NOT NULL CHECK (status IN ('TESTING','CONFIRMED','EXHAUSTED')),
  rounds_without_new_champion INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE variants (
  variant_id TEXT PRIMARY KEY,             -- e.g. X.5.2
  theme_id TEXT NOT NULL, parent_variant_id TEXT, changed_element TEXT NOT NULL, surface TEXT NOT NULL,
  creative_id TEXT, round_no INTEGER NOT NULL, decision_metric TEXT NOT NULL,
  result_json TEXT, p_beats_champion REAL, outcome TEXT CHECK (outcome IN ('CHAMPION','LOST','INSUFFICIENT') OR outcome IS NULL));
CREATE TABLE cascade_tickets (
  ticket_id TEXT PRIMARY KEY, theme_id TEXT NOT NULL, step INTEGER NOT NULL CHECK (step BETWEEN 1 AND 8),
  surface TEXT NOT NULL, mode TEXT NOT NULL CHECK (mode IN ('AUTONOMOUS','OWNER_PACKET')),
  status TEXT NOT NULL CHECK (status IN ('OPEN','TESTING','WON','LOST','VETOED','APPLIED')),
  apply_after TEXT, control_ref TEXT, result_json TEXT, created_at TEXT NOT NULL);
CREATE TABLE capguard_log (
  ts TEXT PRIMARY KEY, cap_aud REAL NOT NULL, cap_file_sha256 TEXT NOT NULL,
  spend_today_syd_aud REAL, spend_7d_aud REAL, budget_sum_aud REAL, state TEXT NOT NULL CHECK (state IN ('OK','WARN','TRIP','BROKEN')),
  action TEXT);
```

Retention: ledger, beliefs history, fail memory, gates, trust state — forever (append-only; growth estimate §17.8). `llm_calls` rows forever; transcripts in `ART/llm/` 90 days.

### 4.6 Extensions to existing stores

```sql
-- PDB (ALTER ADD only; tracker keeps working if columns are NULL)
ALTER TABLE purchases ADD COLUMN shopify_order_id TEXT;
ALTER TABLE purchases ADD COLUMN click_id_type TEXT;
ALTER TABLE purchases ADD COLUMN click_id TEXT;
ALTER TABLE purchases ADD COLUMN click_ts TEXT;
ALTER TABLE purchases ADD COLUMN lt_json TEXT;         -- last-touch {utm_*, nr_*, landing_path, ts}
ALTER TABLE purchases ADD COLUMN ft_json TEXT;         -- first-touch, same shape
ALTER TABLE purchases ADD COLUMN ga_client_id TEXT;    -- from _ga cookie, format <rand>.<ts>
ALTER TABLE purchases ADD COLUMN ga_session_id TEXT;   -- from _ga_YJP5QDGTHD cookie
ALTER TABLE purchases ADD COLUMN consent_json TEXT;    -- Shopify customerPrivacy flags at checkout
ALTER TABLE purchases ADD COLUMN pixel_version TEXT;
ALTER TABLE purchases ADD COLUMN synthetic INTEGER NOT NULL DEFAULT 0;
CREATE TABLE probes (probe_id TEXT PRIMARY KEY, received_at TEXT NOT NULL, kind TEXT NOT NULL,
  token TEXT NOT NULL, page_url TEXT, pixel_version TEXT, raw TEXT);
CREATE TABLE gads_click_uploads (order_id TEXT NOT NULL, conversion_action_id TEXT NOT NULL,
  click_id_type TEXT NOT NULL, click_id TEXT NOT NULL, conversion_ts TEXT NOT NULL, value_sek REAL NOT NULL,
  validate_only INTEGER NOT NULL, uploaded_at TEXT NOT NULL, http_status INTEGER, partial_failure_json TEXT,
  status TEXT NOT NULL CHECK (status IN ('OK','PARTIAL_FAIL','FAIL','SKIPPED_CONSENT','SKIPPED_TOO_OLD')),
  PRIMARY KEY (order_id, conversion_action_id, validate_only));
CREATE TABLE gads_adjustments (order_id TEXT NOT NULL, adjustment_type TEXT NOT NULL CHECK (adjustment_type IN ('RETRACTION','RESTATEMENT')),
  adjusted_value_sek REAL, adjusted_at TEXT NOT NULL, status TEXT NOT NULL, response_json TEXT,
  PRIMARY KEY (order_id, adjustment_type, adjusted_at));

-- KDB
CREATE TABLE kw_planner_metrics (keyword_norm TEXT NOT NULL, geo TEXT NOT NULL, lang TEXT NOT NULL, month TEXT NOT NULL,
  avg_monthly_searches INTEGER, competition_index INTEGER, low_top_bid_micros INTEGER, high_top_bid_micros INTEGER,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (keyword_norm, geo, lang, month));
CREATE TABLE serp_snapshots (query_norm TEXT NOT NULL, taken_at TEXT NOT NULL, gl TEXT NOT NULL, hl TEXT NOT NULL,
  ads_json TEXT, organic_top10_json TEXT, own_organic_pos INTEGER, competitor_ads_count INTEGER, raw_path TEXT,
  run_id TEXT NOT NULL, source TEXT NOT NULL, harvested_at TEXT NOT NULL, attribution_window TEXT NOT NULL,
  currency TEXT NOT NULL, fx_to_sek REAL, fx_date TEXT,
  mstate TEXT NOT NULL CHECK (mstate IN ('MEASURED','MEASURED_ZERO','NO_DATA','BROKEN')),
  PRIMARY KEY (query_norm, taken_at));

-- FDB (beside product_facts)
CREATE TABLE product_claims (claim_id TEXT PRIMARY KEY, product_handle TEXT, lang TEXT NOT NULL,
  claim_type TEXT NOT NULL CHECK (claim_type IN ('SPEC','GUARANTEE','PRICE','SHIPPING','BRAND','OUTCOME_ALLOWED')),
  canonical_text TEXT NOT NULL, allowed_variants_json TEXT NOT NULL,   -- phrasings the generator may use
  source_ref TEXT NOT NULL,                                             -- spec sheet / live URL
  valid_from TEXT NOT NULL, valid_to TEXT);
CREATE TABLE banned_phrases (pattern TEXT PRIMARY KEY, lang TEXT NOT NULL, kind TEXT NOT NULL CHECK (kind IN
  ('BANNED_CLAIM','MEDICAL_OUTCOME','TRADEMARK','SUPERLATIVE_UNSOURCED','EDITORIAL')), reason TEXT NOT NULL);
```

---

## 5. Sensing & Ingestion Layer

All ingest jobs live in `ROOT/adsys/ingest/`, run through the dispatcher (§17), write one `run_ledger` row per run and one `fact_coverage` row per (table, scope, day) attempted. Common failure semantics:

| Failure | Classification | Behaviour |
|---|---|---|
| auth failure (401, `UNAUTHENTICATED`, `TOKEN_REFRESH_FAILED`) | `BROKEN/AUTH` | 1 retry after `source gads-env.sh` re-mint; then coverage `BROKEN`, incident class `AUTH_GADS` sev 1, trust stage → 0 (restorable, §18.4) |
| transient (429, 5xx, `RESOURCE_TEMPORARILY_EXHAUSTED`, timeout) | `BROKEN/TRANSIENT` | retry ×3 at 30 s, 120 s, 480 s; then `BROKEN`, incident sev 3; next scheduled run re-pulls |
| schema/query error (400 `INVALID_ARGUMENT`, unknown field) | `BROKEN/SCHEMA` | no retry; store full `error.details` JSON; incident sev 2 class `SCHEMA_DRIFT` |
| empty payload where the entity snapshot says ≥ 1 ENABLED serving entity and yesterday had impressions | not an error by itself | coverage `COMPLETE`; the accessor returns `MEASURED_ZERO`; the anomaly detector (§15, CB-IMPR) decides whether that is plausible |
| unparseable output / non-JSON from `--agent` | `BROKEN/PARSE` | no retry; raw output saved to `ART/raw/<run_id>.txt`; incident sev 2 |
| DB write failure (disk, lock > 15 s) | `BROKEN/STORAGE` | abort run; incident sev 1 if disk ≥ 90% |

### 5.1 Google Ads (API v22 via `gads --agent customers-google-ads search "$GADS_CUSTOMER_ID" --query …`)

All queries run through `adsys/gads.py::search(gaql, page_size=10000)` which sources `ROOT/bin/gads-env.sh` in a subshell (`bash -c 'source … && exec "$GADS_CLI" --agent …'`), never mints tokens itself, and returns rows + request id. Cost is `metrics.cost_micros` (AUD).

| # | Pull | GAQL (abridged — full text in `adsys/ingest/gaql/*.sql`) | Table | Tier / window |
|---|---|---|---|---|
| A1 | entity snapshot: customer | `SELECT customer.id, customer.currency_code, customer.time_zone, customer.auto_tagging_enabled, customer.status, customer.tracking_url_template, customer.final_url_suffix FROM customer` | `gads_entity_snapshot` | hot, daily |
| A2 | campaigns | `SELECT campaign.id, campaign.name, campaign.status, campaign.primary_status, campaign.primary_status_reasons, campaign.advertising_channel_type, campaign.bidding_strategy_type, campaign.campaign_budget, campaign.network_settings.target_search_network, campaign.network_settings.target_content_network, campaign.network_settings.target_partner_search_network, campaign.geo_target_type_setting.positive_geo_target_type, campaign.final_url_suffix, campaign.target_spend.cpc_bid_ceiling_micros FROM campaign WHERE campaign.status != 'REMOVED'` | snapshot | hot |
| A3 | budgets (**fix for §5.1 bug**: separate query, joined in Python on `campaign.campaign_budget` resource name) | `SELECT campaign_budget.resource_name, campaign_budget.id, campaign_budget.amount_micros, campaign_budget.delivery_method, campaign_budget.explicitly_shared, campaign_budget.status FROM campaign_budget` | snapshot | hot |
| A4 | ad groups, ads (incl. `ad_group_ad.policy_summary.approval_status`, `.policy_topic_entries`, `ad_group_ad.ad_strength`, `ad.final_urls`, RSA headlines/descriptions), keywords (incl. `ad_group_criterion.quality_info.quality_score`, `.creative_quality_score`, `.post_click_quality_score`, `.search_predicted_ctr`, `ad_group_criterion.system_serving_status`), campaign/ad-group negatives, shared sets + criteria, customer negatives, conversion actions (`conversion_action.primary_for_goal`, `.counting_type`, `.type`, `.status`, `.category`, `.include_in_conversions_metric`, `.origin`), geo and language criteria, recommendation subscriptions | one GAQL per resource, `WHERE … status != 'REMOVED'` | snapshot | hot (daily) |
| A5 | campaign hourly | `SELECT campaign.id, segments.date, segments.hour, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value FROM campaign WHERE segments.date BETWEEN '{d0}' AND '{d1}'` | `gads_campaign_hourly` | hot: D-3..D0 (today partial, flagged `PARTIAL`) every 30 min for capguard at campaign grain; settle at D+3 |
| A6 | campaign daily + IS | `SELECT campaign.id, segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value, metrics.all_conversions, metrics.conversions_by_conversion_date, metrics.conversions_value_by_conversion_date, metrics.search_impression_share, metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share, metrics.search_absolute_top_impression_share FROM campaign WHERE segments.date BETWEEN …` | `gads_campaign_daily` | hot D-3..D-1; warm D-14..D-4 every 3 days; cold D-30..D-15 weekly |
| A7 | ad group / ad / keyword daily | `FROM ad_group`, `FROM ad_group_ad`, `FROM keyword_view` with `segments.date` and the same metric set | `gads_adgroup_daily`, `gads_ad_daily`, `gads_keyword_daily` | as A6 |
| A8 | search terms | `SELECT campaign.id, ad_group.id, search_term_view.search_term, search_term_view.status, segments.search_term_match_type, segments.keyword.ad_group_criterion, segments.keyword.info.text, segments.keyword.info.match_type, segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value FROM search_term_view WHERE segments.date BETWEEN …` (Shopping/PMax later: `campaign_search_term_insight`) | `gads_search_term_daily` | hot D-3..D-1 |
| A9 | geo | `SELECT campaign.id, user_location_view.country_criterion_id, user_location_view.targeting_location, segments.geo_target_region, segments.date, metrics.* FROM user_location_view WHERE …`; second query `FROM geographic_view` for `location_type` split | `gads_geo_daily` | warm |
| A10 | device | `SELECT campaign.id, segments.device, segments.date, metrics.* FROM campaign WHERE …` | `gads_device_daily` | warm |
| A11 | conversions by action | `SELECT campaign.id, segments.conversion_action, segments.date, metrics.conversions, metrics.conversions_value, metrics.all_conversions, metrics.conversions_by_conversion_date, metrics.conversions_value_by_conversion_date FROM campaign WHERE …` | `gads_conv_action_daily` | hot D-14..D-1 daily (conversions settle late) |
| A12 | asset performance | `SELECT ad_group_ad.ad.id, asset.id, asset.text_asset.text, ad_group_ad_asset_view.field_type, ad_group_ad_asset_view.pinned_field, ad_group_ad_asset_view.performance_label, metrics.impressions, metrics.clicks FROM ad_group_ad_asset_view WHERE segments.date DURING LAST_30_DAYS` (if `performance_label` is absent in v22 for RSAs, store NULL → `NO_DATA`) | `gads_ad_asset_snapshot` | cold, weekly |
| A13 | click view | `SELECT click_view.gclid, click_view.ad_group_ad, click_view.keyword, click_view.keyword_info.text, click_view.keyword_info.match_type, campaign.id, ad_group.id, segments.device, segments.date FROM click_view WHERE segments.date = '{d}'` (single-day queries only; API retains ≈ 90 days) | `gads_click_view` | hot, D-1 and D-2; backfill 90 days once |
| A14 | change events | `SELECT change_event.change_date_time, change_event.change_resource_name, change_event.change_resource_type, change_event.client_type, change_event.resource_change_operation, change_event.changed_fields, change_event.old_resource, change_event.new_resource, change_event.user_email FROM change_event WHERE change_event.change_date_time >= '{t0}' ORDER BY change_event.change_date_time LIMIT 10000` (user_email stored only as sha256) | `gads_change_event` | hot, daily; window last 2 days |
| A15 | recommendations (read-only) | `SELECT recommendation.type, recommendation.campaign, recommendation.impact, recommendation.dismissed FROM recommendation` | snapshot (`RECOMMENDATION`) | cold |

**Completeness assertions (per run, each failure → coverage `PARTIAL` + incident sev 3):**
- `Σ ad_group cost(d) = campaign cost(d)` for Search campaigns within max(0.01 AUD, 1%).
- `Σ keyword clicks(d) ≤ ad_group clicks(d)`; `Σ search-term clicks(d) ≤ Σ keyword clicks(d)`; the ratio is stored as `st_click_coverage` (Google withholds low-volume terms; a ratio < 0.5 over 28 days is reported, not an incident).
- A1 `currency_code = 'AUD'` and `time_zone = 'Australia/Sydney'`; any other value → sev 1 `ACCOUNT_IDENTITY` (wrong customer ID is the historical failure).
- `customer.id` equals `GADS_CUSTOMER_ID` from `gads-env.sh`, and equals `8479789152`; mismatch → sev 1, run aborted before any write.

**Staleness rule:** a decision class needing Ads data refuses to run (status `STALE`) if the newest `COMPLETE` coverage for its tables is older than 2 days (hot) / 5 days (warm) / 10 days (cold).

**Legacy compatibility:** `adsys/ingest/legacy_ads_campaigns.py` writes the existing `ads_campaigns` LAST_30_DAYS rows from A6 so `refresh-ads-data.sh`/`ingest-ads.py` consumers keep working; `bin/harvesters/google-ads.sh` is rewritten to call `adsys ingest gads --tier hot` (removes Composio).

### 5.2 GA4 (`/root/.nordisk/scripts/ga4-read.py`, extended with `--json` that returns `{rows, metadata:{currencyCode,timeZone,dataLossFromOtherRow,samplingMetadatas}, rowCount}`)

| Pull | Call | Table | Cadence |
|---|---|---|---|
| channel daily | `report sessions,engagedSessions,addToCarts,checkouts,transactions,purchaseRevenue date,sessionDefaultChannelGroup 5 --json` | `ga4_daily_channel` | hot (D-5..D-1, settle at D+2) |
| campaign/utm daily | `report sessions,engagedSessions,addToCarts,checkouts,transactions,purchaseRevenue,advertiserAdCost date,sessionCampaignName,sessionSourceMedium,sessionManualAdContent,sessionManualTerm 5 --json` | `ga4_daily_campaign` | hot |
| landing daily | `report sessions,engagedSessions,addToCarts,transactions,purchaseRevenue date,landingPagePlusQueryString,sessionSourceMedium 5 --json` (query string stripped of `gclid`, `gbraid`, `wbraid` before storage) | `ga4_daily_landing` | hot |
| item daily | `report itemsViewed,itemsAddedToCart,itemsPurchased,itemRevenue date,itemId,itemName 5 --json` | `ga4_daily_item` | hot |
| transactions | `report purchaseRevenue transactionId,date,sessionSourceMedium,sessionCampaignName,firstUserSourceMedium 14 --json` | `ga4_transactions` | hot |
| realtime probe | `realtime nr_synthetic_probe` | none (probe result → `run_ledger`) | §15.3 |

Assertions: `metadata.currencyCode` recorded as the row `currency` (the brief's item revenue figures — Duschvattenfilter 473.07 — are too low to be SEK for a 990 SEK product, so the property currency must be read, never assumed); `dataLossFromOtherRow = true` → `PARTIAL`; sampling present → `PARTIAL`. Staleness: 3 days.

### 5.3 Shopify (Admin REST, token from secrets — UNIT 0.7 moves it out of the harvest script)

| Pull | Call | Table | Cadence |
|---|---|---|---|
| orders (+ line items, refunds, discount codes, shipping address country/province, landing_site) | `GET /admin/api/{ver}/orders.json?status=any&updated_at_min={t-3d}&limit=250` paginated via `Link` header | `shop_order_ext`, `shop_line_items`, `shop_refunds` | hot, daily; full backfill once |
| inventory | `GET /admin/api/{ver}/products.json?fields=id,handle,variants` → `variants[].inventory_quantity` | `shop_inventory_snapshot` | hot |
| pages (lander registry) | `GET /admin/api/{ver}/pages.json?fields=id,handle,title,published_at,template_suffix` | `ent_lander` (via lander job) | cold |

Assertions: every `orders.id` updated in window has ≥ 1 line item (else `PARTIAL`); `Σ li.price×qty − discounts + shipping + tax − order.total_price` within 1 SEK (else row-level `mstate='BROKEN'`, order excluded from CM, incident sev 3). Orders with `test=true` or `source_name` ∈ {`shopify_draft_order`} are kept but excluded from paid attribution (draft orders are manual; they are 35 of 111 orders and would otherwise dilute every rate). Staleness: 2 days.

### 5.4 First-party tracker (`PDB`, local)

Read directly (same box). Assertions every hour (§15): tracker `/track/purchase` returns 200 on `OPTIONS`/health; `purchases` and `order_webhooks` newest rows compared against Shopify (§6.8 R1). Staleness is not time-based (no orders ≠ broken); it is reconciliation-based.

### 5.5 GSC (existing `traffic_daily`)

adsys reads only; assertion `MAX(date) ≥ today_sto − 3`; else coverage `BROKEN` for GSC-dependent classes (opportunity scoring, cannibalisation) and incident sev 3 routed to the existing GSC harvester owner (harness comb).

### 5.6 Klaviyo (existing `klaviyo_*` in NDB)

Read-only; `klaviyo_flow_metrics` is empty, so flow-entry attribution uses email-hash joins (§6.7), not Klaviyo metrics. Staleness 3 days; stale → lagged-value term set to `NO_DATA`, never 0.

### 5.7 Merchant Center (N2; Stage 3 prerequisite)

| Pull | Call | Table | Cadence |
|---|---|---|---|
| product status/issues | Merchant API products list (`productStatus.destinationStatuses`, `itemLevelIssues`) | `gmc_product_status` | warm |
| performance | Merchant API Reports `search` over the product performance view: `offer_id, date, clicks, impressions` split by marketing method | `gmc_perf_daily` | warm |
| feed push (existing) | `gmc-feed.sh` unchanged | — | existing |

Until N2 is granted: `gmc_*` coverage is `BROKEN` with `error_class='NO_ACCESS'`, and Shopping launch preconditions fail closed.

### 5.8 Keyword planning & SERP

| Pull | Call | Table | Cadence |
|---|---|---|---|
| volume/CPC for ≤ 200 candidate keywords per week (from §10 queue) | preferred: `generateKeywordHistoricalMetrics` (geo `geoTargetConstants/2752` Sweden, language `languageConstants/1015` Swedish) if the CLI exposes it; else `customers-keyword-plans` forecast path | `KDB.kw_planner_metrics` | cold, weekly |
| SERP (ads present, organic top 10, own position) for top 50 candidate queries | Serper `POST /search {q, gl:'se', hl:'sv', num:10}` | `KDB.serp_snapshots` | cold, weekly |

Planner volumes for Swedish long-tail are often bucketed or null → stored as `NO_DATA`, not 0.

### 5.9 FX (N1)

Daily 16:30 Stockholm (after ECB publication): fetch, write `fx_rates` for EUR→{SEK,AUD,USD} and derived AUD→SEK, USD→SEK. Failure: carry last rate with `is_assumed=1`; after 3 days money-dependent mutations are blocked (§3.1).

### 5.10 Auth probe

Every 30 min: `python3 ROOT/bin/gads-auth.py check` then `SELECT customer.id FROM customer LIMIT 1`. Two consecutive failures → `AUTH_GADS` incident (§15). Result also written to `ROOT/adsys/state/auth_gads.json` `{state, checked_at, token_expiry}` so every job can refuse early without calling the API.

---

## 6. Attribution, Measurement Integrity & Reconciliation

### 6.1 Truth hierarchy

| Question | Authoritative | Diagnostics (never averaged in) |
|---|---|---|
| Did an order happen, for how much, refunded? | Shopify orders/line items/refunds (SEK) | tracker `purchases`, GA4 transactions, Ads conversions |
| Which click produced the order? | tracker `purchases.click_id` + `lt_json` (first-party, transaction-keyed), resolved to entities via `nr_*` params or `gads_click_view` | GA4 session attribution, Ads conversion attribution, Shopify `landing_site` |
| What did it cost? | Google Ads `cost_micros` (AUD), settled at D+3 | GA4 `advertiserAdCost` |
| Did the visitor engage / add to cart? | GA4 events (behavioural only) | — |
| Which search demand exists? | Ads search terms (paid), GSC (organic) | keyword planner, autosuggest |

When sources disagree beyond tolerance (§6.8) the authoritative number is still used for decisions **only if** its own coverage is `COMPLETE`; the disagreement opens an incident and the affected decision classes are listed in the digest as "running on authoritative source, diagnostic disagrees by X". If the authoritative source is `BROKEN`, dependent classes return `NO_ACTION(DATA_BROKEN)`.

### 6.2 Join keys

| Join | Key | Notes |
|---|---|---|
| Shopify order ↔ tracker purchase | `purchases.shopify_order_id` (new, from pixel `checkout.order.id`) = `orders.shopify_id`; fallback `purchases.transaction_id` = order name/number (whichever UNIT 0.10 proves the current pixel sends) | match rate target in R1 |
| Shopify order ↔ webhook | `order_webhooks.order_id` = `orders.shopify_id` | registration already green |
| tracker purchase ↔ Ads click | `click_id` (gclid/gbraid/wbraid) captured by the pixel from the landing URL, 90-day TTL in pixel storage | §6.3 |
| click ↔ Ads entities | `nr_c`/`nr_ag`/`nr_ad`/`nr_kw` ValueTrack params stored with the click; fallback `gads_click_view.gclid` (≤ 90 days) | gbraid/wbraid have no click_view → params only |
| tracker purchase ↔ GA4 | `transaction_id` sent in MP; `ga_client_id` + `ga_session_id` from cookies | fixes the paid→transaction join (§6.11) |
| order ↔ customer (new vs repeat) | `email_sha256` over all prior Shopify orders; `customers.orders_count` as diagnostic | |

### 6.3 Pixel v2: click capture (extend `bin/token-obtainer/webpixel-backup/custom_pixel.js`)

Behaviour (runs in Shopify's web-pixel sandbox; uses only `analytics.subscribe`, `browser.localStorage`, `browser.cookie`, `init.customerPrivacy`):

```js
// illustrative — full implementation in UNIT 1.3
const CLICK_KEYS = ['gclid','gbraid','wbraid'];
const TOUCH_KEYS = ['utm_source','utm_medium','utm_campaign','utm_term','utm_content','nr_c','nr_ag','nr_ad','nr_kw'];
analytics.subscribe('page_viewed', async (e) => {
  const p = new URLSearchParams(e.context.document.location.search);
  const priv = init.customerPrivacy || {};
  if (p.get('nr_probe')) await probe(p.get('nr_probe'), e);                // synthetic self-test hook (§6.10)
  if (!priv.marketingAllowed) return;                                         // no click-id storage without marketing consent
  const touch = {ts: e.timestamp, path: e.context.document.location.pathname};
  TOUCH_KEYS.forEach(k => p.get(k) && (touch[k] = p.get(k)));
  const cid = CLICK_KEYS.find(k => p.get(k));
  if (cid) touch.click = {type: cid.toUpperCase(), id: p.get(cid)};
  if (cid || touch.utm_source) {
    await browser.localStorage.setItem('nr_lt', JSON.stringify(touch));      // last touch
    if (!(await browser.localStorage.getItem('nr_ft'))) await browser.localStorage.setItem('nr_ft', JSON.stringify(touch));
  }
});
analytics.subscribe('checkout_completed', async (e) => {
  const priv = init.customerPrivacy || {};
  const body = { transaction_id: e.data.checkout.order?.id, /* existing fields kept */
    lt: JSON.parse(await browser.localStorage.getItem('nr_lt') || 'null'),
    ft: JSON.parse(await browser.localStorage.getItem('nr_ft') || 'null'),
    ga_client_id: priv.analyticsProcessingAllowed ? parseGa(await browser.cookie.get('_ga')) : null,
    ga_session_id: priv.analyticsProcessingAllowed ? parseGaSession(await browser.cookie.get('_ga_YJP5QDGTHD')) : null,
    consent: priv, pixel_version: '2.0.0' };
  // POST to https://nordisk.vektal.systems/track/purchase (existing endpoint)
});
```
Touch records older than 90 days are ignored at checkout. `tracker.py` stores the new fields into the §4.6 columns and forwards to GA4 MP **with** `client_id = ga_client_id` (fallback: existing id) and `session_id` inside event params, which is what lets GA4 stitch the purchase to the paid session.

### 6.4 Internal attribution model (the one decisions use)

- **Model:** last paid click within 30 days before the order, from the tracker's last-touch record; if the last touch is non-paid but the first touch within 30 days is paid, the order is *assisted* (counted in the stage-specific assisted value, §6.7, never in last-click CM).
- **Channel classification:** `PAID_SEARCH_BRAND` if resolved campaign role = BRAND; `PAID_SEARCH_NONBRAND` for NONBRAND/CONQUEST/HARVEST; `PAID_SHOPPING` for SHOPPING/PMAX; else from `utm_medium`/referrer as GA4 would; `UNKNOWN_CONSENT` when `consent.marketingAllowed=false` (reported as a share, never imputed).
- **Why not Google's data-driven attribution:** it requires volume this account will not have and returns fractional credit (the 0.61 conversions) that cannot be joined to an order.
- **Honest limits (stated in every weekly digest footer):** cross-device journeys and consent-declined sessions are invisible; the `UNKNOWN_CONSENT` share bounds the error.

### 6.5 Conversion-action hygiene fix

Current state (§3.3 of brief): four ENABLED primaries — GA4 purchase (6878142622), `add_payment_info` labelled as purchase (6882963286), `form_submit` (6882963292), `add_to_cart` (6882963745). Correction to the brief's framing: `MANY_PER_CLICK` is correct for purchases (Google recommends "Every" for e-commerce, with order-id dedupe); the double-count hazard is **four actions summed into one "conversions" column**, which any conversion-based bid strategy then optimises.

Target state, in two gate requests (class `CONV_GOALS`, blocking by §4.13):

| Step | Change | When | Why safe |
|---|---|---|---|
| G-CONV-1 | Set 6882963286, 6882963292, 6882963745 to secondary (`primary_for_goal=false`); rename 6882963286 to "GA4 add_payment_info (diagnostic)"; keep 6878142622 as sole primary | Phase 0 (UNIT 0.9) | Fully reversible; secondary actions still report under "All conv." for diagnostics |
| G-CONV-2 | Create `NR Purchase — server click upload` (type `UPLOAD_CLICKS`, category PURCHASE, counting MANY_PER_CLICK, click-through window 30 d) as **secondary** — creation of a secondary action is not a goal change and runs autonomously in UNIT 1.7 | Phase 1 | Secondary = no bidding effect |
| G-CONV-3 | After 14 days where R4 (§6.8) is within tolerance: make the upload action primary and 6878142622 secondary | end of Phase 1 | Server upload is independent of GA4 consent/cookie loss and keyed by order id |

Silence on a `CONV_GOALS` gate means *no change* (it is a true blocking gate). The system does not need these gates to be approved to function: while polluted primaries remain, adsys does not use conversion-based bidding (§8, D10 switches such campaigns to Maximize Clicks with a CPC ceiling) and does not read Ads conversions for decisions — only internal truth. The gate is re-sent weekly in the digest until answered.

### 6.6 Settling windows

| Source / metric | Settled at | Rule |
|---|---|---|
| Ads cost, clicks, impressions | D+3 (Sydney day) | invalid-click credits and late data |
| Ads conversions (GA4 import) | D+7 | 24–48 h import lag observed, plus click-date re-attribution |
| Ads conversions (click upload) | order date + 3 | uploads run daily for D-1 orders; Google processing ≤ 24 h |
| GA4 events | D+2 | GA4 processing |
| Shopify orders | D+1 | |
| Purchase-stage entity CM | click window 14 d after the last day of the window | lag from click to order |
| Problem-aware entity value | 30 d | longer consideration |
| Refund discount | continuous to day 100 | §3.2 |

`fact_coverage.settled` flips to 1 when the day passes its window; decision classes that compare periods only use settled days; digest shows unsettled days in grey with `(settling)`.

### 6.7 Lagged and assisted value (stage-specific measurement)

| Awareness stage | Primary judgement metric | Secondary | Horizon |
|---|---|---|---|
| MOST_AWARE (brand, cartridge) | click-capture ratio (§16.6), CM | — | 14 d |
| PRODUCT_AWARE | CM_ROAS (last paid click) | ATC-value proxy | 14 d |
| SOLUTION_AWARE | CM_ROAS + 0.5 × assisted CM | ATC-value proxy, checkout starts | 21 d |
| PROBLEM_AWARE | engaged-session rate, ATC-value proxy, email signups, assisted CM | CM_ROAS reported but not used to kill before 30 d | 30 d |
| UNAWARE | not targeted (no search campaigns for unaware traffic; see §22) | — | — |

**ATC-value proxy:** `v_atc = P(purchase | add_to_cart) × C_new`, with `P(purchase|ATC)` = site-wide GA4 `transactions / sessions with add_to_cart` over 90 days, Beta-shrunk (prior Beta(1,9), strength 10). Used for incubation floors and exploration ranking only; never uploaded to Google as a primary conversion and never counted in headline CM.

**Email-assisted:** orders whose `email_sha256` belongs to a profile first created within 30 days after a paid first-touch session (Klaviyo profile `created` vs tracker `ft_json.ts`, joined on email hash where Klaviyo returns it) count as assisted for the first-touch entity.

### 6.8 Reconciliation (job `recon`, daily 07:20 Stockholm, over settled windows)

| Id | Check | Tolerance | On breach |
|---|---|---|---|
| R1 | Shopify web orders (excl. draft/test) vs tracker purchases matched by order id, rolling 14 d | match rate ≥ 0.90 (consent-declined orders still fire the pixel only if Shopify's privacy settings allow it — baseline measured in UNIT 1.10; tolerance is reset to baseline − 0.05 if lower) | sev 2 `TRACKER_GAP`; if match rate < 0.5 or 0 matches with ≥ 2 orders in 7 d → sev 1 `TRACKING_BROKEN`, trust → 0 |
| R2 | tracker purchases with `ga4_status=204` vs GA4 `ga4_transactions` by transaction id, rolling 7 d, D+2 settled | ≥ 0.85 | sev 2 `GA4_FORWARD_GAP` |
| R3 | GA4 transactions attributed to `google / cpc` vs tracker orders with paid-search last touch, 28 d | abs diff ≤ max(1 order, 30%) | sev 3 (diagnostic; this is the §5.5 join) |
| R4 | Ads primary conversions (by conversion date) vs tracker orders with a Google click id and marketing consent, 28 d, D+7 settled | abs diff ≤ max(1, 20%) | sev 2 `ADS_CONV_GAP`; blocks G-CONV-3 |
| R5 | Ads conversion value (converted to SEK) vs Σ uploaded `value_sek` for the same orders | ≤ 2% | sev 3 `ADS_VALUE_MISMATCH` (currency conversion or value-rule interference) |
| R6 | Ads cost vs GA4 `advertiserAdCost` per campaign, 28 d | ≤ 5% (GA4 converts currency; tz differs) | sev 4 |
| R7 | Shopify order totals vs line-item sums | 1 SEK | row excluded, sev 3 |
| R8 | Ads account identity (id, currency, tz) | exact | sev 1, abort |
| R9 | `conversion_action` snapshot unchanged vs last approved hygiene state (primary flags, status) | exact | sev 1 `CONV_CONFIG_DRIFT` (someone changed goals) + trust → 1 max |

Discrepancies are never averaged: the digest shows the authoritative number and, beside it, "Δ vs GA4 −2 orders (R3)". Incidents auto-resolve after 3 consecutive in-tolerance days.

### 6.9 UTM / tracking-template standard

- Keep the `google-ads/ops-operations.md` scheme (per-campaign `final_url_suffix` with `utm_source/medium/campaign/term/content` + `{campaignid}`). adsys **reads** the existing suffixes in UNIT 0.13 and fails loudly if any ENABLED campaign lacks one.
- Superset appended (migration note: existing params unchanged, four added, applied at campaign level so ads inherit): `nr_c={campaignid}&nr_ag={adgroupid}&nr_ad={creative}&nr_kw={targetid}`. Where `utm_content` is not already defined by the old scheme, it becomes `{adgroupid}_{creative}` so GA4's `sessionManualAdContent` resolves to an ad group.
- Auto-tagging must be ON (`customer.auto_tagging_enabled`); gclid is then appended automatically.
- **Enforcement at creation:** the action layer composes the suffix from `adsys/utm.py::suffix_for(campaign)`; the pre-flight check (P-UTM) rejects any create/update whose effective suffix is not byte-equal to the composed one.

### 6.10 End-to-end verification (job `e2e`, proves the chain rather than trusting a zero)

| Leg | Synthetic test (daily 05:37) | Real-traffic proof (daily, in `recon`) |
|---|---|---|
| Browser → pixel → tracker | Headless Chromium (profile dir under `TMP`, deleted after run) loads `https://{canonical_host}/?nr_probe=<uuid>` with consent accepted; asserts a `probes` row with that token within 120 s | — |
| Tracker → GA4 MP | Tracker sends MP event `nr_synthetic_probe` (not `purchase`; revenue untouched) with the probe token; `ga4-read.py realtime nr_synthetic_probe` must show ≥ 1 within 30 min | R2 |
| GA4 → Ads import | not synthesisable without polluting revenue | R4 |
| Order → Ads (click upload) | `uploadClickConversions` with `validate_only=true`, a syntactically valid synthetic gclid-shaped payload: asserts auth, action resource name and schema are valid (a "click not found" partial failure is the expected pass signal) | R4, R5 |
| Webhook | Shopify webhook registration read (existing doctor check) | R1 |

A failed synthetic leg writes coverage `BROKEN` for the dependent tables and opens `E2E_<LEG>` sev 2; two consecutive days → sev 1 and trust → 0. The system can therefore always answer "prove you are alive and measuring": the digest shows the last green time of each leg.

### 6.11 Diagnosis plan for "GA4 paid campaign → transactions = 0" (§5.5 of brief)

Most likely cause, testable in UNIT 0.10: the MP purchase is sent with a `client_id` that is not the browser's `_ga` client id and without `session_id`, so GA4 creates a new user/session and attributes the purchase to `(direct)`/`(not set)`; Ads' GA4-import action then has no Google click to credit — which also explains conversion *value* appearing with a ~zero *count* (fractional/low-credit rows). Test order: (1) compare `purchases.client_id` format against `_ga` format (`<10 digits>.<10 digits>`); (2) `report transactions sessionSourceMedium 30` — if tracker purchases sit under `(direct) / (none)` or `(not set)` the hypothesis holds; (3) check whether a client-side GA4 `purchase` (e.g. Shopify's Google channel) also fires → duplicates by transaction id; (4) after pixel v2, R3 should move within tolerance within 14 days. If it does not, R3 stays a diagnostic incident and decisions are unaffected because they use the internal model (§6.4).

### 6.12 Consent

- Pixel v2 stores click ids only when `marketingAllowed`, GA ids only when `analyticsProcessingAllowed`.
- Click uploads carry `consent.ad_user_data = GRANTED` only for orders whose stored consent says so; others are `SKIPPED_CONSENT` (logged, not uploaded).
- UNIT 1.12 verifies the storefront has a consent banner wired to Shopify's Customer Privacy API and that Google tags respect Consent Mode v2 for EEA users; failure is an incident sev 2 and blocks Stage 1 promotion (a system optimising on non-compliant data is a liability).
- Hashed-email user identifiers on uploads (enhanced conversions) only after N3 and only for consented orders.

### 6.13 Click-conversion upload (job `upload`, daily 08:10 Stockholm)

- Scope: orders created D-1 (and any D-2..D-7 orders not yet uploaded) with `click_id` and marketing consent, not draft/test.
- Call: `POST https://googleads.googleapis.com/v22/customers/{cid}:uploadClickConversions` (through the CLI if it exposes the service; else `adsys/gads_rest.py` using the access token exported by `gads-env.sh` — same credentials, no new access) with `partialFailure=true`, one `ClickConversion` per order: `{gclid|gbraid|wbraid, conversionAction, conversionDateTime:"yyyy-mm-dd hh:mm:ss+01:00", conversionValue: net_rev_sek, currencyCode:"SEK", orderId: shopify order id, consent:{adUserData:"GRANTED"}}`.
- Value = **net revenue ex VAT (SEK)**, not contribution: comparable with Shopify, and contribution stays internal until conversion-value bidding is ever justified (§14.5).
- Idempotency: Google dedupes by `orderId` per action; locally `gads_click_uploads` PK.
- Refunds: `uploadConversionAdjustments` RETRACTION (full) / RESTATEMENT (partial) keyed by `orderId`, daily for refunds created D-1, within Google's adjustment window (verify limit in v22 docs during UNIT 1.7; refunds older than the window are handled internally only).

---

## 7. Reasoning Layer

### 7.1 Roles

| Role | Job | Tier (config `llm.tiers`) | May act directly? | Output |
|---|---|---|---|---|
| R1 Term classifier | Classify search terms and candidate keywords: relevance (RELEVANT / IRRELEVANT / AMBIGUOUS), negative category, language, intent, awareness, journey, pain point | fast (a Gemini-Flash-class model via `GOOGLE_AI_STUDIO_API_KEY`) + second fast model via OpenRouter for agreement | No — labels feed D1/D4 | JSON per term |
| R2 Tagger | Backfill taxonomy for landers, content assets, ICP segments from `nordisk-icp.md` | mid | No | JSON |
| R3 Diagnostician | Explain anomalies/incidents; propose ranked hypotheses (e.g. "impression collapse due to disapproval") with the checks that would confirm | frontier | No — only proposes **diagnostic checks** from an enumerated list the deterministic engine runs | JSON |
| R4 Creative generator | Angles, RSA headlines/descriptions, sitelinks, callouts in Swedish, each line tagged with claim ids | frontier | No — passes to gates | JSON |
| R5 Reviewers (MOE, 3 models, different families) | Score R4/R8 outputs on fluency, claim safety, stage fit, relevance | frontier ×3 | Veto only | JSON verdict |
| R6 Opportunity synthesiser | Cluster demand signals into themes; write hypothesis statements | frontier | No | JSON |
| R7 Narrator | Write digest prose from structured facts; may not introduce any number not present in its input | mid | No | text + number-audit |
| R8 Lander writer | Shopify Page body (Swedish) for a theme from facts, VOC and articles | frontier | No — gated as R4 | HTML fragment + claim map |

Model identifiers live in `ROOT/adsys/config/llm.toml`; routing through Orcarouter first, OpenRouter fallback, provider-direct keys last.

### 7.2 Prompt contract format (`ROOT/adsys/prompts/<role>.v<N>.md`)

Each file has: `ROLE`, `INPUT_SCHEMA` (JSON Schema), `OUTPUT_SCHEMA` (JSON Schema, `additionalProperties:false`, enums for every label), `RULES` (e.g. "never output a number not present in input"), `EXAMPLES` (3 positive, 2 negative), `REFUSAL` shape (`{"status":"UNSURE","reason":…}`). The prompt hash and version are stored in `llm_calls`. Changing a prompt bumps the version and requires the role's golden-set test (`adsys/tests/llm_<role>_golden_tests.py`, 30 labelled cases from real account data) to pass ≥ the previous version's score.

R1 output schema (abridged):
```json
{"type":"object","additionalProperties":false,"required":["items"],
 "properties":{"items":{"type":"array","items":{"type":"object","additionalProperties":false,
  "required":["term","relevance","lang","intent","awareness","journey","pain_point","neg_category","confidence"],
  "properties":{
   "term":{"type":"string"},
   "relevance":{"enum":["RELEVANT","IRRELEVANT","AMBIGUOUS"]},
   "lang":{"enum":["sv","en","fr","other"]},
   "intent":{"enum":["TRANSACTIONAL","INVESTIGATIONAL","INFORMATIONAL","NAV_BRAND","NAV_COMPETITOR","SUPPORT"]},
   "awareness":{"enum":["UNAWARE","PROBLEM_AWARE","SOLUTION_AWARE","PRODUCT_AWARE","MOST_AWARE"]},
   "journey":{"enum":["RESEARCH","COMPARISON","CONSIDERATION","PURCHASE","RETENTION"]},
   "pain_point":{"enum":["DRY_SKIN","ITCHY_SKIN","HARD_WATER","CHLORINE","HEAVY_METALS","HAIR_DAMAGE","ALLERGY","NONE","OTHER"]},
   "neg_category":{"enum":["NONE","PRICE_SHOPPER","DIY","NON_BUYER_INTENT","WRONG_CATEGORY","PROFESSIONAL","WRONG_MECHANISM","COMPETITOR_BRAND","OTHER_LANGUAGE","SPAM","JOBS_EDU","GEO_WRONG"]},
   "confidence":{"type":"number","minimum":0,"maximum":1}}}}}}
```

### 7.3 Validation and fail-closed

1. JSON parse → schema validate → enum check. Failure: one repair retry with the validator error appended; second failure → `llm_calls.status='SCHEMA_FAIL'`, all items labelled `UNKNOWN`.
2. **Agreement rule (R1):** a label affecting an action (IRRELEVANT + category) needs both classifier models to agree and each confidence ≥ 0.7; else `AMBIGUOUS`. `AMBIGUOUS`/`UNKNOWN` → no negation, term re-queued after 7 days or at +5 impressions.
3. **Number audit (R7):** every numeric token in narrator output must match a number in its input payload (string compare after locale normalisation); otherwise the digest falls back to the deterministic template (no prose).
4. **Claims audit (R4/R8):** §12.4, deterministic, runs before MOE.
5. LLM unavailable, timeout (60 s fast / 180 s frontier), budget exhausted: the dependent step returns `NO_ACTION(LLM_UNAVAILABLE)`; deterministic classes (vocabulary negatives, budget holds, circuit breakers, kills) continue unaffected. **Default is no change, never a best guess.**
6. LLM output never contains thresholds, budgets or bids; the executor rejects any action payload whose numeric fields did not come from the policy engine (payload provenance flag set by `policy/*.py` only).

### 7.4 Cost budget

| Role | Volume assumption | Tokens/day (avg) |
|---|---|---|
| R1 | ≤ 150 new terms/day after vocabulary pre-filter, batched 50/call, ×2 models | 40k |
| R2 | backfill once (≈ 150 assets) then ≤ 10/week | 5k |
| R3 | ≤ 3 incidents/day | 15k |
| R4 + R5 | ≤ 3 ad groups/week × (generation 15k + 3 reviews × 10k) | 20k |
| R6 | weekly, 60k | 9k |
| R7 | daily heartbeat 3k, weekly 15k | 5k |
| R8 | ≤ 1 page/week × 60k incl. reviews | 9k |
| **Total** | | **≈ 105k/day** |

Hard caps (config): **400k tokens/day and 3.00 USD/day; 45 USD/month.** Enforced before each call from `llm_calls` sums; denial writes `BUDGET_DENIED`. Degradation order when > 80% of daily cap: R6, R8, R4 deferred to next day → R2 → R3 falls back to template diagnosis → R1 limited to terms with ≥ 3 clicks; R7 falls back to template. At 100%: all L stages off; D continues.

---

## 8. Decision Engine

Code: `ROOT/adsys/policy/d<NN>_<name>.py`, one module per class, pure functions `evaluate(ctx) -> list[Decision]`. Rule versions are module constants; thresholds live in `ROOT/adsys/config/policy.toml` (values below are the shipped defaults).

### 8.1 Signal hierarchy — minimum data per action class

| Action class | Evidence type | Minimum data before acting | Why |
|---|---|---|---|
| Negate irrelevant term (D01) | semantic | vocab match: 1 impression; LLM-agreed: 1 click or 5 impressions | irrelevance is not a rate; waiting only buys more waste |
| Negate costly relevant term (D02) | profitability | cost ≥ 1.0 × `C_new`, 0 purchases, 0 ATC | cost of one order's contribution with nothing to show |
| Pause keyword (D05) | profitability | ≥ 25 clicks, cost ≥ 1.5 × `C_new`, age ≥ 21 d | keyword-level CVR is prior-dominated below ~200 clicks; cost floor limits false kills |
| Rotate RSA (D06) | CTR comparison | ≥ 1,000 impressions per RSA in 56 d | Beta-CTR differences of ~30% need ~1k impressions to reach P ≥ 0.95 |
| Incubation verdict (D15) | leading indicators | 21 d or 63 AUD; floors at 15/20/25 clicks | §8.4 |
| Budget change (D08) | IS + profitability | 28 settled days; ≥ 100 eligible impressions; increases need ≥ 2 attributed purchases | never scale on a single order |
| CPC ceiling (D09) | derived | none (prior-backed), change ≤ ±15%/7 d | ceiling is economics, not a test |
| Scale (D19) | profitability | ≥ 6 purchases in 56 settled days | with k=400 prior, 6 purchases moves the posterior meaningfully |
| Geo/device/schedule (D20) | segment CVR | ≥ 300 clicks and ≥ 5 purchases per segment in 90 d | below that, segment differences are noise |
| Kill non-incubating (D16) | profitability | ad group cost ≥ 2 × `C_new`; campaign ≥ 3 × `C_new` | kills must survive one unlucky month |

**Anti-1-of-2 rule (all classes):** any "winner" claim (scale, graduate on CVR, promote a variant) requires ≥ 2 purchases and ≥ 30 clicks in the entity; any rate comparison requires trials ≥ 30 per arm. A single order can graduate an incubation (as evidence that the path converts), never scale it.

**Volume-adaptive by construction:** thresholds are absolute evidence counts, so the same rules fire faster as volume grows. At today's measured paid volume (unknown until tracking is fixed; recorded Ads conversions 0.61/30 d) mainly D01, D03, D09, D10, D11, D15 and the circuit breakers fire. At ≈ 100 paid orders/month, D02/D05/D08/D16/D19 fire weekly and D06/D20 monthly. Priors come from what already sells (§8.2, §10.0), not from the broken Ads conversion count, so the system does not start by assuming ads fail.

### 8.2 Belief model

Beta-Binomial for rates, fixed-strength hierarchical shrinkage: a child's prior is `Beta(k·m_parent, k·(1−m_parent))` where `m_parent` is the parent's posterior mean. Recomputed nightly, top-down (account → role → campaign → ad group → keyword/term).

**Root priors (account level):**

| Metric | Prior mean | Source | Strength |
|---|---|---|---|
| CTR non-brand Search | recomputed in UNIT 1.10 from historical non-brand search terms **excluding any term containing the brand token** (the raw campaign pool, 189 clicks / 2,145 impressions = 8.81%, may be brand-contaminated via broad match) | legacy search terms, mined not surfaced | 200 pseudo-impressions (≤ 10% of the 2,145 observed impressions, so data outweighs prior) |
| CTR brand | 37.8% | 34 / 90 | 50 |
| CVR (click→purchase) non-brand, default | 0.7 × organic CVR of the ad group's landing page (`page_value.cvr_org_post_mean`) if the page has ≥ 2 orders in 90 d; else 0.5 × `site_cvr_90d` | Shopify + tracker + GA4 via §10.0; 0.7 because paid visitors of the same query convert somewhat below organic ones that chose the result | 150 when page-based (evidence exists), 400 when site-based; legacy 0/189 applied only to site-based priors |
| CVR brand | `site_cvr_90d` | as above | 100 |
| ATC rate | GA4 paid-search ATC sessions ÷ sessions, 90 d (site-wide if < 100 paid sessions) | GA4 | 150 |
| Engaged rate | GA4 paid-search engaged ÷ sessions, 90 d | GA4 | 100 |
| Relevant share (clicks from RELEVANT terms) | 0.70 | weak default | 10 |

**Strengths by level (k):**

| Metric | role / campaign | ad group | keyword / term |
|---|---|---|---|
| CTR | 200 | 100 | 50 |
| CVR | 400 | 300 | 200 |
| ATC | 150 | 100 | 50 |
| Engaged | 100 | 50 | 30 |

Reasoning: conversion rates across entities of one store rarely differ by more than 3×; a keyword should not carry half its own weight until ≈ 200 clicks, which at ≈ 7 non-brand clicks/day account-wide means keyword-level CVR almost never drives action — by design. If UNIT 3.2 calibration shows posterior intervals covering < 70% of realised values, k is halved for that metric (prior too confident).

**Profitability posterior (seeded, reproducible):** 20,000 draws, RNG seed = first 8 bytes of `sha256(decision_id)`:
`cvr ~ Beta(post)`, `C ~ Normal(C_new, sd)` truncated at 0 (`sd` from `value_beliefs`; if n < 10, `sd = 0.5 × C_new`), `cpc_sek` = observed window mean (planner low top-of-page bid for untested entities). `CM_ROAS = cvr × C / cpc_sek`. Stored: mean, 10th/90th percentiles, `P(profitable) = P(CM_ROAS > 1)`.

### 8.3 Global guards (evaluated before every class, in order; the first hit sets the outcome)

| Guard | Condition | Outcome |
|---|---|---|
| G1 HALT | `ROOT/adsys/state/HALT` exists | `BLOCKED(HALT)` — circuit-breaker pauses still allowed |
| G2 Stage | class's required stage > current trust stage | `BLOCKED(STAGE)`, logged as counterfactual |
| G3 Data | any required input `BROKEN`, `STALE` or unsettled | `NO_ACTION(DATA_BROKEN)` |
| G4 Human lock | `gads_change_event` shows a non-API edit to the entity or its parent within 14 d | `NO_ACTION(HUMAN_LOCK)`; the edit is treated as strategy and noted in the digest |
| G5 Cooldown | entity touched by adsys within the class cooldown | `NO_ACTION(VELOCITY)` |
| G6 Anti-thrash | action reverses an adsys action on the same entity within 28 d and the posterior mean has moved < 50% of the original 80% CI width | `NO_ACTION(ANTI_THRASH)` |
| G7 Account velocity | > 40 mutations today, or > 10 non-negative mutations today | `NO_ACTION(VELOCITY)` |
| G8 Cap | spend-increasing action and capguard `check()` refuses | `BLOCKED(CAP)` |
| G9 Legacy | entity lifecycle `LEGACY_PAUSED` | never re-enabled; data mined only |

**Stage-0 exception:** circuit-breaker pauses (CB-*, §15.2) are the only mutations allowed at Stage 0, because they can only reduce spend.

### 8.4 Creation common block (D12, D13, D14)

- **Hypothesis record (required, P-HYP):** `statement` ("Problem-aware searches about dry skin after showering convert to the filter at ≥ the ad-group prior when routed to /pages/torr-hud-efter-duschen-duschfilter"), `metric`, `predicted_value` + 80% interval from the belief model, `confidence`, `deadline`, `floor_json`.
- **Launch envelope:** per §3.5 — at start **N = 3.00 AUD/day, M = 21 days, ≤ 63 AUD total, ≤ 2 concurrent**; at current cap ≥ 60 AUD/day, N = 5% of cap, M = 14 d, ≤ 6 concurrent. 63 AUD ≈ 30 clicks at 2.09 AUD — the smallest sample at which the floors below discriminate.
- **Pre-flight (all must pass; each is a function in `adsys/preflight.py`):** P-URL200 (direct fetch 200, no redirect, within 10 min before submit), P-HOST (https + canonical host from config), P-PATH (descriptive path or the lander's `preferred_alias_id`), P-LANG (`<html lang>` = campaign language), P-REL (lander relevance ≥ 0.3 token overlap or R2 score ≥ 7/10), P-TRACK (pixel probe green in last 24 h; lander on the pixel-bearing storefront domain), P-UTM (§6.9), P-COPY (§12 gates passed), P-NEG20 (≥ 20 negatives effective on the campaign if any BROAD keyword), P-DUP (no `fail_memory` fingerprint match without satisfied retry condition), P-HYP, P-CAP (envelope fits cap and incubation count), P-STOCK (target variant inventory ≥ 5), P-GEO (Sweden, `PRESENCE` targeting), P-NET (search network only; partners and display off).
- **Pre-committed auto-kill:** D15. No owner action required.

### 8.5 Policy classes

Format per class: Inputs · Trigger · Rule · Threshold/why · Min-data guard · Confidence · Authorisation (stage, mode) · Blast radius · Velocity · Bounds · Rollback · Escalation · Do-nothing.

**D01 Negate irrelevant search term**
- Inputs: `gads_search_term_daily` (28 d), R1 labels, `neg_vocab`, `ent_keyword`, ad-group awareness stage, GA4 `manual_term` ATC.
- Trigger: term with ≥ 1 impression in the hot window, not already negated or a keyword.
- Rule: negate if (a) vocab match (token-sequence match on term or any inflection; `auto_apply=1`; ad-group stage not in `stage_exempt`), or (b) R1 IRRELEVANT agreed by both models with confidence ≥ 0.7, or (c) `lang` ≠ campaign language, or (d) GEO_WRONG. Vocab hits → PHRASE negative of the vocab term (all inflections) on shared list `NR vocab negatives (sv)`; R1 hits → EXACT negative of the full term at campaign level.
- Safety vetoes: term has any purchase or ATC in 90 d; negative would block an ENABLED positive keyword in scope (conflict check: negative tokens ⊂ keyword tokens in order); term contains the brand token.
- Min data: §8.1. Confidence: vocab = 1.0; R1 = min of two confidences.
- Authorisation: Stage ≥ 1, autonomous-notify. Blast radius: one query's traffic; spend-reducing. Velocity: ≤ 25/day, ≤ 100/week. Bounds: ≤ 80 chars, ≤ 10 words.
- Rollback: remove criterion (`inverse_json`). Escalation: > 25 candidates/day for 3 consecutive days → digest "waste surge" + R3 diagnosis (likely match-type leak).
- Do-nothing: AMBIGUOUS/UNKNOWN → re-queue at +7 d or +5 impressions.

**D02 Negate costly relevant term**
- Trigger: RELEVANT term, `cost_28d_sek ≥ 1.0 × C_new`, 0 purchases, 0 ATC (if term→ATC unresolvable: cost ≥ 1.5 × `C_new`), `P(profitable) < 0.10` with term prior from ad group (k=200).
- Action: EXACT negative at ad-group level. Stage ≥ 1, notify. Velocity ≤ 5/week; 28-d ad-group cooldown for D02.
- Rollback: remove. Do-nothing: below cost floor → revisit when cost crosses it.

**D03 Promote negative to account shared list**
- Trigger: same term negated in ≥ 2 campaigns, or vocab category with `default_scope=ACCOUNT_LIST`.
- Action: add to `NR account negatives`; remove duplicate campaign-level copies after read-back. Stage ≥ 1. ≤ 10/week. Bound: list ≤ 5,000 entries.

**D04 Harvest search term → keyword**
- Trigger: RELEVANT term, not a keyword, ≥ 3 clicks in 28 d and (≥ 1 ATC or purchase, or term CTR posterior mean ≥ ad-group mean).
- Action: EXACT keyword in the ad group whose tags (stage, pain, product) match and whose lander passes P-REL; if that is a different ad group from the source, add an EXACT negative in the source ad group (query sculpting).
- Stage ≥ 2, notify. ≤ 10 per ad group per week. Rollback: pause keyword, remove sculpting negative.

**D05 Pause keyword**
- Trigger: ≥ 25 clicks in 56 d, cost ≥ 1.5 × `C_new`, 0 purchases, `P(profitable) < 0.10`, age ≥ 21 d, not the last ENABLED keyword in its ad group (else → D16).
- QS branch: QS ≤ 3 with `post_click_quality_score = BELOW_AVERAGE` and ≥ 100 impressions → route to D11 (a landing-page cost problem), no pause.
- Stage ≥ 1, notify. ≤ 5/day. Hysteresis: re-enable only if `P(profitable) > 0.40` later (parent evidence). Rollback: set ENABLED.

**D06 Rotate RSA**
- Trigger: ≥ 2 ENABLED RSAs, each ≥ 1,000 impressions in 56 d, `P(CTR_a < CTR_best) ≥ 0.95`, RSA a has 0 attributed purchases.
- Action: pause a, queue replacement via §12. Always ≥ 1 ENABLED RSA. Stage ≥ 1; 28-d cooldown per ad group. Honest note: at brand's 90 impressions/30 d this cannot fire for ≈ a year.

**D07 Refresh assets (fatigue)**
- Trigger: asset `performance_label = LOW` in 2 consecutive weekly snapshots with ≥ 2,000 ad impressions, or `ad_strength = POOR`, or CTR posterior of the last 28 d < 60% of the first 28 d with ≥ 300 impressions in each window.
- Action: generate replacement assets (§12), swap one asset slot per refresh. Stage ≥ 2. ≤ 1 per ad group per 28 d.

**D08 Budget reallocation within cap** (weekly, Monday)
- Pools: brand (D17), exploration (incubations, ≤ 40% of cap), performance (ACTIVE non-brand, remainder). Unused performance pool is **not** force-spent.
- Increase +20% (min +0.50 AUD) if budget-limited (`search_budget_lost_is ≥ 0.20` averaged over days with ≥ 10 impressions, ≥ 100 eligible impressions) **and** ≥ 2 attributed purchases in 56 d **and** `P(CM_ROAS ≥ 1) ≥ 0.6`.
- Decrease −30% (floor 1.50 AUD/day) if cost_28d ≥ 2 × `C_new` **and** `P(CM_ROAS < 1) ≥ 0.9` **and** ATC-proxy value < 0.5 × spend.
- Rank-limited (`search_rank_lost_is ≥ 0.5`) and not budget-limited → no budget change; route to D09/QS.
- Stage ≥ 1, notify. Cooldown 7 d per campaign. Capguard pre-check. Rollback: previous `amount_micros`. Do-nothing: hold with revisit trigger "≥ 2 purchases or cost ≥ 2 × C_new".

**D09 CPC ceiling**
- ACTIVE entities: `ceiling_aud = clamp(0.9 × median(cvr × C) / fx_AUD→SEK, 0.20, 3.00)`. If the unclamped value < 0.20 AUD, the entity is unviable → D16 candidate instead of buying junk clicks.
- INCUBATING entities (exploration clause): `min(3.00, max(breakeven_ceiling, 1.2 × planner low top-of-page bid))`.
- Brand 1.50 AUD. Conquest 0.5 × non-brand ceiling.
- Change only if |new − current| > 10%; move at most ±15% per 7 d. Applied as `target_spend.cpc_bid_ceiling_micros` (Maximize Clicks) or ad-group `cpc_bid_micros` (Manual CPC). Stage ≥ 1. Blocked if FX is `FX_ASSUMED` > 3 d.

**D10 Bidding strategy correction**
- Trigger: campaign on MAXIMIZE_CONVERSIONS / TARGET_CPA / MAXIMIZE_CONVERSION_VALUE / TARGET_ROAS while G-CONV not closed or < 30 clean primary conversions in 30 d.
- Action: → TARGET_SPEND (Maximize Clicks) with D09 ceiling; brand → TARGET_IMPRESSION_SHARE (ANYWHERE_ON_PAGE, 90%, ceiling 1.50 AUD).
- Stage ≥ 1, notify. One-time per campaign; 28-d cooldown. Rollback: restore stored strategy. Return to conversion bidding is a D19/G-CONV matter, not automatic.

**D11 Lander routing**
- (a) ENABLED ad final URL non-200 on two checks 10 min apart → pause those ads (circuit breaker CB-LANDER, allowed from Stage 0).
- (b) URL returns 301 → update ad `final_urls` to the canonical target after P-URL200 (Stage ≥ 1).
- (c) `<html lang>` ≠ campaign language → pause ads, incident sev 2.
- (d) Mismatch: ad-group CTR posterior ≥ parent mean but engaged-rate posterior < 0.6 × parent → SEQUENTIAL_SWAP experiment to the best-scoring alternative lander of the same stage class for 21 d (Stage ≥ 2).
- Layer attribution: CTR low → ad/keyword problem; CTR ok + engagement low → lander/intent problem; engagement ok + no ATC → offer/price problem (reported, not "fixable" by ads).

**D12 Create ad group** — Stage ≥ 2. Source: §10 queue (score ≥ 0.25). §8.4 envelope and pre-flight. ≤ 2/week. Lifecycle `INCUBATING`.

**D13 Create campaign** — Stage ≥ 3. Types: Search SV; Standard Shopping (needs N2 and ≥ 90% of feed items approved for Shopping ads in Sweden). PMax (≥ 30 clean conversions/30 d), Demand Gen / Video and market steps 1–3: Stage 3 per §14.7. ≤ 1 per 14 d. Created PAUSED, fully assembled, read back, then ENABLED.

**D14 Create lander page (lander factory)** — Stage ≥ 2. Trigger: a PROVEN/PROMISING query cluster or opportunity (score ≥ 0.25) whose best existing lander scores < 0.5 relevance, or a diagnosis of PROMISE_DISCONNECT (§12.8). One page per query cluster × stage × market ("a page per segment"). Shopify Page (non-theme), §12.6. ≤ 5/week; ≤ 1 per cluster per 28 d; pages whose paid engaged rate is < 0.6 × parent after 150 sessions are unpublished (graveyard).

**D15 Incubation evaluation** (daily from day 7; final at deadline or when spend reaches the envelope total)

| Verdict | Condition | Action |
|---|---|---|
| NO_DEMAND | impressions < 100 by deadline | pause; fail memory, retry after 180 d or if planner volume doubles |
| TARGETING_LEAK (early-kill eligible) | clicks ≥ 15 and relevant-share posterior mean < 0.5 | pause; retry after negatives/keyword rework |
| LANDER_MISMATCH | clicks ≥ 20 and engaged-rate posterior < 0.6 × parent (35% absolute until UNIT 1.10 baseline) | pause; retry with a different lander |
| FUNNEL_DEAD | 0 ATC, 0 checkout, 0 purchase and `(1 − atc_parent)^clicks < 0.10` (e.g. parent ATC 8% → kill at 28 clicks) | pause; retry after 90 d or price/offer change |
| PASS → GRADUATE | ≥ 1 purchase, or ATC posterior mean ≥ parent mean, and no kill verdict | lifecycle ACTIVE; ceiling switches to breakeven formula |
| INCONCLUSIVE | < 20 clicks at deadline | extend once by 10 d (same envelope); still < 20 → pause, retry after 90 d |

Also early-kill on: disapproval unresolved for 72 h; lander BROKEN. Authorisation: autonomous-notify (kills are always allowed — they reduce spend). Every verdict writes `fail_memory` (non-PASS) and closes the hypothesis.

**D16 Kill non-incubating entity** — ad group: cost_56d ≥ 2 × `C_new`, `P(profitable) < 0.10`, ATC-proxy value < 0.25 × spend; campaign: cost_56d ≥ 3 × `C_new`, same conditions. Action: pause (`PAUSED_BY_SYSTEM`), fail memory. Stage ≥ 1. Re-enable only through a fresh D12/D13 hypothesis.

**D17 Brand governance** — budget = clamp(1.5 × max daily brand spend in 28 d, 1.50, 3.00) AUD; TARGET_IMPRESSION_SHARE 90%, ceiling 1.50 AUD; any brand-campaign search term without the brand token → EXACT negative in the brand campaign. Never auto-killed. After E-01 (§16.6): capture ratio ≥ 0.8 → budget 1.00 AUD/day, defensive only; re-raise if weekly Serper check shows competitor ads on brand queries. Stage ≥ 1.

**D18 Conquest governance** — competitor-name keywords only in CONQUEST campaigns; lander = comparison page; ad text may not contain any `banned_phrases` TRADEMARK entry; ceiling 0.5 × non-brand; judged on engaged rate + assisted CM (PROBLEM/SOLUTION measurement); incubation rules apply.

**D19 Scale entity (Stage 2)** — ACTIVE ≥ 28 d, ≥ 6 attributed purchases in 56 settled days, `P(CM_ROAS ≥ growth_floor × 1.2) ≥ 0.8`, budget-limited → +30% per 7 d within the performance pool.

**D21 Spend ramp (Stage 2; weekly; account level)** — sets the ramp value; capguard applies `current = max(15, min(ramp, governor, ceiling))` daily.
- Up ×1.5 (min +5 AUD) if: bottleneck = SPEND; ≥ 5 paid orders in last 14 settled days; paid `P(CM_ROAS ≥ growth_floor) ≥ 0.7`; the previous step's incremental spend returned incremental paid CM ≥ `growth_floor` × incremental spend **and** a total-store-order lift posterior > 0 (§3.7 incrementality check; skipped for the first step).
- Hold otherwise, with the failing condition as `revisit_trigger`; bottleneck GOVERNOR is reported, not fought — the governor is the owner's rule.
- Down ×0.7 (floor 15) if paid `P(CM_ROAS < 0.8 × floor) ≥ 0.8` with ≥ 5 orders, or the last step's marginal CM_ROAS median < 0.5, or its total-order lift posterior ≤ 0.
- Governor enforcement is independent of D21: if store revenue falls, capguard lowers budgets the same day (largest non-brand budgets first, incubations last so learning continues).
- Bounds: capguard refuses steps > ×1.5, within 7 days of the last step, or above min(governor, ceiling).

**D20 Geo / device / schedule (Stage 4)** — segment ≥ 300 clicks and ≥ 5 purchases in 90 d and `P(segment CVR < 0.5 × campaign CVR) ≥ 0.9` → −30% modifier (only if the bid strategy honours modifiers; else not attempted). Schedules are set in Sydney time: `adsys/tz.py::sto_to_syd_schedule()` converts, recomputed at each DST change.

**D00 Do-nothing and "out of ideas"** — each weekly cycle writes one `NO_ACTION` decision per (entity, class) evaluated, with `revisit_trigger`. When the opportunity queue is empty the opportunity engine runs, in order: GSC impressions-without-clicks re-mine; competitor sitemap diff; ICP pain × product gap matrix; retry-eligible fail memory; Shopping surface (if not launched). If still empty: digest states "steady state — holding; next re-scan <date>".

---

## 9. Action Layer

### 9.1 Executor algorithm (`ROOT/adsys/actions/executor.py`)

1. Load action (`actions` row + `PLANNED` event). Payload must carry `provenance="policy"`; else reject.
2. G1 HALT → `BLOCKED_BY_HALT` (except `CB_PAUSE`). G2 stage → `BLOCKED_BY_STAGE`. Capguard `check()` for spend-increasing types → `BLOCKED_BY_CAP`.
3. Re-run class pre-conditions against **fresh** reads (≤ 10 min old).
4. Idempotency: `idem_key = sha256(action_type | target_ref | canonical_json(payload) | decision_id)`; if an `APPLIED`/`VERIFIED` event exists → skip. For creates, natural-key read-before-write (same name/text in same parent) → adopt existing, mark `VERIFIED`.
5. Read `before_json`; compute and store `inverse_json`.
6. `--validate-only` call → `VALIDATED` (or `FAILED` with policy errors; no exemption requests ever).
7. Apply with `--partial-failure --agent`. Batch bound: ≤ 20 operations per call; > 20 entities → split and stage over days (G7).
8. Every action also records `effect_reversibility` ∈ {`REVERSIBLE`, `REVERSIBLE_WITH_LOSS`, `IRREVERSIBLE`}: `inverse_json` undoes the *write*, not spend already made, emails already sent or learning already reset. Caps (§18.2) are the real safety layer; breakers and rollbacks limit damage after the fact.
9. Read back via GAQL within 60 s; compare expected fields → `VERIFIED`; mismatch → apply `inverse_json`, `ROLLED_BACK`, incident sev 2.
10. New ads: re-read `policy_summary.approval_status` at +24 h and +72 h.

Exact CLI verb syntax is pinned once in `adsys/gads.py` (UNIT 0.1 records `--help` output for each family into `adsys/gads_syntax.json` and a test asserts it). Shapes below follow Google Ads API v22 REST JSON; `C` = `customers/8479789152`.

### 9.2 Action catalogue

| action_type | CLI family | Operation shape | Read-back | Inverse |
|---|---|---|---|---|
| `NEG_CAMPAIGN_ADD` | customers-campaign-criteria | `{"create":{"campaign":"C/campaigns/{id}","negative":true,"keyword":{"text":"…","matchType":"EXACT"}}}` | `campaign_criterion` by resource name | `{"remove":"C/campaignCriteria/{id}~{crit}"}` |
| `NEG_ADGROUP_ADD` | customers-ad-group-criteria | `{"create":{"adGroup":"C/adGroups/{id}","negative":true,"keyword":{…}}}` | `ad_group_criterion` | remove |
| `NEG_SHARED_ADD` | customers-shared-criteria | `{"create":{"sharedSet":"C/sharedSets/{id}","keyword":{…}}}` | `shared_criterion` | remove |
| `SHARED_SET_CREATE_ATTACH` | customers-shared-sets + campaign shared sets | create `{"name":"NR vocab negatives (sv)","type":"NEGATIVE_KEYWORDS"}` then attach to campaign | `shared_set`, `campaign_shared_set` | detach (set kept) |
| `KW_ADD` | customers-ad-group-criteria | `{"create":{"adGroup":…,"status":"ENABLED","keyword":{"text":"…","matchType":"EXACT"}}}` | `ad_group_criterion` | status PAUSED |
| `KW_STATUS` | customers-ad-group-criteria | `{"update":{"resourceName":…,"status":"PAUSED"},"updateMask":"status"}` | same | previous status |
| `AD_STATUS` | customers-ad-group-ads | `{"update":{"resourceName":"C/adGroupAds/{ag}~{ad}","status":"PAUSED"},"updateMask":"status"}` | `ad_group_ad` | previous status |
| `RSA_CREATE` | customers-ad-group-ads | `{"create":{"adGroup":…,"status":"ENABLED","ad":{"finalUrls":["https://{host}{path}"],"responsiveSearchAd":{"headlines":[{"text":"…"}],"descriptions":[{"text":"…"}],"path1":"…","path2":"…"}}}}` | `ad_group_ad` incl. policy | status PAUSED |
| `AD_FINAL_URL` | customers-ads | `{"update":{"resourceName":"C/ads/{id}","finalUrls":["…"]},"updateMask":"final_urls"}` | `ad` | previous URLs |
| `ASSET_CREATE_LINK` | customers-assets + ad-group/campaign-assets | create text/sitelink/callout asset, link with `fieldType` | asset + link | remove link |
| `BUDGET_SET` | customers-campaign-budgets | `{"update":{"resourceName":"C/campaignBudgets/{id}","amountMicros":"…"},"updateMask":"amount_micros"}` | `campaign_budget` | previous amount |
| `CPC_CEILING` | customers-campaigns | `{"update":{"resourceName":…,"targetSpend":{"cpcBidCeilingMicros":"…"}},"updateMask":"target_spend.cpc_bid_ceiling_micros"}` | `campaign` | previous |
| `BID_STRATEGY` | customers-campaigns | update `targetSpend` or `targetImpressionShare{location,locationFractionMicros,cpcBidCeilingMicros}` | `campaign` | stored previous strategy fields |
| `CAMPAIGN_STATUS` / `ADGROUP_STATUS` | customers-campaigns / customers-ad-groups | status update | entity | previous |
| `CAMPAIGN_CREATE` | budgets → campaigns → campaign-criteria (geo `geoTargetConstants/2752` PRESENCE, language) → ad-groups → criteria → ads → assets | all created with campaign `status:"PAUSED"`, `networkSettings{targetGoogleSearch:true,targetSearchNetwork:false,targetContentNetwork:false}`, `geoTargetTypeSetting.positiveGeoTargetType:"PRESENCE"`, `finalUrlSuffix` from §6.9, `containsEuPoliticalAdvertising` set as the API requires | full tree | campaign PAUSED (never removed) |
| `CAMPAIGN_ENABLE` | customers-campaigns | status ENABLED after tree read-back | campaign | PAUSED |
| `CONV_ACTION_CREATE_SECONDARY` | customers-conversion-actions | `{"create":{"name":"NR Purchase — server click upload","type":"UPLOAD_CLICKS","category":"PURCHASE","countingType":"MANY_PER_CLICK","primaryForGoal":false,"clickThroughLookbackWindowDays":30}}` | `conversion_action` | status HIDDEN (never removed) |
| `CLICK_UPLOAD` | uploadClickConversions (§6.13) | — | `gads_click_uploads` + R4 | RETRACTION adjustment |
| `CB_PAUSE` | any status update | as above, tagged circuit-breaker | entity | previous status |

`GATE_*` types (conversion goals, cap raise, theme publish) are never executed by the executor directly; they create `gate_requests` and execute only after an `APPROVED` owner command (§19.3).

Idempotency keys for uploads use Google's `orderId` dedupe plus the local PK. All request/response JSON is stored in `action_events.detail_json` (secrets never included — the wrapper strips headers).

---

## 10. Opportunity Engine

Code: `ROOT/adsys/opportunity/`. Weekly (Sunday 20:00 Stockholm), output a ranked queue in `ADB.hypotheses` with status `OPEN` and no entity yet.

### 10.0 Proven demand — start from what already sells (first-priority source)

Built nightly by `adsys/derive/proven_demand.py` into `page_value` and `query_value` (§4.3):

1. **Page → orders (90 d).** For every storefront path: orders whose tracker first- or last-touch landing path is the page; orders whose Shopify `landing_site` path is the page; GA4 `ga4_daily_landing` transactions. Deduplicated by order id; Shopify/tracker evidence outranks GA4. Organic-only subset uses channel from §6.4.
2. **Page organic CVR.** `orders_org / sessions_org` (GA4 organic sessions landing on the page), Beta-shrunk to site CVR with strength 100 sessions.
3. **Query → page.** GSC `traffic_daily` clicks per (query, page), 90 d.
4. **Query value.** `est_orders_90d = Σ_page gsc_clicks(q,p) × cvr_org(p)`; `est_value_sek_90d = est_orders × C_new(product_mix(p))`. Direct paid evidence (Ads search term = query with tracker-attributed orders) is added as `paid_orders_90d`.
5. **Tiers.** PROVEN: `paid_orders_90d ≥ 1`, or `est_orders_90d ≥ 0.5` on a page with ≥ 2 real orders. PROMISING: page has ≥ 1 order and query has ≥ 10 clicks. DEMAND_ONLY: everything else.
6. **Products.** `ga4_daily_item` + Shopify line items give which products sell organically; that product mix sets the ad group's target product and `C_new`.

Uses: PROVEN queries are proposed first, as EXACT/PHRASE keywords in an ad group whose lander is **the page that already sells** (if it passes pre-flight; else its preferred alias); their CVR prior is page-based (§8.2). PROMISING queries follow. DEMAND_ONLY enters the normal scoring below. The cannibalisation rule (§10.4) still applies, except that PROVEN queries where the organic result is below position 3 or competitor ads appear above it are bid on first.

### 10.1 Demand sources → candidate themes

| Source | Extraction | Signal |
|---|---|---|
| Proven demand (`query_value`, `page_value`, §10.0) | PROVEN and PROMISING tiers | real sales |
| Ads search terms (`gads_search_term_daily`, incl. mined legacy data) | RELEVANT terms not yet keywords; R6 clusters them | real paid demand |
| GSC `traffic_daily` | queries with ≥ 50 impressions/28 d and position > 10 (organic cannot capture) → paid candidates; queries with position ≤ 3 → cannibalisation list (§10.4) | organic demand |
| `KDB.kw_ideas`, `gap_ideas` (autosuggest, competitor sitemaps) | ideas with intent ∈ {TRANSACTIONAL, INVESTIGATIONAL} or pain lexicon hit | expansion |
| `KDB.kw_planner_metrics` | volume, competition, top-of-page bid | sizing and CPC |
| `KDB.serp_snapshots` | competitor ads count, own organic position | competition, cannibalisation |
| `nordisk-icp.md` → `tax_pain`, `tax_icp_segment` | pain × product matrix cells with no ad group | ICP gaps |
| competitors table (12) | brand names → conquest candidates; weaknesses → differentiation angles | conquest |
| Google recommendations (A15) | keyword/negative suggestions treated as candidate terms only | signal |
| MemPalace diary / fail memory | retry-eligible fingerprints | second chances |

### 10.2 Scoring

```
score = sqrt(demand) × intent_w × icp_fit × margin_idx × lander_ready × (1 − 0.5 × competition) × novelty × proven
proven      = 1 + 2 × min(1, est_orders_90d / 3)                # 1.0 (no sales evidence) … 3.0 (≥ 3 estimated orders)
demand      = min(1, est_monthly_searches / 500)          # planner; if NO_DATA: min(1, gsc_impr_28d / 500); if both absent: 0.1
intent_w    = TRANSACTIONAL 1.0 | INVESTIGATIONAL 0.7 | PROBLEM-informational 0.4 | NAV_COMPETITOR 0.5 | pure INFORMATIONAL 0.2 | NAV_BRAND 0 (brand is governed by D17)
icp_fit     = 1.0 primary ICP pain | 0.6 secondary | 0.2 none
margin_idx  = C_new(target product) / max_product C_new     # routes non-brand toward higher-contribution products (§1.5)
lander_ready= 1 if some lander passes P-URL200/P-LANG/P-REL else 0 (→ D14 lander request instead)
competition = max(planner competition_index/100, min(1, serp competitor_ads_count/4))
novelty     = 0 if fail_memory match without met retry condition, else 1
```
Threshold 0.25 to enter the queue. Order of proposal: PROVEN, then PROMISING, then by score. Proposals per week = number of free incubation slots (§3.5: 2 at small caps, up to 6). 500 searches/month normalisation: Swedish long-tail rarely exceeds it, and a theme at 500 at ~5% CTR yields ≈ 25 clicks/month — roughly one incubation's sample.

### 10.3 Proposal → gated launch

Proposal = hypothesis row + draft entity spec (keywords, match types, negatives, lander, stage tags, product, envelope). D12/D13 pick it up; pre-flight (§8.4) is the gate; P-COPY triggers §12. No human step.

### 10.4 Cannibalisation rule

A candidate whose query cluster has own organic position ≤ 3 and no competitor ads on the SERP is **not** bid on (paid would buy clicks organic gets free). Re-evaluated monthly; if a competitor starts appearing above the organic result, the rule lifts.

### 10.5 Search-engine and Shopping conquest per proven query

For every PROVEN/PROMISING query the goal is to **own as many SERP surfaces as are profitable**: paid Search (absolute-top impression share), organic (article/lander in top 3, via the existing organic pipeline — adsys writes briefs, it does not publish articles), Shopping ad and free listing (feed titles containing the query phrasing, §12.7), and answer-engine citation (§10.6). The cannibalisation rule (§10.4) becomes: bid on a query where organic is top 3 only when competitor ads or Shopping units appear above the organic result, or when the E-01-style holdout for that query shows paid adds total orders.

### 10.6 Answer-engine conquest (AEO)

GA4 already reports an `AI Assistant` channel. Monthly job `aeo`: 30 buyer questions per market (from GSC question queries with `hur/vad/varför/vilket/bästa/pris/alternativ` and the five types: cost, X vs Y, best for, how it works, what changed this year), asked through OpenRouter to at least 3 model families with web search enabled; cited domains parsed into `aeo_checks`. Output: own citation rate, competitors cited, and briefs for missing answers sent to the organic content pipeline's topic queue (its gates and publisher, not adsys). Technical checks: `robots.txt` allows `OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User` (on Shopify this is `robots.txt.liquid`, a theme file → theme-guard path), FAQ/Product JSON-LD present on landers. Target: own domain cited in ≥ 50% of answers to category questions in Sweden within 6 months of Stage 2.

### 10.7 Category conquest scoreboard

Weekly `conquest_scoreboard` for the top 100 category queries per market (PROVEN first, then planner volume): paid IS and abs-top IS, organic position, Shopping and free-listing presence, AI citation, competitor ads (Serper). `surfaces_owned` = count of the 4 surfaces held. KPIs: share of PROVEN queries with ≥ 2 surfaces owned (target 60% within 6 months of Stage 2); **share of search** = own brand search volume ÷ (own + the 12 competitors' brand volumes) from planner/GSC — the long-run proof that the category is being won. The scoreboard drives priorities: a PROVEN query with 0–1 surfaces owned outranks new DEMAND_ONLY opportunities.

---

## 11. Keyword, Negative & Intent Engine

### 11.1 Keyword lifecycle

`CANDIDATE` (queue) → `INCUBATING` (inside an incubating ad group) → `ACTIVE` → `PAUSED_BY_SYSTEM` → (retry via new hypothesis). Registry: `ent_keyword`, tags from §13.

### 11.2 Match-type strategy

| Situation | Match type | Condition |
|---|---|---|
| New theme discovery (harvest ad group) | BROAD | P-NEG20 satisfied; CPC ceiling; ≤ 3 AUD/day; campaign on Maximize Clicks (broad without smart bidding is wide — the negative engine is its brake) |
| Proven term | EXACT | from D04 harvest |
| Theme ad groups | PHRASE + EXACT | default for D12 |
| Brand | EXACT + PHRASE of brand tokens | D17 |

### 11.3 Grouping

One ad group = one (awareness, pain_point, product, lander) tuple. R6 clusters terms; deterministic post-check: every keyword in the ad group shares the tuple tags; otherwise split.

### 11.4 Negative engine

- **Seed:** `google-ads/negatives.md` parsed into `neg_vocab` (categories: price shoppers, DIY, non-buyer intent, wrong category, professional, wrong buying mechanism) + the hardcoded `ads-monitor.sh` list (lotion, cream, moisturizer, shampoo, lidl, bunnings, competitor brands). `ads-monitor.sh` is changed to read `neg_vocab` (UNIT 2.8).
- **Swedish inflection:** negative keywords do **not** match close variants, so each vocab term stores its forms (e.g. `lotion, lotionen, lotioner, lotionerna`; compound heads where relevant). Forms come from a rule table for common noun declensions plus R1 suggestion; LLM-suggested forms are accepted only if they appear in `gads_search_term_daily`, `traffic_daily` or `kw_ideas` (observed language, not invented).
- **Stage exemptions:** informational stems (`vad är`, `hur`, `varför`) are negatives for PRODUCT/PURCHASE ad groups and exempt for PROBLEM_AWARE ad groups.
- **Competitor brands:** negative in NONBRAND and BRAND campaigns; positive only in CONQUEST.
- **Scopes:** account list `NR account negatives` (spam, jobs/education, other-language, geo-wrong), shared list `NR vocab negatives (sv)` attached to all SV non-brand campaigns, campaign/ad-group level for performance negatives and sculpting.
- **Broad floor:** P-NEG20 counts *effective* negatives on a campaign (own + attached shared lists + account list), and UNIT 0.13 audits the currently ENABLED broad-match campaign against it.
- **Waste signal:** `bunnings` in the historical waste list implies Australian queries reached the account; UNIT 0.13 checks `positive_geo_target_type` (must be `PRESENCE`) and `gads_geo_daily` country split.

### 11.5 Language / locale

- SV campaigns: Swedish keywords, Swedish landers, **language targeting Swedish + English** (Google matches on the user's interface language; many Swedes run English UIs), geography Sweden (PRESENCE). EN-language queries in SV campaigns → OTHER_LANGUAGE negative unless the EN term is on the SV lander's topic and in `ent_keyword` as an intentional EN keyword (none by default).
- EN (`/en/`) and FR (`/fr/`) campaigns: Stage 3 market steps 2–3 (§14.7), each in its own campaign with its own language, lander tree and negative lists; never mixed ad groups.
- Locale detection: keyword-intel SV/EN detection + å/ä/ö heuristic + R1 `lang`; disagreements → `AMBIGUOUS`, not used.
- Lander language verified from `<html lang>` on every check (P-LANG).

### 11.6 Landing-page registry and checks

Seed: `google-ads/landing-page-inventory.md`, `ROOT/ads/nordisk_ads_context.json` (existing intent→ad→lander mappings), sitemap (50 URLs), `published-articles.json` (23), Shopify pages/products. Daily check for landers used by ENABLED ads; weekly for the rest:
- direct `curl -o /dev/null -s -w "%{http_code} %{redirect_url}" --max-redirs 0` on the canonical host; 301/302 → `redirect_to` recorded, lander `DEGRADED`, P-URL200 fails;
- `<html lang>`, canonical link, price on page vs `product_facts` (±0 SEK), banned-phrase scan;
- weekly `nrperf` mobile score and LCP; `nrshot`/`nrmobile.js` screenshot to `ART/landers/` (30-day retention); `nrvision` style-fit on change;
- relevance per ad group: token overlap of lemmatised keyword tokens with title/H1/first 300 words ≥ 0.3, else R2 score.
- Descriptive paths: `/pages/se-4` is code-like; if a descriptive equivalent exists (`/pages/duschfilter-jamforelse-bast-i-test` for comparison intent) it is preferred via `preferred_alias_id`.

---

## 12. Creative & Copy Generation

Pipeline `ROOT/adsys/creative/`, reusing `/root/loops/nordisk-comparison-pipeline/` nodes by import (`swedish_polish`, `judge-reasoning.py`, `judge-reliability.py`, MOE gate). Reaches live with no human step.

### 12.1 Inputs

Ad-group tuple (awareness, journey, pain, product, lander), top keywords, `product_facts` + `product_claims`, VOC phrases from `tax_icp_segment` (ads and landers only — never Shopify product descriptions), `ad-copy-library.md` parsed into `ent_creative` (lifecycle `DRAFT`, origin library), `ad_audit_archetype_weights` as angle priors, fail memory for creatives, asset performance labels.

### 12.2 Stages

| # | Stage | Type | Output |
|---|---|---|---|
| G1 | Angles: pain→solution, proof/spec, offer/guarantee (100 days), comparison (SOLUTION/COMPARISON stages only) | L (R4) | 3 angles |
| G2 | Generate 20 headlines (≤ 30 chars), 6 descriptions (≤ 90), 4 sitelinks (text ≤ 25, lines ≤ 35), 6 callouts (≤ 25), path1/path2 (≤ 15). Each line tagged `claim_ids[]` and `line_type` ∈ {PROBLEM_STATEMENT, CLAIM, CTA, BRAND, KEYWORD_ECHO} | L (R4) | JSON |
| G3 | Deterministic validation (§12.4) | D | pass/fail per line |
| G4 | `swedish_polish` node | L (existing) | revised lines → re-run G3 |
| G5 | MOE: 3 reviewers (different model families). Rubric: fluency 0–10, claim_safety PASS/FAIL with line refs, stage_fit 0–10, keyword relevance 0–10. Pass = no FAIL on claim_safety, median fluency ≥ 8, median stage_fit ≥ 7, median relevance ≥ 7. Max 2 regeneration rounds, then fail memory `creative generation failed` | L (R5) | verdict |
| G6 | Assembly: 15 headlines = ≥ 3 keyword-echo, ≥ 2 benefit (allowed claims), ≥ 2 spec/proof, ≥ 1 guarantee, ≥ 1 CTA, ≥ 1 brand; 4 descriptions. Pinning: none, except brand campaigns pin the brand headline to position 1 | D | RSA spec |
| G7 | `--validate-only` create; non-exemptible policy error → reject line and regenerate once; exemptible → reject (no autonomous exemption requests) | D | |
| G8 | Create live (Stage ≥ 2), max 3 RSAs per ad group (Google limit); approval re-read at +24 h/+72 h; `DISAPPROVED` → pause, R3 diagnosis, fail memory with policy topic | D | |

### 12.3 Brand voice

Stored as `ROOT/adsys/config/brand_voice.md` (derived from existing ad-copy library and site): calm, factual, Nordic understatement; no exclamation marks in headlines; no all-caps words except the brand; no urgency tactics ("sista chansen" etc. are in `banned_phrases` EDITORIAL).

### 12.4 Claims and policy gate (deterministic, before and after MOE)

- Every CLAIM line must map to ≥ 1 `claim_id` whose `allowed_variants_json` contains a phrase with token overlap ≥ 0.8 with the line; otherwise **hard fail**.
- `banned_phrases`: `oberoende tester`, `TEWL`, `klinisk*`/`clinical research`, medical-outcome verbs (`botar`, `läker`, `behandlar`, `förebygger`) combined with conditions (`eksem`, `psoriasis`, `allergi`), unsourced superlatives (`bäst`, `nr 1`) unless a claim id supports them, competitor trademarks (12 competitors + Sparkpod, Magichome, AquaBliss) → hard fail.
- Pain words (torr hud, klåda, hårt vatten, klor, tungmetaller, allergi) are allowed only as PROBLEM_STATEMENT lines ("Torr hud efter duschen?"), never as outcome promises.
- Spec truth: any line mentioning KDF-55, CaSO₃ or GAC must be about Duschvattenfilter; any Duschhuvud line may only mention activated carbon fibre. Mixed → hard fail.
- Price and guarantee: numbers must equal `product_facts` (990/1199/2189/4283/398 SEK; 100 days). A "60 dagar" string anywhere → hard fail.
- No fabricated quotes or reviews: quotation marks with attributions → hard fail.
- Conflict #1 position (§15 of brief): because outcome claims are restricted to an enumerated whitelist and everything else fails closed, the gate is reliable enough to run unattended. The measurable condition that would force copy back behind a human: > 1 disapproval per 20 live ads in a rolling 90 days, or any post-publication claim violation found by the weekly audit (T-CLAIM, §15.3). Either → demotion to Stage 1 for creative classes and incident sev 2.

### 12.5 Images

Product images from Shopify (via `products_rich.json`), judged by `nrvision` for style fit; used only for image assets on Stage 3+ surfaces. No generated product images (they would depict unverified product features).

### 12.6 Landers

- **Autonomous path (Stage ≥ 2): Shopify Pages.** `POST /admin/api/{ver}/pages.json` with `published:false`, `template_suffix` of an existing lander template (no theme write), body from R8 constrained to facts/claims, internal links to the matching article. Gates: §12.4 on every sentence, MOE (G5), `nrshot` desktop+mobile, `nrvision` style-fit ≥ config threshold, `nrperf` mobile score not worse than the median of existing landers minus 10. Then `published:true`, lander checks (§11.6), then eligible for routing. Rollback: unpublish.
- **Theme path (blocking at the last step).** Anything needing a theme section or template change: adsys writes a change spec; `theme_guard.py` flow runs unattended up to and including duplicate theme, preview-URL browser test, 17 tests, Lighthouse on the duplicate; the publish-to-live step creates Gate `THEME_PUBLISH` with preview link, test results and perf delta. Duplicate creation failure → stop and escalate (never edit live). Condition for automating the final step (conflict #2): 20 consecutive gated publishes with zero rollbacks, a visual-diff test on 5 key pages (`nrvisdiff` under threshold) and no perf regression > 5 points — then the owner may reclassify the gate (only he can).
- GemPages pages are routable but never created or edited by adsys (no API in inventory).
- Article featured images stay manual-only; adsys never writes an `image` key.

### 12.7 Feed as creative (Shopping, Stage 3+)

GMC item issues (`gmc_product_status.issues_json`) → incident per item class; title/attribute improvements proposed as edits to the `gmc_title_sv` column consumed by `gmc-feed.py`, validated by §12.4 and MOE, applied autonomously (feed titles are reversible via column history), verified by the next day's status pull.

### 12.8 Creative feedback loop (every surface: RSA assets, sitelinks, Shopping titles, landers, images, video)

Pipeline states in `ent_creative.lifecycle` + `creative_reviews`: `CONCEPT → STAGED → LIVE → FEEDBACK_DUE → {WINNER, HIGH_POTENTIAL} → ITERATION → LIVE …` or `LOSER → GRAVEYARD` (fail memory with the diagnosis).

- **Feedback due:** 7 days after launch **and** a minimum evidence floor per surface (RSA/asset: 300 impressions; lander: 100 sessions; Shopping title: 500 impressions; video: 1,000 views), whichever is later; maximum 28 days, then `INSUFFICIENT` → pooled into the pattern library only. Never judged on day 2.
- **Buckets** (posteriors vs the ad group / surface baseline, same market):
  - WINNER: `P(CTR > baseline) ≥ 0.8` and downstream (engaged rate and ATC) ≥ baseline, or ≥ 1 attributed order.
  - HIGH_POTENTIAL: one strong stage and one weak stage (e.g. CTR strong, engagement weak) — a fixable break.
  - LOSER: `P(CTR < 0.8 × baseline) ≥ 0.8` and no downstream strength.
- **Diagnosis before iteration** (deterministic from metrics, then R3 + `nrvision` visual review for images/landers/video):

| Metric pattern | Diagnosis | Surgical iteration (keep what works) |
|---|---|---|
| rank-lost IS high, QS expected CTR / ad relevance BELOW_AVERAGE | RELEVANCE | tighter ad group (query cluster), headlines echo the query |
| impressions ok, CTR low | HOOK | new headline hooks; descriptions kept |
| CTR high, engaged rate low | PROMISE_DISCONNECT (ad's hook ≠ page's first screen) | keep ad; route to or build a matching page (D14) |
| engaged ok, ATC low | DESIRE/OFFER | lander offer framing: 100-day guarantee, bundle, price anchoring; ad adds offer |
| ATC ok, purchases low | FRICTION | shipping/price/checkout packet to owner (not an ads fix) |
| all good, CM_ROAS ≈ break-even | AOV/MARGIN | route to Wellness Kit / bundles; ad leads with bundle |
| Shopping CTR low | FEED | title/image test via feed loop |

- **Iteration rule:** WINNER and HIGH_POTENTIAL enter the winner loop (§12.11); LOSER → graveyard, no rescue effort.
- **Weekly creative review** (Monday, `creative` job): every FEEDBACK_DUE item reviewed, bucketed, diagnosed, iteration briefs generated and executed inside Stage-2 limits; digest shows win rate and the three biggest lessons.

### 12.9 CTR and Quality Score as the CPC weapon

Actual CPC ≈ the ad rank of the advertiser below ÷ own Quality Score. QS components (expected CTR, ad relevance, landing-page experience) are ingested per keyword (A4). Therefore the historical 2.09 AUD CPC is attacked from the ad side, not only by bidding: every PROVEN query gets its own tight ad group (1 query cluster, headlines echoing it, a page built for it). **Benchmark gate:** a new RSA/asset set must reach CTR ≥ its ad-group baseline posterior within its feedback window, or R4 rewrites the hooks (creative-director loop, max 3 rounds). Target: QS ≥ 7 on ≥ 70% of spend-weighted keywords; tracked weekly with CPC trend. Each QS point gained on a keyword lowers its CPC at constant position — this is the main route from "non-brand can't break even at 2.09 AUD" to profitable scale.

### 12.10 Creative volume and the pattern library

- **Volume:** each active ad group keeps a pre-approved bench of 40 headlines and 12 descriptions (passed §12.4 and MOE) and rotates one asset slot per feedback cycle; Shopping titles get 3 variants per product; landers 1 variant per cluster/stage/market. At full scale this means hundreds of live variants — generation is cheap; the gates and the feedback loop are the quality control ("LLM as judge").
- **Pattern library:** every creative is tagged (`creative_attributes`: angle, hook type, pain, proof type, offer, CTA, format, lander class, product, market). Posteriors are pooled per attribute value (`creative_patterns`), so at low volume the system learns "guarantee-led hooks beat spec-led hooks on PROBLEM_AWARE queries" long before any single ad has significance. After 30/60/90 days the library is the brand's proprietary answer to what works; R4 reads the top patterns as priors and the digest reports them monthly. Seeded from `ad_audit_archetype_weights` and the MemPalace `ads-creative-ops` wing.
- **One message spine:** a WINNER angle is propagated to every surface in the same market (Search, Shopping title, lander first screen, organic brief, Klaviyo flow suggestion to the email workflow) so the buyer meets one claim everywhere.

### 12.11 Winner loop and funnel cascade ("X works → X.1…X.5 → X.5 wins → rebuild the funnel around it")

**Theme and lineage.** Every idea is a *theme* X (an angle, hook, offer or proof — e.g. "100-day guarantee first"). Variants are numbered by lineage: X.1…X.5 each change **exactly one element** of the current champion (hook, proof, offer mention, CTA, first screen, image), recorded in `variants.changed_element`, so a win says *what* worked.

**Rounds.** A round = the champion + up to 4 challengers on one surface:

| Surface | How challengers run | Decision metric | Evidence floor per arm |
|---|---|---|---|
| Search ads | asset swaps / 2 challenger RSAs (3-RSA limit) | value per impression = CTR × engaged × ATC-proxy | 300 impressions |
| Landers | Google Ads experiment 50/50 on final URL | value per session (ATC-proxy, orders × V) | 100 sessions |
| Shopping titles | sequential, 14 d each | clicks per impression × value per session | 500 impressions |
| Offer (bundle, upsell, downsell) | lander/offer variant via experiment | revenue × margin per session (AOV-aware) | 100 sessions |
| Email (Klaviyo flow message) | flow A/B split | revenue per recipient | 200 recipients |

A challenger becomes champion when `P(challenger > champion) ≥ 0.8` on the decision metric at the evidence floor. The next round is generated from the new champion (X.5 → X.5.1…X.5.4). A theme whose last 3 rounds produced no new champion is **exhausted**: frozen, its budget share goes to the next theme, its lesson is written to the pattern library.

**Cascade.** When a theme's champion is confirmed — WINNER bucket plus ≥ 2 attributed orders, or pooled pattern `P ≥ 0.8` — the system opens cascade tickets in this order, each a test against its own control (nothing is assumed to transfer):

1. **Budget:** D19 +30%/7 d on the entities carrying it, inside the governor.
2. **Spread:** new ad groups for adjacent PROVEN queries using the champion angle.
3. **Landing page:** rebuild the lander's first screen and copy around the angle (Shopify Page variant, 50/50 experiment).
4. **Shopping:** feed titles in the champion's phrasing.
5. **Offer:** bundle, upsell or downsell built around the angle (e.g. filter + cartridge bundle when the "long-term savings" theme wins).
6. **Email:** Klaviyo welcome / abandoned-cart message variant carrying the angle.
7. **Organic and answer engines:** brief to the article pipeline.
8. **Markets:** localized version for the next market (§14.7).

**Authority per cascade step — all eight run on their own; Maestro holds veto and can alter anything after the fact:**

| Step | Mode | Bound (why) |
|---|---|---|
| 1 Budget | autonomous | inside the governor and ceiling |
| 2 Ad groups | autonomous | incubation envelope per ad group |
| 3 Landing page rebuild | autonomous (Shopify Pages; theme-file changes keep the theme-guard publish gate) | old version kept as control until the new one wins |
| 4 Shopping titles | autonomous | previous title restorable from column history |
| 5 Offer (bundle, upsell, downsell, discount) | autonomous once 90 days of clean `order_economics` exist (data gate, not approval); before that, built and shown, not switched live | via Shopify Admin API (discounts, bundles, whatever upsell mechanism UNIT 5.13 finds); base prices never changed; max discount depth lives in the owner-only cap file (`offer_max_discount`, default 0.20) — the system cannot raise it; margin check against the profit target |
| 6 Email | flow variants autonomous behind the same 90-day data gate (they only affect new entrants and switch off); **broadcasts never autonomous** — a sent email cannot be undone; the system drafts them for Maestro | the list has ≈ 3 profiles today, so the first email job is list capture (UNIT 1.17), not testing; complaint/unsubscribe guard pauses all autonomous email |
| 7 Organic content | autonomous via the existing article pipeline and its gates | — |
| 8 Markets | parked until store orders ≥ 50/month for 2 consecutive months; then autonomous where the store already sells and ships, and a ready packet for markets needing tax, shipping or a new Shopify Market | a new market multiplies a working funnel; it does not fix one that isn't working yet |

Every step lands in the ledger with an inverse operation and a veto handle; the digest reports it as done, not as a question.

**What Maestro sees** (weekly digest, "Winner board", ≤ 5 themes):

```
X "100 dagars garanti"  champ X.3
 X.3 +28% value/impr (P 0.86)
 ✓ budget +30%  ✓ 2 new AGs
 ⏳ lander test d9/21
 ✓ bundle offer live (test d3)
    /ads veto c-41
Y "hårt vatten" exhausted → Z
```
(Illustrative.) Every item has a veto handle; `/ads why <id>` shows the evidence.

### 12.12 Idea bank — start with 100, proven-first

On Stage 0 the system fills `themes` with **100 ideas** and keeps the bank at ≥ 100 as ideas are used up.

**Sources:** day-one lessons (§16.10), PROVEN/PROMISING queries and the pages that sell (§10.0), past ad-audit winners and ad-copy library angles, competitor weaknesses, ICP pain × product × angle combinations, answer-engine gaps.

**Ranking — proven-to-work first:**

| Evidence tier | Meaning | Examples |
|---|---|---|
| 1 MEASURED WIN | worked before in measured data | query/page with real orders; past ad or angle with top audit score and above-baseline CTR |
| 2 ORGANIC PROOF | sells organically, never tested in paid | PROVEN queries without an ad group |
| 3 PATTERN/COMPETITOR PROOF | pattern-library prior or visibly used by competitors that rank | guarantee-led hooks, comparison angles |
| 4 HYPOTHESIS | reasoned but untested | new pain × product combinations |

Within a tier: `EV = P(win) × upside`, where `P(win)` comes from the pattern library (§12.10) and `upside` = estimated extra orders/month × `C_new`.

**How many run at once:**
- **Free-traffic tests** (RSA asset swaps inside existing budgets, Klaviyo A/B on existing flow traffic, Shopping titles, organic briefs) run for as many themes as the rate limits and review gates allow — typically dozens.
- **Paid-slot tests** (new ad groups, lander experiments that need their own traffic): `floor(exploration budget ÷ envelope N)` slots — 2 at 15 AUD/day, ~13 at 100 AUD/day. The top-ranked themes take the slots; the rest queue.

The weekly digest shows the top 10 of the bank and what moved in or out.

### 12.13 Klaviyo: clone-and-vary

- **Access:** a private API key with `flows:write`, `templates:write`, `flows:read`, `metrics:read`, stored with `secrets set KLAVIYO_PRIVATE_API_KEY` (never pasted in chat). UNIT 5.12 first checks whether the existing `KLAVIYO_TOKEN` already has these scopes (N12).
- **Reference flows (one-time, built by hand in the Klaviyo UI):** welcome, abandoned cart, browse abandonment, post-purchase, cartridge replenishment. The API can't create a flow definition from nothing — it clones one that exists.
- **Varying:** `GET /api/flows/{id}?additional-fields[flow]=definition` → swap message content for HTML templates created via the Templates API (drag-and-drop templates are capped for API partners, so everything is HTML) → rename action ids to `temporary_id` → `POST /api/flows` → `PATCH` status `live` once the gates pass. Prefer an A/B split inside the cloned definition; otherwise run champion and challenger sequentially for 14 days each.
- **Limits built into the job:** flow create ≤ 15/min and ≤ 100/day, status updates ≤ 60/min; only this store's own account (Klaviyo discourages bulk pre-provisioning across accounts, which this is not).
- **Gates:** same claims gate, Swedish polish and MOE as ads; email-specific checks: unsubscribe link, sender identity, no fabricated reviews.
- **No CLI needed:** `klaviyo-pp-cli` isn't installed and the hosted Klaviyo MCP isn't authenticated; adsys calls the REST API directly from Python.

---

## 13. Funnel / Stage / ICP / Locale Matrix

### 13.1 Taxonomy (enums used everywhere)

| Dimension | Values |
|---|---|
| awareness | UNAWARE, PROBLEM_AWARE, SOLUTION_AWARE, PRODUCT_AWARE, MOST_AWARE |
| journey | RESEARCH, COMPARISON, CONSIDERATION, PURCHASE, RETENTION |
| intent | TRANSACTIONAL, INVESTIGATIONAL, INFORMATIONAL, NAV_BRAND, NAV_COMPETITOR, SUPPORT |
| pain_point | DRY_SKIN, ITCHY_SKIN, HARD_WATER, CHLORINE, HEAVY_METALS, HAIR_DAMAGE, ALLERGY, NONE |
| role | BRAND, NONBRAND, CONQUEST, SHOPPING, PMAX, DEMAND_GEN, VIDEO, HARVEST |
| lang | sv, en, fr |
| lander_class | PRODUCT, COMPARISON, PROBLEM, GUIDE, GEMPAGES, HOME, ARTICLE, COLLECTION |
| content class | EDUCATIONAL (TOF), INFORMATIONAL/COMPARISON (MOF), PURCHASE (BOF), RETENTION |

### 13.2 Stage → format, lander, CTA, metric

| awareness | Typical query (sv) | Ad angle | Lander class | CTA | Judged on (§6.7) |
|---|---|---|---|---|---|
| PROBLEM_AWARE | "torr hud efter duschen", "hårt vatten hud" | problem statement → cause → solution category | PROBLEM (e.g. `/pages/torr-hud-efter-duschen-duschfilter`, `/pages/hard-water-in-sweden`, `/pages/tungmetaller-i-duschvatten`) | "Läs varför" | engaged rate, ATC proxy, assisted CM, 30 d |
| SOLUTION_AWARE | "duschfilter", "duschhuvud med filter" | spec/proof, 100-day guarantee | PRODUCT or COMPARISON | "Se filtret" | CM + 0.5 × assisted, 21 d |
| COMPARISON (journey) | "duschfilter bäst i test", "jämför duschfilter" | differentiation vs competitor weaknesses (no trademarks) | COMPARISON `/pages/duschfilter-jamforelse-bast-i-test` | "Jämför" | as SOLUTION |
| PRODUCT_AWARE | "nordisk duschvattenfilter pris" | price, guarantee, shipping | PRODUCT | "Köp" | CM_ROAS 14 d |
| MOST_AWARE | brand, "ersättningspatron" | brand, reorder | PRODUCT / cartridge | "Beställ" | capture ratio, CM |

### 13.3 Pain → keyword → ad → lander → product

Rows in `ROOT/adsys/config/taxonomy.toml`, seeded from `nordisk-icp.md` (UNIT 2.6) and existing `nordisk_ads_context.json` buckets ("Hudproblem" → `/pages/itchy-skin`, "Klor & Vatten" → product page, "Guide / Jämför" → `/pages/se-4` → preferred alias comparison page). Default product routing: HARD_WATER/CHLORINE/HEAVY_METALS → Duschvattenfilter (KDF-55 + CaSO₃ + GAC) or Wellness Kit; DRY_SKIN/ITCHY_SKIN/HAIR_DAMAGE → Duschvattenfilter or Duschhuvud; claims for each strictly per `product_claims`.

### 13.4 Who fills it

| Asset | Filled by | When | Confidence rule |
|---|---|---|---|
| Keywords, search terms | RULE lexicon first (`taxonomy.toml` token lists), then R1 | on ingest | RULE = 1.0; R1 needs 2-model agreement ≥ 0.7 |
| Landers, content assets (23 articles, 50 sitemap pages) | R2 backfill, RULE for product pages | UNIT 2.7, then on new asset | R2 < 0.7 → `NEEDS_REVIEW`, excluded from routing |
| ICP segments, pains, VOC | R2 from `nordisk-icp.md` (no new research) | UNIT 2.6 | file hash recorded; re-tag on change |
| Ad groups | inherited from creating hypothesis; legacy ad groups by R2 | UNIT 2.2 | — |

---

## 14. Budget, Scaling & Exploration

### 14.1 Allocation (shares of current cap; 15 AUD/day at start)

| Pool | Share | AUD/day | Rule |
|---|---|---|---|
| Brand | ≤ 20% at 15 AUD, ≤ 10% above 30 AUD | ≤ max(3.00, 10% of cap) | D17 |
| Exploration (incubations, harvest) | ≤ 40%, protected (≥ 15% floor) | 6.00 at start | only D12/D13/D15; the optimiser cannot move it to performance |
| Performance (ACTIVE non-brand) | remainder | grows with the ramp | D08; unspent is not forced |

Budget-limited vs bid/rank-limited: `search_budget_lost_is ≥ 0.20` → budget action; `search_rank_lost_is ≥ 0.50` → CPC ceiling/QS/lander action, never budget. Both < thresholds → demand-limited → opportunity engine, not money.

### 14.2 Increments, cooldowns

Budget ±20%/−30% per step (§8.5 D08), min change 0.50 AUD, floor 1.50 AUD/day, one change per campaign per 7 d; CPC ceiling ±15% per 7 d. Smart-bidding learning periods are not relevant while on Maximize Clicks.

### 14.3 Entity lifecycle

`STAGED` (created paused, pre-flight) → `INCUBATING` (envelope, D15) → `ACTIVE` (performance pool, D05/D08/D16) → `SCALING` (Stage 2+, D19/D21) → `PAUSED_BY_SYSTEM`/`KILLED` (fail memory). Existing ENABLED non-brand campaigns are enrolled as `INCUBATING` at Stage 1 start with retroactive hypotheses, so they get exploration ceilings and pre-committed kill rules instead of breakeven ceilings they cannot yet meet.

### 14.4 Seasonality

Swedish winter (Nov–Mar) raises dry-skin demand: opportunity scoring uses planner monthly volumes (seasonal), and D08 compares against same-month planner seasonality index when judging budget-limited status. `bidding_seasonality_adjustments` apply only to smart bidding — not used while on Maximize Clicks.

### 14.5 Value-based bidding

Only when a campaign has ≥ 30 clean primary purchase conversions in 30 d (requires G-CONV-3 closed). At current volume this is not expected within 12 months; the system states that instead of switching early.

### 14.6 Scaling (Stage 2+: D19 entity scale, D21 account ramp)

D19 (+30%/7 d per proven entity) and D21 (current cap ×1.5/week inside the ceiling) as long as marginal returns hold the growth floor; ceiling raise only via Gate `CAP` with evidence packet (attributed orders, marginal CM_ROAS per step, bottleneck history). Trajectory if every step qualifies: 15 → 22.5 → 34 → 51 → 76 → 114 → 171 → 256 → 350 AUD/day. **This is the maximum speed, not a forecast** — each step requires profitability that may never be reached.

### 14.7 Market and channel expansion — localization, not translation

**Demand ceiling per market (monthly):** `Σ relevant keyword planner volume × CTR belief × CVR belief` + Shopping estimate. When the total-order target exceeds 70% of reachable demand in current markets, the digest carries a **market-entry packet**.

**Localization rule:** a new market gets pages and copy written from that market's own research — local water conditions, local competitors, local search language and VOC, local price and shipping expectations — using the `research` CLI and R6/R8. Translating the Swedish pages is not allowed as the market's primary lander; the claims gate (§12.4) and a native-language MOE panel apply per language. Winning *angles* travel (pattern library, per-market posteriors start from the source market with strength 50); wording does not.

**Market seed:** each new market gets a fixed seed budget inside the governor (default 1,000 AUD over 60 days) and a proof criterion (≥ 10 store orders from the market and paid `P(CM_ROAS ≥ floor) ≥ 0.6`). Proven → it joins the ramp; not proven → closed with a fail-memory entry and retry conditions.

| Step | Market / channel | Needs | Autonomy |
|---|---|---|---|
| 1 | Standard Shopping + free listings, Sweden | N2 | Stage 3 |
| 2 | Answer engines + organic briefs (§10.6) | none | Stage 0 monitoring, briefs from Stage 2 |
| 3 | English queries in the Nordics → `/en/` tree | EN landers pass checks | Stage 3 |
| 4 | Norway, Denmark, Finland | localized storefront (Shopify Markets), shipping, currency — business decision | packet → owner; system launches once localized landers exist and pass P-LANG |
| 5 | Germany, France/Belgium (`/fr/` exists) | as step 4 | as step 4 |
| 6 | PMax | ≥ 30 clean conversions/30 d | Stage 3 |
| 7 | YouTube / Demand Gen (PROBLEM_AWARE video) | N11 or owner footage | Stage 3 |
| 8 | Meta | N10 | outside this spec until access exists; likely required for T3 |

---

## 15. Self-Healing

Pattern (conforming to `harness-opt`): **observe → gate → heal → verify → log.** Probes in `ROOT/adsys/health/`; heal actions only through the executor or the existing gated credential-heal actor.

### 15.1 Failure surface

| Failure | Detect | Diagnose | Auto-repair (if safe) | Escalate |
|---|---|---|---|---|
| Ads OAuth refresh fails / revoked | auth probe every 30 min (§5.10); 2 consecutive fails | `gads-auth.py check` output class (`invalid_grant` = revoked vs network) | re-source `gads-env.sh`, one retry; hand to gated credential-heal actor | sev 1 Telegram: "Ads auth dead since HH:MM; system is observe-only; run `gads-auth.py url`, open link, send redirect back" (Gate `OAUTH`). All Ads-dependent outputs `BROKEN`; trust → 0 (restorable) |
| Ads refresh flaps (intermittent) | > 2 failures/24 h but recovers | — | retry with backoff | sev 3 digest line with failure count |
| Google Ads API version sunset | calendar entry per API version from Google's published sunset schedule; digest warning 60 days before; CLI upgrade + `gads_syntax.json` re-capture is a scheduled build task | — | — | sev 3 at 60 d, sev 2 at 14 d |
| API schema drift / 400 | `SCHEMA_DRIFT` class | stored `error.details` | none | sev 2, R3 explanation; affected tables `BROKEN` |
| Quota exhaustion | `RESOURCE_EXHAUSTED` | ops count in `run_ledger` | defer cold/warm tiers 24 h | sev 3; sev 2 if hot tier affected |
| Wrong customer ID / account identity | R8 | env vs API | none (abort) | sev 1 |
| Tracker down | hourly `curl` health of `/track/purchase` + `systemctl is-active nordisk-tracker` | journal tail | `systemctl restart nordisk-tracker` once/hour max, verify | sev 1 if down > 30 min |
| Pixel stopped firing | synthetic probe (§6.10) + R1 | probe vs webhook | none (pixel edit is a build task) | sev 1 after 2 days |
| GA4 forwarding dead | R2, MP status codes in `purchases.ga4_status` | 4xx/5xx pattern | none | sev 2 |
| Conversion action disabled/changed | R9 snapshot diff | change_event | none (gated) | sev 1, trust ≤ 1 |
| Ad disapproved / policy | snapshot `approval_status` | policy topics | pause ad (reversible), R4 regenerate without offending line | sev 3; sev 2 if all ads in an ad group |
| Lander 404/5xx/301 | lander checks (§11.6); CB-LANDER | status/location | pause affected ads; 301 → canonical swap | sev 2 |
| Lander perf regression | weekly `nrperf` −15 points or LCP > 4,000 ms | — | none | sev 3 |
| GMC feed rejection | `gmc_product_status` | issues | feed title edit if title-class issue | sev 2 if > 20% items |
| Stale warehouse table | coverage freshness per table | upstream `run_ledger` | re-run ingest once | sev 3 → sev 2 after 48 h |
| Disk full / high | `df` every 30 min: `/` ≥ 85% warn, ≥ 90% crit | largest dirs under `/tmp`, `TMP`, `ART` | delete Chrome profile dirs in `/tmp` older than 1 h matching `/tmp/*chrom*`, `/tmp/playwright*`; prune `ART` > retention | sev 2 at 90%; all browser jobs paused ≥ 92% |
| DKIM missing | infra doctor DNS check | — | none | digest footer until N6; Telegram primary |
| FX feed down | §5.9 | — | carry last rate `FX_ASSUMED` | sev 3; mutations blocked after 3 d |
| LLM provider down / budget | `llm_calls` status | — | fallback provider chain; then L off | sev 4 |
| Dispatcher not running | external dead-man (N4) + comb heartbeat check | — | — | Telegram from healthchecks.io / comb |
| **System's own outputs wrong** | §15.3 T-* tests, calibration (§16.5), digest number audit | — | freeze affected class | sev 2; demotion rules |

### 15.2 Circuit breakers (active from Stage 0; pause-only)

| Id | Trigger | Action | Reset | Who may reset |
|---|---|---|---|---|
| CB-SPEND-1 | today's Sydney-day spend ≥ 1.25 × cap before 18:00 Stockholm (hourly data) | pause all non-brand campaigns until Sydney midnight | automatic next Sydney day | system |
| CB-SPEND-2 | today ≥ 1.5 × cap, or 7-day spend ≥ 7 × cap | pause all campaigns incl. brand; HALT | owner `/ads resume` | owner |
| CB-TRACK | R1 match 0 with ≥ 2 Shopify web orders in 7 d, or E2E legs red 2 days | trust → 0 (no mutations except CB) | automatic after 3 green days, stage restored | system |
| CB-CPC | campaign 3-day CPC > 2.5 × trailing-28-d median with ≥ 10 clicks | ceiling → 1.2 × trailing median | after 7 d | system |
| CB-IMPR | ENABLED campaign 0 impressions for 3 days while trailing-14-d mean ≥ 3/day | no mutation; diagnosis tree: disapprovals → budget → billing (`customer.status`, billing setup) → bids below first-page → keyword "low search volume" status | resolves when impressions return | system |
| CB-LANDER | non-200 twice 10 min apart | pause ads on that URL | automatic when URL 200 for 2 checks + P-* pass → ads re-enabled | system |
| CB-GMC | > 20% items disapproved | pause Shopping campaigns | automatic when < 10% | system |
| CB-API | > 30% of API calls in a run fail | abort run, `BROKEN` | next run | system |
| CB-CAPFILE | cap file missing, unparseable or sha256 changed without an owner command record | HALT | owner `/ads cap <AUD>` | owner |

### 15.3 Health and synthetic self-test suite (daily 05:37 + on every deploy)

| Test | Proves |
|---|---|
| T-E2E-PIXEL, T-E2E-MP, T-E2E-UPLOAD | §6.10 legs alive |
| T-AUTH | Ads token valid, customer identity correct |
| T-BROKEN-INJECT | weekly: runs Ads ingest with `GOOGLE_ADS_ACCESS_TOKEN=invalid` in a sandbox DB copy; asserts coverage `BROKEN`, accessor returns `BROKEN`, digest renders `?` — the nine-week failure cannot recur silently |
| T-ZERO-SEMANTICS | fixture: complete coverage + eligible entity + no rows → `MEASURED_ZERO`; ineligible → `NO_DATA`; missing coverage → `BROKEN` |
| T-INT | cross-DB referential checks (actions ↔ decisions, ent_* ↔ snapshots) |
| T-PAUSED-LEAK | renders the digest from live data and asserts no `LEGACY_PAUSED` campaign name/id appears |
| T-CLAIM | weekly re-scan of all LIVE ads and adsys Pages against `banned_phrases` and `product_claims` |
| T-CURRENCY | every money column has non-null currency; SEK conversions recompute to stored values ± 0.01 |
| T-CAP | capguard refuses a synthetic over-cap budget request |
| T-HALT | executor refuses all non-CB actions when HALT exists |
| T-APPEND-ONLY | UPDATE/DELETE on ledger tables raise |

Results → `run_ledger` (job `selftest`) and the digest "Proof of life" block.

### 15.4 Watching the watcher

1. Dispatcher writes `ROOT/adsys/state/heartbeat` every tick; the harness-opt comb (hourly) alerts if older than 45 min.
2. The comb itself pings external dead-man N4 check "comb"; the dispatcher pings check "adsys". Box down → healthchecks.io alerts Telegram.
3. Daily heartbeat message 09:00; the weekly digest lists the last 7 heartbeat times — a missing day is visible to Maestro.

---

## 16. Self-Learning

### 16.1 Belief store

`beliefs`/`belief_history`/`value_beliefs` (§4.5), updated nightly (§8.2). Creative priors seeded from `ad_audit_archetype_weights` mapped to angle names; persona calibration tables stay the audit system's own.

### 16.2 Revision rules

Posteriors recompute from windowed evidence (28 d for rates in decisions, 180 d for `C_new`, all-time for refund/repeat). Evidence counted only from settled days and `MEASURED`/`MEASURED_ZERO` states. A belief whose evidence state is `BROKEN` keeps its last value, flagged `stale_since`.

### 16.3 Outcome → decision attribution

Each `ACT` decision stores `predicted_json` (e.g. D01: "term spend next 28 d = 0"; D08: "clicks +x ± y"; D12: hypothesis metrics). At `horizon_days` the `learn` job writes `outcomes` with verdict; at day 100 after each order (end of the refund window) every outcome that counted that order is **re-graded** with its final value and a new `outcomes` row is appended, so late refunds and chargebacks correct the system's record of its own judgement. Judgement-quality metrics (§20.4) are computed from these. Decisions whose realised effect is confounded by a concurrent change on the same entity within the horizon are `UNMEASURABLE` — the touch lock (G5) minimises this.

### 16.4 Memory of failure

Fingerprint = `sha1(role | awareness | pain_point | product | lander_path | match_type_set | theme_cluster_id)`. Retry conditions are machine-checkable JSON, e.g. `{"after":"2027-03-01"}`, `{"lander_changed":true}`, `{"price_changed":true}`, `{"planner_volume_ge":2.0}`, `{"cap_aud_ge":30}`. Seeded (UNIT 2.11) from legacy data: the historical investigative-search spend (294.88 AUD, 141 clicks, 0 conversions) and the EU English discovery spend (126.94 AUD, 43 clicks, 0 conversions) become `LOSER`/`MEASURED_BADLY` entries (attribution was broken then, so the verdict is "measured badly", retry after attribution proven) — mined, never surfaced by name.

### 16.5 Counterfactual lane and calibration

Every evaluated candidate is a `decisions` row (`counterfactual=1` when not executed). The `learn` job evaluates counterfactuals where observable: an un-negated term keeps spending (was the negation right?), a held budget stays budget-limited, a shadow-mode kill's entity later converts (false kill). Calibration: fraction of realised values inside predicted 80% intervals, per decision class, rolling 60 d. Target 70–90%; < 70% → halve k for the metric (over-confident prior); > 95% → intervals too wide, raise k by 25%.

### 16.6 Evidence discipline and experiments

- Valid learning evidence: settled, complete-coverage, no confounding change on the entity during the window, not overlapping an incident affecting the source.
- **E-01 Brand click-capture switchback (Stage 1):** 8 weeks, alternating weeks brand ON/OFF (OFF = campaign paused by experiment; named in digest as "Brand — holdout week, experiment E-01"). Metric: brand-query clicks total (GSC brand clicks + Ads brand clicks) and brand-path orders. Capture ratio = OFF-week organic brand clicks ÷ ON-week (paid + organic) brand clicks. Abort rule: Serper shows a competitor ad on the brand query during an OFF week → resume ON. Honest power note: at ≈ 34 paid brand clicks/30 d the click metric is readable (±~25%); the order metric is not and is reported as directional only.
- **Always-on control:** harvest ad group keeps 10% of exploration budget on broad discovery regardless of performance, so the account keeps sampling demand the policy would otherwise stop exploring.
- **Geo split:** not run until ≥ 60 non-brand purchases/quarter (below that, Swedish regional splits are pure noise).
- **Sequential swap** for lander tests (21 d per arm) and Google Ads experiments (50/50) for copy tests at Stage 2+ only when the ad group has ≥ 300 impressions/week.

### 16.7 Drift and decay

Weekly for ACTIVE entities: CTR and engaged rate of last 28 d vs previous 56 d, both as posteriors; `P(decline > 30%) ≥ 0.8` → classify: seasonal (planner month index moved same direction) / competitive (SERP competitor-ad count up, abs-top IS down) / fatigue (asset labels, same ads ≥ 90 days) / market (GSC category impressions down) / noise (none). Fatigue → D07; competitive → digest + CPC ceiling unchanged; seasonal → hold; market → opportunity re-scan.

### 16.8 Anti-thrash

G5 cooldowns, G6 reversal rule, hysteresis (kill at `P(profitable) < 0.10`, restore only at `> 0.40`), one budget change per week, and the decision engine never alternates between two states on the same entity more than twice in 90 d (third attempt → `ESCALATE` to digest).

### 16.9 Lesson write-back

`learn` writes each closed hypothesis and fail-memory entry to MemPalace (`mempalace-cli diary-write --wing ads` and `kg-add` triples like `Theme:torr-hud --tested_in--> AG:<id>`, `--verdict--> LANDER_MISMATCH`). R3/R6 read `mempalace-cli search` results at session start. MemPalace is a mirror for agents; `ADB` stays the system of record.

### 16.10 Day-one import of what is already known

Before Stage 0, UNIT 2.13 converts existing Google Ads knowledge into machine-usable form, so the system starts from past lessons instead of from zero:

| Source | Becomes |
|---|---|
| All 30 campaigns' history (search terms, keywords, ads, landers, spend, clicks — incl. legacy paused, mined only) | priors (§8.2), negatives, fail memory, PROVEN/PROMISING query evidence |
| `google-ads/historical-analysis.md`, `strategy.md`, `campaign-architecture-v2/v3.md`, `ops-operations.md` | lessons: rules, hypotheses, thresholds to recalibrate |
| `negatives.md`, `ad-copy-library.md`, `landing-page-inventory.md`, `campaigns/*.json`, `nordisk_ads_context.json` | vocab, creative seeds (tagged into the pattern library), lander registry, blueprints |
| `competitor-review-analysis.md`, `clearly-of-sweden-intel.md`, `swedish-market-research.md` | angles, differentiation claims (still gated by `product_claims`), conquest hypotheses |
| `ads_decisions.db` `ad_audit_*` tables, MemPalace `ads-creative-ops` wing and ads-monitor diary | creative pattern priors, winner/loser history |

**Anti-hallucination rule:** each lesson is stored with the exact source file and line/row it came from; a lesson with no source reference is rejected. Lessons backed by measured data become priors or rules; opinions and untested claims become *hypotheses* to test, never rules. Legacy data measured while tracking was broken is marked `MEASURED_BADLY` where it concerns conversions. At Stage 0 Maestro receives one short "What we already know" list (≤ 15 lines, strongest evidence first); `/ads veto L-<id>` removes a lesson.

---

## 17. Orchestration, Scheduling & Runtime

### 17.1 Substrate: cron + Python + SQLite (Temporal rejected)

The 100-day refund window is a **row with a due date** (`order_economics` recomputed daily until age 100), not a long-running process; durable state lives in SQLite with WAL, and every job is idempotent per window. Temporal would need a Postgres (nothing listening on 5433), a server and workers — on the order of 1–2 GB RAM and several GB disk on a root filesystem at 82% — to manage state that fits in one table. Condition that would reverse this: more than ~5 multi-step workflows needing cross-job compensation that the run ledger cannot express.

### 17.2 Dispatcher

Single cron entry (server crontab, like existing jobs):
```
*/10 * * * *  flock -n /mnt/HC_Volume_105587324/nordisk/adsys/state/tick.lock  /mnt/HC_Volume_105587324/nordisk/bin/adsys tick >> /mnt/HC_Volume_105587324/nordisk/cron/adsys/tick.log 2>&1
*/30 * * * *  flock -n /mnt/HC_Volume_105587324/nordisk/adsys/state/capguard.lock /mnt/HC_Volume_105587324/nordisk/bin/adsys capguard >> /mnt/HC_Volume_105587324/nordisk/cron/adsys/capguard.log 2>&1
```
`adsys tick` reads `ROOT/adsys/config/schedule.toml` (times in Europe/Stockholm), runs due jobs whose dependencies have an `OK`/`DEGRADED` `run_ledger` row for the same `window_key`, with per-job timeout. Capguard is deliberately a separate cron line and process.

### 17.3 Job set

| Job | Tier / cadence (Stockholm) | Depends on | Timeout | Failure semantics |
|---|---|---|---|---|
| `authprobe` | every 30 min | — | 2 min | incident per §15 |
| `capguard` | every 30 min (own cron) | A5 hourly pull inside | 5 min | `BROKEN` → pause non-brand if spend unknown > 6 h |
| `ingest.gads.hourly` | every 30 min, D0–D-1 campaign hourly | authprobe OK | 5 min | retry per §5 |
| `selftest` | 05:37 daily | — | 15 min | incidents |
| `ingest.fx` | 16:30 daily | — | 2 min | carry forward |
| `ingest.gads.hot` | 06:50 daily | authprobe | 20 min | retry ×3 |
| `ingest.ga4` | 06:55 | — | 10 min | retry ×3 |
| `ingest.shopify` | 07:00 (after existing run-all Shopify step) | — | 10 min | retry ×3 |
| `derive.attribution` + `derive.economics` | 07:10 | shopify, gads.hot, fx | 10 min | skip dep |
| `recon` | 07:20 | derive.* , ga4 | 10 min | incidents |
| `beliefs` | 07:30 | recon | 10 min | — |
| `classify` (R1) | 07:35 | gads.hot | 20 min | L-degrade |
| `decide` | 07:45 | beliefs, classify, landers | 10 min | — |
| `act` | 08:00 | decide | 20 min | per-action |
| `upload` | 08:10 | derive.attribution | 10 min | retry next day |
| `verify` | 08:30 and +24 h/+72 h follow-ups | act | 10 min | rollback |
| `digest.daily` | 09:00 | verify | 5 min | template fallback |
| `landers.active` | 06:40 daily (+ CB-LANDER check every 30 min for URLs in ENABLED ads) | — | 15 min | — |
| `ingest.gads.warm` | every 3rd day 05:00 | authprobe | 30 min | — |
| `ingest.gads.cold` + `planner` + `serp` | Sunday 04:30 | authprobe | 45 min | — |
| `opportunity` | Sunday 20:00 | cold | 30 min | — |
| `creative` | Monday 05:30 | opportunity | 45 min | — |
| `decide.weekly` (D08, D06, D16, D19, drift) | Monday 07:50 | beliefs | 15 min | — |
| `learn` | 22:00 daily | — | 20 min | — |
| `digest.weekly` | Monday 09:15 | decide.weekly | 10 min | — |
| `digest.monthly` | first Monday 09:30 | — | 10 min | — |
| `landers.all` + `gmc` | Wednesday 05:00 | — | 45 min | — |
| `retention` | Sunday 03:00 | — | 20 min | — |

Existing jobs: `run-all.sh` (06:07) keeps running; its Google Ads step is re-pointed to `adsys ingest gads --tier hot --legacy-only` (UNIT 0.5); `ads-monitor.sh` becomes a thin wrapper around `adsys report monitor` (UNIT 2.8); `weekly-ads-checkpoint.sh` is absorbed into `digest.weekly` and its cron removed after 2 green weeks (UNIT 0.11); `google-ads/pipeline/01–04.js` are superseded — 01 by `ingest`+`digest.daily`, 02 by D15/D16, 03 by D04/D05 + keyword registry, 04 by D08/capguard — and moved to `google-ads/pipeline/_superseded/` with a README pointing to the replacements (UNIT 3.6).

### 17.4 Idempotency

Ingest: `INSERT … ON CONFLICT(pk) DO UPDATE` per window (re-pull replaces). Derivations: recompute per window. Mutations: §9.1 idem key. Uploads: order id. Jobs: `(job, window_key)` with status `OK` is not rerun unless `--force`.

### 17.5 Freshness policy

Per-table max age (hot 2 d, warm 5 d, cold 10 d, GSC 3 d, GA4 3 d, Shopify 2 d, FX 3 d). Jobs assert input freshness at start and exit `STALE` (recorded, digest-visible) rather than computing.

### 17.6 Kill switch / read-only mode

- `/ads halt` (Telegram) or `touch ROOT/adsys/state/HALT` (shell) → executor refuses everything except CB pauses; decide keeps running in SHADOW; digest header "HALTED since …".
- `/ads halt revert` → additionally pauses every entity with lifecycle `INCUBATING` created in the last 21 days.
- `/ads resume` removes HALT (owner only).
- Without Telegram routing (N5), halt from a phone over SSH: `touch /mnt/HC_Volume_105587324/nordisk/adsys/state/HALT` — this line is also printed at the bottom of every weekly digest.

### 17.7 Run ledger schema

`run_ledger` (§4.5). Every job writes RUNNING at start and a terminal status; a RUNNING row older than 2 × timeout is marked `TIMEOUT` by the next tick and raises sev 3.

### 17.8 Operational cost

| Resource | Estimate | Basis |
|---|---|---|
| Google Ads API requests | ≈ 250/day (48 hourly pulls + capguard 48 + ~40 daily GAQL + ~20 read-backs + snapshots); mutations ≤ 40 ops/day | fits Explorer-level daily limits; confirm N9 |
| GA4 Data API | ≈ 10 reports/day | well under property quotas |
| Shopify API | ≈ 20 calls/day | — |
| Serper | ≈ 200 queries/month | negligible cost |
| LLM | ≈ 105k tokens/day; caps 400k/day, 3 USD/day, 45 USD/month | §7.4 |
| Disk growth (HC volumes, not `/`) | facts ≈ 60 MB/yr (hourly + search terms + snapshots), ledger ≈ 20 MB/yr, screenshots ≈ 40 MB rolling, LLM transcripts ≈ 200 MB rolling 90 d | all on `/mnt/HC_Volume_*`; `/` untouched |
| Cron load | +2 cron lines; ≈ 25 job runs/day; peak one headless Chromium (e2e/landers) at a time | lock-serialised |

### 17.9 Runtime vs harness (pi / hermes)

- **Runtime:** the `adsys` Python package, its cron lines and SQLite on the Hetzner box. It does not depend on any agent session being alive; LLM roles (§7) call Orcarouter/OpenRouter directly.
- **Harness (OWL on hermes, or pi):** builds the units in §21, receives sev 1–2 incidents as tasks (`adsys --agent incidents --open` is its entry point), and runs one-off investigations. If the harness is down, adsys keeps running and keeps reporting to Telegram; if adsys is down, the harness comb and the external dead-man switch report it (§15.4).
- **Harness-neutral interface:** everything the harness needs is `adsys --agent <command>` JSON plus the files in `ROOT/adsys/`; nothing is tied to hermes-specific or pi-specific tooling, so the builder can switch harness without changes.

---

## 18. Safety, Compliance & Guardrails

### 18.1 Constraint → enforcement point

| Constraint (brief §) | Enforcement (code) | Test |
|---|---|---|
| 4.1 Currency/timezone | `adsys/fx.py::to_sek()` requires explicit `(amount, currency, date)`; money columns NOT NULL currency; `tz.py` re-bucketing | T-CURRENCY |
| 4.2 URL 200 / https / canonical / descriptive | `preflight.P_URL200/P_HOST/P_PATH`; `lander_checks` timestamp ≤ 10 min | preflight_tests |
| 4.3 Language consistency | `P_LANG` from `<html lang>` | preflight_tests |
| 4.4 ≥ 20 negatives for broad | `P_NEG20` on create and daily audit of ENABLED broad campaigns (violation → CB pause of broad keywords at Stage ≥ 1, incident at Stage 0) | neg_floor_tests |
| 4.5 Lander relevance | `P_REL`; one-URL-for-all detector: > 1 ad group in a campaign sharing a lander with different stage tags → incident | preflight_tests |
| 4.6 Claims, specs, no fake quotes | `creative/claims_gate.py` against `product_claims`/`banned_phrases` | claims_gate_tests, T-CLAIM |
| 4.7 Paused campaigns never surfaced | `digest.py` filter `reportable=1`; `ent_campaign.reportable` computed only in `entities.py` | T-PAUSED-LEAK |
| 4.8 Theme guardrail | adsys has no code path writing theme assets; theme changes only via `theme_guard.py`; last step Gate `THEME_PUBLISH` | grep test `no_theme_writes_tests.py` (no `themes/` endpoints in adsys) |
| 4.9 Secrets | `adsys/secrets.py` reads env/`secrets get`; log redactor filter on all handlers; test greps logs for token patterns | secrets_tests |
| 4.10 UTM | `utm.py` + `P_UTM` | utm_tests |
| 4.11 Reversibility, ledger, dry-run, batch bound, no removal of conversion actions | executor §9.1; `REMOVE` operations disallowed except for negatives/links; conversion-action remove not in catalogue | executor_tests |
| 4.12 Truthfulness, three states, full result sets | `metrics.py`, coverage, pagination asserts (`nextPageToken` exhausted) | T-ZERO-SEMANTICS, T-BROKEN-INJECT |
| 4.13 Autonomy boundaries, gates | `trust.py` stage checks; `gates.py` for the five gates | trust_tests |
| 4.14 Operational | run ledger, freshness, idempotency, no `/dev/sdb` (paths validated against allow-list of mount points) | ops_tests |

**§4.7 interpretation (Q7, confirmed by the reviewers; owner to confirm):** only entities **adsys itself created** may be named in the digest, for 14 days after adsys pauses them, so it can report its own kills. If adsys pauses a legacy or human-created entity, the digest reports the hypothesis id, class and reason — never the entity name. Legacy paused campaigns are never named. E-01 OFF weeks are reported as experiment state, not as a paused campaign.

### 18.2 Cap layer the optimiser cannot override

- Cap file `/root/.nordisk/guard/ads_cap.json` (mode 600): `{"max_spend_to_revenue":0.35,"profit_target":0.15,"offer_max_discount":0.20,"ceiling_aud_per_day":350.0,"current_aud_per_day":15.0,"growth_floor":1.0,"learning_budget_aud":1200,"set_by":"owner|d21","set_at":"…","ref":"cmd_id|decision_id"}`. `max_spend_to_revenue`, `ceiling_*`, `growth_floor`, `learning_budget_aud` are written only by `adsys owner-cmd`; capguard recomputes the governor daily from Shopify revenue and monthly from the margin ratio (if Shopify coverage is BROKEN, the governor uses the last good value × 0.8 and non-brand budgets cannot increase); `current_aud_per_day` only by capguard executing a D21 decision, and capguard refuses any value above the ceiling or any step > ×1.5 or within 7 days of the last. Every write's sha256 is recorded in `capguard_log`.
- `adsys capguard` (separate process): every 30 min reads cap file + hourly spend + current budgets; states OK/WARN/TRIP; TRIP executes CB-SPEND-1/2 via its own minimal pause path (status updates only).
- Executor calls `capguard.check(delta_budget_aud)` (pure function over the same file and DB) before any spend-increasing action; the policy engine has no write access to the cap file (lint test: only `owner_cmd.py` opens it for writing).

### 18.3 Trust ladder

| Stage | Unlocks | Promotion test (automatic, all must hold) | Min days |
|---|---|---|---|
| 0 Observe | CB pauses only | 10 consecutive days: all selftests green on ≥ 9; R1, R2, R8, R9 in tolerance; ≥ 40 shadow forecasts with 80%-interval coverage 70–90%; UNIT 1.12 consent check green | 10 |
| 1 Reversible | D01–D03, D05, D08, D09, D10, D11a–c, D15 (on enrolled campaigns), D16, D17, E-01 | ≥ 14 d at Stage 1; ≥ 15 executed actions; 0 guardrail breaches; 0 read-back mismatches; 0 negated terms later found in any purchase path | 14 |
| 2 Build | + D04, D06, D07, D11d, D12, D14, D19, **D21 ramp**, creative pipeline | ≥ 21 d at Stage 2; ≥ 2 adsys-created ad groups whose clicks are resolvable end to end; ≥ 1 incubation closed with a verdict; creative disapproval rate ≤ 1/20 | 21 |
| 3 Launch | + D13 (Search, Shopping, market steps 1–3, PMax, Demand Gen), D18 | ≥ 42 d at Stage 3; ≥ 1 launched entity graduated and ≥ 1 auto-killed per rule; ≥ 10 paid orders attributed in the last 42 settled days; paid `P(CM_ROAS ≥ growth_floor) ≥ 0.7` | 42 |
| 4 Scale | + D20, ceiling-raise proposals with evidence, market-entry packets step 4 | — | — |

Promotion is announced in the digest, not requested.

### 18.4 Demotion triggers (automatic, announced)

| Trigger | Result | Restore |
|---|---|---|
| Guardrail breach (any §18.1 test fails in prod) | −1 stage, 7-d freeze | re-earn |
| Read-back mismatch not auto-rolled-back | −1 stage | re-earn |
| Tracking broken (CB-TRACK) or auth dead | → Stage 0 | automatic to prior stage after 3 green days (external cause) |
| Spend anomaly (CB-SPEND-2) | → Stage 0 + HALT | owner resume, then re-earn from Stage 1 |
| Mis-attribution: R4 breach > 72 h after G-CONV-3 | → max Stage 1 | re-earn |
| Creative claim violation found live (T-CLAIM) | creative classes off, → max Stage 1 | re-earn |
| Calibration < 50% coverage for 30 d | → max Stage 1 | re-earn |

### 18.5 Notify-vs-block matrix

| Class | Mode |
|---|---|
| All D-classes within the current stage, and all 8 cascade steps (§12.11) | autonomous-notify (daily count, weekly detail); owner veto/alter after the fact |
| CB pauses, kills, rollbacks | autonomous-notify (immediate Telegram line if CB-SPEND/CB-TRACK) |
| Cap raise | **block** (Gate CAP) |
| Conversion goals / attribution / value rules | **block** (Gate CONV_GOALS) |
| Irreversible Google-side (remove conversion action, hard-delete) | **block**, and adsys never proposes them except removing adsys-created negatives/links |
| OAuth re-consent | **block** (human-only) |
| Live theme publish | **block** (Gate THEME_PUBLISH) |

### 18.6 Self-kill conditions (→ HALT + Telegram sev 1)

- CB-SPEND-2.
- Tracking broken > 48 h while any non-brand campaign is ENABLED (after pausing non-brand).
- Learning budget 100% consumed (1,200 AUD unrecovered) — HALT of non-brand; brand continues.
- Three demotions within 30 days.
- Cap file tampering (CB-CAPFILE).

---

## 19. Owner Interface

### 19.1 Channels

Telegram (primary, via Hermes gateway, N5); email via `weekly-email.py` only after DKIM (N6). All messages under 4,096 chars; monospace blocks for tables; Unicode box tables ≤ 36 characters wide.

### 19.2 Messages

| Message | When | Content |
|---|---|---|
| Heartbeat | daily 09:00 | stage, health, spend yesterday, actions count, open sev ≤ 2 incidents |
| Weekly digest | Monday 09:15 | full format below |
| Monthly | first Monday | 28-d vs previous, experiments, learning-budget, stage history, honest-limits section |
| Incident | on sev 1–2 | what broke, since when, what it did about it, what (if anything) he must do |
| Gate | on creation + weekly reminder | one blocking decision with default |

### 19.3 Commands (from Maestro's chat_id only; anything else rejected and logged)

```
/ads status                       current stage, health, cap, HALT state
/ads halt [revert]                stop mutations (and pause recent incubations)
/ads resume
/ads cap <AUD>                    set the ceiling (current cap ramps inside it)
/ads floor <x>                    set growth floor CM_ROAS (default 1.0)
/ads profit <x>                   set profit share to keep after ads (default 0.15; governor derives from it)
/ads invest <r> <days>            time-boxed higher spend ratio (≤ 0.60, ≤ 60 days)
/ads target <n>/<month|week|day>  set the order target
/ads learnbudget <AUD>
/ads veto <action_id|launch_id>   execute inverse op(s); mark VETOED; fail-memory entry verdict HUMAN
/ads why <action_id>              rationale, evidence, posterior, prediction
/ads approve <gate_id>  |  /ads deny <gate_id>
/ads stage <0-4>                  cap the stage (owner may lower; raising above earned stage is ignored)
/ads strategy <free text>         R3 turns it into a structured config diff; shown back; applied after 12 h unless /ads deny <diff_id> (silence = proceed); safety/cap fields cannot be changed this way
```
Parsing is regex-based (`^/ads (status|halt|…)`), not LLM.

### 19.4 Weekly digest format (Telegram)

```
NORDISK ADS · v39 · 2026-09-28
Stage 1 Reversible · HEALTH ✅
Proof of life: pixel 05:38 ✅
 MP 05:52 ✅ upload 05:39 ✅
┌───────────┬─────────┬────────┐
│ 7d settled│   AUD   │  SEK   │
├───────────┼─────────┼────────┤
│ Spend     │   98.40 │ 619.92 │
│ Non-brand │   72.10 │ 454.23 │
│ Brand     │   26.30 │ 165.69 │
│ NB contrib│       – │ 512.00 │
│ NB net    │       – │  57.77 │
└───────────┴─────────┴────────┘
GOAL 100 orders/mo: 37 (28d)
 paid 14 · org 17 · AI 2 · mail 4
MER 4.1 · governor 58 AUD/d
 bottleneck SPEND → cap 34→51
CREATIVE: 9 reviewed · 2 win
 3 iterate · 4 graveyard
CONQUEST: 41% proven queries
 own ≥2 surfaces · AI cited 3/30
NB CM-ROAS 1.13 (80%: 0.4–2.9)
 based on 2 orders → not yet
 meaningful (need ~6)
DID (autonomous):
 • 31 negatives (27 vocab, 4 AI)
 • paused 2 keywords [a91,a92]
 • killed AG "hårt vatten" —
   FUNNEL_DEAD, 61 AUD  [/veto l7]
 • incubating AG "klåda dusch"
   day 9/21 · 18 AUD · floor ok
LEARNED:
 • PROBLEM landers: engaged 41%
   vs PRODUCT 58% (n=140)
BROKEN/UNKNOWN: none
DECIDE (blocking):
 G-CONV-1 demote 3 conv actions
 default: no change · /ads approve
FX 1 AUD=6.30 SEK (ECB 09-26)
```
(All figures illustrative.) Every line with an action carries its rollback handle; any `BROKEN` measure prints `?` with the incident id.

### 19.5 Audit trail locations

`ADB.decisions`, `actions`, `action_events`, `outcomes`, `incidents`, `gate_requests`, `owner_commands`; `adsys report ledger --since 7d --agent` prints JSON; MemPalace wing `ads` mirrors lessons.

---

## 20. Evaluation Harness

### 20.1 Baseline (UNIT 1.10 recomputes from `segments.date`; the brief's figures are the claim to verify)

| Metric | Brief figure (30 d to 2026-09-23) | Note |
|---|---|---|
| ENABLED campaigns | impressions 178, clicks 39, cost 48.24 AUD (≈ 303.91 SEK), conversions 0.61 | brand 90/34/38.45/0.61; broad 88/5/9.79/0; conquest 0/0/0/0 |
| All campaigns incl. legacy paused rows | clicks 223, cost 470.06 AUD | the brief's §9 P1 cites "34 clicks in 30 days" and §2 cites "a few hundred AUD to date" — inconsistent with 470.06 AUD in one window; UNIT 1.10 resolves which window the table used (Q5) |
| Attributed non-brand orders | 0 known | tracker had no click ids |
| Contribution margin | not computable yet | UNIT 1.5 |

### 20.2 Guard metrics (must not degrade; breach = incident + demotion rules)

Tracking integrity (R1 ≥ 0.90, E2E legs green ≥ 13/14 days), active-lander 200 rate = 100% (any non-200 → CB), policy disapproval rate ≤ 1/20 live ads, cap adherence 100% (7-d rule), currency correctness (T-CURRENCY 100%), paused-campaign leakage 0, secrets leakage 0, selftest pass 100%.

### 20.3 Success metrics

**Headline:** total store orders per month vs the active target (T1/T2/T3), MER, bottleneck class (§3.7), current cap vs governor vs ceiling. **Conquest KPIs:** share of PROVEN queries with ≥ 2 surfaces owned, answer-engine citation rate, share of search vs the 12 competitors, spend-weighted QS ≥ 7 share, creative win rate (winners ÷ reviewed) and iteration success rate, pages shipped per week. Then: Non-brand Net_sek (28 d), non-brand CM_ROAS with interval, new-customer CPA (SEK), count of profitable keywords/ad groups (`P(profitable) ≥ 0.6`), share of non-brand spend on terms classified RELEVANT (target ≥ 85%), budget utilisation per pool (reported, not targeted), time-to-detect breakage (target ≤ 60 min for auth/tracker/spend, ≤ 24 h for reconciliation).

### 20.4 Judgement quality

Per class: prediction interval coverage (70–90%); verdict mix of outcomes (CONFIRMED/REFUTED); D01 precision (share of negated terms not later found in a purchase path; target ≥ 98%); kill precision (killed entities later re-tested and graduating; target ≤ 1 in 5); diagnosis precision of R3 (hypothesis confirmed by the deterministic check it proposed; tracked, no target until 20 incidents).

### 20.5 Review cadence

Daily automated (selftest, recon, heartbeat); weekly human (digest read, 5 min); monthly strategic (monthly digest; cap/learning-budget/strategy commands).

### 20.6 Statistical honesty statement (printed in every monthly digest, recomputed)

| Comparison | Meaningful when | At current volume |
|---|---|---|
| Account non-brand CM_ROAS ± 50% | ≈ 6 attributed purchases in window | months away |
| Ad-group CVR vs account | ≈ 200 clicks per ad group | rarely |
| RSA CTR A/B | ≈ 1,000 impressions per RSA | ~1 year for brand |
| Device/geo/daypart | ≥ 300 clicks and ≥ 5 purchases per segment | not within 12 months |
| Brand incrementality (clicks) | 8-week switchback | readable at ±25% |
| Page/CRO test on all traffic (≈ 2,600 sessions/month, 0.34% CVR) | ≈ 2× lift readable in ~2 months; +30% needs ≈ 53,000 sessions per arm; +20% ≈ 117,000 | only large changes are measurable — test big swings |
| Order-based comparisons of any kind | ≥ 30 orders per arm | not within the current year at 9/month |

The system computes "date at which this becomes meaningful" by projecting the trailing-28-d event rate.

### 20.7 Kill criterion for the system itself

**Cost of ownership (published in the monthly digest):** build ≈ 71 units ≈ 100 Builder-days at S = 0.5 / M = 1.5 / L = 4 days (Phases 0–1 ≈ 29 days); run cost ≤ 45 USD/month LLM + Serper and healthchecks at ≈ 0; upkeep: OWL (hermes) is the maintainer of record, Maestro ≈ 5 min/week. Switched off (brand-only maintenance) if system cost exceeds the incremental contribution it can show over two consecutive quarters. Also off if: Turn adsys off (owner decision, recommended by the digest) if any: two consecutive quarters of non-brand Net_sek below −(learning budget)/2 with no graduating entity; guard-metric breaches in 3 of 4 consecutive weeks; judgement-quality coverage < 50% for 60 days. Turning off = HALT + brand-only maintenance mode, which still reports truthfully.

---

## 21. Phased Build Plan

**Funding gates (both reviewers' recommendation, adopted):** Phases 0, 1 and 1b are funded now. Phase 2–4 start when Phase 1 exits. Phases 5–7 start only when store orders reach **≥ 30/month for 2 consecutive months** *and* the phase before shows a measured contribution improvement — not on the calendar.

**Phase 1 go/no-go (decision tree, computed from real per-product `C_new` in UNIT 1.5):** for each product, break-even CPC = expected paid conversion × `C_new`. If break-even CPC ≥ the planner's low top-of-page bid for its comparison/product queries → GO non-brand for that product. If it holds only for Wellness Kit / Full Home Filtration → non-brand routes only to those. If it holds for none → no non-brand paid; all effort goes to conversion rate and organic until it does.

Rules for the Builder: every unit lands with its test in `ROOT/adsys/tests/<name>_tests.py` wired into `run_guard_tests.sh`; every schema change is a numbered migration in `ROOT/adsys/migrations/`; every job writes `run_ledger`. Backups of any existing DB file before its first migration: `sqlite3 <db> ".backup <db>.pre-adsys-<date>"` onto the same HC volume.

### Phase 0 — Repair the lies
- **Goal:** every measurement input is either correct or loudly `BROKEN`. **Why first:** nothing above can be trusted on a lie. **Exit:** 7 consecutive days with `COMPLETE` coverage for hot Ads tables; T-BROKEN-INJECT and T-ZERO-SEMANTICS pass; ads-monitor budget query returns data; Composio removed from the Ads path; G-CONV-1 sent. **Deferred:** attribution joins, all decisions. **Effort:** ≈ 2 weeks. **Money:** none.

```
UNIT 0.1  adsys skeleton + gads wrapper
Purpose:        One package, one CLI, one place that talks to google-ads-pp-cli.
Files:          ROOT/adsys/{__init__,__main__,config,db,gads,secrets,log}.py; ROOT/bin/adsys; ROOT/adsys/config/{paths,adsys,schedule}.toml; ROOT/adsys/gads_syntax.json
Depends on:     —
Interface:      in: GAQL string / operation JSON; out: {rows, request_id} or GadsError(class, details)
Implementation: - resolve ADB/FDB paths (find, excluding /dev/sdb mounts) and pin in paths.toml
                - gads.py sources gads-env.sh in a subshell, runs "$GADS_CLI --agent …", parses JSON, maps errors to AUTH/TRANSIENT/SCHEMA/PARSE
                - record `--help` of every mutate family + keyword-planning/upload services into gads_syntax.json
                - log redactor for token-like strings; TMPDIR=TMP for all subprocesses
                - `adsys --agent <cmd>` JSON output convention
Test:           adsys/tests/gads_wrapper_tests.py (mocked CLI: each error class; live: SELECT customer.id FROM customer returns 8479789152)
Acceptance:     `adsys --agent gads-ping` prints {"customer_id":"8479789152","currency":"AUD","time_zone":"Australia/Sydney"}
Rollback:       delete ROOT/adsys, ROOT/bin/adsys (nothing else depends yet)
Est. effort:    M
```
```
UNIT 0.2  Measurement-state core (coverage + accessor + lint)
Purpose:        Make zero-vs-unknown conflation structurally impossible.
Files:          ROOT/adsys/migrations/ndb_001_facts.sql (fact_coverage, fx_rates only here); ROOT/adsys/metrics.py; ROOT/adsys/tests/{zero_semantics,no_raw_fact_reads}_tests.py
Depends on:     0.1
Interface:      metrics.get(metric, entity, window) -> Measure(value, state, run_ids)
Implementation: - coverage writer used by every ingest (context manager: writes BROKEN on exception)
                - state logic per §4.4 incl. eligibility from gads_entity_snapshot
                - Measure type; digest/decision code accepts Measure only
                - AST lint forbidding raw fact SELECTs outside metrics.py/ingest/
Test:           python3 -m pytest adsys/tests/zero_semantics_tests.py adsys/tests/no_raw_fact_reads_tests.py
Acceptance:     fixtures yield MEASURED_ZERO / NO_DATA / BROKEN exactly as §4.4
Rollback:       drop tables fact_coverage (new, empty of dependants)
Est. effort:    M
```
```
UNIT 0.3  Fix ads-monitor campaign-health query
Purpose:        Close brief §5.1.
Files:          bin/harvesters/ads-monitor.sh; ROOT/adsys/ingest/gaql/{campaigns,budgets}.sql
Depends on:     0.1
Interface:      out: campaign health incl. budget amount in ads-monitor log + MemPalace diary (unchanged destinations)
Implementation: - capture the current 400's full error.details into the log first (the brief attributes it to selecting campaign_budget fields FROM campaign; record the actual errorCode)
                - replace with A2 + A3 two-query form joined on campaign.campaign_budget
                - on any error: exit non-zero and write "UNKNOWN" (never "no spend")
Test:           bash bin/harvesters/ads-monitor.sh --dry-run | grep -q 'budget_aud='
Acceptance:     one scheduled run shows budget amounts for the 3 ENABLED campaigns
Rollback:       git checkout of ads-monitor.sh (backup copy .pre-adsys)
Est. effort:    S
```
```
UNIT 0.4  Auth probe + token-death escalation
Purpose:        Detect Ads auth death within 60 min; never report zeros from it.
Files:          ROOT/adsys/health/authprobe.py; ROOT/adsys/state/auth_gads.json; migrations/adb_001_control.sql (incidents, run_ledger only)
Depends on:     0.1, 0.2
Interface:      out: auth_gads.json, incidents, Telegram sev-1 message
Implementation: - gads-auth.py check + minimal GAQL; classify invalid_grant vs network
                - 2 consecutive failures → incident AUTH_GADS + Telegram with re-auth steps (url/finish)
                - all ingest jobs read auth_gads.json first and write BROKEN coverage if dead
                - hand transient failures to the existing gated credential-heal actor (no bypass)
Test:           adsys/tests/authprobe_tests.py (mock invalid_grant → incident + BROKEN coverage)
Acceptance:     probe runs every 30 min for 48 h with run_ledger rows; simulated failure produces one Telegram message
Rollback:       remove cron line
Est. effort:    S
```
```
UNIT 0.5  Replace Composio Ads harvester
Purpose:        Daily Ads harvest without Composio; keep ads_campaigns consumers alive.
Files:          bin/harvesters/google-ads.sh; ROOT/adsys/ingest/legacy_ads_campaigns.py
Depends on:     0.1, 0.2
Interface:      out: ads_campaigns rows (same schema) from A6
Implementation: - google-ads.sh → `adsys ingest gads --tier hot --legacy-only`
                - write LAST_30_DAYS aggregate rows exactly as ingest-ads.py did (column parity test)
                - remove any composio call from the Ads path
Test:           adsys/tests/legacy_parity_tests.py (compare against a refresh-ads-data.sh run on same day, ±0.01 AUD)
Acceptance:     run-all.sh 06:07 log shows Google Ads step OK for 3 days
Rollback:       restore google-ads.sh.pre-adsys
Est. effort:    S
```
```
UNIT 0.6  Multi-grain Ads ingestion
Purpose:        Close brief §5.4 (ad group/ad/keyword/search term/geo/device/hourly/assets/IS/QS/conv-by-action/change events/click view).
Files:          ROOT/adsys/ingest/gads.py; ROOT/adsys/ingest/gaql/*.sql (A1–A15); ndb_001_facts.sql (gads_* tables)
Depends on:     0.2, 0.4
Interface:      out: gads_* tables + coverage per day
Implementation: - tiered windows per §5.1; pagination until nextPageToken empty (assert)
                - cross-grain completeness assertions → PARTIAL
                - identity assertion (id/currency/tz) before any write
                - 90-day backfill once (click_view single-day loop; search terms 365 d if API allows)
                - hourly job for A5 (feeds capguard later)
Test:           adsys/tests/gads_ingest_tests.py (fixtures) + live: `adsys --agent coverage --table gads_keyword_daily --days 7` all COMPLETE
Acceptance:     7 consecutive days COMPLETE for hot tables; Σ ad-group cost = campaign cost
Rollback:       disable jobs in schedule.toml; tables are additive
Est. effort:    L
```
```
UNIT 0.7  Shopify line items, refunds, order ext, inventory; token to secrets
Purpose:        Close brief §5.11 and the hardcoded-token defect.
Files:          ROOT/adsys/ingest/shopify.py; bin/resync-orders.py (token read change only); /root/.secrets.env (SHOPIFY_ADMIN_TOKEN)
Depends on:     0.2
Interface:      out: shop_line_items, shop_refunds, shop_order_ext, shop_inventory_snapshot
Implementation: - move token: add to secrets, replace literal in harvest script with env read; rotate token (it has been in a script file)
                - REST pull per §5.3, full backfill once
                - total reconciliation per order (R7)
                - draft/test flags carried
Test:           adsys/tests/shopify_ingest_tests.py; live: every order in `orders` has ≥1 line item row
Acceptance:     111+ orders covered; 0 R7 failures or each failure has an incident
Rollback:       tables additive; restore resync-orders.py.pre-adsys (token then still in secrets)
Est. effort:    M
```
```
UNIT 0.8  GA4 ingestion with currency metadata
Purpose:        First GA4 tables in NDB (brief §3.4 gap).
Files:          /root/.nordisk/scripts/ga4-read.py (add --json, backward compatible); ROOT/adsys/ingest/ga4.py
Depends on:     0.2
Interface:      out: ga4_daily_* , ga4_transactions with currency from metadata
Implementation: - --json returns rows + metadata.currencyCode + sampling/dataLoss flags
                - five reports per §5.2, 5-day rolling window, settle at D+2
                - strip click ids from landing page strings
Test:           adsys/tests/ga4_ingest_tests.py; live: ga4_daily_channel has 7 days COMPLETE and currency not NULL
Acceptance:     property currency recorded (answers why item revenue 473.07 ≠ SEK prices)
Rollback:       ga4-read.py.pre-adsys; tables additive
Est. effort:    M
```
```
UNIT 0.9  Conversion-action audit + Gate G-CONV-1
Purpose:        Stop four mixed primaries; blocking gate per §4.13.
Files:          ROOT/adsys/gates.py; ROOT/adsys/reports/conv_audit.py; migrations adb_001 (gate_requests)
Depends on:     0.6
Interface:      out: audit report (JSON) + Telegram gate message
Implementation: - read conversion_action snapshot + gads_conv_action_daily (which action produced the 0.61 and the 27.53 AUD value)
                - gate payload: exact field changes for 6882963286/…292/…745 → secondary, rename …286
                - on /ads approve: executor applies with validate-only first, read-back, R9 baseline stored
                - weekly reminder while PENDING; silence = no change
Test:           adsys/tests/gates_tests.py (approve/deny/expire paths with mocked executor)
Acceptance:     gate delivered; if approved, snapshot shows single primary 6878142622
Rollback:       inverse op restores primary flags and name
Est. effort:    S
```
```
UNIT 0.10 GA4 paid→transaction join diagnosis
Purpose:        Establish why paid transactions are 0 (brief §5.5) before building on it.
Files:          ROOT/adsys/reports/ga4_join_diag.py; docs ROOT/adsys/docs/ga4-join-diagnosis.md
Depends on:     0.8
Interface:      out: diagnosis doc with evidence per step of §6.11
Implementation: - compare purchases.client_id format with _ga format
                - GA4 transactions by sessionSourceMedium for tracker transaction ids
                - detect duplicate client-side purchase events by transaction id
                - determine what purchases.transaction_id contains (order id vs name vs checkout token)
Test:           script exits 0 and doc contains a verdict line `VERDICT: <cause>|UNRESOLVED`
Acceptance:     verdict recorded; feeds UNIT 1.3 design choices
Rollback:       n/a (read-only)
Est. effort:    S
```
```
UNIT 0.11 Absorb weekly checkpoint (fail loudly)
Purpose:        Close brief §5.7.
Files:          bin/weekly-ads-checkpoint.sh (wrapper → `adsys report checkpoint`); ROOT/adsys/reports/checkpoint.py
Depends on:     0.2, 0.6
Interface:      out: cron/ads-weekly-checkpoint.json with Measure states
Implementation: - every number emitted with state; any BROKEN → JSON "status":"BROKEN" and non-zero exit
                - no prose "normal for low traffic" strings anywhere (lint)
Test:           adsys/tests/checkpoint_tests.py incl. revoked-token fixture → status BROKEN
Acceptance:     2 consecutive Mondays green, then legacy cron removed (digest.weekly supersedes)
Rollback:       restore .pre-adsys script
Est. effort:    S
```
```
UNIT 0.12 Disk and temp hygiene
Purpose:        Keep / below 85%; stop Chrome profiles eating /tmp.
Files:          ROOT/adsys/health/disk.py; TMP and ART directories
Depends on:     0.1
Interface:      out: incidents; deletions logged
Implementation: - df check every 30 min; thresholds §15.1
                - delete /tmp chrome/playwright profile dirs older than 1 h (pattern allow-list only)
                - create TMP/ART on /mnt/HC_Volume_105573741; export TMPDIR for adsys and nr* calls
Test:           adsys/tests/disk_tests.py (fixture dirs; never touches paths outside allow-list; never /dev/sdb)
Acceptance:     / usage not increased by adsys over 7 days
Rollback:       remove job
Est. effort:    S
```
```
UNIT 0.13 Account settings audit (read-only) + constraint remediations by Builder
Purpose:        Find live violations of §4 now.
Files:          ROOT/adsys/reports/settings_audit.py
Depends on:     0.6
Interface:      out: audit JSON + Telegram summary
Implementation: - per ENABLED campaign: geo target type PRESENCE, networks (no display/partners), final_url_suffix vs ops-operations scheme, auto-tagging, effective negatives count (P-NEG20 for broad), language criteria, bidding strategy, recommendation auto-apply subscriptions
                - lander checks for all ENABLED final URLs (canonical host resolved: fetch nordiskrenhet.se and nordiskrenhet.com, record which returns 200 without redirect → config canonical_host)
                - violations listed; Builder (supervised OWL session) remediates reversible ones: attach ≥20-negative shared list to the broad campaign, set PRESENCE, turn off auto-apply subscriptions
Test:           audit runs; each remediation verified by re-running audit
Acceptance:     audit shows 0 open violations or each has an incident with owner-visible reason
Rollback:       inverse of each remediation stored in ledger
Est. effort:    M
```

### Phase 1 — Measurement first
- **Goal:** prove click → order → Ads/GA4 end to end and compute contribution. **Why now:** decisions need a true objective. **Exit:** R1 ≥ 0.90 and R2 ≥ 0.85 for 14 days; E2E legs green 13/14 days; `order_economics` covers ≥ 95% of web orders with non-MISSING COGS; baseline report written; G-CONV-2 action exists; consent check green. **Deferred:** decisions. **Effort:** ≈ 3 weeks + 14 days proof. **Money:** none.

```
UNIT 1.1  FX ingestion
Purpose:        Daily ECB rates; every money fact convertible.
Files:          ROOT/adsys/ingest/fx.py; ROOT/adsys/fx.py
Depends on:     0.2
Interface:      out: fx_rates; fx.to_sek(amount, ccy, date)
Implementation: - ECB daily XML + 90-day history backfill; cross rates AUD/USD→SEK
                - FX_ASSUMED carry-forward with is_assumed=1
Test:           adsys/tests/fx_tests.py (cross-rate math; weekend carry)
Acceptance:     fx_rates filled for last 400 days (history file) and today
Rollback:       table additive
Est. effort:    S
```
```
UNIT 1.2  Timezone normalisation
Purpose:        Canonical Stockholm days from Sydney-hourly data.
Files:          ROOT/adsys/tz.py
Depends on:     0.6
Interface:      date_sto/hour_sto columns; sto_to_syd_schedule()
Implementation: - zoneinfo conversion incl. both DST regimes (8–10 h offset)
                - view v_campaign_daily_sto summing hourly by date_sto
Test:           adsys/tests/tz_tests.py (DST boundary dates in March, April, October)
Acceptance:     Σ hourly by date_syd = gads_campaign_daily per day (±0.01 AUD)
Rollback:       n/a
Est. effort:    S
```
```
UNIT 1.3  Pixel v2 + tracker schema
Purpose:        Capture click ids, touches, GA ids, consent; send MP with real client/session ids.
Files:          bin/token-obtainer/webpixel-backup/custom_pixel.js (new version file custom_pixel.v2.js); bin/pixel-tracker/tracker.py; migrations pdb_001.sql
Depends on:     0.10
Interface:      in: pixel POST; out: purchases new columns, probes rows, MP events
Implementation: - follow WEBPIXEL_RUNBOOK_2026-09-07.md; back up current container JSON before edit
                - §6.3 logic; probe hook; pixel_version 2.0.0
                - tracker: ALTER columns, /track/probe endpoint, MP with client_id/session_id
                - deploy tracker with systemctl restart; verify existing flows unaffected
Test:           adsys/tests/tracker_v2_tests.py (local POST fixtures); live probe via UNIT 1.9
Acceptance:     first real order after deploy has click/touch/consent fields populated (or consent-false recorded)
Rollback:       restore pixel from container_pre_edit.json backup; tracker.py.pre-adsys + columns ignored
Est. effort:    M
```
```
UNIT 1.4  Order attribution derivation
Purpose:        One row per order: click, touches, entity, channel, new/repeat.
Files:          ROOT/adsys/derive/attribution.py; ndb migration (order_attribution)
Depends on:     0.6, 0.7, 1.3
Interface:      out: order_attribution
Implementation: - join per §6.2 with match_method
                - entity resolution: nr_* params → click_view → utm name → UNRESOLVED
                - channel classification §6.4; UNKNOWN_CONSENT separate
                - new vs repeat by email hash
Test:           adsys/tests/attribution_tests.py (fixtures for each match path)
Acceptance:     every web order has a row; match-method distribution reported
Rollback:       table rebuildable
Est. effort:    M
```
```
UNIT 1.5  Order economics + product_facts extension
Purpose:        Contribution per order (§3.2) and C_new.
Files:          ROOT/adsys/derive/economics.py; FDB migration (product_claims, banned_phrases); nordisk_self.py loader extension; ROOT/adsys/config/economics.toml (vat table, payment_fee_rate)
Depends on:     0.7, 1.1
Interface:      out: order_economics, value_beliefs(C_NEW)
Implementation: - COGS from hypersku_final.json via cogs_final.py output; SKU medians fallback
                - refund Beta posterior, uniform hazard, LTV uplift cap
                - daily recompute for orders < 100 d old
Test:           adsys/tests/economics_tests.py (hand-computed fixtures incl. partial refund)
Acceptance:     C_new per product published in `adsys --agent economics`; COGS coverage ≥ 95% or incident
Rollback:       tables rebuildable
Est. effort:    M
```
```
UNIT 1.6  (merged into 1.5 — refund watch is the daily recompute)
```
```
UNIT 1.7  Click-conversion upload (secondary action) + adjustments
Purpose:        Server-side, order-keyed Ads conversions independent of GA4.
Files:          ROOT/adsys/actions/upload.py; ROOT/adsys/gads_rest.py (only if CLI lacks the service)
Depends on:     1.4, 1.5, 0.9
Interface:      out: gads_click_uploads, gads_adjustments
Implementation: - create UPLOAD_CLICKS action as secondary (catalogue CONV_ACTION_CREATE_SECONDARY) — validate-only first
                - daily upload per §6.13 with consent handling, partialFailure parsing
                - adjustments for refunds within Google's window (limit verified and recorded in config)
Test:           adsys/tests/upload_tests.py; live validate_only run returns expected partial-failure shape
Acceptance:     14 days of uploads; R4 computed daily
Rollback:       stop job; action left secondary (no bidding effect)
Est. effort:    M
```
```
UNIT 1.8  Reconciliation job
Purpose:        R1–R9 daily with incidents.
Files:          ROOT/adsys/recon.py
Depends on:     1.4, 1.7, 0.8
Interface:      out: incidents, recon section of digest
Implementation: - checks and tolerances per §6.8; auto-resolve after 3 green days
Test:           adsys/tests/recon_tests.py (breach and recovery fixtures)
Acceptance:     14-day history in run_ledger
Rollback:       disable job
Est. effort:    M
```
```
UNIT 1.9  Synthetic E2E self-tests
Purpose:        Prove pixel→tracker→GA4 and upload auth daily.
Files:          ROOT/adsys/health/e2e.py; ROOT/adsys/health/selftest.py
Depends on:     1.3, 1.7
Interface:      out: selftest run_ledger + incidents
Implementation: - headless Chromium (Playwright) with profile under TMP, consent accept, nr_probe token
                - MP nr_synthetic_probe + realtime read within 30 min
                - validate-only upload
                - T-* suite of §15.3 (those available by now)
Test:           run once manually; forced failure (tracker stopped in a test port) produces incident
Acceptance:     13/14 green days
Rollback:       disable job
Est. effort:    M
```
```
UNIT 1.10 Baseline report
Purpose:        Numbers the eval harness compares against (§20.1).
Files:          ROOT/adsys/reports/baseline.py → ROOT/adsys/docs/baseline-<date>.json
Depends on:     1.1–1.8
Interface:      out: baseline JSON (AUD, SEK, FX, windows, states)
Implementation: - recompute 30/90-day spend, clicks, conversions by segments.date per campaign
                - site_cvr_90d, ATC, engaged rates, C_new, refund rate, consent share, R1 baseline
                - resolve the 34-vs-223-clicks discrepancy (Q5)
Test:           rerun reproduces identical JSON
Acceptance:     file committed; priors in §8.2 seeded from it
Rollback:       n/a
Est. effort:    S
```
```
UNIT 1.11 Dead-man + heartbeat
Purpose:        Detect adsys or box death.
Files:          ROOT/adsys/health/heartbeat.py; healthchecks ping URLs in secrets (N4)
Depends on:     0.1
Interface:      out: heartbeat file, pings, Telegram daily heartbeat
Implementation: - tick writes heartbeat; comb check added; pings N4
Test:           stop tick 60 min in staging → comb alert fires
Acceptance:     heartbeat messages for 7 days
Rollback:       remove job
Est. effort:    S
```
```
UNIT 1.12 Consent verification
Purpose:        Don't optimise on non-compliant data.
Files:          ROOT/adsys/reports/consent_check.py
Depends on:     1.3
Interface:      out: report + incident
Implementation: - headless visit: banner present, Customer Privacy API reflects choices, Google tags in consent mode for EEA (inspect network requests for gcs/gcd params)
                - consent share from purchases.consent_json
Test:           decline-consent run → no click id stored in probes/purchases
Acceptance:     check green (Stage-0 promotion prerequisite)
Rollback:       n/a
Est. effort:    S
```

```
UNIT 1.13 Proven-demand model
Purpose:        Rank searches and pages by real sales (GSC × GA4 × Shopify × tracker), §10.0.
Files:          ROOT/adsys/derive/proven_demand.py; ndb migration (page_value, query_value)
Depends on:     0.7, 0.8, 1.4, 1.5
Interface:      in: traffic_daily, ga4_daily_landing, shop_order_ext.landing_site_full, order_attribution; out: page_value, query_value
Implementation: - page→orders dedup by order id; evidence priority tracker > Shopify landing_site > GA4
                - organic CVR Beta-shrunk to site CVR (k=100 sessions)
                - query value = Σ gsc clicks × page CVR × C_new(product mix); tiers PROVEN/PROMISING/DEMAND_ONLY
                - first run backfills 90 d; nightly thereafter
Test:           adsys/tests/proven_demand_tests.py (hand-computed fixture: 2 pages, 5 queries, 3 orders)
Acceptance:     report `adsys --agent proven-demand --top 30` lists pages with real orders and their queries; top items manually plausible to Maestro
Rollback:       tables rebuildable
Est. effort:    M
```

```
UNIT 1.14 Spend governor (revenue-linked cap)
Purpose:        Enforce 7-d spend ≤ 0.35 × 7-d store revenue inside capguard.
Files:          ROOT/adsys/capguard.py (governor), ROOT/adsys/derive/store_revenue.py
Depends on:     0.7, 1.1, 2.9
Interface:      in: shop_order_ext, shop_refunds, fx_rates; out: governor_aud_day in capguard_log/growth_state; budget reductions
Implementation: - store revenue 7 d = gross orders (excl. test/cancelled) − refunds, SEK→AUD daily
                - current cap = max(15 while learning budget remains, min(ramp, governor/7·7, ceiling))
                - on revenue drop: lower largest non-brand budgets first, same day; incubations last
                - Shopify BROKEN → last good governor × 0.8, no increases
Test:           adsys/tests/governor_tests.py (revenue 1,000 AUD/d → 350 allowed; 400 → 140; BROKEN path)
Acceptance:     capguard_log shows governor daily; T-CAP extended to governor
Rollback:       config max_spend_to_revenue unchanged; governor cannot be disabled, only its ratio changed by owner
Est. effort:    S
```

### Phase 1b — Growth levers (Builder-run, owner-approved, measured by adsys)
- **Goal:** move orders now, without waiting for the autonomy ladder. The Builder (OWL/pi) makes these changes with Maestro, like UNIT 0.13 remediations; adsys only measures them. **Exit:** each lever has a before/after reading with stated uncertainty. **Money:** paid only if the Phase 1 go/no-go says GO.

```
UNIT 1.15 Comparison-path conversion
Purpose:        Turn the article that gets 67% of organic clicks into a buying path.
Files:          Shopify article/page edits via the existing article pipeline or Pages (theme changes via theme_guard only)
Depends on:     1.10
Interface:      out: page changes; adsys measures article→product clicks, ATC, orders (before/after, 28 d each)
Implementation: - product blocks with price and 100-day guarantee inside the comparison table and above the fold
                - one clear next step per product; bundle offer where Wellness Kit fits
                - claims gate (§12.4) on every changed sentence
Test:           nrshot/nrmobile screenshots; claims gate pass; link checks 200
Acceptance:     change live; 28-d before/after report with credible interval
Rollback:       restore previous article body (pipeline history)
Est. effort:    M
```
```
UNIT 1.16 Comparison-intent Search + Shopping (only on GO)
Purpose:        Paid on the intent that already converts, at break-even CPC.
Files:          campaigns created by the Builder through adsys executor (validate-only first), enrolled as INCUBATING
Depends on:     1.14, 1.15, Phase 1 go/no-go
Interface:      out: one Search campaign (bäst i test / jämför queries → comparison page), Standard Shopping when N2 lands
Implementation: - CPC ceiling = break-even from real C_new; negatives floor; UTM standard
                - governor and envelope apply from day one
Test:           executor read-back; recon R1/R4 on the first orders
Acceptance:     14 d live with measured cost per order vs break-even
Rollback:       pause campaigns
Est. effort:    M
```
```
UNIT 1.17 Email capture and core flows
Purpose:        Build an audience (≈ 3 profiles today) and the flows that convert it.
Files:          Klaviyo signup form and flows built in the UI by Maestro/Builder; adsys ingests metrics
Depends on:     —
Interface:      out: list growth/week, abandoned-cart and welcome flow revenue
Implementation: - signup offer tied to the comparison content (e.g. the comparison as a guide), consent-compliant
                - welcome, abandoned cart, post-purchase, cartridge replenishment flows (these become the §12.13 reference flows later)
Test:           test profile passes through each flow
Acceptance:     flows live; weekly list growth reported
Rollback:       set flows to draft
Est. effort:    S
```
```
UNIT 1.18 Order value: bundles and cartridge subscription
Purpose:        Raise AOV and repeat value, which raises C_new and the break-even CPC for every channel.
Files:          Shopify bundle/subscription configuration (owner-approved)
Depends on:     1.5
Interface:      out: AOV, attach rate, subscription starts
Implementation: - filter + cartridge bundle; cartridge subscription made visible on product pages (3 subscription orders already exist)
                - margin check against the profit target before launch
Test:           checkout of each bundle in preview
Acceptance:     live; AOV before/after reported
Rollback:       unpublish bundle
Est. effort:    S
```

### Phase 2 — Entity model and decision ledger
- **Goal:** empty-but-correct control plane; every later write lands here. **Exit:** all §4.5 tables migrated; entities synced daily; landers verified; taxonomy tagged; executor runs in dry-run producing ledger rows; Telegram commands work. **Effort:** ≈ 2 weeks (parallel with Phase 1 proof window). **Money:** none.

```
UNIT 2.1  Control-plane migration
Purpose:        Create ADB tables + append-only triggers without touching ad_audit_*.
Files:          ROOT/adsys/migrations/adb_001_control.sql (full); adb backup
Depends on:     0.4
Interface:      schema
Implementation: - backup ADB; apply; PRAGMA integrity_check
Test:           adsys/tests/append_only_tests.py (T-APPEND-ONLY)
Acceptance:     ad_audit_* row counts unchanged
Rollback:       restore backup
Est. effort:    S
```
```
UNIT 2.2  Entity sync + lifecycle
Purpose:        ent_campaign/ad_group/keyword from snapshots; roles; legacy flags; human locks.
Files:          ROOT/adsys/entities.py
Depends on:     2.1, 0.6
Interface:      out: ent_* rows
Implementation: - role from name conventions + blueprint mapping (5 blueprints) + R2 fallback
                - LEGACY_PAUSED for all non-ENABLED at first sync; reportable rules
                - human_lock_until from change_event client_type ≠ API
Test:           adsys/tests/entities_tests.py; T-PAUSED-LEAK fixture
Acceptance:     3 ENABLED campaigns reportable; 27 others not
Rollback:       rebuildable
Est. effort:    M
```
```
UNIT 2.3  Landing-page registry + checker
Purpose:        §11.6.
Files:          ROOT/adsys/landers.py
Depends on:     2.1, 0.13
Interface:      out: ent_lander, lander_checks
Implementation: - seed from landing-page-inventory.md, nordisk_ads_context.json, sitemap, published-articles.json, Shopify pages/products
                - checks incl. nrperf/nrshot weekly, screenshots to ART
Test:           adsys/tests/landers_tests.py (301 fixture fails P-URL200)
Acceptance:     every ENABLED final URL VERIFIED or incident
Rollback:       rebuildable
Est. effort:    M
```
```
UNIT 2.4  Taxonomy rules + keyword/term tagging (R1)
Purpose:        Stage/intent/pain/lang on every keyword and term.
Files:          ROOT/adsys/config/taxonomy.toml; ROOT/adsys/reason/r1_classifier.py; prompts/r1.v1.md; golden set tests
Depends on:     2.1
Interface:      out: tags on ent_keyword, term label cache table in ADB (term_labels: term_norm, labels_json, models, conf, labelled_at)
Implementation: - RULE lexicon first; R1 two-model agreement; UNKNOWN on schema fail
                - 30-case golden set from real search terms
Test:           adsys/tests/llm_r1_golden_tests.py ≥ 90% label accuracy on relevance
Acceptance:     all existing keywords + 90-day terms tagged or AMBIGUOUS
Rollback:       labels are data; delete rows
Est. effort:    M
```
```
UNIT 2.5  Claims tables
Purpose:        product_claims + banned_phrases seeded from spec sheet/live site.
Files:          FDB migration; ROOT/adsys/creative/claims_gate.py
Depends on:     1.5
Interface:      claims_gate.check(lines) -> per-line pass/fail
Implementation: - seed specs (KDF-55+CaSO₃+GAC; ACF only), prices, 100-day guarantee, brand claims with source_ref URLs
                - banned list per §12.4
Test:           adsys/tests/claims_gate_tests.py (60 dagar, TEWL, mixed specs, trademark → fail)
Acceptance:     existing ad-copy-library lines scanned; violations reported
Rollback:       tables additive
Est. effort:    S
```
```
UNIT 2.6  ICP machine-tagging
Purpose:        nordisk-icp.md → tax_pain, tax_icp_segment (no new research).
Files:          ROOT/adsys/reason/r2_tagger.py; prompts/r2.v1.md
Depends on:     2.1
Interface:      out: taxonomy tables with icp_ref line anchors
Implementation: - R2 extraction; every VOC phrase must be verbatim substring of the file (deterministic check)
Test:           substring test passes for 100% of phrases
Acceptance:     ≥ 6 pains present (dry/itchy skin, hard water, chlorine, heavy metals, hair damage, allergies)
Rollback:       delete rows
Est. effort:    S
```
```
UNIT 2.7  Content asset map
Purpose:        Tag 23 articles + 50 sitemap pages as TOF/MOF/BOF assets.
Files:          ROOT/adsys/reason/r2_tagger.py (assets mode)
Depends on:     2.4, 2.6
Interface:      out: content_assets
Implementation: - fetch page text via nrtext.js; R2 tags; conf < 0.7 → NEEDS_REVIEW
Test:           spot fixture of 5 pages with known tags
Acceptance:     ≥ 90% assets tagged with conf ≥ 0.7
Rollback:       delete rows
Est. effort:    S
```
```
UNIT 2.8  Negative vocabulary + monitor rewire
Purpose:        negatives.md machine-readable; replace hardcoded waste list.
Files:          ROOT/adsys/negatives.py; bin/harvesters/ads-monitor.sh
Depends on:     2.1
Interface:      out: neg_vocab, ent_negative (LEGACY + SEED)
Implementation: - parse negatives.md categories; add hardcoded list; inflections (rule table + observed forms)
                - ads-monitor reads neg_vocab (report-only until Stage 1)
Test:           adsys/tests/negatives_tests.py (conflict check blocks negative matching a live keyword)
Acceptance:     vocab ≥ size of negatives.md + hardcoded list; monitor output unchanged in shape
Rollback:       ads-monitor.sh.pre-adsys
Est. effort:    M
```
```
UNIT 2.9  Executor (dry-run) + capguard
Purpose:        The only mutation path, proven in dry-run.
Files:          ROOT/adsys/actions/executor.py; ROOT/adsys/capguard.py; ROOT/adsys/preflight.py; /root/.nordisk/guard/ads_cap.json
Depends on:     2.1, 0.6
Interface:      in: actions rows; out: action_events
Implementation: - §9.1 steps with --validate-only only (APPLY disabled by config until Phase 4)
                - capguard process + cron line; CB-SPEND logic (pause path enabled from Stage 0)
                - HALT file handling
Test:           adsys/tests/{executor,capguard,halt}_tests.py (T-CAP, T-HALT)
Acceptance:     20 dry-run actions VALIDATED with inverse_json stored
Rollback:       remove cron line; config apply=false
Est. effort:    L
```
```
UNIT 2.10 Belief store + priors
Purpose:        §8.2 hierarchy computed nightly.
Files:          ROOT/adsys/beliefs.py
Depends on:     1.10, 2.2
Interface:      out: beliefs, belief_history, value_beliefs
Implementation: - root priors from baseline JSON; k table from policy.toml; Monte Carlo helper with seeded RNG
Test:           adsys/tests/beliefs_tests.py (shrinkage math; reproducible draws)
Acceptance:     beliefs exist for every ENABLED entity
Rollback:       rebuildable
Est. effort:    M
```
```
UNIT 2.11 Failure memory seed
Purpose:        Legacy lessons without surfacing names.
Files:          ROOT/adsys/failmem.py
Depends on:     2.2, 2.4
Interface:      out: fail_memory (source LEGACY_MINED)
Implementation: - fingerprints from legacy campaigns' terms/landers; verdict MEASURED_BADLY where attribution was absent; retry condition {"attribution_proven":true}
Test:           P-DUP blocks an identical tuple
Acceptance:     entries for all legacy campaigns with spend
Rollback:       delete rows with source LEGACY_MINED
Est. effort:    S
```
```
UNIT 2.12 Owner interface
Purpose:        Telegram digest renderer + command handler.
Files:          ROOT/adsys/digest.py; ROOT/adsys/owner_cmd.py; ROOT/adsys/reason/r7_narrator.py
Depends on:     2.1, N5
Interface:      in: /ads commands; out: messages
Implementation: - box tables ≤ 36 chars; Measure-only renderer; number audit for R7
                - regex command parser; chat_id allow-list; cap file writer
Test:           adsys/tests/{digest_types,owner_cmd}_tests.py; width test on rendered samples
Acceptance:     /ads status round-trips; daily heartbeat delivered 3 days
Rollback:       disable jobs
Est. effort:    M
```

```
UNIT 2.13 Day-one knowledge import
Purpose:        Turn existing Google Ads history and documents into sourced lessons, priors, negatives, fail memory and creative seeds.
Files:          ROOT/adsys/lessons.py; ADB lessons
Depends on:     0.6 (legacy backfill), 2.1, 2.8, 2.11
Interface:      in: §16.10 sources; out: lessons + their applications
Implementation: - R2 extracts candidate lessons per document; each must cite file + line range (checked by string match) or it is dropped
                - classify kind and evidence_state; measured → priors/rules; opinions → hypotheses
                - legacy search terms/ads/landers → PROVEN evidence, vocab, fail memory
                - "What we already know" digest block (≤ 15 lines)
Test:           adsys/tests/lessons_tests.py (unsourced lesson rejected; opinion never becomes RULE)
Acceptance:     lesson list delivered to Maestro at Stage 0; every line has a source
Rollback:       mark lessons VETOED
Est. effort:    M
```

### Phase 3 — Stage 0 shadow observation
- **Goal:** full loop in SHADOW; judgement measured against reality at zero cost. **Why now:** cheapest way to calibrate thresholds. **Exit:** §18.3 Stage 0→1 criteria met (≥ 14 days). **Deferred:** all non-CB mutations. **Money:** none (existing spend continues unchanged).

```
UNIT 3.1  Policy engine (all classes, SHADOW)
Purpose:        D00–D20 evaluate daily/weekly and write decisions.
Files:          ROOT/adsys/policy/d*.py; ROOT/adsys/config/policy.toml; ROOT/adsys/decide.py
Depends on:     2.2–2.10
Interface:      out: decisions (mode SHADOW), predicted_json
Implementation: - global guards G1–G9 as decorators
                - each class returns ACT/NO_ACTION/ESCALATE with revisit_trigger
                - existing ENABLED non-brand campaigns enrolled as INCUBATING with retro hypotheses (§14.3)
Test:           adsys/tests/policy_d<NN>_tests.py per class (trigger, guard, do-nothing branches)
Acceptance:     14 days of decisions; each class has ≥ 1 NO_ACTION with revisit trigger
Rollback:       disable job
Est. effort:    L
```
```
UNIT 3.2  Forecasts + calibration
Purpose:        Predicted-vs-actual for promotion criterion.
Files:          ROOT/adsys/learn.py (forecast + outcome modes)
Depends on:     3.1
Interface:      out: outcomes, calibration metrics
Implementation: - daily per-campaign and per-ad-group next-7-day clicks and cost forecasts (Gamma-Poisson on trailing 28 d) with 80% intervals
                - coverage computation; k adjustment rule (§16.5) logged, not auto-applied until Stage 1
Test:           adsys/tests/learn_tests.py
Acceptance:     ≥ 60 evaluated forecasts
Rollback:       n/a
Est. effort:    M
```
```
UNIT 3.3  Counterfactual lane
Purpose:        Learn from inaction.
Files:          ROOT/adsys/learn.py (counterfactual mode)
Depends on:     3.1
Interface:      out: outcomes for counterfactual decisions
Implementation: - evaluators per class (§16.5 examples)
Test:           fixture: un-negated junk term continues spending → CONFIRMED
Acceptance:     weekly counterfactual summary in digest
Rollback:       n/a
Est. effort:    S
```
```
UNIT 3.4  Diagnostician (R3) + incident narration
Purpose:        Explain incidents with checkable hypotheses.
Files:          ROOT/adsys/reason/r3_diag.py; prompts/r3.v1.md
Depends on:     0.4, 1.8
Interface:      out: incidents.detail_json.hypotheses; deterministic checks run from enumerated list
Implementation: - enumerated check catalogue (disapproval, budget, billing, bid below first page, low search volume, lander, tracking legs)
Test:           golden incidents (Conquest 0-impression case, §24.G3)
Acceptance:     every sev ≤ 2 incident has a diagnosis or "UNDIAGNOSED"
Rollback:       template fallback
Est. effort:    S
```
```
UNIT 3.5  Trust ladder evaluator
Purpose:        Automatic promotion/demotion.
Files:          ROOT/adsys/trust.py
Depends on:     3.2, 1.9
Interface:      out: trust_state rows + digest announcement
Implementation: - criteria per §18.3/§18.4 as pure functions over ADB/NDB
Test:           adsys/tests/trust_tests.py (each promotion and demotion path)
Acceptance:     stage visible in /ads status
Rollback:       owner /ads stage 0
Est. effort:    M
```
```
UNIT 3.6  Retire superseded pipeline scripts
Purpose:        Don't orphan google-ads/pipeline/01–04.js silently.
Files:          google-ads/pipeline/_superseded/README.md
Depends on:     3.1, 2.12
Interface:      —
Implementation: - move scripts; README maps each to its replacement; remove any cron referencing them
Test:           grep crontab for pipeline/0 → none
Acceptance:     README present
Rollback:       move back
Est. effort:    S
```

### Phase 4 — Stage 1: reversible actions
- **Goal:** live negatives, pauses, budget/CPC within cap, bidding correction, brand governance, E-01. **Exit:** Stage 1→2 criteria. **Money:** yes — within the 15 AUD/day cap; learning budget clock starts.

```
UNIT 4.1  Executor APPLY for Stage-1 catalogue
Purpose:        Turn on real mutations for D01–D03, D05, D08–D11c, D15, D16, D17.
Files:          ROOT/adsys/config/adsys.toml (apply=true, allowed_types by stage)
Depends on:     3.5 (Stage 1 reached)
Interface:      out: live mutations + ledger
Implementation: - per-type allow-list derived from trust stage at call time
                - first mutation of each type: validate-only → apply → read-back → Telegram line
Test:           staged live test: one negative on the broad campaign, verify, veto via /ads veto, verify removal
Acceptance:     20 actions VERIFIED, 0 mismatches
Rollback:       apply=false; /ads halt
Est. effort:    M
```
```
UNIT 4.2  Circuit breakers full set
Purpose:        CB-* per §15.2 live.
Files:          ROOT/adsys/health/breakers.py
Depends on:     4.1
Interface:      out: CB actions, incidents
Implementation: - hourly data for spend/CPC; lander URL checks every 30 min
Test:           fixtures for each CB trigger and reset
Acceptance:     tests pass; no CB false trip in 7 days (or each explained)
Rollback:       disable individual CB via config (CB-SPEND cannot be disabled)
Est. effort:    M
```
```
UNIT 4.3  Brand switchback E-01
Purpose:        Measure brand click capture.
Files:          ROOT/adsys/experiments/e01_brand.py
Depends on:     4.1
Interface:      out: experiments row, weekly results
Implementation: - alternate weeks Mon 00:00 Stockholm (converted to Sydney); Serper brand SERP check daily in OFF weeks (abort rule)
Test:           schedule simulation test
Acceptance:     8 weeks complete or aborted with reason
Rollback:       set brand ENABLED; mark ABORTED
Est. effort:    S
```
```
UNIT 4.4  Veto and rollback commands
Purpose:        After-the-fact veto for every action and launch.
Files:          ROOT/adsys/owner_cmd.py (veto), ROOT/adsys/actions/rollback.py
Depends on:     4.1
Interface:      in: /ads veto <id>; out: inverse actions, VETOED events
Implementation: - launch id → all actions of that incubation in reverse order
Test:           adsys/tests/rollback_tests.py
Acceptance:     live veto tested in 4.1
Rollback:       n/a
Est. effort:    S
```

### Phase 5 — Stage 2: build actions
- **Goal:** keywords, RSAs, assets, ad groups, Shopify Page landers — autonomous, gated by pre-flight and MOE. **Exit:** Stage 2→3 criteria. **Money:** within cap (exploration pool).

```
UNIT 5.1  Creative pipeline G1–G8
Purpose:        §12 end to end.
Files:          ROOT/adsys/creative/{pipeline,assemble}.py; prompts/r4.v1.md, r5.v1.md; imports from /root/loops/nordisk-comparison-pipeline/nodes
Depends on:     2.5, 4.1
Interface:      in: ad-group tuple; out: ent_creative (STAGED) → RSA_CREATE actions
Implementation: - claims gate before and after swedish_polish; MOE thresholds; validate-only policy check
Test:           adsys/tests/creative_tests.py (fixtures that must fail: 60 dagar, KDF on Duschhuvud, trademark); golden run on one existing ad group
Acceptance:     one RSA created live and APPROVED within 72 h
Rollback:       pause RSA
Est. effort:    L
```
```
UNIT 5.2  Keyword harvest (D04) and query sculpting
Purpose:        Grow exact keywords from real terms.
Files:          ROOT/adsys/policy/d04_harvest.py (live)
Depends on:     4.1, 2.4
Interface:      out: KW_ADD, NEG_ADGROUP_ADD
Implementation: - lander consistency check before add
Test:           policy_d04_tests.py
Acceptance:     ≥ 1 harvested keyword live with read-back
Rollback:       pause keyword
Est. effort:    S
```
```
UNIT 5.3  Ad-group incubation (D12 + D15 live)
Purpose:        Self-initiated ad groups with envelope and auto-kill.
Files:          ROOT/adsys/policy/{d12_adgroup,d15_incubation}.py; ROOT/adsys/incubation.py
Depends on:     5.1, 5.2, 10-engine (5.5)
Interface:      out: incubations, hypotheses, actions
Implementation: - pre-flight all P-*; ad group created with keywords, RSA, sitelinks; budget via campaign pool
                - ad-group spend enforcement: pause at 63 AUD cumulative
Test:           dry-run full creation in validate-only; live first launch
Acceptance:     first incubation closed with a verdict and fail-memory/graduation written
Rollback:       /ads veto <launch_id>
Est. effort:    L
```
```
UNIT 5.4  Shopify Page landers (D14)
Purpose:        Autonomous non-theme landers.
Files:          ROOT/adsys/creative/pages.py; prompts/r8.v1.md
Depends on:     5.1, N8 (write_content verified)
Interface:      out: Shopify page (unpublished → published), ent_lander CANDIDATE → VERIFIED
Implementation: - §12.6 autonomous path; screenshot + nrvision + nrperf gates
Test:           create unpublished page in test mode, run gates, delete (test page only)
Acceptance:     one page published and VERIFIED
Rollback:       unpublish
Est. effort:    M
```
```
UNIT 5.5  Opportunity engine
Purpose:        §10 queue weekly.
Files:          ROOT/adsys/opportunity/{sources,score,propose}.py; prompts/r6.v1.md
Depends on:     2.4, 0.6, planner/serp ingest
Interface:      out: hypotheses (OPEN)
Implementation: - scoring formula; cannibalisation rule; out-of-ideas cascade
Test:           adsys/tests/opportunity_tests.py (score math; cannibalised query excluded)
Acceptance:     weekly queue with ≥ 1 candidate or explicit empty-state reason
Rollback:       disable job
Est. effort:    M
```
```
UNIT 5.6  Fatigue + asset refresh (D07) and lander swap (D11d)
Purpose:        Creative and lander maintenance.
Files:          ROOT/adsys/policy/{d07_fatigue,d11_lander}.py; ROOT/adsys/experiments/swap.py
Depends on:     5.1
Interface:      out: asset swaps, SEQUENTIAL_SWAP experiments
Implementation: - §8.5 D07/D11d rules
Test:           policy tests
Acceptance:     tests pass (live firing depends on volume)
Rollback:       inverse ops
Est. effort:    S
```

```
UNIT 5.7  Spend ramp controller (D21) + growth state
Purpose:        Move current cap toward the ceiling while profitable; report the bottleneck.
Files:          ROOT/adsys/policy/d21_ramp.py; ROOT/adsys/growth.py; ROOT/adsys/config/growth.toml; capguard.py (current-cap writer)
Depends on:     1.13, 3.5, 4.1
Interface:      out: growth_state rows, current_aud_per_day changes, Gate CAP at ceiling
Implementation: - weekly bottleneck classification (§3.7)
                - ramp rules ×1.5 / hold / ×0.7 with marginal check; capguard enforces ceiling, step size, cooldown
                - digest GOAL line
Test:           adsys/tests/d21_ramp_tests.py (each bottleneck; refusal above ceiling; marginal-return down-step)
Acceptance:     growth_state row every Monday; a simulated profitable fixture ramps 15→22.5→34
Rollback:       owner /ads cap or capguard reset current to 15
Est. effort:    M
```

```
UNIT 5.8  Creative feedback loop + pattern library
Purpose:        §12.8–12.10: review, bucket, diagnose, iterate, pool learnings.
Files:          ROOT/adsys/creative/{feedback,diagnose,patterns,bench}.py; ADB tables creative_reviews, creative_attributes, creative_patterns
Depends on:     5.1
Interface:      in: ent_creative, gads_ad_asset_snapshot, GA4/tracker downstream; out: reviews, iteration briefs → §12 pipeline, pattern posteriors
Implementation: - feedback-due rule (7 d AND evidence floor, max 28 d)
                - bucket formulas + deterministic diagnosis table; nrvision review for images/landers
                - iteration limits (3; stop after 2 non-improving); graveyard → fail memory
                - attribute tagging at creation; nightly pooled posteriors per attribute/surface/market
                - 40-headline / 12-description bench per active ad group
Test:           adsys/tests/feedback_loop_tests.py (each diagnosis row; bucket edges; iteration stop)
Acceptance:     first weekly review with buckets and briefs; pattern table populated
Rollback:       disable job; creatives stay as they are
Est. effort:    L
```
```
UNIT 5.9  QS attack + lander factory throughput
Purpose:        §12.9 benchmark gate and D14 at up to 5 pages/week.
Files:          ROOT/adsys/policy/{d14_lander,qs_gate}.py
Depends on:     5.4, 5.8
Interface:      out: tight query-cluster ad groups, new pages, QS trend report
Implementation: - PROVEN cluster → own ad group + own page; CTR benchmark gate with ≤ 3 hook rewrites
                - weekly spend-weighted QS ≥ 7 share and CPC trend in digest
Test:           policy tests; fixture where QS rise lowers modelled CPC
Acceptance:     QS report weekly; ≥ 1 cluster page live
Rollback:       unpublish pages; merge ad groups back
Est. effort:    M
```
```
UNIT 5.10 Answer-engine monitor (AEO)
Purpose:        §10.6 citation tracking and briefs to the organic pipeline.
Files:          ROOT/adsys/aeo.py; prompts/aeo_questions.v1.md; ADB aeo_checks
Depends on:     1.13
Interface:      out: aeo_checks, briefs into the organic pipeline's topic queue (its own gates publish)
Implementation: - 30 questions/market monthly from GSC question queries; ≥ 3 model families with web search via OpenRouter
                - parse cited domains; own-cited rate; competitor citation map
                - robots.txt/JSON-LD audit (theme changes → theme-guard path)
Test:           adsys/tests/aeo_tests.py (citation parsing fixtures)
Acceptance:     first monthly AEO report in digest
Rollback:       disable job
Est. effort:    S
```

```
UNIT 5.11 Winner loop and cascade
Purpose:        §12.11 lineage rounds, champion promotion, exhaustion, and the 8-step cascade.
Files:          ROOT/adsys/winners/{rounds,cascade}.py; ADB themes, variants, cascade_tickets
Depends on:     5.8, 5.9, 5.4
Interface:      out: variant rounds, champions, cascade tickets and their tests; Winner board in digest
Implementation: - one-element-changed variant generation from the champion; round runner per surface
                - promotion at P ≥ 0.8 over evidence floor; exhaustion after 3 rounds
                - cascade steps 1–8 all autonomous with bounds (§12.11); OWNER_PACKET only for new tax/shipping jurisdictions
                - idea bank: 100 themes ranked by evidence tier then EV; free-traffic vs paid-slot allocation (§12.12)
Test:           adsys/tests/winner_loop_tests.py (promotion, exhaustion, veto window, draft fallback)
Acceptance:     first theme with ≥ 1 round closed and a cascade ticket opened
Rollback:       /ads veto <ticket>; themes set to EXHAUSTED
Est. effort:    L
```

```
UNIT 5.12 Klaviyo clone-and-vary writer
Purpose:        Cascade step 6: email variants live without a manual step (after the one-time reference flows).
Files:          ROOT/adsys/channels/klaviyo.py
Depends on:     5.11, N12
Interface:      in: champion angle + reference flow ids; out: HTML templates, cloned flow variants, status changes, flow metrics
Implementation: - scope check on KLAVIYO_TOKEN; else KLAVIYO_PRIVATE_API_KEY from secrets
                - GET definition → swap templates → temporary_id → POST → gates → PATCH live
                - rate limiter (15/min, 100/day creates; 60/min status); complaint/unsubscribe guard
Test:           adsys/tests/klaviyo_tests.py (definition rewrite fixture; rate limiter; guard trips pause)
Acceptance:     one cloned variant live on the abandoned-cart flow and its metrics ingested
Rollback:       PATCH variant flow to draft; reference flow untouched
Est. effort:    M
```
```
UNIT 5.13 Offer builder
Purpose:        Cascade step 5: bundles, upsells, downsells, discounts from winning themes.
Files:          ROOT/adsys/channels/offers.py
Depends on:     5.11, N13
Interface:      out: Shopify discount/bundle configs, offer lander variants, AOV/margin results
Implementation: - discover the store's bundle and upsell mechanism (Admin API + installed apps list); record it in config
                - build offers inside max discount depth and margin check; never touch base prices
                - test each offer against control on lander/checkout traffic; winners stay, losers are removed
Test:           adsys/tests/offers_tests.py (margin check blocks a too-deep discount)
Acceptance:     one offer tested end to end with AOV and contribution reported
Rollback:       disable/delete the discount or bundle created by adsys
Est. effort:    M
```

### Phase 6 — Stage 3: launch
- **Goal:** new Search and Standard Shopping campaigns autonomously. **Exit:** Stage 3→4 criteria (≥ 90 d). **Money:** within cap.

```
UNIT 6.1  Search campaign launcher (D13)
Purpose:        Full campaign trees from blueprints + hypothesis.
Files:          ROOT/adsys/policy/d13_campaign.py; ROOT/adsys/launch/search.py
Depends on:     5.3
Interface:      out: CAMPAIGN_CREATE tree, CAMPAIGN_ENABLE
Implementation: - blueprints from google-ads/campaigns/*.json as templates (brand, long-tail problem, competitor, investigative)
                - created PAUSED, read back, P-* re-run, then ENABLED
Test:           validate-only full tree; live first launch
Acceptance:     one campaign launched and later graduated or auto-killed
Rollback:       /ads veto → campaign PAUSED
Est. effort:    L
```
```
UNIT 6.2  Merchant Center ingest + Standard Shopping launcher
Purpose:        Product-level surface; feed as creative.
Files:          ROOT/adsys/ingest/gmc.py; ROOT/adsys/launch/shopping.py; ROOT/adsys/creative/feed_titles.py
Depends on:     N2, 6.1
Interface:      out: gmc_*; Shopping campaign; feed title edits
Implementation: - Merchant API reads; shopping_performance_view ingest once live
                - Shopping campaign with Max Clicks + ceiling, product groups by handle, CB-GMC
Test:           gmc_ingest_tests.py; validate-only campaign
Acceptance:     Shopping campaign incubating with product-level data flowing
Rollback:       pause campaign
Est. effort:    L
```
```
UNIT 6.3  Theme-gated lander interface
Purpose:        §12.6 theme path up to Gate THEME_PUBLISH.
Files:          ROOT/adsys/creative/theme_bridge.py (calls theme_guard.py; never theme APIs directly)
Depends on:     5.4
Interface:      out: duplicate-theme preview + gate request
Implementation: - change spec → theme_guard flow → gate with preview URL, 17-test result, Lighthouse delta
Test:           no_theme_writes_tests.py still passes; bridge dry-run
Acceptance:     one gate request produced end to end
Rollback:       duplicate theme deleted by theme_guard
Est. effort:    M
```
```
UNIT 6.4  Conquest governance (D18)
Purpose:        Competitor keywords safely.
Files:          ROOT/adsys/policy/d18_conquest.py
Depends on:     6.1
Interface:      out: conquest keywords/negatives
Implementation: - trademark ban in copy; comparison lander; half ceiling
Test:           policy tests
Acceptance:     current conquest campaign diagnosed (§24.G3) and enrolled
Rollback:       inverse ops
Est. effort:    S
```

```
UNIT 6.5  Category conquest scoreboard
Purpose:        §10.7 surfaces-owned per query + share of search.
Files:          ROOT/adsys/conquest.py; ADB conquest_scoreboard
Depends on:     5.10, 6.2
Interface:      out: weekly scoreboard, priority boosts to opportunity engine
Implementation: - join paid IS, organic position (GSC), Shopping/free listing presence, AI citation, Serper competitor ads
                - share of search from planner/GSC brand volumes vs 12 competitors
Test:           adsys/tests/conquest_tests.py
Acceptance:     scoreboard in weekly digest
Rollback:       disable job
Est. effort:    M
```
```
UNIT 6.6  Localized market-entry playbook
Purpose:        §14.7 packets, market seed budgets, localized landers and copy.
Files:          ROOT/adsys/markets/{ceiling,packet,seed}.py
Depends on:     6.1, 5.9
Interface:      out: demand-ceiling estimates, market packets, seed incubations
Implementation: - per-market demand ceiling monthly; packet when target > 70% of reachable demand
                - localized research → R8/R4 in target language + native MOE; no translated primary landers
                - seed budget 1,000 AUD/60 d inside governor; proof criterion; close or join ramp
Test:           adsys/tests/markets_tests.py
Acceptance:     first packet generated when trigger fires
Rollback:       pause market campaigns
Est. effort:    L
```

### Phase 7 — Stage 4: scale
- **Goal:** segment adjustments, ceiling proposals, market-entry packets for new storefront markets (entity scaling and the spend ramp already run from Stage 2). **Money:** yes; cap increases only via Gate CAP.

```
UNIT 7.1  Scale engine (D19) + cap proposals
Purpose:        Ceiling-raise proposals with marginal-return evidence (D19/D21 already live from Stage 2).
Files:          ROOT/adsys/policy/d19_scale.py
Depends on:     Stage 4
Interface:      out: budget increases, gate_requests(CAP)
Implementation: - §8.5 D19; WoW slope limit; evidence packet
Test:           policy tests
Acceptance:     tests pass
Rollback:       inverse budgets
Est. effort:    M
```
```
UNIT 7.2  Segment adjustments (D20)
Purpose:        Geo/device/schedule with Sydney-time schedules.
Files:          ROOT/adsys/policy/d20_segments.py
Depends on:     7.1, 1.2
Interface:      out: criteria modifiers
Implementation: - only when strategy honours modifiers; DST recompute job
Test:           tz schedule tests
Acceptance:     tests pass
Rollback:       remove modifiers
Est. effort:    S
```
```
UNIT 7.3  Channel/market expansion
Purpose:        EN Nordic, PMax, Demand Gen/Video per §14.7.
Files:          ROOT/adsys/launch/{pmax,demand_gen,en_market}.py
Depends on:     7.1
Interface:      out: incubating campaigns
Implementation: - each type its own blueprint, envelope, measurement stage; placement exclusions
Test:           validate-only trees
Acceptance:     each type launched only when its preconditions hold
Rollback:       pause
Est. effort:    L
```

### Permanent lane
The counterfactual lane (UNIT 3.3), calibration (3.2), selftests (1.9) and recon (1.8) run from their phase onward, forever.

---

## 22. Explicit Non-Goals

1. **No dashboard.** Telegram digest + `adsys report … --agent` JSON. A dashboard shows; this system decides.
2. **No Smart Bidding on polluted or thin conversion data.** Maximize Clicks with contribution-derived ceilings until ≥ 30 clean conversions/30 d.
3. **No UNAWARE targeting** (display/video prospecting to people without the problem) before Stage 4 — no measurable path at this volume.
4. **No Meta/Microsoft/TikTok/LinkedIn** — no access (§3.18).
5. **No autonomous theme publishing, conversion-goal changes, cap raises, hard deletes, OAuth.**
6. **No generated product imagery, fabricated reviews or quotes, medical-outcome claims, competitor trademarks in copy.**
7. **No LLM-set thresholds, bids or budgets.**
8. **No Google auto-apply recommendations.**
9. **No re-research of the ICP.** Tagging only.
10. **No Temporal/Postgres/Kafka/Airflow/vector-DB/Kubernetes.**
11. **No surfacing of legacy paused campaigns** in any output.
12. **No simulated confidence:** where the data cannot support a conclusion, the output says "not yet meaningful" with the date it will be.

---

## 23. Open Questions & Assumptions

| # | Question | Default applied (work never blocked) | What would change the design |
|---|---|---|---|
| Q1 | Canonical host: `nordiskrenhet.se` or `www.nordiskrenhet.com`? | Resolved at build (UNIT 0.13): the host returning 200 without redirect for the lander paths; stored in config; P-HOST uses it | Maestro names one → config value, re-run lander checks |
| Q2 | Governor r = contribution ratio − profit target (default 0.15; r = 0.35 until 90 d of margin data); ceiling 350 AUD/day; learning floor 15 AUD; paid CM_ROAS floor 1.0 | Applied | `/ads profit <x>`, `/ads invest <r> <days>`, `/ads cap`, `/ads floor` |
| Q3 (A3) | Payment fee rate | 0.029 of gross | Shopify payout reports → exact rate |
| Q4 (A4) | Refunded product is not resaleable; outbound shipping cost included in `cost_sek` of hypersku | COGS sunk on refund; no extra shipping cost term | If returns are resold or shipping is separate → formula term added |
| Q5 | The §3.3 table's paused rows show 294.88/126.94 AUD in "30 d", while §9 P1 says 34 clicks/30 d and §2 "a few hundred AUD to date" | UNIT 1.10 recomputes by date; priors use pooled history regardless of window | If "30 d" was lifetime, baselines shift; priors unchanged |
| Q6 | Conflict #1 (approval vs veto) | Rev 3 position adopted: copy runs unattended behind the deterministic whitelist gate + MOE | Disapproval > 1/20 or any live claim violation → creative back to Stage 1 (§12.4) |
| Q7 | Paused-campaign rule | Adopted as §18.1: only adsys-created entities named, 14 days after adsys pauses them; others by hypothesis id | Maestro confirms or rejects |
| Q8 | Conflict #2 (theme publish) | Final publish stays Gate THEME_PUBLISH; Shopify Pages (non-theme) are autonomous | 20 clean gated publishes + visual diff + perf proof → owner may reclassify |
| Q9 | Target scope | **TOTAL store orders (owner decision)**; paid, organic, AI, email shares reported | — |
| Q10 | Account in AUD/Sydney (unchangeable). A new SEK/Stockholm account under the same manager would remove FX and tz complexity; history lost is small | Stay on current account; revisit at Stage 3 | Maestro prefers migration → new customer id in `gads-env.sh`, one-time re-seed (§24.H) |

Conflicts #3, #4 and #6 of the brief's §15 are adopted as stated (config host; phases with units; Rev 2 product list authoritative via `product_facts`).

---

## 24. Appendices

### A. DDL
Full DDL is §4.3, §4.5 and §4.6. Migration files: `ndb_001_facts.sql`, `adb_001_control.sql`, `pdb_001.sql`, `kdb_001.sql`, `fdb_001.sql` in `ROOT/adsys/migrations/`, applied by `adsys migrate` with backup first and `PRAGMA integrity_check` after.

### B. Example decision records

```json
{"decision_id":"d-2026-10-12-D01-7f3a","decision_class":"D01","rule_id":"D01.vocab","rule_version":"1.0",
 "entity_type":"SEARCH_TERM","entity_id":"ag:1234|schampo mot torrt hår",
 "stage_at_decision":1,"mode":"LIVE","outcome":"ACT","counterfactual":0,
 "inputs_json":{"impressions_28d":4,"clicks_28d":1,"cost_aud_28d":2.10},
 "evidence_json":{"vocab_match":"schampo","category":"WRONG_CATEGORY","forms":["schampo","schampot","schampon"]},
 "confidence":1.0,"predicted_json":{"term_spend_next_28d_aud":0},"horizon_days":28,
 "rationale":"Vocabulary WRONG_CATEGORY match; no ATC/purchase in 90 d; no conflict with live keywords.",
 "revisit_trigger":null,"fx_to_sek":6.30}
```
```json
{"decision_id":"d-2026-11-02-D15-a91c","decision_class":"D15","rule_id":"D15.funnel_dead","entity_type":"AD_GROUP",
 "entity_id":"ag:5678","stage_at_decision":2,"mode":"LIVE","outcome":"ACT",
 "inputs_json":{"days":17,"spend_aud":61.2,"clicks":29,"atc":0,"checkouts":0,"purchases":0,"atc_parent_mean":0.08},
 "evidence_json":{"p_zero_atc_given_parent":0.089,"threshold":0.10},
 "predicted_json":{"hypothesis":"h-2026-10-16-02","verdict":"REFUTED"},
 "rationale":"29 clicks with 0 add-to-cart is unlikely (p=0.089<0.10) if the ad group matched the parent ATC rate; pre-committed kill executed.",
 "revisit_trigger":"retry after 2027-02-01 or price/offer change"}
```
```json
{"decision_id":"d-2026-10-19-D08-0b2e","decision_class":"D08","entity_type":"CAMPAIGN","entity_id":"c:<nonbrand>",
 "mode":"LIVE","outcome":"NO_ACTION","counterfactual":1,
 "inputs_json":{"budget_lost_is":0.05,"purchases_56d":0,"cost_28d_sek":310.0,"c_new_sek":"<computed>"},
 "rationale":"Not budget-limited; 0 purchases; cost below 2×C_new. Hold.",
 "revisit_trigger":"purchases_56d>=2 OR cost_28d_sek>=2*C_new"}
```

### C. Example digest
§19.4.

### D. Negative-keyword vocabulary seed (merged with `negatives.md` at UNIT 2.8; `negatives.md` wins on conflicts)

| Category | Seed terms (sv unless marked) | Auto-apply | Scope |
|---|---|---|---|
| WRONG_CATEGORY | lotion, kräm, cream, moisturizer, schampo, shampoo, balsam, diskmaskin, vattenkokare, akvarium, pool, kranfilter, vattenkanna, kolsyremaskin | 1 | account list |
| DIY | gör det själv, diy, hemmagjord, bygga eget | 1 | shared sv list |
| NON_BUYER_INTENT | wikipedia, definition, pdf, uppsats | 1 | shared |
| INFORMATIONAL stems | vad är, hur fungerar, varför | 1, `stage_exempt:["PROBLEM_AWARE"]` | shared |
| JOBS_EDU | jobb, lediga jobb, lön, utbildning, praktik | 1 | account |
| PROFESSIONAL | grossist, återförsäljare, b2b, rörmokare | 1 | shared |
| WRONG_MECHANISM | begagnad, blocket, tradera, hyra | 1 | shared |
| GEO_WRONG | bunnings (AU), lidl* | 1 / *REVIEW_ONLY (Lidl exists in Sweden; price-shopper signal) | account |
| COMPETITOR_BRAND | the 12 competitors + Sparkpod, Magichome, AquaBliss | 1 in non-brand and brand; 0 in CONQUEST | campaign |
| PRICE_SHOPPER | gratis, billigaste* | gratis 1; *REVIEW_ONLY (purchase intent possible) | shared |
| OTHER_LANGUAGE | English-only generic terms in SV campaigns (from R1 `lang`) | via R1 | campaign |

Inflections generated per §11.4 (e.g. `kräm, krämen, krämer, krämerna`).

### E. Intent / persona matrix (seed; UNIT 2.6 fills segments from `nordisk-icp.md`)

| Pain | PROBLEM_AWARE keyword examples | Lander | Product | Allowed framing |
|---|---|---|---|---|
| DRY_SKIN | torr hud efter duschen | `/pages/torr-hud-efter-duschen-duschfilter` | Duschvattenfilter / Duschhuvud | problem statement; outcome only via claim ids |
| ITCHY_SKIN | klåda efter dusch | `/pages/itchy-skin` (verify 200/lang) | Duschvattenfilter | problem only |
| HARD_WATER | hårt vatten dusch, kalk i duschen | `/pages/hard-water-in-sweden` | Duschvattenfilter, Wellness Kit | problem + spec claims |
| CHLORINE | klor i duschvatten | product page | Duschvattenfilter (KDF-55 + CaSO₃ + GAC) | spec claims |
| HEAVY_METALS | tungmetaller i vatten | `/pages/tungmetaller-i-duschvatten` | Duschvattenfilter | spec claims only as sourced |
| HAIR_DAMAGE | torrt hår efter dusch | problem lander (to build, D14) | Duschvattenfilter / Duschhuvud | problem only |
| ALLERGY | allergi duschvatten | none by default (medical-claim risk) | — | PROBLEM_ONLY; no ads until a compliant lander exists |
| (COMPARISON) | duschfilter bäst i test, jämför duschfilter | `/pages/duschfilter-jamforelse-bast-i-test` | range | differentiation, no trademarks |

### F. Policy-compliance checklist (automated in claims gate + pre-flight)

1. Every outcome claim maps to `product_claims` id with source_ref.
2. No banned phrases (§12.4), no medical-outcome promises, no "oberoende tester", "TEWL", clinical claims.
3. Spec truth per product; prices and 100-day guarantee equal `product_facts`.
4. No competitor trademarks in ad text or display paths.
5. No fabricated quotes/reviews; VOC only on landers/ads, never in Shopify product descriptions.
6. Editorial: no "!" in headlines, no all-caps words except brand, no gimmicky repetition, character limits.
7. Lander: 200 direct on canonical host, `lang` matches, price matches, claims on page pass the same gate.
8. Google policy: validate-only without non-exemptible errors; no exemption requests.
9. Consent: click-id capture and uploads only with marketing consent.
10. Swedish quality: `swedish_polish` + MOE fluency median ≥ 8.

### G. Worked examples on real data

**G1 — Historical investigative search (legacy, mined): 294.88 AUD, 141 clicks, 0 conversions.**
What adsys would have done, in order:
1. *Before launch:* the hypothesis pre-flight computes break-even. CPC 2.09 AUD ≈ 13.17 SEK. With the non-brand CVR prior (illustrative: `site_cvr_90d` = 1.2% → prior mean 0.6%) and an illustrative `C_new` = 400 SEK, break-even CVR is 3.3% and `P(profitable)` under the prior is < 0.01. The launch would still be allowed only as an *incubation* (exploration clause) — capped at 3 AUD/day, 21 days, 63 AUD — and with a CPC ceiling of `min(3.00, max(breakeven, 1.2 × planner low bid))`.
2. *Day 1–7:* D01 negates vocabulary junk daily; R1 labels terms. Investigative-intent terms (comparisons, "what is") are INVESTIGATIONAL/INFORMATIONAL; if relevant share < 0.5 at ≥ 15 clicks → early TARGETING_LEAK kill.
3. *At ≈ 30 clicks / ≤ 63 AUD:* FUNNEL_DEAD test: with parent ATC 8% (illustrative), `0.92^30 = 0.082 < 0.10` → kill if 0 ATC. **Total loss ≈ 63 AUD instead of 294.88 AUD** (−79%).
4. *Learned:* fail-memory `FUNNEL_DEAD` for (INVESTIGATIONAL, stage SOLUTION_AWARE, lander, match set) with retry "lander change or price/offer change"; plus the structural lesson that at 13 SEK CPC non-brand requires either ≥ 3.3% CVR or higher-contribution products — which is why `margin_idx` in scoring pushes toward the Wellness Kit / Full Home Filtration.
5. Because attribution was broken then, the legacy entry is seeded as `MEASURED_BADLY` (UNIT 2.11), not `LOSER`: it cannot prove zero purchases, only zero recorded purchases.

**G2 — Brand Search (ENABLED): 90 impressions, 34 clicks, 38.45 AUD, 0.61 conversions in 30 d.**
1. The 0.61 is fractional GA4-import credit; internal truth counts tracker orders with a brand-campaign click (none resolvable before pixel v2). Reported as `NO_DATA` for CM until Phase 1.
2. D17: budget = clamp(1.5 × max daily brand spend, 1.50, 3.00) AUD; D10 moves it to Target Impression Share 90% with 1.50 AUD ceiling if it is on a conversion strategy; any non-brand term in brand search terms → exact negative.
3. Never pooled into non-brand CM_ROAS. E-01 runs at Stage 1: if organic recovers ≥ 80% of brand clicks in OFF weeks, brand drops to 1.00 AUD/day defensive — freeing ≈ 1 AUD/day of a 15 AUD cap for exploration. Digest wording: "Brand ROAS overstates acquisition; capture ratio 0.xx (E-01, clicks; orders directional only)."
4. D06 (RSA rotation) cannot fire: 90 impressions/30 d → ≈ 11 months to 1,000 per RSA; the monthly honesty table says so.

**G3 — Conquest campaign (ENABLED): 0 impressions, 0 clicks, 0 cost in 30 d.**
Three-state resolution: coverage for `gads_campaign_daily` is `COMPLETE` and the campaign is ENABLED, so the accessor returns `MEASURED_ZERO` — genuinely zero, not broken. That is where old tooling stopped ("no spend, normal"). adsys continues: CB-IMPR does not fire (no prior impressions), but the D00/R3 "never served" tree runs deterministic checks in order: (1) `primary_status_reasons` (e.g. budget, bidding, ad disapproval, `NOT_ELIGIBLE`); (2) ads `approval_status` — competitor names in ad text would be disapproved under trademark policy (D18 bans them anyway); (3) keywords `system_serving_status` = low search volume (likely for Swedish competitor names); (4) CPC ceiling vs planner first-page bid; (5) geo/language criteria present. Outcome recorded: e.g. "MEASURED_ZERO because keywords are low-search-volume and ads limited by trademark policy" → at Stage 1 it is enrolled as INCUBATING with a retro hypothesis; at deadline with < 100 impressions, D15 verdict NO_DEMAND, paused, fail memory "retry after 180 d or if planner volume doubles". If instead ingest coverage were missing, the same query would render `?` with an AUTH/INGEST incident — never 0.

### H. Cold-start / rebuild-from-zero

Minimum path back to a functioning loop if the DBs, tokens or account are lost:
1. Tokens: `gads-auth.py url` → human consent → `finish`; Shopify token rotate; GA4 key present in `/root/.nordisk/keys`.
2. `adsys migrate` (empty schemas) → `adsys ingest --backfill 90` (Ads API retains history; click_view ≈ 90 d) → Shopify full order backfill → GA4 90 d.
3. Seed state from files, not DBs: `negatives.md`, `landing-page-inventory.md`, `nordisk_ads_context.json`, `nordisk-icp.md`, `campaigns/*.json`, `product_facts` (FDB backup), `ads_cap.json`, `policy.toml`, prompts — all under version control in `ROOT/adsys/` and nightly-copied to `/mnt/HC_Volume_105573741/adsys-backup/` (7 daily + 4 weekly `.backup` snapshots of ADB/NDB/PDB, ≈ 150 MB).
4. Restart at Stage 0 regardless of prior stage; promotion re-earned (14 d minimum).
5. New account (Q10): update `gads-env.sh` only; everything keyed by customer id from there; legacy data becomes fail-memory `LEGACY_MINED`.
