"""Read-only. Score the non-CC snares in the Witch House 'Snares & Claps' folder (skipped by cc_style_match.py
because the CC references live there) on the same scale, written like cc_style_matches.csv."""
import os,csv
import numpy as np
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"cc_style_match.py")).read()
exec(src[:src.index("\nCC=")])
CC="/Users/amir/Desktop/SAMPLES MAC/Witch House Samples/Drums/Snares & Claps"
refs=["CC_LSnare","Snare (Love And Caring)","Snare (Fleece)","Snare (Birds)","ULTIMATE_CC - snare - 14","Snare (Crimewave)","Snare (Alice Practice)","Snare (Good Time)","Snare (Vanished)","CC_VSnare"]
cc_names=set(refs)|{"ULTIMATE_CC - snare - 11","Snare (Not In Love)"}
files=[os.path.join(CC,f) for f in sorted(os.listdir(CC)) if f.lower().endswith(".wav")
       and os.path.splitext(f)[0] not in cc_names and "clap" not in f.lower()]
cand=[r["file"] for r in csv.DictReader(open("cc_style_matches.csv"))]
F=[x for x in (feats(p) for p in cand) if x]
K=["len","logbody","prom","bal","logcen"]; W=np.array([1.0,1.4,1.0,0.8,0.8])
A=np.array([[x[k] for k in K] for x in F]); mu=A.mean(0); sd=A.std(0)+1e-9
Z=lambda x:(np.array([x[k] for k in K])-mu)/sd*W
RZ=[(n,Z(feats(os.path.join(CC,n+".wav")))) for n in refs]
out=[]
for p in files:
    x=feats(p)
    if not x: continue
    d=sorted((float(np.linalg.norm(Z(x)-rz)),n) for n,rz in RZ)[0]
    out.append((d[0],d[1],p,x))
out.sort(key=lambda t:t[0])
with open("wh_folder_matches.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["distance","closest CC snare","file","length ms","body Hz","note","prominence dB","low/high dB"])
    for dist,ref,p,x in out:
        w.writerow(["%.2f"%dist,ref,p,"%.0f"%x["len"],"%.0f"%x["body"],note(x["body"]),"%.1f"%x["prom"],"%+.1f"%x["bal"]])
        print("%.2f %-24s %-9s %5.0f  %s"%(dist,ref[:24],note(x["body"]),x["len"],os.path.basename(p)))
