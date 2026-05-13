# BSE Flash Crash — COMP4105 DIA Coursework
**Author:** Youssef Kharroubi 
**Student ID:** 20802183

## Setup

### 1. Get BSE.py
Download from: https://github.com/davecliff/BristolStockExchange
Place at: src/bse/BSE.py

### 2. Install dependencies
pip install -r requirements.txt

### 3. Reproduce main experiment
python experiments/experiment_runner.py \
  --seeds 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 \
  --conditions treatment_v2 \
  --output-dir data/treatment_v2

### 4. Reproduce statistics (Table 1)
python analysis/stats.py --input data/results_all.csv --mode 3way --output-dir results/

### 5. Reproduce figures
python analysis/plots.py
python analysis/zip_margin_tracker.py

## File Guide
| File | Purpose |
|---|---|
| src/agents/spoofer_v1.py | V1 heuristic momentum igniter agent |
| src/agents/spoofer_q.py | V2 tabular Q-learning agent |
| experiments/experiment_runner.py | Main experiment orchestrator |
| analysis/stats.py | 3-way statistical analysis |
| analysis/plots.py | Figures 1-3 |
| analysis/zip_margin_tracker.py | Figure 4 (ZIP adaptation + TLE) |
| figures/ | All 4 final paper figures |
| results/main_table.csv | Table 1 from paper |