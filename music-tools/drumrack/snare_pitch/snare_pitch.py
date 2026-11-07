"""Shell pitch for snares/claps (spectral peak 10-140 ms after the transient, same method as the Terminator check),
plus the tonal fundamental as a cross-check. Read-only. usage: python3 snare_pitch.py <folder> <out.csv>"""
import sys,os,csv,re,importlib.util
import numpy as np, soundfile as sf
HERE=os.path.dirname(os.path.abspath(__file__))
s=importlib.util.spec_from_file_location("t",os.path.join(HERE,"..","drumrack_tool_v2.py")); T=importlib.util.module_from_spec(s); s.loader.exec_module(T)
rows=[]
for root,_,fs in os.walk(sys.argv[1]):
    for f in sorted(fs):
        if not f.lower().endswith((".wav",".aif",".aiff")): continue
        p=os.path.join(root,f)
        try: y,sr=sf.read(p,always_2d=True)
        except Exception as e: rows.append([f,"","","","","read error"]); continue
        y=y.mean(1); kind="CP" if re.search(r"clap",f,re.I) else "SD"
        band=T.SHELL_TYPES[kind]
        hz,conf=T.get_shell_pitch(y,sr,band)
        fhz,fconf=T.get_fundamental(y,sr,band)
        note,_,cents=T.hz_to_note(hz) if hz else (None,None,None)
        fnote=T.hz_to_note(fhz)[0] if fhz else ""
        m=re.search(r"(?:^|[\s_\-\[(])([A-G](?:#|b)?)(?:m|min|maj)?(?=[\s_\-\])]|\.\w+$)",os.path.splitext(f)[0]+" ")
        rows.append([os.path.relpath(p,sys.argv[1]),kind,"%.0f"%(len(y)/sr*1000),
                     ("%s %+d ct"%(note,cents) if note else ""),"%.0f"%conf if hz else "0",
                     (fnote+" (%.0f)"%fconf if fhz else ""),(m.group(1) if m else "")])
with open(sys.argv[2],"w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["file","type","ms","shell pitch","confidence","fundamental (conf)","note in name"]); w.writerows(rows)
print(len(rows),"files")
