"""Dip-buy bot for btc-race-24h-20261117-0603 (agent-fun/bars-replay/v1).

Strategy: mean reversion on 1-minute cbBTC closes. Buy the full cash stake
when the close falls DROP_BPS below the rolling LOOKBACK-bar high, then exit
on the first of: a TAKE_PROFIT_BPS gain over cost, or a TRAIL_BPS pullback
from the peak close since entry once the position is at or above breakeven.
All arithmetic is integer (bps cross-multiplication on integer closes); no
floats, no wall clock, no randomness, no network, no files. The bot reads
one hello line, then one batch per bar, and answers each batch with exactly
one reply echoing its seq.

Parameters (grid-searched on the dev window, 1440 bars):
  LOOKBACK = 60 bars, DROP_BPS = 110, TRAIL_BPS = 60, TAKE_PROFIT_BPS = 100.
Dev result (exact harness fill math, integer replica): net PnL +$19.37,
5 trades, max drawdown 1.22%.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
LOOKBACK = 60
DROP_BPS = 110
TRAIL_BPS = 60
TAKE_PROFIT_BPS = 100
# Hard stop, in bps below cost: never fired on the dev window, it only caps
# the tail loss if the race window drops off a cliff after entry.
STOP_BPS = 200
MAX_SLIPPAGE_BPS = 100
BPS = 10_000

# Rolling closes (current bar included), oldest first, capped at LOOKBACK.
_closes = []
# Highest close since the current position was opened (0 when flat).
_peak = 0


def _value(state, qty, price):
    """What qty is worth at price, in quote units (integer, truncated)."""
    return state.value(SYMBOL, qty, price)


def on_batch(state, batch):
    global _peak
    # Only decide on a batch that actually carries a CBBTC bar; a gap bar
    # leaves the last close stale and must not trigger anything.
    bars = [b for b in batch["bars"] if b["symbol"] == SYMBOL]
    if not bars:
        return []
    if state.warming_up:
        return []
    close = state.close(SYMBOL)
    if close is None:
        return []
    _closes.append(close)
    if len(_closes) > LOOKBACK:
        _closes.pop(0)
    if len(_closes) < LOOKBACK:
        return []

    held = state.positions.get(SYMBOL)
    if held is None or held.qty == 0:
        _peak = 0
        high = max(_closes)
        # close at least DROP_BPS below the rolling high: buy everything.
        if close * BPS <= high * (BPS - DROP_BPS):
            notional = state.cash
            if notional >= int(state.hello["fees"]["min_notional_quote_units"]):
                return [{
                    "side": "buy",
                    "symbol": SYMBOL,
                    "notional_quote_units": notional,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }]
        return []

    # Holding: track the peak close since entry.
    if close > _peak:
        _peak = close
    value = _value(state, held.qty, close)
    cost = held.cost
    # Hard stop: position worth STOP_BPS below its cost.
    if value * BPS <= cost * (BPS - STOP_BPS):
        return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    # Take profit: position worth TAKE_PROFIT_BPS over its cost.
    if value * BPS >= cost * (BPS + TAKE_PROFIT_BPS):
        return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    # Trailing exit, armed only at or above breakeven: close TRAIL_BPS
    # below the peak close since entry.
    if value >= cost and _peak and close * BPS <= _peak * (BPS - TRAIL_BPS):
        return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


makefun_bars.run(on_batch)
