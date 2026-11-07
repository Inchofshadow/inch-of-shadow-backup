"""Rename the source Misc files per misc_renames.json and rewrite each machine's rack.
Replaces only whole names (="stem" and stem.wav) so RX5-I can never touch RX5-II."""
import json,os,gzip,shutil,re,html,sys
HERE=os.path.dirname(os.path.abspath(__file__))
REN="/Users/amir/Desktop/SAMPLES MAC/Drum Machine Tune/renamed"
RACKS="/Users/amir/Music/Ableton/User Library/User - Drum Racks/Drum Machines"
rows=[r for r in json.load(open(os.path.join(HERE,"misc_renames.json"))) if r.get("new")]
only=sys.argv[1:]
if only: rows=[r for r in rows if r["machine"] in only]
bad=[r for r in rows if r["corr"]<0.995]
if bad: print("REFUSING: %d matches below 0.995"%len(bad)); sys.exit(1)
byM={}
for r in rows: byM.setdefault(r["machine"],[]).append(r)
tot_f=tot_r=0; problems=[]
for m,rs in sorted(byM.items()):
    adg=os.path.join(RACKS,m+".adg")
    if not os.path.exists(adg): problems.append("no rack "+m); continue
    done=[]
    for r in rs:
        A=os.path.join(REN,m,r["old"]); B=os.path.join(REN,m,r["new"])
        if not os.path.exists(A) or os.path.exists(B): problems.append("skip %s/%s"%(m,r["old"])); continue
        os.rename(A,B)
        if os.path.exists(A+".asd") and not os.path.exists(B+".asd"): os.rename(A+".asd",B+".asd")
        done.append(r)
    shutil.copy2(adg,adg+".bak")
    x=gzip.open(adg,'rb').read().decode('utf-8'); n=0
    for r in done:
        os_,ns=html.escape(r["old"][:-4]),html.escape(r["new"][:-4])
        for o,w in (('="%s"'%os_,'="%s"'%ns),(os_+".wav",ns+".wav")):
            n+=x.count(o); x=x.replace(o,w)
    with gzip.open(adg,'wb') as f: f.write(x.encode('utf-8'))
    x=gzip.open(adg,'rb').read().decode('utf-8','ignore')
    miss=[p for p in (html.unescape(q) for q in re.findall(r'<Path Value="([^"]+)"',x)) if p.startswith("/") and not os.path.exists(p)]
    left=len(re.findall(r'Misc \d\d ',x))
    print("%-24s files %2d  replacements %3d  missing refs %d  Misc left %d"%(m,len(done),n,len(miss),left))
    if miss or left: problems.append("%s: missing %d, Misc left %d"%(m,len(miss),left))
    tot_f+=len(done); tot_r+=1
print("\nracks %d  files %d  problems %d"%(tot_r,tot_f,len(problems)))
for p in problems: print("  PROBLEM",p)
