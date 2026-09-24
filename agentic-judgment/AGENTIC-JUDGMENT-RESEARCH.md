# Judgment and Decisions in Autonomous Agentic Systems — What Already Exists

Research report for Maestro · engrane.xyz · 2026-09-25
Scope: what the world has already built, measured, and broken in "gate an autonomous agent's proposed decision before it ships."

---

## 1. What you were actually asking

Strip the mechanics away and there are two questions in your design, not one:

**Q1 (plumbing):** how do I stop an autonomous agent from making a bad or unnecessary change — a pyramid of judges (A: is it necessary, with context gathered; B: context-free protocol check on A; C: adversarial decider with full transcript), then a scout that gathers files and writes a plan, then a worker that only executes.

**Q2 (the real one):** *does this move the project toward its goal?* For engrane.xyz: best learning experience first, paywall eventually, and the product is the moat.

The research says plainly: **Q1 is essentially solved prior art, and the world's best implementations look almost nothing like your pyramid. Q2 is not solved by any gate architecture at all, and the people who get closest do it with a small, repetitive, mechanical check — not with judges.**

Two headline numbers to hold onto:

- **Nine judges, two effective votes.** Apple tested a panel of 9 frontier LLMs from 7 model families on 3 NLI datasets with 100 human annotations per item. The 9 judges provided **about 2 independent votes' worth of information**. ~75% of nominal independence was lost because the models make the same mistakes on the same items. The panel's accuracy fell **8–22 percentage points** below what independent voting would give, and **the best single judge matched or beat the full panel** in every condition. Adding more judges didn't help; smarter aggregation closed at most **11%** of the gap. Conclusion in their words: *"The bottleneck is correlated judges, not the aggregation algorithm, implying that scaling up panels cannot substitute for genuinely independent evaluation."* ([Apple ML Research, June 2026](https://machinelearning.apple.com/research/correlated-llm-evaluation-panels), [arXiv 2605.29800](https://www.alphaxiv.org/abs/2605.29800))
- **98% more PRs, zero DORA improvement.** Faros AI, across 10,000+ developers and 1,255 teams: high AI adoption → 21% more tasks completed, **98% more pull requests merged**, but **no significant correlation with company-level DORA metrics**. Review time per PR went **up 91%** and average PR size went **up 154%**. Net effect at org level: near zero. ([AgentMarketCap summary of Faros AI data, Apr 2026](https://agentmarketcap.ai/blog/2026/04/10/faros-ai-dora-metrics-coding-agents-2026))

The second number is your whole design's reason to exist, and the first number is why your pyramid, as specified, probably won't deliver it.

---

## 2. What already exists

Organised by problem, not by vendor.

### 2a. Multi-judge / panel evaluation
| Thing | What it is | Maturity |
|---|---|---|
| **PoLL — Panel of LLM Evaluators** ([arXiv 2404.18796](https://arxiv.org/abs/2404.18796), Cohere) | Panel of smaller models beats one large judge, less intra-model bias, >7× cheaper | Proven for eval. Key mechanism: **disjoint model families**, not judge count |
| **Apple correlated-error study** ([link](https://machinelearning.apple.com/research/correlated-llm-evaluation-panels)) | Panels are worth ~1/4 of their nominal size | Proven, June 2026 — and it caps this whole approach |
| **Self-preference bias** ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819), SB Intuitions) | GPT-4 significantly favours its own outputs; root cause is **perplexity/familiarity**, not identity | Proven and measured |
| **Position bias** ([IJCNLP 2025](https://aclanthology.org/2025.ijcnlp-long.18.pdf)) | Verdict changes with ordering of presented options | Proven, with mitigations |
| **Multi-agent debate** ([arXiv 2305.14325](https://arxiv.org/abs/2305.14325), Du et al.) | Debate improves factuality/reasoning accuracy | Proven in eval settings; expensive; not a coding gate |
| **Eugene Yan's evaluator guide** ([eugeneyan.com](https://eugeneyan.com/writing/llm-evaluators)) | Best practitioner synthesis of when LLM judges are worth it | Practitioner gold |
| **orq.ai "Weak judges, strong panel"** ([link](https://orq.ai/blog/llm-juries-in-practice)) | Ensemble in practice, with the cost/benefit caveats | Practitioner |

### 2b. The deterministic-vs-judgment boundary
This is the most important prior art and it is nearly your design.

**InfoQ — "Agentic Fitness Functions: Extending Evolutionary Architecture Beyond Deterministic Rules"** ([link](https://www.infoq.com/articles/agentic-fitness-functions-evolutionary-architecture)). Their key takeaways, verbatim from the article:
- *"Deterministic fitness functions should remain the **primary enforcement mechanism** for measurable invariants such as dependency direction, contract shape, latency budgets, security posture, and policy checks."*
- *"Agentic fitness functions add value when architectural risk is **evidence-bound but judgement-heavy**, such as boundary fidelity, semantic contract drift, workflow coupling, and stale ADR assumptions."*
- A production-ready implementation *"separates deterministic gates from agentic advisory signals, scopes evidence to the change, **applies versioned rubrics, returns structured verdicts**, and escalates low-confidence or high-blast-radius outcomes to humans."*
- And the payoff: *"convert into deterministic guardrails when patterns repeat."*

Also: **TLA+ / formal methods at AWS** ([Lamport, AWS paper](https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf)) — machine-checkable specs caught real bugs in S3/DynamoDB designs that testing would not. **Property-based testing** now has an empirical evaluation of its real effect ([ACM OOPSLA'25](https://dl.acm.org/doi/10.1145/3764068)). **Structured output / constrained decoding** ([arXiv 2501.10868](https://arxiv.org/html/2501.10868v1)) eliminates whole classes of agent output error mechanically.

### 2c. Durable execution + approval primitives
- **Temporal** ships human-in-the-loop as a first-class pattern ([docs](https://docs.temporal.io/ai/cookbook/human-in-the-loop-python), [tutorial](https://learn.temporal.io/tutorials/ai/building-durable-ai-applications/human-in-the-loop)). Durable = the approval survives a crash; no gate design is real without this.
- **LangGraph** interrupt + checkpointer ([community pattern](https://vanducng.dev/2025/06/26/Agentic-RAG-and-Human-in-the-Loop-with-LangGraph), [HITL dashboard](https://forum.langchain.com/t/human-in-the-loop-approval-dashboard-for-langgraph-agents-open-source-free-to-deploy/3616/3)).
- **Guardrails layer**: NeMo Guardrails, Guardrails AI, Pydantic AI output validators — all deterministic-shape enforcement around model output.

### 2d. Plan-then-execute (your scout/worker split)
- **GitHub spec-kit** ([repo](https://github.com/github/spec-kit), [docs](https://github.github.com/spec-kit)) — spec as source of truth, and a whole toolchain around it.
- **AWS Kiro** ([re:Invent 2025 session](https://dev.to/aws/dev-track-spotlight-spec-driven-development-with-kiro-dev314-45e8), [case study](https://aws.amazon.com/blogs/industries/from-spec-to-production-a-three-week-drug-discovery-agent-using-kiro)) — spec-driven IDE. Note AWS **end-of-supported Amazon Q Developer** ([announcement](https://aws.amazon.com/blogs/devops/amazon-q-developer-end-of-support-announcement)) — this space is churning fast.
- **SDD Observatory** ([sddobservatory.com](https://sddobservatory.com/)) — a project literally tracking spec-driven development "in the wild." Read it before designing your own.
- Practitioner pulse, Sept 2026: **Ask HN "Are you leveraging Spec-Driven / Spec-Anchorated development?"** ([HN 49618556](https://news.ycombinator.com/item?id=49618556)) — 9 points, live discussion. New subreddit **r/SpecDrivenDevelopment** exists. The dominant complaint in these threads is not "specs help" — it is that agents **randomly rewrite 14 files across 5 directories** once the spec is even slightly ambiguous ([r/ClaudeCode, Sep 2026](https://www.reddit.com/r/ClaudeCode/comments/1wpblkg/stop_vibe_coding_blindly_the_secret_weapon_to/)).

### 2e. Multi-agent orchestration — the live fight
- **Cognition, "Don't Build Multi-Agents"** ([link](https://cognition.ai/blog/dont-build-multi-agents)). Two principles: **(1) share context and full agent traces, not individual messages.** **(2) actions carry implicit decisions, and conflicting decisions carry bad results.** Their verdict: rule out by default any architecture that doesn't obey both.
- **Anthropic, "How we built our multi-agent research system"** ([link](https://www.anthropic.com/engineering/multi-agent-research-system)). Opus lead + Sonnet subagents beat single-agent Opus by **90.2%** on their internal research eval. But: token usage alone explains **80%** of performance variance on BrowseComp; multi-agent burns **~15×** the tokens of chat (single agent ~4×). And critically: *"some domains that require all agents to share the same context or involve many dependencies between agents are **not a good fit**... most coding tasks involve fewer truly parallelizable tasks than research, and **LLM agents are not yet great at coordinating and delegating to other agents in real time**."*

**These two are not in contradiction — they are describing different task shapes.** Breadth-first, parallel, context-exceeding research: multi-agent wins. Coupled, dependency-dense, shared-state work: single-threaded wins. **Your system is in the second category.** Cognition's principles govern you, not Anthropic's.

### 2f. Goal alignment, drift, and moats
- **Goal misgeneralization** ([Langosco et al., ICML 2022](https://proceedings.mlr.press/v162/langosco22a.html), [arXiv 2105.14111](https://www.alphaxiv.org/abs/2105.14111v7)) — agents keep the capability and lose the goal. Proven in RL.
- **Specification gaming** ([Krakovna's list](https://vkrakovna.wordpress.com/2018/04/02/specification-gaming-examples-in-ai), [DeepMind](https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity)) and **reward hacking** ([survey, arXiv 2604.13602](https://arxiv.org/html/2604.13602v1), [Lil'Log](https://lilianweng.github.io/posts/2024-11-28-reward-hacking)) — the canonical failure is *optimising the measure you asked for and drifting from the thing you wanted*. OpenAI's own **"Measuring Goodhart's Law"** ([link](https://openai.com/index/measuring-goodharts-law)) is the practical version.
- **Architecture drift by accumulation.** The InfoQ article states the mechanism better than I did: *"**They are the normal way architecture decays: through individually reasonable changes that pass every written rule while slowly moving the implementation away from the intent the team believed it had protected.**"* That is your goal-drift problem, described by someone else, about a different domain, with a working mitigation (continuous fitness functions).
- **Fitness functions / evolutionary architecture** ([continuous-architecture.org](https://continuous-architecture.org/practices/fitness-functions), [Thoughtworks](https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development), [AWS](https://aws.amazon.com/blogs/architecture/using-cloud-fitness-functions-to-drive-evolutionary-architecture)) — the established discipline for turning intent into continuous automated feedback instead of periodic review.
- **Moats**: **7 Powers / counter-positioning** ([Helmer summary](https://www.hustlebadger.com/what-do-product-teams-do/7-powers-establishing-your-competitive-moat), [Commoncog with 18 case studies](https://commoncog.com/c/concepts/counter-positioning)). What is *not* in the literature: an operationalised rubric for "does this deepen the moat?" as a review question. **Nobody has published that.** It's yours to build.
- **Kill criteria / pre-mortems** ([SaaSdash on pre-committing kill criteria](https://saasdash.ai/blog/kill-criteria-product-bets-saas)) — the closest thing to a decision-gate-with-a-falsifier that exists in product practice.

### 2g. What actually acts as a gate in practice
- **Human code review**: unreviewed commits have **over 2× the chance of introducing bugs** than reviewed ones (Bavota & Russo 2015, cited in the [MCR survey](https://arxiv.org/html/2405.18216v1)). But Bacchelli & Bird (ICSE 2013) found a **systematic mismatch**: defect-finding is developers' *top stated expectation* of review, and actual review performance does not meet it — the reliable measured benefit is knowledge transfer and shared understanding ([TUDelft record](https://research.tudelft.nl/en/publications/expectations-outcomes-and-challenges-of-modern-code-review), [Microsoft tech report](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/05/MS-Code-Review-Tech-Report-MSR-TR-2016-27.pdf)). **That is the exact trap your judges are walking into.**
- **AI code review as a product**: CodeRabbit claims top of the Martian code-review benchmark ([vendor blog](https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark)); **Anthropic launched a dedicated Code Review tool in 2026 explicitly to handle "the flood of AI-generated code"** ([AI Expert Magazine](https://www.aiexpertmagazine.com/anthropic-ai-code-review-tool-bug-ai-generated-code), [CryptoRank](https://cryptorank.io/news/feed/2d404-anthropic-code-review-ai-generated-code)). The bottleneck is real enough that labs are shipping products for it.
- **DORA 2025** ([The Register summary of the 440-page report](https://theregister.com/software/2025/09/24/dora-report-reframes-ai-as-central-to-software-development/1122275/)): ~90% use AI; 80% believe productivity improved; but **30% don't trust AI-generated code**, **AI increases delivery instability**, and AI acts as an **amplifier** — it strengthens high performers and worsens dysfunctional orgs. 61% never use agent mode. DORA also added **rework rate as a 5th metric** ([Faros](https://www.faros.ai/blog/5th-dora-metric-rework-rate-track-it-now)). Its AI Capabilities Model lists **small batches of work** as a top practice.
- **Post-hoc gates that measurably work**: canary analysis with automated rollback ([Argo Rollouts](https://blog.px.dev/argo-rollouts), [Octopus](https://octopus.com/blog/recover-automatically-from-failed-deployments)), blue-green, feature flags, kill switches.
- **Failure rates**: Fiddler estimates **70–95% of AI agent projects fail in production** ([link](https://www.fiddler.ai/blog/ai-agent-failure-rate)) — treat as a directional vendor claim, not a measurement.
- **Alert/approval fatigue is a measured phenomenon** in the best-studied domain available: healthcare ([AHRQ PSNet primer](https://psnet.ahrq.gov/primer/alert-fatigue)) and SRE ([Rootly](https://rootly.com/alert-management/alert-fatigue)). Gates that fire too often stop being gates.
- **Decision records**: ADRs ([adr.github.io](https://adr.github.io), [Microsoft](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record), [AWS](https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making)), Google design docs ([industrialempathy](https://www.industrialempathy.com/posts/design-docs-at-google)), RFC processes ([Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs)). The honest counterpoint: **"Has Your Architectural Decision Record Lost Its Purpose?"** ([InfoQ](https://www.infoq.com/articles/architectural-decision-record-purpose)) — the ritualisation failure mode, documented.
- **Eval gates in CI**: statistically careful gating exists ([statgate](https://github.com/yashchimata/statgate) — paired bootstrap verdicts, power analysis, sequential early stopping; [Agent Native eval-gate checklist](https://www.agentnative.dev/checklists/llm-evals-in-ci-checklist); [Max Petrusenko](https://www.maxpetrusenko.com/blog/ci-cd-eval-gates-for-llm-apps)).

---

## 3. What the evidence says about your pyramid, judge by judge

### Judge A (gathers context, binary necessity verdict)

**Supported:** nothing here is novel, and the *instinct* — gather evidence before judging — is what every real system does.

**Broken by evidence:**
1. **Binary forces a false collapse.** "Necessary" actually contains three questions: *is the problem real* (validity), *is this the right fix* (appropriateness), *is it worth doing now* (priority). Every real system in production returns a **structured verdict with score, confidence, rationale and escalation guidance** ([InfoQ](https://www.infoq.com/articles/agentic-fitness-functions-evolutionary-architecture)). Forcing binary means A answers one of the three and the others leak downstream unexamined.
2. **Context-gathering by A defeats your own cost ordering** and pre-commits the scouter's selection bias. Production systems **scope evidence to the change** (same source) precisely because open-ended context gathering by a judge is unbounded and unreproducible.
3. **Self-preference bias is measured** ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819)): an LLM judge systematically favours text that is *familiar to it*. If A is the same or a related model as the proposer, A is not neutral — it's reading prose it already likes.

### Judge B (no context, protocol-only, authenticates A)

**Supported, and this is the best idea in your design.** Context-free structural validation is real, cheap, and it's exactly what the industry calls a **deterministic fitness function**. Versioned rubrics + structured verdicts + escalation thresholds is the shipped pattern.

**Broken by evidence:**
1. **B cannot authenticate A's judgement.** With no project context it can only check *form*: protocol compliance, internal consistency, whether the required fields are present and non-vacuous. That is a **validator**, not an independent opinion. Naming it "authenticator of A" will make you trust it for something it cannot do.
2. If B is an LLM, **B is correlated with A**. From the Apple study: 9 judges from 7 families gave ~2 effective votes. Three judges from a similar stack give you closer to 1.
3. **The much stronger version of B is not an LLM at all.** Anything mechanically checkable — payload shape, URL returns 200, migration has a rollback, guard checks pass — should be **code**. Your `theme_guard.py` (17 deterministic checks) is a better Judge B than any model will ever be, and no judge can argue it into a different verdict.

### Judge C (full transcript, adversarial, decides)

**Supported:** assigning an explicit adversarial role is a real, effective pattern. The adversarial framing is right, and making C the decider (rather than a veto) is right.

**Broken by evidence:**
1. **This is the anchoring cascade.** PoLL's measured advantage comes from **disjoint model families**, not from stacking judgement on judgement ([arXiv 2404.18796](https://arxiv.org/abs/2404.18796)). C reading A's verdict and B's silence converts three correlated samples into one confident opinion with three signatures on it.
2. **"C reads the transcripts" is exactly what the evidence says does not work.** Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet* ([arXiv 2310.01798](https://arxiv.org/abs/2310.01798)): **without external feedback, self-correction degrades performance.** Transcripts are not external feedback. They are more of the proposer's own framing. C reviewing a narrative is self-correction wearing a costume.
3. **Order matters and you have it backwards.** Artifact first, structured handoff second, verdicts third, distilled transcript last and optional. Narratives persuade; diffs don't. Reading the origin story before the diff is how C inherits the bug.

### The scout → worker split

**Supported:** separating planning from execution is shipped practice — spec-kit, Kiro, plan/architect modes, and DORA's "small batches" guidance all push this direction.

**Broken by evidence:**
1. **Cognition Principle 1 and 2 are aimed straight at this.** Worker gets a plan, not the trace; the worker's actions will carry implicit decisions the plan didn't specify; those decisions will conflict with the scout's assumptions. Cognition's named failure is *"subagent 1 mistook your subtask… now the final agent is left with the undesirable task of combining these two miscommunications."* **A scout→worker handoff with a compressed plan is precisely the architecture Cognition says to rule out by default.**
2. **Anthropic's own caveat**: multi-agent coordination is weak in real time and coupled coding tasks are a poor fit. Your scout/worker pair is a two-agent coordination problem over a coupled artifact.
3. **"Only acts" is where your gates get bypassed.** The moment the plan is ambiguous the worker either improvises (holes every upstream gate at the highest-blast-radius moment) or stalls. You need a structured **plan-defect path back to the scout** — and the plan must carry its own **verification command**, not just steps.
4. **What does NOT exist, and is your real gap:** nobody in this space has a clean shared **artifact + trace** contract between planner and executor. That's the thing worth building.

### Verdict on the pyramid

| Component | Status |
|---|---|
| Cheap verdict before expensive context | **Right, and your design partly violates it** (A gathers context) |
| Context-free structural validation | **Right — make it deterministic code, not a model** |
| Adversarial decider | **Right pattern, wrong seat** — put it on the artifact, not the transcript |
| Three-judge deliberation | **Contradicted by measurement.** 3 judges ≈ 1 opinion unless model families are disjoint |
| Binomial necessity verdict | **Contradicted.** Needs approve/reject/insufficient-evidence + a rubric |
| Scout → worker separation | **Right in principle, contradicted in this form** by Cognition's two principles |
| Worker only acts | **Right — but needs a defect path or it silently becomes the decider** |

---

## 4. The known failure modes, ranked by strength of evidence

1. **Correlated judges.** Apple, June 2026: 9 judges, 7 families, ~2 effective votes, best single judge matched or beat the panel ([link](https://machinelearning.apple.com/research/correlated-llm-evaluation-panels)). *Mitigation that works:* disjoint model families (PoLL), or make one "judge" deterministic code, or drop to one judge and spend the savings on post-hoc verification. *Mitigation that does not work:* more judges, better aggregation.
2. **Anchoring on the proposer's framing.** PoLL found intra-model bias is reduced only by **disjoint composition**. *Mitigation:* have C form a verdict on the artifact **before** seeing A and B, then reconcile. Or strip attribution entirely.
3. **Self-correction without external signal degrades performance** ([arXiv 2310.01798](https://arxiv.org/abs/2310.01798)). *Mitigation:* every verdict must be grounded in something outside the model — a test result, a diff, an HTTP code, a benchmark number.
4. **Goal drift by accumulation of locally-correct decisions.** Stated independently in the architecture literature: *"individually reasonable changes that pass every written rule while slowly moving the implementation away from the intent"* ([InfoQ](https://www.infoq.com/articles/agentic-fitness-functions-evolutionary-architecture)). **No per-proposal gate can see this by construction.** *Mitigation:* recurring fitness functions on the intent, not the change.
5. **Specification gaming / Goodhart.** ([Krakovna](https://vkrakovna.wordpress.com/2018/04/02/specification-gaming-examples-in-ai), [arXiv 2604.13602](https://arxiv.org/html/2604.13602v1), [OpenAI](https://openai.com/index/measuring-goodharts-law)). The moment "necessity" becomes a score judges optimise, the score decouples from necessity.
6. **Ritualised gates / checklist theatre.** Documented for ADRs ([InfoQ](https://www.infoq.com/articles/architectural-decision-record-purpose)) and measured for alerts in healthcare ([AHRQ PSNet](https://psnet.ahrq.gov/primer/alert-fatigue)). A gate with a 98% approval rate is not a gate.
7. **Verification is the bottleneck, not generation** — 98% more PRs, +91% review time, +154% PR size, zero DORA movement ([Faros via AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/10/faros-ai-dora-metrics-coding-agents-2026)). Adding a three-judge gate *increases* verification load. **Your design as specified makes the measured industry bottleneck worse.**
8. **Review catches fewer defects than reviewers expect** — Bacchelli & Bird's mismatch ([ICSE 2013](https://research.tudelft.nl/en/publications/expectations-outcomes-and-challenges-of-modern-code-review)). *Mitigation:* predict gates on mechanical checks and small batches (which do have evidence), not on judgement.
9. **AI increases delivery instability** ([DORA 2025](https://theregister.com/software/2025/09/24/dora-report-reframes-ai-as-central-to-software-development/1122275/)). *Mitigation:* rollback, canary, flags.
10. **Worker scope creep at the plan's ambiguous edges.** Cognition Principles 1–2. *Mitigation:* plan-defect path + shared trace + plan carries its verification command.

---

## 5. What to steal (ranked by evidence strength × cheapness)

1. **Post-hoc revert + decision ledger, first, before any judge.** Nothing else in this report has evidence this strong per unit of effort. Canary + automated rollback ([Argo](https://blog.px.dev/argo-rollouts)); rework rate as your KPI ([Faros](https://www.faros.ai/blog/5th-dora-metric-rework-rate-track-it-now)).
2. **Deterministic fitness functions as the primary gate** ([InfoQ](https://www.infoq.com/articles/agentic-fitness-functions-evolutionary-architecture), [continuous-architecture.org](https://continuous-architecture.org/practices/fitness-functions)). Your `theme_guard.py` model, generalised. Code, not judgement.
3. **Versioned rubrics + structured verdicts + confidence + escalation thresholds** (same source). This is what a real judge outputs: score, confidence, rationale, escalation — not a boolean.
4. **Scope evidence to the change.** Judges evaluate a bounded evidence packet, not an open-ended investigation.
5. **Disjoint model families** if you keep multiple LLM judges ([PoLL](https://arxiv.org/abs/2404.18796)) — and read the [Apple numbers](https://machinelearning.apple.com/research/correlated-llm-evaluation-panels) before assuming anything.
6. **A durable state machine for the whole lifecycle** ([Temporal HITL](https://docs.temporal.io/ai/cookbook/human-in-the-loop-python), [LangGraph interrupts](https://vanducng.dev/2025/06/26/Agentic-RAG-and-Human-in-the-Loop-with-LangGraph)). proposed → judged → approved → scouted → planned → executing → verified → closed/reverted. Without durability the queue leaks silently.
7. **Share context AND full traces between planner and executor** ([Cognition Pr. 1](https://cognition.ai/blog/dont-build-multi-agents)). Not a summary — the trace.
8. **Spec as source of truth, with the spec authored before implementation** ([spec-kit](https://github.com/github/spec-kit), [Kiro](https://dev.to/aws/dev-track-spotlight-spec-driven-development-with-kiro-dev314-45e8), and watch [sddobservatory.com](https://sddobservatory.com/)).
9. **Convert repeated judgements into deterministic rules.** InfoQ again: *"convert into deterministic guardrails when patterns repeat."* Every time a judge rules the same way three times, that rule should become code.
10. **Small batches** (DORA AI Capabilities Model). Small changes need no gate; big ones earn depth. This *is* your stakes-scaling rule, and it's already validated.
11. **Statistically honest eval gates** ([statgate](https://github.com/yashchimata/statgate)) — paired bootstrap verdicts and power analysis, so you don't ship a gate that can't detect the effect it claims to detect.
12. **Kill criteria committed in advance** ([SaaSdash](https://saasdash.ai/blog/kill-criteria-product-bets-saas)). Your "what would change my mind" field, productised.

---

## 6. What to build yourself

Only two things are genuinely uncovered by prior art: **the alignment/moat gate**, and **the planner↔executor artifact contract**.

### 6a. The alignment gate — this is Q2, and no judge can answer it

The research is unambiguous that per-proposal judgement cannot detect accumulation drift. So don't ask judges your goal question. Do this instead:

**Write the goal down as two falsifiable proxies.** Not "best learning experience" — that is unfalsifiable, so any judge will approve anything against it. Pick two of: time-to-first-aha, core-loop completion rate, week-4 return rate, unprompted willingness to pay. Two is enough. Now a judge can be *wrong*, which is the only thing that makes it useful.

**Name the moat in one sentence.** Then the gate question is not "does this align with the goal" but:

> **Does this make the learning loop harder to copy?**

Yes → moat. Generic-but-nice → sideways. Only pays off after the paywall → a bet on a future you haven't earned.

**Ask the displacement question.** Every proposal is judged against what it displaces, never in isolation:
> **What do we not build instead, and is this better than that?**

This is the single change that makes the logic sound, and it costs one field.

**Apply the killer test for your specific stage:**
> **Would I still build this if the paywall never came?**
> Yes → it serves the moat. No → it serves a business model that doesn't exist yet.

**And one recurring check that isn't per-proposal**, because that's where drift actually dies: every N merges, or monthly — *is the product still the moat?* measured against the two proxies. Use the fitness-function pattern on the *intent*.

### 6b. The handoff schema (make it a claim, not an argument)

Minimum fields, all required, all machine-checkable for presence:

```
claim            one sentence, falsifiable
evidence         what proves the problem is real + reproduction
alternatives     what else was considered, and why each was rejected
displacement     what we do not build instead  <-- the alignment field
blast_radius     what breaks if wrong; reversibility; rollback path
cost             cost to build; cost of doing nothing
verification     the exact command/check that proves it worked
disposition      what would change my mind  <-- falsifier, given to judges to test
moat_answer      moat / sideways / post-paywall-only
```

`alternatives` and `disposition` are the load-bearing fields. Necessity is decided in `alternatives`; the falsifier is what gives every judge something to *test* rather than opine about. A judge given a falsifier is a verifier. A judge given prose is a reviewer, and reviewers approve.

### 6c. The gate, reduced to something sound

**Deterministic tier (code, always runs, never a model):**
- handoff schema complete and non-vacuous
- `verification` command exists and passes
- blast radius stated; rollback path exists
- existing guard/assert checks pass
- URL/artifact checks, payload shape, etc.

**Judgement tier (models, stakes-scaled):**

| Stakes | Gate |
|---|---|
| Small + reversible (a small batch) | deterministic tier only. No judge. |
| Medium | deterministic tier + **one** judge answering one axis |
| Irreversible / high blast radius | deterministic tier + **two or three judges with disjoint model families, on different axes** (empirical / adversarial / economical), each returning score + confidence + rationale + escalation, each **forming its verdict on the artifact before seeing the others** |

**Three axes, not three servings of the same one:**
- **Empirical:** is the evidence sufficient, is the reproduction real?
- **Adversarial:** what breaks, what was not considered, what is the failure story?
- **Economical:** what does this displace, is it worth it now, does it deepen the moat?

**Refusal is a legal vote.** `insufficient evidence` must be non-failing and must escalate. If judges are forced to pick, they guess, and you get confident noise.

**One rule that keeps it from becoming a theocracy:** *the goal is an axiom. Judges never author it, never reinterpret it.* They evaluate consistency with declared goals and sufficiency of evidence. The moment they interpret what the goal "really means," you've handed product strategy to three correlated language models.

### 6d. The planner↔executor contract (Cognition-compliant)

- Scout receives the approved handoff **and** the trace, not a summary.
- Plan is a spec, not prose: files, changes, order, and **the verification command per step**.
- Worker receives **the plan + the scout's trace** (Principle 1) and must not re-decide intent.
- Worker's ambiguities go back as a structured **plan defect**, never as an improvisation. This is the hole that would otherwise let every upstream gate leak at the moment of maximum blast radius.

---

## 7. The uncomfortable findings

1. **Your pyramid is close to a measured-dead configuration.** Three LLM judges in one stack give roughly one vote (Apple). Three judges *plus* shared transcripts give roughly one vote *plus* anchoring. You have designed the correlated case deliberately. This is not a tuning problem; the mechanism (same mistakes on the same items) is structural.

2. **You have the cheapest, strongest gate in the wrong position.** Revert + ledger is the evidence-backed gate; the pyramid is the expensive, least reliable part. Build order should be inverted from your description.

3. **The pyramid increases the bottleneck the industry is actually drowning in.** +91% review time and +154% diff size with zero org-level gain is already the state of play before you add three judges per decision. A gate that adds verification load to a verification-bound system is negative value unless it *replaces* human review.

4. **Judge C reading transcripts is self-correcting without external feedback**, which the literature says degrades performance. If C reads the proposer's reasoning before the artifact, C inherits the framing. Artifact first, transcript last and optional.

5. **Judge A gathering context is the wrong direction and duplicates the scout.** Context acquisition should happen once, after approval, in the scout — with the handoff carrying its own evidence so A can *verify* rather than *investigate*.

6. **"Does this align with the goal" is not answerable by any judge**, because the goal as stated ("best learning experience") is unfalsifiable. Your pyramid isn't the bug — the goal statement is. Fixing that makes the judges mostly unnecessary.

7. **Judge B, as designed, cannot do what you want it to do.** Without context it can judge form, not merit. It is a validator. If you keep it, rename it and give it a checklist — or better, make it code, because code doesn't get anchored.

8. **The scout→worker split as specified is the architecture Cognition says to rule out by default**, and the reason is concrete: the worker's implicit decisions will conflict with the scout's assumptions, and no gate upstream can see it, because the conflict doesn't exist until execution begins.

9. **There is no published operationalisation of "does this deepen the moat."** The strategy literature (7 Powers) says strong things about *what* moats are; nobody has turned it into a review rubric. You will have to invent it, which means it needs calibration against outcomes, which means you need the ledger before the rubric is worth anything.

10. **Three judges on every handoff will ritualise.** Documented for ADRs, measured for alerts. The gates that survive are the ones that fire rarely and block hard.

### The short version

Your judges are for *"did we think this through."* Your goal is for *"should we care."* Those are different jobs, and you have built an elaborate machine for the first while the second is still undefined. Define the two proxies and the moat sentence, add the displacement field, make the mechanical checks mechanical, put the adversarial reviewer on the artifact instead of the transcript, split judges by *axis and model family* rather than by *sequence and context volume*, scale depth to reversibility — and then build the revert and the ledger first, because that is the only gate in this entire report that the evidence actually supports.

---

## 8. Sources

### Judge reliability and bias
- Apple ML Research — *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels* (Jun 2026) — https://machinelearning.apple.com/research/correlated-llm-evaluation-panels · https://www.alphaxiv.org/abs/2605.29800
- Verga et al. (Cohere) — *Replacing Judges with Juries (PoLL)* — https://arxiv.org/abs/2404.18796
- Wataoka et al. — *Self-Preference Bias in LLM-as-a-Judge* — https://arxiv.org/abs/2410.21819
- *A Systematic Study of Position Bias in LLM-as-a-Judge* (IJCNLP 2025) — https://aclanthology.org/2025.ijcnlp-long.18.pdf
- Huang et al. (DeepMind) — *Large Language Models Cannot Self-Correct Reasoning Yet* — https://arxiv.org/abs/2310.01798
- Du et al. — *Improving Factuality and Reasoning with Multiagent Debate* — https://arxiv.org/abs/2305.14325
- Eugene Yan — *Evaluating the Effectiveness of LLM-Evaluators* — https://eugeneyan.com/writing/llm-evaluators
- orq.ai — *Weak judges, strong panel* — https://orq.ai/blog/llm-juries-in-practice
- *Shrinking the Generation-Verification Gap with Weak Verifiers* — https://www.themoonlight.io/en/review/shrinking-the-generation-verification-gap-with-weak-verifiers
- *Tractable Asymmetric Verification via Deterministic Replicability* — https://ar5iv.labs.arxiv.org/html/2509.11068

### Multi-agent architecture
- Cognition — *Don't Build Multi-Agents* — https://cognition.ai/blog/dont-build-multi-agents
- Anthropic — *How we built our multi-agent research system* — https://www.anthropic.com/engineering/multi-agent-research-system
- xAGI Labs — *Cognition vs Anthropic* — https://xagi-labs.github.io/blog/cognition-vs-anthropic-dont-build-multi-agentshow-to-build-multi-agents

### Deterministic vs judgment
- InfoQ — *Agentic Fitness Functions: Extending Evolutionary Architecture Beyond Deterministic Rules* — https://www.infoq.com/articles/agentic-fitness-functions-evolutionary-architecture
- Amazon — *Use of Formal Methods at AWS* (TLA+) — https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf
- *An Empirical Evaluation of Property-Based Testing in Python* (OOPSLA'25) — https://dl.acm.org/doi/10.1145/3764068
- *Generating Structured Outputs from Language Models* — https://arxiv.org/html/2501.10868v1
- continuous-architecture.org — *Fitness Functions* — https://continuous-architecture.org/practices/fitness-functions
- Thoughtworks — *Fitness function-driven development* — https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development

### Alignment, drift, moats, prioritisation
- Langosco et al. — *Goal Misgeneralization in Deep RL* (ICML 2022) — https://proceedings.mlr.press/v162/langosco22a.html
- Krakovna — *Specification gaming examples in AI* — https://vkrakovna.wordpress.com/2018/04/02/specification-gaming-examples-in-ai
- DeepMind — *Specification gaming: the flip side of AI ingenuity* — https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity
- *Reward Hacking in the Era of Large Models: Mechanisms, Emergent Misalignment, Challenges* — https://arxiv.org/html/2604.13602v1
- OpenAI — *Measuring Goodhart's law* — https://openai.com/index/measuring-goodharts-law
- Lil'Log — *Reward Hacking in Reinforcement Learning* — https://lilianweng.github.io/posts/2024-11-28-reward-hacking
- Commoncog — *Counter-Positioning (18 case studies)* — https://commoncog.com/c/concepts/counter-positioning
- Hustle Badger — *7 Powers framework* — https://www.hustlebadger.com/what-do-product-teams-do/7-powers-establishing-your-competitive-moat
- SaaSdash — *Pre-Committing Kill Criteria* — https://saasdash.ai/blog/kill-criteria-product-bets-saas

### Code review, gates, delivery
- *A Survey on Modern Code Review* — https://arxiv.org/html/2405.18216v1
- Bacchelli & Bird — *Expectations, Outcomes, and Challenges of Modern Code Review* (ICSE 2013) — https://research.tudelft.nl/en/publications/expectations-outcomes-and-challenges-of-modern-code-review
- Microsoft — *Code Review Tech Report MSR-TR-2016-27* — https://www.microsoft.com/en-us/research/wp-content/uploads/2016/05/MS-Code-Review-Tech-Report-MSR-TR-2016-27.pdf
- The Register — *DORA 2025 report reframes AI as central to software development* — https://theregister.com/software/2025/09/24/dora-report-reframes-ai-as-central-to-software-development/1122275/
- Faros AI — *Rework Rate is Here (5th DORA metric)* — https://www.faros.ai/blog/5th-dora-metric-rework-rate-track-it-now
- AgentMarketCap — *98% More PRs, Zero DORA Improvement (Faros, 10k devs)* — https://agentmarketcap.ai/blog/2026/04/10/faros-ai-dora-metrics-coding-agents-2026
- dora.dev — *DORA's software delivery performance metrics* — https://dora.dev/guides/dora-metrics
- PX — *Automate Canary Analysis on Kubernetes with Argo* — https://blog.px.dev/argo-rollouts
- Octopus — *Recover Automatically From Failed Deployments With Argo Rollouts* — https://octopus.com/blog/recover-automatically-from-failed-deployments
- AHRQ PSNet — *Alert Fatigue* — https://psnet.ahrq.gov/primer/alert-fatigue
- Rootly — *Alert Fatigue* — https://rootly.com/alert-management/alert-fatigue

### Human-in-the-loop, durable execution, tooling
- Temporal — *Human-in-the-loop AI agent cookbook* — https://docs.temporal.io/ai/cookbook/human-in-the-loop-python
- Temporal — *Building Durable AI Applications: Human-in-the-Loop* — https://learn.temporal.io/tutorials/ai/building-durable-ai-applications/human-in-the-loop
- LangGraph HITL pattern — https://vanducng.dev/2025/06/26/Agentic-RAG-and-Human-in-the-Loop-with-LangGraph
- LangGraph HITL approval dashboard (OSS) — https://forum.langchain.com/t/human-in-the-loop-approval-dashboard-for-langgraph-agents-open-source-free-to-deploy/3616/3

### Spec-driven development
- GitHub spec-kit — https://github.com/github/spec-kit · https://github.github.com/spec-kit
- AWS — *Spec-driven development with Kiro* (re:Invent 2025) — https://dev.to/aws/dev-track-spotlight-spec-driven-development-with-kiro-dev314-45e8
- AWS — *From spec to production: three-week drug discovery agent using Kiro* — https://aws.amazon.com/blogs/industries/from-spec-to-production-a-three-week-drug-discovery-agent-using-kiro
- AWS — *Amazon Q Developer end-of-support* — https://aws.amazon.com/blogs/devops/amazon-q-developer-end-of-support-announcement
- SDD Observatory — https://sddobservatory.com/
- HN — *Ask HN: Are you leveraging Spec-Driven / Spec-Anchored development?* (Sep 2026) — https://news.ycombinator.com/item?id=49618556
- r/ClaudeCode — agent rewrites 14 files, spaghetti (Sep 2026) — https://www.reddit.com/r/ClaudeCode/comments/1wpblkg/stop_vibe_coding_blindly_the_secret_weapon_to/
- r/SpecDrivenDevelopment — https://www.reddit.com/r/SpecDrivenDevelopment/comments/1w9rhto/spec_driven_development_tools_and_skills/

### AI code review products
- Anthropic Code Review launch coverage — https://www.aiexpertmagazine.com/anthropic-ai-code-review-tool-bug-ai-generated-code · https://cryptorank.io/news/feed/2d404-anthropic-code-review-ai-generated-code
- CodeRabbit — *tops Martian code review benchmark* (vendor) — https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark
- *CodeRabbit vs Greptile vs Qodo* (2026) — https://tech-insider.org/coderabbit-vs-greptile-vs-qodo-2026

### Evals as gates
- statgate — statistically calibrated CI gates for LLM evals — https://github.com/yashchimata/statgate
- Agent Native — *LLM Evals in CI: The Eval Gate Checklist (2026)* — https://www.agentnative.dev/checklists/llm-evals-in-ci-checklist
- Max Petrusenko — *CI/CD Eval Gates for LLM Apps* — https://www.maxpetrusenko.com/blog/ci-cd-eval-gates-for-llm-apps

### Decision records and process
- adr.github.io — https://adr.github.io
- Microsoft — *Maintain an architecture decision record* — https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record
- AWS — *Master architecture decision records* — https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making
- InfoQ — *Has Your Architectural Decision Record Lost Its Purpose?* — https://www.infoq.com/articles/architectural-decision-record-purpose
- Google design docs — https://www.industrialempathy.com/posts/design-docs-at-google
- Pragmatic Engineer — *Engineering Planning with RFCs, Design Documents and ADRs* — https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs

### Failure rates and drift
- Fiddler AI — *Why do 70-95% of AI agent projects fail in production?* (vendor estimate, treat directionally) — https://www.fiddler.ai/blog/ai-agent-failure-rate
- Maxim AI — *Preventing AI Agent Drift Over Time* — https://www.getmaxim.ai/articles/a-comprehensive-guide-to-preventing-ai-agent-drift-over-time
- Converra — *Agent Drift: Why AI Agents Degrade in Production* — https://converra.ai/agent-drift
