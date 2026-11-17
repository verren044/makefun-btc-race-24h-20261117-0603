# makefun-btc-race-24h-20261117-0603

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/verren044/makefun-btc-race-24h-20261117-0603/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/verren044/makefun-btc-race-24h-20261117-0603/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

Dip-buy bot for make.fun's Race a BTC trading bot live for 24 hours: it buys cbBTC after a 110 bps dip from the 60-bar lookback and exits on a 60 bps trailing stop, with a 100 bps take-profit and a 200 bps hard stop. Python 3.13, standard library only, fully deterministic.

## Run it

```sh
python3 -P -s main.py
```

## What it does

- Watches the close of each 1-minute bar of cbBTC against USDC.
- Buys the full cash stake when the close falls **110 bps below the highest
  close of the last 60 bars** (a dip buy).
- Exits the whole position on the first of:
  - **take profit:** the position is worth 100 bps over its cost;
  - **trailing stop:** the close falls 60 bps below the highest close since
    entry, once the position is at or above breakeven;
  - **hard stop:** the position is worth 200 bps below its cost (never fired
    on the dev window; tail protection for the race window).
- Orders fill at the next bar's open, per the harness. Max slippage 100 bps.

The bot reads newline-delimited JSON (`hello`, then one `batch` per bar,
then `done`) on stdin and writes exactly one `reply` per batch on stdout.
It uses only integer arithmetic, reads no clock, no environment, no files
outside its own directory, and seeds nothing — two runs on the same data
produce byte-identical replies.

`vendor/makefun_bars.py` is a byte-identical copy of the kit's Python SDK
shim (`sdk/makefun_bars.py`).

## Dev-window result (exact integer replica of the harness fill math)

- Net PnL: **+$19.37** (19,374,116 micro-USDC), 5 trades, max drawdown 1.22%
- Determinism: two full protocol runs produce byte-identical reply streams
  (sha256 `83b7ce06026db606acd472132c7f92ead1cc1907a4c260873912d78d5228dbb8`)
- Dev gate: passes (net PnL > $0). Guardrails: ≥1 trade, DD ≤ 25%.

See `DESIGN.md` for the strategy and grid search, `BUILD_LOG.md` for the
build steps and verification.

---

<sub>Entered on [make.fun](https://make.fun/?ref=vvz66fvh&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>
