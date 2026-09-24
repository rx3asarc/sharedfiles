# AUTONOMOUS-ADS-GENERATIVE-LAYER.md

Companion extension to `AUTONOMOUS-ADS-ARCHITECTURE2.md` (v2.3 → v2.4).
Version 1.0, 2026-09-24. Adds **Phase 1c — Generative Layer** (UNIT 1.19–1.23) and amends
§12.1, §12.4, §12.5, §12.6, §13.1, §13.2, §21, §22, §23 of the parent spec.

**Owner decision this responds to (Maestro, verbatim):** *"it is a fully autonomous self learning
self healing self propelling google ads environment… I want it to be able to launch new campaigns
and new adgroups and new ads and take into consideration keywords as well as negative keywords as
well as language and also landing page url and also awareness stage and customer journey and ICP
and pain points and brand and competition and educational content and informational and purchase
intent and awareness stages and so on. There are a lot of things I'm not thinking about here, I
don't know what they are."*

---

## GL.0 Why this document exists

### GL.0.1 The problem is vocabulary, not engine

The parent spec already specifies the self-propelling loop in detail: §12.11 (winner loop and
funnel cascade, seven of eight steps autonomous), §12.12 (100-idea bank), §12.10 (pattern library
with attribute-pooled posteriors), §12.8 (diagnosis table: CTR low → HOOK, engaged low →
PROMISE_DISCONNECT, ATC low → DESIRE). That loop is sound and this document does not change it.

What the parent spec constrains is the **range of expressions the loop may emit**:

| Dimension | Parent spec position | Where |
|---|---|---|
| Topic research / persuasion grounding | **Absent.** §12.1's inputs are entirely internal — product facts, VOC, past ad copy, archetype weights, fail memory. No input researches a topic or cites a principle | §12.1 |
| Lander archetypes | `lander_class` = `PRODUCT, COMPARISON, PROBLEM, GUIDE, GEMPAGES, HOME, ARTICLE, COLLECTION`. No advertorial, listicle, "N reasons", or authority-story class | §13.1 |
| Generated imagery | **Banned.** "Product images from Shopify… No generated product images" + §22.6 | §12.5, §22.6 |
| Display / demand-gen prospecting | **Parked** until Stage 4; `role` enum has no DISPLAY | §22.3, §13.1 |

Maestro named all four dimensions unprompted, from memory, before reading §12. The gaps were
therefore not unknown to him — they were **decisions in sections he had not read**. This document
converts those implicit decisions into explicit, sequenced ones.

### GL.0.2 The governing constraint: vocabulary expansion costs guardrail surface

Every unit here is qualitatively different from the parent spec's units. A bidding change is
bounded by the governor. **A new *kind* of page, or a new *kind* of image, is bounded by nothing
the parent spec already models** — because the parent spec's safety machinery (§12.4 claims gate,
§18 guardrails) was built to constrain *text within a known format*, not to vet a new format.

Two hard rules follow, and they apply to every unit in this document:

> **GL-R1 — A new archetype must declare its claim surface before it may be generated or routed to.**
> Each lander archetype states, in `taxonomy.toml`, which claim classes it may carry. An
> archetype that cannot enumerate its claim surface is not eligible for autonomous generation, and
> nor is it eligible to receive routed traffic.

> **GL-R2 — A new surface does not inherit the account's stage.**
> Each *surface class* carries its own stage, persisted on the surface. An account-wide stage must
> not silently grant a brand-new surface the autonomy earned by a different surface. New surface
> classes start **one rung below** the account stage and must earn each subsequent rung on their own
> evidence.

GL-R2 exists because the parent spec's stage model is *account-wide*, and that is the specific way
this extension could break something.

**GL-R2a — why archetypes start at Stage 1 (reversible), not Stage 0 (shadow).** Stage 0 is defined
as *shadow observation*: it makes no changes and predicts what it would have done. That is coherent
for a surface that already exists (imagery, display) because there is behaviour to predict against.
It is **incoherent for a brand-new format**, which has no prior behaviour to observe — the archetype
would need a track record to leave Stage 0 and would need to generate to acquire one. Archetypes
therefore enter at **Stage 1**, which is the correct rung: a Shopify Page has a clean, tested inverse
operation (`published:false`), which is precisely what Stage 1 requires. If shadow-style evidence is
wanted, the archetype's first deployment runs as a 50/50 content experiment against the incumbent,
which is a Stage-1 action producing comparable evidence.

**GL-R2b — GL-R2 must be persisted to be enforceable.** A stage rule with nowhere to store the stage
is a policy, not a control. Required storage: `archetypes.surface_stage`, `image_assets.surface_stage`,
and a persisted display-surface stage (not merely a computed `scope.toml` predicate). See §GL.7.

---

## GL.1 Scope

### GL.1.1 What this adds

| Unit | Name | Phase | Autonomous at | Blocks |
|---|---|---|---|---|
| 1.19 | Persuasion & evidence corpus | 1c | n/a (knowledge base) | 1.20 |
| 1.20 | Research brief generator | 1c | Stage 2 (advisory only until then) | 1.21, §12 generation |
| 1.21 | Archetype layer & claim surfaces | 1c | Stage 1 on first use, earning rungs per GL-R2 | §11.6 routing |
| 1.22 | Imagery module + Art. 50 compliance | 1c (guardrails) / Phase 5 (generation) | **never for Representational** | §12.5, display |
| 1.23 | Display / demand-gen readiness | scope decision in 1c, build in Phase 7 | Stage 4 | — |

### GL.1.2 What this does NOT change

- §12.4's claims gate is **extended, not replaced**. All existing banned phrases and spec-truth
  rules survive verbatim.
- The spend governor (§3.5), the cap layer (§4.13), the ledger, inverse operations and the five
  gates are untouched.
- The theme guardrail is untouched and is the binding constraint on 1.21 (§GL.4).
- Article featured images stay manual-only. Nothing here writes an `image` key.
- No unit here changes a bid, a budget or a threshold.

### GL.1.3 Evidence discipline for this document

The parent spec's §0.2 rule — *a number supplied by a person or pasted from chat enters as
`NO_DATA` until a named, stored query reproduces it* — is applied here to **claims, not just
numbers**. Accordingly §GL.9 records, per clause, whether it is grounded in a retrieved primary
source or is a design assertion. Clauses written from unretrieved model knowledge are labelled
`UNVERIFIED` and carry a verification obligation. Two research passes for this document returned
knowledge-only briefs without web access; their content is recorded as `UNVERIFIED` and was
**not** used to write any normative clause.

---

## GL.2 UNIT 1.19 — Persuasion & evidence corpus

### Purpose
Give the generator a **citable, tiered** set of persuasion and advertising principles, so that
angle selection is grounded rather than improvised — and so that the system cannot launder folklore
as evidence.

