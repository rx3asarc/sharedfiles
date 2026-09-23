# HANDOFF PROMPT — Design an Autonomous, Self-Learning, Self-Healing Google Ads System

**Recipient:** Claude Opus 5 (architect)
**Author:** OWL (Hermes agent, running on the production server)
**Date:** 2026-09-23
**Revision:** 2 (final) — every fact re-verified live against the box at 20:40 CEST. Added 3.12 (first-party server-side tracking stack, already in production), 3.13 (keyword-intel DB), 3.14 (general agent/research/LLM tooling available to the loop), 3.15 (what does not exist), four new entries in Section 4, and corrections to the Klaviyo, GSC-count, `pi-moa` and Postgres claims carried in Revision 1.
**Status:** Greenfield architecture request. Nothing here is built yet. You are designing the spec that will be handed back for implementation.

---

## 0. HOW TO READ THIS BRIEF

You are being asked to design a system, not to write the code. The agent that sent you this (OWL) will implement it. That means:

- **Be concrete.** File paths, table schemas, cron cadences, API call shapes, decision rules with real thresholds, state machines. Not "use ML to optimise bids."
- **Respect the reality in Section 3 and 4.** Those are verified facts from the live account, not assumptions. Everything you design must run against *this* account, *this* server, *these* tools. There is no team, no data warehouse, no ML budget, no Dataflow, no vertex. There is one Linux box, a Go CLI, a SQLite file, and cron. **Section 3.14 is the complete list of what the reasoning/generative layers may call; Section 3.15 is what does not exist.** Do not invent a capability that is not in either list.
- **Design for the failure modes in Section 6.** Every existing automation here that broke did so *silently and plausibly* — it reported "no spend this week, normal for low traffic" while actually being locked out for 9 consecutive weeks. A system that cannot distinguish "nothing happened" from "I am broken" is worse than no system. Fixing this class of bug is a first-class design requirement, not a footnote.
- **Assume real money.** This spends the owner's cash daily in AUD against a small budget. Every write path needs a blast-radius story.
- **Section 7 lists what the owner asked for. Section 8 lists what he doesn't know he needs.** Both are requirements. Section 8 is arguably the harder and more valuable half.

Return format is specified in Section 10.

---

## 1. THE MISSION

> "A fully autonomous self-learning, self-healing, self-propelling Google Ads environment. I don't want to have to guide it. I want it to work by itself — self-healing, self-learning, self-initiating, budget-optimising, scaling-minded, ROAS-increasing, money-making. I want it to launch new campaigns, new ad groups, new ads, take into consideration keywords and negative keywords, language, landing page URL, awareness stage, customer journey, ICP, pain points, brand, competition, educational content, informational and purchase intent, awareness stages... There are a lot of things I'm not thinking about. I don't know what they are. All I know is I want autonomous monitoring, reasoning built in, judgement made, based on what products get the most clicks and impressions and sales in the end effect. Sales must be cross-referenced, and there must be tracking set up so the autonomous system knows and understands what works and what doesn't. That is highly vital."

Decoded into engineering terms, the owner wants a **closed-loop, goal-seeking paid-acquisition agent** with these properties:

| Property | Engineering meaning |
|---|---|
| **Self-initiating** | Discovers and launches new campaigns/ad groups/ads/campaign types without a human prompt. Has an idea pipeline, not just a fix pipeline. |
| **Self-learning** | Persists what worked and what didn't, across entities and over time, and changes its future behaviour because of it. Not just dashboards — an actual feedback loop with memory. |
| **Self-healing** | Detects its own breakage (auth death, API schema drift, empty data, ingest failure) and repairs or escalates. Never confuses broken with quiet. |
| **Self-propelling** | Always has a next action queued. Budget flows toward winners; losers die. Compounding, not stalling. |
| **Budget-optimising** | Reallocates spend across campaigns/ad groups/keywords/geos by measured return, within a hard total cap. |
| **Scaling-minded** | Grows winners deliberately (budget, bid, geo, audience, creative variants) with guardrails against runaway spend. |
| **ROAS-increasing** | Optimises for revenue, not clicks. Requires trustworthy revenue attribution end-to-end — this is the load-bearing wall of the whole design. |
| **Money-making** | Ultimately judged by net contribution: revenue minus ad spend, by cohort and by horizon. |

The end state is a system where the owner's involvement is: **read a periodic digest, and change a strategy or a guardrail when he wants to.** Not approve individual actions.

---

## 2. THE BUSINESS BEING ADVERTISED

**Nordisk Renhet** — Swedish e-commerce, DTC. Sells shower water filtration to the Swedish market (with secondary EU/Nordic exposure).

- **Store:** Shopify, `e68099-e4.myshopify.com`, public domain `nordiskrenhet.se` (also `.com`)
- **GA4 property ID:** `454852488`
- **Google Ads account:** `8479789152` — currency **AUD**, timezone **Australia/Sydney** (mismatch with the Swedish market — flagged in Section 6)
- **Merchant Center:** live product feed pushed daily via SFTP
- **Products (SEK):**

| Product | Handle | Price |
|---|---|---|
| Duschvattenfilter (shower water filter) | `nordisk-duschvattenfilter` | 990 |
| Duschhuvud (filtered shower head) | `nordisk-duschhuvud` | 1199 |
| Wellness Kit | `nordisk-wellness-kit` | 2189 |
| Full Home Filtration | `full-home-filtration` | 4283 |
| Ersättningspatron (replacement cartridge) | `nordisk-duschfilter-ersattningspatron` | 398 |

- **Landing page inventory (Swedish):** GemPages landers (`/pages/se-4`, `/pages/sv-pre-checkout-v1`), content pages (`/pages/torr-hud-efter-duschen-duschfilter`, `/pages/duschfilter-jamforelse-bast-i-test`, `/pages/hard-water-in-sweden`, `/pages/science`, `/pages/tungmetaller-i-duschvatten`), product pages, plus an English `/en/` tree and a `/fr/` tree.
- **Competitive set:** 12 competitors already profiled in a DB table (`competitors`) — Velluva, Aqua Swedish, StoneStream, vattenrenare.se, Comforth, Aqualux, DuschVital, duschfilter.se, Kinetic Reactor, svenskavattenfilter.se, Amazon international (Sparkpod/Magichome/AquaBliss), Onlinefilter — with pricing, filtration media, strengths, weaknesses, positioning.
- **Scale:** small. This is a bootstrapped store, not a brand with a media team. Total Google Ads spend to date is on the order of a few hundred AUD. Every design choice must be proportionate: a system that needs 50 conversions/day to train is useless here.

---

## 3. VERIFIED CURRENT STATE — TOOLS, DATA STREAMS, CREDENTIALS

Everything below was checked live on 2026-09-23. This is your build surface. Trust it over any generic assumption about "what a marketing stack looks like."

### 3.1 Server & runtime

- Single Linux box (Hetzner ARM64), root access, Docker available.
- Primary data volume: `/mnt/HC_Volume_105587324/nordisk` — the whole Nordisk operation lives here.
- `/dev/sdb` (30G) is off-limits. Never write to it.
- `sqlite3` is the database layer. No Postgres, no warehouse.
- `cron` is the scheduler. There is also a Hermes `cronjob` tool for agent-native scheduled jobs.
- Python 3.12 available; a Go toolchain is present; Node available.
- Agent framework: **Hermes Agent** (CLI + tool ecosystem: terminal, browser, web search, MCP, session recall) plus a local **MemPalace** MCP server (knowledge graph + semantic search + agent diary) and **GBrain** (wiki/docs index). Both are usable by an autonomous loop.
- There is an existing SkilOpt pipeline that scores/evolves agent skills, a `harness-opt` directory with automated "noticing" and credential-healing jobs, and nightly infra doctors. **These are precedents for how self-healing is done on this box — study the pattern (observe → gate → heal → verify → log) and reuse it.**

### 3.2 Google Ads — WRITE-CAPABLE, and this is the big enabler

