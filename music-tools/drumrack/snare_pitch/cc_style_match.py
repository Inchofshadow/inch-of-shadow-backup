"""Read-only. Find snares in the library that sit closest to the Crystal Castles snare fingerprint.
Features per snare: effective length (peak to -40 dB), body peak 90-400 Hz (log Hz) + its prominence, low/high
energy balance, spectral centroid (10-140 ms window). Distance = nearest CC reference in z-scored feature space."""
import os,re,math,csv,glob,sys
import numpy as np, soundfile as sf
NN=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
def note(f): m=69+12*math.log2(f/440); r=int(round(m)); return "%s%d %+d"%(NN[r%12],r//12-2,round((m-r)*100))
def feats(p):
    y,sr=sf.read(p,always_2d=True); y=y.mean(1)
    if len(y)<sr*0.03 or np.abs(y).max()==0: return None
    y=y/np.abs(y).max(); pk=int(np.argmax(np.abs(y)))
    env=np.abs(y); hop=int(sr*0.005); e=np.array([env[i:i+hop].max() for i in range(pk,len(env),hop)]) if len(env)>pk+hop else np.array([1.0])
    below=np.nonzero(e<0.01)[0]; L=(below[0]*hop/sr*1000) if len(below) else (len(y)-pk)/sr*1000
    seg=y[pk+int(.01*sr):pk+int(.14*sr)]
    if len(seg)<int(.03*sr): return None
    n=1<<15; P=np.abs(np.fft.rfft(seg*np.hanning(len(seg)),n))**2+1e-18; S=10*np.log10(P); f=np.fft.rfftfreq(n,1/sr)
    b=(f>=90)&(f<=400); i=np.argmax(S[b]); fp=f[b][i]; prom=S[b][i]-np.median(S[(f>=90)&(f<=2000)])
    lo=P[(f>=60)&(f<400)].sum(); hi=P[(f>=400)&(f<8000)].sum(); bal=10*np.log10(lo/hi)
    w=(f>=60)&(f<12000); cen=(f[w]*P[w]).sum()/P[w].sum()
    return dict(len=L,logbody=math.log2(fp),prom=prom,bal=bal,logcen=math.log2(cen),body=fp)
CC="/Users/amir/Desktop/SAMPLES MAC/Witch House Samples/Drums/Snares & Claps"
refs=["CC_LSnare","Snare (Love And Caring)","Snare (Fleece)","Snare (Birds)","ULTIMATE_CC - snare - 14","Snare (Crimewave)","Snare (Alice Practice)","Snare (Good Time)","Snare (Vanished)","CC_VSnare"]
R=[(r,feats(os.path.join(CC,r+".wav"))) for r in refs]
roots=["/Users/amir/Desktop/SAMPLES MAC","/Users/amir/Splice/sounds/packs"]
SKIP=("/Digitakt/","/renamed/","/_Presets not in use yet/","/Witch House Samples/Drums/Snares & Claps/")
cand=[]
for root in roots:
    for r,_,fs in os.walk(root):
        if any(s in r+"/" for s in SKIP): continue
        for fn in fs:
            if not fn.lower().endswith((".wav",".aif",".aiff")): continue
            full=os.path.join(r,fn); low=(fn+" "+os.path.basename(r)).lower()
            if re.search(r"snare|snr|\bsd\b|_sd_|rimshot",low) and not re.search(r"loop|roll|fill|build|riser|\d{2,3}\s?bpm",fn.lower()): cand.append(full)
print("candidate snares:",len(cand),flush=True)
F=[]
for p in cand:
    try: x=feats(p)
    except Exception: x=None
    if x: F.append((p,x))
K=["len","logbody","prom","bal","logcen"]; W=np.array([1.0,1.4,1.0,0.8,0.8])
A=np.array([[x[k] for k in K] for _,x in F]); mu=A.mean(0); sd=A.std(0)+1e-9
Z=lambda x:(np.array([x[k] for k in K])-mu)/sd*W
RZ=[(n,Z(x)) for n,x in R]
out=[]
for p,x in F:
    z=Z(x); d=[(float(np.linalg.norm(z-rz)),n) for n,rz in RZ]; d.sort()
    out.append((d[0][0],d[0][1],p,x))
out.sort(key=lambda t:t[0])
with open(sys.argv[1],"w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["distance","closest CC snare","file","length ms","body Hz","note","prominence dB","low/high dB"])
    for dist,ref,p,x in out: w.writerow(["%.2f"%dist,ref,p,"%.0f"%x["len"],"%.0f"%x["body"],note(x["body"]),"%.1f"%x["prom"],"%+.1f"%x["bal"]])
print("analysed:",len(F))
print("CC reference ranges: len %d-%d ms, body %d-%d Hz"%(min(x["len"] for _,x in R),max(x["len"] for _,x in R),min(x["body"] for _,x in R),max(x["body"] for _,x in R)))
for dist,ref,p,x in out[:40]:
    src=p.replace("/Users/amir/Desktop/SAMPLES MAC/","").replace("/Users/amir/Splice/sounds/packs/","SPLICE/")
    print("%.2f  ~%-24s %-9s %4.0fms prom %4.1f  %s"%(dist,ref[:24],note(x["body"]),x["len"],x["prom"],src[-95:]))
