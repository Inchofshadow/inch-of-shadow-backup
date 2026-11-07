"""Where a snare/clap body sits: strongest peak 90-400 Hz in the 10-140 ms after the hit, its prominence over the
90-2000 Hz median (dB), and low (<400 Hz) vs high (400-8k) energy. >=24 dB clear note, 15-24 body leans, <15 noise.
usage: python3 body_pitch.py <out.csv> <file> [<file> ...]"""
import os,sys,math,csv
import numpy as np, soundfile as sf
NN=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
def note(f): m=69+12*math.log2(f/440); r=int(round(m)); return "%s%d %+d"%(NN[r%12],r//12-2,round((m-r)*100))
rows=[]
for p in sys.argv[2:]:
    y,sr=sf.read(p,always_2d=True); y=y.mean(1); y=y/(np.abs(y).max() or 1)
    pk=int(np.argmax(np.abs(y))); seg=y[pk+int(.01*sr):pk+int(.14*sr)]
    n=1<<15; S=20*np.log10(np.abs(np.fft.rfft(seg*np.hanning(len(seg)),n))+1e-9); f=np.fft.rfftfreq(n,1/sr)
    b=(f>=90)&(f<=400); i=np.argmax(S[b]); fp=f[b][i]; prom=S[b][i]-np.median(S[(f>=90)&(f<=2000)])
    lo=np.sum(10**(S[(f>=60)&(f<400)]/10)); hi=np.sum(10**(S[(f>=400)&(f<8000)]/10)); body=10*np.log10(lo/hi)
    cls="clear note" if prom>=24 else ("body leans" if prom>=15 else "noise / no note")
    rows.append([os.path.basename(p)[:-4],"%.0f"%(len(y)/sr*1000),"%.0f"%fp,note(fp),"%.1f"%prom,"%+.1f"%body,cls])
with open(sys.argv[1],"w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["sample","ms","body Hz","note","prominence dB","low vs high dB","class"]); w.writerows(rows)
order={"clear note":0,"body leans":1,"noise / no note":2}
for r in sorted(rows,key=lambda r:(order[r[6]],float(r[2]))): print("  %-34s %5sms  body %4s Hz = %-9s prom %5s dB  low/high %6s  [%s]"%tuple(r))
import collections; print(dict(collections.Counter(r[6] for r in rows)))
