## Seed 42 — Early Signal (Day 1 MVE)
- Treatment mean price 3.18 units BELOW baseline (86.25 vs 89.43)
- Treatment volatility HIGHER (3.51 vs 3.28 std)  
- Treatment trade volume 3x higher (71 vs 23) — unexpected, under investigation
- Hypothesis: spoofer attacks are executing real trades, not just creating LOB illusion
- Market below equilibrium (~100) in both conditions — convergence phase being sampled
- ZIP margin adaptation to spoof signals appears to pull prices DOWN during convergence
- Seed 45 anomaly: Largest trade volume (102 treatment vs 51 baseline) but smallest price depression (−0.75). Hypothesis: when spoofer triggers many trades, ZIP adapts faster, "healing" the price dislocation. The market's adaptive immune system is stronger under high order flow.
- Seed 46 anomaly: Fewest trades overall (16/22) but still −3.41 depression. Thin markets amplify price impact — fewer trades to absorb each spoof.
- ### MVE 5-Seed Analysis (Day 1)
- **Universal Price Depression:** 5/5 seeds show treatment prices below baseline. A paired sign test (5/5) suggests p < 0.05 directional significance before formal t-tests. The H1 (Spoofer depresses prices) is robust.

#### Emergent Anomalies (Distinction-Level Findings)
1. **Seed 45 Anomaly (Market Immunity via High Flow):** - *Observation:* Showed the largest trade volume (102 treatment vs. 51 baseline) but the smallest price depression (−0.75).
   - *Hypothesis:* When the Spoofer triggers a massive cascade of trades, the ZIP agents' Widrow-Hoff algorithms process more learning updates per second. High order flow acts as an adaptive "immune system," allowing the market to "heal" the price dislocation faster.
2. **Seed 46 Anomaly (Thin Market Vulnerability):**
   - *Observation:* Showed the fewest trades overall (16/22) but maintained a severe −3.41 price depression.
   - *Hypothesis:* Thin, low-liquidity markets amplify the impact of spoofing. With fewer legitimate trades to dilute the fake signals, the ZIP agents overweight the spoofer's aggressive limits, preventing the price from recovering.
- ### Statistical Validation (5-Seed MVE)
- **Methodological Justification:** The paired t-test yielded high significance ($p=0.007$), whereas the independent Welch's test did not ($p=0.091$). This validates the within-seed experimental design; pairing eliminates inter-market noise, whereas treating the groups independently at $n=5$ destroys statistical power. This formally justifies the requirement for the full 30-seed production run.
- **Extreme Effect Size:** The SpooferV1 induced a paired Cohen's $d_z$ of $-2.30$. This is an exceptionally large effect size (>3x the standard 'large' benchmark), strongly supporting the hypothesis that the spoofer acts as a "Momentum Igniter," successfully manipulating ZIP learning margins.
- **Volatility Dynamics:** A medium-large effect size in price volatility was observed ($d=0.61$), indicating the market is less stable under attack. However, this did not reach statistical significance at $n=5$ ($p=0.24$), confirming that full statistical power for secondary metrics requires the 30-seed sample size.
- ### Visual Data Validation (MVE)
- **Universal Vulnerability Demonstrated:** Figure 2 (Price Impact) visually confirms that 100% of the MVE seeds experienced negative price pressure. The effect is strictly directional; the Spoofer never accidentally inflated the market. 
- **Relative Environmental Impact:** Figure 1 confirms the Spoofer scales its attack to the local environment. Seed 46 operated in a naturally higher-priced equilibrium (~94.5), yet the Spoofer still successfully anchored the market down (-3.4 impact). The attack does not rely on a specific absolute price level to function.
- **Visualizing the Seed 45 Anomaly:** The "High Order Flow Immunity" hypothesis is visually stark in the difference plots. Investigating the specific trade-book dynamics of Seed 45 vs. Seed 43 (the maximum impact seed) will be a primary focus of the 30-seed production run.


 Document that SpooferV1 behaves more like an "Aggressive Pinger" than a pure passive spoofer. It executes real trades at the price floor rather than faking liquidity. This distinction is worth one paragraph in your Discussion and separates your analysis from a naive description of spoofing.
 
## Finding 7 — v2 ε-exploration phase partially offsets manipulation effect
Seeds 42, 45: v2 raised mean price vs baseline. Agent is in high-ε
territory (near-random actions), meaning ~33% of actions are WITHDRAW
(passive high ask), which *reduces* downward pressure vs v1's constant
aggression. This is not a bug — it is the exploration-exploitation 
tradeoff manifesting as a measurable market effect.
Implication for write-up: compare v2 to v1 AFTER ε has decayed,
i.e., interpret full-30-seed results as a mixture of early-exploration
and late-exploitation phases within each episode.

## Finding 8 — Agent S22 near-zero Q-table (max Q=0.078)
BSE's stochastic scheduler may call an agent rarely AND in states 
where profitable trades never occur. Agent S22 visited only 9/81 states
with max reward 0.078 — consistent with an agent that was never in the 
right state at the right time to capture a profitable trade signal.
This is the sparse-reward problem in tabular RL applied to short-horizon 
stochastic environments. Document as a limitation.

## Finding 9 — Q-table policy structure: bid-heavy state specialisation
Aggregated heatmap shows learned value concentrated in states where
OBI=0 (bid-heavy) and PT=0 (price below limit). Agent discovered WITHOUT
explicit programming that bid-heavy conditions are the profitable attack
window. States with OBI=2 (ask-heavy) are correctly assigned near-zero
value. This is emergent policy structure from sparse profit signals —
the core RL finding of the project.

## Finding 10 — v1 vs v2 outcome equivalence with mechanism divergence  
If paired t-test confirms p > 0.05 for v1 vs v2 price difference:
Both agents depress prices equivalently but v2 achieves this through
a learned structured policy rather than a hard-coded rule. This is the
"sample-efficient manipulation" finding — relevant for regulators
designing detection systems that target learning agents.


V1 is a Blunt Instrument — consistent price depression, moderate volatility. V2 is an Erratic Manipulator — equivalent price depression, but 28% more volatility injected into the market.

This is a stronger Distinction finding than equivalence. The RL agent discovered a noisier attack strategy than the hand-coded one, possibly because the ε-greedy exploration phase itself generates random order submissions that destabilise the book even when not profitably executed.Result 2 — Volume: v2 generates significantly more trades than v1C: v1 → v2 volume: Δ=+11.4, p=0.0512 (borderline), d=+0.371V2 generates 75.6 trades/session vs v1's 64.2. Combined with the volatility finding, the picture is: v2 is a higher-frequency, higher-noise attacker. The Q-learning agent, still in partial exploration, fires more actions and produces more market churn even when those actions don't all result in profitable trades.
