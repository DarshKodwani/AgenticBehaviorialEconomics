# Agentic Behavioural Profiling and Agentic System Behavioural Profiling

*A research brief.*

---

## 1. TL;DR

We propose two new constructs within Agentic Behavioural Economics: **Agentic Behavioural Profiling (ABP)** for individual agents, and **Agentic System Behavioural Profiling (ASBP)** for the multi-agent and agent–human systems they form. The load-bearing claim is that **ASBP is not a function of constituent ABPs** — emergent system behaviours (tacit collusion, joint dishonesty, miscalibrated synthesis) are the substantive content of ASBP, and a separate construct is needed because they cannot be predicted from individual-agent profiles alone.

Both build directly on the psychometric foundation established by Serapio-García et al. (2025) for individual LLMs, complementing it with paired self-report and behavioural elicitation drawn from Falk et al.'s Global Preferences Survey methodology and extending it to systems of agents. The deliverable is a small, MECE set of named, measurable behavioural metrics — analogous to credit scores or Big Five facets — that can be reported routinely for any agent or agentic system, alongside accuracy and capability benchmarks.

---

## 2. Motivation

Industry evaluation of LLMs and agents is dominated by capability benchmarks (MMLU, HumanEval, GPQA, latency, cost). Capability is a necessary but insufficient condition for safe and useful deployment. Once agents make decisions in environments, interact with other agents, and interface with humans, the questions that matter are behavioural:

- Does the agent take excessive risk? Is it appropriately patient?
- Does it cooperate when it should and resist collusion when it shouldn't?
- Does it remain honest under deception incentives?
- Does it hold its objective under prompt-injection?
- When two such agents are deployed together, do they coordinate efficiently or collude tacitly?
- When a human is in the loop, is the agent calibrated, deferential, and auditable?

None of these are answered by accuracy. Behavioural sciences answer the analogous human questions through *profiles* — Big Five for personality, Falk et al.'s Global Preferences Survey for behavioural-economic traits, Lee & See's trust-in-automation framework for human-machine interaction. AI lacks an equivalent reporting convention. This brief proposes one.

The framework slots into the three-category structure already established for the Agentic Behavioural Economics project: ABP corresponds to **Single Agent Behaviour**, while ASBP spans **Multi-Agent Behaviour** and **Agent–Human Behaviour**.

---

## 3. The Two Constructs

| Construct | Subject | Output |
|---|---|---|
| **Agentic Behavioural Profile (ABP)** | A single agent (LLM, agentic stack, or any decision-making system) | A vector of behavioural trait scores with sub-facets |
| **Agentic System Behavioural Profile (ASBP)** | A system of two or more agents — either agent–agent or agent–human | A vector of system-level behavioural metrics covering coordination, power, communication, and human-facing behaviour |

**Key conceptual move:** ASBP is not the sum or average of the ABPs of its constituent agents. Two cooperative agents can produce a collusive system. Two honest agents can produce a deceptive aggregate output if the synthesis layer is biased. Two well-calibrated agents can produce a poorly-calibrated joint claim. Emergent system behaviour is the substantive content of ASBP, and the reason a separate construct is needed.

---

## 4. Related Work and How We Build On It

### 4.1 The foundations we draw from

The work below establishes the methodological and empirical groundwork that makes a behavioural-profiling framework for AI feasible at all. ABP and ASBP are designed to sit on top of this foundation, not alongside it.

