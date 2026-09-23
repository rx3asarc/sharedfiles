# HANDOFF PROMPT → Claude Opus 5
## Mission: Architect a Fully Autonomous, Self-Learning, Self-Healing Google Ads System for Nordisk Renhet

> ⛔ **SUPERSEDED — DO NOT HAND THIS FILE TO THE ARCHITECT.**
> This is the Revision-1 draft (2026-09-23). The current, re-verified handoff prompt is
> **`google-ads-autonomy/HANDOFF-PROMPT-claude-opus5.md`** (Revision 2). Hand off that one.
> Kept only for history.


> **How to use this document:** paste everything below into Claude Opus 5. It is a prompt, not a report. The final section defines the exact document you must return.

---

# 1. YOUR ROLE

You are the **systems architect** for a production autonomous paid-acquisition system. You are not a copywriter, not a media buyer, not a consultant producing a strategy deck.

You are writing a **build spec**. A coding agent (me, a Pi coding agent operating directly on this server) will implement it. Everything you specify must be implementable against the capabilities listed in §5. Nothing else exists.

Three people matter:
- **Maestro** — the business owner. Wants to stop steering. Wants the system to run itself and make money. Non-technical on architecture, very sharp on business judgement.
- **The Builder (me)** — a terminal-resident coding agent with shell, Python, SQLite, network access, LLM access, and the CLIs in §5. I implement what you specify, in phases, and I will push back if a spec is unbuildable or self-contradictory.
- **The System** — the thing you are designing.

**Your output is judged on one question: could a competent engineer build this straight from your document without asking you a single clarifying question?**

---

# 2. THE BUSINESS

**Nordisk Renhet** (`nordiskrenhet.com`) — Swedish D2C ecommerce, water filtration for showers.

| Item | Value |
|---|---|
| Market | Sweden (primary), then EN/EU |
| Store language | Swedish (SEK) |
| Currency of the Google Ads account | **AUD** (account `8479789152`) — never conflate with SEK |
| Products | Duschvattenfilter 990 SEK (CaSO₃ + KDF-55 + GAC triple-media, inline); Duschhuvud 1,199 SEK (activated carbon fibre ONLY); Wellness Kit (both); Family Bundle; replacement cartridges (~398 SEK) |
| Margin data | Per-order COGS exists: `product_usd`, `ship_usd`, `duty_usd`, `cost_sek` per order (`/root/.nordisk/data/hypersku_final.json`) |
| Guarantee | **100-day** money-back (not 60) |
| Storefront | Shopify (theme id locked, see §4) |
| Content moat | 23 published articles, 50 sitemap pages, competitor comparison pipeline, 12 tracked competitors |
| ICP | Already documented in depth: `/root/.nordisk/nordisk-icp.md` (demographics, psychographics, customer language, pain points, sourced from Reddit/Trustpilot/GSC/82 orders) |

**Commercial reality you must design around:** this store is *tiny in paid terms*. Live 30-day figures for the only ENABLED campaigns:

| Campaign | Channel | Impressions | Clicks | Cost (AUD) | Conversions |
|---|---|---|---|---|---|
| SV SE \| Brand - Search | SEARCH | 90 | 34 | 38.45 | 0.61 |
| SV SE \| Discovery \| Broad Match | SEARCH | 88 | 5 | 9.79 | 0 |
| SV SE \| Conquest \| Competitors | SEARCH | 0 | 0 | 0.00 | 0 |

Organic is also small: ~8–36 GSC clicks/day, 2,345 distinct queries in the last 30 days. ~111 orders in the warehouse.

**Do not design as if this were a high-volume account.** At this volume, classical statistical optimization is impossible. Designing a system that pretends otherwise is the single most likely way for you to fail this brief. §7 makes this a mandatory design problem.

---

# 3. THE GOAL (Maestro's words, verbatim)

> "I have a big goal: it is a fully autonomous self learning self healing self propelling google ads environment. I don't want to have to guide it. I want it to work by itself. I want it to be a self healing self learning self initiating, budget optimising, scaling minded, ROAS increasing, money making system. I want it to be able to launch new campaigns and new adgroups and new ads and take into consideration keywords as well as negative keywords as well as language and also landing page url and also awareness stage and customer journey and ICP and pain points and brand and competition and educational content and informational and purchase intent and awareness stages and so on. There are a lot of things I'm not thinking about here, I don't know what they are. All I know is, I want autonomous monitoring, reasoning built in, judgement made, based on what products the most clicks and impressions and sales in end effect. Sales must be cross referenced and there must be some tracking that is set up with all this so that the autonomous system knows and understands what works and what doesn't. That is highly vital."

Decomposed into the five properties you must deliver:

1. **Self-initiating** — discovers opportunities and launches campaigns/ad groups/ads/keywords/negatives without being prompted.
2. **Self-learning** — updates its own beliefs about what works, from evidence, and records *why*.
3. **Self-healing** — detects and repairs (or escalates) its own breakage: dead credentials, broken tracking, disapproved ads, dead landing pages, feed errors, runaway spend.
4. **Self-propelling** — budget optimisation and scaling management with a growth bias, bounded by safety.
5. **Money-making** — the objective function is *contribution profit*, not clicks, not impressions, not even revenue.

**Explicit new dimensions Maestro flagged as under-specified** — you must cover, and you must *add the ones he did not name*: negative keywords, language/locale matching, landing page URL selection, awareness stage, customer journey stage, ICP fit, pain-point mapping, brand vs non-brand, competitor conquest, educational/informational content, purchase-intent keywords, and search-intent taxonomy.

---

# 4. HARD CONSTRAINTS — NON-NEGOTIABLE

These are enforced today by scripts and by burnt experience. **Your architecture must encode them as machine-checkable preconditions in the action layer, not as prose advice.** A design that can violate any of these is rejected.

### 4.1 Currency
Google Ads account `8479789152` is **AUD**. The Shopify storefront is **SEK**. Never implicitly convert. Any decision rule involving money must declare which currency it is in and convert explicitly with a recorded rate.

