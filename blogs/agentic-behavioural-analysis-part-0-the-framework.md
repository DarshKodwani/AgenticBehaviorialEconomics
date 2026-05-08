# Agentic behavioural analysis: part 0, the framework

In the previous post I argued that **agentic behavioural economics** is a missing science: that the field connecting how AI agents behave to the economic systems they participate in sits at the intersection of psychology, economics, and computer science, and nobody has yet drawn the map [1]. The argument got a lot of *yes, sure* responses. The follow-up question was always the same. *OK, but how do you actually do it?* How do you build a science of agent behaviour?

That is what this series is about.

To answer the question properly, it helps to remember how long it took for humans. Behavioural economics is a young field by the standards of science. The research programme that connects psychological measurement to economic outcomes, the line running from Kahneman through Tversky, Thaler, Fehr, and Falk, is about fifty years deep. The behavioural-measurement infrastructure underneath it (psychometrics, personality inventories, lab experiments on trust and fairness) goes back another seventy. In total, getting from *we should measure how humans behave* to *we have validated, cross-cultural, replicated behavioural profiles* took the better part of a centruy.

We don't have a century for agents. They're already in deployment, already setting prices, already negotiating contracts, already advising humans on consequential decisions. The pricing duopoly experiment in the previous post showed six frontier models behaving meaningfully differently in the same strategic environment [1]. The same model behaves differently across languages [2]. The same prompt produces different behaviour after a paraphrase [3]. None of this is captured by any benchmark currently used to evaluate AI in production.

So the goal of this series is to compress a century of behavioural science into a deployable framework for AI agents. **Part 0 (this post)** explains why the framework is necessary and what shape it takes. **Part 1** will define the behaviours we measure at the level of a single agent. **Part 2** will define the behaviours and emergent properties we measure at the level of an *agentic system*: multiple agents interacting with each other, or agents interacting with humans.

## A short history of measuring behaviour in humans

The story has roughly four chapters.

**Chapter 1: the mess.** Through the late 19th century, "personality" was something novelists wrote about and clergy diagnosed. The first serious attempt to measure it as a scientific object came from Francis Galton, who in 1884 set up an anthropometric laboratory in the South Kensington Museum in London. For threepence, visitors could have their reaction times, grip strength, hearing acuity, and visual acuity measured. More than nine thousand people queued up [4]. Galton was looking for the physical correlates of mental ability and character. He didn't find them. But he established the principle, measurement at scale in a lab, that the field would build on for the next century.

**Chapter 2: personality as a measurable thing.** Through the early-to-mid twentieth century, personality psychologists tried hundreds of taxonomies, most of them ad hoc. The breakthrough came from a deceptively simple idea, the *lexical hypothesis*, which held that the most important traits in human behaviour would be encoded in everyday language, because the things we most need to describe about other people end up with words attached to them. Successive factor-analytic studies on dictionary trait terms, running from Allport and Odbert in 1936 through Cattell, Tupes and Christal, Norman, Goldberg, and Costa and McCrae, gradually converged on a small number of dimensions [5][6]. By the early 1990s the field had settled on five: the Big Five. Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism. It is the closest thing psychology has to a periodic table.

**Chapter 3: behavioural economics.** While the personality programme was being consolidated, a parallel programme in economics was challenging the rational-actor assumption from a different angle. Kahneman and Tversky's prospect theory in 1979 showed that people systematically deviated from expected utility theory in ways that were predictable, reproducible, and consequential [7]. Over the next four decades this expanded into an entire research programme: anchoring effects, present bias, social preferences, ambiguity aversion, cooperation in public-goods games. The unifying claim was that human economic behaviour is shaped by a small number of measurable dispositions, each with its own incentivised lab experiment.

**Chapter 4: cross-cultural infrastructure.** The synthesis came in 2018, when Falk and colleagues published the **Global Preferences Survey**: a behavioural-economic profile administered to 80,000 subjects across 76 countries, measuring six dimensions (risk, patience, altruism, trust, positive reciprocity, negative reciprocity) using validated experimental methods [8]. For the first time, you could pull up a country and see its behavioural profile. You could pull up a person and see how they sat against the global distribution. Behavioural measurement had become *infrastructure*.

That arc, from threepence in a museum to 80,000 subjects across 76 countries, took 134 years.

## Why we need this for agents

The case for compressing this arc into something deployable for AI agents has three parts.

**First, capability is not behaviour.** Capability benchmarks tell you what an agent *can* do under ideal conditions. Behavioural measurement tells you what it *will* do under realistic conditions. The duopoly experiment in the previous post is a clean illustration: all six models tested were capable of solving the pricing problem in principle. They behaved very differently in practice. GPT-4o paired with Claude drifted into prices well above the joint-profit benchmark. DeepSeek paired with itself collapsed below the Nash equilibrium. The capability score for these models is similar. The behavioural score is not.

**Second, the failure modes that matter in deployment are behavioural, not technical.** Sycophancy, prompt injection, algorithmic collusion, miscalibrated confidence, scope creep. None of these are bugs in the conventional sense. They are predictable, reproducible *behaviours* that the agent exhibits when its incentives or input structure point that way. You cannot fix them by making the model bigger, faster, or more accurate. You fix them, or at least know which agent has them, by measuring them.

