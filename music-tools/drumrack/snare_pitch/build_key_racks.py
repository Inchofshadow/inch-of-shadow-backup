"""Snares by Key: one rack per note for every snare with a clear body note (prominence >= 24 dB).
Reads cc_style_matches.csv + wh_folder_matches.csv + cc_snares_body.csv. Originals are only read.
Writes: SAMPLES MAC/Snares by Key/<note>/<octave note> <name>.wav  (the racks point here)
        SAMPLES MAC/Digitakt/Snares by Key/<note>/  (48k/16 mono, -6 dB peak)
        User Library/User - Drum Racks/Snares by Key/Snares [<note>].adg  (max 32 pads, low to high from C1)
Run with --dry to print the plan only."""
import os,re,sys,csv,shutil,collections
import soundfile as sf
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from drumrack_tool_v2 import write_adg, convert_for_digitakt
SAMPLES="/Users/amir/Desktop/SAMPLES MAC"; SPLICE="/Users/amir/Splice/sounds/packs/"
COPIES=os.path.join(SAMPLES,"Snares by Key"); DT=os.path.join(SAMPLES,"Digitakt","Snares by Key")
RACKS=os.path.expanduser("~/Music/Ableton/User Library/User - Drum Racks/Snares by Key")
CC=os.path.join(SAMPLES,"Witch House Samples/Drums/Snares & Claps")
NN=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
BAD=re.compile(r"reverse|snap|/loops?/|_loops?/|loop",re.I)
CC_COPIES={"ULTIMATE_CC - snare - 4","ULTIMATE_CC - snare - 6","✧CRIMEWAVE"}

rows=[r for f in ("cc_style_matches.csv","wh_folder_matches.csv") for r in csv.DictReader(open(f)) if not BAD.search(r["file"])]
for x in csv.DictReader(open("cc_snares_body.csv")):
    if "clap" in x["sample"].lower() or x["sample"] in CC_COPIES: continue
    rows.append({"file":os.path.join(CC,x["sample"]+".wav"),"note":x["note"],"prominence dB":x["prominence dB"],
                 "length ms":x["ms"],"body Hz":x["body Hz"]})
VAR=re.compile(r"^(aorig|[ct]\d[as]?|r\d+|x\d?|st)$",re.I)
def tokens(stem): return [w for w in re.split(r"[_\-\.\s\(\)\[\]]+",stem) if w]
def sound_key(p):   # tape takes and round robins anywhere in the name: MR10_SD_T1A-02 -> mr10 sd 02
    return (os.path.dirname(p)," ".join(w.lower() for w in tokens(os.path.splitext(os.path.basename(p))[0]) if not VAR.match(w)))
NOISE=re.compile(r"^(one|shot|oneshot|drum|drums|hits?|snares?|snr|sd|snaredrum|wav|dry|processed)$",re.I)
def label_and_stem(p):
    stem=os.path.splitext(os.path.basename(p))[0]
    stem=re.sub(r"\[[^\]]*\]","",stem)                      # old pitch tags like [D# -44]
    if p.startswith(CC):
        if stem.startswith("@skeletone"): return "WH Skeletone",stem.split("-")[-1]
        if stem.startswith("✧"): return "WH",stem.replace("✧","").replace("SNARE -","")
        return "CC",re.sub(r"^Snare \((.*)\)$",r"\1",stem).replace("ULTIMATE_CC - snare -","Ultimate")
    if p.startswith(SPLICE):
        pack=p[len(SPLICE):].split("/")[0]
        lab=[w for w in tokens(pack) if not re.match(r"^(by|vol|the|of|s|\d+)$",w,re.I)]
        ws=tokens(stem)
        while len(ws)>1 and re.fullmatch(r"[A-Z0-9#]{2,8}",ws[0]) and not NOISE.match(ws[0]): ws=ws[1:]   # pack codes OLIVER_ TS_ADD_ 91V_AC_
        n=1 if lab and lab[0] in ("Oliver","Angelcore","Transcendent","Sullivan","Popwave","VIRTU") else 2
        return " ".join(lab[:n]), " ".join(ws)
    rel=p[len(SAMPLES)+1:].split("/")
    m=re.match(r"ZERO G - DISC (\d)",rel[0])
    if m: return "ZeroG"+m.group(1),stem
    if rel[0].startswith("Tape Drum Machines"): return (rel[-2] if rel[-2]!="Samples" else ""),stem
    if rel[0]=="Studio Real Drum Machines": return rel[1].replace("Kawai R-50e & R-100",rel[2]).replace("Yamaha RX-Series",rel[2]),stem
    if rel[0]=="Cluster New Wave": return re.sub(r"^CS-|-Live$","",rel[1]),stem
    if "Eitan" in rel[0] or "TRNSNT" in rel[0]: return "Eitan",stem.replace("TRNSNT1 Snares & Claps","")
    return rel[0],stem