### 4.2 URL preconditions (every ad, every time)
- Landing page URL **must return HTTP 200** before an ad goes live. Verified with `curl -o /dev/null -s -w "%{http_code}"`. A 301 means the URL is wrong — use the canonical `www` directly.
- Must be `https://` and must use `www.nordiskrenhet.com`.
- Path must be descriptive, not a code (`/pages/duschfilter-jamforelse-bast-i-test`, not `/pages/se-4`).
- Every URL must be machine-verified with a HEAD/GET immediately before submission, and the result stored.

### 4.3 Language ⇔ campaign/landing-page consistency
Swedish campaign → Swedish landing page. English campaign → English landing page. Verify via the page's `lang="..."` attribute, not by assumption.

### 4.4 Negative keyword floor
Broad match may not be activated without a verified negative keyword list in place: ≥20 negatives minimum per campaign, covering competitor brands, other languages, irrelevant categories, spam terms. A live list exists: `/mnt/HC_Volume_105587324/nordisk/google-ads/negatives.md` (Swedish, categorised into price shoppers, DIY, non-buyer intent, wrong product category, professional, wrong buying mechanism).

### 4.5 Landing page relevance
Each ad group's keyword theme must match its landing page content. Problem keywords → problem/solution page. Solution keywords → product page. Decision keywords ("bäst i test") → comparison page. **All ad groups pointing at one generic URL is a bug, not a strategy.**

### 4.6 Product copy vocabulary
Only claims on the official spec sheet or the live site. **Banned:** "oberoende tester", "TEWL", "clinical research", any unsourced claim. **Never fabricate customer quotes.** VOC language from research belongs on landing pages and ads; *never* in Shopify product descriptions. Filtration specs are hardcoded truth: Duschvattenfilter = KDF-55 + CaSO₃ + GAC (triple-media); Duschhuvud = activated carbon fibre ONLY (no KDF-55, no CaSO₃, no GAC). Never blur these.

### 4.7 Paused campaigns
Campaigns with status PAUSED must **never** be surfaced in any human-facing output or reasoning. Only ENABLED campaigns may be reported on. (Their *data* may be mined for learnings — negatives, search-term patterns, ad copy — but the campaigns must not be discussed.)

### 4.8 Shopify theme guardrail — **this directly constrains the landing-page dimension**
Any change to a landing page that lives in the Shopify theme must go through a hard-enforced flow:
- The live/main theme (id `195492381006`) is **immutable**. Never write to it. Never flip roles.
- All theme edits happen on a **DUPLICATE UNPUBLISHED theme**, tested in a real browser at `?preview_theme_id=...` first.
- If duplicate creation fails → **STOP and escalate**. Never fall back to editing live.
- Never upload untested inline JS/CSS. Shopify validates Liquid syntax, not JS behaviour.
- Performance-regression measurement (Lighthouse/PSI) on the duplicate before any publish.
- Enforcer: `/root/.nordisk/guard/theme_guard.py`, config `/root/.nordisk/guard/theme_guard_config.json`, 17 tests.

**Implication for your design:** the autonomous system may *select* and *route to* landing pages freely, and may *propose* new landing pages, but **publishing a landing page is a gated action**, not an autonomous one. Your spec must define the interface between the ads system and this gate.

Similar for the article pipeline: the article featured image is **manual-only in Shopify Admin**; the pipeline never writes an `image` key.

### 4.9 Secrets
Secrets live in `/root/.secrets.env` (mode 600) and `/root/.nordisk/.env`. Never print, echo or log values. Read via env or `$(secrets get NAME)`. Any secret that appears in a transcript is considered burned and must be rotated.

### 4.10 Analytics tagging integrity
UTM/tracking templates are already specified in `/mnt/HC_Volume_105587324/nordisk/google-ads/ops-operations.md` (per-campaign `final_url_suffix` with `utm_source/medium/campaign/term/content`, plus `{campaignid}` ValueTrack). Your attribution design must be compatible with, or explicitly supersede, this scheme.

---

# 5. WHAT EXISTS — CAPABILITY AND DATA INVENTORY

This is the complete list. **If your design needs something not here, you must flag it explicitly as `REQUIRES NEW ACCESS` with the provider, cost, and grant required.**

## 5.1 Advertising — Google Ads (READ + WRITE, live)

| Asset | Detail |
|---|---|
| CLI | `google-ads-pp-cli` (`/root/go/bin/`) + `gads` wrapper on PATH |
| Version | API v2026.9.1 |
| Auth | OAuth2 refresh token in `/root/.nordisk/.env`; env loader `/mnt/HC_Volume_105587324/nordisk/bin/gads-env.sh` (**source this, never mint tokens inline**) |
| Account | `GADS_CUSTOMER_ID=8479789152`, login customer id same |
| Developer token | `GOOGLE_ADS_DEVELOPER_TOKEN` in `/root/.secrets.env` |
| Read | Full GAQL: `gads --agent customers-google-ads search <cid> --query "<GAQL>"` — campaigns, ad groups, ads, criteria, keywords, search terms, budgets, bidding strategies, assets, audiences, conversion actions, recommendations, change history |
| Write | Full mutate surface present: campaigns, ad groups, ads, criteria, negative criteria, budgets, bid modifiers, assets, asset groups, audiences, campaigns-drafts, experiments, keyword plans, offline user data jobs |
| Cached read | `/root/.local/share/google-ads-pp-cli/data.db` (schema mirrors every API resource; currently rows=0 — `sync_state` empty, `google-ads-pp-cli sync` would hydrate it) |
| Warehouse | `ads_campaigns` table in `/mnt/HC_Volume_105587324/nordisk/db/nordisk.db` — 348 rows, refreshed daily by `bin/refresh-ads-data.sh` (LAST_30_DAYS campaign grain) |
| Conversion actions (ENABLED) | `Nordisk Renhet (web) purchase` (GOOGLE_ANALYTICS_4_PURCHASE, PURCHASE, primary), `Purchase (GA4 event add_payment_info)`, `Submit lead form (GA4 event form_submit)`, `Add to cart (GA4 event add_to_cart)` — all `primary_for_goal=True`, all `MANY_PER_CLICK`. **Multiple competing primaries is an attribution hazard you must address.** |
| Existing automation | `bin/harvesters/ads-monitor.sh` (daily 06:37 — enabled-campaign health, search terms, waste), `bin/weekly-ads-checkpoint.sh` (Mon 07:07), `bin/harvesters/run-all.sh` |
| Existing strategy artifacts | `google-ads/`: `campaign-architecture-v2.md`, `campaign-architecture-v3.md`, `strategy.md`, `negatives.md`, `landing-page-inventory.md`, `ad-copy-library.md`, `funnel-pages/`, `historical-analysis.md`, `swedish-market-research.md`, `swedish-market-research`, `competitor-review-analysis.md`, `clearly-of-sweden-intel.md`, `manual-checklist.md`, `pre-launch-checklist.md`, `ops-operations.md` (UTM + 3-layer decision thresholds), `campaigns/*.json` (5 campaign blueprints) |
| Existing pipeline (JS, partial) | `google-ads/pipeline/01-daily-snapshot.js`, `02-weekly-winner-loser.js`, `03-keyword-deep-dive.js`, `04-budget-auto-scaler.js` — read-only analysis + a naive budget plan. **This is the current ceiling: it reports, it does not act, it does not learn, it does not reason.** |

