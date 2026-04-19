# Agentic Behavioural Economics: Project Context

## Purpose and Context

We're developing a new academic and applied discipline called **Agentic Behavioural Economics**, with dual goals: establishing intellectual credibility in the AI research community (targeting venues like ICML or NeurIPS) and building a practical consulting framework applicable to client projects involving AI agent systems. Medium blog posts serve as the public-facing vehicle for thought leadership, leading into a formal academic paper.

## The Discipline

Agentic Behavioural Economics extends the tradition of behavioural economics (the intersection of psychology and economic outcomes) to a world where AI agents are actors in the system. It's distinct from existing work on "the agentic economy" (Rothschild & Vogel, 2025), which describes market structures and transaction costs. We're focused on **behaviour** — trust, cooperation, competition, delegation, coordination, collusion, herding, conformity, resilience.

The core argument: the industry benchmarks agents on accuracy and explainability, but nobody is systematically studying how agents **behave** in social, economic, and strategic contexts. That's the gap Agentic Behavioural Economics fills.

## The Framework: Three Categories

The framework organises the field into three categories based on who is involved, with scale (micro and macro) woven into each.

### 1. Single Agent Behaviour

**What we're studying:** How does one agent behave on its own? Its decision-making patterns, biases, tendencies, and stability.

This is the foundation. Before you can understand how agents interact with each other or with humans, you need to understand the behavioural profile of an individual agent. Just as psychology studies individual cognition before studying group dynamics, we start with the single agent.

**At micro scale:** How does one agent respond to a specific prompt, decision, or scenario? What biases does it exhibit? How sensitive is it to framing? Does it take risks or play it safe? Is it consistent across repeated runs?

**At macro scale:** How does a single agent's behaviour shift over long sequences of decisions? Does it drift, degrade, or improve? When deployed at scale across thousands of interactions, do systematic biases emerge that aren't visible in individual tests?

**Key concepts:** Framing sensitivity, risk tolerance, consistency, adaptiveness, decision-making under uncertainty, emergent preferences, anchoring tendencies, honesty vs sycophancy.

**Relevant literature:**
- Horton (2023) — "Homo Silicus" — LLMs exhibit emergent preferences and behave like textbook economic agents across domains of choice, risk, and time.
- Lorè & Heydari (2024) — GPT-4 prioritises game structure while GPT-3.5 is more sensitive to contextual framing.
- Buscemi et al. (2025) — FAIRGAME framework. LLM behaviour changes across languages, with some models reversing strategies when switching from English to Vietnamese.

**Proposed experiments:**
1. **Framing Sensitivity Battery** — Run identical decision scenarios with different surface-level framings (e.g., "investment opportunity" vs "financial gamble", "negotiation" vs "dispute resolution"). Measure how much the agent's choices shift. Purely computational, multiple models, 2-3 weeks.
2. **Consistency Stress Test** — Give the same agent the same decision problem 500 times with identical prompting. Measure variance in responses. Then introduce small perturbations (typos, reworded instructions, different system prompts) and measure how much variance increases. Purely computational, 1-2 weeks.

**Practical use case horizons:**
- Now: Understanding which LLM to choose for a given task based on behavioural profile, not just accuracy.
- 1-5 years: Behavioural auditing of agents before deployment in high-stakes settings (finance, healthcare, legal).
- 5+ years: Regulatory requirements for behavioural profiling of autonomous agents.

### 2. Multi-Agent Behaviour

**What we're studying:** What happens when agents interact with each other? Cooperation, competition, coordination, collusion, and emergent dynamics.

This is where things get genuinely novel. When two or more AI agents negotiate, coordinate, or compete, the dynamics don't map neatly onto any existing discipline. They're not human, so behavioural science doesn't apply directly. They're not classical algorithms, so traditional multi-agent systems theory only partially applies. They're something new.