SHORT_LAB={"Sequential Circuits Tom":"SCI Tom","Acoustic Drums (80's Style)":"80s Acoustic","Linn Drum LM2":"LinnDrum LM2","S900 KITS":"S900","Visco SpaceDrum":"Visco","Kawai R-50e":"R-50e","Kawai R-100":"R-100"}
def short(p):
    lab,stem=label_and_stem(p)
    lab=SHORT_LAB.get(lab,lab)
    labw=lab.split(); seen={w.lower() for w in labw}|{re.sub(r"\W","",w.lower()) for w in labw}|set(re.split(r"[^a-z0-9]+",lab.lower()))
    body=[]
    for w in tokens(stem):
        k=w.lower()
        if VAR.match(w) or NOISE.match(w) or k in seen or re.sub(r"\W","",k) in seen: continue
        if k in ("cs","rx11","mr10","rpm40","tr505","tr626","lm1","linndrm","kpr77","thekit","oberheim","dmx","roland","yamaha","r8","rx","s900","kits","sequentil","circuit","space","rx5","rx7") and lab: continue
        body.append(w)
    name=" ".join(labw+body)
    return re.sub(r"\s+"," ",name).strip()[:30].strip()

groups,index=[],{}
for r in rows:   # one per sound: tape takes / round robins / the same hit in two packs
    k1=sound_key(r["file"]); k2=(r["length ms"],r["body Hz"],r["prominence dB"])
    i=index.get(k1,index.get(k2))
    if i is None: i=len(groups); groups.append([]); index[k1]=index[k2]=i
    groups[i].append(r)
uniq=[next((r for r in g if "aorig" in os.path.basename(r["file"]).lower()),g[0]) for g in groups]
clear=[r for r in uniq if float(r["prominence dB"])>=24]

by=collections.defaultdict(list)
for r in clear: by[re.match(r"[A-G]#?",r["note"]).group()].append(r)
plan={}
for n in NN:
    g=sorted(by[n],key=lambda r:-float(r["prominence dB"]))[:32]       # D has 33: weakest note drops
    g.sort(key=lambda r:float(r["body Hz"]))
    names=collections.Counter(); out=[]
    for r in g:
        nm="%s %s"%(r["note"].split()[0],short(r["file"]))
        names[nm]+=1
        if names[nm]>1: nm+=" %d"%names[nm]
        out.append((nm,r))
    plan[n]=out
if "--dry" in sys.argv:
    for n in NN:
        print("== Snares [%s] %d"%(n,len(plan[n])))
        for nm,r in plan[n]: print("   %-34s %s"%(nm,r["file"].replace(SAMPLES+"/","").replace(SPLICE,"SPL/")[-70:]))
    print("total",sum(len(v) for v in plan.values()),"of clear",len(clear),"unique",len(uniq)); sys.exit()

if any(os.path.exists(p) for p in (COPIES,DT,RACKS)): sys.exit("output folder already exists, stopping")
with open("undo_key_racks.sh","w") as fh:
    fh.write("#!/bin/sh\n# removes only what build_key_racks.py created; originals were never touched\n")
    for p in (COPIES,DT,RACKS): fh.write('rm -rf "%s"\n'%p)
log=[]; os.makedirs(RACKS)
for n in NN:
    cdir=os.path.join(COPIES,n); ddir=os.path.join(DT,n); os.makedirs(cdir); os.makedirs(ddir)
    pads=[]
    for i,(nm,r) in enumerate(plan[n]):
        safe=nm.replace("/","-").replace(":","-")
        dst=os.path.join(cdir,safe+os.path.splitext(r["file"])[1].lower())
        shutil.copy2(r["file"],dst); convert_for_digitakt(r["file"],os.path.join(ddir,safe+".wav"))
        info=sf.info(dst); pads.append(dict(note=36+i,name=safe,path=dst,frames=info.frames,sr=info.samplerate))
        log.append([n,NN[(36+i)%12]+str((36+i)//12-2),safe,r["body Hz"],r["prominence dB"],r["file"],dst])
    write_adg(os.path.join(RACKS,"Snares [%s].adg"%n),pads)
with open("key_racks_built.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["rack","pad","name","body Hz","prominence dB","original","copy"]); w.writerows(log)
print("built",len(log),"pads in",len(NN),"racks")