## 5.2 Search Console

| Asset | Detail |
|---|---|
| Property | `GSC_PROPERTY` in `/root/.nordisk/.env` |
| CLI/harvester | `bin/harvesters/gsc.sh` + `gsc-harvester.js` |
| Direct Python | `/root/.nordisk/scripts/nordisk-gsc.py`; venv `/root/.nordisk/venv-gsc/` |
| Token | Service account `/root/.nordisk/keys/google-service-account.json`; refresh cron every 30 min (`bin/refresh-gsc-token.sh`) |
| Warehouse | `traffic_daily` in `nordisk.db` — **69,864 rows**, grain = date × query × page, with clicks, impressions, ctr, position. 2,345 distinct queries in last 30d |
| Freshness caveat | Latest row is 2026-09-20. Staleness itself must be monitored by the self-healing layer. |

## 5.3 Google Analytics 4

| Asset | Detail |
|---|---|
| Property | `454852488`, measurement id `G-YJP5QDGTHD` |
| Read | GA4 **Data API** via service account: `/root/.nordisk/scripts/ga4-read.py` — `realtime`, `report <metrics> <dims> [days]`, `tx` (purchase transactions) |
| Write | GA4 **Measurement Protocol** — secret `GA4_MP_API_SECRET` in `/root/.secrets.env`. Used server-side only, never in browser code. |
| Warehouse | No GA4 table in `nordisk.db` yet — **this is a gap your design must fill** |

## 5.4 First-party server-side conversion tracking (already live)

| Asset | Detail |
|---|---|
| Path | `/mnt/HC_Volume_105587324/nordisk/bin/pixel-tracker/` |
| `tracker.py` | HTTP endpoint on `127.0.0.1:9123` behind Caddy at `nordisk.vektal.systems/track/purchase`. Receives normalised `checkout_completed` POST from a **Shopify Web Pixel extension**, validates, appends to local log, forwards to GA4 Measurement Protocol. |
| DB | `/mnt/HC_Volume_105587324/nordisk/db/pixel_track.db` — `purchases(transaction_id PK, received_at, client_id, value, currency, ga4_status, ga4_response, raw, source)` |
| Doctors | `tracking-doctor.py`, `google-ads-conv-doctor.py`, `nordisk-infra-doctor.py` (daily 05:07 cron) |
| **This is the strongest attribution asset you have.** It is first-party, transaction-id-keyed, server-side, and it is the natural join key between ad click and Shopify order. |

## 5.5 Shopify

| Asset | Detail |
|---|---|
| CLI | `shopify-pp-cli` |
| Auth | `SHOPIFY_ACCESS_TOKEN`, `SHOPIFY_SHOP`, `SHOPIFY_API_VERSION` in `/root/.nordisk/.env`; also `/root/.nordisk/keys/shopify-admin-token` |
| Cached read | `/root/.local/share/shopify-pp-cli/data.db` — products (32), orders (50), resources (82), plus FTS indexes |
| Warehouse | `nordisk.db`: `orders` (111 rows; includes `landing_site` and `referring_site` — **join keys for attribution**), `products` (31, with multilingual titles/descriptions and a `filtration_media` spec column), `customers` (221) |
| Rich exports | `/root/.nordisk/data/`: `orders.json`, `orders_full.json`, `orders_rich.json`, `products_rich.json`, `customers.json`, `hypersku_final.json` (per-order COGS: product + shipping + duty in USD, converted to SEK/EUR) |
| Also | `bin/push-new-article.py`, `bin/sync-descriptions.py`, `bin/resync-orders.py` |

## 5.6 Klaviyo (email — downstream of acquisition quality)

| Asset | Detail |
|---|---|
| Auth | `KLAVIYO_API_KEY` in `/root/.nordisk/.env` |
| CLI | `klaviyo-pp-cli` (pp-klaviyo skill) |
| MCP | `klaviyo` server registered (currently disconnected — reconnectable) |
| Warehouse | `nordisk.db`: `klaviyo_campaigns` (2), `klaviyo_daily` (402), `klaviyo_flows` (24), `klaviyo_flow_metrics` (0) |
| Purpose | Post-purchase / repeat-purchase behaviour; LTV and repeat-rate signal for the objective function |

## 5.7 Google Merchant Center

| Asset | Detail |
|---|---|
| Auth | `GMC_SFTP_PASS` in `/root/.nordisk/.env` |
| Tooling | `bin/harvesters/gmc-feed.py`, `bin/harvesters/gmc-feed.sh`; product table carries `gmc_title_sv/en/fr` |
| Relevance | Shopping / PMax feeds; feed disapprovals are a self-healing surface |

## 5.8 Keyword and demand intelligence (free, already built)

