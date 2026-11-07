"""Pick the 64 pads for the two CC Snares racks from cc_style_matches.csv + wh_folder_matches.csv (read-only).
Rack 1 = the 11 pitched CC snares + the 21 closest unique matches; rack 2 = the next 32.
Variants of one hit (tape takes, round robins, the same file in two packs) count once."""
import os,re,csv,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from drumrack_tool_v2 import strip_variant
CC="/Users/amir/Desktop/SAMPLES MAC/Witch House Samples/Drums/Snares & Claps"
CC_SNARES=["CC_LSnare","Snare (Love And Caring)","Snare (Fleece)","Snare (Birds)","ULTIMATE_CC - snare - 14",
           "Snare (Crimewave)","Snare (Good Time)","Snare (Alice Practice)","Snare (Vanished)","CC_VSnare","ULTIMATE_CC - snare - 11"]
BAD=re.compile(r"reverse|snap|/loops?/|_loops?/|loop",re.I)
rows=[r for f in ("cc_style_matches.csv","wh_folder_matches.csv") for r in csv.DictReader(open(f)) if not BAD.search(r["file"])]
rows.sort(key=lambda r:float(r["distance"]))
seen_stem,seen_feat,picks,folded={}, {}, [], {}
for r in rows:
    key_stem=(os.path.dirname(r["file"]),strip_variant(r["file"]).lower())
    key_feat=(r["length ms"],r["body Hz"],r["prominence dB"],r["low/high dB"])
    hit=seen_stem.get(key_stem) or seen_feat.get(key_feat)
    if hit is not None:
        folded[hit].append(r["file"])
        if "aorig" in os.path.basename(r["file"]).lower(): picks[hit]=r   # prefer the untreated take
        continue
    i=len(picks); picks.append(r); folded[i]=[]; seen_stem[key_stem]=i; seen_feat[key_feat]=i
    if len(picks)==53: break
cc=[]
body={x["sample"]:x for x in csv.DictReader(open("cc_snares_body.csv"))}
for n in CC_SNARES:
    b=body[n]; cc.append(dict(distance="CC",file=os.path.join(CC,n+".wav"),note=b["note"],**{"length ms":b["ms"],"body Hz":b["body Hz"]}))
rack1=cc+picks[:21]; rack2=picks[21:53]
with open("cc_racks_plan.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["rack","distance","note","body Hz","length ms","file","variants folded"])
    for k,rk in ((1,rack1),(2,rack2)):
        for r in rk: w.writerow([k,r["distance"],r["note"],r["body Hz"],r["length ms"],r["file"],len(folded.get(picks.index(r),[])) if r in picks else 0])
print(len(rack1),len(rack2))
