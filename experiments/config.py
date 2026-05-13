# Bristol Stock Exchange (BSE) — Cliff (2018)
# "BSE: A Minimal Simulation of a Limit-Order-Book Stock Exchange"
# EMSS 2018. Source: https://github.com/davecliff/BristolStockExchange
import sys, os
# Add src/bse directly so BSE.py is importable as a flat module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'bse'))
import BSE  # then use BSE.Order, BSE.Trader, BSE.market_session