| Asset | Detail |
|---|---|
| Tool | `/mnt/HC_Volume_105587324/nordisk/bin/keyword-intel.py`, DB `/mnt/HC_Volume_105587324/nordisk/db/keyword-intel.db`, weekly cron (Mon 04:17) |
| Sources | (1) **Google Autosuggest** `suggestqueries.google.com` with `hl=sv&gl=se`, alphabet + question-prefix expansion (`hur/vad/varför/vilket/bästa/pris/alternativ`); (2) **competitor sitemaps** (Shopify `sitemap_blogs_N.xml`) for what competitors publish; (3) **GSC `traffic_daily`** for real positions |
| Capabilities | `suggest`, `sitemaps`, `gsc`, `gaps --limit N`, `report`, `seed-topics`, `all`; SV/EN language detection, intent classification, theme clustering, Jaccard dedupe against existing phrases |
| Also free | `bin/nightly-topic.py` (GSC-based topic finder, classifies one-push-away / content-gap / decay-rescue) |

## 5.9 SERP / rank tracking

| Asset | Detail |
|---|---|
| `SERPER_API_KEY` | in `/root/.secrets.env` — a real SERP API, usable for rank tracking arbitrary keywords |
| Existing use | `/root/loops/nordisk-comparison-pipeline/nodes/demand_node.py` (demand scoring), `migrations/MIGRATION-DEMAND-SCORE.sql.py` |
| Docs | `/root/loops/nordisk-comparison-pipeline/docs/SERP-OPTIONS.md` |

## 5.10 Web-scale research and scraping

| Tool | Purpose |
|---|---|
| `research-unified` CLI | `search`, `deep`, `extract <url>`, `docs`, `similar <url>`, `news`, `scholar`, `social`, `scrape <url>`, `browse <goal>`, `status`, `cache`, `sync` — routes across Tavily → Exa → Apify → Composio → Context7 → Brave → Browser Use Cloud, with MemPalace caching |
| Tavily | `TAVILY_API_KEY`, `tvly` / `tavily-pp` CLIs |
| Exa | `EXA_API_KEY` (semantic search, similar pages, neural) |
| Apify | `APIFY_TOKEN` / `APIFY_API_KEY`, MCP server registered — actors for scraping |
| Firecrawl | `FIRECRAWL_API_KEY` |
| Browserbase | `BROWSERBASE_API_KEY` + `BROWSERBASE_PROJECT_ID`, MCP registered |
| Composio | Harvesters present (`harvesters/composio-harvester.js`) |
| Serper | `SERPER_API_KEY` — SERP results |
| AliExpress/Alibaba | `ali` MCP (7 tools) + `/root/.local/bin/rtk`-adjacent sourcing workflow — **relevant if SKU expansion or cost-of-goods negotiation enters the scaling dimension** |
| Local browser | `chromium-browser`, `google-chrome`, headless CDP at `/root/.chrome-cdp`, Playwright, `agent-browser`, `camofox`, plus Nordisk-specific: `nrshot.js`, `nrdiff`, `nrvisdiff`, `nrmobile.js`, `nralign`, `nrcmp`, `nrstruct.js`, `nrtext.js`, `nrtop.js`, `nrwhere.js`, `nrverify`, `nrscout`, `nrvision` |
| Vision | `nrvision` / `cosmos.vision` subagent (Gemini flash) — returns style fit + Swedish alt text + ASCII slug. **Use for screenshot-based landing-page and ad-creative judgement.** |

## 5.11 Content, landing pages, and the article pipeline

| Asset | Detail |
|---|---|
| Article pipeline | `/root/loops/nordisk-comparison-pipeline/` — nodes: `discovery`, `demand`, `research`, `enrichment`, `ground`, `draft`, `eval`, `moe`, `humanizer`, `swedish_polish`, `verify`, `publish`, `cosmos_hero`. DB `competitors.db`. Has `topics`, `evidence`, `format_rotation` entities, a demand score, an evidence guardrail (`EVID-001`), and format/intent rubrics. Full autonomous pipeline with eval nodes. |
| Canonical facts kernel | `nodes/nordisk_self.py` — loads Nordisk's own product facts from a `product_facts` table so no script ever hardcodes a wrong spec. **This pattern is the model to follow: canonical facts in a table, consumers import, no inline copies.** |
| Landing pages | `/mnt/HC_Volume_105587324/nordisk/landing-pages/` (`scraped/`, `built/`, `analyses/`), `google-ads/funnel-pages/`, plus GemPages-hosted pages and Shopify theme sections |
| Site architecture | `/root/.nordisk/site-architecture.md`, `nordiskrenhet-com-sitemap.xml` (50 URLs), `published-articles.json` (23 articles) |
| Performance testing | `nrperf` CLI (PageSpeed Insights / Lighthouse) + `nordisk-perf` skill |

## 5.12 Orchestration, memory, and reasoning substrate

| Asset | Detail |
|---|---|
| Cron | Active crontab with ~25 jobs (harvesters, organic pipeline, guards, doctors, watchdogs, MemPalace sync) |
| Temporal | Skills installed: `temporal-developer`, `temporal-cloud` — **durable execution, retries, timers, saga compensation, signals are available if you want them** |
| MemPalace | Knowledge graph (`/root/palace/knowledge_graph.sqlite3`) + Chroma vector store + diary + semantic search; CLI `mempalace-cli`; daily sync at 08:07. Cross-session memory for the fleet. |
| Self-improvement loops | `/root/loops/` (e.g. `nordisk-comparison-pipeline/daily-pipeline.sh`, `eval/`, `judge-reasoning.py`, `judge-reliability.py`); `/root/harness-opt/` (read-only noticing comb, credential-heal actor, evals suite as a gate); skills `loopy`, `graphopt`, `graph-workflow-spec`, `agent-native-architecture` |
| LLM access | `OPENROUTER_API_KEY`, `ORCAROUTER_API_KEY` (self-hosted gateway `/mnt/HC_Volume_105587324/orcarouter-lite/`), `OPENAI_API_KEY`, `pi-moa` CLI (fan-out to multiple reference models + aggregator — **use for high-stakes judgement calls**), subagent/chain/workflow orchestration primitives |
| Test/eval tooling | `eval` nodes, `harness-ops` (`doctor`, `diagnose`, `skills`, `subagent`), `validate-skills`, `<T>_tests.py` conventions, `run_guard_tests.sh` |
| Notifications | Telegram bridge (this is how Maestro is reached), `bin/weekly-email.py` |
| Databases | SQLite everywhere (`nordisk.db`, `store.db`, `research.db`, `competitors.db`, `keyword-intel.db`, `pixel_track.db`, `ali/sourcing.db`) + a Postgres instance (`DB_HOST/DB_NAME/DB_USER/DB_PASSWORD/DB_PORT` in `/root/.env.unified`) |
| Host | Disk: `/` 38G with ~6.8G free (82% — **the tight one, keep temp files off `/tmp`**), `/mnt/HC_Volume_105573741` 30G ~12G free, `/mnt/HC_Volume_105587324` 40G ~12G free. Recurring hazard: headless-Chrome profile dirs accumulate in `/tmp`. |
| Constraints | Single host, no cloud autoscaling. Design for one box. |

