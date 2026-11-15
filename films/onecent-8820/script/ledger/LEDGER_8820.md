# The satoshi carrying Cent #8820's image, on Bitcoin's ledger

Traced 2026-11-15 from mempool.space (public API), for the line "Bitcoin's ledger records each transfer of the satoshi that carries its image". ordinals.com, ordiscan and api.hiro.so are blocked here, so the sat was followed by hand: `trace.py` starts at the reveal transaction of inscription 65907201 (id `9c5d9cddc271d702d5ac367ebacd631ee045476e018e358da70b18a0ab23ecfbi0`), assumes the inscription sits on the first sat of output 0 (the ord default), and at each spend places the sat by first-in-first-out order, as ord does. Output: `hops.json`.

| UTC | Step | Transaction | Sat goes to |
|---|---|---|---|
| 2024-03-26 03:00 | inscribed (reveal) | 9c5d9cddc271… | bc1p7t7pmnztlk… |
| 2024-03-26 17:27 | transfer | 199c3c71b0ad… | bc1pdg5cf6r69h… |
| 2026-11-06 15:14 | transfer | 04caecf8d2c9… | bc1psfrtev263e… |
| 2026-11-06 15:33 | transfer | 7e3eb18a6a1f… | bc1puw6m4j9pqw… |
| 2026-11-14 11:05 | transfer | 8c1d156e822a… | bc1pn7dugln7t6… |
| 2026-11-14 11:05 | transfer | ff215cc7c060… | bc1ppsdngx9frf… (now) |

Five transfers after the reveal. The last output was unspent when traced.

## Checked against a source the trace didn't use

cents.vision's wallet index (`collectors/snapshots/*/raw/wallet_index_cents.json`, fetched separately for the Collector Wall work) names #8820's holder on three dates. Each matches a hop, in full address:
- 2026-10-27 snapshot: bc1pdg5cf6r69h… = hop 1
- 2026-11-09 snapshot: bc1puw6m4j9pqw… = hop 3
- 2026-11-14 snapshot (fetched 18:51Z, after the 11:05Z transfer): bc1ppsdngx9frf… = hop 5

Control: in every hop's transaction the other outputs pay other addresses (the 14 Nov transaction has 21 inputs and 6 outputs), so a wrong sat placement would have named a different holder and failed this comparison.

## What this says, and what it doesn't

- On 14 Nov 2026 the satoshi moved to bc1ppsdngx9frf…, which cents.vision's `wallet-groups.json` lists as a secondary wallet of the Wall named **Daidatep** (signature Cent #9908). Daidatep included #8820 in their list when DOPEMIND asked what to add (What to add next, ep. 1).
- The 6 Nov and 14 Nov transactions each also pay the previous holder's address, which looks like a sale. This note does not say so as fact, and gives no amounts (no prices in the films).
- Times are block times. Addresses are shortened here; full ones are in `hops.json`.
