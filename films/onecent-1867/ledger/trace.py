"""Copied from 8820/ledger/trace.py for #1867 (inscription 66001799, id ...b7i1), with the reveal output as argv[2]: an i1 inscription in a two-output reveal sits on output 1 (ord batch, separate outputs). Original: follow the satoshi carrying inscription 65907201 (Cent #8820) through Bitcoin's ledger via mempool.space.
Assumes the inscription sits on the first sat of output 0 of its reveal tx (the ord default, no pointer).
Each hop: find the input that spends the sat's output, its position among the spending tx's input sats,
then the output that position falls in (first-in-first-out, as ord assigns sats)."""
import json, sys, time, urllib.request, datetime
API = "https://mempool.space/api"
def get(path):
    req = urllib.request.Request(API + path, headers={"User-Agent": "cents-video-ledger-trace"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
        except Exception as e:
            if i == 3: raise
            time.sleep(2 ** i)
txid, vout, off = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0, 0
hops, cache = [], {}
tx = get(f"/tx/{txid}")
hops.append({"txid": txid, "kind": "reveal (inscribed)", "time": tx["status"].get("block_time"), "height": tx["status"].get("block_height"), "vout": vout, "address": tx["vout"][vout].get("scriptpubkey_address")})
for step in range(40):
    outs = get(f"/tx/{txid}/outspends")
    o = outs[vout]
    if not o.get("spent"): break
    nxt = o["txid"]; tx2 = get(f"/tx/{nxt}")
    pos = 0
    for vin in tx2["vin"]:
        if vin["txid"] == txid and vin["vout"] == vout: pos += off; break
        pos += vin["prevout"]["value"]
    else: sys.exit("input not found")
    cum = 0
    for j, out in enumerate(tx2["vout"]):
        if pos < cum + out["value"]: vout, off = j, pos - cum; break
        cum += out["value"]
    else:
        hops.append({"txid": nxt, "kind": "to fees", "time": tx2["status"].get("block_time")}); break
    txid = nxt
    hops.append({"txid": txid, "kind": "transfer", "time": tx2["status"].get("block_time"), "height": tx2["status"].get("block_height"), "vout": vout, "offset": off, "address": tx2["vout"][vout].get("scriptpubkey_address"), "value": tx2["vout"][vout]["value"]})
    time.sleep(0.5)
for h in hops:
    h["date"] = datetime.datetime.fromtimestamp(h["time"], datetime.timezone.utc).strftime("%Y-%m-%d %H:%M") if h.get("time") else None
json.dump(hops, open("hops.json", "w"), indent=1)
for h in hops: print(h["date"], h["kind"], h["txid"][:12], h.get("vout"), h.get("offset"), (h.get("address") or "")[:14], h.get("value"))
print(len(hops) - 1, "transfers after the reveal")
