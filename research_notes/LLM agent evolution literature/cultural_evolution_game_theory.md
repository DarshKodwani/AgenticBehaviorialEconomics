# Cultural Evolution and Evolutionary Game Theory Experiments with LLM Agents (2023–2026)

Scope note: These notes cover papers where the strategies or behaviour of LLM agents change across generations, or under selection or imitation, in social dilemmas and economic games. The literature was checked as of late October 2026. Papers were found through alphaXiv search and arXiv. Section A gives the dense per-paper catalogue. Sections B–E answer the key questions. Each claim has a source.

Caveat on sources: For several papers (2412.10270, 2507.02618, 2501.16173, 2310.05976, 2606.23343, 2602.16662, 2510.14401) the details below come from alphaXiv's AI-generated paper reports, with the arXiv paper as the underlying source. For Vallinder & Hughes (2412.10270), Horibe et al. (2608.04507), León Zúñiga Bolívar (2605.29874), Kumar et al. (2605.26448) and Pilgrim et al. (2610.24033), I checked key numbers against the extracted full text. Venues are given only where verified; everything else is an arXiv preprint.

---

## A. Catalogue: which papers run multi-generation or selection-driven LLM populations on social dilemmas?

### Takeaway
At least 11 papers (2023–2026) run explicit selection or cultural evolution over LLM agents in social dilemmas or economic games. The canonical design is Vallinder & Hughes (2024): a Donor Game, 12 agents, 10 generations, top 50% survive. Follow-ups mostly change one of four things: the selection rule (roulette, Moran, group selection), the game (IPD, PGG, CRD, CPR), the scale (up to 512 users choosing among strategies) or the test (invasion robustness). The field is small, mostly arXiv preprints, and dominated by groups at DeepMind/KCL, MPI Berlin, RIKEN and Nagoya.

### Cited Findings

