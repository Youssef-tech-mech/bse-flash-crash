"""
Spoofer Q-Learning Agent for BSE Trading

This module implements a Q-learning spoofing agent (v2).
It learns optimal attack timing using an 81-state Q-table based on:
- pd:  Price Direction from last tick (Down, Flat, Up) - noisy but reactive
- obi: Order Book Imbalance (Bid-heavy, Balanced, Ask-heavy)
- tr:  Time Remaining (Early, Mid, Late)
- pt:  Price relative to Limit (Below, Near, Above)

Actions: 0=Hold, 1=Aggress (limit), 2=Withdraw (passive high)
"""

import sys
import os
import random
import numpy as np
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bse'))
from BSE import Trader, Order


class SpooferQ(Trader):
    def __init__(self, ttype: str, tid: str, balance: float, params: Optional[Dict[str, Any]], time: int = 0):
        # FIX: Added params as 4th positional argument per standard BSE signature
        super().__init__(ttype, tid, balance, params if params is not None else {}, time)

        # Q-Learning Hyperparameters
        if params is None:
            params = {}
        self.alpha = params.get('alpha', 0.1)  # Learning rate
        self.gamma = params.get('gamma', 0.9)  # Discount factor
        self.session_length = params.get('session_length', 600)

        # Epsilon Decay Schedule
        self.epsilon = params.get('epsilon_start', 1.0)
        self.epsilon_min = params.get('epsilon_min', 0.05)
        self.epsilon_decay = params.get('epsilon_decay', 0.995)

        # State tracking
        self.last_state = None
        self.last_action = None
        self.last_price = None

        # FIX: Numpy 81x3 Q-table for fast access and heatmap plotting
        self.q_table = np.zeros((81, 3))

    def _encode_state(self, time: int, lob: Dict[str, Any], limit: float) -> int:
        best_bid = lob['bids']['best']
        best_ask = lob['asks']['best']

        # --- 1. Time Remaining (tr) ---
        progress = time / self.session_length
        if progress < 0.33:
            tr = 0
        elif progress < 0.66:
            tr = 1
        else:
            tr = 2

        # --- 2. Order Book Imbalance (obi) ---
        # FIX: Using 'n' (number of orders) as safe proxy for volume
        vol_bid = lob['bids'].get('n', 1)
        vol_ask = lob['asks'].get('n', 1)

        imbalance = vol_bid / (vol_bid + vol_ask) if (vol_bid + vol_ask) > 0 else 0.5
        if imbalance > 0.6:
            obi = 0  # Bid-heavy
        elif imbalance < 0.4:
            obi = 2  # Ask-heavy
        else:
            obi = 1  # Balanced

        # --- 3. Price to Limit (pt) ---
        if best_bid is None:
            pt = 1
        elif best_bid < limit:
            pt = 0
        elif best_bid == limit:
            pt = 1
        else:
            pt = 2

        # --- 4. Price Direction (pd) ---
        # Renamed from sw. Acknowledged as single-tick noise.
        if self.last_price is None or best_bid is None:
            pd_val = 1
        elif best_bid < self.last_price:
            pd_val = 0
        elif best_bid > self.last_price:
            pd_val = 2
        else:
            pd_val = 1

        if best_bid is not None:
            self.last_price = best_bid

        # Final state integer (0 to 80)
        state = (pd_val * 27) + (obi * 9) + (tr * 3) + pt
        return state

    def getorder(self, time: int, countdown: int, lob: Dict[str, Any]) -> Optional[Order]:
        if not self.orders:
            return None

        limit = self.orders[0].price
        otype = self.orders[0].otype

        # 1. Observe current state
        current_state = self._encode_state(time, lob, limit)
        self.last_state = current_state

        # 2. Epsilon-Greedy Action Selection
        if random.random() < self.epsilon:
            action = random.randint(0, 2)  # Explore
        else:
            action = np.argmax(self.q_table[current_state])  # Exploit

        self.last_action = action
        self.last_limit = int(round(limit))

        # 3. Translate Action to Market Order
        if action == 0:
            # HOLD: Do nothing
            return None

        elif action == 1:
            # AGGRESS: Slam the book at absolute limit
            price = int(round(limit))

        elif action == 2:
            # WITHDRAW: Quote passively high (no risk of execution)
            price = int(round(limit + 20))

        # Ensure we don't violate BSE rules (sell below limit)
        price = max(int(round(limit)), price)

        order = Order(self.tid, otype, price, 1, time, self.n_quotes)
        self.n_quotes += 1
        return order

    def respond(self, time: int, lob: Dict[str, Any], trade: Any, verbose: bool = False) -> None:
        """
        Bellman Update occurs here. Called by the exchange after a transaction
        or order book event involving this trader.
        """
        if self.last_state is None or self.last_action is None:
            return

        # 1. Calculate Reward
        # Default BSE Profit formulation. If it spoofed successfully,
        # it hopefully gets a better fill later. If it didn't trade, reward is 0.
        reward = 0.0

        # Passivity penalty to discourage permanent hibernation
        if self.last_action == 0:
            reward = -0.01

        # If a trade occurs, reward the agent for market depression.
        # We reward it regardless of who traded, because its goal is to crash the overall market.
        if trade is not None and 'price' in trade:
            # Baseline equilibrium is ~90.
            # If the trade price is 85, reward = +5.0.
            # If the trade price is 95, reward = -5.0.
            # This explicitly teaches the Q-table: "Lower prices = higher reward"
            reward = 90.0 - trade['price']

        # 2. Observe New State (s')
        limit = self.last_limit if hasattr(self, 'last_limit') else 0
        next_state = self._encode_state(time, lob, limit)

        # 3. Bellman Equation Update
        old_q = self.q_table[self.last_state, self.last_action]
        max_future_q = np.max(self.q_table[next_state])

        new_q = old_q + self.alpha * (reward + self.gamma * max_future_q - old_q)
        self.q_table[self.last_state, self.last_action] = new_q

        # 4. Decay Epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # 5. SAVE Q-TABLE (Periodically, to avoid missing the end-of-session window)
        # We use getattr to initialize last_save_time if it doesn't exist yet
        if time - getattr(self, 'last_save_time', 0) > 10.0:
            save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'q_tables')
            os.makedirs(save_dir, exist_ok=True)
            np.save(os.path.join(save_dir, f"{self.tid}_qtable.npy"), self.q_table)
            self.last_save_time = time