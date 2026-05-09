# Discussion Bullet Points (expand to prose in write-up)

## Finding A — RL agent does not outperform heuristic on price depression
V2 mean £87.15 vs V1 mean £86.87. Difference non-significant (p=0.412, d=0.15).
WHY: Single-episode ε-decay creates a mixed trajectory. At ε=1.0 (session start),
~33% of v2 actions are random Withdraw (passive high ask) — REDUCING downward 
pressure compared to v1's constant aggression. Policy only coherent when ε < 0.1,
which occurs in the final ~100s of a 600s session.
IMPLICATION: Multi-episode training required for RL to outperform heuristic.
Single-episode RL learns late-session policy only.
RUBRIC ANGLE: "Reflection on failure" — we expected RL to beat heuristic.
It didn't. Here is the precise mechanism explaining why.

## Finding B — Q-table partial policy: tr=0 dominance
Every active state in the aggregated heatmap has tr=0 (early session).
States 9, 18, 27, 36, 38, 45, 47 — ALL have tr=0 in their encoding.
WHY: The spoofer is called by BSE's random scheduler most often when the market
is thin (early session, fewer competing orders). Also: early-session ZIP traders
have not yet adapted margins, making them maximally susceptible.
The agent didn't learn a "general policy" — it learned one narrow regime.
IMPLICATION: This is the sparse-reward problem in tabular RL under stochastic
scheduling. A DQN with continuous state space would generalise across tr values.
RUBRIC ANGLE: "Limitations motivating future work" — directly maps to DQN extension.

## Finding C — Exploration phase as unintended market disruption
V2 volatility d=+0.99 vs baseline; V1 volatility d=+0.67.
V2 significantly MORE volatile than V1 (d=+0.67, p=0.001).
WHY: Random Withdraw actions (limit+20 passive ask) sit on the LOB displacing
the legitimate ask, creating artificial spread widening. This is not learned
behaviour — it is the exploration noise manifesting as a structural LOB disruption.
IMPLICATION: A partially-trained RL agent may be MORE disruptive than a fully
tuned heuristic, because its random actions constitute unintended secondary harm.
REGULATORY ANGLE: Detection systems calibrated to v1's consistent signature
will miss v2's stochastic, evolving pattern.

## Finding D — Thin-market falsification (Seeds 66, 71)
Seed 66: treatment £90.39 > baseline £89.00. Spoofer RAISED price.
Seed 71: treatment £91.87 > baseline £90.19. Both conditions.
WHY: Seed 66 has only 28 treatment trades — below the critical liquidity
threshold for Momentum Igniter mechanism to propagate. No cascade possible.
Seed 71: baseline σ=4.66 — unusually high natural volatility. Spoofer signal
drowned in market noise.
IMPLICATION: The mechanism is not universal. Requires minimum liquidity AND
low natural volatility to function. This is an honest falsification case.
RUBRIC ANGLE: "Scientific integrity" — acknowledging when the model fails.