"""Read-only. How close is each pad of 'DRUM - Snare Witch House.adg' to the CC snare fingerprint,
and which of its samples are the same audio as a pad in the CC Snares racks (cc_racks_plan.csv)."""
import os,re,csv,gzip,hashlib,html
import numpy as np
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"cc_style_match.py")).read()
exec(src[:src.index("\nCC=")])                      # feats() + note() only, no library scan
ADG=os.path.expanduser("~/Music/Ableton/User Library/DRUM - Snare Witch House.adg")
CC="/Users/amir/Desktop/SAMPLES MAC/Witch House Samples/Drums/Snares & Claps"
refs=["CC_LSnare","Snare (Love And Caring)","Snare (Fleece)","Snare (Birds)","ULTIMATE_CC - snare - 14","Snare (Crimewave)","Snare (Alice Practice)","Snare (Good Time)","Snare (Vanished)","CC_VSnare"]
def audio_md5(p):
    import soundfile as sf
    y,_=sf.read(p,dtype="int32"); return hashlib.md5(y.tobytes()).hexdigest()
xml=gzip.decompress(open(ADG,"rb").read()).decode()
pads=[html.unescape(p) for p in re.findall(r'<Path Value="([^"]+\.wav)"',xml) if "/User Library/Samples/Imported/" in p]
pads=list(dict.fromkeys(pads))
plan=list(csv.DictReader(open("cc_racks_plan.csv")))
cand=[r["file"] for r in csv.DictReader(open("cc_style_matches.csv"))]
F=[x for x in (feats(p) for p in cand) if x]
K=["len","logbody","prom","bal","logcen"]; W=np.array([1.0,1.4,1.0,0.8,0.8])
A=np.array([[x[k] for k in K] for x in F]); mu=A.mean(0); sd=A.std(0)+1e-9
Z=lambda x:(np.array([x[k] for k in K])-mu)/sd*W
RZ=[(n,Z(feats(os.path.join(CC,n+".wav")))) for n in refs]
plan_md5={audio_md5(r["file"]):r for r in plan}
with open("wh_rack_vs_cc.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["sample","distance","closest CC snare","note","length ms","same audio as CC rack pad"])
    for p in pads:
        x=feats(p); d=sorted((float(np.linalg.norm(Z(x)-rz)),n) for n,rz in RZ) if x else [(99,"-")]
        m=plan_md5.get(audio_md5(p)); same=("rack %s: %s"%(m["rack"],os.path.basename(m["file"]))) if m else ""
        w.writerow([os.path.basename(p),"%.2f"%d[0][0],d[0][1],note(x["body"]) if x else "-","%.0f"%x["len"] if x else "-",same])
        print("%.2f %-24s %-9s %5s  %-45s %s"%(d[0][0],d[0][1][:24],note(x["body"]) if x else "-","%.0f"%x["len"] if x else "-",os.path.basename(p),same))