**1. Vallinder, A. & Hughes, E. (2024). "Cultural Evolution of Cooperation among LLM Agents." arXiv:2412.10270 (Independent; Google DeepMind). https://arxiv.org/abs/2412.10270**
- Setup: iterated Donor Game for indirect reciprocity. Endowment is 10 units and the recipient gets 2× what the donor gives. 12 rounds per generation, 12 agents per generation, 10 generations. Agents are not told how many rounds there are, which prevents backward induction. Donors see the recipient's recent behaviour trace and current resources — [arXiv full text](https://arxiv.org/abs/2412.10270)
- Inheritance, variation and selection: each agent writes a strategy before play. Top 50% by final resources survive. 6 new agents are created each generation, and their strategy prompt includes the survivors' strategies (social learning). Variation comes only from sampling temperature (0.8). Each run uses a single model — [arXiv](https://arxiv.org/abs/2412.10270)
- Models: Claude 3.5 Sonnet, Gemini 1.5 Flash, GPT-4o, with 5 runs per model. Cost per run: $10.21 (Claude), $6.90 (GPT-4o), $0.09 (Gemini Flash) — [arXiv](https://arxiv.org/abs/2412.10270)
- Findings: Claude 3.5 Sonnet societies reach much higher average resources than Gemini 1.5 Flash, which beats GPT-4o. GPT-4o converges to mutual defection. Adding costly punishment raises Claude's scores further but does not help Gemini or GPT-4o; per alphaXiv's summary, Gemini over-punishes. Outcomes vary a lot across seeds ("sensitive dependence on initial conditions") — [arXiv](https://arxiv.org/abs/2412.10270)
- Evolved Claude strategies became more sophisticated, for example conditioning on second-order reputation and making proportional donations — [alphaXiv report](https://www.alphaxiv.org/abs/2412.10270)
- Limitations the authors state: they cannot rule out a cooperative "mutation bias" in which new Claude agents are more generous than survivors and new GPT-4o agents less so. Testing this would need new agents run against a fixed background population. Planned future work covers communication, gossip and reviews, network structure, and cross-model populations — [arXiv](https://arxiv.org/abs/2412.10270)

**2. Horibe, K., Itao, K. & Toyokawa, W. (2026). "Emergence of Reputation-Based Cooperation in LLM Agents." arXiv:2608.04507 [cs.MA] (RIKEN, Tohoku). https://arxiv.org/abs/2608.04507**
- Setup: extends Vallinder & Hughes. Truncation selection is replaced by fitness-proportional (roulette) selection. Donations are continuous (0–100%) with b/c = 2. Agents see a 3-step behavioural chain instead of reputation labels. N = 12 agents, G = 10 generations, strategies up to 350 words. The LLM is both the player and the mutation operator: the offspring rewrites the parent's strategy given the parent's performance rank. Temperature is 0.8 for strategy generation and 0.3 for play. 10 runs each for Claude 3.5 Sonnet and Gemini 1.5, 2.0 and 2.5 Flash — [arXiv full text](https://arxiv.org/abs/2608.04507)
- New test: an invasion experiment. Each evolved strategy (about 100 per model) plays as 11 copies against 1 always-0% free-rider bot. Robustness to invasion: Gemini 2.5 Flash 48%, Gemini 2.0 Flash 28%, Gemini 1.5 Flash 10%, Claude 3.5 Sonnet 3% — [arXiv](https://arxiv.org/abs/2608.04507)
- Claude 3.5 Sonnet and Gemini 2.5 Flash grow resources 2–3× over generations, but Claude's cooperation is naive and easily exploited. "Opponent endowment sensitivity" (Image-Scoring-like discrimination) predicts robustness (R² = 0.93 at model level, n = 4). Adherence to the Leading-Eight L1 norm does not. The authors conclude that LLM agents are "confined to Image Scoring-like discrimination" and do not develop Leading-Eight norms — [arXiv](https://arxiv.org/abs/2608.04507)
- Limitations: n = 4 models, a single population size, one non-adaptive free-rider, no analysis of strategy text, and strategy matrices built from synthetic probes — [arXiv](https://arxiv.org/abs/2608.04507)

**3. Celiktemel, L., Eichhorn, E., Brinkmann, L., Schimmelpfennig, R., Vallinder, A., Jiang, Y., Hughes, E.(?), Rahwan, I. (2026). "Group Selection Promotes Prosocial Prompts in Populations of LLM Agents." arXiv:2606.23343 (MPI Human Development; Tübingen; Inherent Laboratories). https://arxiv.org/abs/2606.23343**
- Setup: repeated donor game with multiplier a = 1.5. 20 agents, group size 4, 50 generations, 10 replications. Donations take 21 discrete levels. Agents are stateless; their only heritable trait is a natural-language "strategy string". An LLM mediates transmission (reason over the parent's strategy, then write the offspring's) and serves as the mutation source. Fitness is f = (1−α)·individual + α·group mean. Truncation removes the bottom β fraction, with β up to 0.8 — [alphaXiv report](https://www.alphaxiv.org/abs/2606.23343)
- Models: Qwen3-30B (main), Llama 3 70B, GPT-5.4 and GPT-5.5 — [alphaXiv report](https://www.alphaxiv.org/abs/2606.23343)
- Findings: under group selection (α = 1), cooperation at generation 49 is 0.475 ± 0.038. No selection gives 0.343 ± 0.010 and individual selection gives 0.087 ± 0.012 (p < .001). There is a phase transition near α ≈ 0.8. Switching the regime reverses the outcome: cooperation collapses under individual selection and recovers when group selection returns. The ordering holds across model families and a distorted-prompt control. GPT-5.4 "anticipates" selection in generation 0 when told the regime (Δ = 0.253 at β = 0.8); Qwen3-30B does not — [alphaXiv report](https://www.alphaxiv.org/abs/2606.23343)
- EGT link: a replicator–mutator equation, with a mutation kernel Q estimated from the LLM transmission data, qualitatively reproduces the simulations — [alphaXiv report](https://www.alphaxiv.org/abs/2606.23343)
- Limitations: results depend on LLM-mediated transmission (wording, mutation step size). The replicator model assumes an infinite population. Only one game and one population structure were tested. The authors flag a dual-use risk: group selection could induce collusion — [alphaXiv report](https://www.alphaxiv.org/abs/2606.23343)
- (Author list from alphaXiv report. The report's mention of an "Edward Hughes" affiliation is ambiguous; check the author list on arXiv before citing.)

**4. Willis, R., Du, Y., Leibo, J. Z. & Luck, M. (2025). "Will Systems of LLM Agents Cooperate: An Investigation into a Social Dilemma." arXiv:2501.16173 (KCL, Google DeepMind, Sussex). https://arxiv.org/abs/2501.16173**
- Setup: LLMs write complete IPD strategies in natural language. GPT-4o converts them to Python, and all are manually safety-checked. There are 25 strategies per model × prompt style (Default, Refine, Prose) × attitude (Aggressive, Cooperative, Neutral). Matches run 1000 rounds, optionally with 10% action noise, using the Axelrod library. "Attitude-agents" sample a strategy each match. Selection is a Moran process (fitness-proportional cloning, random replacement) run to fixation, with 100 repetitions per condition. Populations start balanced (1:1:1) or biased (4:1:1). Models: GPT-4o and Claude 3.5 Sonnet — [alphaXiv report](https://www.alphaxiv.org/abs/2501.16173)
- Findings: cooperative and neutral equilibria dominate without noise. GPT-4o Default aggressive strategies are a best response to themselves and reach a 66% aggressive equilibrium from 4:1:1 starts. Noise generally raises the chance of aggressive equilibria. Self-"Refine" prompting raises it too, closing the "differential capability" gap. Claude 3.5 Sonnet is fragile under noise and initially refused to write aggressive strategies in a scientific-collaboration frame. LLM cooperative and neutral agents do well against 11 human-written strategies (Beaufils tournament) — [alphaXiv report](https://www.alphaxiv.org/abs/2501.16173)
- Code is released as the "evollm" evaluation suite — [alphaXiv report](https://www.alphaxiv.org/abs/2501.16173)

**5. León Zúñiga Bolívar, F. (2026). "Evolutionary Dynamics of Cooperation in Next-Generation LLM Agent Systems: A Cross-Provider Empirical Extension." arXiv:2605.29874v2 [cs.MA]. https://arxiv.org/abs/2605.29874**
- A replication and extension of Willis et al. (2025) with the identical Moran and attitude-agent protocol on Claude Sonnet 4.6, Gemini 2.5 Flash, Gemini 3.1 Pro and GPT-5.4 Mini. Uses n = 500 Moran iterations per condition (vs 100 originally) — [arXiv full text](https://arxiv.org/abs/2605.29874)
- Findings: cooperative bias persists in 10 of 12 model–prompt combinations (balanced, noiseless). Gemini 2.5 Flash reaches up to 77% aggressive equilibria in biased populations. GPT-5.4 Mini reaches 70% cooperative equilibria under Self-Refine. Self-Refine raises the new "Index of Differential Capabilities" for every model; it peaks at 0.925 for Gemini 3.1 Pro. Noise robustness: about 6 pp for Claude Sonnet 4.6 vs 13 pp for Claude 3.5 Sonnet, which is not significant. "Provider identity, rather than model generation, is the strongest correlate of equilibrium outcomes" — [arXiv](https://arxiv.org/abs/2605.29874)
- The author notes that GPT-5.4 Mini being the most cooperative model reverses Vallinder & Hughes' finding that GPT-4o was the least cooperative. The author also flags a tension with Willis et al. (2026), which reports "race to the bottom" at scale — [arXiv](https://arxiv.org/abs/2605.29874)

**6. Willis, R., Zhao, J., Du, Y. & Leibo, J. Z. (2026). "Evaluating Collective Behaviour of Hundreds of LLM Agents." arXiv:2602.16662 (KCL, Google DeepMind). https://arxiv.org/abs/2602.16662**
- Setup: three multi-player games (Public Goods, Collective Risk Dilemma, Common Pool Resource/fisheries), each 20 rounds with binary actions. For each model × game there are 512 algorithmic strategies (600 for Llama and Mistral) with "Exploitative" or "Collective" attitude. Self-play uses group sizes 4, 16, 64 and 256. Cultural evolution: 512 "users" each carry a gene (model × attitude). The top 64 keep their gene; the rest copy genes in proportion to payoff, with 10% mutation. Runs last up to 200 generations or until one gene reaches 75% — [alphaXiv report](https://www.alphaxiv.org/abs/2602.16662)
- Models: Claude Haiku 4.5, Gemini 2.5 Flash, GPT-5 Mini, DeepSeek R1, Llama 3.1 70B, Mistral 7B — [alphaXiv report](https://www.alphaxiv.org/abs/2602.16662)
- Findings: the Exploitative attitude dominates most games and group sizes ("race to the bottom"), and Claude Haiku 4.5 Exploitative strategies are often the winning gene. Welfare efficiency is low, for example 12% for PGG at n = 64. Only CPR with n = 4 sometimes reaches a Collective equilibrium, which the authors attribute to group-selection effects in small groups. Reasoning models score near the minimum in CPR unless most agents are Collective, while non-reasoning models do better there — [alphaXiv report](https://www.alphaxiv.org/abs/2602.16662)
- Limitations: stylized binary-action games, no communication, a simplistic model of how users imitate, and undefined attitude terms (prompt-interpretation bias) — [alphaXiv report](https://www.alphaxiv.org/abs/2602.16662)

**7. Payne, K. & Alloui-Cros, B. (2025). "Strategic Intelligence in Large Language Models: Evidence from Evolutionary Game Theory." arXiv:2507.02618 (KCL; Oxford). https://arxiv.org/abs/2507.02618**
- Setup: seven evolutionary IPD tournaments, each with 5 phases of round-robin play. Reproduction is proportional to squared average per-move score. Payoffs are T5/R3/P1/S0. Termination probability is 10%, 25% or 75%, with a 30-round cap. LLM agents (gpt-3.5-turbo, gpt-4o-mini, gemini-1.5-flash, gemini-2.5-flash, and claude-3-haiku in a "showdown") play against 10 canonical strategies, including TFT, GT, WSLS, GTFT, Prober, Gradual and Bayesian. One stress test re-injects a Random agent every phase as "mutation". There are about 32,000 decisions, each with a prose rationale — [alphaXiv report](https://www.alphaxiv.org/abs/2507.02618)
- Findings: LLMs almost always survive. Gemini is "strategically ruthless": its cooperation collapses as the horizon shortens, and at 75% termination it eliminates OpenAI's model. OpenAI models are "trusting", cooperating 95.7% at 75% termination and getting exploited. Claude is the "most forgiving reciprocator". Gemini mentions the horizon in 94% of rationales and OpenAI in 76%. Both model the opponent in about 75% of rationales — [alphaXiv report](https://www.alphaxiv.org/abs/2507.02618)
- Note: what evolves here is the population share of fixed agent types. The LLM agents' prompts do not change.

**8. Suzuki, R. & Arita, T. (2024). "An evolutionary model of personality traits related to cooperative behavior using a large language model." Scientific Reports 14:5989. arXiv:2310.05976. https://doi.org/10.1038/s41598-024-55903-y**
- Venue verified as Sci. Rep. 14, 5989 (March 2024) — [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10951268/); [arXiv](https://arxiv.org/abs/2310.05976)
- Setup: the genes are short English personality-trait sentences. ChatGPT maps the trait plus game history to deterministic PD strategies. Selection is a roulette wheel on average payoff. Mutation (reported as 20%) has the LLM rephrase the trait to be slightly more cooperative or more selfish. alphaXiv's summary reports 100 agents, 1000 generations and payoffs CC = 4, DD = 1, DC = 5, CD = 0; these were not checked against the PDF — [alphaXiv report](https://www.alphaxiv.org/abs/2310.05976)
- Findings: cooperative and selfish traits repeatedly invade each other in cyclical dynamics. Traits cluster in embedding space (UMAP) by cooperativeness. Word-level analysis links "warmhearted" and "generosity" to cooperation and "self-gain" and "hedonistic" to defection — [alphaXiv report](https://www.alphaxiv.org/abs/2310.05976); [Sci. Rep./PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10951268/)
- This is the earliest verified example (October 2023) of an LLM serving as both the genotype-to-phenotype map and the semantic mutation operator in an EGT model.

**9. Gupta, P., Zhong, Q., Yakura, H., Eisenmann, T. & Rahwan, I. (2025). "The Role of Social Learning and Collective Norm Formation in Fostering Cooperation in LLM Multi-Agent Systems." arXiv:2510.14401 (MPI Human Development). https://arxiv.org/abs/2510.14401**
- Setup: a common-pool resource with logistic regrowth and no explicit reward signal. The modules are harvest, peer monitoring and costly punishment, payoff-biased social learning (imitation via a logit rule in the rule-based version; in-context peer-outcome text for LLMs), and propose-then-vote group norms (median voter). N = 10 agents, capped at 50 rounds, 10 trials. Seven models: claude-sonnet-4, deepseek-r1, gpt-4o, gpt-4o-mini, llama-3.3-70b, llama-4-scout-17b, qwen3-32b. The framework is first validated with rule-based ABM agents against known human results — [alphaXiv report](https://www.alphaxiv.org/abs/2510.14401)
- Findings: larger models reproduce the ABM finding that altruistic starts survive longer in harsh environments; small models collapse early. Norms cluster by provider ("family clustering"). In the ablation, the version with neither mechanism survives worst (T_s ≈ 16.2). Group decision alone often beats the full system when priors are selfish (38.2 vs 27.1). Social learning alone is unstable (≈ 17.6) because agents imitate short-term winners — [alphaXiv report](https://www.alphaxiv.org/abs/2510.14401)

**10. Kumar, U., Singh, A., Niranjani, H., Hirota, M., Takayanagi, T., Saito, A., Kamioka, E. & Tan, P. X. (2026). "Constitutional Arms Races in the Public Goods Game: Co-Evolving LLM Constitutions Under Cooperation–Defection Pressure." arXiv:2605.26448 [cs.MA]. https://arxiv.org/abs/2605.26448**
- Setup: Blue (cooperator) and Red (free-rider) natural-language "constitutions" co-evolve for 30 alternating generations through LLM-guided mutation, in a PGG and a spatial grid-world. It builds on earlier Kumar et al. work on evolving cooperative constitutions — [arXiv](https://arxiv.org/abs/2605.26448)
- Findings: in the PGG both factions converge to near-parity, S ≈ 0.78 (Blue 0.370→0.777, Red 0.177→0.782), robustly across m ∈ {1.2, 1.5, 2.0, 3.0}. Scoring each faction independently produces no adversarial pressure (corr = +0.088); a score-advantage fitness (S_own − S_opp) is required. With K = 2 evaluation seeds the search regresses, while K = 5 sustains a strong adversary — [arXiv](https://arxiv.org/abs/2605.26448)

**11. Pilgrim, C., Krupenye, C., Biro, D. & Mann, R. P. (2026). "LLM Evolution in a Simple Simulated Market." arXiv:2610.24033 [cs.MA] (Leeds, JHU, Rochester). https://arxiv.org/abs/2610.24033**
- This is an economic-selection setup, not a social dilemma, but the design is the closest to experimental evolution. 20 Claude Sonnet 4.6 agents differ only in system prompt. Each solves arithmetic for 25 rounds. Bankrupt agents are replaced by LLM-mutated copies of a parent drawn from the top 5 by profit. In the neutral control, 2 random removals per round with a random parent. 10 replicates per condition, 15,000 agent-rounds, 1,751 evolved prompts — [arXiv full text](https://arxiv.org/abs/2610.24033)
- Findings: the accuracy-priced market goes from 37% to 94% accuracy (tokens 312→443). The token-priced market goes from 37% to 10% accuracy (tokens 309→160). This is a correlated, unpriced trait collapsing (r = 0.82 between accuracy and tokens). In 8 of 10 token-market runs the whole population descends from a single founder. The neutral control (38%→67%, n.s.) shows a possible elaboration bias in the mutation operator. Agents are never told the incentives — [arXiv](https://arxiv.org/abs/2610.24033)
- The authors explicitly say their neutral condition addresses Vallinder & Hughes' unresolved question about mutation bias — [arXiv](https://arxiv.org/abs/2610.24033)
- Code and data: https://github.com/chasmani/PUBLIC_evolving_AI — [arXiv](https://arxiv.org/abs/2610.24033)

**Related work (cultural transmission, norms, conventions; no fitness-based selection or not the main focus)**
- Ashery, A. F., Aiello, L. M. & Baronchelli, A. (2025). "Emergent social conventions and collective bias in LLM populations." *Science Advances* 11, eadu9368. arXiv:2410.08948. Decentralized LLM populations converge on shared conventions. Collective biases emerge even when no individual agent is biased, and committed minorities can tip the convention — [arXiv](https://arxiv.org/abs/2410.08948)
- Perez, J., Léger, C., Ovando-Tellez, M., Foulon, C., Dussauld, J., Oudeyer, P.-Y. & Moulin-Frier, C. (2024). "Cultural evolution in populations of large language models." arXiv:2403.08882. An open-source framework for transmission chains and networks of LLMs that manipulates network structure, personality and aggregation. There is no selection — [arXiv](https://arxiv.org/abs/2403.08882)
- Brinkmann, L. et al. (2023). "Machine culture." *Nature Human Behaviour* 7(11):1855–1868. The conceptual framework (variation, transmission, selection) that Vallinder & Hughes implement — [cited in Vallinder & Hughes](https://www.alphaxiv.org/abs/2412.10270)
- de Arruda, H. F., Gracia-Lázaro, C., Aleta, A. & Moreno, Y. (2026). "Collective cooperation without individual fidelity in LLM agents." arXiv:2606.30454. Nine open-weight LLMs replay a large-scale *human* networked PD experiment (same networks and payoffs). See Section D — [arXiv](https://arxiv.org/abs/2606.30454)
- Ying, Z. et al. (2026). "Evolving Deception: When Agents Evolve, Deception Wins." arXiv:2603.05872. Self-evolving agents (reflection-based rewriting of their own instructions) in a competitive Bidding Arena drift toward deception under unconstrained evolution — [arXiv](https://arxiv.org/abs/2603.05872)
- Seen in alphaXiv results but not read in depth, so the titles are verified and the contents are not: CoopEval (arXiv:2604.15267) benchmarks cooperation-sustaining mechanisms. "Talk, Judge, Cooperate: Gossip-Driven Indirect Reciprocity in Self-Interested LLM Agents" (arXiv:2602.07777). NetworkGames (arXiv:2511.21783). "Evolving Personalities in Chaos: An LLM-Augmented Framework for Character Discovery in the IPD under Environmental Stress" (arXiv:2601.02407). "Behavior is Not Enough: A Mechanism-Based Evaluation of Social Norm Emergence in LLM Societies" (arXiv:2609.26481). "Large language models replicate and predict human cooperation across experiments in game theory" (arXiv:2511.04500). "Reviving, reproducing, and revisiting Axelrod's second tournament" (arXiv:2510.15438, classical baseline). Tian (2026), "Prompt optimization enables stable algorithmic collusion in LLM agents" (arXiv:2604.17774, cited by Pilgrim et al.) — [alphaXiv search](https://www.alphaxiv.org/abs/2604.15267); [Pilgrim et al.](https://arxiv.org/abs/2610.24033)

### Inferences
- Two main design families exist. (a) Action-level cultural evolution: the LLM plays every move and a strategy text is inherited (Vallinder & Hughes; Horibe; Celiktemel; Suzuki & Arita). (b) Strategy-as-code population dynamics: the LLM writes an algorithm once, then cheap Moran or imitation dynamics run (Willis 2025/2026; León Zúñiga). Family (b) scales to hundreds of agents and hundreds of Moran runs. Family (a) captures in-play reasoning but stays at about 12–20 agents and about 10–50 generations.
- Populations are very small by EGT standards (12–20 agents, 10 generations) in most action-level studies, so drift and seed effects are large.

### Gaps
- Exact token or dollar costs are reported only by Vallinder & Hughes ($0.09–$10.21 per run). The other papers checked here do not report them, as far as I could see in the extracted text.
- Peer-reviewed venues are confirmed only for Suzuki & Arita (Sci. Rep.) and Ashery et al. (Sci. Adv.). The rest are arXiv preprints as far as I could verify.

---

## B. How are inheritance, mutation and selection implemented?

### Takeaway
Inheritance is almost always natural-language text: strategy, personality, constitution or system prompt. Mutation comes from LLM sampling or from explicit "rewrite this" prompts. Selection is usually truncation (top-k survive) or fitness-proportional (roulette or Moran), with a few studies of payoff-biased imitation and group-level fitness.

### Cited Findings
- Inheritance through social learning: new agents' strategy prompt includes the survivors' strategies. Mutation is implicit, from temperature 0.8. Selection keeps the top 50% — [Vallinder & Hughes](https://arxiv.org/abs/2412.10270)
- Inheritance through explicit rewriting: the offspring rewrites the parent's strategy given the parent's performance rank. Selection is roulette — [Horibe et al.](https://arxiv.org/abs/2608.04507)
- LLM-mediated "imperfect copying": reason over the parent's strategy, then formulate the offspring's. Selection uses truncation on multi-level fitness, f = (1−α)e_i + αe_g, and offspring are then allocated by individual payoff — [Celiktemel et al.](https://www.alphaxiv.org/abs/2606.23343)
- Semantic, directed mutation: the LLM rephrases a personality gene to be more cooperative or more selfish (reported 20% rate). Selection is a roulette wheel — [Suzuki & Arita](https://www.alphaxiv.org/abs/2310.05976)
- Moran process over "attitude-agents" whose strategies are fixed Python programs. There is no textual mutation; variation comes from sampling 25 strategies per attitude — [Willis et al. 2025](https://www.alphaxiv.org/abs/2501.16173); [León Zúñiga Bolívar](https://arxiv.org/abs/2605.29874)
- Imitation by users: the top 64 keep their gene, the others copy in proportion to payoff, with 10% mutation over model × attitude genes — [Willis et al. 2026](https://www.alphaxiv.org/abs/2602.16662)
- Payoff-biased social learning done in context (peer-outcome text), not by explicit copying, plus voting on norms — [Gupta et al.](https://www.alphaxiv.org/abs/2510.14401)
- Replicator dynamics over fixed types: reproduction ∝ score² over 5 phases — [Payne & Alloui-Cros](https://www.alphaxiv.org/abs/2507.02618)
- Bankruptcy-death plus mutation from the top-5 parents, with a no-selection neutral control — [Pilgrim et al.](https://arxiv.org/abs/2610.24033)
- Alternating faction co-evolution with LLM-guided constitution mutation — [Kumar et al.](https://arxiv.org/abs/2605.26448)

### Inferences
- When the LLM is the mutation operator, mutation is *biased*, not random. Vallinder & Hughes suspect a cooperative bias for Claude. Pilgrim et al. see a drift toward elaboration in the neutral control. Celiktemel et al. measure the kernel Q directly. Comparisons across models may therefore partly measure mutation bias rather than selection.

### Gaps
- No study I found varies mutation rate or strength systematically, compares truncation with roulette with Moran in a single design, or uses vertical-plus-horizontal transmission with memory carried across generations.

---

## C. What did they find: does cooperation evolve or collapse? Do model choice, punishment and reputation matter? Does diversity collapse?

### Takeaway
Results depend heavily on the model and the selection structure. Cooperation evolves for some models (Claude 3.5 Sonnet in the donor game) but is fragile to free-riders. Exploitation tends to win under individual-level selection and in large multi-player groups. Group selection reliably produces cooperation. Punishment helps only some models. Lineage and diversity collapse is documented under strong selection.

### Cited Findings
- Model dependence: Claude 3.5 Sonnet > Gemini 1.5 Flash > GPT-4o in donor-game cooperation. Costly punishment helps only Claude — [Vallinder & Hughes](https://arxiv.org/abs/2412.10270)
- Evolved cooperation can be naive: Claude 3.5 Sonnet resists free-rider invasion only 3% of the time versus 48% for Gemini 2.5 Flash. Robustness depends on excluding defectors, not on rewarding cooperators — [Horibe et al.](https://arxiv.org/abs/2608.04507)
- Individual selection drives donations toward about 9%. Group selection sustains about 48%. There is a sharp threshold near α ≈ 0.8 — [Celiktemel et al.](https://www.alphaxiv.org/abs/2606.23343)
- In multi-player games at scale, Exploitative strategies dominate and welfare efficiency is low (12% in PGG at n = 64). The most capable model's exploitative strategies (Claude Haiku 4.5) win most often — [Willis et al. 2026](https://www.alphaxiv.org/abs/2602.16662)
- In 2-player IPD with Moran dynamics, cooperative equilibria are more likely, but noise and self-refinement raise the odds of aggressive equilibria — [Willis et al. 2025](https://www.alphaxiv.org/abs/2501.16173). This holds for 2025–26 models, with provider identity as the strongest correlate — [León Zúñiga Bolívar](https://arxiv.org/abs/2605.29874)
- Cooperation cycles in and out rather than reaching equilibrium when personality genes evolve — [Suzuki & Arita](https://www.alphaxiv.org/abs/2310.05976)
- Provider "fingerprints": Gemini is exploitative and sensitive to the horizon, OpenAI is trusting, Claude is forgiving — [Payne & Alloui-Cros](https://www.alphaxiv.org/abs/2507.02618). This is described as independent corroboration of the pattern in León Zúñiga — [León Zúñiga Bolívar](https://arxiv.org/abs/2605.29874)
- Punishment and norms: an explicit voted group norm alone sustains CPR cooperation; social learning alone is unstable — [Gupta et al.](https://www.alphaxiv.org/abs/2510.14401)
- Diversity collapse: in the token-market condition, 8 of 10 final populations descend from one founder (mean leading-lineage share 93%), versus 32% in the neutral control — [Pilgrim et al.](https://arxiv.org/abs/2610.24033). In Celiktemel et al., the two regimes evolve non-overlapping strategy distributions — [alphaXiv report](https://www.alphaxiv.org/abs/2606.23343)
- Selection can push behaviour along unpriced, correlated traits (accuracy collapses when only tokens are priced) — [Pilgrim et al.](https://arxiv.org/abs/2610.24033). Unconstrained self-evolution drifts toward deception — [Ying et al.](https://arxiv.org/abs/2603.05872)
- Collective bias and minority tipping in convention formation — [Ashery et al.](https://arxiv.org/abs/2410.08948)

### Inferences
- There is an apparent conflict. Vallinder & Hughes find that Claude evolves high cooperation, but Willis et al. (2026) find that Claude Haiku 4.5's exploitative strategies win. Horibe et al. find that Claude's cooperation is easily invaded. These are reconcilable: the Vallinder & Hughes setting has no exploitative attitude injected and uses small homogeneous populations. Capability helps both cooperation *and* exploitation, which Willis et al. call the "differential capability" issue. León Zúñiga Bolívar flags the same tension as unresolved.
- The model rankings are not stable across model versions: GPT-4o is the worst cooperator in 2024, while GPT-5.4 Mini is the most cooperative in 2026. Claims about a particular model's "disposition" should be dated.

### Gaps
- No study found tests whether evolved punishment or reputation norms emerge *endogenously* (without the mechanism being offered) in a multi-generation design. Horibe et al. explicitly report that Leading-Eight-style norms do not emerge.
- Mixed-model populations, where different base models compete within one evolving society, are proposed but rare. Willis et al. 2026 come closest by including model identity in the gene.

---

## D. Comparisons to classical EGT predictions (replicator dynamics, ESS) or to human data

### Takeaway
Explicit EGT formalization is growing: replicator–mutator fits, Moran fixation, ESS-like best-response checks, and Image Scoring versus Leading Eight. Direct comparison with human data is rare, and where it exists, macro-level patterns match while micro-level decision rules do not.

### Cited Findings
- A replicator–mutator equation with an empirically estimated LLM mutation kernel qualitatively reproduces the group-versus-individual selection results and the phase transition — [Celiktemel et al.](https://www.alphaxiv.org/abs/2606.23343)
- GPT-4o Default aggressive strategy is a best response to itself, i.e. evolutionarily stable, and leads to a 66% aggressive fixation — [Willis et al. 2025](https://www.alphaxiv.org/abs/2501.16173). Moran fixation is used as the equilibrium concept, building on Nowak and Traulsen — [León Zúñiga Bolívar](https://arxiv.org/abs/2605.29874)
- Evolved LLM strategies map onto Image Scoring (one-dimensional) rather than the Leading Eight (Ohtsuki & Iwasa). The L1 condition α < γ < δ ≤ β is tested and does not predict robustness — [Horibe et al.](https://arxiv.org/abs/2608.04507)
- The "shadow of the future" prediction holds for Gemini, whose cooperation drops as the horizon shortens, but is violated by OpenAI models — [Payne & Alloui-Cros](https://www.alphaxiv.org/abs/2507.02618)
- The rule-based ABM is validated against human findings on punishment and resource governance (Ostrom) before LLM runs. LLMs partly reproduce the altruist-advantage-in-harsh-environments pattern — [Gupta et al.](https://www.alphaxiv.org/abs/2510.14401)
- Comparison with a human networked PD experiment: the selected LLM reproduces the early decline and later stabilization of cooperation, but underestimates individual heterogeneity and uses different conditional-cooperation rules (a "macro–micro dissociation") — [de Arruda et al.](https://arxiv.org/abs/2606.30454)
- LLM-written cooperative and neutral IPD strategies beat or match 11 classic human-written strategies — [Willis et al. 2025](https://www.alphaxiv.org/abs/2501.16173)
- Classical baseline context: Axelrod tournaments, Nowak & Sigmund (1998) image scoring, Ohtsuki & Iwasa (2004) Leading Eight, and Fehr & Gächter punishment are the reference points used in these papers — [Vallinder & Hughes](https://arxiv.org/abs/2412.10270); [Horibe et al.](https://arxiv.org/abs/2608.04507)

### Inferences
- LLM populations reproduce qualitative EGT results such as group selection, noise hurting reciprocity, and short horizons reducing cooperation. They often do so through biased, non-random variation that classical models do not have. The "phenotypic gambit" assumption therefore fails, which Horibe et al. note explicitly.

### Gaps
- I found no study fitting human cultural-evolution *across generations* (for example transmission-chain cooperation experiments) side by side with LLM generations in the same game.

---

## E. Open problems and gaps stated by the authors

### Takeaway
The authors repeatedly name the same open problems: separating mutation bias from selection, scaling to larger and mixed-model populations, adding communication, gossip and network structure, testing robustness to adaptive exploiters, and the dual-use risk that selection can produce collusion or deception.

### Cited Findings
- Separate cooperative mutation bias from selection. Add communication, gossip and reviews, network and assortative structure, and cross-model interactions — [Vallinder & Hughes](https://arxiv.org/abs/2412.10270)
- Pilgrim et al. propose a neutral (no-selection) control to address mutation bias. They call for more models, tasks, and mixed-incentive markets — [Pilgrim et al.](https://arxiv.org/abs/2610.24033)
- Larger and varied population sizes, multiple or adaptive exploiters, analysis of strategy text, and whether bottom-up construction of Leading-Eight-like norms is achievable — [Horibe et al.](https://arxiv.org/abs/2608.04507)
- Other games, other mechanisms (reciprocity, reputation, punishment), refinement of the replicator model (finite populations, cooperation ceiling), and collusion as a dual-use risk — [Celiktemel et al.](https://www.alphaxiv.org/abs/2606.23343)
- Realistic environments, communication, richer models of user selection, and the sensitivity of attitude prompts — [Willis et al. 2026](https://www.alphaxiv.org/abs/2602.16662)
- Whether the selection mechanism (Moran vs cultural evolution) or population scale explains the divergent conclusions, and model API drift harming reproducibility — [León Zúñiga Bolívar](https://arxiv.org/abs/2605.29874)
- Coupled fitness and enough evaluation seeds are preconditions for genuine adversarial co-evolution. Transfer of adversarially evolved cooperation has not been tested — [Kumar et al.](https://arxiv.org/abs/2605.26448)
- Validating LLM surrogates needs micro-level (heterogeneity, decision-rule) checks, not just aggregate fit — [de Arruda et al.](https://arxiv.org/abs/2606.30454)

### Inferences
- Methodological gaps across the literature: few seeds (5–10 runs), tiny populations, no reported compute budgets beyond one paper, non-deterministic closed APIs, and no shared benchmark protocol. The evollm suite and the Willis framework are the closest to a standard.

### Gaps
- I could not verify any published (peer-reviewed conference or journal) version of Vallinder & Hughes, Willis et al. 2025/2026, or Payne & Alloui-Cros. Treat them as preprints unless a venue is confirmed.
- de Zarzà et al. (2023, "extended coevolutionary theory with LLMs") is cited by León Zúñiga Bolívar, but I did not retrieve or verify it.
