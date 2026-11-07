"""Copy chosen Ableton projects from ~/Desktop/PROJECTS to a NEW dated folder on Intenso.
FULL projects are copied whole; DELTA projects only get files that are new or changed since the
July 2025 copy in 'Mac July 25 First Backup/PROJECTS' (that copy did not keep dates, so: same size AND
source older than 2025-07-23 = unchanged). Nothing on the Mac or in older backups is touched.
Usage: projects_backup.py <date> [--dry]   Stops before copying if less than KEEP_FREE would stay free."""
import os,sys,shutil,datetime,json,time
S=os.path.expanduser("~/Desktop/PROJECTS"); V="/Volumes/Intenso"; J=V+"/Mac July 25 First Backup/PROJECTS"
CUT=datetime.datetime(2025,7,23).timestamp(); CL=1048576; KEEP_FREE=0.5e9
FULL=["Sitar Star Cm 115 bpm","Open F minor 121","Rock Wave C dot 100","Harmonic D 140","I See Am 75 bpm","D Minor 112 BPM",
      "Night F Dorian 119","Morality Song","A Dorian 111 bpm","test","Goth Wich Project","DJ Blank","F# minor song 118","Emphaty",
      "The Tunnel Eb 124","Yuval amir","Jam 127","125 bpm Project","song writing","TEMAPLTE REC"]
DELTA=["Sundial","Start Gladrial 137 BPM","Exotic dance ","Curtain Rain*","Desert Forest","Down and low","Nothingness 118 BPM",
       "Asid 130 bpm","Fata Morgana 138 bpm","Salty Night","song","Gerog Samosa","Tibilsi"]
date=sys.argv[1]; DEST=os.path.join(V,"PROJECTS BACKUP",date,"PROJECTS")
def wanted(p,delta):
    out=[]
    for r,ds,fs in os.walk(os.path.join(S,p)):
        ds.sort()
        for f in sorted(fs):
            if f.startswith("._") or f==".DS_Store": continue
            fp=os.path.join(r,f); st=os.stat(fp)
            if delta:
                try:
                    if os.stat(os.path.join(J,os.path.relpath(fp,S))).st_size==st.st_size and st.st_mtime<CUT: continue
                except OSError: pass
            out.append((fp,st.st_size))
    return out
jobs={p:wanted(p,False) for p in FULL}; jobs.update({p:wanted(p,True) for p in DELTA})
dirs={os.path.dirname(fp) for v in jobs.values() for fp,_ in v}
need=sum(-(-s//CL)*CL for v in jobs.values() for _,s in v)+(len(dirs)+40)*CL
free=shutil.disk_usage(V).free
print("files %d  need %.2f GB  free %.2f GB  free after %.2f GB"%(sum(map(len,jobs.values())),need/1e9,free/1e9,(free-need)/1e9))
if free-need<KEEP_FREE: sys.exit("STOP: would leave less than %.1f GB free"%(KEEP_FREE/1e9))
if "--dry" in sys.argv: sys.exit()
if os.path.exists(os.path.dirname(DEST)): sys.exit("STOP: %s already exists"%os.path.dirname(DEST))
os.makedirs(DEST); log=[]; t0=time.time()
for p,files in jobs.items():
    for fp,size in files:
        dst=os.path.join(DEST,os.path.relpath(fp,S)); os.makedirs(os.path.dirname(dst),exist_ok=True)
        shutil.copyfile(fp,dst); st=os.stat(fp); os.utime(dst,(st.st_atime,st.st_mtime))
        log.append({"project":p,"kind":"delta" if p in DELTA else "full","file":os.path.relpath(fp,S),"size":size})
    print("copied %-26s %5d files %6.2f GB  (%.0fs)"%(p,len(files),sum(s for _,s in files)/1e9,time.time()-t0),flush=True)
json.dump(log,open(os.path.join(os.path.dirname(DEST),"files.json"),"w"),indent=0)
bad=[x["file"] for x in log if os.path.getsize(os.path.join(DEST,x["file"]))!=x["size"]]
print("verify: %d files, %d size mismatches, free now %.2f GB"%(len(log),len(bad),shutil.disk_usage(V).free/1e9))
for b in bad[:20]: print("  MISMATCH",b)
