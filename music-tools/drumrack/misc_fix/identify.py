"""Trace every 'Misc NN <machine>.wav' back to its original pack file by waveform,
derive the real instrument type, and write the rename map + a sources CSV."""
import struct,glob,os,subprocess,numpy as np,json,re,csv,collections
FF="/Users/amir/.local/bin/ffmpeg"
BASE="/Users/amir/Desktop/SAMPLES MAC"
REN=BASE+"/Drum Machine Tune/renamed"
OUT=os.path.dirname(os.path.abspath(__file__))
SKIP=("/Drum Machine Tune/renamed","/Digitakt/","/Splice Racks/renamed","/_rack_backup")

def dur(p):
    try:
        with open(p,'rb') as f: d=f.read(65536)
    except: return None
    if d[:4]!=b'RIFF': return None
    i=12; ch=sr=bits=None
    while i+8<=len(d):
        cid=d[i:i+4]; sz=struct.unpack('<I',d[i+4:i+8])[0]
        if cid==b'fmt ': _,ch,sr,_,_,bits=struct.unpack('<HHIIHH',d[i+8:i+24])
        elif cid==b'data':
            return sz/(ch*(bits//8))/sr if ch and sr and bits else None
        i+=8+sz+(sz&1)
cache={}
def aud(p):
    if p in cache: return cache[p]
    r=subprocess.run([FF,"-loglevel","error","-i",p,"-ac","1","-ar","48000","-f","s16le","-"],capture_output=True)
    y=np.frombuffer(r.stdout,dtype='<i2').astype(np.float32); m=abs(y).max(); y=y/m if m else y
    if len(cache)>3000: cache.clear()
    cache[p]=y; return y
def best_corr(a,b,maxlag=2400):
    n=min(len(a),len(b))
    if n<128: return -1.0
    a=a[:n]; b=b[:n]; L=1<<(int(np.ceil(np.log2(n+maxlag)))+1)
    cc=np.fft.irfft(np.fft.rfft(a,L)*np.conj(np.fft.rfft(b,L)),L)
    cc=np.concatenate([cc[-maxlag:],cc[:maxlag+1]])
    na=np.sqrt(float(np.dot(a,a))); nb=np.sqrt(float(np.dot(b,b)))
    return float(cc.max()/(na*nb)) if na>0 and nb>0 else -1.0

MANUAL={"UNIVOXb1.wav":"Kick","UNIVOXbd.wav":"Kick","UNIVOXch.wav":"HiHat","UNIVOXoh.wav":"OpenHat",
        "UNIVOXsd.wav":"Snare","Yamaha RX7 castnet.wav":"Castanet","v_Roland_R8.wav":"Perc"}
RULES=[(r"brush","Brush"),(r"chime","Chime"),(r"tria[lm]|triangle","Triangle"),(r"cuica","Cuica"),
(r"wistl|whistl","Whistle"),(r"sidestick|side ?stick","Sidestick"),(r"stick","Stick"),(r"^ping","Ping"),
(r"agogo","Agogo"),(r"cabasa","Cabasa"),(r"cast[ae]?ne?t","Castanet"),(r"clave","Clave"),
(r"claps?|hand ?clap","Clap"),(r"congh","CongaHi"),(r"congl","CongaLo"),(r"conga","Conga"),
(r"cowbell|\bcb\b","Cowbell"),(r"crash","Crash"),(r"china","China"),(r"ride","Ride"),
(r"cymbal|\bcym\b","Cymbal"),(r"timbale?|timb","Timbale"),(r"timpani","Timpani"),
(r"tambo?u?r?|tamb","Tambourine"),(r"vibraslap","Vibraslap"),(r"guiro|quija","Guiro"),
(r"shaker|shake","Shaker"),(r"maraca","Maraca"),(r"block|wood","Block"),(r"bongo|bong","Bongo"),
(r"rim","Rim"),(r"finger ?snap|snap|finger","Snap"),(r"click","Click"),(r"scratch","Scratch"),
(r"squeak","Squeak"),(r"bell ?tree","BellTree"),(r"bell","Bell"),(r"orc\.? ?hit|orch|\bhits?\b","Hit"),
(r"gun","Gun"),(r"door","Door"),(r"beep","Beep"),(r"metal","Metal"),(r"laser|lazer","Laser"),
(r"open ?hat|ophat|\boh\b","OpenHat"),(r"cl ?hat|clhat|closed|\bch\b|hi ?hat|\bhh\b","HiHat"),
(r"\bsd\d?\b|snare|snaredrum|\bsn\d","Snare"),
(r"\bbd\d?\b|bdloud|bdsoft|kick|\bfbd\b|hbd\d?|pbd\d?|dkik","Kick"),
(r"tom","Tom"),(r"chop","Chop"),(r"reverse|rvs","Reverse"),(r"noise","Noise"),(r"perc","Perc")]
def typ(n):
    if n in MANUAL: return MANUAL[n]
    s=n.lower().replace("_"," ").rsplit(".",1)[0]
    for p,t in RULES:
        if re.search(p,s): return t

src=sorted((d,p) for p in glob.glob(BASE+"/**/*.wav",recursive=True)
           if not any(s in p for s in SKIP) for d in [dur(p)] if d)
durs=np.array([s[0] for s in src])
targets=sorted(glob.glob(REN+"/*/Misc *.wav"))
print("sources %d  targets %d"%(len(src),len(targets)),flush=True)
res=[]
for i,t in enumerate(targets):
    td=dur(t); y=aud(t)
    lo,hi=np.searchsorted(durs,td-0.03),np.searchsorted(durs,td+0.03)
    sc=sorted(((best_corr(aud(src[j][1]),y),src[j][1]) for j in range(lo,hi)),reverse=True)
    c,p=sc[0] if sc else (-1,None)
    res.append({"machine":os.path.basename(os.path.dirname(t)),"old":os.path.basename(t),
                "corr":round(c,4),"source":os.path.relpath(p,BASE) if p else None,
                "orig":os.path.basename(p) if p else None})
    print("%3d/%d %.3f %-30s <- %s"%(i+1,len(targets),c,res[-1]["old"],res[-1]["orig"]),flush=True)

# types + numbering that continues after files already in the folder
being={(r["machine"],r["old"]) for r in res}
top=collections.defaultdict(int)
for r in res:
    for p in glob.glob(os.path.join(REN,r["machine"],"*.wav")):
        b=os.path.basename(p)
        if (r["machine"],b) in being: continue
        m=re.match(r"^([A-Za-z]+)(?: \[[^\]]+\])? (\d+) ",b)
        if m: top[(r["machine"],m.group(1))]=max(top[(r["machine"],m.group(1))],int(m.group(2)))
seq=collections.defaultdict(int)
for r in sorted(res,key=lambda z:(z["machine"],z["old"])):
    r["type"]=typ(r["orig"] or "")
    if not r["type"]: r["new"]=None; continue
    k=(r["machine"],r["type"]); seq[k]+=1
    r["new"]="%s %02d %s.wav"%(r["type"],top[k]+seq[k],r["old"].rsplit(" ",1)[-1][:-4])
json.dump(res,open(os.path.join(OUT,"misc_renames.json"),"w"),indent=1)
with open(BASE+"/Drum Machine Tune/MISC_SOURCES.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["machine","old_name","new_name","type","original_file","match"])
    for r in res: w.writerow([r["machine"],r["old"],r["new"],r["type"],r["source"],r["corr"]])
bad=[r for r in res if r["corr"]<0.995 or not r["new"]]
print("\nDONE  mapped %d  below-0.995-or-untyped %d"%(len(res)-len(bad),len(bad)))
for r in bad: print("  CHECK",r)
