import os, sys, shutil, json, datetime, hashlib
ROOT = "/Users/amir/Desktop/Inch of Shadow"
TRASH = os.path.expanduser("~/.Trash")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
dest_root = os.path.join(TRASH, "IoS-cleanup-A-" + stamp)
def sha(p):
    m = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): m.update(b)
    return m.hexdigest()
items = []
items.append("ChatGPT/fa7142d8fcbe226d64c389d9ce1920e9771a479be64c12caa36e8bc88ef79332-2026-10-13-18-00-14-0d5480c9a26c41488ec46d12fdeaa467.zip")
for dp, dn, fn in os.walk(ROOT):
    if '.git' in dp.split(os.sep): continue
    for d in list(dn):
        if d in ('__pycache__', '.pytest_cache'):
            items.append(os.path.relpath(os.path.join(dp, d), ROOT)); dn.remove(d)
    dn[:] = [d for d in dn if d != '.git']
    if '.DS_Store' in fn: items.append(os.path.relpath(os.path.join(dp, '.DS_Store'), ROOT))
FS = "Inchofshadowcode/artwork/Farewell Single/"
pairs = [
    (FS + "untitled folder/Inch_of_Shadow_Farewell_Single_3000x3000 copy.png", FS + "Inch_of_Shadow_Farewell_Single_3000x3000.png"),
    (FS + "untitled folder/Ich.png", FS + "Reel Build/USE/01_full_artwork.png"),
    (FS + "untitled folder/70% no angels.png", FS + "Reel Build/USE/09_world_below.png"),
    (FS + "Reel Build/SKIP/duplicate_original.png", FS + "Inch_of_Shadow_Farewell_Single_3000x3000.png"),
]
for dup, keep in pairs:
    a, b = os.path.join(ROOT, dup), os.path.join(ROOT, keep)
    if os.path.exists(a) and os.path.exists(b) and sha(a) == sha(b): items.append(dup)
    else: print("SKIP (not identical):", dup)
I2 = "Releases/Eastern Star/Music for insta/Music for Instagram videos 2"
I1 = "Releases/Eastern Star/Music for insta/Music for Instagram videos"
ok = all(os.path.exists(os.path.join(ROOT, I1, f)) and sha(os.path.join(ROOT, I2, f)) == sha(os.path.join(ROOT, I1, f))
         for f in os.listdir(os.path.join(ROOT, I2)) if f != '.DS_Store')
if ok: items.append(I2)
else: print("SKIP (not identical):", I2)
items = [i for i in dict.fromkeys(items) if not any(i != j and i.startswith(j + "/") for j in items)]
dry = '--go' not in sys.argv
log = []
for rel in items:
    src = os.path.join(ROOT, rel)
    if not os.path.exists(src): continue
    dst = os.path.join(dest_root, rel)
    log.append({"from": src, "to": dst})
    if not dry:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
print(("DRY RUN " if dry else "MOVED ") + str(len(log)) + " items to " + dest_root)
if not dry:
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(log, open(os.path.join(here, "trash-a-log-" + stamp + ".json"), "w"), indent=1)
    with open(os.path.join(here, "undo-trash-a-" + stamp + ".py"), "w") as u:
        u.write("import json, os, shutil\nlog = json.load(open(%r))\nfor e in log:\n    if os.path.exists(e['to']) and not os.path.exists(e['from']):\n        os.makedirs(os.path.dirname(e['from']), exist_ok=True); shutil.move(e['to'], e['from'])\nprint('restored', len(log))\n" % os.path.join(here, "trash-a-log-" + stamp + ".json"))
