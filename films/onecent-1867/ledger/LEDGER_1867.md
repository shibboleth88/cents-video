# The satoshi carrying Cent #1867's image, on Bitcoin's ledger

Traced 2026-11-25 from mempool.space (public API) for the closing line ("set again each time someone reads it, keeps it or lets it go"). `trace.py` is #8820's tracer with one change: the reveal output is an argument. Inscription 66001799 has id `d8c47645…e886b7i1`; its reveal transaction has two outputs of 546 sats, so the i1 inscription sits on the first sat of output 1 (ord's batch mode with separate outputs). At each spend the sat is placed first-in-first-out, as ord does. Output: `hops.json`.

| UTC | Step | Transaction |
|---|---|---|
| 2024-03-27 01:51 | inscribed (reveal), output 1 | d8c47645713b… |
| 2024-03-27 17:31 | transfer | 73a9632d8f17… |
| 2024-03-28 09:10 | transfer | d6b2f703f4d2… |
| 2024-04-17 08:13 | transfer | b704c695147e… (unspent when traced) |

Three transfers after the reveal, ~~all within three weeks of it~~; the same wallet has held it since 17 April 2024 (as of 25 November 2026).

*Correction, 2026-11-25 (22:50Z):* "all within three weeks" was false. Measured from the timestamps above, the transfers came 15 h 40 min, 1 d 7 h 19 min and 21 d 6 h 22 min after the reveal, so the third falls just over three weeks after it (and 19 d 23 h after the second). Accurate wordings: "twice in its first two days, and once more on 17 April 2024", or "three times by 17 April 2024".

## Checked against a source the trace didn't use

cents.vision's wallet index (`/mnt/project-files/collectors/snapshots/<date>/raw/wallet_index_cents.json`) names #1867's holder on five dates (2026-10-25, 10-27, 11-09, 11-14, 11-15). All five name the address of the last hop, in full.

**Limit of this check.** In the 17 April 2024 transaction the sat's address also receives two other outputs, so the snapshots confirm the holder, not the exact output. In the 27 March transaction likewise (two others). The 28 March transaction pays each address once.

## Rules for the plate

Dates and shortened transaction ids only. No addresses (presentation rule: wallet addresses never go on screen) and no amounts (no prices in the films).