### The governing insight
Most copywriting frameworks circulating in 2026 are **transcribed folklore**. Several are
unfalsifiable as stated ("5 stages of sophistication", "30 psychological triggers", "8 life-force
desires"); at least one contains a mechanism that modern neuroscience rejects outright. A corpus
that stores these as fact would make the system *more* confident and *less* correct.

The corpus is therefore **not a list of principles**. It is a list of principles *with their
evidence grade, boundary conditions, and forbidden renditions attached*, plus a hard blocklist the
generator may never cite.

### GL.2.1 Evidence tiers (schema)

| Tier | Meaning | Admissible use |
|---|---|---|
| **T1** | Meta-analysis, preregistered replication, large-scale field experiment, or large econometric dataset with disclosed sampling | May inform a decision directly |
| **T2** | Real evidence with documented boundary conditions; effect sizes from the pre-2011 small-sample era should be **discounted (~half)** per the broad replication findings | May inform a decision **only with boundary conditions attached** |
| **T3** | Practitioner heuristic — no research base, or unfalsifiable as stated | **Hypothesis only.** Requires a registered measurement proxy in the same commit. Auto-labelled `HYPOTHESIS` in every rationale |
| **T4** | Debunked: failed replication, retraction, or documented folklore | **Hard-blocked.** Enforced as an *output lint*, not merely a retrieval filter |

T4 is enforced on generated text because LLMs readily restate folk mechanisms as science: if a
blocked mechanism exists anywhere in the corpus prose, it will eventually appear in generated copy.

### GL.2.2 Blocklist (T4) — must be linted in output, not just filtered in retrieval

Each entry requires a documented replication or validity failure before inclusion. Seed list:

| Blocked mechanism | Failure |
|---|---|
| Social/behavioural priming ("subconscious priming makes people buy") | Elderly-priming walking-speed effect failed to replicate with an experimenter-expectancy explanation; unconscious-goal priming RRR found no effect |
| Ego depletion ("willpower is finite, so buy now") | Two large multi-lab tests found ~zero effect |
| Subliminal persuasion | The originating 1957 study was self-admitted as a gimmick; consumer-choice meta-analysis found no meaningful effect |
| Mirror-neuron explanations of ad response | Mirror-neuron theory of action understanding has documented problems |
| Neuro-linguistic programming (eye-accessing cues, "representational systems") | Systematic review found no support for claimed outcomes |
| Power posing as a sales/confidence lever | Hormonal/behavioural claims failed replication; evidential value only for self-reported feelings |
| Choice overload ("fewer options always convert better") | Meta-analysis found no reliable mean effect |
| Triune / "lizard brain" mechanism | Unsupported in modern neuroscience — the parent spec's own §20 ambitions do not rescue it |
| Neuromarketing "buy button" | Legitimate research area; commercial claims outrun the evidence |
| Stanford Prison Experiment as authority evidence | Substantially documented as coached/directed |

**Rule:** T4 entries may appear in the corpus **only** in `blocked_mechanisms`, never in
`principles`. A generated rationale that names a verified T4 mechanism is a gate failure.

**The verification asymmetry — and it runs the right way.** The tier hierarchy downgrades
*unverified* entries to T3 (they may inform, but only as labelled hypotheses). The blocklist must
downgrade in the same direction and for the same reason:

> **GL-R3 — only a verified entry may BLOCK.** An entry with `verified: false` loads as `WARN`
> (advisory: the generator is told not to cite it, but its presence does not fail the gate). It
> becomes `BLOCK` only once its failure citation has been checked against its source. An incorrect
> blocklist entry silently kills a legitimate technique, and — unlike the T3 downgrade — has no
> automatic catch.

**Scope of the lint.** The lint targets *persuasion mechanisms that could appear as reasoning in
generated copy*. Entry classes that cannot plausibly surface in ad copy (e.g. a research-ethics or
methodology failure such as the Stanford Prison Experiment) do not belong in an output lint; they go
in a separate `do_not_cite_as_authority` list, which is a sourcing rule rather than a generation gate.
Including them in the lint inflates it and blurs what it enforces.

### GL.2.3 The boundary the corpus must respect (and the parent spec already enforces)

The corpus is *persuasion* input. It is **not** a licence to make claims. The two are separate
gates and the claims gate always wins:

- A T1-supported principle may still be **unusable** because the claim it implies is not on
  `product_claims`. Authority framing may not create authority that does not exist.
- Scarcity/urgency tactics are **constrained by truth**, not by tier: scarcity language is admissible
  only when the constraint is literally true (real stock, real deadline). Fake countdowns and fake
  stock counters are separately regulated as unfair commercial practices.
- Fear-based angles require a paired efficacy statement — fear appeals without efficacy content
  risk defensive avoidance and backfire.

### GL.2.4 Modern evidence that *bounds* the classics

The corpus cannot be a flat list, because parts of the modern literature **contradict** parts of the
classics. Where they collide, the collision is recorded and a precedence rule is set — not averaged.

| Collision | Precedence rule adopted |
|---|---|
| "Differentiate via a unique proposition" vs. evidence that perceived differentiation is largely illusory and driven by salience/distinctive assets | **Adopt distinctive-assets + one clear claim.** Treat "our claim is unique" as a **checkable proposition**, never an assumption |
| Funnel/AIDA hierarchical models vs. evidence that advertising effects are often non-hierarchical | Awareness-stage routing survives as a **message-fit heuristic**. The system must not claim or optimise on a funnel-causal model |
| Long-form copy doctrine vs. low-involvement feed formats | Length is gated by involvement and format |
| Brand-building vs. per-ad ROAS optimisation | **The deepest collision.** A per-ad optimiser systematically selects most-aware direct-response principles and starves upper-funnel salience work. See §GL.2.6 |

### GL.2.5 The base-rate warning the corpus must carry

The corpus must ship with its own humility clause, because the system will otherwise read its
posteriors as more informative than they are:

- Across a large body of real split-cable tests, roughly **half of tested ads produced no sales
  increase**, and increasing weight did not reliably increase sales.
- Meta-analytic mean short-term advertising elasticity is small (~0.1), decaying over time.

**Consequence:** the prior probability that any given principle-driven ad works is near a coin flip,
and most single-ad "learnings" will be noise being fitted. This is the same finding §20.6 of the
parent spec already reaches honestly. The corpus must state it, and the pattern library must weight
accordingly rather than treating a WINNER bucket as evidence of a law.

### GL.2.6 Brand/activation policy — an owner decision, not a build item

A system that optimises short-term contribution (the parent spec's §3 objective) will converge on
most-aware, direct-response angles. That is correct *for the objective as written* and wrong as a
description of how a brand grows. The parent spec's T1 is a total-store target, so this matters.

This document does **not** resolve it. It records that one of three positions must be chosen before
Stage 3, and that the choice changes what the corpus is for:

1. **Activation-only** (status quo). Cheapest, honest, and consistent with §3. Accepts that the
   system will not build long-term memory structures.
2. **Fixed portfolio split.** A named fraction of budget reserved for upper-funnel/salience work,
   evaluated on a long-horizon metric. Requires a metric the account does not currently have at
   this volume.
3. **Defer.** Park upper-funnel until the account clears the volume floor where a long-horizon
   metric is even measurable.

**Default applied (so work is not blocked):** option 1, explicitly labelled as such in the weekly
digest, so the limitation is visible rather than implicit.

### Files & interface
```
ROOT/adsys/corpus/principles/{awareness,persuasion,structure,proof}.yaml
ROOT/adsys/corpus/blocked_mechanisms.yaml
ROOT/adsys/corpus/provenance.md            # per-entry: primary source, edition/page, verified flag
ROOT/adsys/corpus/__init__.py              # corpus.query(stage, tier_max, channel) -> [Principle]
```
Entry schema (normative):
```yaml
- principle_id: hopkins.specificity
  label: "Concrete specificity over generality"
  tier: T2
  tier_basis: "Concreteness effects documented; ad-specific sales evidence directional"
  source: {ref: "Hopkins, Scientific Advertising (1923)", verified: false}
  structure: {claim: "...", conditions: [...], predicted_effect: "..."}
  stage_fit: [problem_aware, solution_aware, product_aware]
  channel_fit: [search_nonbrand, lander, email]
  boundary_conditions: [...]
  forbidden_renditions: [...]
  measurement_proxy: "RSA CTR vs ad-group baseline posterior, feedback window"
  status: active
```

### Gates
- Every shipped entry has: a tier, a `tier_basis`, a `source.ref`, ≥1 `boundary_condition`, and a
  `measurement_proxy`. **An entry missing any of these does not load.**
- Provenance must point at a **primary text** (author, title, edition/year), never an agency blog or
  secondary explainer. Secondary sources are the documented vector for transcription errors —
  including the widespread compression of a five-stage model to three.
- Any entry whose `source.verified` is false is loaded with `tier: T3` **regardless of its claimed
  tier**. Verification promotes; it is never assumed.
- Corpus size target: **30–60 entries**. Not 300. Each must earn its place with a predicted effect.

### Acceptance
1. `corpus.query()` returns tier-filtered principles for every `(awareness, journey)` pair in §13.1.
2. A rationale generated with a T4 mechanism fails the output lint (Test: inject one, expect fail).
3. Every entry resolves to a primary source with a `verified` flag.
4. No entry claims a regulatory or legal effect without a cited instrument.

### Rollback
Corpus is a knowledge base: revert the directory. Entries referenced by live creatives are kept for
the life of the creative.

---

## GL.3 UNIT 1.20 — Research brief generator

### Purpose
Turn "we noticed angle X might work" into a structured brief that the archetype and copy stages can
consume — so that a new angle arrives *researched* rather than merely *asserted*.

### Why it is needed
§12.12's idea bank ranks 100 ideas by evidence tier and `EV = P(win) × upside`, sourced from
PROVEN queries, past audit winners, competitor weaknesses and ICP pain combinations. Every source is
**internal**. Nothing in the parent spec can answer *"what is this market actually talking about, and
what does this audience already believe?"* — which is precisely the input that decides awareness
stage, and therefore angle and format.

### Interface
```
in:  {angle_id | pain_point | query_cluster, market, product}
out: research_brief.md + brief.json
```
`brief.json` is the contract; `research_brief.md` is for the digest and the owner.

```jsonc
{
  "brief_id": "...",
  "topic": "...",
  "market": "sv-SE",
  "query_evidence": [ {query, clicks, impressions, position, source, window} ],
  "audience_beliefs": [ {belief, support, source_ref, confidence} ],
  "awareness_hypothesis": "PROBLEM_AWARE",
  "awareness_basis": "...",                  // required; may not be empty
  "competitor_moves": [ {competitor, observation, source_ref} ],   // no trademarks in copy
  "pain_language": [ "...", "..." ],         // VOC phrases, from tax_icp_segment
  "claim_candidates": [ {claim_id, why_applicable} ],  // MUST resolve in product_claims
  "principles": [ {principle_id, tier, fit_reason} ],
  "gaps": [ "what the research could not establish" ],
  "sources": [ {url, retrieved_at, kind: primary|secondary} ],
  "confidence": "low|medium|high"
}
```

### Hard rules
- **`claim_candidates` must resolve in `product_claims`.** Research may propose a *candidate*;
  only the claims gate admits it. A brief that proposes a claim not on the spec sheet is a
  gate failure, not a near miss.
- **`awareness_basis` is mandatory.** A stage assigned without a stated basis is a guess, and a
  guess that silently routes format and copy.
- **`gaps` is mandatory and may not be empty.** A research brief that found nothing uncertain did
  not do research. Same discipline as §0.2 and §20.6.
- Sources are typed `primary | secondary`. A brief resting only on secondary sources is capped at
  `confidence: low`.
- **Competitor observations never enter copy as trademarks.** §12.4's trademark ban is unchanged;
  competitor findings inform *differentiation*, not *naming*.

### Autonomy
Advisory until Stage 2. From Stage 2 it may trigger automatically when: a PROVEN query has no ad
group, or a `PROMISE_DISCONNECT` diagnosis fires, or an idea-bank entry reaches tier 1–2 with no
brief attached. It writes a brief; it never writes live copy directly.

### Acceptance
- A brief on a known topic reproduces the awareness stage a human would assign, with a stated basis.
- Every `claim_candidates` entry resolves or the brief fails.
- `gaps` non-empty in a sample of 10 briefs.

### Rollback
Briefs are artifacts. Delete or supersede; nothing live depends on one by reference.

---

## GL.4 UNIT 1.21 — Archetype layer & claim surfaces

### Purpose
Widen what the system can *build* beyond "fill an existing template", while keeping the theme
guardrail intact — and name the archetypes so §13.1's taxonomy can route to them.

### GL.4.1 What actually exists — and the correction that changes this unit

Maestro asked for four archetype families: *advertorial*, *listicle ("10 things for X")*,
*authority/trust story*, and implicitly a data/report shape. Reconnaissance of the theme repository
(`/mnt/HC_Volume_105587324/nordisk/theme-repo`, remote `rx3asarc/nordiskrenhet-theme`) found a
genuinely valuable design asset — and then found the reason it **cannot** be the generation
substrate.

**What exists (all verified by direct inspection):**

| Asset | Count | What it is |
|---|---|---|
| Native `nr-*` sections | **12** | `nr-hero`, `nr-reason`, `nr-comparison`, `nr-faq`, `nr-guarantee`, `nr-study`, `nr-testimonial`, `nr-trust-band`, `nr-value-stack`, `nr-kit`, `nr-cta-bar`, `nr-sticky-cta` |
| `nr-*` snippets | **7** | design tokens, image helper, landing fonts, trust/CC icons, band style |
| Native listicle templates | **2** | `page.nr-4-reasons.json` (13 sections, 11 native), `page.nr-8-reasons.json` (19 sections, 17 native) |
| GemPages-derived page templates | **2** | `page.science.json` (14 sections, 0 native `nr-*`), `page.water-report.json` (1 section, 0 native `nr-*`) |

**The blocking fact — two of them, and together they invert the obvious conclusion.**

**Blocking fact 1: the `nr-*` templates are fully-authored fixed pages, not parameterised ones.**
`page.nr-8-reasons.json` hardcodes its copy — the hero heading, all eight reason headings, the kit,
guarantee, FAQ and comparison copy are literal strings in the template JSON. It hardcodes five
links to `/products/nordisk-welcome-kit`. Critically:

- **No `nr-*` section renders `page.content`** (verified: zero matches).
- **No `nr-*` section reads page metafields** (verified: zero matches).

So setting `template_suffix` on a new Page yields a **byte-identical clone** of the athlete listicle.
Per-page variation through mechanism B is structurally impossible without either a new template file
— a theme push *per page* — or a refactor of the sections to be settings/metafield-driven, which is
a build this document does not contain. `max_sections` / `required_sections` are likewise
unenforceable against a static template, whose section set is fixed.

**Blocking fact 2: `page.science` and `page.water-report` are GemPages-derived, and §12.6 states
GemPages pages are routable but never created or edited by adsys.** They are *rendering shells* and
*design references*, not inherited generatable artefacts. (`page.water-report` is additionally a
minimal one-section content shell, not a designed report.)

**The correction — and it is a better architecture than the draft had.**

There are **two mechanisms**, and only one of them is a generator:

| | **A. Content-driven — THE GENERATOR** | **B. Section-driven — hand-built designs** |
|---|---|---|
| Mechanism | Shopify Pages with `body_html`; the template renders `{{ closest.page.content }}` | `template_suffix` selects a template whose sections carry literal copy |
| Theme write? | **No** | **Yes — one push per variant** |
| Variety | **Unbounded** | **None** — same template twice = identical clone |
| Live today? | **Yes** — `page.json`, `page.contact.json`, `page.water-report.json`, `page.science.json` all render `{{ closest.page.content }}` (as a `text` block setting, and via `blocks/page-content.liquid`) | `page.nr-*` exist in the repo but are **absent from the live theme** |
| Marginal cost | zero | one owner-gated push **per page** |

**Therefore an archetype in this system is a *content template* — the HTML skeleton, section order,
claim surface and required elements that adsys writes into `body_html` — not a Shopify theme
template.** This is also what the parent spec's §12.6 already describes ("body from R8 constrained to
facts/claims"): the autonomous path was always the body, and the theme-template route was never it.

The `nr-*` library keeps real value: it is the **reference implementation** each content template
should imitate (its section vocabulary, its listicle rhythm, its guarantee/sticky-CTA structure are
exactly the commercial disciplines §GL.4.5 encodes). It becomes a generator substrate only after a
metafield/settings refactor that is **not** in this document and must not be assumed.

**Granted/parked: the honest count.** Of the four requested families, **all four are achievable as
content templates** (that is new capability, not inheritance), and **one** (listicle) additionally
exists as a designed section-driven page. Nothing here should be read as "3 of 4 already built":
what was already built is the *design vocabulary*, and reusing it per page was never possible.

### GL.4.2 The publish question, restated

`nrtheme status` against live theme `195492381006` reports **27 files present in the repo but absent
from the live theme**. *(The tool's header prints the count 27; its listing prints 15. The stated
decomposition — 6 Barlow font assets + 12 `nr-*` sections + 7 `nr-*` snippets + 2 `page.nr-*`
templates — is an inference from the directory listing plus the header count, not a printed list. It
reconciles exactly, but it is inference and is labelled as such.)*

Given §GL.4.1, publishing that library is **no longer on the critical path for generation**. It is
worth doing on its own merits (the designs are finished; G26 records that nothing has ever been
published so there is no perf or conversion evidence for any of it), but it is not the unlock the
draft claimed, and it must not be presented to the owner as "one approval buys a page factory".

What publishing *does* buy: the two designed listicle pages become live and routable as fixed
showcase pages, and the section vocabulary becomes available to any future metafield-driven refactor.

### GL.4.3 The dependency chain (corrected)

```
CONTENT PATH (the generator — no theme write, available now)
  content template  ──> body_html ──> Shopify Page ──> renders via {{ closest.page.content }}
        │                    │
        │                    └─> §12.6 gates (claims, MOE, nrshot, nrperf) ──> published
        └─> archetype claim surface (GL-R1) + required_sections

SECTION PATH (design asset — theme write, one push per variant)
  nr-* refactor to metafields  ──[NOT IN THIS SPEC]──> would make nr-* a second generator substrate
  nr-* publish (owner-gated)   ──> fixed showcase pages only
```

Everything downstream of the content template is autonomous. The content path needs **no** theme
approval and therefore has no per-class approval cost at all — which is a stronger property than the
draft claimed, and the opposite of "one approval per template class". The section path needs one
approval **per page**, which is why it is not the generator.

### GL.4.4 Amended `lander_class` enum

Parent spec §13.1 enum is
`PRODUCT, COMPARISON, PROBLEM, GUIDE, GEMPAGES, HOME, ARTICLE, COLLECTION`.

Add (each generated as a **content template** per §GL.4.1, each with a declared claim surface per
GL-R1):

| Added `lander_class` | Content shape | Claim surface it may carry | Stage fit | Render through |
|---|---|---|---|---|
| `LISTICLE` | N-reason skeleton | PROOF, SPEC, GUARANTEE, BENEFIT, ECONOMIC_SAVING *(sourced only)* | SOLUTION_AWARE, PRODUCT_AWARE | `page.water-report`, `page.json` |
| `ADVERTORIAL` | narrative → mechanism → offer | PROBLEM_STATEMENT, SPEC, GUARANTEE | PROBLEM_AWARE, SOLUTION_AWARE | `page.water-report`, `page.json` |
| `AUTHORITY` | proof-first | PROOF, SPEC only; study blocks must cite a real source or be omitted; **no fabricated quotes** | SOLUTION_AWARE, COMPARISON | `page.science`, `page.water-report` |
| `REPORT` | data-first | PROOF, SPEC, data claims with a named source | PROBLEM_AWARE, SOLUTION_AWARE | `page.water-report` |

**`ADVERTORIAL` was the one genuine "gap" in the draft and is not a gap under this architecture** —
as a content template it is simply an HTML skeleton, needing no theme work. The theme work that
*remains* genuinely absent is a metafield-driven `nr-*` refactor, which is optional and out of scope.

### GL.4.5 Claim-surface declaration (GL-R1 made concrete)

`taxonomy.toml` gains, per archetype, a claim-surface block. **A full block is required for every
archetype before it may generate or receive routed traffic** (GL-R1) — all four follow:

```toml
# NOTE ON template_suffix: this is the SUFFIX ONLY.
# templates/page.nr-8-reasons.json  ->  template_suffix = "nr-8-reasons"
# The file name and the suffix value are different strings; v2.4-draft used the file name.
# The content path does not need a suffix at all: it uses the default page template,
# which renders {{ closest.page.content }}.

[archetype.LISTICLE]
render_through   = "page.water-report"       # minimal shell; "page" = shell + page title header
content_template = "content/listicle.html.j2"
allowed_claim_classes   = ["PROOF", "SPEC", "GUARANTEE", "BENEFIT", "ECONOMIC_SAVING"]
require_sourced_arithmetic = ["ECONOMIC_SAVING"]   # see note below
forbidden_claim_classes = ["MEDICAL_OUTCOME", "SUPERLATIVE_UNSOURCED", "FABRICATED_TESTIMONIAL"]
max_sections     = 24
required_sections = ["hero", "guarantee", "sticky-cta"]   # matched against section.type
awareness_fit    = ["SOLUTION_AWARE", "PRODUCT_AWARE"]

[archetype.ADVERTORIAL]
render_through   = "page.water-report"
content_template = "content/advertorial.html.j2"
allowed_claim_classes   = ["PROBLEM_STATEMENT", "SPEC", "GUARANTEE"]
forbidden_claim_classes = ["MEDICAL_OUTCOME", "SUPERLATIVE_UNSOURCED", "ECONOMIC_SAVING", "FABRICATED_TESTIMONIAL"]
max_sections     = 20
required_sections = ["hero", "guarantee", "sticky-cta"]
awareness_fit    = ["PROBLEM_AWARE", "SOLUTION_AWARE"]

[archetype.AUTHORITY]
render_through   = "page.science"
content_template = "content/authority.html.j2"
allowed_claim_classes   = ["PROOF", "SPEC"]
forbidden_claim_classes = ["MEDICAL_OUTCOME", "SUPERLATIVE_UNSOURCED", "ECONOMIC_SAVING", "FABRICATED_TESTIMONIAL", "UNSOURCED_STUDY"]
max_sections     = 26
required_sections = ["hero", "study", "guarantee"]
awareness_fit    = ["SOLUTION_AWARE", "COMPARISON"]

[archetype.REPORT]
render_through   = "page.water-report"
content_template = "content/report.html.j2"
allowed_claim_classes   = ["PROOF", "SPEC", "NAMED_SOURCE_DATA"]
forbidden_claim_classes = ["MEDICAL_OUTCOME", "SUPERLATIVE_UNSOURCED", "ECONOMIC_SAVING", "FABRICATED_TESTIMONIAL", "UNSOURCED_STUDY"]
max_sections     = 22
required_sections = ["hero", "named-source", "guarantee"]
awareness_fit    = ["PROBLEM_AWARE", "SOLUTION_AWARE"]
```

- A generated page may not exceed `max_sections` or omit a `required_section`.
- A page containing a `forbidden_claim_class` fails the gate.
- `required_sections` are matched against **`section.type`**, not against section keys
  (`page.nr-8-reasons.json` uses keys like `nr_hero` for type `nr-hero`). The interpretation must be
  fixed or the gate is unimplementable.
- `required_sections` encodes the commercial discipline the cheapest-path analysis identified:
  guarantee and a persistent CTA are **structural**, not optional decoration.

**`claim_class` is a new vocabulary and must be reconciled with the existing claim model.** The
parent spec's §12.4 defines `line_type ∈ {PROBLEM_STATEMENT, CLAIM, CTA, BRAND, KEYWORD_ECHO}` and
binds each CLAIM line to `claim_id`s in `product_claims`. **No `claim_class` exists in the parent.**
So this unit must add a `claim_class` column to `product_claims` and define the class→`claim_id`
derivation; otherwise §12.4's fail-closed gate is enforcing an undefined term. Adding the column is
part of UNIT 1.21, not an assumed precondition. `PROBLEM_STATEMENT` is listed both as a `line_type`
and a `claim_class` deliberately (a problem statement is a line type that carries no claim); the
derivation must state that it maps to no `claim_id`.

**`ECONOMIC_SAVING` is permitted on `LISTICLE` subject to sourced arithmetic** — it may only appear
where the saving follows from `product_facts` (e.g. 13 000 L per cartridge at the stated price =
≈3.50 SEK/week, which the existing `nr_reason_06` heading already does). The v2.4-draft forbade it
outright, which contradicted the parent spec's §12.11 cascade step 5: that step builds an offer
"when the 'long-term savings' theme wins", and step 3 rebuilds the lander around the winning angle —
so forbidding the class would forbid the archetype from carrying the very theme the cascade is
propagating. Sourced-arithmetic keeps the real concern (unsourced savings claims) without the
contradiction.

### GL.4.6 The two open defects that must be closed first

The theme repo's gap register flags two defects that bear directly on a system whose purpose is to
drive purchases. Both are **OPEN** and both would make this unit produce plausible-looking pages
that do not sell:

- **G18 — add-to-cart / form submission never tested end to end.** "The buy button renders and
  points at the right variant+selling plan. Nothing proves a purchase completes." A lander factory
  that has never confirmed a purchase can complete is generating pages of unknown commerce value.
- **G17 — interactive components only checked statically.** A FAQ accordion that will never open
  passes every existing gate.

**Gate:** the archetype layer may not generate autonomously until G17 and G18 have executable checks.
Per the register's own rule — *"a check that has never failed has not been tested"* — each must be
demonstrated failing on a deliberately broken state before it may pass a real one.

### GL.4.7 Separately: a possible live revenue issue

The same register carries an unresolved item (**G21**): the `Nordisk Wellness Kit` reports
`inv=0` on both variants, **yet the live page's own cart form buys it**. The register says
"Possible live revenue issue — flagged, not resolved."

This is not part of the generative layer and this document does not resolve it — it is outside
scope and requires a human decision. It is recorded here because **unit 1.21 would route paid
traffic to Wellness-Kit-bearing landers**, and the cheapest-path analysis separately identifies
Wellness Kit as one of only two products that clear the non-brand break-even bar. If inventory is
genuinely zero, the highest-value routing target in the account is also the one that cannot be
fulfilled. **Owner action requested before 1.21 generates anything.**

### Acceptance
- `nrtheme status` reports zero `nr-*` files absent from live after the gated publish.
- §11.6 lander checks pass on each archetype instantiated from real data.
- G17 and G18 checks exist, are executable, and have been demonstrated failing on a broken state.
- A page generated for each archetype contains no `forbidden_claim_class` and all `required_sections`.

### Rollback
Unpublish the page (Shopify Pages: `published:false`). Template-level rollback is the theme guard's
snapshot/verify path, per §R3. Archetypes published but unused are inert.

---

## GL.5 UNIT 1.22 — Imagery module + Article 50 compliance

### Purpose
Make generated imagery usable where it genuinely helps (scroll-stoppers, mood, pattern disruption)
**without** creating a regulatory exposure the account does not currently have.

### GL.5.1 Status: this is live law, not a plan item — and it is already 53 days in force

Verified from retrieved sources on 2026-09-24:

| Fact | Value |
|---|---|
| EU AI Act Art. 50 transparency obligations applicability | **2 August 2026 — IN FORCE** |
| Days in force at time of writing | **53** |
| Digital Omnibus effect on Art. 50 | **None.** The Digital Omnibus (provisionally agreed 7 May 2026; Council final approval 29 June 2026) deferred **Annex III high-risk** obligations to 2 Dec 2027 / 2 Aug 2028. **Art. 50 transparency was not deferred** |
| Commission Guidelines on Art. 50 | **Final, published 20 July 2026** |
| Code of Practice on Transparency of AI-Generated Content | Published, with provider (marking) and deployer (labelling) sections |
| EU icons | Three optional icons (fully AI-generated / AI-modified / a third variant). Use is optional; **the labelling requirement is not** |
| Retroactivity | Content generated **before** 2 Aug 2026 need not be labelled retroactively (encouraged, not required) |

**And the substantive scope, which is broader than assumed:**

- Art. 50(4) binds the **deployer** — i.e. the brand, not the image tool.
- A **realistic synthetic depiction of a person who does not exist is a deepfake** — because such a
  person plausibly could exist. "We invented the face" is not an exemption.
- The Guidelines clarify that **clearly fantastical or physically impossible content** (their
  example: dragons, unaided human flight) falls **outside** the definition.
- The Guidelines further state the rules are **not confined to deceptive content** and that
  **ordinary commercial uses of generative AI may fall within scope**; marketing using synthetic
  depictions of realistic **people, places or events** is named as in scope.
- **Disclosure must be at first exposure**, clear and distinguishable, plain language, perceivable
  without technical tools or dedicated actions. It **cannot** be buried in file metadata or terms.
  For **display advertising, a label on the creative unit is the expected approach**.
- Deployers **cannot** satisfy the obligation by relying on the provider's machine-readable marking
  under Art. 50(2) alone.

### GL.5.2 The design consequence — stylised, not photorealistic

This resolves cleanly and in the direction Maestro already wanted:

| Imagery class | Art. 50 exposure | Design verdict |
|---|---|---|
| **Clearly stylised / illustrative / graphic / abstract** | Outside the deepfake definition because it does not satisfy the *"would falsely appear authentic or truthful"* prong of Art. 3(60). *(The Guidelines' separate carve-out for "clearly fantastical or physically impossible" content is a further, narrower safe harbour — its examples are dragons and unaided human flight — and is **not** the basis for the general stylised case. An earlier draft cited it as though it covered all stylisation; it does not.)* | **Preferred default.** No labelling overhead |
| **Photorealistic scene** (an invented bathroom, a plausible real place) | In the unsettled-to-risky band. Guidelines say ordinary commercial use may be in scope; a photorealistic scene that would appear authentic is the risk case | **Disclose**, or better: don't generate it photorealistic |
| **Realistic synthetic person** | **Is a deepfake by the Guidelines' own reading**, even if invented — "such a person plausibly could exist" | **Disclose. Never as a customer, reviewer, expert, employee or endorser** |
| **Any depiction of results / before-after / performance** | Highest risk under Swedish marketing law independently of AI | **Forbidden outright** |

Two payoffs converge:

1. **Compliance argues for stylised.** A clearly non-photorealistic visual does not satisfy the
   "appears authentic" prong of the deepfake definition, which removes a labelling burden and a legal
   uncertainty at once.
2. **Performance argues the same way.** Maestro's own requirement for display creative was "a scroll
   stopper… should invoke pattern disruption." A stylised, non-photorealistic visual disrupts a
   photorealistic feed far more reliably than another photograph of water.

So the compliant choice and the effective choice are the same choice. This is the rare amendment
that costs nothing.

### GL.5.3 The clause (normative)

**AI-1 — Classification.** Every generated image is classified before use:
**(a) Representational** — depicts the product, its packaging or components, an effect/result, a
person, or an identifiable real place or event.
**(b) Atmospheric** — a stylised/conceptual scene depicting no product, no person, no identifiable
real place.

**AI-2 — Forbidden regardless of classification.**
(i) any depiction of the product other than a faithful representation of the shipped SKU;
(ii) before/after, result, or performance depictions;
(iii) depictions of customers, reviewers, experts, employees or endorsers;
(iv) anything implying testing, certification, laboratory results, awards or independent verification;
(v) any image adding, removing or altering a product feature — filtration media, number of stages,
finish, fittings, dimensions;
(vi) fabricated reviews, quotes, or their visual equivalent.

**AI-3 — Disclosure.** Any **Representational** image used in advertising, and **any photorealistic
synthetic image that would appear authentic**, MUST carry a clear disclosure adjacent to the image at
first exposure, **in the language of the surface it appears on** — Swedish on sv-SE surfaces
(e.g. *"Bilden är AI-genererad."*), with the equivalent in the surface's own language on EN/FR
landers and in localised markets (§14.7). The disclosure must be understandable to the audience
perceiving it, so a hardcoded Swedish string would itself be a compliance defect on a non-Swedish
surface. The EU icon MAY be used alongside. Stylised **Atmospheric** imagery requires no disclosure
**provided** no accompanying copy implies the scene documents a real customer's home, a real
installation, or a product result.

**AI-4 — Provenance.** Provenance metadata (C2PA / watermark / model metadata) MUST NOT be stripped
from an asset file. If a platform rejects an asset because of provenance metadata, escalate — do not
remove it.

**AI-5 — Register.** Per-asset record: asset ID, tool + model, date, prompt/reference, classification
(a)/(b), disclosure applied (Y/N), reviewer, and every URL it was used on.

**AI-6 — Re-verification triggers.** Mandatory re-validation on: any amendment to the Art. 50
Guidelines or the Code of Practice; any new EU icon guidance; any change to Google/Meta policy on
AI creative. *(The 2 Aug 2026 trigger has already passed; the obligation is now continuous.)*

**AI-7 — Stylisation default.** Absent an explicit owner decision otherwise, generated imagery is
**stylised, not photorealistic**. Photorealistic generation requires the classification under AI-1
and the disclosure under AI-3 to be recorded *before* the asset is used.

### GL.5.4 What this replaces in the parent spec

Parent §12.5 ("Product images from Shopify… No generated product images (they would depict
unverified product features)") and §22.6 ("No generated product imagery, fabricated reviews or
quotes…"):

- The **reasoning in §12.5 is correct and survives**: generated imagery must not depict unverified
  product features. AI-2(i)/(v) restate it.
- The **scope was over-broad**: it banned *concept* imagery along with *product* imagery. §22.6
  becomes "No generated **product** imagery; generated concept imagery only per §12.5 as amended."
- **The actual bind was never the ban — it was that nobody had written the compliant form.** It is
  written now, and it turns out to be permissive for stylised work.

### GL.5.5 Feasibility (measured, not assumed)

| Capability | State on box |
|---|---|
| `google-genai` SDK | installed |
| `openai` SDK | installed (v2.41.1) |
| `OPENAI_API_KEY` | **present** |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | **absent** |

`gemini-imagegen` (the skill the parent spec's `nrvision` work assumed) **cannot run** without a
key provision. Image generation via the OpenAI SDK is available today. This is an access item, not a
build item: **pick a provider and provision a key before UNIT 1.22's generation half starts.**
The *guardrail* half (classification, disclosure, register, lint) has no external dependency and can
be built now.

**The classifier is unassigned, and the project's own tooling is documented as unreliable for exactly
this judgement.** AI-1 requires every image to be classified Representational/Atmospheric, and AI-3
turns on whether an image is "photorealistic … would appear authentic". No unit in this document
names the mechanism, model or confidence threshold for that call — and the theme repo's gap register
already documents **G2** ("vision model hallucinates, confidently and repeatedly" — the model asserted
a clipping the DOM disproved) and **G27** ("vision model choice is untested"). Neither is referenced
by the v2.4-draft. The stated acceptance test checks the *gate*, not the *classifier*: a misclassified
unlabelled asset passes it.

**UNIT 1.22 must therefore name the classifier, require a confidence score with human review below
threshold, and cross-reference G2/G27.** Until it does, AI-1/AI-3 is a policy with no measured
enforcement, and "classifier error rate unmeasured" stands as an explicit gap (§GL.11 GL-G14).

### Acceptance
1. An asset classified (a) without disclosure fails a gate. (Test both directions.)
2. A generated image implying a product feature change fails.
3. A generated image implying a result/before-after fails.
4. Provenance survives every pipeline step (byte-level check).
5. The register is complete for every asset in use.

### Rollback
Assets are files. Remove from the surface and the register; no inverse operation needed beyond
re-uploading the previous asset. Because AI-3 attaches disclosure to the *asset*, not the page,
rollback is per-asset.

---

## GL.6 UNIT 1.23 — Display / demand-gen readiness (scope decision)

### The decision, stated plainly

The parent spec's §22.3 parks display and video prospecting until Stage 4 on the reasoning that
there is "no measurable path at this volume." **That reasoning is economically sound and this
document does not overturn it.** At ~9 orders/month with 39 live clicks, a display prospecting
campaign to unaware audiences is unmeasurable by construction.

But Maestro asked for it, and the question deserves a straight answer rather than a deferral:

> Display is not blocked by capability or by policy. It is blocked by **statistics**. There is
> currently no way to tell a good display audience from a bad one, because nothing in the account
> produces enough conversions to compare against.

**Recommendation: keep §22.3, and make the unlock condition explicit and measurable** rather than
"Stage 4". Proposed condition:

```
Display becomes eligible when BOTH hold:
  (a) the store clears >= 30 STORE ORDERS/month for 2 consecutive months, AND
  (b) the conversion-tracking legs from Phase 0/1 are green
      (R1 >= 0.90, R2 >= 0.85) for 14 consecutive days
```

**Two things the earlier draft got wrong and this corrects.**

1. **Orders, not conversions.** §22 item 2 (parent) uses "≥ 30 clean **conversions**/30 d" for its
   Maximize-Clicks hold. That is a different quantity from store orders and the two are not
   interchangeable; this condition is stated in **store orders** deliberately.
2. **14 days, not 30.** Condition (b)'s window is aligned to Phase 1's own exit criterion
   ("R1 ≥ 0.90 and R2 ≥ 0.85 for 14 days"). The draft introduced a 30-day window with no stated
   reason, which would have been a silent divergence from the parent spec's gate.

**Honest note for the owner — the threshold is near the optimistic ceiling.** The cheapest-path
analysis referenced in §GL.4.7 puts the realistic 6–12 month band at **20–30 store orders/month**.
A 30/month threshold therefore sits at the top of that range and may not be met inside a year. That
is a property of the number, not a hidden deferral — if faster display entry is wanted, the threshold
is the thing to change, and it should be changed deliberately rather than discovered later.

Condition (b) is the important one: display prospecting to unaware audiences is the *most*
attribution-hostile surface in the account. Running it while the tracking legs are unproven means
paying for conversions that cannot be seen. The parent spec's own §1.5 already flags that the 0.61
Ads conversions "cannot yet be read either way" — which is exactly the condition under which display
spend is unreadable.

**Retained from §22.3, unchanged:** no UNAWARE targeting before the unlock. The `role` enum stays
without a DISPLAY value until then, so routing cannot address it by accident.

---

## GL.7 Data model deltas

New tables (ADB/control plane), additive, no destructive change:

| Table | Purpose |
|---|---|
| `corpus_principles` | Loaded corpus entries: `principle_id, tier, tier_basis, source_ref, verified, status` |
| `corpus_blocked` | T4 blocklist, with failure citation per entry |
| `research_briefs` | One row per brief; `brief_json`, `awareness_hypothesis`, `awareness_basis`, `confidence`, `gaps_json` |
| `archetypes` | `lander_class, render_through, content_template, template_suffix, allowed_claim_classes, forbidden_claim_classes, require_sourced_arithmetic, required_sections, awareness_fit, surface_stage` (per GL-R2 / GL-R2b) |
| `image_assets` | `asset_id, tool, model, generated_at, classification, classifier_model, classifier_confidence, review_required, disclosure_applied, disclosure_language, provenance_present, sha256, urls_json, surface_stage` |
| `claim_surface_violations` | Gate failures: `page_id, archetype, claim_class, line_ref, detected_at` |
| `surface_stages` | `surface_class` (`ARCHETYPE`/`IMAGERY`/`DISPLAY`), `surface_id`, `stage`, `evidence_ref`, `promoted_at` — required by GL-R2b so every surface GL-R2 governs has somewhere to persist its stage |

Extended:
- `ent_creative`: `principle_ids_json`, `tier_max_used`, `blocked_mechanism_hits` (must be 0)
- `ent_lander`: `lander_class` widened per §GL.4.4; `archetype` FK to `archetypes`
- `creative_attributes`: `principle_id` becomes a taggable attribute so the pattern library (§12.10)
  can pool posteriors **by principle** — this is what makes the corpus self-correcting rather than
  decorative

That last line is the important one. Without it the corpus is a static asset that decays
(persuasion knowledge means repeated tactics are detected and resisted). With it, the corpus's
tiers become **testable in this account** — the pattern library will eventually say whether a given
T2 principle actually earns its tier here.

---

## GL.8 Build order & dependencies

```
                    ┌─────────────────────────────────────────────┐
                    │ OWNER-GATED (theme_guard §R3 path)          │
                    │                                             │
                    │  Publish nr-* library (27 files)            │
                    │   └─> unlocks 3 archetypes, no per-page cost│
                    └────────────────────┬────────────────────────┘
                                         │
UNIT 1.19 corpus ──> UNIT 1.20 briefs ───┼───> UNIT 1.21 archetypes ──> §13 routing
      (no deps)         (needs 1.19)     │        (needs publish)
                                         │
UNIT 1.22 guardrails ────────────────────┘   (no deps — build now, in force now)
      │
      └─> generation half waits on provider key

UNIT 1.23 = scope decision only (no build before unlock)
```

**Sequence:**

1. **UNIT 1.22 guardrails** — highest urgency, zero dependencies, addresses law that has applied since
   2 August 2026 (53 days at time of writing). Do first.
2. **UNIT 1.19 corpus** — no dependencies, unblocks 1.20 and §12 generation. Can run in parallel.
3. **UNIT 1.21 archetypes (content path)** — no theme dependency. Requires the `claim_class` column
   (§GL.4.5) and the G17/G18 checks to exist. **This is the generator, and it is not blocked by any
   theme work.**
4. **UNIT 1.20 briefs** — after 1.19.
5. **UNIT 1.22 generation** — after a provider key exists and a classifier is named.
6. **Optional: publish the `nr-*` library** — owner-gated; buys two fixed showcase pages and a design
   reference, **not** a page factory (§GL.4.2). Its preconditions are the theme guard's, not this
   document's:

   > **Before any theme work: run `theme_guard.py check` and `assert-live-untouchable` (R4).**
   > Snapshot the live theme first (`theme_guard.py snapshot <id>`, R3). Land the change on a
   > **duplicate unpublished** theme only — `allowed_test_theme_roles: ["unpublished"]` in the guard
   > config means the change must land on a duplicate regardless of anything said here. Browser-test
   > the exact HTML on the duplicate (R2b — Shopify validates Liquid syntax, not JS behaviour). Run
   > the 17 `theme_guard_tests.py` checks (R5). Measure Lighthouse on the duplicate against a
   > pre-change baseline (R7). Only then, with Maestro's written approval, take the live step.
   > If duplicate creation fails, **stop** — never fall back to editing live.
   >
   > *(This paragraph is stated in full because this is the only place in either document that
   > recommends touching a theme, and the project has two prior live-theme incidents — the 2026-08-22
   > 404 and the 2026-09-05 untested-inline-JS breakage. A recommendation to publish should carry its
   > own gates rather than assume the reader will find them.)*

7. **UNIT 1.23** — no build until its unlock condition is met.

**Note on the parent spec's Phase 2:** this document's §GL.7 tables are entity-model work. They
should be authored **with** Phase 2 (UNIT 2.2 entity model), not after it, because `principle_id` as
a creative attribute is a schema decision that is cheap now and a migration later.

---

## GL.9 Evidence & provenance register

Per §GL.1.3. Every normative clause is labelled with its grounding.

### Grounded in retrieved external sources (verified 2026-09-24)

*(Split from the original single table: three of its rows were labeled "Direct measurement on box"
but sat under a heading claiming retrieved sources. Nothing was hidden — each row disclosed its own
basis — but the heading was inaccurate.)*

| Clause | Basis | Source type |
|---|---|---|
| Art. 50 applicability = 2 Aug 2026, obligations **apply from** that date | Retrieved; multiple independent legal sources agree. *(The AI Act entered into force 1 Aug 2024 with staged application; "applies from 2 Aug 2026" is the precise form. "53 days" is correct for that date.)* | Primary (Commission FAQ) + secondary (law-firm memos) |
| Digital Omnibus did **not** move Art. 50 for deployers | Retrieved; Council approval 29 June 2026; the deferral applies to Annex III high-risk (2 Dec 2027 / 2 Aug 2028). **One retrieved source indicates a deferral limited to the Art. 50(2) *marking* obligation for systems that are both interactive and generative** — read as "None" in the draft; now flagged as an open question (Appendix A, V13) | Secondary (Council press release as reported) + secondary (law firm) |
| Commission Guidelines final, 20 July 2026 | Retrieved | Multiple independent sources agree |
| Code of Practice + three EU icons; use optional, labelling not | Retrieved; Commission digital-strategy pages | Primary (European Commission) |
| Realistic invented person still a deepfake | Retrieved; Guidelines analysis | Secondary (legal analysis) |
| **Art. 50(4) binds the deployer** (the brand), not the image tool | Retrieved | Secondary (legal analysis) |
| **Deployers cannot rely on the provider's Art. 50(2) machine-readable marking alone** | Retrieved; Commission FAQ | Primary (European Commission) |
| Fantastical/impossible content outside definition | Retrieved; Guidelines summary | Secondary |
| Ordinary commercial use may be in scope | Retrieved; Commission clarification as reported | Secondary |
| Disclosure at first exposure, not via metadata; display = label on creative | Retrieved | Primary (Commission FAQ) + secondary |
| No retroactive labelling for pre-2 Aug 2026 content | Retrieved | Primary (Commission FAQ) |

### Grounded in direct measurement on this box (2026-09-24)

*(Split out from the table above — see note there. These are Primary evidence of *this machine's state*,
not of the external world.)*

| Clause | Method |
|---|---|
| `nrtheme status` reports **27** repo-only files (header count); its printed listing shows **15** | **Direct measurement.** The tool prints the count 27 in its header but lists only 15 entries, truncated alphabetically after `sections/nr-study.liquid`. The decomposition 6 fonts + 12 sections + 7 snippets + 2 templates = 27 is an **inference** from the directory listing plus the header count — it reconciles exactly, but it is not a printed list, and the draft presented it as observation. Re-run with a full-listing flag to confirm |
| `nr-*` section/snippet/template inventory (12 / 7 / 4) | **Direct inspection of repo** |
| `page.json`, `page.contact.json`, `page.water-report.json`, `page.science.json` render `{{ closest.page.content }}` | **Direct inspection** — the expression is a `text` block *setting* in the template JSON and/or `blocks/page-content.liquid`, which is why a `grep` of `sections/` alone returns nothing |
| No `nr-*` section renders `page.content` or reads metafields (0 matches each) | **Direct measurement** (`grep`) |
| `page.nr-8-reasons.json` hardcodes copy and 5 links to `/products/nordisk-welcome-kit` | **Direct inspection** (JSON parse + link grep) |
| G2/G17/G18/G21/G25/G26/G27 status | **Read from theme repo gap register** |
| `OPENAI_API_KEY` present; `GEMINI_API_KEY`/`GOOGLE_API_KEY` absent; both SDKs installed | **Direct measurement** (env probe) |
| Theme guard live id / protected roles / `allowed_test_theme_roles` | **Read from guard config** |

### `UNVERIFIED` — design assertions, obligations attached

| Clause | Status | Obligation |
|---|---|---|
| Evidence tiers T1–T4 and the specific tier assigned to any named framework | **UNVERIFIED** — the research pass that produced the tier draft had no web access | Each tier assignment must be verified against the primary text before load. Per §GL.2.1, unverified entries load as **T3 regardless of claimed tier** — the schema is safe by construction |
| The T4 blocklist entries and their citations | **UNVERIFIED** (bibliographic) | Verify each replication failure against its cited source before the entry may block output. Per **GL-R3**, an unverified entry may only `WARN`, never `BLOCK` — so an unverified blocklist cannot silently kill a legitimate technique |
| The specific modern-literature findings in §GL.2.4/§GL.2.5 (half of ads no lift; elasticity ~0.1; hierarchy-of-effects critique) | **UNVERIFIED** (bibliographic) | Verify before these are used as decision inputs. They inform a *humility clause*, so the cost of being wrong is low, but they must not be presented to the owner as measured fact until verified |
| Cognitive/behavioural mechanism claims attributed to any principle | **UNVERIFIED** | Must be verified before entering generated rationale. This is the highest-risk category, because it is the one that would appear in customer-facing copy |

### Could not establish
- Whether any Swedish RO/RON opinion or KO/PMD case has addressed AI-generated ad imagery
- The current consolidated section numbering of marknadsföringslagen (2008:486) and the current
  statutory cap on `marknadsstörningsavgift`
- Whether Sweden has designated its AI Act market-surveillance authority
- Whether any enforcement action exists specifically on AI-generated ad imagery in the EU/Nordics
- The exact third EU icon's label
- Whether the `Nordisk Wellness Kit` zero-inventory condition (G21) is real and live
- **Whether any part of Art. 50(2) marking was deferred for systems that are both interactive and
  generative** — one retrieved source indicates a deferral limited to the marking obligation. This
  matters because AI-4 (provenance non-stripping) is entangled with the provider/deployer split
  (Appendix A, item V13)
- **Which vision model may classify an image Representational vs Atmospheric with acceptable error**
  — required by AI-1/AI-3 and currently unassigned (§GL.5.5, GL-G14). The theme repo's own G2/G27
  record that the available vision model hallucinates confidently and has never been benchmarked

### Honest note on the research process

Both research subagents dispatched for this document **lacked web access** and returned
knowledge-only briefs that self-flagged as unverified. Their content was **not** used to write any
normative clause. The Art. 50 findings above were retrieved directly, after that failure was
detected. This is recorded because a brief that *looks* like research but was not retrieved is more
dangerous than no brief — it is the §0.2 failure mode one level up.

---

## GL.10 Open questions for the owner

| # | Question | Default applied (work not blocked) | What changes if answered differently |
|---|---|---|---|
| 1 | Is the `Nordisk Wellness Kit` zero-inventory condition real? (theme-repo G21) | Nothing generates until answered — 1.21 gated | If real, the highest-value routing target in the account is unfulfillable. Blocks paid routing to Wellness-Kit landers |
| 2 | Publish the `nr-*` library now, under the §R3 gated path? | Not published; 1.21 blocked | Publishing unlocks three archetypes at one approval cost |
| 3 | Which image provider? (`GEMINI_API_KEY` absent; OpenAI key present) | OpenAI SDK is the available path | Determines §12.5 tooling and whether `nrvision`-style review keeps working |
| 4 | Brand/activation policy (§GL.2.6) | Option 1, activation-only, labelled as such in the digest | Determines what the corpus is *for*, and whether upper-funnel work is ever funded |
| 5 | Display unlock condition (§GL.6) | §22.3 retained, condition made explicit | Confirms or moves the display timeline |
| 6 | Build the one genuinely-missing archetype (`ADVERTORIAL`)? | Not built; treated as follow-on under the same gate | Adds a fourth archetype at the cost of a second gated theme change |
| 7 | Does the corpus want *citation* (generator names its principle + tier in the rationale) or *silent injection*? | **Citation with tier**, output-linted, never surfaced to the end reader | Silent injection is less auditable; citation invites rhetoric dressed as evidence in the digest |

---

## GL.11 Gaps named in this document

Recorded in the manner of the theme repo's gap register: each is a known hole with evidence, not a
wishlist item.

| # | Gap | Status | Evidence |
|---|---|---|---|
| GL-G1 | The corpus carries **no local validation** that any principle works in this account, this category or these channels | **OPEN** | All tiers are imported from literature, not measured here. Mitigation is §GL.7's `principle_id` attribute, which makes tiers testable over time |
| GL-G2 | `ADVERTORIAL` archetype does not exist | **OPEN** | Confirmed absent from the template set |
| GL-G3 | Commerce behaviour untested (no proven end-to-end purchase) | **OPEN** | Theme-repo G18. Blocks autonomous generation |
| GL-G4 | Interactive components untested (accordion/tabs/carousel behaviour) | **OPEN** | Theme-repo G17 |
| GL-G5 | No pixel-diff visual regression | **OPEN** | Theme-repo G19. A generated page can drift visually with no signal |
| GL-G6 | Anonymous theme preview disabled → every check needs an authenticated dev session | **PARTIAL** | Theme-repo G14. Constrains unattended verification |
| GL-G7 | Section-coverage check not automated | **OPEN** | Theme-repo G23/G1. The only defect class that produced *no signal at all* — a section vanished and nothing complained |
| GL-G8 | The `nr-*` library is unproven in production | **UNVALIDATED** | Theme-repo G26: never published, so no PSI, no conversion data |
| GL-G9 | Only 1 of 8 unique GemPages designs is rebuilt | **OPEN** | Theme-repo G25 |
| GL-G10 | No verified legal position on Swedish marketing law's treatment of synthetic imagery | **OPEN** | Could not establish; marknadsföringslagen contains no AI-specific rule to my retrieval, but this was not positively confirmed against the consolidated text |
| GL-G11 | Corpus provenance is bibliographic, not verified against primary texts | **OPEN** | §GL.9. Schema compensates (unverified → T3) but entries are weaker than they look |
| GL-G12 | No licensing/quoting policy for copyright-encumbered sources | **OPEN** | Several core texts are under active copyright enforcement. Corpus must **paraphrase + cite**, never embed passages |
| GL-G13 | persuasion-knowledge decay is unmodelled | **OPEN** | Audiences detect and resist repeated tactics. The corpus is a **decaying** asset and needs a re-validation schedule, not a one-time build |
| GL-G14 | **The AI-1 image classifier is unassigned and its error rate is unmeasured** | **OPEN** | §GL.5.5. The theme repo's G2 documents a vision model hallucinating confidently; G27 records that model choice was never benchmarked. The current acceptance test validates the *gate*, not the *classifier*, so a misclassified unlabelled asset passes. AI-1/AI-3 is a policy with no measured enforcement until this is fixed |
| GL-G15 | **The `nr-*` templates are fixed, fully-authored pages — they cannot generate variants** | **OPEN** | Verified: zero `nr-*` sections render `page.content`, zero read metafields; `page.nr-8-reasons.json` hardcodes its entire copy and five product links. Instantiating the same template twice yields a byte-identical clone. Making them a generator substrate requires a metafield/settings refactor that is **not in this document**. An earlier draft of §GL.4 claimed the opposite ("one approval per template class, not one per page"); that claim was false and has been removed |
| GL-G16 | **`page.science` and `page.water-report` are GemPages-derived and cannot be created or edited by adsys** | **OPEN** | Parent §12.6 states this explicitly. They are rendering shells and design references only. `page.water-report` is additionally a one-section minimal shell, not a designed report. An earlier draft counted them as "built archetypes"; corrected in §GL.4.1 |
| GL-G17 | **Content-path styling ceiling is unmeasured** | **OPEN** | The content path (mechanism A) writes `body_html` rendered by the theme's RTE wrapper. How much of the `nr-*` design language survives in that path — section rhythm, layout, the guarantee/CTA treatment — has never been measured, because no content-path page has been built. The archetype claim "imitates the `nr-*` reference implementation" is therefore an intention, not a verified capability |

---

## GL.12 Summary of amendments to the parent spec

| Parent section | Amendment |
|---|---|
| §1.6 / §1.5 / §3 | **Unchanged.** This document makes no economic claim and resolves no contradiction |
| §12.1 | Add research brief + corpus principles as inputs |
| §12.4 | Extend: (a) T4 mechanism lint on output, gated by GL-R3 (only a verified entry may BLOCK); (b) AI disclosure requirement in copy context, language-parametric; (c) archetype claim-surface enforcement, backed by a new `claim_class` column on `product_claims` |
| §12.5 | **Rewritten** — replace blanket ban with AI-1…AI-7; stylised-by-default on the "appears authentic" prong; language-parametric disclosure; measured feasibility; classifier named as a UNIT 1.22 obligation |
| §12.6 | Add archetype layer; the autonomous path is the **content path** (body_html through a `{{ page.content }}` template, no theme write) and does **not** depend on publishing `nr-*` |
| §12.11 | Add: cascade step 7 (organic brief) now consumes a research brief; cascade step 3 (lander rebuild) selects an **archetype**, not a page |
| §13.1 | `lander_class` gains `LISTICLE`, `AUTHORITY`, `REPORT`, `ADVERTORIAL` |
| §13.2 | Add §13.2.1 archetype ↔ awareness-stage fit, with claim surfaces **and the two-mechanism distinction (content-driven generator vs section-driven hand-built designs)** |
| §21 | Add Phase 1c (UNIT 1.19–1.23) with the dependency chain of §GL.8 |
| §22.3 | Retained, with an explicit measurable unlock condition replacing "Stage 4" |
| §22.6 | Narrowed: bans generated **product** imagery; generated **concept** imagery governed by §12.5 |
| §22 | **Renumbered 7–15** (the three additions were inserted as 7/8/9 and collided with the original 7/8/9; originals shifted to 10–15). Additions: no T4 persuasion mechanism in any output; no undisclosed Representational synthetic imagery; no archetype generated with an undeclared claim surface |
| §23 | Add the **eight** open questions **Q11–Q18** (seven from §GL.10 plus Q18, promoted from the "could not establish" list) |
| §24 | Reference this document as Appendix |

---

## Appendix A — Verification checklist (for a session with web access)

Carry forward and complete before any `UNVERIFIED` entry is promoted above T3:

| # | Check |
|---|---|
| V1 | Each named framework's tier: verify against the primary text (edition/page), not a secondary explainer |
| V2 | Each T4 blocklist entry's replication failure: verify the cited study exists and says what is claimed |
| V3 | §GL.2.4/§GL.2.5 modern-literature figures (half of ads no lift; ~0.1 elasticity) |
| V4 | marknadsföringslagen (2008:486) consolidated text — confirm absence of any AI/synthetic-imagery provision; confirm section numbering and the `marknadsstörningsavgift` cap |
| V5 | Reklamombudsmannen opinion database — any AI/manipulated-imagery opinion |
| V6 | Konsumentverket — any AI-imagery guidance; KO decisions and PMD judgments on misleading visuals |
| V7 | Sweden's designated AI Act market-surveillance authority |
| V8 | The third EU icon's label; current icon implementation guidance |
| V9 | Any post-20-July-2026 amendment to the Art. 50 Guidelines or the Code of Practice |
| V10 | Google Ads / Meta current policy on AI-generated creative |
| V11 | Enforcement scan: any EU/Nordic action on AI-generated ad imagery |
| V12 | Directive (EU) 2024/825 (green-transition claims), applicability 27 Sept 2026 — relevant if generated imagery implies natural/clean/eco |
| V13 | **Whether any part of Art. 50(2) marking was deferred for systems that are both interactive and generative** — one retrieved source raises this; §GL.5.1's "None" reading should be confirmed against the Digital Omnibus final text |
| V14 | Confirm the deployed AI Act market-surveillance authority in Sweden and whether a complementary national act is in force |

---

## Appendix B — What reconnaissance established, for the record

Commands run (all read-only) and their results, so this is reproducible:

| Command | Result |
|---|---|
| `nrtheme status` | live `195492381006` vs repo: **0 only-in-Shopify, 27 only-in-repo**, incl. all 12 `nr-*` sections + 6 Barlow font files |
| `ls theme/sections/nr-*.liquid` | 12 sections |
| `ls theme/snippets/nr-*` | 7 snippets |
| `json.load(templates/page.nr-8-reasons.json)['order']` | 19 sections, 17 native `nr-*` |
| `json.load(templates/page.nr-4-reasons.json)['order']` | 13 sections, 11 native `nr-*` |
| `git -C theme-repo log --oneline` | `e9f265a nr-kit…`, `2497f6a nr-8-reasons…`, `92e0d6b Hero media…` |
| `cat theme-repo/docs/PAGE-REBUILD-GAPS.md` | G2/G17/G18/G21/G25/G26/G27 status |
| `grep -rl "page.content" theme/` | **8 files** — including `templates/page.json`, `page.contact.json`, `page.water-report.json`, `page.science.json` and `blocks/page-content.liquid`. The expression lives as a `text` block **setting** (`"text": "{{ closest.page.content }}"`), not as a section render — which is why grepping `sections/` alone returns nothing and why the mechanism was missed on the first pass |
| `grep -rl "page.content" theme/sections/` | **0 matches** |
| `grep -l "metafields" theme/sections/nr-*.liquid` | **0 matches** — the `nr-*` sections are not parameterised |
| `json.load(templates/page.nr-8-reasons.json)` | Copy hardcoded; 5 links to `/products/nordisk-welcome-kit` |
| `json.load(templates/page.science.json / page.water-report.json)` | Section types are GemPages classes (`hero`, `main-page`, `product-list`, `divider`), **zero** native `nr-*` |
| `cat /root/.nordisk/guard/theme_guard_config.json` | live id, `protected_roles:["main"]`, `allowed_test_theme_roles:["unpublished"]`, `allowed_image_classes:["product-cta-img","pick-img"]` |
| env probe | `OPENAI_API_KEY` SET; `GEMINI_API_KEY`/`GOOGLE_API_KEY` ABSENT; `google-genai` + `openai` SDKs installed |
| `date -u` | 2026-09-24 — Art. 50 in force 53 days |

**No write was performed against any Shopify theme, and no theme-guard gate was invoked, because no
theme work was undertaken.** The `nr-*` publish recommended in §GL.4.3 is deliberately left to the
owner-gated §R3 path.

---

*End of extension. Parent spec amended to v2.4 per §GL.12.*
