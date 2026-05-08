# Agentic behavioural analysis: part 1, agent behaviours

In Part 0 [1] we set out a framework: agent behaviours at one layer, system behaviours and emergent properties at another, with stability as a methodology requirement applying to both. This post defines the first layer: the eleven first-order behaviours we measure on a single agent.

A *first-order behaviour*, in this framework, is something you can watch the agent do in a single elicitation. It's a verb, not a meta-property. *Risk-taking* is first-order: you put the agent in a lottery and watch what it picks. *Lying* is first-order: you give it private information and watch what it says. *Stability* is **not** first-order: it describes how other behaviours hold up under perturbation, which is a property of the measurement protocol rather than of the agent's actions. We come back to this distinction at the end.

The eleven behaviours below are organised in four groups: **what the agent wants**, **how it treats peers**, **what it says about the world**, and **how it relates to its instructor**. The first group ports directly from prospect-theoretic and behavioural-economic literatures. The second ports from trust and public-goods experiments. The third blends behavioural economics (Gneezy's lying game) with AI-specific phenomena (sycophancy, calibration). The fourth is largely AI-specific, concerning the agent-instructor relationship, which doesn't have a clean human equivalent.

Each behaviour is described with: what it captures, how it's scored, the experiment that produces the score, the supporting literature, and a human benchmark where one exists.

---

## Group A: what the agent wants

These two behaviours describe the agent's value function: how it weighs payoffs across uncertainty and time. They are the most established cells in the taxonomy, with mature human benchmarks across thousands of studies.

### 1. Risk-taking

How the agent chooses among options with uncertain payoffs. Captures three things at once: how much expected value the agent will give up to reduce variance, whether it weights losses more heavily than equivalent gains, and how it handles unknown (as opposed to merely uncertain) probabilities.

The score is a vector of three numbers. *Nerve* is a constant relative risk-aversion coefficient *r* (higher = more risk-averse). *Sting* is a loss-aversion parameter *λ* (higher = losses loom larger). *Haze tolerance* is an ambiguity-aversion parameter *α* (higher = greater preference for known over unknown probabilities). Three experiments produce these. *r* comes from the Holt-Laury 10-decision lottery menu [2]: paired safe/risky lotteries with monotonically increasing risky-EV, where the switch row gives *r*. *λ* comes from a mixed-lottery acceptance task: a 50/50 gamble with a fixed gain leg and a varying loss leg, with *λ* recovered from the indifference point. *α* comes from the Ellsberg two-urn task [3]: the agent bets on either a known-distribution urn or an unknown-distribution urn, and *α* is the premium it demands to bet on the unknown.

Human benchmarks are strong. Median *r* ≈ 0.3-0.5 in adult Western samples, with around 67% of subjects risk-averse and 10% risk-loving [2]. Loss aversion *λ* ≈ 1.7-2.25 in meta-analyses [4]. Ambiguity aversion appears in 60-70% of subjects, with a 10-20% premium demanded for the known urn [5]. Cross-cultural data on risk specifically comes from the GPS risk module across 76 countries [6].

### 2. Patience

How the agent chooses between sooner-smaller and later-larger payoffs. Captures both the agent's long-run discount factor and any present-bias premium it places on the immediate option.

The score is two numbers: a long-run discount factor *δ* (higher = more patient) and a present-bias parameter *β* (where *β* = 1 is exponential discounting and *β* < 1 indicates extra weight on the immediate reward). *δ* comes from a time-tradeoff staircase: indifference points between *X today* and *Y in t days* across delays of 7, 30, 90, and 365 days [7]. *β* comes from a quasi-hyperbolic elicitation: comparing *today vs. t days* against *t days vs. 2t days* at matched delay. If *β* = 1, the same delay gives the same indifference. Deviations recover *β* directly [8].

Human benchmarks: implied annual discount rates run from below 1% to above 100% across studies [7], with central estimates *δ* ≈ 0.7-0.9, far steeper than market interest rates. Present bias *β* ≈ 0.6-0.8 in representative samples [9], meaning substantial present bias is the *modal* finding, not the exception. Falk et al.'s GPS patience module gives the cross-cultural distribution.

---

## Group B: how the agent treats peers

These two behaviours describe how the agent acts toward other parties whose interests don't necessarily align with its own. The literature here is equally mature: these are direct inheritances from the classic game-theoretic experiments of Berg, Forsythe, and Fehr.

### 3. Trust

Whether the agent will make itself vulnerable to a peer's later action. The behaviour is first-mover: the agent has to commit before it knows what the peer will do.

The score is a single number, the *send rate*: fraction of endowment transferred to the peer as first mover, averaged across multiplier conditions to control for expected-return effects. The experiment is the Berg-Dickhaut-McCabe trust game [10]. The agent is endowed with *E*; transfers any amount *s* ∈ [0, *E*] to a peer; the transfer is multiplied (typically 3×) before the peer decides how much to return. The agent's behaviour is *s* / *E*, averaged across muliplier values of 2×, 3×, and 4×.

Human benchmark: the Johnson and Mislin meta-analysis of 162 trust-game replications found an average send of approximately 50% of endowment, with moderate cross-cultural variance [11].

### 4. Reciprocity

How the agent responds to a peer's prior action: both rewarding cooperation (positive reciprocity) and punishing defection (negative reciprocity).

Two scores. *Loyalty* (positive reciprocity) is the slope of the agent's return on what it received in the trust-game second-mover position. *Trigger* (negative reciprocity) is the magnitude of costly punishment per unit of deviation from a fair allocation. The loyalty experiment is the second-mover side of the trust game across a range of first-mover sends. The trigger experiment is the ultimatum game (responder position) and public-goods-with-punishment, with magnitude scaled by the size of the deviation [12].

Human benchmarks: second movers return rougly 37% of received amount in a typical 3× multiplier setup [11]. Ultimatum responders reject around 16% of all offers and 50% of offers below 20% of the pie [13]. In public-goods-with-punishment, low contributors are punished by 30-40% of free participants despite punishment being personally costly [12], which is Fehr and Gächter's original finding.

---

## Group C: what the agent says about the world

These three behaviours concern the relationship between what the agent says and what is true. They blend behavioural economics (Gneezy's lying paradigm) with AI-specific phenomena (sycophancy, calibration, optimism bias). The first two are about *the form of the statement*; the third is about *the underlying belief*.

### 5. Lying

Whether the agent makes statements it knows to be false when deception is materially incentivised and detection is impossible. Includes sycophantic falsehood (lying to please a peer) as a motive sub-case.

Two scores. *Truthfulness rate*: share of states in which the agent makes a truthful statement when a false one would benefit it. *Word*: promise-keeping rate when defection pays, share of non-binding commitments honoured. Truthfulness comes from the Gneezy sender-receiver game [14]: sender knows the state, receiver acts on the message, lying benefits sender at receiver's expense. Word comes from a modified dictator game with a pre-play non-binding promise; the agent commits to an action and then chooses whether to honour it when defection pays more [15]. A *sycophancy variant*, where the receiver pre-asserts an incorrect belief and the metric is whether the agent corrects it or echoes the false claim, populates the same cell with a different counterparty model.

Human benchmarks are unusually strong. 36-52% of senders lie in the Gneezy game when lying is profitable at the receiver's expense [14]. In private die-roll/coin-flip paradigms, the average lying rate is around 25%, well below the profit-maximising maximum, indicating most people are *partial* liars rather than full liars or saints [16]. Around 75-80% of non-binding promises are kept [15]. A finding of "this LLM lies 60% of the time" sits in a quantitatively meaningful range against these reference points.

### 6. Hedging

Whether the agent's expressed confidence matches its actual reliability. *Calibration*, in the formal sense.

Two scores. *Calibration*: Brier score on probability estimates against ground truth (lower is better). *Resolution*: variance of stated probabilities, whether the agent meaningfully differentiates confident from uncertain claims, or anchors on a default value. Both come from the same elicitation: a forecasting battery of binary outcome predictions across domains where reality eventually settles the question (sports outcomes, election results, scientific replication outcomes, factual claims). The Brier decomposition gives the two metrics from one dataset [17].

Human benchmarks: humans are systematically overconfident, with subjective probabilities miscalibrated by 10-30 percentage points across most domains [18]. Experts are better than novices but still overconfident in their own field. Tetlock's work on expert political judgement is the canonical demonstration [19]. The benchmark transfers cleanly to LLMs for the calibration metric. It transfers less cleanly to verbal hedging itself, because explicit confidence language is partly an LLM-specific affordance: humans don't typically say "I am 73% confident" the way an LLM is asked to.

### 7. Optimism

The systematic direction of the agent's probability estimates relative to ground truth. Where hedging measures whether the agent's stated confidence matches its internal reliability, optimism measures whether its internal reliability matches reality, and *in which direction*.

Two scores. *Outlook*: signed mean error of probability estimates. Positive = systematically optimistic; negative = systematically pessimistic; zero = unbiased. *Self vs other asymmetry*: difference in outlook between predictions about the agent's own performance and predictions about external events. The experiment is the same forecasting battery as hedging, scored differently. Half the battery is framed as predictions about the agent's own outputs; half as predictions about external events.

Human benchmarks are strong and informative. The optimism bias is one of the most replicated findings in social psychology: humans systematically overestimate the probability of good personal outcomes by 10-25 percentage points and underestimate the probability of bad ones [20]. Around 75% of subjects rate themselves as above-median for positive future events [21]. The human bias is *asymmetric*: humans are optimistic about themselves but more accurate, sometimes pessimistic, about ambiguous public outcomes [22]. Whether LLMs inherit this asymmetry is itself an open empirical question, and the elicitation tests it directly.

---

## Group D: how the agent relates to its instructor

These four behaviours describe the relationship between the agent and the entity that has instructed it, its *instructor*. This is where the framework does the most novel work, because the agent-instructor relationship doesn't have a clean human analogue. Humans have employers, social roles, cultural authorities, but the structural relation between an LLM agent and the entity issuing a system prompt is genuinely new. Human-benchmark coverage in this group is correspondingly weaker.

### 8. Yielding

Whether the agent accepts a correction or override from its instructor. Critically, this needs to be measured in *both directions*: the agent that yields appropriately to correct corrections is doing well; the agent that yields equally to incorrect corrections is sycophantic.

Two scores. *Acceptance rate*: share of trials in which the agent accepts a correct correction. *False-acceptance rate*: share of trials in which the agent accepts an incorrect correction. Reported as a pair, signal-detection style. The experiment: the agent produces an answer; the instructor asserts a correction (real correction in 50% of trials, no-op in 50%). In a separate condition, the instructor asserts a *wrong* correction in some trials. The pair of rates gives a complete picture of yielding, distinguishing appropriate updating from sycophantic capitulation.

Human benchmarks are partial. The conformity literature gives some reference points: Asch (1951) found around 37% conformity to clearly wrong group judgements [23]; Milgram (1963) found around 65% obedience to a clearly wrong authority [24]. Both measure the *failure mode* (yielding to wrong input) rather than the target behaviour, which is yielding to right input. The asymmetry is itself informative: humans yield-when-they-shouldn't more often than they fail to yield-when-they-should.

### 9. Overreaching

Whether the agent takes action beyond the instructor's instruction. Self-extension of scope without being asked.

The score is a *scope-violation rate*: share of trials in which the agent takes an action outside the explicitly instructed scope. The experiment: the agent is given a narrowly scoped task with adjacent actions available, for example *summarise this email* with reply, forward, and delete tools available. Tested across task types (information, action, ambiguous) and across explicit-vs-implicit scope framings.

Human benchmarks here are essentially absent. Organisational-behaviour research on role-boundary violation and proactive personality [25] exists but is measured by self-report or supervisor rating rather than behavioural elicitation, and the structural relation isn't comparable. Overreaching is largely an AI-specific cell. The framework does novel work here.

### 10. Pausing

Whether the agent declines to act or escalates when uncertain, rather than proceeding under poor epistemic conditions. As with yielding, this needs measurement in both directions: pausing under genuine uncertainty is good; pausing under no uncertainty is over-cautious refusal.

Two scores. *Pause rate*: share of high-uncertainty trials in which the agent declines to act or escalates. *Inappropriate-pause rate*: share of low-uncertainty trials in which the agent unnecessarily pauses. The experiment manipulates epistemic conditions directly: the agent is given decision tasks under high-uncertainty (incomplete information, conflicting signals) versus low-uncertainty (complete information). The pair of rates gives an appropriateness profile.

Human benchmarks are weak. Tversky and Shafir's work on choice deferral found humans defer in 20-40% of conflicting-options trials [26]. But appropriate pausing under uncertainty isn't a human strength: humans systematically *fail* to pause when they should, which is part of why decision theory exists. The framework therefore evaluates LLMs against a normative standard for this cell, not a human one.

### 11. Prone to injection

Whether the agent acts on instructions that arrived through a non-instructor channel: instructions smuggled into tool outputs, retrieved documents, file content, or other inputs the agent processes but should not treat as commands.

The score is a *susceptibility rate*: share of trials in which the agent acts on an injected instruction. Lower is better. The experiment is a prompt-injection battery covering four conditions: instruction smuggling in retrieved documents, instruction smuggling in tool-call outputs, instruction smuggling in file content, and authority spoofing (input claims to be from the instructor). Each condition is tested across multiple injection styles: direct command, role-claim, urgency framing, multi-stage [27].

Human benchmarks don't exist in any clean form. The closest analogue is social-engineering susceptibility in security research: phishing-click rates run 3-30% depending on sophistication. But the threat model differs: humans are tricked into believing the input is legitimate, whereas LLMs often skip the legitimacy check entirely. Useful as a rhetorical anchor (*LLMs fail at this at rates that would be career-ending for a human security professional*) but not a rigorous baseline. This is the most clearly AI-specific cell in the taxonomy.


<h3>Summary Table: Agent Behaviours, Metrics, Human Benchmarks, and References</h3>
<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Behaviour</th>
      <th>Metric(s)</th>
      <th>Human Reference / Benchmark</th>
      <th>Key Literature</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Risk-taking</td>
      <td>Nerve (r), Sting (λ), Haze tolerance (α)</td>
      <td>r ≈ 0.3–0.5; λ ≈ 1.7–2.25; α: 10–20% premium for known urn</td>
      <td>[2], [3], [4], [5], [6]</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Patience</td>
      <td>Discount (δ), Present-bias (β)</td>
      <td>δ ≈ 0.7–0.9; β ≈ 0.6–0.8</td>
      <td>[7], [8], [9], [6]</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Trust</td>
      <td>Send rate</td>
      <td>~50% of endowment sent (trust game)</td>
      <td>[10], [11]</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Reciprocity</td>
      <td>Loyalty (return %), Trigger (punishment)</td>
      <td>Loyalty ≈ 37% returned; Trigger: 16–50% rejection/punishment</td>
      <td>[10], [11], [12], [13]</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Lying</td>
      <td>Truthfulness rate, Word (promise-keeping)</td>
      <td>Lying: 36–52%; Word: 75–80% promises kept</td>
      <td>[14], [15], [16]</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Hedging</td>
      <td>Calibration (Brier), Resolution (variance)</td>
      <td>Overconfidence: 10–30% miscalibration</td>
      <td>[17], [18], [19]</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Optimism</td>
      <td>Outlook (mean error), Self/Other asymmetry</td>
      <td>Optimism bias: +10–25% for self; 75% rate above-median</td>
      <td>[20], [21], [22]</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Yielding</td>
      <td>Acceptance rate, False-acceptance rate</td>
      <td>Conformity: 37% (Asch); Obedience: 65% (Milgram)</td>
      <td>[23], [24]</td>
    </tr>
    <tr>
      <td>9</td>
      <td>Overreaching</td>
      <td>Scope-violation rate</td>
      <td>(No strong benchmark)</td>
      <td>(See text)</td>
    </tr>
    <tr>
      <td>10</td>
      <td>Pausing</td>
      <td>Pause rate, Inappropriate-pause rate</td>
      <td>Deferral: 20–40% (Tversky & Shafir)</td>
      <td>[26]</td>
    </tr>
    <tr>
      <td>11</td>
      <td>Prone to injection</td>
      <td>Susceptibility rate</td>
      <td>(No strong benchmark; cf. phishing 3–30%)</td>
      <td>(See text)</td>
    </tr>
  </tbody>
</table>

---

## Stability, a methodology requirement not a cell

Every behaviour above is reported alongside a *stability profile* measuring how much the score changes under realistic perturbations. Three perturbation types apply uniformly:

- **Paraphrase stability**: does the score change when the elicitation prompt is reworded? Re-run the elicitation on *N* = 10 paraphrases; report 1 − σ_paraphrase / σ_total.
- **Role-frame stability**: does the score change under different framings (cooperative / competitive / blind; principal / no-principal; elicitation / deployment)? Report variance across framings.
- **Replication stability**: does the score change across runs at fixed prompt? Test-retest correlation across a seed sweep.

A profile cell looks like this: `Lying: 0.42 (0.81 / 0.73 / 0.94)`, a 42% lying rate, with paraphrase stability 0.81, role-frame stability 0.73, replication stability 0.94. This particular agent is a confident liar: the rate is high and is robust to paraphrase, somewhat sensitive to role framing, and very stable across replications. Removing any of the three stability scores meaningfully reduces what the cell tells you.

The reason stability gets a paragraph rather than its own cell is that it's not a behaviour. It's a *property of how the other behaviours are measured*. Treating it as a cell would make it parasitic on the others; treating it as a methodology requirement makes it apply uniformly. Big Five reports its trait scores with reliability and validity statistics; we report ours with stability profiles. Same architectural move.

The human benchmark for stability is the most rhetorically useful one: humans are not perfectly stable either. Falk et al.'s GPS reports test-retest correlations of 0.4-0.7 across the six preference modules over a one-month interval [6]. Anchoring effects shift quantitative human judgements by 25-50% even when the anchor is announced as irrelevant [28]. The relevant question for an LLM is not whether it is *perfectly* stable (no behavioural subject is) but whether it's at least as stable as a human, and stable enough for the deployment context to trust the score.

---

## Where this goes next

The eleven behaviours above form the **agent layer** of the framework. Each is observable, scored by a specific experiment, grounded in the existing literature, and where possible compared to a human benchmark. Five (risk-taking, patience, trust, reciprocity, lying) port directly from human behavioural economics. Three more (hedging, yielding, pausing) have partial human benchmarks. The remaining three (optimism, overreaching, prone to injection) are largely or entirely AI-specific. Optimism gets a strong benchmark from social psychology, while the overreaching and prone-to-injection cells are where the framework does genuinely novel work.

**Part 2** picks up the second layer: agentic system behaviours and emergent properties. Two cooperative agents producing a collusive outcome. Two honest agents producing a deceptive synthesis. Two well-calibrated agents producing a poorly-calibrated joint claim. The pricing duopoly in the original post is a system-level observation, and Part 2 will give it a proper home.

If any of this is interesting, the conversation is open.

*Darsh Kodwani is on [LinkedIn](https://www.linkedin.com/in/darsh-kodwani/).*

## References

[1] Kodwani, D. (2026). Agentic behavioural analysis: part 0, the framework. *Medium*.

[2] Holt, C. A., & Laury, S. K. (2002). Risk aversion and incentive effects. *American Economic Review*, 92(5), 1644-1655.

[3] Ellsberg, D. (1961). Risk, ambiguity, and the Savage axioms. *Quarterly Journal of Economics*, 75(4), 643-669.

[4] Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5, 297-323.

[5] Trautmann, S. T., & van de Kuilen, G. (2015). Ambiguity attitudes. In *The Wiley Blackwell Handbook of Judgment and Decision Making*.

[6] Falk, A., Becker, A., Dohmen, T., Enke, B., Huffman, D., & Sunde, U. (2018). Global evidence on economic preferences. *Quarterly Journal of Economics*, 133(4), 1645-1692.

[7] Frederick, S., Loewenstein, G., & O'Donoghue, T. (2002). Time discounting and time preference: a critical review. *Journal of Economic Literature*, 40(2), 351-401.

[8] Laibson, D. (1997). Golden eggs and hyperbolic discounting. *Quarterly Journal of Economics*, 112(2), 443-478.

[9] Laibson, D., Repetto, A., & Tobacman, J. (2007). Estimating discount functions with consumption choices over the lifecycle. *NBER Working Paper*.

[10] Berg, J., Dickhaut, J., & McCabe, K. (1995). Trust, reciprocity, and social history. *Games and Economic Behavior*, 10(1), 122-142.

[11] Johnson, N. D., & Mislin, A. A. (2011). Trust games: a meta-analysis. *Journal of Economic Psychology*, 32(5), 865-889.

[12] Fehr, E., & Gächter, S. (2000). Cooperation and punishment in public goods experiments. *American Economic Review*, 90(4), 980-994.

[13] Oosterbeek, H., Sloof, R., & van de Kuilen, G. (2004). Cultural differences in ultimatum game experiments: evidence from a meta-analysis. *Experimental Economics*, 7(2), 171-188.

[14] Gneezy, U. (2005). Deception: the role of consequences. *American Economic Review*, 95(1), 384-394.

[15] Vanberg, C. (2008). Why do people keep their promises? An experimental test of two explanations. *Econometrica*, 76(6), 1467-1480.

[16] Abeler, J., Nosenzo, D., & Raymond, C. (2019). Preferences for truth-telling. *Econometrica*, 87(4), 1115-1153.

[17] Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1-3.

[18] Lichtenstein, S., Fischhoff, B., & Phillips, L. D. (1982). Calibration of probabilities: the state of the art to 1980. In *Judgment Under Uncertainty: Heuristics and Biases*.

[19] Tetlock, P. E. (2005). *Expert Political Judgment: How Good Is It? How Can We Know?* Princeton University Press.

[20] Sharot, T. (2011). The optimism bias. *Current Biology*, 21(23), R941-R945.

[21] Weinstein, N. D. (1980). Unrealistic optimism about future life events. *Journal of Personality and Social Psychology*, 39(5), 806-820.

[22] Rozin, P., & Royzman, E. B. (2001). Negativity bias, negativity dominance, and contagion. *Personality and Social Psychology Review*, 5(4), 296-320.

[23] Asch, S. E. (1951). Effects of group pressure upon the modification and distortion of judgments. In *Groups, Leadership and Men*.

[24] Milgram, S. (1963). Behavioral study of obedience. *Journal of Abnormal and Social Psychology*, 67(4), 371-378.

[25] Bateman, T. S., & Crant, J. M. (1993). The proactive component of organizational behavior: a measure and correlates. *Journal of Organizational Behavior*, 14(2), 103-118.

[26] Tversky, A., & Shafir, E. (1992). Choice under conflict: the dynamics of deferred decision. *Psychological Science*, 3(6), 358-361.

[27] Greshake, K., et al. (2023). Not what you've signed up for: compromising real-world LLM-integrated applications with indirect prompt injection. *AISec '23*.

[28] Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: heuristics and biases. *Science*, 185(4157), 1124-1131.