- **Tool:** `google-ads-pp-cli` at `/root/go/bin/google-ads-pp-cli`, version `2026.9.1`. Published by the CLI vendor, wraps Google Ads API **v22**.
- **Doctor output (live):** `api: reachable`, `auth: configured`, `credentials: valid`, `env_vars: OK 3/3`.
- **It is not read-only.** Confirmed mutate-capable command families include:
  - `customers-campaigns` → `mutate` (create/update/remove campaigns)
  - `customers-ad-groups` → create/update/remove ad groups
  - `customers-ad-group-ads` / `customers-ads` → create/update ads, RSAs
  - `customers-ad-group-criteria` → **keywords, negative keywords, audience criteria** (full `--operations` JSON array)
  - `customers-campaign-criteria` → campaign-level negatives
  - `customers-customer-negative-criteria` → account-level shared negatives
  - `customers-shared-criteria` / `customers-shared-sets` → negative keyword lists
  - `customers-campaign-budgets` → **budget create/update**
  - `customers-bidding-strategies`, `customers-bidding-seasonality-adjustments`, `customers-bidding-data-exclusions` → bidding control
  - `customers-conversion-actions`, `customers-custom-conversion-goals`, `customers-conversion-value-rules`, `customers-conversion-value-rule-sets`, `customers-campaign-conversion-goals` → **conversion tracking & value rules**
  - `customers-assets` / `customers-campaign-assets` / `customers-ad-group-assets` / `customers-asset-groups` → RSA assets, image/headline library
  - `customers-keyword-plans`, `customers-keyword-plan-campaigns`, `customers-keyword-plan-ad-groups`, `customers-keyword-plan-ad-group-keywords` → **keyword planning/forecasting (search volume, CPC estimates) via API**
  - `customers-experiments`, `customers-experiment-arms` → A/B campaign experiments
  - `customers-recommendations` + `customers-recommendation-subscriptions` → Google's own recommendations, readable and subscribable
  - `customers-audiences`, `customers-asset-group-signals` → audience targeting
  - `customers-campaign-drafts` → editable drafts (**idea: stage all autonomous changes as drafts internally before pushing**)
- Useful flags for autonomy: `--agent` (JSON + non-interactive defaults), `--dry-run`, `--validate-only`, `--idempotent`, `--ignore-missing`, `--partial-failure`, `--data-source live|local|auto`, `--deliver file:<path>|webhook:<url>`.
- **Auth bootstrap:** `/mnt/HC_Volume_105587324/nordisk/bin/gads-env.sh` — source it, don't execute. It exports `GOOGLE_ADS_ACCESS_TOKEN` (freshly minted), `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`, `GADS_CUSTOMER_ID`, `GADS_CLI`. It is deliberately the *single source of truth* for account IDs because three separate scripts previously hardcoded different customer IDs, drifted, and failed silently for weeks.
- **OAuth helper:** `/mnt/HC_Volume_105587324/nordisk/bin/gads-auth.py` with subcommands `url`, `finish <url|code>`, `refresh`, `check`, `cfg <key>`. Config at `/root/.config/google-ads-pp-cli/config.toml` (mode 600). Refresh tokens have been revoked before — re-auth requires a human to open a consent URL in a browser and paste the redirect back. **This is the one human-in-the-loop step that cannot be automated away with the current OAuth client. It must be designed around (see Section 6).**
- **Local cache:** `/root/.local/share/google-ads-pp-cli/data.db` (~800KB). Currently `sync_state` is empty — `sync` has never been run. Hydrating it would enable fast local SQL reads.

### 3.3 Google Ads — live account contents (30-day window, pulled today)

**Campaigns, all statuses:**

| ID | Name | Status | 30d impr | 30d clicks | 30d cost (AUD) | 30d conv |
|---|---|---|---|---|---|---|
| 23908048771 | SV SE \| Brand - Search | **ENABLED** | 90 | 34 | 38.45 | 0.61 |
| 24031947551 | SV SE \| Discovery \| Broad Match | **ENABLED** | 88 | 5 | 9.79 | 0 |
| 24219641400 | SV SE \| Conquest \| Competitors | **ENABLED** | 0 | 0 | 0 | 0 |
| 23908048774 | SV SE \| Search \| Investigative | PAUSED | 1,024 | 141 | 294.88 | 0 |
| 24032103599 | EU EN \| Discovery \| Broad Match | PAUSED | 1,033 | 43 | 126.94 | 0 |
| 23908048777 | SV SE \| Search \| Chlorine | PAUSED | 0 | 0 | 0 | 0 |
| 23908048774 + 24 others | legacy SE/EU/DK/FR/BE/LU/PMax/Shopping experiments | PAUSED or REMOVED | — | — | — | — |

(30 campaign records in total; 3 ENABLED, the rest paused or removed.)

Note the shape of this: **the only campaign that ever produced a conversion is Brand Search** (0.61 conv on 38.45 AUD — and brand conversion is largely cannibalising organic demand, not creating it). The Investigative search campaign burned 294.88 AUD over 141 clicks for **zero** conversions before being paused. Two of the three ENABLED campaigns are effectively dormant (Conquest has zero impressions; Discovery is at ~10 AUD/30d). **The account is not currently a working acquisition machine. It is a graveyard with three live remnants.**

**Conversion actions (this is a serious problem you must address):**

| ID | Name | Type | Status | Primary for goal |
|---|---|---|---|---|
| 6878142622 | Nordisk Renhet (web) purchase | GA4 import | **ENABLED** | yes |
| 6882963286 | Purchase (GA4 event `add_payment_info`) | GA4 import | **ENABLED** | yes |
| 6882963292 | Submit lead form (GA4 event `form_submit`) | GA4 import | **ENABLED** | yes |
| 6882963745 | Add to cart (GA4 event `add_to_cart`) | GA4 import | **ENABLED** | yes |
| — | 24 further actions | — | REMOVED | — |

Four ENABLED actions are all flagged `primary_for_goal = true`, and one of them is a *purchase* action bound to `add_payment_info` (a mid-funnel event) while another binds purchase to `form_submit`. **Bidding strategies that optimise to "conversions" are currently being fed a mixture of purchases, add-to-carts, form submissions, and payment-info events as if they were equivalent.** This alone can explain historically incoherent optimisation. Any real system must fix conversion hygiene before it can be trusted to make decisions.

**Ad structure:** at least one ad group with 19 keywords and multiple RSAs, each RSA bound to a different landing page and a bucketed theme (e.g. "Hudproblem" → `/pages/itchy-skin`; "Klor & Vatten" → product page; "Guide / Jämför" → `/pages/se-4`). A structured context file documents these mappings at `/mnt/HC_Volume_105587324/nordisk/ads/nordisk_ads_context.json`. So the germ of intent→keyword→ad→landing-page mapping exists and should be formalised, not discarded.

### 3.4 Google Analytics 4

- **Helper:** `/root/.nordisk/scripts/ga4-read.py` — uses a service-account keyfile (`/root/.nordisk/keys/google-service-account.json`), talks to the GA4 Data API for property `454852488`.
- **Subcommands:** `realtime [eventFilter]`, `report <metrics> <dims> [daysAgo]`, `tx [daysAgo]`.
- **Verified working, e.g.:**
  - `report itemRevenue,itemsPurchased itemName 30` → product-level revenue (7 products with sales in 30d; top: Duschvattenfilter 473.07, Duschhuvud 268.58, Ersättningspatron 148.86)
  - `report sessions,transactions,eventCount sessionDefaultChannelGroup 7` → channel split (Organic Search 251, Direct 140, Paid Search 21, AI Assistant 10, Referral 8...)
  - `report sessions,advertiserAdCost,transactions sessionCampaignName 30` → **campaign-level ad cost joined to on-site behaviour**, including campaign names matching Google Ads, plus `(organic)`, `(direct)`, `(ai-assistant)`, `(referral)`, `(cross-network)` rows
  - `report sessions,purchaseRevenue landingPagePlusQueryString 30`
  - `tx 7` → transaction IDs and revenue
- **Known gap:** at campaign level, `transactions` returns **0** for every paid campaign while `advertiserAdCost` returns real numbers. Revenue is visible at item level and in `tx`, but the paid-campaign → transaction join is not currently resolving. **Diagnosing and fixing this attribution break is a prerequisite for the whole ROAS mission.**
- GA4 has an `AI Assistant` channel group — the store already receives AI-referred traffic. Worth a channel-specific strategy later.

