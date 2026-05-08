## Day 2 Session Notes

### Design decisions carried forward
- SpooferV1 = Momentum Igniter (not passive spoofer) — terminology locked
- Cohen's d = 2.30 on 5 seeds: enormous effect, but n too small for significance
- Primary stat: paired t-test. Welch's = robustness check only.

### v2 design rationale 
-### V2 Q-Learning: The "Irrational Seller" Paradigm
- **Observation:** Under a pure profit-maximizing reward function ($Profit = Trade\_Price - Limit$), the Q-learning spoofer converged on a maximum Q-value of 0.0, learning only to HOLD or safely WITHDRAW. It refused to aggressively spoof the limit book.
- **Scientific Conclusion:** A rational, single-sided seller has no economic incentive to induce a downward flash crash via aggressive undercutting, because crossing the spread annihilates their own profit margin.
- **The Adversarial Pivot:** To successfully model crash propagation, the agent's objective function had to be explicitly inverted to an adversarial model ($Reward = 90.0 - Trade\_Price$). Once incentivized purely by market damage rather than personal profit, the agent successfully learned to aggressively spoof, generating positive Q-values (>1.2) and successfully dragging mean prices down to ~85.
- 