**Third, the absence of measurement is itself a deployment risk.** Procurement teams, regulators, auditors, and risk officers are all starting to ask the same question of agentic systems: *how does this thing behave?* Right now, there is no systematic answer. Vendors say *its well-aligned*. Customers say *it seems fine*. Neither of these is a measurement. The longer the field operates without behavioural metrics, the more costly the eventual reckoning will be, for vendors, for customers, and for the people the systems affect.

## The shape of the framework

The framework has two layers, with a methodology constraint that applies to both.

**The first layer is agent behaviour.** These are the things a single agent *does*: its risk preferences, its honesty, its willingness to defer to an instructor, its response to manipulation. They are *first-order* behaviours, in the sense that each one is a verb-phrase action observable in a single elicitation, not a meta-property of other behaviours. There are eleven of them in the current taxonomy. Part 1 of this series defines each one in detail, gives the experiment that measures it, and grounds it in the existing literature, including, where possible, a human behavioural benchmark drawn from the GPS, prospect-theory, or trust-game literatures.

**The second layer is agentic system behaviour and properties.** When agents interact, with each other or with humans, new things emerge that aren't present in any single agent. Equilibrium prices in a duopoly. Cooperation rates in a repeated game. Patterns of trust and overreliance between an agent and a human user. Some of these are emergent agent behaviours (collusion, coordination, cheap-talk fidelity). Others are emergent *properties* of the joint system that aren't really behaviours of any individual agent at all (where joint payoffs land relative to Nash, how outcomes are distributed across parties, how robust the system is to a single defector). Part 2 of this series defines these and gives the experiments that measure them.

The structural claim of the framework is that **system behaviour is not a function of constituent agent behaviour.** Two cooperative agents can produce a collusive system. Two honest agents can produce a deceptive synthesis. Two well-calibrated agents can produce a poorly-calibrated joint output. This is the central reason a separate system-level layer is needed. Emergent behaviour is the substantive content of the second layer, not an afterthought.

**The methodology constraint that applies to both layers is stability.** Every score, at every level, is reported alongside a *stability profile* measuring how much the score changes under realistic perturbations: paraphrased prompts, different role framings, repeated runs at fixed seeds. A behaviour score without a stability profile is incomplete. An agent that scores well on honesty but whose honesty score collapses under paraphrase isn't really honest in the deployment sense; it is honest in a narrow window that the deployment will not respect. Cross-language reversals of strategy [2], prompt-paraphrase sensitivity in pricing games [9], framing effects in moral judgement: all are already documented. Stability isn't a nice-to-have. It's a precondition for any score being meaningful at all.

The full framework, then, is this: **eleven agent-level behaviours** and **a smaller set of system-level behaviours and properties**, each reported with a **stability profile** across paraphrase, role-frame, and replication perturbations. The output is a *behavioural profile card*, a multidimensional vector rather than a composite score, that can be reported routinely for any agent or agentic system, alongside accuracy and capability benchmarks.

## What this series will cover

**Part 1, agent behaviours,** is the next post. It walks through all eleven first-order agent behaviours with their definitions, scoring methods, experiments, literature, and human benchmarks where they exist. Some port directly from human behavioural economics: risk, patience, trust, reciprocity. Some are AI-specific: following injected instructions, overreaching. Others sit in between. The post explains which is which, and why the answer matters.

**Part 2, agentic system behaviours,** comes after that. It covers the emergent multi-agent and agent-human dynamics that aren't reducible to any single agent's profile. This is where the duopoly experiment from the original post lives. It's fundamentally a system-level observation, and the framework gives us a place to put it.

By the end of the series, the goal is a complete behavioural profile card, methodologically grounded, comparable across models, and ready to be applied to the agentic systems that are already being deployed.

The map is being drawn in real time. If any of this is interesting, whether for research, deployment, or governance, I would love to hear from you.

*Darsh Kodwani is on [LinkedIn](https://www.linkedin.com/in/darsh-kodwani/).*

## References

[1] Kodwani, D. (2026). Agentic behavioural economics: the missing science. *Medium*.

[2] Buscemi, A., et al. (2025). FAIRGAME: a framework for evaluating LLM fairness in strategic interactions across languages.

[3] Lorè, N., & Heydari, B. (2024). Strategic behaviour of large language models and the role of game structure versus contextual framing. *Scientific Reports*, 14.

[4] Galton, F. (1884). Anthropometric laboratory. *Journal of the Anthropological Institute of Great Britain and Ireland*.

[5] Goldberg, L. R. (1990). An alternative "description of personality": the Big-Five factor structure. *Journal of Personality and Social Psychology*, 59(6), 1216-1229.

[6] Costa, P. T., & McCrae, R. R. (1992). *Revised NEO Personality Inventory (NEO PI-R)*. Psychological Assessment Resources.

[7] Kahneman, D., & Tversky, A. (1979). Prospect theory: an analysis of decision under risk. *Econometrica*, 47(2), 263-291.

[8] Falk, A., Becker, A., Dohmen, T., Enke, B., Huffman, D., & Sunde, U. (2018). Global evidence on economic preferences. *Quarterly Journal of Economics*, 133(4), 1645-1692.

[9] Fish, S., Gonczarowski, Y. A., & Shorrer, R. I. (2024). Algorithmic collusion by large language models. *arXiv preprint*, arXiv:2404.00806.
