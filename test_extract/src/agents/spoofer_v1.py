"""

Spoofer V1 Agent for BSE Trading

This module implements a sophisticated spoofing agent that manipulates the
Widrow-Hoff margin adaptation mechanism in the BSE. The agent uses a
state machine with three states:

- IDLE: Normal selling behavior, monitors best bid and probabilistically
        triggers attacks when favorable conditions exist.
- ATTACK: Aggressively undercuts the limit price. Under the Widrow-Hoff
          learning rule, ZIP buyers observe this low-price trade and lower
          their bids (assuming the seller is cheap).
- COOLDOWN: Submits passive orders at elevated prices to wait out the
            market reaction, then returns to IDLE.


The exploitation works because:
1. The aggressive bid in ATTACK triggers ZIP's loss-driven margin increase
2. ZIP buyers then submit bids at higher prices
3. The spoofer captures these higher bids at the limit price in COOLDOWN
"""

import sys
import os
import random
from typing import Optional, Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bse'))
from BSE import Trader, Order


class SpooferV1(Trader):
    """
    A spoofing agent that exploits ZIP buyer margin adaptation.

    Uses a three-state machine to:
    1. Detect favorable bidding conditions (IDLE)
    2. Submit aggressive orders to trigger margin increases (ATTACK)
    3. Exploit elevated prices with passive orders (COOLDOWN)
    """

    def __init__(
        self,
        ttype: str,
        tid: str,
        balance: float,
        params: Optional[Dict[str, Any]] = None,
        time: int = 0
    ) -> None:
        """
        Initialize the SpooferV1 agent.

        Args:
            ttype: Trader type (should be 'Seller' for this strategy)
            tid: Unique trader identifier
            balance: Initial balance
            params: Configuration dict with keys:
                - attack_prob: float, default 0.15
                - cooldown_duration: int, default 25
                - passive_margin: float, default 0.05
            time: Current simulation time
        """
        super().__init__(ttype, tid, balance, params, time)

        # Extract parameters with defaults
        if params is None:
            params = {}
        self.attack_prob: float = params.get('attack_prob', 0.15)
        self.cooldown_duration: int = params.get('cooldown_duration', 25)
        self.passive_margin: float = params.get('passive_margin', 0.05)

        # State machine variables
        self.state: str = 'IDLE'
        self.cooldown_timer: int = 0

        # Analytics tracking
        self.n_attacks: int = 0
        self.attack_log: List[Dict[str, Any]] = []

    def getorder(
        self,
        time: int,
        countdown: int,
        lob: Dict[str, Any]
    ) -> Optional[Order]:
        """
        Generate the next order based on current state and market conditions.

        Args:
            time: Current simulation time
            countdown: Time until market closure
            lob: Limit order book with structure:
                {'bids': {'best': price or None}, 'asks': {'best': price or None}}

        Returns:
            Order object if one should be submitted, None otherwise
        """
        # Safety: no orders to fulfill
        if not self.orders:
            return None

        # Extract order details
        limit: float = self.orders[0].price
        otype: str = self.orders[0].otype

        # State machine logic
        if self.state == 'IDLE':
            price = self._idle_state(limit, lob, time)
        elif self.state == 'COOLDOWN':
            price = self._cooldown_state(limit)
        else:
            price = int(round(limit))

        price = max(int(round(limit)), price)

        order = Order(self.tid, otype, price, 1, time, self.n_quotes)
        self.n_quotes += 1

        return order

    def _idle_state(self, limit: float, lob: Dict[str, Any], time: int) -> int:
        """
        IDLE state: normal selling with probabilistic attack triggering.

        Returns to IDLE if no attack is triggered.
        Transitions to ATTACK if:
        - Best bid exists
        - Best bid >= limit price
        - Random trigger fires (probability = attack_prob)
        """
        best_bid: Optional[float] = lob['bids']['best']

        # Check attack trigger conditions
        if (best_bid is not None and
                best_bid >= limit and
                random.random() < self.attack_prob):
            self.state = 'ATTACK'
            # Pass best_bid down to attack_state for logging
            price = self._attack_state(limit, time, best_bid)
        else:
            price = int(round(limit))

        return price

    def _attack_state(self, limit: float, time: int, best_bid: float) -> int:
        """
        ATTACK state: aggressively undercut to trigger margin adaptation.

        Submits order at limit price (not below to avoid losses).
        Immediately transitions to COOLDOWN.
        Logs the attack for analysis.
        """
        # Submit at limit (aggressive relative to expected margins)
        price = int(round(limit))

        self.state = 'COOLDOWN'
        self.cooldown_timer = self.cooldown_duration

        self.n_attacks += 1
        self.attack_log.append({
            'time': time,
            'price': price,
            'limit': limit,
            'best_bid': best_bid  # Added to log
        })

        return price

    def _cooldown_state(self, limit: float) -> int:
        """
        COOLDOWN state: submit passive orders at elevated prices.

        Submits at limit * (1 + passive_margin).
        Decrements timer each call.
        Transitions to IDLE when timer reaches 0.
        """
        # Passive price with margin
        price = int(round(limit * (1 + self.passive_margin)))

        # Decrement cooldown timer
        self.cooldown_timer -= 1

        # Transition back to IDLE when cooldown expires
        if self.cooldown_timer <= 0:
            self.state = 'IDLE'

        return price

    def respond(
        self,
        time: int,
        lob: Dict[str, Any],
        trade: Any,
        verbose: bool = False
    ) -> None:
        """
        Respond to trades. SpooferV1 is rule-based and requires no adaptation.

        Args:
            time: Current simulation time
            lob: Current limit order book
            trade: Trade information
            verbose: Verbosity flag (unused)
        """
        pass
