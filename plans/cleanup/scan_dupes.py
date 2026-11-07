import os, hashlib, sys, json, collections
root = sys.argv[1]; out = sys.argv[2]; MIN = int(sys.argv[3]) if len(sys.argv) > 3 else 1_000_000
by_size = collections.defaultdict(list)
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in ('.git','node_modules','.venv','venv')]
    for f in fn:
        p = os.path.join(dp, f)
        try:
            if os.path.islink(p): continue
            s = os.path.getsize(p)
        except OSError: continue
        if s >= MIN: by_size[s].append(p)
def h(p):
    m = hashlib.sha1()
    with open(p,'rb') as fh:
        for b in iter(lambda: fh.read(1<<20), b''): m.update(b)
    return m.hexdigest()
groups = []
for s, ps in by_size.items():
    if len(ps) < 2: continue
    byh = collections.defaultdict(list)
    for p in ps:
        try: byh[h(p)].append(p)
        except OSError: pass
    for k, v in byh.items():
        if len(v) > 1: groups.append({'size': s, 'paths': sorted(v)})
groups.sort(key=lambda g: -g['size']*(len(g['paths'])-1))
json.dump(groups, open(out,'w'), indent=1)
print(len(groups), 'groups, reclaimable MB:', round(sum(g['size']*(len(g['paths'])-1) for g in groups)/1e6))