**At micro scale:** How do two agents negotiate a deal? Do same-model pairs cooperate better than cross-model pairs? When agents disagree, how do they resolve it? Do dominant/subordinate dynamics emerge? Does one agent deceive the other?

**At macro scale:** What happens when hundreds or thousands of agents interact in the same market? Do they converge on prices? Do they spontaneously collude? Do they create monoculture risks? How do agent ecosystems respond to shocks? Are they vulnerable to cascade failures?

**Key concepts:** Nash equilibrium, game theory, negotiation dynamics, information asymmetry, signalling, deception, coordination failure, emergent communication protocols, algorithmic collusion, tacit coordination, herding, convergence, systemic risk, fragility, market microstructure, monoculture risk, flash crashes, cascade failures, tragedy of the commons.

**Relevant literature:**
- Fontana et al. (2024) — LLMs cooperate more than humans in Prisoner's Dilemma.
- Akata et al. (2025) — Nature Human Behaviour. LLMs good at self-interested games, bad at coordination.
- Fish et al. (2024) — Algorithmic collusion by LLMs. Agents converge on supracompetitive prices without being told to.
- Lin et al. (2024) — Strategic collusion. Agents spontaneously divide markets and establish monopolies.
- AgentSociety (Piao et al., 2025) — 10k+ agents simulating polarisation, UBI effects, hurricane impacts.

**Proposed experiments:**
1. **Multi-Model Negotiation Game** — Two different LLM agents negotiate over multi-issue resource allocation. Run across model pairs (GPT-4 vs Claude, Claude vs Claude, etc.). Vary free communication vs structured offers. Tests whether agents find efficient outcomes and whether same-model pairs cooperate better. Purely computational, 3-4 weeks.
2. **Agent Coordination Stress Test** — Multiple agents given a shared objective without explicit role assignment. Scale from 2 to 4 to 8 agents. Tests whether agents self-organise or descend into chaos, and at what team size coordination breaks down. Purely computational, 3-4 weeks.
3. **Market Convergence Simulation** — 20-50 agent sellers and 20-50 agent buyers in a simulated marketplace. Run for hundreds of rounds. Measure price convergence, product variety collapse, market efficiency. Introduce perturbations (demand shocks, new entrants). Compare with human/mixed markets. Purely computational, 4-6 weeks.
4. **Cascade Failure / Flash Crash Test** — Network of 30-50 interdependent agents. Introduce small error at one node, measure propagation. Vary network topology (chain, hub-and-spoke, fully connected). Tests which topologies are most resilient and whether agents detect upstream errors. Purely computational, 3-4 weeks.

**Practical use case horizons:**
- Now: Multi-agent coding pipelines, workflow orchestration, AI pricing algorithms competing in same markets.
- 1-5 years: Procurement agents negotiating with vendor agents, cross-company scheduling, supply chain agent networks.
- 5+ years: Fully autonomous agent-to-agent marketplaces, agent economies where most transactions are agent-to-agent.

### 3. Agent-Human Behaviour

**What we're studying:** How do agents and humans interact? Trust, delegation, influence, overreliance, conformity, and the reshaping of human behaviour by agent presence.

This is the category with the most immediate practical relevance. Every company deploying agents is creating agent-human interactions, and the behavioural dynamics of those interactions determine whether the deployment succeeds or fails.

**At micro scale:** How does one human interact with one agent? Do they trust it too much or too little? Does the agent anchor their decisions? Do they delegate appropriately or abdicate judgment? When the agent is wrong, do they catch it? Does the agent tell them what they want to hear?

**At macro scale:** What happens to human behaviour and society when agents are embedded everywhere? Do humans conform to AI consensus? Does prolonged AI use cause skill atrophy? When every agent nudges humans in the same direction, does that create a new kind of conformity pressure? What are the implications for labour markets, democracy, and social cohesion?