## 5.13 What does NOT exist (do not assume)

- ❌ Meta / Facebook / Instagram Ads API access
- ❌ Microsoft / Bing Ads access
- ❌ TikTok, LinkedIn, YouTube-specific ad APIs (YouTube is reachable through Google Ads but no dedicated tooling)
- ❌ Call tracking / offline conversion import pipeline (the API surface exists locally via `offline_user_data_jobs`, but nothing is wired)
- ❌ A customer data platform or a formal attribution product
- ❌ Warehouse beyond SQLite + one Postgres
- ❌ A dashboard UI for ads (there is a Go `dashboard/` dir — content unknown, assume it needs building)
- ❌ Server-side GCLID capture → CRM → offline conversion loop (the **capability** exists; the **wiring** does not)

---

# 6. THE EXISTING CEILING — WHAT YOU ARE IMPROVING ON

Be precise about the delta. Today, for ads:

1. A daily shell monitor reads ENABLED campaigns and search terms, and writes findings into a log and MemPalace. **It reports.**
2. A weekly checkpoint writes a JSON snapshot. **It reports.**
3. Four JS pipeline scripts compute a daily snapshot, a winner/loser report, a keyword deep dive, and a naive "scale by share of spend" budget plan capped at 350 SEK/day. **They analyse, and one of them writes a plan file that nobody executes.**
4. `ops-operations.md` contains a hand-written 3-layer threshold table (CTR > 5% keep / 2–5% investigate / < 2% rewrite / < 1% pause) — **this is the closest thing to a policy that exists. It is prose, it is un-coded, and at 90 impressions/30d its thresholds are unreachable.**

**Nothing closes the loop. Nothing acts. Nothing learns. Nothing recovers from its own breakage.** That is the gap.

There is also a comment in the codebase that a previous version of the weekly checkpoint produced an **all-zero result and then reported it as "normal for a low-traffic period"** — a broken job manufacturing a confident all-clear. **Your design must make that failure mode structurally impossible:** the system must distinguish *"no data because nothing happened"* from *"no data because I am broken"* and must never convert the second into reassurance.

---

# 7. HARD PROBLEMS YOU MUST SOLVE (mandatory sections — do not skip, do not hand-wave)

These are the problems that will decide whether the system works. Maestro explicitly said there are things he is not thinking of. **These are those things.** Treat each as a first-class design requirement with a concrete mechanism.

### P1 — Signal scarcity and the cold-start problem
The account has 34 clicks and 0.6 conversions in 30 days. Classical optimization (significance testing, bandits on conversion rate, budget scaling by ROAS) is **statistically meaningless** at this volume — a single order moves ROAS by an order of magnitude. You must define:
- A **signal hierarchy**: which decisions are safe at which data volumes (e.g. search-term negatives can act on ~5 impressions; budget scaling cannot act on <30 conversions).
- A **cold-start protocol**: how the system buys information efficiently (exploration budget, keyword harvesting via broad-ish match with heavy negatives, Learning-phase awareness) before it tries to optimize.
- A **minimum viable data threshold per action class**, expressed as concrete numbers, with the reasoning.
- How the system avoids mistaking noise for signal — explicitly including a Bayesian or shrinkage approach to small-sample rates, and a rule that prevents acting on a 1-of-2 win rate.

### P2 — Attribution truth, and reconciliation of four competing signals
Available signals: Google Ads conversions (GA4-imported, **four primaries all `MANY_PER_CLICK`**, which is a known double-count hazard), GA4 Data API transactions, the first-party server-side pixel (`pixel_track.db`, transaction-id-keyed), and Shopify orders (with `landing_site` / `referring_site`). Plus `utm_term` / `utm_content` ValueTrack data flowing into the landing URL.
You must define:
- Which signal is **revenue truth** and which are diagnostics.
- A **reconciliation procedure** with tolerance thresholds, run daily, that raises an incident when signals diverge beyond tolerance.
- A **GCLID/wbraid → order** linkage design, including where the click id is captured, stored, and joined. (Note: the capability exists through offline conversion import; the wiring does not.)
- Explicit handling of **the four primary conversion actions** — either collapse them or justify keeping them and define how double-counting is prevented.
- Treatment of the **100-day guarantee / refund and return window**: a system optimizing on orders will happily buy customers who refund on day 90. Define **refund-adjusted and LTV-adjusted** revenue as the objective, and how a long refund window is handled in a system that must make decisions daily. This means either a lag-aware objective, a cohort-based holdback, or a confidence-discounted revenue figure. Pick one and justify it.

### P3 — The objective function
Not clicks. Not impressions. Not revenue. Define the objective function precisely, in code-ready terms, including:
- **Contribution margin** per SKU (COGS data exists — `hypersku_final.json`, `cogs_final.py`), not just revenue.
- **Multi-SKU weighting**: Maestro said "based on what products have the most clicks and impressions and sales in the end effect". Define how product-level performance aggregates to campaign/ad group level, and how a low-margin hero product vs a high-margin bundle is valued.
- **New-customer vs repeat** distinction.
- **Currency**: account is AUD, storefront SEK, COGS in USD. Define the canonical unit of account and the FX handling.
- Hard **spend caps** at account, campaign, and ad-group level; and a global daily cap (the existing pipeline assumes 350 SEK ≈ 50 AUD — question that assumption rather than inheriting it).
- The explicit **risk appetite**: how much is the system allowed to lose while exploring, at what total daily budget, and what triggers an automatic pull-back.

