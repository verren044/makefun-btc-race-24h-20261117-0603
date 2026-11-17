# Build log — btc-race-24h-20261117-0603

Built 2026-11-17 ~15:00–15:30 WIB (deadline 19:03 WIB). Build only: no
GitHub repo, push, bundle, kit-check, or submit (parent handles those).

## Steps

1. Read kit: `RULES.txt` (full), `competition.yaml`, `sdk/makefun_bars.py`,
   baselines `ema-cross` and `rsi-bollinger`. Dataset: 1,440 bars, 141 flat,
   BTC +53 bps open→close, range $63,874–$65,466, max 60-min drop 205 bps.
2. Read the harness fill math from `harness/sim/bars/engine.ts`
   (`barsBuyFill`, `barsSellFill`, `BarsPool`, `decide`, `resolve`,
   `flatten`, `stepTo`) and rebuilt it as an exact integer replica in
   `/tmp/btcr/replica.py` (not in the entry dir).
3. Sanity-checked the replica: buy-and-hold +$1.07 / 1 trade / DD 2.12%;
   hold-cash $0.00 / 0 trades — both as expected from the raw price move
   minus round-trip costs.
4. Grid-searched five strategy families on the replica (see DESIGN.md).
   Winner: dip-buy, L=60, drop=110 bps, trail=60 bps, take-profit=100 bps.
5. Wrote `main.py` fresh in this session (v1: entry + take-profit +
   breakeven-gated trailing exit), vendored the kit Python shim
   byte-identical under `vendor/` (`cmp` clean).
6. Drove the real `main.py` subprocess through the full protocol
   (hello → 1,440 batches → done) with the exact engine math
   (`/tmp/btcr/driver.py`): net PnL **+$19.374116**, 5 trades,
   max DD 1.22%, fees $2.43. Two runs byte-identical.
7. Revision (separate edit): added `STOP_BPS = 200` hard stop. Re-ran the
   driver twice: identical results and identical reply-stream hash —
   the stop never fires on dev, as designed.
8. Tried `grade-local --driver process`: kit verified (29 files), dataset
   re-derived (1,440 bars from 42,798 samples), then refused —
   "the process sandbox runs node22 only (python3.13 runs only inside
   Docker)"; Docker is not installed here, so the official local grade
   cannot run for Python. The protocol drive in step 6–7 is the
   verification.

## Verification numbers (final)

- Dev net PnL: **+$19.374116** (19,374,116 micro-USDC) — gate passes (>$0)
- Trades: **5** (guardrail ≥1: passes)
- Max drawdown: **1.2158%** (guardrail ≤25%: passes)
- Fees paid: $2.430198
- Determinism: reply-stream sha256, run 1 and run 2:
  `83b7ce06026db606acd472132c7f92ead1cc1907a4c260873912d78d5228dbb8`
  (identical, 1,440 replies each)
- Runtime per full-window run: ~0.2 s wall (far inside the 1,800 s budget)

## Files in the entry dir

- `main.py` — the bot (Python 3.13, stdlib only)
- `vendor/makefun_bars.py` — kit SDK shim, byte-identical copy
- `README.md`, `DESIGN.md`, `BUILD_LOG.md` (this file), `LICENSE` (MIT)
