"""Pitch check for ZERO G discs. Type comes from the FOLDER (filenames are generic: 'Bass 21').
Read-only: writes SAMPLES MAC/_zero_g_pitch_report.csv. Loops / FX / Animals are skipped (one-shots only rule)."""
import os,glob,csv,importlib.util,sys,time
import numpy as np, soundfile as sf
here=os.path.dirname(os.path.abspath(__file__))
s=importlib.util.spec_from_file_location("t",os.path.join(here,"..","drumrack_tool_v2.py")); t=importlib.util.module_from_spec(s); s.loader.exec_module(t)
BASE="/Users/amir/Desktop/SAMPLES MAC"
BAND={"Bass":(28,400),"Synth":(40,1000),"Melody oneshots":(40,1000),"Melody loops":(40,1000),"Strings":(40,1000),
      "Brass":(40,1000),"Flute":(80,1500),"Piano":(40,1000),"Guitar":(40,1000),"Vocals":(80,1000),
      "Drums":(30,500),"Hits":(30,500),"Beatbox":(40,800)}
SKIP={"Drumloops","Breaks","FX","Animals"}
rows=[]; t0=time.time(); n=0
files=sorted(glob.glob(BASE+"/ZERO G - DISC */*/*.wav"))
for fp in files:
    disc=fp.split("/")[-3][-1]; folder=fp.split("/")[-2]; name=os.path.basename(fp)
    if folder in SKIP: continue
    n+=1
    try:
        y,sr=sf.read(fp,always_2d=False); y=np.asarray(y)
        hz,conf=t.get_fundamental(y,sr,BAND.get(folder,(40,1000)))
        note,_m,cents=t.hz_to_note(hz) if hz else (None,None,None)
        sec=round(len(y)/sr,3)
    except Exception as e:
        hz=conf=note=cents=None; sec=None; print("ERR",fp,e,flush=True)
    rows.append([disc,folder,name,sec,round(hz,1) if hz else "",note or "",cents if cents is not None else "",round(conf,1) if conf else 0,"yes" if conf and conf>=80 else ""])
    if n%200==0: print("%d analysed, %.0fs"%(n,time.time()-t0),flush=True)
out=BASE+"/_zero_g_pitch_report.csv"
with open(out,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["disc","folder","file","seconds","hz","note","cents","confidence","tag_at_80"]); w.writerows(rows)
print("DONE %d files -> %s  (%.0fs)"%(n,out,time.time()-t0),flush=True)