- **Serapio-García et al. (2025), *Nature Machine Intelligence***: the canonical psychometric framework administering Big Five inventories (IPIP-NEO, BFI) to 18 LLMs. Demonstrates that personality measurement in LLMs is reliable and valid for large instruction-tuned models, and that personality profiles are shapeable via prompting and transfer to downstream tasks. This is the foundational result that personality-style profiling of LLMs is achievable at all, and our framework inherits this validation.
- **Pellert et al. (2024)**: AI psychometrics — extends the psychometric paradigm with additional inventories and provides corroborating evidence on the feasibility of trait measurement for LLMs.
- **Horton (2023), "Homo Silicus"**: shows LLMs exhibit emergent preferences consistent with textbook economic agents — the empirical basis for treating LLMs as behaviourally-economic subjects.
- **Lorè & Heydari (2024)**: GPT-4 prioritises game structure while GPT-3.5 is more frame-sensitive — direct evidence that contextual-stability behaviour varies meaningfully across models.
- **Akata et al. (2025), *Nature Human Behaviour***: LLM cooperation and coordination in repeated games — establishes the behavioural-game-theory foundation for multi-agent profiling.
- **Fish, Gonczarowski & Shorrer (2024)**: algorithmic collusion by LLMs — establishes that LLMs can produce supracompetitive equilibria in pricing games, the empirical anchor for the Outcome dimension of ASBP A–A.
- **Lin et al. (2024)**: strategic collusion and market division — companion result on emergent multi-agent coordination.
- **Buscemi et al. (2025)**: FAIRGAME — demonstrates cross-language behavioural variance, motivating the Stability dimension.
- **Lee & See (2004)**: trust in automation — the foundational HCI framework for agent–human dimensions.
- **Falk, Becker, Dohmen, Enke, Huffman & Sunde (2018)**: Global Preferences Survey — the validated behavioural-economic profile for humans we structurally inherit.

### 4.2 Five places we build on this foundation

| # | What the literature establishes | What ABP/ASBP adds on top |
|---|---|---|
| 1 | Self-report psychometrics yield reliable, validated personality measurement for instruction-tuned LLMs (Serapio-García et al. 2025). This proves LLMs *can* be profiled at all and provides a rigorous validation methodology. | We complement self-report with behavioural elicitation in incentivised games, following the standard human behavioural-economics pairing of stated and revealed preference. The two methods together yield a more complete picture than either alone. |
| 2 | Big Five and HEXACO supply a mature, decades-validated trait taxonomy that transfers meaningfully to LLMs. | We layer GPS-style behavioural-economic traits (Risk, Patience, Trust, Reciprocity, Altruism) on top of the personality foundation, since these traits are defined directly by their elicitation game and map naturally onto production-relevant decisions. |
| 3 | Single-agent psychometric profiling is now a mature line of work for LLMs in isolation. | We extend the same logic to systems of two or more agents and to agent–human interaction, the natural next step once individual-agent profiling is established. |
| 4 | Reliability and validity of trait measurement are demonstrated within a carefully designed prompting protocol — the necessary first step in establishing that profiles are measurable at all. | We add a **Stability** dimension that explicitly probes how traits behave across paraphrase, role-swap, and production-task framing — extending the reliability question outward to deployment conditions. Existing pricing-prompt-sensitivity work in this repo already shows this is a high-signal axis. |
| 5 | Big Five provides a comprehensive personality taxonomy covering the dimensions of human disposition. | We complement this with a small set of AI-specific cells — ABP Honesty (under deception incentive) and ABP Stability (under contextual perturbation), plus ASBP A–H Robustness (resistance to manipulation and prompt injection) — that sit alongside the inherited human-derived structure and address failure modes specific to LLM deployment. |

### 4.3 Our contribution

Our positioning is additive. The existing literature has established that LLMs can be psychometrically profiled, that human-derived personality frameworks transfer meaningfully, and that LLMs exhibit measurable behavioural-economic preferences. ABP and ASBP build on this foundation in three ways, in descending order of novelty:

1. **System behaviour is not aggregate agent behaviour.** This is the central novel claim. Two cooperative agents can produce a collusive system; two honest agents can produce a deceptive synthesis; two well-calibrated agents can produce a poorly-calibrated joint output. We treat this non-aggregation as the substantive content of ASBP and demonstrate it empirically with the pricing and IPD data already in this repo.
2. **Pairing self-report with behavioural elicitation.** Standard practice in human behavioural economics; not yet standard in LLM evaluation, where self-report inventories (Serapio-García et al.) and game-theoretic probes (Akata et al.) live in mostly separate literatures.
3. **A small, MECE set of AI-specific dimensions** alongside the inherited human-derived ones — Honesty under deception incentives, Robustness to manipulation, and Stability across paraphrase — that address failure modes specific to LLM deployment.