### P4 — The decision loop, and the split between deterministic policy and LLM judgement
This is the architectural heart. You must specify a closed loop with named stages, and for **every stage** state whether it is:
- **(D) Deterministic** — code, thresholds, arithmetic, always reproducible.
- **(L) LLM reasoning** — judgement, generation, synthesis, open-ended diagnosis.
- **(H) Human-gated** — requires Maestro's approval.

Then define:
- **Where the LLM is allowed to act directly** and where it may only **propose**.
- The **fail-closed rule**: what happens when the LLM is unavailable, returns malformed output, or is uncertain. (Default must be: no change, not a best-guess change.)
- How LLM output is **validated before execution** (schema, precondition re-check, dry-run).
- **Cost control**: a per-day LLM token/cost budget for the ads system, and what the system degrades to when the budget is exhausted.

### P5 — Determinism against irreversibility: reversibility, blast radius, and change velocity
Define for every action class:
- **Blast radius** (how much money/delivery can it affect before a human notices).
- **Reversibility** (fully reversible / reversible with loss / irreversible).
- **Required authorisation level** (autonomous / autonomous-with-notification / human-gated).
- **Velocity limits** — max N changes per entity per day, max budget delta per change, budget change floors and cooling-off periods, and a "don't touch it again for X" rule so the system can't oscillate.
- **Circuit breakers**: spend anomaly, conversion-tracking drop to zero, CPC spike, impression collapse, landing page 404 rate, GMC feed rejection, API error rate. For each: trigger, threshold, action, and how the breaker is reset (and who can reset it).
- An **append-only action ledger** with before/after state and rollback pointers — the mechanism that makes "self-healing" possible at all.

### P6 — Self-healing: the full failure surface
Enumerate every way this system (and its dependencies) can break, and for each: detection, diagnosis, auto-repair if safe, escalation if not. At minimum cover: expired OAuth refresh token (has broken this account before — the GSC token needs refresh every 30 min), dead GA4/pixel forwarding, Shopify web pixel stopped firing, conversion action disabled or deleted, ads disapproved, policy violation, landing page 404/degraded performance, GMC feed rejection, stale warehouse tables (GSC is currently 3 days stale), API quota exhaustion, the pixel endpoint down, disk full (82% already, and Chrome profiles accumulate), and the system's own outputs being wrong.
Also required: **a watchdog for the watcher** — who notices when the autonomous system silently stops running?

### P7 — Self-learning without overfitting noise
The system must learn, but at this data volume naive learning is guaranteed to learn garbage. Specify:
- The **belief/memory structure**: what hypotheses exist, how evidence accumulates, how beliefs are revised, how beliefs are retired. (Candidate: per-keyword/per-ad-group/per-audience/per-creative-archetype posterior with explicit priors derived from GSC + market research, not from scratch.)
- **Hierarchical pooling / shrinkage** — how a low-data entity borrows strength from its parent (keyword → ad group → campaign → account), so the system does not conclude "this keyword is terrible" from 3 impressions.
- The **decision ledger with outcomes**: every action recorded with its rationale, its predicted effect, and the realised effect — so the system can evaluate *its own judgement*, not just campaign metrics.
- **Counterfactual discipline**: because budgets move, attribution is imperfect, and seasons change, define what counts as valid learning evidence. Include a holdout/control design (a small always-on control, or a geo/time-based split) even though volume is tiny.
- **Drift and decay detection**: what happens when yesterday's winner stops working; how the system distinguishes fatigue, seasonality, competitor moves, and market-level changes from noise.
- **Anti-thrashing**: how the system prevents oscillation between two states.

### P8 — Self-initiation: the opportunity engine
Where do new campaigns, ad groups, ads, keywords, and negatives come from? Specify the full pipeline from **raw signal → opportunity → proposal → gated launch**:
- **Demand sources**: Google Ads search-term reports, GSC `traffic_daily` (including queries with impressions but no clicks — free demand signal), Autosuggest expansion (`keyword-intel.py`), competitor sitemaps and competitor review mining, SERP analysis (`SERPER_API_KEY`), Reddit/Trustpilot VOC, and the existing ICP document's pain-point language (`nordisk-icp.md`).
- **Opportunity scoring**: a concrete scoring formula combining demand, intent stage, ICP fit, margin, competitive density, and landing-page readiness.
- **Landing page readiness** — the system may only launch an ad group when a matching landing page exists and passes its checks. Define this gate explicitly (ties to §4.2, §4.5, §4.8).
- **Negative keyword engine**: discovery (search-term mining, competitor brand handling, cross-language junk, irrelevant category clustering), auto-application thresholds, shared negative lists at account level, and the "broad match requires ≥20 verified negatives" precondition.
- **Ad copy generation**: reuse and extend the existing `ad-copy-library.md` and `ad-creative` skill; enforce the §4.6 vocabulary ban; define RSA asset counts, pinning policy, and how assets are rotated and tested.
- **Language/locale**: how SV and EN campaigns are kept separate, how locale is detected for a keyword, how mixed-language traffic is excluded, and how landing page language is verified against campaign language.
- **Awareness-stage and journey mapping**: define the taxonomy you will use (e.g. unaware → problem-aware → solution-aware → product-aware → most-aware), how a keyword maps to a stage, and how the stage determines the ad format, landing page, and CTA. Include how the **content library** (23 articles, comparison pages, educational pieces) is used as a TOF/MOF asset map with the articles tagged by stage, pain point, and ICP segment — you may specify the tagging schema, and the system will backfill it.
- **Brand vs non-brand vs conquest**: separate governance, separate targets, separate negatives (the existing list already excludes own-brand in conquest).

