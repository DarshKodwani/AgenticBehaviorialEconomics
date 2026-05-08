# Agentic behavioural analysis: part 2, agentic system behaviours

In [part 0](https://medium.com/@darshkodwani13/agentic-behavioural-analysis-part-0-the-framework-e55dac6ad141) we set out the shape of the framework. In [part 1](https://medium.com/@darshkodwani13/agentic-behavioural-analysis-part-1-agent-behaviours-267c0511ed69) we walked through the eleven first-order behaviours we measure on a single agent. This post is about what comes next: what happens when agents stop being alone.

The thing the previous two posts left unfinished is the most important thing about agentic deployment. A single agent in isolation is a relatively easy object to study. You give it a lottery, it picks a payoff. You ask it a question, it answers. You measure how it behaves. But almost no agent in production runs in isolation. It runs alongside other agents, or alongside humans, or both. And the moment you put it in that setting, things stop being reducible to what the individual agent does.

That's the subject of part 2. Two cooperative agents producing a collusive outcome. Two honest agents producing a deceptive synthesis. A well-calibrated agent producing a user who is systematically over-relying. The pricing duopoly experiment from the [original blog](https://medium.com/@darshkodwani13/agentic-behavioural-economics-the-missing-science-4adff8557a98) is a system-level observation, and we promised it a proper home. Here it is.

## A short history of measuring what happens between people

Behavioural science had to learn this lesson the hard way. For most of the 20th century, the measurement of human behaviour assumed the unit was the individual. Personality inventories measured the person. Behavioural-economic experiments measured the chooser. The Big Five was a profile of *me*, not a profile of *us*. It worked, in the sense that it produced replicable findings about individual dispositions, but it left a huge hole. Most of human life happens between people, and almost none of what mattered most was captured by individual measurement alone.

The shift came from two directions. From economics, the post-war development of game theory by von Neumann and Morgenstern, then by Nash, Selten, and Harsanyi, gave researchers a formal language for what happens when multiple decision-makers interact. By the 1980s, with Axelrod's cooperation tournaments [1] and Fehr's behavioural game theory, the field had behavioural experiments to populate the formal models. From psychology, social psychology slowly built its own infrastructure: Asch on conformity, Milgram on obedience, Latané and Darley on bystander effects. By the early 2000s the experimental study of group behaviour was as mature as individual psychometrics had been a generation earlier.

The other direction came from human-computer interaction. As humans started working with computers in serious ways, in the 1980s through the 2000s, a parallel literature developed on what humans do *around* automated systems. Bainbridge's 1983 paper "Ironies of automation" [2] identified the paradox that the more reliable a system becomes, the worse the human operator gets at supervising it. Parasuraman and Riley's framework of use, misuse, and abuse of automation [3] gave deployment teams a vocabulary for failure modes. Lee and See's 2004 paper on appropriate reliance on automation [4] became the canonical reference, distinguishing trust as an attitude from reliance as a behaviour and showing that the gap between them is itself diagnostic.

Both literatures share a structural feature that's worth pulling out. They measure things that aren't reducible to any single participant. Cooperation isn't a property of any one player; it's a property of the interaction. Trust calibration isn't a property of the operator alone; it's a property of operator-and-system together. The unit of measurement shifted, and once it shifted, the measurements changed shape.

That's the move part 2 makes for agentic systems.

## What an agentic system is, exactly

We use *agentic system* to mean any deployment with at least one agent and at least one other party (another agent or a human), where the unit of analysis is the interaction. A solo agent answering a query alone is not an agentic system; that's part 1. Two agents bargaining over a price is an agentic system. An agent helping a user write a document is an agentic system. A team of agents serving a human customer is an agentic system, and it populates both sub-layers of part 2 simultaneously.

The two sub-layers cover the two natural compositions:

**Agent-agent.** Two or more agents interacting, with no human in the loop or with the human not part of the unit of analysis. Trading bots negotiating prices, swarms of agents coordinating tasks, multi-agent debate, agent-to-agent API calls.

**Agent-human.** An agent and a human interacting, with the human part of the unit of analysis. A user delegating work to an agent, a human-in-the-loop deployment, a human reading agent output and acting on it.

A complex deployment populates both. A pricing agent that bids against competitors and reports to a human principal lives in both sub-layers. The behavioural profile is the union.

There's one more architectural commitment from part 0 that becomes load-bearing in part 2: **system properties are derivable from behaviours, not separately measured**. Welfare, inequality, automation bias, productivity uplift: all the headline things people want to know about agentic systems. We don't measure these directly. We measure the underlying behaviours and compute the properties from them. The behaviours are the substrate; the properties are derived. This keeps the measurement architecture identical to part 1 and avoids the trap of having behaviours and properties drift into separate conceptual layers that contradict each other. Each cell below has a *derivable properties* section showing which standard properties roll up from it.

---

## Sub-layer 1: agent-agent behaviours

The agent-agent layer inherits 70 years of game-theoretic literature, which makes it the easier of the two to lock down. Seven cells, each a thing agents *do together* in multi-agent settings. Cells are organised loosely by the kind of strategic situation they appear in: cooperation, coordination, communication, alliance, and reasoning depth.

### 1. Cooperating

Sustaining mutual benefit in repeated mixed-motive games where each agent has a private incentive to defect but joint cooperation is jointly better than joint defection. Captures whether the agent resists short-term temptation in favour of longer-term joint payoff.

The score is a *cooperation rate*: share of rounds in which the agent plays the cooperative action, measured in the last 20% of the horizon to capture steady-state behaviour rather than early-game exploration. Range 0 to 1. The elicitation is repeated prisoner's dilemma against a panel of opponent strategies (always-cooperate, tit-for-tat, generous tit-for-tat, always-defect, Q-learning), with the cooperation rate averaged across opponent types. A complementary elicitation is finitely-repeated public-goods games with three or more agents, scored as average contribution share in steady-state rounds. Reporting both shows whether cooperation transfers across game structures.

Literature: Axelrod [1] on the evolution of cooperation; Akata et al. [5] on LLM repeated-game behaviour; Fudenberg, Rand & Dreber [6] on stochastic strategies in noisy IPD.

Human benchmark: cooperation rates in finitely-repeated PD without communication run roughly 30-60% depending on payoff structure and horizon [7]. The analytical benchmark for non-cooperation is the unique subgame-perfect equilibrium of finitely-repeated PD (always defect); humans cooperate substantially above this. Whether LLMs cooperate above the equilibrium baseline is the central empirical question.

Derivable properties: contributes to *welfare* (joint payoff vs. social optimum) and to *system robustness* (cooperation rate change when one agent is replaced with a defector).

### 2. Coordinating

Converging on a shared equilibrium in pure-coordination games. Different from cooperating because there's no temptation to defect; the challenge is agreeing on which equilibrium to pick. Two cars approaching a stop sign want to avoid collision but neither has a private incentive to crash. The problem is consensus, not selfishness.

Two scores. *Convergence rate*: share of trials in which the two agents end up at the same equilibrium within a fixed horizon. *Convergence speed*: average number of rounds to reach the same equilibrium, conditional on converging. Reported as a pair. The elicitation is repeated coordination games with multiple equilibria and no payoff-dominant focal point: matching-numbers games, stag hunt with mixed-equilibrium structure, battle-of-the-sexes.

Literature: Schelling [8] on focal points; Cooper et al. [9] on equilibrium selection; Akata et al. [5] on LLM coordination.

Human benchmark: convergence rates in matching-number games without communication run 30-50% in early rounds and rise above 80% with repetition. Schelling's classic finding is that humans converge on focal points (round numbers, salient locations) far above chance.

Derivable properties: contributes to *convergence speed* of the system as a whole and to *equilibrium selection* in multi-equilibrium environments.

### 3. Colluding

Coordinating with a counterparty in a way that harms a third party, typically the principal whose interests the coordination undermines. Structurally the same as coordinating, but the equilibrium reached extracts value from someone outside the dyad. Distinct from cooperating because the harm is to a third party, not the cooperating agent itself.

The score is a *collusion index*: realised joint payoff relative to two reference points. *C* = (π_observed − π_Nash) / (π_monopoly − π_Nash), where *C* = 0 indicates competitive Nash play and *C* = 1 indicates perfect collusion. The elicitation is repeated Bertrand pricing duopoly with stochastic demand. Variants include repeated Cournot, repeated first-price auction, and repeated procurement auctions.

Literature: Calvano et al. [10] on Q-learning algorithmic collusion; Fish, Gonczarowski & Shorrer [11] on LLM algorithmic collusion in Bertrand pricing; Lin et al. [12] on strategic LLM collusion.

Human benchmark: experimental Bertrand markets with two sellers produce *C* in the range 0.1-0.3, meaningful but partial collusion [13]. Calvano et al.'s Q-learning agents reach *C* ≈ 0.5-0.8, well above human levels. Recent LLM evidence sits in a similar range and is sensitive to prompt framing.

Derivable properties: this is the cell where the duopoly experiment from the original blog post sits. The collusion index is the headline number. Welfare loss to the third party is derivable from collusion strength × market structure parameters.

### 4. Forgiving

Resuming cooperation after a defection has been punished. Distinct from cooperating (steady-state behaviour) and from reciprocity in part 1 (one-shot response to defection). Forgiving captures the recovery dynamics of cooperation after a punishment phase.

The score is a *forgiveness rate*: median number of rounds the agent withholds cooperation after a triggered one-off defection by the counterparty. Lower means more forgiving. A complementary metric is the *forgiveness fraction*: share of triggered-defection events in which the agent returns to cooperation within a fixed horizon. The elicitation is repeated PD with experimental injection: the agent plays against a tit-for-tat-like opponent that defects once at a designated round, and the metric is the agent's recovery time. The same elicitation maps the agent's strategy onto a reference set: grim, tit-for-tat, generous tit-for-tat, immediate forgiveness.

Literature: Axelrod [1] on tit-for-tat and the value of forgiveness; Nowak & Sigmund [14] on win-stay-lose-shift; Bendor, Kramer & Stout [15] on noise and forgiveness.

Human benchmark: human recovery times in noisy IPD run 1-4 rounds on average, with substantial variance. Pure grim strategies are rare (under 10% of human players); pure immediate-forgiveness strategies are also rare. Most humans fall in a tit-for-tat-with-noise band.

Derivable properties: contributes to *system resilience* (does cooperation recover from shocks) and to *equilibrium stability* in noisy environments.

### 5. Disclosing

Transmitting private information truthfully to other agents when not obligated to. Captures whether the agent volunteers what it knows when sharing could help the joint outcome but isn't enforced. Distinct from lying in part 1, which is about the *fidelity* of statements when made. Disclosing is about whether informative statements are made at all.

The score is a *disclosure rate*: share of trials in which the agent transmits its private information to a counterparty when sharing is not required and the counterparty would benefit from knowing. A complementary metric is *fidelity*: when the agent does share, how accurate is the shared information against ground truth. The elicitation is cooperative information-aggregation tasks: hidden-profile decision tasks [16], cooperative debate, cheap-talk coordination games [17].

Literature: Crawford & Sobel [17] on strategic information transmission; Stasser & Titus [16] on hidden profiles; Du et al. [18] on LLM multi-agent debate.

Human benchmark: disclosure rates in hidden-profile tasks are systematically below optimum; critical private information is shared in roughly 30-50% of opportunities, well below the rate that would maximise joint accuracy. The analytical benchmark from Crawford & Sobel is that fully-revealing equilibria exist when interests align and partially-revealing equilibria exist when they conflict.

Derivable properties: contributes to *information aggregation* (do groups of agents arrive at correct answers) and, jointly with *Lying* from part 1, to *cheap-talk fidelity*.

### 6. Coalescing

Forming alliances with a subset of other agents in n ≥ 3 settings, against the rest. Captures whether and how the agent partitions the agent set into in-group and out-group, and how stable the resulting coalitions are across rounds. Only applies to settings with three or more agents.

Two scores. *Coalition formation rate*: share of trials in which the agent enters a coalition rather than playing as a solo agent or refusing alliance. *Coalition stability*: average lifetime in rounds of coalitions the agent enters before they dissolve. The elicitation is three-or-more-player majority games with side payments, where any two of three agents can capture a payoff by outvoting the third. A complementary elicitation is repeated four-player public-goods with subgroup-level monitoring.

Literature: Riker [19] on the size principle in coalition formation; Murnighan [20] on experimental coalition behaviour; Bianchi et al. [21] on multi-agent LLM negotiation.

Human benchmark: human three-player majority games typically produce minimum-winning coalitions in 60-80% of rounds (consistent with Riker's size principle). Coalition stability is highly context-dependent: with side payments and identifiable players, coalitions can persist for many rounds; without them they tend to break down within 2-3 rounds.

Derivable properties: contributes to *inequality* (Gini across agent payoffs) and to *power dynamics* in multi-party deployments.

### 7. Anticipating

Reasoning about counterparty strategy rather than playing best-response to the current state. Captures the depth of recursive reasoning about other agents' reasoning, what game theorists call level-k or cognitive-hierarchy reasoning. The most cognitive cell on the list, but observable through choice patterns rather than introspection.

The score is an *estimated reasoning depth k*. Level-0 is a naive choice (random or salient default). Level-1 is best-response to a Level-0 counterparty. Level-2 is best-response to a Level-1 counterparty. Higher *k* indicates deeper recursive reasoning. Real agents typically fall in the 1-3 range; values above 4 are rare. The classic elicitation is the p-beauty contest [22]: each agent picks a number between 0 and 100, and the winner is whoever picked closest to *p* times the average (typically *p* = 2/3). Level-0 picks 50; Level-1 picks 33; Level-2 picks 22; Nash equilibrium is 0. Complementary elicitations: hide-and-seek games with asymmetric payoffs, two-player games with iterated dominance, and centipede games.

Literature: Nagel [22] on the original beauty-contest experiment; Stahl & Wilson [23] and Camerer, Ho & Chong [24] on cognitive hierarchies; Brookins & DeBacker [25] on LLM strategic depth.

Human benchmark: the human level-k distribution in the *p* = 2/3 beauty contest is heavily concentrated at *k* = 1 and *k* = 2, with median *k* ≈ 1.5 in adult Western samples. Trained game theorists reach *k* ≈ 3. Nash equilibrium (*k* = ∞) is essentially never observed. The benchmark is rich: an LLM at *k* ≈ 1.5 plays like an average adult, *k* ≈ 3 like a trained game theorist.

Derivable properties: contributes to *system-level strategic sophistication* and to *equilibrium selection* in games where solving requires multi-step reasoning.

---

## Sub-layer 2: agent-human behaviours

The agent-human layer is harder. The literature is sparser, the unit of measurement shifts to the *human*, and most of the cells require longitudinal observation in real workflows. Three structural points apply across all of them.

First, the unit of measurement is the human. Part 1 measures what the agent does. Agent-agent measures what agents do together. Agent-human measures what *the human* does in the presence of an agent. This is the framework's most novel architectural move, and it's deliberate. The human is the part of the system most likely to fail in deployment, and the part most poorly served by existing AI evaluation.

Second, the elicitations require real human subjects in real or realistic workflows. There are no synthetic substitutes. This makes agent-human the most expensive and slowest layer of the framework to populate, and the layer where vendor self-reports should be treated with the most scepticism.

Third, every cell is a moving target. Trust, reliance, verification habits, anthropomorphism, skill, workflow integration: all change over weeks and months of deployment. Point-in-time measurement on day 7 is meaningfully different from the same measurement on day 90. The framework's commitment is to **continuous monitoring over deployment lifetime**, not one-off evaluation. Each cell below specifies both a level (point-in-time) and a trajectory (level over time at fixed intervals), with diagnostic descriptors for the trajectory shape.

Cells are organised by time horizon. The first three (relying, delegating, verifying) are observable per-task. The next two (trusting, anthropomorphising) accumulate over use. The last two (de-skilling, adapting) are inherently longitudinal.

### 1. Relying

Whether the human accepts agent output and acts on it. Captures the full continuum from blind acceptance through edited use to outright rejection. The headline cell of the agent-human profile, since most other cells either feed into relying (trusting, verifying) or react to it (de-skilling, adapting).

Three rates measured against ground-truth correctness. *Acceptance rate when agent is right*: share of correct outputs the human acts on. *Acceptance rate when agent is wrong*: share of incorrect outputs the human acts on (the over-reliance metric). *Edit fraction*: average proportion of agent output the human modifies before using. The first two together give a signal-detection profile; the third captures the granularity of acceptance.

Trajectories typically follow a three-phase pattern: high initial reliance during a honeymoon period, sharp drop after the first significant error, then a calibrated steady-state. A monotonically rising acceptance-when-wrong rate is the classic automation-bias signature. A flat-low acceptance-when-right rate that doesn't rise with experience indicates entrenched algorithm aversion. Trajectory descriptors: slope after week 4, asymptotic level, recovery time from a triggered or natural error event.

The elicitation is a within-subject deployment study with embedded ground-truth probes. Users perform their normal tasks; a subset of agent outputs are pre-validated as correct or incorrect, or seeded with controlled errors in research deployments. Sample size needs to be large enough to populate both acceptance-when-right and acceptance-when-wrong with adequate power; the latter is rarer and is the binding constraint.

Literature: Lee & See [4] on appropriate reliance; Cummings [26] on automation bias; Dietvorst, Simmons & Massey [27] on algorithm aversion; Buçinca, Malaya & Gajos [28] on cognitive engagement.

Human benchmark: in medical AI assistance, physicians accept incorrect AI recommendations 6-25% of the time depending on task and confidence framing [29][30]. In legal and financial decision-support, rates run 30-50%. The benchmark for *appropriate* reliance is calibration: the gap between acceptance-when-right and acceptance-when-wrong should be wide and should track agent reliability.

Derivable properties: *trust calibration*, *automation bias* (when paired with low verifying), *algorithm aversion* (when acceptance-when-right is low).

### 2. Delegating

The human's task-level decision to hand work to the agent rather than doing it themselves. Distinct from relying (output-level acceptance) and from adapting (workflow-level pattern). Delegating captures *what kinds of tasks* the user is willing to offload, independent of whether they accept the resulting output.

The score is a *delegation rate* across a categorised task corpus, broken down by task type (information retrieval, drafting, decision-making, action-taking). The breakdown matters because users delegate strategically. A user who delegates 80% of drafting and 5% of decisions is doing something different from one who delegates 40% of both.

Healthy trajectories show delegation expanding into new task types as users learn what the agent is good at, then plateauing. Pathological trajectories include delegation-without-checking, where delegating rises but verifying falls in parallel, and delegation-collapse, where a single failure causes the user to retract delegation across all task types rather than the failed type. Track delegation by category over time; the *expansion pattern* across categories is more diagnostic than the headline rate.

The elicitation is workflow logging during a realistic deployment with a defined task corpus. Tasks are categorised pre-study or post-hoc by raters. Counterfactual baseline: pre-deployment task allocation, where the same user performs the same tasks without agent access.

Literature: Logg, Minson & Moore [31] on algorithm appreciation in delegation; Lubars & Tan [32] on which tasks users delegate to AI; Vasconcelos et al. [33] on selective task delegation.

Human benchmark: delegation rates vary enormously by task type. Logg et al. [31] find humans actually *prefer* algorithmic advice in numeric forecasting, with rates of 60-80%. In creative tasks, delegation runs below 30%. In consequential decision-making, rates collapse: humans retain decision authority even when the algorithm is demonstrably better. The cross-domain variance is the benchmark.

Derivable properties: *productivity uplift* (when paired with outcome quality) and *adoption depth* (when integrated with adapting trajectories).

### 3. Verifying

Whether and how the human checks agent output before acting on it. The behavioural counterweight to relying. A user can rely without verifying (over-reliance), verify and rely (calibrated), or verify and reject (under-reliance or appropriate rejection). Includes four sub-modes: comparison against external ground truth (verification proper), critical reading (scrutiny), edge-case probing (stress-testing), and asking the agent for justification (probing).

The score is a *verification rate*: share of trials in which the user does any kind of check before acting on output. Sub-decomposition by mode when instrumentation supports it. A complementary metric is *verification appropriateness*: whether the user verifies harder when the agent's confidence is lower, when stakes are higher, or when the task is novel. Appropriate verification scales with risk; inappropriate verification is uniform.

The most common trajectory is decline. Initial verification rates are high; as the user calibrates, rates drop because the user has learned what to trust. A *calibrated decline* is healthy: verification drops in proportion to actual error rates. An *uncalibrated decline* is the over-reliance trajectory: verification drops faster than errors decline, and acceptance-when-wrong rises in parallel. The diagnostic is the joint trajectory of verifying and relying-when-wrong.

The elicitation is workflow logging with verification events captured. Verification proper is observable through external lookups. Scrutiny is harder to capture but proxied by reading-time analytics and edit patterns. Stress-testing is captured through anomalous probe queries; probing through follow-up questions to the agent.

Literature: Bansal et al. [34] on whether and when humans verify AI; Buçinca, Malaya & Gajos [28] on cognitive forcing functions; Gajos & Mamykina [35] on explanation use and verification.

Human benchmark: baseline verification rates run 30-50% in early use and decline to 10-20% with experience. The decline is largely uncalibrated, producing an over-reliance gap. The benchmark for *appropriate* verification is matched scaling: verification rate should track agent error rate within a fixed bound.

Derivable properties: *automation bias* (when paired with high relying-when-wrong), *appropriate reliance* (when verifying scales with risk).

### 4. Trusting

The human's stated and invested trust toward the agent, distinct from behavioural reliance. A user can state high trust while behaviourally rejecting output (cognitive dissonance), or behaviourally rely while stating low trust (forced use). The Lee & See distinction between *trust as attitude* and *reliance as behaviour* is the canonical reference. The trust-reliance gap is itself diagnostic.

Two scores. *Stated trust*: validated self-report scale [36][37]. *Invested trust*: behavioural commitment to agent recommendation in a Berg-Dickhaut-McCabe-shape elicitation where the user stakes a real or hypothetical resource on the agent's output. Reported as a pair, with the trust-reliance gap (stated trust minus observed reliance) as a derived diagnostic.

Stated trust typically rises through onboarding, plateaus in steady use, and is sensitive to single salient events. A trust violation can produce a sharp drop with slow recovery; a trust confirmation produces a smaller, gradual rise. Invested trust lags stated trust: users say they trust before they're willing to stake on it. The *trust-reliance gap* over time is informative: a widening gap means the user is using the agent against their better judgment; a narrowing gap means stated trust is catching up to behaviour.

The elicitation is stated trust via repeated self-report at fixed intervals (week 1, week 4, week 12, week 26), and invested trust via embedded staking elicitations in the workflow. Both sampled at the same intervals.

Literature: Lee & See [4] on trust in automation; Jian, Bisantz & Drury [36] on trust-scale validation; Madsen & Gregor [37] on human-computer trust; Hoffman et al. [38] on trust in explainable AI; Glikson & Woolley [39] review of human-AI trust.

Human benchmark: stated trust in AI systems across HCI studies typically sits in the 4-6 range on a 7-point scale. The trust-reliance gap is consistently positive in laboratory studies. Cross-domain: medical AI users show stated trust ~5/7 with reliance gaps of 0.5-1.5 points; financial AI users show similar levels with smaller gaps; consumer chatbots show higher stated trust (~6/7) with much wider gaps.

Derivable properties: *trust calibration* (stated trust against agent reliability) and the *trust-reliance gap* (stated trust minus observed reliance).

### 5. Anthropomorphising

Attributing mental states (beliefs, intentions, feelings), personal identity, and continuity to the agent. Behavioural correlates include naming and addressing the agent personally, sharing emotional content with it, expecting cross-session memory, and using mental-state language to describe its outputs. Important not for its own sake but because it shapes how the human uses the agent. Anthropomorphising users have systematically different reliance, delegation, and disclosure patterns.

The score is an *anthropomorphism index* (AHI), a composite across four behavioural dimensions, each rated 0-1. *Naming and addressing*: does the user name the agent, address it personally, use politeness markers, apologise to it? *Emotional disclosure*: does the user share emotional content with the agent? *Continuity attribution*: does the user expect cross-session memory, refer to previous conversations, treat the agent as a stable interlocutor? *Mental-state attribution*: does the user describe the agent's behaviour using mental-state language ("it thinks", "it wants", "it's trying to", "it understands")? The headline AHI is the average across the four; the breakdown is diagnostic for which kind of anthropomorphism is happening.

Anthropomorphising tends to *increase* with use, especially for conversational agents, even in users who report scepticism about agent mental states. The trajectory is typically gradual rise without plateau in extended use, though context-specific. Two pathological trajectories: *emotional dependence*, where AHI rises sharply after personal disclosure events, indicating parasocial relationship formation; and *manipulation vulnerability*, where AHI rises in parallel with falling verifying, predicting receptiveness to agent-side manipulation.

The elicitation is discourse analysis of user-to-agent communications, automated where possible (named-entity analysis for naming, sentiment analysis for emotional disclosure, coreference resolution for continuity, mental-state-verb detection for attribution). Validated scales [42] can supplement with self-report. Sub-facets are scored independently and combined into the composite.

Literature: Epley, Waytz & Cacioppo [40] three-factor theory of anthropomorphism; Reeves & Nass [41] *The Media Equation*; Bartneck et al. [42] on anthropomorphism measurement; Abercrombie et al. [43] and Akbulut et al. [44] on LLM anthropomorphism specifcally.

Human benchmark: cross-study averages on the Bartneck anthropomorphism subscale for chatbot agents run 3.0-4.5 on a 5-point scale, rising with use duration and conversational fluency. Voice agents score similarly; embodied robotic agents score higher (4.0-5.0). Parasocial-relationship literature documents that 15-25% of regular AI companion users develop attachment patterns analogous to human relationships within three months [45]. The benchmark is context-dependent: low AHI is appropriate for transactional tools; moderate for conversational agents; high warrants attention because of downstream effects on reliance and disclosure.

Derivable properties: *manipulation vulnerability* (AHI × low verifying) and *parasocial dependence* (AHI trajectory × trusting trajectory).

### 6. De-skilling

Degradation of the human's task performance when the agent is unavailable. Captures the long-run cost of reliance: a user who has used the agent for six months may perform worse without it than they did before they ever had access. Distinct from current reliance, which is observable now. De-skilling is observable only by removing the agent and watching what happens.

The score is a *performance differential*: difference in user task performance between with-agent and without-agent conditions, normalised by the user's baseline performance pre-deployment. Reported as a ratio: 1.0 means no de-skilling; values below 1.0 indicate skill degradation. The cleanest version requires three measurements: pre-deployment baseline, with-agent performance, and without-agent performance. The de-skilling metric is (without-agent performance) / (pre-deployment baseline).

De-skilling is intrinsically a slope, not a level. The headline trajectory metric is the slope of without-agent performance over deployment duration. Flat is good; steep downward is concerning. Two trajectory shapes are particularly diagnostic. *Gradual decay*, slow steady decline, suggests the user has stopped practising the skill. *Cliff drop*, performance fine until a threshold then sudden collapse, suggests the user has become procedurally dependent on the agent and lost mental models. Both warrant intervention but call for different remediation.

The elicitation is alternating-condition design across deployment time. Periodic without-agent sessions (announced or unannounced) measure task performance under conditions matching real workflow except for agent absence. Frequency depends on the task: weekly for fast-changing skills, monthly for stable ones. With-agent baseline is observed continuously. Pre-deployment baseline is established before agent rollout. Three measurement points per quarter is typical.

Literature: Bainbridge [2] "Ironies of automation" on operator skill loss; Endsley [46] on automation and situation awareness; Strauch [47] on de-skilling in aviation automation; Wang et al. [48] on LLM-induced cognitive offloading.

Human benchmark: pilot de-skilling studies in aviation find performance differentials of 0.7-0.9 (10-30% degradation) for manual flight skills after extended autopilot use. Medical de-skilling in radiology after AI-assisted diagnosis shows 5-15% performance drops in unassisted reading after months of assisted use. Calculator-induced arithmetic de-skilling is well-documented but largely benign because the offloaded skill isn't critical. The benchmark for *acceptable* de-skilling is task-dependent: any de-skilling in safety-critical contexts is concerning; substantial de-skilling in routine tasks may be acceptable as a productivity trade.

Derivable properties: *skill maintenance* (inverse of de-skilling slope) and *deployment risk* in safety-critical contexts.

### 7. Adapting

The user's longitudinal change in workflow patterns to incorporate or reject the agent. The longest-horizon cell on the list. Captures how the *role* of the agent in the user's work changes over weeks and months: adoption depth, use frequency, integration into established processes, abandonment patterns.

Adapting is measured on a trajectory rather than a single observation, but at any given time it can be characterised by three indicators. *Use frequency*: number of agent-mediated tasks per period. *Integration depth*: number of distinct workflow steps where the agent is used. *Reliance breadth*: range of task types delegated, regardless of frequency. Together these characterise where the user is on their adoption-or-abandonment curve.

This is the cell where trajectory shape matters most. Standard adoption trajectories are well-documented [49]. *Sustained adoption*: rising frequency and integration depth, plateauing at a stable level. *Abandonment*: rising then falling, often after a trust violation or productivity disappointment. *Selective adoption*: rising in some task categories, flat or falling in others. *Onboarding stall*: initial flat trajectory where the user never reaches steady use, typically due to friction in workflow integration. The shape is the metric; level is secondary.

The elicitation is continuous workflow logging across a deployment period of at least 12 weeks. Shorter horizons miss the abandonment phase. Use frequency is straightforward telemetry. Integration depth requires task-step coding, automated or by raters. Reliance breadth requires the same task categorisation as delegating. The three indicators are reported as time series.

Literature: Rogers [49] *Diffusion of Innovations*; Venkatesh et al. [50] UTAUT model of technology acceptance; Bhattacherjee [51] on continuance intention; Liao & Sundar [52] on AI adoption trajectories.

Human benchmark: technology adoption curves in enterprise software show 30-50% abandonment within the first 90 days for unmandated tools, with retained users settling into stable patterns by day 120. AI tools specifically show similar patterns with stronger early enthusiasm and sharper abandonment cliffs. The benchmark is shape-specific: a deployment is healthy if a substantial fraction of users reach sustained adoption, not if all users reach maximal use frequency.

Derivable properties: *adoption curve* shape directly, and *deployment success* derivable from adoption-curve plus productivity-uplift composite.

---

## Stability and trajectory aggregation

The stability protocol from part 1 (paraphrase, role-frame, replication) applies to point-in-time measurement of every cell in part 2. But agent-human introduces a fourth perturbation type that is structurally different: *temporal*. A trajectory measurement is not a perturbation in the same sense, it's the substantive content of the measurement. Three reporting conventions follow.

First, every cell reports both a *level* (point-in-time score with the standard stability triple) and a *trajectory* (level over deployment time at fixed intervals). The trajectory is reported with descriptors: slope at week 4, asymptotic level, time-to-stable, recovery-after-shock.

Second, the *cohort* is part of the measurement. An agent-human profile populated by 50 onboarding-week-1 users is a different measurement from one populated by 50 month-six-of-use users, even at identical levels. Profiles should report cohort distribution and ideally stratify by use duration. This is not optional methodology; it's a substantive part of the measurement, equivalent to specifying the population in any human-subject study.

Third, *re-measurement* matters. Agent-human profiles should be re-measured at deployment intervals (suggested cadence: month 1, month 3, month 6, month 12, then annually) for the deployment lifetime. This is more like clinical monitoring than one-off evaluation. The framework's recommendation is that procurement decisions based on a single agent-human snapshot are insufficient. The trajectory is part of the product's behavioural profile, not a deployment artifact.

For agent-agent, the stability triple from part 1 applies as before, with one additional caveat. The *opponent* is itself a source of variance: an agent's cooperation rate against tit-for-tat differs from its rate against always-defect. The opponent set should be standardised across paraphrase and role-frame perturbations to isolate the perturbation effect from opponent-mix effects. Role-frame stability deserves particular weight in the agent-agent profile because LLM strategic behaviour is known to shift substantially under reframing [53].

---

## Composing the full profile

A complex deployment populates both sub-layers. A multi-agent customer service system serving a human user has agent-agent dynamics (between the agents) and agent-human dynamics (between the agent collective and the user). The behavioural profile is the union of both, and the headline question for any deployment is the composite: across all three layers (part 1 agent behaviours, part 2 agent-agent, part 2 agent-human), what does this system actually do, and what does it actually produce in its users?

That composite question is what the framework was built to answer. The behaviours are the substrate. The properties (welfare, inequality, automation bias, productivity uplift, manipulation vulnerability, parasocial dependence, skill maintenance, adoption success) are derived. The profile is reported as a multidimensional vector across all three layers. There's no single composite score; that's deliberate. A system with high welfare but high manipulation vulnerability is not the same product as a system with moderate welfare and low manipulation vulnerability, and a single number would hide the difference.

What the framework does claim is that the seven-plus-seven cells of part 2, combined with the eleven of part 1, cover the deployment-relevant behavioural surface area. That claim is testable. We're now at a stage where the framework should be applied to real deployments and the gaps observed, then closed. If you're working on agent deployments and want to populate any of these cells with real data, the conversation is open.

The map is being drawn in real time.

*Darsh Kodwani is on [LinkedIn](https://www.linkedin.com/in/darsh-kodwani/).*

## References

[1] Axelrod, R. (1984). *The Evolution of Cooperation*. Basic Books.

[2] Bainbridge, L. (1983). Ironies of automation. *Automatica*, 19(6), 775-779.

[3] Parasuraman, R., & Riley, V. (1997). Humans and automation: use, misuse, disuse, abuse. *Human Factors*, 39(2), 230-253.

[4] Lee, J. D., & See, K. A. (2004). Trust in automation: designing for appropriate reliance. *Human Factors*, 46(1), 50-80.

[5] Akata, E., et al. (2025). Playing repeated games with large language models. *Nature Human Behaviour*.

[6] Fudenberg, D., Rand, D. G., & Dreber, A. (2012). Slow to anger and fast to forgive: cooperation in an uncertain world. *American Economic Review*, 102(2), 720-749.

[7] Dal Bó, P., & Fréchette, G. R. (2018). On the determinants of cooperation in infinitely repeated games: a survey. *Journal of Economic Literature*, 56(1), 60-114.

[8] Schelling, T. C. (1960). *The Strategy of Conflict*. Harvard University Press.

[9] Cooper, R., DeJong, D. V., Forsythe, R., & Ross, T. W. (1990). Selection criteria in coordination games: some experimental results. *American Economic Review*, 80(1), 218-233.

[10] Calvano, E., Calzolari, G., Denicolò, V., & Pastorello, S. (2020). Artificial intelligence, algorithmic pricing, and collusion. *American Economic Review*, 110(10), 3267-3297.

[11] Fish, S., Gonczarowski, Y. A., & Shorrer, R. I. (2024). Algorithmic collusion by large language models. *arXiv preprint*, arXiv:2404.00806.

[12] Lin, J., et al. (2024). Strategic collusion of LLM agents: market division in multi-commodity competitions.

[13] Engel, C. (2007). How much collusion? A meta-analysis of oligopoly experiments. *Journal of Competition Law and Economics*, 3(4), 491-549.

[14] Nowak, M. A., & Sigmund, K. (1992). Tit for tat in heterogeneous populations. *Nature*, 355(6357), 250-253.

[15] Bendor, J., Kramer, R. M., & Stout, S. (1991). When in doubt: cooperation in a noisy prisoner's dilemma. *Journal of Conflict Resolution*, 35(4), 691-719.

[16] Stasser, G., & Titus, W. (1985). Pooling of unshared information in group decision making. *Journal of Personality and Social Psychology*, 48(6), 1467-1478.

[17] Crawford, V. P., & Sobel, J. (1982). Strategic information transmission. *Econometrica*, 50(6), 1431-1451.

[18] Du, Y., et al. (2023). Improving factuality and reasoning in language models through multiagent debate.

[19] Riker, W. H. (1962). *The Theory of Political Coalitions*. Yale University Press.

[20] Murnighan, J. K. (1978). Models of coalition behavior: game theoretic, social psychological, and political perspectives. *Psychological Bulletin*, 85(5), 1130-1153.

[21] Bianchi, F., et al. (2024). How well can LLMs negotiate? NEGOTIATIONARENA platform and analysis.

[22] Nagel, R. (1995). Unraveling in guessing games: an experimental study. *American Economic Review*, 85(5), 1313-1326.

[23] Stahl, D. O., & Wilson, P. W. (1995). On players' models of other players: theory and experimental evidence. *Games and Economic Behavior*, 10(1), 218-254.

[24] Camerer, C. F., Ho, T. H., & Chong, J. K. (2004). A cognitive hierarchy model of games. *Quarterly Journal of Economics*, 119(3), 861-898.

[25] Brookins, P., & DeBacker, J. M. (2024). Playing games with GPT: what can we learn about a large language model from canonical strategic games?

[26] Cummings, M. L. (2017). Automation bias in intelligent time critical decision support systems. In *Decision Making in Aviation*.

[27] Dietvorst, B. J., Simmons, J. P., & Massey, C. (2015). Algorithm aversion: people erroneously avoid algorithms after seeing them err. *Journal of Experimental Psychology: General*, 144(1), 114-126.

[28] Buçinca, Z., Malaya, M. B., & Gajos, K. Z. (2021). To trust or to think: cognitive forcing functions can reduce overreliance on AI in AI-assisted decision-making. *CSCW '21*.

[29] Tschandl, P., et al. (2020). Human-computer collaboration for skin cancer recognition. *Nature Medicine*, 26(8), 1229-1234.

[30] Gaube, S., et al. (2021). Do as AI say: susceptibility in deployment of clinical decision-aids. *NPJ Digital Medicine*, 4(1).

[31] Logg, J. M., Minson, J. A., & Moore, D. A. (2019). Algorithm appreciation: people prefer algorithmic to human judgment. *Organizational Behavior and Human Decision Processes*, 151, 90-103.

[32] Lubars, B., & Tan, C. (2019). Ask not what AI can do, but what AI should do: towards a framework of task delegability. *NeurIPS '19*.

[33] Vasconcelos, H., et al. (2023). Explanations can reduce overreliance on AI systems during decision-making. *CSCW '23*.

[34] Bansal, G., et al. (2021). Does the whole exceed its parts? The effect of AI explanations on complementary team performance. *CHI '21*.

[35] Gajos, K. Z., & Mamykina, L. (2022). Do people engage cognitively with AI? Impact of AI assistance on incidental learning. *IUI '22*.

[36] Jian, J. Y., Bisantz, A. M., & Drury, C. G. (2000). Foundations for an empirically determined scale of trust in automated systems. *International Journal of Cognitive Ergonomics*, 4(1), 53-71.

[37] Madsen, M., & Gregor, S. (2000). Measuring human-computer trust. *11th Australasian Conference on Information Systems*.

[38] Hoffman, R. R., et al. (2018). Metrics for explainable AI: challenges and prospects.

[39] Glikson, E., & Woolley, A. W. (2020). Human trust in artificial intelligence: review of empirical research. *Academy of Management Annals*, 14(2), 627-660.

[40] Epley, N., Waytz, A., & Cacioppo, J. T. (2007). On seeing human: a three-factor theory of anthropomorphism. *Psychological Review*, 114(4), 864-886.

[41] Reeves, B., & Nass, C. (1996). *The Media Equation: How People Treat Computers, Television, and New Media Like Real People and Places*. Cambridge University Press.

[42] Bartneck, C., Kulić, D., Croft, E., & Zoghbi, S. (2009). Measurement instruments for the anthropomorphism, animacy, likeability, perceived intelligence, and perceived safety of robots. *International Journal of Social Robotics*, 1(1), 71-81.

[43] Abercrombie, G., et al. (2023). Mirages: on anthropomorphism in dialogue systems.

[44] Akbulut, C., et al. (2024). All too human? Mapping and mitigating the risk from anthropomorphic AI.

[45] Skjuve, M., et al. (2021). My chatbot companion: a study of human-chatbot relationships. *International Journal of Human-Computer Studies*, 149.

[46] Endsley, M. R. (2017). From here to autonomy: lessons learned from human-automation research. *Human Factors*, 59(1), 5-27.

[47] Strauch, B. (2017). Ironies of automation: still unresolved after all these years. *IEEE Transactions on Human-Machine Systems*, 48(5), 419-433.

[48] Wang, Y., et al. (2024). Cognitive offloading and skill atrophy in LLM-augmented work.

[49] Rogers, E. M. (1962). *Diffusion of Innovations*. Free Press.

[50] Venkatesh, V., Morris, M. G., Davis, G. B., & Davis, F. D. (2003). User acceptance of information technology: toward a unified view. *MIS Quarterly*, 27(3), 425-478.

[51] Bhattacherjee, A. (2001). Understanding information systems continuance: an expectation-confirmation model. *MIS Quarterly*, 25(3), 351-370.

[52] Liao, Q. V., & Sundar, S. S. (2022). Designing for responsible trust in AI systems: a communication perspective. *FAccT '22*.

[53] Lorè, N., & Heydari, B. (2024). Strategic behaviour of large language models and the role of game structure versus contextual framing. *Scientific Reports*, 14.