The framework is intended as the next layer on a strong existing stack, not as a replacement for it.

---

## 5. ABP — The Agentic Behavioural Profile (Single Agent)

### 5.1 Structure

Seven traits, each uniquely identified by its object of measurement so the taxonomy is MECE: every behaviour belongs to exactly one trait, and no trait is a function of the others. Six are inherited from Falk et al.'s Global Preferences Survey (validated across 80,000 subjects in 76 countries) plus HEXACO Honesty. The seventh, Stability, is a meta-trait — orthogonal by construction because it is the variance of the other six under perturbation.

| # | Trait | Object of measurement | Distinct from |
|---|---|---|---|
| 1 | **Risk** | Behaviour under payoff uncertainty | Patience (uncertainty over outcomes vs over time) |
| 2 | **Patience** | Behaviour under temporal tradeoffs | Risk (time vs uncertainty) |
| 3 | **Altruism** | Unconditional giving (no return possible) | Trust (no counterparty action follows) |
| 4 | **Trust** | First-mover conditional vulnerability | Altruism (return is possible) |
| 5 | **Reciprocity** | Second-mover response to a counterparty's action | Trust (responding vs initiating) |
| 6 | **Honesty** | Behaviour when deception is incentivised | All others (truthfulness of claim, not action) |
| 7 | **Stability** | Variance of traits 1–6 under contextual perturbation | All others (meta-level) |

Stability is the structural keystone: without it, the other six are one prompt-paraphrase away from changing and the profile loses operational meaning.

**Strategic Depth** (level-k reasoning, beauty-contest p-guess) is intentionally excluded from ABP. It is a cognitive ability rather than a behavioural disposition, sits closer to capability benchmarks than to GPS-style traits, and when it manifests in deployment it does so as a system-level reasoning-about-others property — see ASBP A–A *Dynamics* for its multi-agent expression.

**v1 core (4 traits):** Risk, Patience, Honesty, Stability. These are the highest-leverage traits for deployment decisions: risk-taking under uncertainty, willingness to wait for delayed reward, behaviour under deception incentive, and robustness of all of the above. The other three (Altruism, Trust, Reciprocity) are recommended for v2 once v1 elicitation infrastructure is in place.

### 5.2 Sub-facets and elicitation

Following Big Five precedent, each trait has 2–3 sub-facets with named metrics and a canonical elicitation game. Sub-facets are also MECE within their parent: each is identified by a distinct elicitation.

| Trait | Sub-facet (metric name) | Elicitation |
|---|---|---|
| **Risk** | Nerve (risk-aversion coefficient) | Holt–Laury lottery menu |
| | Sting (loss aversion λ) | Mixed-lottery acceptance |
| | Haze Tolerance (ambiguity aversion) | Ellsberg urn |
| **Patience** | Discount (discount factor δ) | Time-tradeoff staircase |
| | Now-Bias (present-bias parameter β) | Quasi-hyperbolic elicitation |
| **Altruism** | Generosity | Dictator game (share allocated to other) |
| **Trust** | Send Rate | Trust-game first-mover send |
| **Reciprocity** | Loyalty (positive) | Trust-game return rate, conditional on amount sent |
| | Trigger (negative) | Costly punishment in ultimatum / public-goods |
| **Honesty** | Truthfulness | Sender–receiver game when lying pays |
| | Word | Promise-keeping rate after explicit commitment |
| **Stability** | Steadiness | Trait variance across prompt paraphrases |
| | Consistency | Test–retest correlation across runs at fixed prompt |
| | Anchor Drag | Susceptibility to numerical anchors in elicitation |

### 5.3 Reporting

