# Design — dip-buy cbBTC bot

## Market read (dev window, 1,440 1-min bars, ends 2026-11-17T06:03Z)

- BTC roughly flat over the window: open $64,433.84 → close $64,775.95
  (+53 bps). Range $63,874–$65,466 (~2.5%).
- 141 flat bars. Largest 60-min drop 205 bps. Total absolute 1-min moves
  5,545 bps — a ranging market with a few sharp pullbacks, not a trend.
- Round-trip cost ≈ 26–28 bps (4 bps fee + 2 bps slippage each way, plus
  ~10–13 bps of pool impact per leg at dev depths), so a trade must catch
  a move well above ~30 bps to clear costs.

## Strategy

Mean reversion on closes, all integer bps math:

1. **Entry.** Rolling high = max close of the last 60 bars (current bar
   included). Buy the full cash stake when the close is ≥110 bps below
   that high.
2. **Take profit.** Sell all when the position is worth ≥100 bps over cost.
3. **Trailing exit.** Sell all when the close falls ≥60 bps below the peak
   close since entry — armed only once the position is at or above
   breakeven, so a dip that keeps falling is not sold into weakness at a
   small loss (the hard stop covers the tail instead).
4. **Hard stop.** Sell all when the position is worth ≥200 bps below cost.
   Never fired on dev; tail protection for the race window.
5. Orders carry `max_slippage_bps = 100`. No order on a batch with no
   CBBTC bar, no order while warming up, no order before 60 closes.

## Grid search (exact integer replica of the harness fill math)

Families tested on the full dev window: dip-buy, EMA cross, RSI/Bollinger,
breakout, momentum.

| Family | Best dev PnL | Trades | Max DD |
| --- | --- | --- | --- |
| dip-buy (fine grid) | +$21.31 | 6 | 1.22% |
| momentum | +$1.05 | 2 | 0.69% |
| breakout | −$4.85 | 9 | 2.45% |
| RSI/Bollinger | −$6.95 | 7 | 1.97% |
| EMA cross | −$106.21 | 68 | 10.96% |

EMA cross churns badly on 1-min noise (68 trades, −$106). RSI/Bollinger
and breakout never clear costs. Dip-buy is the only family that clears
the gate with margin.

Fine dip-buy grid (L × drop × trail, full-size single tranche): the
+L$17–22 region spans L 45–90, drop 110–125 bps, trail 60–75 bps,
take-profit 75–200 bps — a broad positive plateau, not a knife edge.
Neighbouring points: L60/d110/t60/tp75 +$21.31, tp100 +$19.37, tp200
+$22.34, tp0 +$17.77; L90/d125/t75/tp100 +$20.50; L45/d110/t60/tp100
+$18.76. The chosen centre point (L=60, drop=110, trail=60, tp=100)
is inside that plateau. Split-half check: first half +$11.65,
second half +$2.21 (L45/d100/t50 variant); the chosen config is
positive in 4 of 6 four-hour blocks.

Rejected variants: trailing exit armed always (no breakeven gate)
−$15.33 — selling every 60 bps pullback while underwater bleeds;
50/50 two-tranche sizing +$9.05 vs +$17.77 full-size; 100 bps hard
stop +$7.82 (cuts winners short).

## Final parameters

| Parameter | Value |
| --- | --- |
| `LOOKBACK` | 60 bars |
| `DROP_BPS` | 110 |
| `TRAIL_BPS` | 60 |
| `TAKE_PROFIT_BPS` | 100 |
| `STOP_BPS` | 200 |
| `MAX_SLIPPAGE_BPS` | 100 |

Dev result: net PnL **+$19.37**, 5 trades, max drawdown **1.22%**,
fees $2.43. Final position (bought bar 1099) flattened at the last close.

## Relation to the sibling entry

The 2026-11-15 sibling (btc-race-24h-20261115-0828) won its dev window
with a dip-buy (60-bar lookback, 210–275 bps triggers, 75 bps trailing).
That was treated as a hypothesis only: this window's pullbacks are
shallower (max 60-min drop 205 bps), so the grid re-derived the trigger
from scratch and landed at 110 bps / 60 bps trailing / 100 bps take
profit. No code was copied; `main.py` was written fresh in this session.
