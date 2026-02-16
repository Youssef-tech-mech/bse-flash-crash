# BSE Flash-Crash: Spoofing Agents in the Bristol Stock Exchange

MSc Intelligent Agents (COMP4105) — University of Nottingham, 2025-26

## Research Question

> Can a spoofing agent induce flash-crash-like price dislocations in a
> simulated limit-order-book market populated by adaptive ZIP traders,
> and does a Q-Learning spoofing strategy outperform a rule-based
> heuristic at destabilising the market?

## Project Structure
```
bse-flash-crash/
├── src/
│   ├── bse/              # BSE integration (third-party, download separately)
│   ├── agents/           # Custom spoofing agents (v1 heuristic, v2 Q-Learning)
│   └── utils/            # Metrics: volatility, spread, flash-crash detection
├── experiments/           # Config and experiment runner scripts
├── analysis/              # Post-hoc analysis and figure generation
├── tests/                 # Unit tests
├── data/                  # Raw CSV outputs (git-ignored, regenerated)
├── figures/               # Plots and charts (git-ignored, regenerated)
└── docs/                  # Notes and report drafts
```

## Quick Start
```bash
# 1. Clone and enter
git clone <your-repo-url>
cd bse-flash-crash

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download BSE (not included — third-party, MIT licence)
curl -o src/bse/BSE.py https://raw.githubusercontent.com/davecliff/BristolStockExchange/master/BSE.py

# 5. Run experiments
python experiments/experiment_runner.py

# 6. Generate figures
python analysis/generate_figures.py
```

## Experiments

| # | Question | Conditions |
|---|----------|------------|
| 1 | Baseline volatility | ZIP-only market (control) |
| 2 | Does Spoofer v1 increase volatility? | ZIP + rule-based spoofer |
| 3 | Does Spoofer v2 increase volatility? | ZIP + Q-Learning spoofer |
| 4 | v1 vs v2 comparison | Head-to-head effectiveness |
| 5 | Sensitivity to spoofer population | 1, 2, 3 spoofers among ZIP |

Each experiment uses 30 seeded trials with Welch's t-test / Mann-Whitney U
and Cohen's d effect size for statistical rigour.

## Attribution

The Bristol Stock Exchange (BSE) is by Dave Cliff, University of Bristol.
Licensed under MIT. [Repository](https://github.com/davecliff/BristolStockExchange).

All other code in this repository is original work.

## Licence

MIT