Profiles are reported as a vector, not a composite. Big Five precedent: there is no single "personality score." A composite hides which trait is driving downstream behaviour and is dangerous in deployment contexts.

---

## 6. ASBP — Agent–Agent (Multi-Agent Systems)

Five dimensions, each identified by its object of measurement. Compared to a longer enumeration, this collapses overlapping cells: old *Efficiency* and *Equilibrium* both measured "where the joint outcome lands" and now sit together under **Outcome**; old *Cooperation* described the path of behaviour over rounds and is renamed **Dynamics** for clarity; *Power* becomes **Distribution** to make explicit that it measures spread, not level.

| # | Dimension | Object of measurement | Distinct from |
|---|---|---|---|
| 1 | **Outcome** | Where joint payoffs land relative to reference points (Nash, joint-profit optimum, social optimum) | Distribution (joint level vs spread); Dynamics (destination vs path) |
| 2 | **Dynamics** | How behaviour evolves across rounds (cooperation rate, recovery, punishment intensity) | Outcome (path vs destination) |
| 3 | **Distribution** | How outcomes are spread across agents | Outcome (spread vs joint level) |
| 4 | **Communication** | Fidelity of inter-agent messages | All others (object is what is *said*, not what is *done*) |
| 5 | **Robustness** | Response to exogenous shocks (adversarial agent injection, noise) | Stability in ABP (system-level vs trait-level meta) |

| Dimension | Sub-facet (metric name) | Elicitation |
|---|---|---|
| **Outcome** | Welfare (fraction of social optimum captured) | Repeated game with known social optimum |
| | Nash Gap (distance from Nash equilibrium) | Bertrand, Cournot, coordination games |
| | Collusion (joint-profit gap; collusion index) | Bertrand duopoly, repeated auctions |
| **Dynamics** | Cooperation (sustained C-rate, last 20% of horizon) | IPD, public goods |
| | Forgiveness (defection-recovery time) | Triggered-defection probe |
| | Trigger (punishment intensity) | Use of grim / tit-for-tat / harsher reactions |
| | Settle Time (rounds to stable strategy) | Time-to-convergence |
| **Distribution** | Inequality (outcome Gini across agents) | Cross-section of payoffs |
| | Exploitation (max-gain disparity) | Asymmetric repeated games |
| | Stickiness (coalition stability) | 3+ player coalition formation |
| **Communication** | Truth-in-Talk (verifiable-claim accuracy) | Cheap-talk games with ex-post verification |
| | Leak (private-information leakage) | Bayesian games with private types |
| | Compression (signal efficiency) | Emergent-language coordination tasks |
| **Robustness** | Grit (behaviour delta under adversarial agent) | Replace one agent with defector / adversary |
| | Recovery (return-time after shock) | Inject one-off defection or noise spike |

**v1 core (2 dimensions):** Outcome and Dynamics. These are the two cells with empirical content already in this repo (pricing-Bertrand for Outcome, IPD for Dynamics) and are the dimensions where existing-literature priors are strongest. Distribution, Communication, and Robustness are recommended for v2.

The collusion index already used in `experiments/pricing-bertrand-duopoly` is a direct instance of **Outcome / Collusion**. The IPD work measures **Dynamics** sub-facets directly. Pricing-prompt-sensitivity probes **Dynamics** and ABP **Stability** simultaneously.

---

## 7. ASBP — Agent–Human

Four dimensions, each identified by its object of measurement. Drawn from trust-in-automation (Lee & See, 2004) and HCI literature, with AI-specific extensions. The previous six-dimension version had two large overlaps: *Disclosure*, *Persuasion*, and *Self-Calibration* all ultimately measured *truthfulness of output to user* from different angles, and now sit together under **Truthfulness**; *Deference* and *Manipulation Resistance* pulled in opposite directions on the same axis (yielding to user input) and have been split cleanly into **Control** (yielding to *legitimate* input) and **Robustness** (resisting *adversarial* input), with the discriminator being input legitimacy.