### P9 — Scaling and budget optimisation that is honest about its limits
Define the budget model precisely: allocation method, increment sizes, cooling-off, per-campaign caps, diminishing-returns handling, whether to shift budget by marginal CPA/ROAS or by a bandit, how the system handles a campaign that is capped by budget vs capped by rank, and how seasonal demand (Swedish market seasonality — dry skin in winter, hard-water regions) enters.
Include the **scaling ambition** Maestro asked for: what triggers a step-up, what is required to justify it, and what the maximum scaling slope per week is.
Explicitly reject naive "scale by share of spend" (that is what exists today and it is circular).

### P10 — Orchestration substrate and durability
Choose and justify: plain cron + Python, a DAG runner, or **Temporal** (which is available, and offers durable execution, retries, timers, sagas, and signals). Define:
- The set of scheduled jobs, their cadence, their dependencies, and their failure semantics (retry vs escalate).
- **Idempotency** for every mutating action (a retried mutate must not double-apply).
- Long-running processes (a 100-day refund window implies state that lives for 100 days — this favours durable workflows over cron).
- The **human-in-the-loop interface**: how findings, proposals, approvals, incidents, and weekly digests reach Maestro on Telegram; and how approvals are expressed in a way the system can parse.
- The **kill switch** — a single, obvious way to stop all autonomous action immediately, plus a "read-only mode".

### P11 — Evaluation: how anyone knows the system is working
Design the eval harness before the system, not after.
- **Baseline**: what is today's number, measured how, over what window (spend, clicks, conversions, CPA, ROAS, contribution margin — in AUD and SEK, with the FX rate recorded).
- **Guard metrics** (must not degrade): tracking integrity, landing page 200 rate, policy compliance, spend cap adherence, currency correctness, zero paused-campaign leakage.
- **Success metrics**: contribution-margin ROAS, new-customer CPA, profitable-keyword count, share of spend on converting terms, budget utilisation, time-to-detect for breakage.
- **The system's own judgement quality**: did the actions it took do what it predicted? Precision/recall of its diagnoses.
- **Review cadence** — daily automated, weekly human, monthly strategic.
- **A kill criterion** — the condition under which the system should be turned off.
- **Statistical honesty**: state plainly which comparisons are not yet meaningful at current volume, and define the date/volume at which each becomes meaningful.

### P12 — Observability and the single screen
Define what Maestro sees, and where. One digest, at a fixed time, that answers: what did the system do, what did it spend, what did it earn, what is broken, what does it want approval for, and what did it learn. Specify the exact Telegram format (Telegram renders poorly — use Unicode box tables under 37 visible cells wide, never markdown pipe tables). Also define the incident log, the action ledger view, and where an audit trail lives.

### P13 — Data model
Specify the schema. At minimum: raw daily fact tables at the correct grain, entity dimension tables, the action/decision ledger, the belief/hypothesis store, the experiment registry, the landing-page registry (with URL, language, stage, ICP segment, pain point, last-verified 200 timestamp, owning article/theme section), the keyword registry (with stage, intent, locale, negatives, performance), the creative registry, and the incident table. Be explicit about **grains and keys** — most analytics bugs are grain bugs. State how it relates to what exists (`nordisk.db`, `pixel_track.db`, `competitors.db`, the `product_facts` canonical-facts pattern from `nordisk_self.py`).

### P14 — Things Maestro did not name
Add your own list of missing concerns with a concrete design for each. This section carries real weight in the review. Candidates you should consider and either include with a mechanism or reject with a reason (this is not an exhaustive list, and inventing more is encouraged): incrementality/geo-lift testing, brand-lift and halo effects, paid↔organic cannibalisation (ads stealing clicks that would have come free), auction dynamics and competitor response, Quality Score and Ad Rank economics, ad-strength and asset diversity, audience and remarketing list health and size thresholds, exclusion lists, IP/bot click filtering and invalid traffic, click fraud, consent mode and the EU/GDPR/Swedish legal context for tracking (this is a Swedish store — consent is load-bearing for GA4 and for Google Ads enhanced conversions), price/promotion coordination with ads, inventory and stockouts (do not advertise what cannot ship), shipping-time promises by region, competitor price moves, review/rating changes that shift conversion rate, seasonality, refund/return rate by acquisition source, contribution from email/SMS to paid cohorts, creative fatigue curves, and a coherent answer to "what does this do when it is out of ideas?"

---

# 8. WHAT TO BUILD ON, NOT REPLACE

Do not propose a greenfield rewrite that discards these. Extend them, and say explicitly for each how your design relates to it:

