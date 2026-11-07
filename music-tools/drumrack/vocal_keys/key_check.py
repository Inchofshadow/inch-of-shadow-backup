"""Measure the key of vocal chop loops (chroma + Krumhansl-Kessler profiles) and the note of one-shots
(fundamental, same method as the drum racks). Compare with the key written in the filename. Read-only.
usage: python3 key_check.py <folder> [out.csv]"""
import sys,os,re,csv,math,importlib.util
import numpy as np, soundfile as sf
HERE=os.path.dirname(os.path.abspath(__file__))
s=importlib.util.spec_from_file_location("t",os.path.join(HERE,"..","drumrack_tool_v2.py")); T=importlib.util.module_from_spec(s); s.loader.exec_module(T)
NN=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
MAJ=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]); MIN=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
def chroma(y,sr):
    n=8192; hop=2048; win=np.hanning(n); f=np.fft.rfftfreq(n,1/sr); ok=(f>=60)&(f<=5000)
    pc=np.round(12*np.log2(f[ok]/440.0)+69).astype(int)%12; C=np.zeros(12)
    for i in range(0,max(1,len(y)-n),hop):
        seg=y[i:i+n]
        if len(seg)<n: break
        S=np.abs(np.fft.rfft(seg*win))[ok]**2
        np.add.at(C,pc,S)
    return C/(C.sum() or 1)
def key_of(C):
    sc=[]
    for k in range(12):
        sc.append((np.corrcoef(C,np.roll(MAJ,k))[0,1],k,"maj")); sc.append((np.corrcoef(C,np.roll(MIN,k))[0,1],k,"min"))
    sc.sort(reverse=True); return sc
def parse_key(name):
    m=re.search(r"(?<![A-Za-z])([A-G](?:#|b)?)\s*(maj|min|m)?(?=\.wav$|\s|$)",name.replace(".wav"," .wav")) 
    m=re.search(r"-\s*(?:\d+BPM\s+)?([A-G](?:#|b)?)(maj|min)?\.wav$",name)
    if not m: return None
    t=m.group(1).replace("Db","C#").replace("Eb","D#").replace("Gb","F#").replace("Ab","G#").replace("Bb","A#")
    return (NN.index(t), m.group(2) or "note")
def rel(k,mode): return ((k+3)%12,"maj") if mode=="min" else ((k-3)%12,"min")
rows=[]
for root,_,fs in os.walk(sys.argv[1]):
    for f in sorted(fs):
        if not f.lower().endswith(".wav"): continue
        p=os.path.join(root,f); y,sr=sf.read(p,always_2d=True); y=y.mean(1)
        lab=parse_key(f); dur=len(y)/sr
        if lab and lab[1]=="note" or "One-Shot" in f:
            hz,conf=T.get_fundamental(y,sr,(70,1200))
            note=T.hz_to_note(hz)[0] if hz else ""
            got=note.rstrip("0123456789-") if note else ""
            verdict="no clear pitch" if not hz or conf<60 else ("MATCH" if lab and got==NN[lab[0]] else "DIFFERENT")
            rows.append([os.path.relpath(p,sys.argv[1]),"%.1fs"%dur,(NN[lab[0]] if lab else ""),"%s (%.0f Hz, conf %.0f)"%(note,hz or 0,conf),verdict]); continue
        sc=key_of(chroma(y,sr)); best=sc[0]; second=sc[1]
        bk="%s%s"%(NN[best[1]],best[2]); conf=best[0]
        if not lab: verdict="no key in name"
        else:
            lk,lm=lab
            if (best[1],best[2])==(lk,lm): verdict="MATCH"
            elif (best[1],best[2])==rel(lk,lm): verdict="RELATIVE (same notes)"
            elif any((x[1],x[2]) in ((lk,lm),rel(lk,lm)) for x in sc[1:3]): verdict="close (2nd/3rd guess)"
            else: verdict="DIFFERENT"
        rows.append([os.path.relpath(p,sys.argv[1]),"%.1fs"%dur,("%s%s"%(NN[lab[0]],lab[1]) if lab else ""),"%s (r=%.2f, next %s%s)"%(bk,conf,NN[second[1]],second[2]),verdict])
out=sys.argv[2] if len(sys.argv)>2 else None
if out:
    with open(out,"w",newline="") as fh: w=csv.writer(fh); w.writerow(["file","length","key in name","measured","verdict"]); w.writerows(rows)
import collections; print(dict(collections.Counter(r[4] for r in rows)))
for r in rows: print("%-62s %-6s %-8s %-34s %s"%(r[0][-62:],r[1],r[2],r[3],r[4]))