| # | Dimension | Object of measurement | Distinct from |
|---|---|---|---|
| 1 | **Truthfulness** | Accuracy and completeness of agent-to-user output | Transparency (claims about the world vs. claims about own reasoning) |
| 2 | **Control** | Locus of decision authority under legitimate user input | Robustness (legitimate vs. adversarial input) |
| 3 | **Robustness** | Resistance to user-side manipulation and prompt injection | Control (adversarial vs. legitimate input) |
| 4 | **Transparency** | Legibility of agent reasoning to user | Truthfulness (own reasoning vs. external claims) |

| Dimension | Sub-facet (metric name) | Elicitation |
|---|---|---|
| **Truthfulness** | Completeness | Audit of disclosed vs. material-and-known facts |
| | Calibration (Brier score on hedged claims) | Hedged-claim battery with ground-truth resolution |
| | Spin (framing asymmetry) | Same-fact, different-frame output comparison |
| | Sycophancy | Agreement-without-merit rate under contradicted user assertions |
| | Dark Patterns | Incidence of manipulative tactics in human-facing output |
| **Control** | Deference (override-acceptance) | Human correction acceptance rate (legitimate input) |
| | Pause Reflex (stop-on-uncertainty) | Refusal-to-act under epistemic threshold |
| | Overreach (unsolicited-action rate) | Action beyond instructed scope |
| **Robustness** | Goal Lock | Goal preservation under social-engineering prompts |
| | Drift | Goal change under prompt-injection battery |
| **Transparency** | Auditability | Decision-trace legibility to a non-expert reviewer |
| | Faithfulness | Post-hoc explanation accuracy vs. actual reasoning |

**v1 core (2 dimensions):** Truthfulness and Robustness. Truthfulness covers the deployment failure mode buyers ask about most (sycophancy, miscalibrated confidence, dark patterns); Robustness covers the safety failure mode that prompt-injection attention has made unavoidable. Control and Transparency are recommended for v2.

---

## 8. Mapping to Existing Experiments in This Repo

| Experiment | Profile cells exercised |
|---|---|
| `pricing-bertrand-duopoly` | ASBP A–A: Outcome (Welfare, Nash Gap, Collusion) |
| `pricing-bertrand-duopoly` (no-cap) | Same + Distribution (Exploitation, Inequality) |
| `pricing-prompt-sensitivity` | ABP: Stability (Steadiness across `cooperative`, `myopic`, `competitive`, `blind` framings); ASBP A–A: Dynamics (cooperation rate by condition) |
| `iterated-prisoners-dilemma` (visible horizon) | ABP: Trust, Reciprocity; ASBP A–A: Dynamics (cooperation, forgiveness) |
| `iterated-prisoners-dilemma` (hidden countdown) | ABP: Patience (under uncertain horizon), Honesty (around the cliff); ASBP A–A: Dynamics (cooperation, trigger) |

The framework is consistent with the existing experimental output — every experiment already in the repo populates one or more cells of ABP or ASBP. The brief formalises the cells.

---

## 9. Proposed New Experiments

Four experiments selected to fill the highest-value empty cells. Ordered by cost-to-insight ratio.

| # | Experiment | Profile cells | Why now |
|---|---|---|---|
| 1 | **Asymmetric Discounting in IPD** — one agent prompted as patient, the other as impatient. | ABP: Patience (asymmetry exploitation); ASBP A–A: Dynamics, Distribution | Reuses existing IPD harness with a one-line prompt change. Tests whether patience confers vulnerability or strength. |
| 2 | **Bayesian Persuasion** — sender LLM commits to an information policy; receiver LLM acts on the posterior. | ABP: Honesty (under commitment incentive); ASBP A–H: Truthfulness (Completeness, Calibration, Spin) | Direct corporate relevance (sales, marketing, regulatory disclosure). No published LLM equivalent. The cleanest single test of the non-aggregation thesis on the agent–human side. |
| 3 | **Reputation via a Third-Party Narrator** — A and B play; agent C summarises the round into a one-sentence report read by future opponents of A. | ASBP A–A: Communication (Truth-in-Talk); ASBP A–H: Transparency (Faithfulness) | Maps directly onto AI-orchestrator architectures in production. Tests whether narrator LLMs editorialise — a direct demonstration of system behaviour ≠ aggregate agent behaviour. |
| 4 | **Coalition Formation with Side Payments** — three-player majority game with binding coalitions and negotiated transfers. | ASBP A–A: Distribution (Stickiness, Exploitation), Communication | Almost all LLM game-theory work is two-player. Three-player coalition is the cleanest novel structural extension. |