### 3.5 Google Search Console

- **Harvester:** `/mnt/HC_Volume_105587324/nordisk/bin/harvesters/gsc.sh` — service account, mints its own JWT, scope `webmasters`.
- **Table:** `traffic_daily` in `nordisk.db` — `date, query, page, clicks, impressions, ctr, position`. **70,678 rows** (re-verified 2026-09-23; it grows with every daily harvest), freshest date 2026-09-21, indexed on date and page. The live DB is `/mnt/HC_Volume_105587324/nordisk/db/nordisk.db` (per `NORDISK_DB` in `.env`) — be aware a **zero-byte decoy** `/mnt/HC_Volume_105587324/nordisk/nordisk.db` exists at the volume root, and a relative-path misread silently yields an empty database. Use the absolute `db/` path.
- This is a *rich, underused* asset: full organic query-level and page-level demand signal. Organic queries that convert are the single best source of paid keyword ideas, and organic pages already ranking are the best landing-page candidates. **Your design should explicitly fuse GSC demand into paid keyword/lander selection.** `traffic_daily_2` is present but empty. (`gsc_archetype_mapping` lives in `ads_decisions.db`, not here — see 3.10.)

### 3.6 Shopify

- **Harvester:** `bin/harvesters/shopify.sh` → `bin/resync-orders.py` (Shopify Admin API, direct REST call with an admin token).
- **Tables:** `orders` (111 rows — id, shopify_id, email, name, total_price, currency, financial_status, fulfillment_status, source_name, city, country, created_at, plus `landing_site` and `referring_site`), `products` (31 rows, richly translated: SV/EN/FR titles, descriptions, meta, H1, plus filtration-media spec fields), `customers` (221 rows).
- **Known gaps (important):**
  1. **No line-items table.** Orders carry only order totals. You cannot currently answer "which product did this order contain" from Shopify data. Combined with GA4 item-level revenue, you can approximate product performance — but a first-class system should ingest `line_items` and build real product-level contribution.
  2. `landing_site` is populated for only ~22 recent orders; `source_name` is `web` for 72 orders, with `shopify_draft_order` (35), `subscription_contract_checkout_one` (3) also present. **Attribution from order → campaign is essentially absent.** `landing_site` + `referring_site` is a weak proxy. UTM discipline is not enforced.
  3. The admin token is currently **hardcoded in the harvest script**. It should be moved to the secrets store (see 3.9).
- **Shopify Admin API is available** with scopes sufficient for orders, products, customers — and can be extended to checkout/abandoned-cart data.

### 3.7 Klaviyo (email/SMS)

- **Correction to a likely assumption: `klaviyo-pp-cli` is NOT installed here.** Only its Go source (`/root/printing-press/library/klaviyo-pp-cli`) and a config (`/root/.config/klaviyo-pp-cli/config.toml`) exist; there is no binary on `PATH`. Any design step that shells out to `klaviyo-pp-cli` is a **build task**, not a given — or work from the API directly with `KLAVIYO_TOKEN`.
- **The Klaviyo data is already in `nordisk.db`** (harvested by `bin/harvesters/`), not in a CLI cache: `klaviyo_flows` (24 rows), `klaviyo_daily` (402), `klaviyo_campaigns` (2), `klaviyo_flow_metrics` (**0 — never populated**). `KLAVIYO_TOKEN` is present in `nordisk/.env`.
- Relevance: owned-channel performance tells you whether paid traffic that *fails to convert immediately* is nonetheless joining flows and converting later. **Lagged contribution and assisted revenue are part of honest ROAS.** Even if Klaviyo stays peripheral, the design must not claim a "loser" on same-day data alone.

### 3.8 Google Merchant Center

- `bin/harvesters/gmc-feed.py` — pulls live Shopify data, applies SV/EN/FR translations, generates TSV feeds, pushes via SFTP to `partnerupload.google.com:19321`. Log is fresh.
- **No performance data is being ingested back from Merchant Center.** Free listings / Shopping surface clicks, impressions, and the feed's disapproval diagnostics are all available via the Content API and are currently dark. Shopping/PMax is a natural scaling surface for a physical-goods store with a live feed.

### 3.9 Credentials & secrets

- `/root/.secrets.env` holds: `GOOGLE_ADS_DEVELOPER_TOKEN`, `GA4_MP_API_SECRET`, `APIFY_TOKEN`, `SERPER_API_KEY`.
- `/mnt/HC_Volume_105587324/nordisk/.env` holds: `SHOPIFY_SHOP`, `SHOPIFY_TOKEN`, `KLAVIYO_TOKEN`, `GSC_ACCESS_TOKEN`, `NORDISK_DB`, `GMC_SFTP_*`, `PORT`.
- There is a vault/secrets-management convention on this box (see the `vault-secrets-management` skill) and an automated credential-healing cron job that is **gated** on an eval suite passing before it writes anything. Respect both.
- **The re-auth path for Google Ads OAuth is the single most fragile dependency in the system** and it has failed before, for weeks, silently.

### 3.10 Agent memory & knowledge layer (available to the autonomous loop)