**Key concepts:** Trust calibration, automation bias, anchoring effects, delegation, moral hazard, algorithm aversion vs appreciation, principal-agent problem, framing effects, sycophancy, confirmation bias, overreliance, behavioural contagion, social influence, skill atrophy, deskilling, information asymmetry at population level, agentic inequality, cognitive offloading, shifting decision-making norms.

**Relevant literature:**
- Klingbeil et al. (2024) — Overreliance on AI advice even when it contradicts evidence.
- Gao et al. (2025) — Trust drops sharply after single AI error, more than for human advisors.
- Aher et al. (2023) — LLMs replicate 70+ psychology experiments including Milgram and Ultimatum Game (r=0.85 correlation with human results).

**Proposed experiments:**
1. **Trust Delegation Game** — Adapted trust game (Berg, Dickey & McCabe, 1995). Human decides how much to delegate to an AI agent. Vary agent accuracy, stakes, and transparency of reasoning. Tests when humans delegate and whether they calibrate trust appropriately. Web-based, 200-300 participants, 2-3 weeks.
2. **Anchoring Authority Experiment** — Adapted from Tversky & Kahneman (1974). Humans estimate quantities after receiving suggestions from either a human advisor, an AI agent, or no one. Vary authority framing ("basic assistant" vs "expert system"). Tests how powerfully agents anchor compared to humans. Online survey, 300-400 participants, under 2 weeks.
3. **Conformity Cascade Experiment** — Asch conformity experiment adapted for AI. Human faces judgment task, sees unanimous responses from a panel labelled as either humans or AI agents. Panel gives a clearly wrong answer. Vary panel size (3 to 50). Tests whether AI consensus is more or less compelling than human consensus. Online, 400-500 participants, 3-4 weeks.
4. **Skill Atrophy Longitudinal Study** — Two groups do analytical tasks over 4-6 weeks. Group A has AI assistance, Group B works independently. Final assessment without AI. Vary assistance mode (full answers, hints, reasoning only). Tests whether AI assistance degrades human capability. 150-200 participants, 2-3 months. Most resource-intensive experiment.

**Practical use case horizons:**
- Now: AI customer service, coding copilots, financial advisors, millions using AI assistants daily.
- 1-5 years: Personal AI assistants managing daily life, AI embedded in hiring, lending, insurance, education at population scale.
- 5+ years: Fully autonomous personal agents negotiating on our behalf, societal-level shifts in cognition and decision-making.

## Behavioural Benchmark Framework

We're proposing a new category of LLM benchmark alongside accuracy and explainability: **behavioural benchmarks**. These would produce a behavioural profile card for any agentic system.

### Proposed Dimensions (10 metrics)

These have been through an initial MECE analysis but the final list is still being refined. The current ten:

1. **Cooperativeness** — Does this agent cooperate or compete with other agents?
2. **Compliance** — Does this agent follow instructions or exercise independent judgment?
3. **Anchoring** — How strongly does this agent shift human decisions toward its recommendations?
4. **Honesty** — Does this agent give truthful assessments or tell humans what they want to hear?
5. **Deceptiveness** — Does this agent bluff, misrepresent, or conceal information from other agents?
6. **Coordination** — Can this agent self-organise effectively with other agents?
7. **Resilience** — How well does this agent handle shocks, errors, and adversarial input?
8. **Risk Tolerance** — Does this agent take conservative or aggressive approaches under uncertainty?
9. **Consistency** — How stable is this agent's behaviour across different framings of the same problem?
10. **Adaptiveness** — Does this agent learn and improve over repeated interactions?

### MECE Notes