1. `google-ads/ops-operations.md` — the UTM scheme and the 3-layer threshold table (fix the thresholds for real volume; keep the UTM scheme).
2. `google-ads/negatives.md` — the categorised Swedish negative list (make it machine-readable and continuously grown).
3. `google-ads/campaigns/*.json` — the five campaign blueprints (brand, standard shopping, competitor, long-tail problem, investigative).
4. `google-ads/campaign-architecture-v3.md` — the current campaign architecture thinking.
5. `google-ads/landing-page-inventory.md` — the existing LP map.
6. `google-ads/ad-copy-library.md` — existing copy assets.
7. `google-ads/pipeline/01..04.js` — the four analysis jobs (supersede or absorb them, don't silently orphan them).
8. `bin/harvesters/ads-monitor.sh` + `bin/weekly-ads-checkpoint.sh` — the monitors (absorb into the new loop).
9. `bin/refresh-ads-data.sh` + `ads_campaigns` table — the existing warehouse ingestion.
10. `bin/pixel-tracker/*` — the first-party tracking core.
11. `nodes/nordisk_self.py` + `product_facts` — **the canonical-facts pattern must be imitated for ad copy specs and product claims.**
12. `keyword-intel.py` + `keyword-intel.db` — keyword demand (extend, don't duplicate).
13. `nordisk-icp.md` — the persona/pain source of truth (machine-tag it; don't re-research it).
14. `/root/.nordisk/guard/theme_guard.py` — the landing-page publish gate.
15. MemPalace — cross-session memory (the ads system should write its learnings there, and read them at session start).
16. The `loopy` / `graphopt` / eval-harness patterns in `/root/loops/` and `/root/harness-opt/` — the fleet already has a self-improvement idiom; conform to it.

---

# 9. REQUIRED OUTPUT

Return **one** Markdown document, titled `AUTONOMOUS-ADS-ARCHITECTURE.md`, with exactly these top-level sections in this order. Do not add a preamble, do not add marketing prose, do not open with a summary of the brief.

```
## 0. Design Principles            — max 12 numbered principles; each one sentence + why
## 1. System Overview               — the loop in plain language + one ASCII diagram
## 2. Capability Register           — every capability used, mapped to §5 inventory;
                                      plus a table of REQUIRES-NEW-ACCESS items
## 3. Objective Function            — the exact metric(s), formula, currency, caps, risk appetite
## 4. Data Model                    — tables, grains, keys, relationships, retention; DDL-level detail
## 5. Attribution & Reconciliation  — truth hierarchy, join keys, tolerance, incident behaviour
## 6. Sensing Layer                 — every data pull, cadence, source, write target, staleness rule
## 7. Reasoning Layer               — LLM roles, prompt contracts, validation, fail-closed, cost budget
## 8. Decision Layer                — policy tables: action class -> trigger -> authorisation ->
                                      blast radius -> velocity limit -> rollback
## 9. Action Layer                  — every executable action, its API call shape, preconditions,
                                      idempotency key, post-verification
## 10. Opportunity Engine           — demand sources -> scoring -> proposal -> gated launch
## 11. Keyword, Negative & Intent Engine
## 12. Funnel / Stage / ICP / Locale Matrix — the tagging taxonomy + who fills it
## 13. Budget & Scaling Engine
## 14. Self-Healing                 — failure surface table: detect / diagnose / repair / escalate
## 15. Self-Learning                — belief store, revision rules, evidence discipline, anti-thrash
## 16. Orchestration                — jobs, DAG, durability, idempotency, kill switch, read-only mode
## 17. Human Interface              — Telegram digest spec, approval protocol, escalation ladder
## 18. Evaluation Harness           — baseline, guard metrics, success metrics, review cadence, kill criterion
## 19. Safety, Compliance & Guardrails — every §4 constraint mapped to its enforcement point in code
## 20. Phased Build Plan            — see §10 below; this is the section the Builder works from
## 21. Explicit Non-Goals           — what this system must NOT do, and why
## 22. Open Questions for Maestro   — max 10, each with a recommended default so work is never blocked
```

---

# 10. BUILD-PLAN FORMAT (Section 20 — read carefully)

Section 20 is the only section the coding agent executes from. It must be a **phased, unit-level plan**, not a narrative. Use this exact structure:

For each **phase**: name, goal, why it comes at this point, exit criteria (observable and testable), and what is explicitly deferred.

For each **unit inside a phase**:
```
UNIT <n.m>  <short name>
Purpose:        one sentence
Files:          exact paths to create or modify
Depends on:     unit ids
Interface:      inputs (type, source) / outputs (type, destination)
Implementation: 3–8 bullet points, specific enough to code without design decisions
Test:           the exact command or assertion that proves it works
Acceptance:     the observable condition that closes the unit
Rollback:       how to undo it
Est. effort:    S / M / L
```

**Mandatory phase ordering constraints** (you may add phases, you may not reorder these):
1. **Measurement first.** Nothing acts until attribution and reconciliation are proven correct. A system that optimises on a wrong number is worse than no system.
2. **Read-only observation.** The system runs in shadow mode, produces its recommendations, and changes nothing — so its judgement can be compared against reality before it is allowed to act.
3. **Reversible actions only.** Negatives, ad rotation, asset additions, bid-modifier-free changes.
4. **Budget actions.** Only after gated dry-runs and with tight velocity limits.
5. **Campaign/landing-page creation.** Last, because it is the largest blast radius and it collides with the theme guardrail.

Every phase must ship something **useful and non-harmful even if all later phases are never built.**

---

# 11. OUTPUT RULES

1. **No code implementation.** You may include small illustrative code, SQL DDL, or JSON schemas where they remove ambiguity — but the deliverable is a spec, not a program.
2. **No invented capabilities.** If it is not in §5, mark it `REQUIRES NEW ACCESS` with provider, cost estimate, and grant needed.
3. **Every threshold must be a number** with stated reasoning. "Monitor closely" and "use good judgement" are rejected. Where you genuinely cannot pick a number without data, state the number you would pick *today* and the condition that would change it.
4. **Every mechanism must be testable.** If a claim cannot be checked by a script, it is not a spec, it is an opinion.
5. **Currency discipline is absolute.** Label every monetary figure AUD, SEK, or USD. State the FX rate you assume.
6. **Never reference paused campaigns** in any interface, report, or reasoning path.
7. **Respect the theme guardrail.** Landing page publication is gated, never autonomous.
8. **Prefer the existing idiom.** When a pattern already exists in this codebase (canonical-facts table, guard scripts with test suites, eval nodes, `--agent` JSON CLIs, append-only ledgers), use it rather than inventing a parallel convention.
9. **Quantify operational cost.** LLM tokens/day, API quota consumption, disk growth, cron load. This runs on one 38G-rooted box that is already 82% full.
10. **Be contrarian where the evidence demands it.** If part of Maestro's goal is unachievable at current volume, say so plainly, say what would make it achievable, and design the system to be *honest* about that rather than to simulate confidence. A system that reports a confident all-clear from broken data is the specific failure this project has already been burned by.
11. **No filler, no restating the brief, no motivational framing.** Dense, technical, buildable.
12. Length: as long as it needs to be. Completeness beats brevity here, but every sentence must carry information.

---

# 12. FINAL CHECK BEFORE YOU ANSWER

Confirm, in your own head, that a competent engineer reading your document could answer all of these without asking you anything:

- What exactly does "working" mean, and how is it measured, in which currency, at what cadence?
- Which numbers are truth, which are diagnostics, and what happens when they disagree?
- Who is allowed to spend money without asking, how much, how fast, and how is that bounded?
- What does the system do when it does not know something?
- What does the system do when it is broken, and who finds out?
- How does the system tell the difference between a signal and noise at 34 clicks a month?
- What is the smallest useful thing that can ship first, and how is it proven correct?
- What must this system never do?

If any answer is "it depends on the reader's judgement", the spec is incomplete. Fix it before returning.