- **MemPalace MCP** at `127.0.0.1:8797/mcp` — knowledge graph (entities + typed triples), semantic search over document drawers, and an agent diary. CLI available as `mempalace-cli` (`search`, `diary-write`, `kg-add`, `kg-query`). **Currently contains almost nothing about ads** — one triple: `Google Ads --auth_depends_on--> Composio`. There is an `ads-creative-ops` wing with a document on completing creative feedback loops (winner / high-potential / loser triage pipeline).
- **GBrain** — wiki + agent-architecture docs, searchable via `gbrain search`. ~92 pages, ~1,751 chunks.
- **Session history** — full past-session search (`session_search`).
- **`ads_decisions.db`** — separate SQLite file with tables `ad_audit_runs`, `ad_audit_performance`, `ad_audit_calibration`, `ad_audit_persona_updates`, `ad_audit_archetype_weights`, `gsc_archetype_mapping`. An **ad-creative audit system with persona/archetype calibration already exists** and should be inspected and reused rather than replaced.
- **Research DB:** `/root/nordisk-research.db` (query before external research; note one table's traffic numbers are inflated ~4.8×).

### 3.11 Supporting automation already running (context for what "self-healing" looks like here)

- `bin/harvesters/run-all.sh` — daily 06:07, runs GSC → Shopify → Klaviyo → Google Ads → compute-metrics → GMC feed → ads-monitor → sync-agent-config, sequentially, logging to `cron/harvest.log`. `compute-metrics` writes the derived `daily_metrics(date, metric_name, metric_value)` table in `nordisk.db` (344 rows).
- `bin/pixel-tracker/nordisk-infra-doctor.py` — daily 05:07, services + endpoints + TLS + DNS + webhook registration + tracker DB + GA4 + Google Ads, then emails a verdict (see 3.12). Also `bin/keyword-intel.py` — Mondays 04:17 (see 3.13).
- `bin/harvesters/ads-monitor.sh` — daily 06:37. Reports ENABLED-campaign health, flags waste in search terms against a hardcoded waste-word list (`lotion`, `cream`, `moisturizer`, `shampoo`, `lidl`, `bunnings`, competitor brands...), writes findings to the MemPalace diary. **Read-only. Makes no changes.**
- `bin/weekly-ads-checkpoint.sh` — Mondays 07:07, writes `cron/ads-weekly-checkpoint.json`.
- **Several cron watchdogs**: Caddy/static-server health every minute, an infra doctor nightly, a harness "comb" that notices issues hourly, a credential-heal actor every 30 minutes (gated).
- There is also an autonomous **organic content pipeline** (topic mining → research → write → 3-reviewer MOE → publish to Shopify) that already runs unattended. **Its architecture — nightly candidate generation, review gate, verification, publish, notify, self-logging — is the closest existing analogue to what you're being asked to design for paid.** Study it as a template.

### 3.12 First-party conversion tracking — server-side purchase feed (ALREADY LIVE — extend this, don't rebuild)

The owner called tracking "highly vital". Part of it exists, in production, right now. It is the single most important thing in this document to not accidentally design over.

- **Receiver:** `nordisk-tracker.service` (systemd, `Restart=always`) runs `/mnt/HC_Volume_105587324/nordisk/bin/pixel-tracker/tracker.py` — a stdlib `ThreadingHTTPServer` on `127.0.0.1:9123`, published via Caddy at `https://nordisk.vektal.systems/track/purchase` (endpoint live, HTTP 200).
- **Path:** Shopify **web pixel** (`checkout_completed`) → POST to the tracker → validated → row appended to `pixel_track.db` → forwarded to **GA4 Measurement Protocol** (measurement ID `G-YJP5QDGTHD`; `api_secret` read from `/root/.secrets.env`, deliberately never in browser code).
- **Web-pixel source + runbook:** `bin/token-obtainer/webpixel-backup/` (`custom_pixel.js`, `pixel_src_index.js`, `container_pre_edit.json`, `WEBPIXEL_RUNBOOK_2026-09-07.md`).
- **`db/pixel_track.db` tables:**
  - `purchases(transaction_id PK, received_at, client_id, value, currency, ga4_status, ga4_response, raw, source)` — a **first-party conversion record that stores the GA4 MP HTTP status per row**. 12 rows today: 9 × `204` accepted, 3 × `503 no api_secret configured` (historical, on synthetic `test-1..test-3`; the secret is in place now).
  - `order_webhooks(order_id PK, received_at, name, total, currency, raw)` — Shopify `orders/create` webhook (registration confirmed green by the doctor), 11 rows.
- **Why it matters to the ROAS mission:** this is a **server-side, first-party** purchase record carrying a `client_id`, independent of client-side/cookie GA4 and therefore durable under consent loss and ad-blockers. It is the natural spine for the Ads ↔ Shopify ↔ GA4 reconciliation demanded in Section 10.6, and the credible place to anchor "prove a click became an order".
- **It already has a self-healing precedent — study and evolve it, don't duplicate it:** `bin/pixel-tracker/nordisk-infra-doctor.py` runs daily at 05:07 and checks services, public endpoints, TLS expiry, DNS (SPF/MX/**DKIM**), the Shopify webhook registration, the tracker DB, GA4 read+realtime, the Google Ads refresh path and the Google Ads conversion read — then emails a verdict line.
  - Its **2026-09-23 verdict was `FAIL`**, and the failures are live problems: Google Ads refresh `TOKEN_REFRESH_FAILED` (intermittent — a manual `gads-auth.py check` later the same day succeeded and reported `live API OK`); GA4 read/realtime probe `purchases(30m)=0`; **DKIM record missing for `vektal.systems`** (SPF and MX pass). It also reports Google Ads conversions as **24–48h import-lagged**: `7d=0.000 ($0.00)`, `30d=0.000 ($27.53 AUD)` — i.e. **conversion *value* present with a zero conversion *count***, another attribution-hygiene symptom.

### 3.13 Keyword intelligence database (pre-existing, underused)

- `db/keyword-intel.db` (~1.2MB), produced by `bin/keyword-intel.py` (cron: Mondays 04:17 — `all`, then `seed-topics --limit 8 --per-theme 1`):
  - `kw_ideas` **4,298 rows**, `gsc_query` **835**, `gap_ideas` **438**, `competitor_pages` **1,839**.
- This is mined demand + content-gap intelligence that already exists and is barely wired into anything. **It should be a primary input to the keyword-intelligence and idea-pipeline subsystems (7.4 and 7.1), not a rebuild.**
  - Under the hood (verified): Google Autosuggest (`suggestqueries.google.com`, `hl=sv&gl=se`, alphabet + question-prefix expansion), competitor Shopify sitemaps, and GSC `traffic_daily` for real positions; SV/EN intent classification, theme clustering, Jaccard dedupe. `bin/nightly-topic.py` (GSC-based topic finder, classifies one-push-away / content-gap / decay-rescue) feeds the organic pipeline from the same family of signal.

### 3.14 General agent tooling available to the autonomous loop (verified present on the box)

These are not ads tools, but they are what a reasoning/generative layer can actually call. Every "the system researches competitors / writes copy / checks a landing page" step must be built from this list, and nothing else.

**Research, scraping and SERP**
- `research-unified` (invoked as `research`) — unified CLI over Tavily → Exa → Apify → Composio → Context7 → Brave → Browser Use, with MemPalace caching: `search`, `deep`, `extract <url>`, `docs`, `similar <url>`, `news`, `scholar`, `social`, `scrape <url>`, `browse <goal>`, `status`, `cache <query>`. Also on PATH: `tvly`, `tavily-pp`.
- Keys held: `TAVILY_API_KEY`, `EXA_API_KEY`, `APIFY_API_KEY`/`APIFY_TOKEN`, `FIRECRAWL_API_KEY`, `BROWSERBASE_API_KEY`+`PROJECT_ID`, `SERPER_API_KEY` (real SERP results → rank tracking), `OCTEN_API_KEY` (semantic index — **not** a SERP), in `/root/.env.unified` and `/root/.secrets.env`.
  - Caveat: `TAVILY_API_KEY` is present in `/root/.env.unified`, yet the Nordisk competitor path has previously failed for a *missing* key (Section 4.9). Verify the key resolves in the pipeline's own environment before depending on it.
- **Local browser is the reliable fallback**: `chromium-browser` / `google-chrome`, headless CDP profile dir at `/root/.chrome-cdp`, Playwright, `camofox`. Composio is dead (Section 4.3) and Browser Use Cloud is a paid external — do not put either on a critical path.
- **20 Nordisk-specific `nr*` helpers on PATH** for landing-page and creative QA: `nrshot.js`, `nrdiff`, `nrdifft`, `nrvisdiff`, `nrcmp`, `nralign`, `nrmobile.js`, `nrstruct.js`, `nrtext.js`, `nrtop.js`, `nrwhere.js`, `nrverify`, `nrscout`, `nrextract.js`, `nrtheme`, `nrsecoffsets.js`, `nrbuild`, `nrcontent`, `nrperf` (PageSpeed/Lighthouse). `nrvision` (Gemini flash) returns style-fit judgement + Swedish alt text — **use it for automated screenshot judgement of landers and ad creative.**

**LLM access and orchestration**
- `OPENROUTER_API_KEY`, `ORCAROUTER_API_KEY` (self-hosted gateway at `/mnt/HC_Volume_105587324/orcarouter-lite/`), `OPENAI_API_KEY`, `GOOGLE_AI_STUDIO_API_KEY`. Model routing for the reasoning/generative layers goes through these; there is no budget for fine-tuning and no GPU.
- Hermes agent primitives: subagents, worktree isolation, cron jobs, MCP toolsets, `session_search` — plus the eval/MOE pattern (`judge-reasoning.py`, `judge-reliability.py`, 3-reviewer pre-publish gate) in `/root/loops/nordisk-comparison-pipeline/`.
- **`pi-moa` is NOT on `PATH`** (a Revision-1 note assumed it was). Fan-out to multiple reference models must be built from the OpenRouter/Orcarouter keys directly.

**Memory, knowledge and self-improvement substrate**
- MemPalace MCP at `127.0.0.1:8797/mcp` (palace at `/root/.mempalace/palace`; **the older `/root/palace/` is stale legacy — don't read it**) — KG, Chroma semantic search, agent diary. GBrain (`gbrain search`, ~92 pages / ~1,751 chunks). Session history via `session_search`.
- `/root/loops/` contains `nordisk-comparison-pipeline` (full autonomous article pipeline: discovery → demand → research → enrichment → ground → draft → eval → moe → humanizer → swedish_polish → verify → publish), `nordisk-content-graph`, plus `disk-health-watchdog.md`. `/root/harness-opt/` holds the read-only noticing comb, the gated credential-heal actor and its eval-suite gate. A SkillOpt L1–L7 pipeline scores and evolves skills.
- **`nodes/nordisk_self.py` in the comparison pipeline is the canonical-facts pattern to copy**: Nordisk's own product facts load from a `product_facts` table so no script can hardcode a wrong spec. The ads system needs the same for products, prices, ICP and claims.

**Runtime and limits**
- ~20 active cron entries; SQLite everywhere (`nordisk.db`, `ads_decisions.db`, `keyword-intel.db`, `pixel_track.db`, `nordisk-research.db`, comparison-pipeline `competitors.db`). Temporal skills are installed and a Postgres is *declared* at `localhost:5433` (`DB_USER=temporal`, `DB_NAME=company_os`) — **but nothing is listening on 5433 right now**; treat durable workflow infra as a build decision, not an existing capability.
- Disk headroom (verified 2026-09-23): `/` **38G, 82% used, 6.8G free — the tight one**; `/mnt/HC_Volume_105587324` 40G / 71%; `/mnt/HC_Volume_105573741` 30G / 62%. Keep temp files, screenshots and browser profiles off `/` (headless-Chrome profile dirs in `/tmp` are a recurring disk eater).
- Notifications: Telegram gateway is configured (Section 6 requires a channel he actually reads); `bin/weekly-email.py` exists for email digests. Note DKIM is currently missing for `vektal.systems` (Section 4.15).

### 3.15 What does NOT exist (do not design around it)

- No Meta/Facebook/Instagram, Microsoft/Bing, TikTok or LinkedIn ad API access. YouTube is reachable only through Google Ads, with no dedicated tooling.
- No call tracking, no CRM, no CDP, no attribution product. **No wired server-side GCLID → CRM → offline-conversion loop** — the API surface (`offline_user_data_jobs`) exists; the wiring does not. This is the biggest missing piece for high-quality conversion signals on a store with few purchases.
- No data warehouse beyond SQLite; no cloud autoscaling; one host, one box, no GPU.
- No ads dashboard UI. (A Go `dashboard/` dir exists; assume it must be built, and per Section 9 don't make a dashboard the deliverable anyway.)

---

## 4. WHAT IS ACTUALLY BROKEN OR DARK RIGHT NOW

Do not design around these as if they work. Each is either a blocker or a required early task.

1. **`ads-monitor.sh` campaign-health query returns HTTP 400 `INVALID_ARGUMENT`.** The GAQL reads `campaign_budget.amount_micros` in a `FROM campaign` query; `campaign_budget` is a separate resource and cannot be selected from `campaign`. Result: the spend/budget half of daily monitoring has never produced data. (Fixed 2026-09-23 for other defects; this one is open.)
2. **The same monitor uses a hardcoded waste-keyword list** rather than a managed negative-keyword strategy, and it only *reports* waste — nothing is ever negated. There is no negative-keyword write path in production.
3. **Composio is dead** — `composio connections list` returns `HTTP 401 Unauthorized`. `bin/harvesters/google-ads.sh` (the daily Google Ads harvester) depends on Composio and therefore harvests nothing. Live Ads data currently reaches SQLite only via the ad-hoc `refresh-ads-data.sh` / `ingest-ads.py` path (`ads_campaigns` has 348 rows, 21 distinct campaigns, freshest 2026-09-23 — so *something* works, but the mainline harvester does not).
4. **`ads_campaigns` is campaign-granularity only** — `id, name, status, cost_micros, impressions, clicks, conversions, conversion_value, date`. **There is no ad-group, ad, keyword, search-term, geo, device, or time-of-day performance table.** You cannot currently evaluate a keyword, an RSA, or a landing page from paid data. This is the largest single data gap.
5. **GA4 paid-campaign → transaction join returns zero.** `advertiserAdCost` is populated per campaign; `transactions` is 0 for all of them. Revenue attribution to paid campaigns is broken or unconfigured.
6. **Conversion action dilution** — four primary actions, two of them mis-bound mid-funnel events (3.3).
7. **`weekly-ads-checkpoint.sh` failed 8 of its last 9 Monday runs** (revoked refresh token, wrong customer ID). Its one "success" produced all zeros and then reported "minimal spend this week, no conversion data yet — normal for low-traffic period." **A broken job manufacturing a confident all-clear is the exact failure this system must be immune to.**
8. **Account timezone is Australia/Sydney while the market, store, and ad schedule are Swedish.** Daily boundaries, dayparting, and week-over-week comparisons are all offset by ~9-10 hours. Any daily-bucket logic must handle this explicitly.
9. **Tavily API key is missing** (referenced by competitor-discovery code paths); the Ads refresh token has been revoked historically.
10. **No write path exists anywhere.** The entire ads toolchain today is monitoring and reporting. Zero mutations have ever been automated.
11. **Shopify line items are not ingested** — no product-level order attribution.
12. **Merchant Center performance is not ingested** — no Shopping/PMax surface visibility.
13. **The Google Ads OAuth refresh path flaps.** The 2026-09-23 05:07 doctor recorded `TOKEN_REFRESH_FAILED` while a manual `gads-auth.py check` hours later returned `live API OK` with `token_expiry` ~1 hour out. So the access token lives ~1h, the refresh intermittently fails, and **every consumer must assume auth can die between runs** — detect, alert, degrade to observe-only, never report zeros.
14. **Nothing currently proves the tracking chain end-to-end.** The tracker accepts and forwards purchases (9 × `204`), but the doctor's GA4 read/realtime probe still returns `purchases(30m)=0`, and Google Ads reports conversion value with a zero conversion count. **Tracker → GA4 → Google Ads is unverified as a chain.** This is the verification job Section 10.6 asks for, and it is currently absent.
15. **DKIM is missing for `vektal.systems`** (SPF/MX pass). The system's reporting channel is email/digest-shaped — a digest that lands in spam is functionally the same as no digest.
16. **Google Ads conversion import lag is 24–48h** and must be modelled: any optimisation loop that reads "yesterday's conversions" is reading an incomplete, still-settling number. Design explicit data-settling windows rather than trusting the freshest row.

---

## 5. THE CORE DESIGN PROBLEM

State it plainly, because it governs everything:

**The account is tiny, the conversion signal is nearly nonexistent, and the existing data linkage is broken. A naive "optimise on ROAS" loop will thrash — it will see noise, declare winners, reallocate, see different noise, and reverse itself, burning real money in the process. Simultaneously, a passive loop will do nothing, because with 0.61 conversions in 30 days almost no entity crosses a statistical significance threshold.**

So the design must solve a two-sided problem:

- **How to make a feedback signal exist at all** (fix attribution, fix conversion hygiene, create leading indicators that precede purchases, fuse GA4 + Shopify + GSC + Ads into one honest revenue-per-source view).
- **How to act decisively without over-fitting noise** (hierarchical pooling, conservative priors, minimum-data guards, exploration budgets, the distinction between "no evidence of effect" and "evidence of no effect", and — critically — the distinction between "this is a loser" and "this is measured badly").

Every decision rule you propose must state **what it does when the data is insufficient**, and the default there must be *escalate to a human digest*, never *act anyway* and never *silently do nothing*.

---

## 6. HARD CONSTRAINTS AND GROUND RULES

These are non-negotiable. The design must obey them.

**Safety and reversibility**
- Real money, real account, no sandbox. All first-time mutations must be `--validate-only` or `--dry-run` first, then applied, then verified by re-reading state.
- Prefer **reversible actions**: pausing beats deleting; budget changes beat campaign restructures; negative keywords beat removing keywords; drafts beat live pushes.
- Never spend above a hard, owner-set total daily budget cap, enforced independently of the optimiser's own logic (a kill-switch layer the optimiser cannot override).
- Never remove a campaign, ad group, ad, or conversion action without a documented two-step deprecation (pause → observe → remove), and never remove conversion actions at all without human sign-off.
- No bulk destructive operations. Every mutation batch is bounded in size, and any operation touching more than N entities must be staged and reviewed.
- Ask before destructive operations. Never ask permission for read-only work.

**Truthfulness (the hardest rule)**
- Never write unverified numbers to files or databases. Re-verify any externally sourced figure by direct API read before persisting it.
- Any "only", "first", "never", "all", or "none" claim requires the full result set to be read, not a truncated view.
- A job that cannot authenticate, cannot reach the API, or receives an empty/unparseable payload must **fail loudly** and mark its outputs as `UNKNOWN`, never `zero`. The `ads-monitor` and `weekly-checkpoint` history is the cautionary tale.
- Distinguish and label three states everywhere: `MEASURED_ZERO` (we looked, it was genuinely zero), `NO_DATA` (we looked, there was nothing to see), `BROKEN` (we couldn't look). Conflating these is the bug that cost this account nine weeks.

**Autonomy boundaries**
- **The end-state authority is full autonomous launch.** The system creates campaigns, ad groups, ads, keywords, negatives, budgets and bids on its own, with no pre-approval. This is the target, not a stretch goal. A design that only *proposes* campaigns has failed the brief.
- **Autonomy is earned in stages, not granted at t=0** (trust ladder below). It starts with reversible mutation classes and unlocks launch authority by proving it can correctly attribute outcomes to its own actions, measured against its own predictions.
- **Escalate ≠ ask permission.** Notifications and approval requests are different mechanisms. Never gate routine work on owner input.
- **Silence means proceed, not stop.** Any proposal step must carry a bounded default action that executes after a stated window if the owner doesn't reply. An approval gate where no-reply = no-action is functionally "he has to guide it" and fails the brief. He gets **after-the-fact veto with a documented rollback**, not veto-by-inaction.
- The only true **blocking** gates are: exceeding the hard spend cap, changing account-level conversion goals / attribution settings / value rules, and anything not cleanly reversible on Google's side (removing conversion actions, hard-deleting campaigns — pause instead).
- Every autonomous launch happens inside a **bounded incubation envelope** so being wrong is survivable: new entities start capped, time-boxed, and pre-committed to auto-kill conditions.
- The escalation channel must be a real messaging platform he reads (Telegram is wired for this box). A digest nobody receives is the same as silence.
- The owner's stated preference: **he does not want to guide it.** The digest's default posture is *it already acted, here's what and why* — not *please approve my routine work*.

**Progressive trust ladder — define each stage and its promotion/demotion criteria:**

| Stage | Unlocked | Promotion criterion |
|---|---|---|
| 0 **Observe** | read-only. Records would-be decisions + predicted effects, acts on nothing | 14 days with attribution verified end-to-end and its own predicted-vs-actual reconciliations inside a stated error band |
| 1 **Reversible** | negative keywords, keyword/entity pauses, creative rotation, budget reallocation inside cap | a stated run of decisions with zero guardrail breaches |
| 2 **Build** | new ad groups, new ads/RSA variants, new keywords inside existing campaigns | attribution proven on entities it created at this stage |
| 3 **Launch** | new campaigns from scratch, new campaign types (Shopping/PMax/Demand Gen/Video) | launched entities that hit their leading-indicator floor, *and* it correctly auto-killed the ones that didn't |
| 4 **Scale** | budget expansion above baseline, geo/audience expansion, larger exploration allocation | sustained contribution above target across a stated horizon |

**Demotion must exist.** A guardrail breach, a mis-attributed outcome, a spend anomaly, or a broken tracking pipeline drops the system back a stage automatically — and it must announce that in the digest, not hide it.

**Launch envelope — the default bound on any self-initiated entity:**
- Capped at N% of the hard daily budget for its first M days (architect sets N and M with justification for this account's scale).
- **Mandatory pre-flight, all must pass before anything executes:**
  - the landing page returns HTTP 200 with a direct fetch — a 301 means the URL is wrong, not a redirect to follow;
  - conversion tracking present and verified live on that path;
  - UTM standard applied so the entity is attributable from day one;
  - copy passes Google policy + Swedish language-quality + claims-compliance gates;
  - not a duplicate of an entity already in the memory-of-failure store;
  - a written hypothesis: what it tests, the metric that confirms or refutes it, a predicted value with a confidence, and a deadline.
- **Pre-committed auto-kill.** If it misses its leading-indicator floor by its deadline, it pauses itself and writes the negative result to memory. No owner action required.
- Every launch lands in the decision ledger with a rollback handle. Pause beats delete. Drafts are the staging mechanism.

**Operational**
- Everything runs on cron on one box, in Python/Shell/SQLite, against these CLIs. No new infrastructure unless you justify it hard.
- Every job logs to a file, writes a structured run record, and is idempotent (safe to re-run).
- Every job has a freshness assertion: if its input data is older than X, it refuses to conclude and reports `STALE`.
- Every job self-heals the failure classes it can (retry with backoff on transient API errors, re-mint tokens, re-run ingest) and escalates the classes it can't (human re-auth).
- Never touch `/dev/sdb`.
- Respect the existing `review/` skill-protection convention and the gated credential-healer — do not bypass safety gates that already exist.
- Do not hardcode account IDs, developer tokens, or customer IDs in callers. `gads-env.sh` is the single source of truth; extend that pattern.

---

## 7. EXPLICIT REQUIREMENTS (what the owner asked for)

Design must cover all of these — each as a named subsystem with inputs, decision logic, outputs, and failure behaviour:

1. **Self-initiating campaign creation.** The system launches new campaigns without a prompt. What triggers a launch? What is the idea pipeline? Where do keywords come from? What validates a launch is worth the spend? What envelope does it launch inside, and what is the pre-committed condition under which it kills its own campaign? A design where a human clicks "approve" before a campaign goes live does not satisfy this requirement.
2. **Self-initiating ad group creation** — new themes/buckets within campaigns, with keyword sets and matched ad copy.
3. **Self-initiating ad creation** — new RSAs, headlines, descriptions, sitelinks, callouts, images. Where does copy come from? How is it validated (policy, brand voice, Swedish language quality, claims legality)?
4. **Keyword intelligence** — discovery, expansion, grouping, match-type strategy, and how search volume/CPC forecasts (`keyword-plans`) feed selection.
5. **Negative keyword intelligence** — waste detection from search terms, automatic negation, shared negative lists, campaign- and account-level negatives, and a growing, managed negative vocabulary *instead of the current hardcoded list*.
6. **Language handling** — Swedish first, with EN and FR trees present. Per-language campaign/ad/keyword/lander coherence. Language-specific copywriting quality gates. Note: agent communication is English, all Swedish customer-facing content must be native-quality Swedish.
7. **Landing page selection and management** — which URL for which intent. A landing page registry. Detection of lander underperformance vs ad/keyword underperformance (attributing the failure to the right layer). Landers include GemPages, content pages, and product pages.
8. **Awareness stage and customer journey mapping** — campaigns/ad groups mapped to awareness stage (unaware → problem-aware → solution-aware → product-aware → most-aware) and to journey stage (research → comparison → consideration → purchase → retention). Ad copy and lander must match stage. Measurement must differ by stage (a problem-aware campaign should not be judged on last-click ROAS alone).
9. **ICP and pain points** — a modelled ideal customer profile, with pain points (dry/itchy skin, hard water, chlorine, heavy metals, hair damage, allergies), and a mapping from pain point → keyword → ad → lander → product.
10. **Brand vs non-brand discipline** — currently the only "converting" campaign is Brand Search, which mostly harvests existing demand. Brand and non-brand must be evaluated separately, with different goals and truthfully reported contribution (including incrementality, or at minimum a clear-eyed acknowledgement that brand ROAS overstates acquisition).
11. **Competition** — the 12-competitor table is a starting asset. Conquesting, competitor-name bidding policy, comparison content, differentiation claims, and competitive-share monitoring via Auction Insights.
12. **Educational / informational / purchase-intent content orchestration** — different content classes for different funnel positions, each with its own ad formats, landers, and success metrics. Fusing the existing organic content pipeline (which already produces comparison and educational articles) with paid strategy.
13. **Autonomous monitoring** — continuous, multi-granularity, anomaly-aware.
14. **Reasoning built in / judgement made** — the system explains its decisions in structured, auditable form. Not a black box: every action carries a recorded rationale, the evidence it was based on, and a confidence level. Decisions must be reviewable after the fact.
15. **Product-level performance as the primary lens** — "what products get the most clicks and impressions and sales in the end effect." Clicks and impressions are leading; sales are ground truth. Need clicks → sessions → add-to-cart → checkout → purchase → revenue per product, per campaign/ad group/keyword, with lag.
16. **Cross-referenced sales.** Sales data must be cross-referenced between Shopify (orders, revenue, currency SEK), GA4 (sessions, events, item revenue, transactions), and Google Ads (conversions, conversion value, in AUD). Three sources, two currencies, different attribution models, different timezone conventions. **The design must specify how these are reconciled, which is authoritative for what, and how discrepancies are surfaced rather than averaged away.**
17. **Tracking set up so the system knows what works.** Explicitly: conversion action hygiene, GA4↔Ads linking, enhanced conversions, UTM discipline on every ad, value-based bidding inputs (conversion value rules), and a verification job that proves the pipeline end-to-end. The owner called this "highly vital" — treat it as the foundation, and design it as *continuously self-verifying*, not set up once.
18. **Budget optimisation** — allocation across campaigns, ad groups, keywords, products, geos, devices, times, within a hard total cap, by measured return, with exploration preserved.
19. **Scaling** — deliberate growth of winners: budget scaling rules, bid scaling, geo expansion, audience expansion, creative multiplication, channel expansion (Shopping/PMax/Demand Gen/Video), with guardrails.
20. **Self-learning** — a persistent, queryable memory of what has been tried and what happened, including *negative results*, feeding future decisions. Must survive restarts, dedupe, and be reviewable by the owner.
21. **Self-healing** — detect and repair the failure classes above; escalate the rest.
22. **ROAS increase as the headline metric**, with a defined measurement period, lag window, attribution model, and honest handling of incrementality and organic cannibalisation.

---

## 8. IMPLIED REQUIREMENTS (what he didn't ask for and needs anyway)

The owner explicitly said he doesn't know what he's missing. This section is the architect's value-add. Cover these, and add anything else the design demands:

- **Incrementality / cannibalisation.** Brand Search "works" because those people were going to buy anyway. Without a geo holdout test or a conversion-lift experiment, ROAS numbers are self-congratulatory. The `customers-experiments` and `customers-experiment-arms` API surface makes geo experiments possible — design one.
- **Statistical discipline for tiny data.** Hierarchical Bayesian pooling (entity → ad group → campaign → account), credible intervals rather than point estimates, explicit minimum-sample guards, sequential-testing awareness, and a documented policy of what the system does when nothing is significant. Without this, "self-learning" becomes "self-flailing."
- **A holdout / exploration budget.** A fixed percentage of spend reserved for testing new ideas, kept separate from performance spend, so the optimiser cannot starve exploration. Without it the system converges on the status quo and stops being self-propelling.
- **LTV and lag.** Purchases arrive after clicks — sometimes days later, sometimes via email after an abandoned cart. Judging campaigns on same-day conversion data will kill campaigns that are actually working. Design the lag window explicitly per channel/stage, and use leading indicators (engaged sessions, add-to-cart, checkout-started, email signup, flow entry) as the early-warning signal.
- **A named, versioned entity model.** Campaigns, ad groups, ads, keywords, landers, intents, personas, products, and the edges between them, as first-class database tables — not as JSON blobs or naming conventions. This is what makes "self-learning" possible: you can only learn across entities you have modelled.
- **Decision ledger and audit trail.** Every action: what, why, evidence, expected effect, confidence, timestamp, actor, rollback path, and — critically — the *outcome* measured later against the expectation. The existing `ads_decisions.db` and `ad_audit_*` tables are the seed of this. Attribution of outcome back to decision is what closes the learning loop.
- **Deliberate memory of failure.** Negative results are the most valuable and most commonly discarded asset. A "we tried this and it didn't work, here's the evidence, don't retry until X changes" store.
- **Creative fatigue detection.** RSAs decay. Frequency, CTR trend decay, and asset-level performance rating (`customers-assets` has asset performance labels) should drive automatic creative refresh.
- **Auction Insights and share-of-voice monitoring** — competitive pressure, impression-share loss to budget vs to rank, and honest diagnosis of *why* a campaign is capped. (`campaign_search_term_insight`, `auction_insight`, `impression_share` metrics.)
- **Quality Score and Ad Rank diagnostics** — expected CTR, ad relevance, landing page experience. A low QS is a *cost* problem that looks like a bidding problem. Distinguish them.
- **Budget-limited vs bid-limited diagnosis.** "We should scale this campaign" and "this campaign can't spend its budget" require opposite actions.
- **Search-term mining for new ad groups** — the search term report is the highest-value untapped asset: it reveals real demand you didn't target, and real waste. Automate theme-clustering from it.
- **Product feed / Shopping surface.** Live GMC feed, physical goods, price points 398–4283 SEK. Shopping and PMax are obvious scaling surfaces and are completely dark today. Feed quality (title, image, attributes) *is* ad creative on these surfaces — design the loop between GMC diagnostics and the feed generator.
- **Discount/promo and seasonality awareness** — Swedish market seasonality (winter dry skin, hard water regions), sale periods, and coordination between paid spend and owned-channel promotion. `bidding-seasonality-adjustments` exists in the API.
- **Geo strategy** — Sweden is the market, but water hardness varies meaningfully by region, which is both a targeting opportunity and a creative-localisation opportunity. Also: account currency AUD / timezone Sydney vs SEK / Sweden — decide and document the canonical reporting timezone.
- **Device and time-of-day strategy.**
- **Exclusion and placement hygiene.** Placement exclusions, brand-safety, mobile-app exclusion on Display/Discovery.
- **Consent / privacy / tracking durability.** EU market, GDPR. Cookie consent affects GA4 and conversion modelling. Design must not assume clean client-side tracking forever; consider server-side or enhanced conversions. **A first-party server-side purchase feed already exists and is running (Section 3.12) — extend it, and treat it as the durable attribution spine rather than building a parallel one.** Check that tracking is consent-compliant — a system that optimises on GDPR-noncompliant data is a liability.
- **Claim and policy compliance.** Swedish consumer marketing rules and Google Ads policy around health/hygiene claims. The product makes implicit health claims (skin, hair, heavy metals). Any autonomous copy generation needs a policy and claims gate before publication — this is a hard requirement, not a nice-to-have, given automated copy generation.
- **Swedish language quality gate.** Machine-generated Swedish that reads translated will damage a brand whose differentiation is local trust. The existing content pipeline already has a Swedish-polish review stage — reuse it for ad copy.
- **Cost of operation.** API quotas (Google Ads has per-account operation limits), rate limits, and the fact that polling everything daily on one box has a real token/time cost. Design a tiered refresh cadence (hot: daily, warm: 3-day, cold: weekly) rather than refreshing everything constantly.
- **How the system decides to do nothing.** The single most important behaviour in a low-data account. Explicit, logged, justified inaction — with the trigger conditions for revisiting — beats action for action's sake.
- **Owner-facing digest design.** What does a weekly/monthly report contain so a non-technical owner can (a) trust the system, (b) catch it going wrong, (c) redirect strategy in one message? Include the system's own confidence, its recent decisions and their outcomes, its current hypotheses being tested, and its honest uncertainties.
- **Cold-start and rebuild-from-zero plan.** If the account, the DB, or the tokens are lost, what is the minimum path back to a functioning loop? What is the seed state?
- **Kill switch.** One command (or one message) that stops all mutation immediately and reverts to observe-only, plus a documented definition of the conditions under which the system should kill itself (spend anomaly, conversion tracking break, ROAS collapse below floor).

---

## 9. WHAT TO AVOID (anti-patterns specific to this setup)

- **Don't propose Kafka, Airflow, a vector DB cluster, dbt, Snowflake, or a Kubernetes deployment.** One box, SQLite, cron. If you think you need more, justify it against a concrete number.
- **Don't design a system that requires statistical significance thresholds this account can never reach.** Design for N=1 conversions per month.
- **Don't propose a dashboard as the deliverable.** A dashboard is a reporting artifact; the owner wants decisions to be made, not to be shown.
- **Don't design "LLM decides everything each cycle."** LLMs are good for generating hypotheses, creative, and explanations; they are bad at consistent numerical policy and will drift, hallucinate thresholds, and be unauditable. Use deterministic policy code for decisions, and LLMs for the generative and explanatory layers, with hard validation gates between them (this box has an established MOE multi-reviewer pre-publish pattern — use it).
- **Don't assume the existing scripts work.** Section 4 is the list of things already broken. Anything you design that depends on `ads-monitor.sh`, `google-ads.sh` (Composio), the Tavily key, or the Ads refresh token has a prerequisite repair task.
- **Don't design away the human re-auth step.** OAuth consent for Google Ads requires a browser and a human. Design the system to *detect* token death early, *alert* clearly, and *degrade gracefully* to observe-only — and to never mistake token death for zero performance.
- **Don't silently change account-level settings** (conversion goals, attribution model, auto-apply recommendations). Recommend, don't execute.
- **Don't leave Google's own `customers-recommendations` on auto-apply.** Read them as a signal source; apply them only through your own validated decision path.

---

## 10. WHAT TO DELIVER

Produce a **technical architecture and implementation specification** — the document OWL will build from. It should be self-contained enough that an engineer with access to the box could execute it without asking you follow-up questions. Structure it as:

1. **Executive summary** — the system in one page: what it is, how it decides, what it will and won't do on its own.
2. **Design principles** — the 6-10 rules that resolve trade-offs (e.g. "measurement integrity outranks optimisation aggressiveness").
3. **System architecture** — components, their responsibilities, and the data flow between them. Include the closed loop explicitly: sense → validate → interpret → decide → act → verify → learn.
4. **Data model** — full SQLite DDL: every table, column, type, index, and its purpose. Include the entity model from Section 8 (campaigns, ad groups, ads, keywords, negatives, landers, intents, personas, products, products↔keywords, decisions, outcomes, experiments, memory-of-failure, run-ledger). Include provenance columns (source, harvested_at, attribution_window, currency) on every fact table.
5. **Ingestion layer** — per data source: what to pull, at what granularity, on what cadence, via which CLI/API call, into which table, with what freshness and completeness assertions, and what to do on failure. Cover the gaps named in Section 4 (ad-group/ad/keyword/geo/device granularity, Shopify line items, GMC performance, search terms, auction insights, asset performance).
6. **Attribution and measurement integrity** — how Google Ads (AUD), GA4 (conversion value), Shopify (SEK), and Klaviyo (lagged/assisted) are reconciled; which source is authoritative for which question; the canonical timezone and currency handling; the conversion-action hygiene fix; the UTM standard; how discrepancies are detected and surfaced. Include the end-to-end verification job that proves a click in Ads becomes an order in Shopify and is visible in both — **anchored on the existing first-party tracker (Section 3.12), which is the only component in the chain that can testify to a purchase without depending on the browser**.
7. **The decision engine** — for each decision class (budget reallocation, bid adjustment, keyword pause/enable, negative addition, creative rotation, ad group creation, ad creation, keyword creation, campaign launch, geo/device adjustment): the inputs, the deterministic rule/policy, the thresholds with their justification, the minimum-data guard, the confidence/credible-interval logic, the action bounds, the rollback plan, and the escalation condition. For every **creation** decision (new ad group / ad / keyword / campaign) additionally specify the hypothesis record, the launch envelope parameters (N and M), the leading-indicator floor that keeps it alive, and the auto-kill rule. Be explicit about the do-nothing branch.
8. **Scaling and exploration** — how winners grow, how new ideas enter the portfolio, the exploration budget, the launch envelope applied to every new entity, the full lifecycle of a campaign from incubation through promotion to scaling or retirement, and the guardrails on each transition.
9. **Creative and copy generation** — the pipeline from intent/persona/pain-point → keywords → ad concepts → headlines/descriptions → lander selection, including the LLM stages, the validation gates (Google policy, Swedish language quality, claims compliance, brand voice), and the review/MOE gate before publication. Specify how this pipeline runs fully autonomously — the copy must reach live status without a human in the loop, with the gates as automated filters, not approval steps.
10. **Self-healing** — the failure taxonomy, per-class detection, per-class repair, the escalation path, and the health/self-test suite that proves the system is alive and truthful (this should include *deliberate* synthetic tests, e.g. detecting a null conversion feed rather than trusting it).
11. **Self-learning** — what is recorded, how outcomes are attributed back to decisions, how confidence/weights update over time, how the memory is queried at decision time, and how negative results are preserved.
12. **Scheduling and runtime** — the full cron/job map with cadences, dependencies, ordering, idempotency, and the tiered refresh strategy. Include the run-ledger schema and the freshness/staleness policy.
13. **Safety, guardrails and kill switch** — the cap layer the optimiser cannot override, blast-radius limits, the progressive trust ladder with its concrete promotion test and demotion triggers, the notification-vs-approval matrix (make clear which items are true blocking gates and which are notify-after-the-fact), the one-command halt, and the self-kill conditions.
14. **Owner interface** — the digest format (weekly and monthly), the escalation format for the handful of true blocking gates, the one-message redirect mechanism, and what the owner can see about the system's reasoning, confidence, and recent autonomous launches. The digest's default posture must be *it already acted — here's what, why, and what it predicts*.
15. **Build plan** — phased and sequenced, ordered by dependency, with a clear definition of done per phase, and an explicit "Phase 0" foundation (repair the broken things in Section 4 first — nothing above works on a lie). Rough effort sizing per phase. Identify what can be built and verified *without spending money* versus what needs live budget.
16. **Open questions and assumptions** — anything you had to assume, and what would change the design.
17. **Appendices** — DDL, example decision records, example digest, the negative-keyword vocabulary seed, the intent/persona matrix, the policy-compliance checklist, and worked examples of the decision engine handling three concrete cases from the real data in Section 3.4/3.6 (e.g. "Investigative spent 295 AUD on 141 clicks for 0 conversions before being paused — what should the system have done, in what order, and what would it have learned?").

**Design quality bar:** every claim about the account must trace to Section 3 or 4. Every number you use must be one of the numbers given (do not invent metrics). Every rule must specify its behaviour on insufficient data. Every action must have a rollback. Every component must state how it knows it is working.

---

## 11. FASTEST PATH TO SOMETHING REAL

If you want to sequence aggressively, the highest-value order is roughly:

1. **Fix the truth layer.** Conversion-action hygiene, GA4→Ads attribution, the `campaign_budget` GAQL bug, ad/keyword/geo/device granularity ingestion, Shopify line items. Without this, every subsequent decision is built on sand.
2. **Build the entity model and the decision ledger** (empty but correct). Everything writes into it from day one.
3. **Ship observe-only intelligence for two weeks** and let it record its decisions *without acting*. Compare what it *would* have done against what actually happened. This is free and is the fastest way to calibrate thresholds before risking money.
4. **Turn on the safe mutation classes** (negatives, pauses, budget within cap) behind the guardrails — Stage 1 on the ladder.
5. **Then climb the ladder:** Stage 2 (build ad groups / ads / keywords) → Stage 3 (launch campaigns from scratch) → Stage 4 (scale budget, geo, audiences). Promotion is automatic on the stated criteria. The owner is notified, not consulted. Nothing in this sequence waits on a human reply.
6. **Run a permanent counterfactual lane.** At every stage, a parallel stream keeps computing what it *would* have done on decisions it didn't take, so the system learns from inaction too and the owner always has a counterfactual to audit when he questions a call.

---

## 12. CLOSING NOTE FROM THE SENDING AGENT

Two things the owner cares about that don't fit neatly into a spec:

First, he has been burned. Jobs here have failed silently for weeks while reporting calm, plausible, zero-data stories. He does not trust dashboards that say things are fine. **The system's credibility rests on it being able to prove, at any moment, that it is alive, that it is measuring correctly, and that it knows the difference between "no" and "unknown."** Build that proof in from the first commit.

Second, he stated the goal as: *"I don't want to have to guide it."* He means it literally. **He is not asking for a system that recommends campaigns — he is asking for one that launches them.** The measure of this design is that in three months he opens a digest and reads that the system launched two campaigns on its own initiative, killed one on its own pre-committed auto-kill rule, scaled the other, negated 40 waste terms, and has a new ad group in incubation — with reasoning he can audit and a rollback handle if he disagrees. His only required act is to change a strategy when he wants to.

The distinction that makes this safe without making it dependent on him: **he holds veto, not approval.** A gate where his silence stops the system is the same thing as having to guide it, just slower. Build for after-the-fact veto with bounded blast radius and documented rollback, and make every autonomous launch survivable in isolation.

Design something that earned the right to be trusted, and that tells the truth when it isn't working.