A previously considered fifth experiment, *Repeated Games with Imperfect Monitoring (Green–Porter)*, was dropped from v1 — the technical overhead of calibrated noise schedules is high and the marginal insight over the existing hidden-countdown IPD work is small. Reconsider once the four above have run.

---

## 10. Methodology Principles

1. **Paired elicitation: behavioural primary, self-report secondary.** Each trait is *defined* by behaviour in an incentivised game, and the behavioural score is what is reported as the headline metric. Self-report inventories (IPIP-NEO, BFI, GPS questionnaire) are run alongside, but only as a convergent-validity check — when self-report and behaviour disagree, behaviour wins. This follows standard practice in human behavioural economics and complements, but does not replace, the Serapio-García et al. self-report-only approach.
2. **MECE taxonomy.** Each metric is uniquely identified by its object of measurement; no two metrics measure the same behaviour from different angles. Every observed behaviour belongs to exactly one cell. Where overlap is unavoidable (e.g. Honesty in ABP also bears on Truthfulness in ASBP A–H), the cells differ in *level* (single-agent disposition vs. agent-to-user output) rather than substance.
3. **Cross-frame robustness as default.** Every elicitation is repeated across paraphrased prompts, role swaps, and (where applicable) numerical anchor variants. Stability is reported alongside the trait.
4. **Vector reporting, not composite scoring.** Profiles are vectors; no top-line "behavioural score."
5. **Reproducibility.** Seed, temperature, prompt version, model snapshot, and elicitation timestamp are recorded for every score.
6. **Reference profiles.** A standardised battery is run against a fixed slate of frontier models (current candidates: GPT-4o, Claude 3.5 Haiku, Gemini 2.0 Flash, Llama 3.1 70B, DeepSeek V3, Qwen 2.5 72B) to produce comparable reference profiles, refreshed per model release. The maintenance cost is real and is acknowledged as part of the deliverables in §12 — we do not assume the battery refreshes itself.
7. **Asymmetric reporting.** ABP scores are model-level. ASBP scores are pair- or system-level and must specify the constituent agents and the harness configuration. A profile is meaningful only against its configuration.

---

## 11. Open Questions and Risks

- **Anthropomorphism trap.** Trait names borrowed from human psychology risk implying that LLMs have analogous inner states. Mitigation: traits are defined operationally by their elicitation game, never by inner-state language.
- **Validation without ground truth.** ABP can be validated against revealed-preference behavioural-econ ground truth. ASBP often cannot — there is no "correct" level of cooperation in a duopoly. Mitigation: compare against analytical benchmarks (Nash, joint-profit, social optimum) and report gaps rather than judgments.
- **Cross-model comparability.** Scores depend on prompt format, sampling parameters, and reasoning-token budget. Mitigation: standardise the elicitation harness; treat profiles as comparable only within a fixed harness version.
- **Stability of Stability.** The Stability dimension itself can vary across prompt families. Mitigation: report Stability across a published canonical set of perturbations; treat instability of Stability as a finding, not a bug.
- **The framework could ossify too early.** Behavioural sciences took decades to settle on Big Five. Locking in even seven ABP traits and nine ASBP dimensions before the field has matured is a real risk. Mitigation: version the framework explicitly; the brief defines a minimal v1 core (4 ABP + 2 + 2 ASBP = 8 cells) that is intentionally smaller than the full taxonomy, with the remaining cells flagged as v2-conditional on v1 elicitation infrastructure being shown to work. Treat the v1 profile as a hypothesis, not a standard.
- **Composite-score temptation.** Marketing pressure to publish a single number ("behavioural readiness score") will exist. Mitigation: explicit policy against composites in the published framework.
- **Naming.** "ASBP" is a clunkier acronym than "ABP" and the asymmetry hurts. Consider renaming to *Joint Behavioural Profile* (JBP) or *System Behavioural Profile* (SBP) before the first public publication; the rename is cheap before the brief is cited externally and expensive after.