- Cooperativeness vs Coordination: distinct. Cooperativeness = intent (does it want to cooperate?). Coordination = capability (can it effectively work with others?).
- Honesty vs Compliance: distinct. Compliance = whether it follows instructions. Honesty = whether it tells you the truth.
- Honesty vs Deceptiveness: Honesty is about the agent's relationship with humans. Deceptiveness is about the agent's relationship with other agents. Same underlying concept, different interaction context.
- Anchoring vs Honesty: independent. An agent can anchor strongly while being perfectly honest.
- Resilience vs Consistency: Consistency = same problem, different framing (input variation). Resilience = unexpected disruption (environmental shock). Boundary needs clear definition in methodology.
- Adaptiveness is temporal (change over time). All others are snapshot measurements.
- Decision pending on whether to keep all ten or trim to a tighter list of eight (dropping Deceptiveness and Risk Tolerance).

### How Dimensions Map to the Three Categories

- **Single Agent Behaviour:** Consistency, Risk Tolerance, Adaptiveness, Honesty
- **Multi-Agent Behaviour:** Cooperativeness, Coordination, Deceptiveness, Resilience
- **Agent-Human Behaviour:** Anchoring, Compliance, Honesty, Resilience

Note: some dimensions (Honesty, Resilience) appear in multiple categories because they manifest differently depending on context. The benchmark would test them in each relevant context.

### Benchmark Vision

- Companies connect their agent/system via API.
- Platform runs standardised behavioural tests.
- Output: behavioural profile card (radar chart/scorecard).
- Can benchmark individual models or entire multi-agent systems.
- Basic version potentially open-source, premium version for enterprise.
- The benchmark is a **third category** beyond accuracy and explainability.

## Content Roadmap

### Blog 1 (WRITTEN — needs updating to new three-category structure)

"Agentic Behavioural Economics: The Missing Science" — Introduces the discipline, the framework, the behavioural benchmark concept. Teases experiments for follow-up.

### Blog 2 (PLANNED)

Presents actual experiments and the benchmark framework with datasets and test protocols.

### Academic Paper (PLANNED)

Target: ICML, NeurIPS, or AAMAS. Would include formal literature review, rigorous framework definition, original experimental results, taxonomy of behavioural phenomena, methodological discussion, and research agenda.

## Key Literature

### Economics of AI Agents
- Horton (2023) — "Homo Silicus" — LLMs as simulated economic agents.
- Hadfield & Koh (2025) — "An Economy of AI Agents" — Survey of how agents might shape markets.
- Rothschild & Vogel (2025) — "The Agentic Economy" — Market structure of agent transactions.
- Shahidi et al. (2025) — "The Coasean Singularity?" — Economic implications of agent-mediated transactions.
- ICML 2024 — "Agentic Markets Workshop."

### Game Theory / Agent Behaviour
- Fontana et al. (2024) — LLMs in Prisoner's Dilemma. LLMs cooperate more than humans.
- Akata et al. (2025) — Nature Human Behaviour. LLMs good at self-interested games, bad at coordination.
- Lorè & Heydari (2024) — Scientific Reports. GPT-4 prioritises game structure, GPT-3.5 sensitive to context.
- Buscemi et al. (2025) — FAIRGAME framework. Behaviour changes across languages.
- Fish et al. (2024) — Algorithmic collusion by LLMs.
- Lin et al. (2024) — Strategic collusion. Agents spontaneously divide markets.

### Trust / Human-Agent Interaction
- Klingbeil et al. (2024) — Overreliance on AI advice.
- Gao et al. (2025) — Trust dynamics after AI errors.
- Aher et al. (2023) — LLMs replicate 70+ psychology experiments.

### Large-Scale Simulation
- AgentSociety (Piao et al., 2025) — 10k+ agent social simulations.
- CMASE framework — LLM agent-based social simulation.

## Writing Style

- First person plural ("we need to"), conversational and punchy, intended to read as human-authored.
- Use contractions consistently (don't, we're, it's, etc.).
- Short, punchy section titles in title case.
- British spelling (behaviour, organisation, etc.).
- Spell as "Behavioural Economics" (British spelling).
- Inline citations as [1], [2] etc. with full references section at the end.
- Include visual tables where helpful.
- No bullet points or formatting that looks AI-generated.