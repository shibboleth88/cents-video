"""Counts for One Cent #1867, from the Sep 2026 trait export (knowledge/data/cents_traits_sep2026.json).
Floors: each count must clear a floor known from the data README or an earlier episode, so a broken
reader cannot pass as an empty pool. Run: python3 -I films/onecent-1867/script/counts.py"""
import json, collections, sys
T = json.load(open('/mnt/project-files/knowledge/data/cents_traits_sep2026.json'))
assert len(T) == 10000, len(T)
def prof(c): return tuple(sorted(k for k, v in c.items() if v is True)) + tuple(sorted(c.get('contaminated') or []))
def has(c, k): return c.get(k) is True
def contam(c, s): return s in (c.get('contaminated') or [])
anyv = lambda c: any(has(c, g + '_verdigris') for g in ('notable', 'significant', 'full'))
anyo = lambda c: any(has(c, g + '_obsidian') for g in ('notable', 'significant', 'full'))
me = T['1867']
out = collections.OrderedDict()
out['1867 year, mark, inscription'] = (me['year'], me['mint_mark'], me['inscription_number'], me['unique_id'])
out['1867 profile'] = prof(me)
out['significant_obsidian'] = sum(has(c, 'significant_obsidian') for c in T.values())
out['significant_verdigris'] = sum(has(c, 'significant_verdigris') for c in T.values())
both = sorted(int(n) for n, c in T.items() if has(c, 'significant_obsidian') and has(c, 'significant_verdigris'))
out['both significant'] = len(both)
alien = sorted(int(n) for n, c in T.items() if contam(c, 'Alien Secretion'))
out['Alien Secretion'] = len(alien)
out['Alien Secretion with any verdigris'] = sum(anyv(T[str(n)]) for n in alien)
out['verdigris any (whole set)'] = sum(anyv(c) for c in T.values())
out['same profile as 1867'] = sorted(n for n, c in T.items() if prof(c) == prof(me))
C = collections.Counter(prof(c) for c in T.values())
out['unique profiles (floor: 436 in stories FINDINGS)'] = sum(1 for k in C.values() if k == 1)
out['1964 all / no mark / D'] = (sum(c['year'] == 1964 for c in T.values()), sum(c['year'] == 1964 and not c['mint_mark'] for c in T.values()), sum(c['year'] == 1964 and c['mint_mark'] == 'D' for c in T.values()))
out['1964 Lustrous-only templates'] = sorted(n for n, c in T.items() if c['year'] == 1964 and prof(c) == ('lustrous',))
for k, v in out.items(): print(f'{k}: {v}')
# floors (data README: verdigris 1,884; stories FINDINGS: 436 unique profiles)
assert out['verdigris any (whole set)'] == 1884, 'verdigris floor'
assert out['unique profiles (floor: 436 in stories FINDINGS)'] == 436, 'profile floor'
assert out['same profile as 1867'] == ['1867']
print('floors ok')
if '--pools' in sys.argv:
    json.dump({'both_significant': both, 'alien': alien,
               'significant_obsidian': sorted(int(n) for n, c in T.items() if has(c, 'significant_obsidian')),
               'significant_verdigris': sorted(int(n) for n, c in T.items() if has(c, 'significant_verdigris'))},
              open('films/onecent-1867/script/pools.json', 'w'))
    print('pools.json written')
