"""Read-only. Exact-audio duplicates in SAMPLES MAC (hash of the audio data chunk, headers ignored).
Excluded on purpose: Digitakt/ (converted copies), */renamed/ (rack copies), _Presets not in use yet/.
Every copy is checked against all Ableton projects (.als, incl. backups) and racks (.adg) by path AND by filename."""
import os,struct,hashlib,gzip,re,json,collections,html,glob,sys
ROOT="/Users/amir/Desktop/SAMPLES MAC"
SKIP=("/Digitakt/","/renamed/","/_Presets not in use yet/")
def data_hash(p):
    with open(p,'rb') as f: d=f.read()
    if d[:4]==b'RIFF':
        i=12
        while i+8<=len(d):
            cid=d[i:i+4]; sz=struct.unpack('<I',d[i+4:i+8])[0]
            if cid==b'data': return hashlib.md5(d[i+8:i+8+sz]).hexdigest(),len(d)
            i+=8+sz+(sz&1)
    if d[:4]==b'FORM':   # aiff: SSND chunk
        i=12
        while i+8<=len(d):
            cid=d[i:i+4]; sz=struct.unpack('>I',d[i+4:i+8])[0]
            if cid==b'SSND': return hashlib.md5(d[i+16:i+8+sz]).hexdigest(),len(d)
            i+=8+sz+(sz&1)
    return hashlib.md5(d).hexdigest(),len(d)
files=[]
for r,_,fs in os.walk(ROOT):
    if any(s in r+"/" for s in SKIP): continue
    for f in fs:
        if f.lower().endswith((".wav",".aif",".aiff")): files.append(os.path.join(r,f))
print("audio files scanned:",len(files),flush=True)
by=collections.defaultdict(list); size={}
for i,p in enumerate(files):
    try: h,n=data_hash(p)
    except Exception: continue
    by[h].append(p); size[p]=n
groups=[v for v in by.values() if len(v)>1]
print("duplicate groups:",len(groups),"| extra copies:",sum(len(g)-1 for g in groups),"| bytes in extra copies: %.0f MB"%(sum(sum(size[p] for p in g)-max(size[p] for p in g) for g in groups)/1e6),flush=True)
# references
refs_path=collections.Counter(); refs_name=collections.defaultdict(set)
als=glob.glob("/Users/amir/Desktop/PROJECTS/**/*.als",recursive=True)+glob.glob("/Users/amir/Desktop/MIXING/**/*.als",recursive=True)+glob.glob("/Users/amir/Music/**/*.als",recursive=True)
adg=glob.glob("/Users/amir/Music/Ableton/User Library/**/*.adg",recursive=True)
dupe_names={os.path.basename(p) for g in groups for p in g}
for a in als+adg:
    try: x=gzip.open(a,'rb').read().decode('utf-8','ignore')
    except Exception: continue
    song=a.split("/PROJECTS/")[1].split("/")[0] if "/PROJECTS/" in a else os.path.basename(a)
    for m in re.findall(r'<Path Value="([^"]+)"',x):
        m=html.unescape(m)
        if m.startswith(ROOT): refs_path[m]+=1
        b=os.path.basename(m)
        if b in dupe_names: refs_name[b].add(song)
print("projects+racks scanned:",len(als)+len(adg),flush=True)
out=[]
for g in groups:
    out.append({"copies":[{"path":os.path.relpath(p,ROOT),"bytes":size[p],"used_by_path":refs_path.get(p,0),"songs_using_this_name":sorted(refs_name.get(os.path.basename(p),[]))} for p in sorted(g)]})
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"dupes_raw.json"),"w"),indent=1)
print("written dupes_raw.json")