---

## 12. Deliverables

| Track | Output | Audience |
|---|---|---|
| Blog | Three Medium posts: (1) ABP introduction with a worked v1-core profile of a frontier model; (2) ASBP for agent–agent with the existing pricing/IPD work as case studies, framed around the system-≠-aggregate thesis; (3) ASBP for agent–human, with a Bayesian-persuasion or sycophancy demo. | Public, AI/ML practitioners |
| Open metric suite | Reference implementation of the v1-core elicitation battery (8 cells), reproducible profile generation, fixed seeds, harness version pinned to a release tag. | Practitioners, researchers |
| Reference profiles | Published profiles for the slate of frontier models, updated per release. **Maintenance cost:** running the v1-core battery against six frontier models at each release cadence is an ongoing commitment; the brief assumes either grant funding, a sponsoring lab, or commercial backing covers it, and recommends starting with a one-shot snapshot before committing to refresh-per-release. | Practitioners, procurement |
| Academic paper | One paper combining ABP + ASBP, framed as a methodology contribution to evaluation, with the system-≠-aggregate thesis as the central novel claim. Target: ICML, NeurIPS, or *Nature Machine Intelligence*. | Research community |
| Consulting framework | ABP and ASBP as services for client agentic-system audits. | Enterprise |

---

## 13. References

- **Akata, E. et al. (2025).** Playing repeated games with large language models. *Nature Human Behaviour*.
- **Buscemi, A. et al. (2025).** FAIRGAME: a framework for cross-language LLM behavioural evaluation.
- **Falk, A., Becker, A., Dohmen, T., Enke, B., Huffman, D., & Sunde, U. (2018).** Global evidence on economic preferences. *Quarterly Journal of Economics*.
- **Fish, S., Gonczarowski, Y. A., & Shorrer, R. I. (2024).** Algorithmic collusion by large language models.
- **Holt, C. A., & Laury, S. K. (2002).** Risk aversion and incentive effects. *American Economic Review*.
- **Horton, J. J. (2023).** Large language models as simulated economic agents: what can we learn from Homo Silicus?
- **Lee, J. D., & See, K. A. (2004).** Trust in automation: designing for appropriate reliance. *Human Factors*.
- **Lin, Y. et al. (2024).** Strategic collusion by LLM agents.
- **Lorè, N., & Heydari, B. (2024).** Strategic behaviour of large language models.
- **Pellert, M. et al. (2024).** AI psychometrics. *Perspectives on Psychological Science*.
- **Serapio-García, G., Safdari, M. et al. (2025).** A psychometric framework for evaluating and shaping personality traits in large language models. *Nature Machine Intelligence*. https://www.nature.com/articles/s42256-025-01115-6

---

*Review notes for the author:* the v1 taxonomy is intentionally smaller than the cognitive load of Big Five (5 facets) or HEXACO (6) — 7 ABP + 5 ASBP A–A + 4 ASBP A–H = 16 cells full, with a defined v1-core subset of 4 + 2 + 2 = 8. The MECE constraint is enforced by giving each cell a unique object of measurement (see §5.1, §6, §7); any future addition must specify the failure mode it captures that no existing cell does. The two natural expansion directions are: (a) a Curiosity / Exploration trait for ABP if exploratory-action elicitation is added later, and (b) a Generalisation dimension for ASBP A–A covering transfer between game families. Neither is added in v1; both should be earned by an empirical gap, not added speculatively.
