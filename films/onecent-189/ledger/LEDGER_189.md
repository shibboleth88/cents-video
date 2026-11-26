# Cent #189: the satoshi's path through Bitcoin's ledger

Inscription 66001226, id `92359bf66d518264f041c0838e99c7103be1db833ab2323c1ed436dd48acbb74i0` (output 0 of its reveal).
Traced 2026-11-26 with `trace.py` (copied from #1867, which keeps #8820's first-in-first-out sat tracking) via mempool.space:
`python3 -I trace.py 92359bf66d518264f041c0838e99c7103be1db833ab2323c1ed436dd48acbb74 0` (in this folder). Output: `hops.json`.

| Date (UTC) | Transaction | Kind |
|---|---|---|
| 2024-03-27 01:39 | 92359bf66d51 | reveal (inscribed) |
| 2024-03-27 08:27 | 0fc719e0f8f2 | transfer (to the reveal address again) |
| 2024-03-28 10:46 | 1ab265842851 | transfer |
| 2024-12-06 16:53 | 8ea313674b85 | transfer |
| 2025-06-30 09:29 | a6c64c23e7e3 | transfer |
| 2025-06-30 09:29 | 817e651055d0 | transfer (same block) |
| 2025-07-28 01:44 | aadc83405eaa | transfer |
| 2025-09-21 22:47 | 5a066613910c | transfer |
| 2025-09-21 22:47 | 6964dcd7e681 | transfer (same block) |
| 2026-02-28 05:22 | d0a03e93bb59 | transfer |
| 2026-11-23 04:14 | 5b18a85a4cb1 | transfer |
| 2026-11-23 04:14 | 4d0876db442f | transfer (same block); unspent at the trace |

**11 transfers after the reveal, as of 26 Nov 2026.** A transfer is a Bitcoin transaction that moved the satoshi; it is not necessarily a sale or a change of owner (two pairs share a block, and the first goes back to the reveal address). The film shows dates and short transaction ids only, no addresses and no prices, under "exchange".

**Not cross-checked.** The Hiro ordinals API refused (403) and ordinals.com is bot-blocked, so this path rests on the trace alone. The same tracer agreed with cents.vision's wallet index on five dates for #1867.
