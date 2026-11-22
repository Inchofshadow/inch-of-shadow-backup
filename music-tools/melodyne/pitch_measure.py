"""Measure how far sung notes sit from a scale, to pick Melodyne settings per song.
Read-only. Usage: python3 pitch_measure.py FILE.wav --root F --scale minor [--start S --end S]
Prints note-center offsets (cents), in-note drift, out-of-scale share.
"""
import argparse, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

NOTES = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
SCALES = {'minor':[0,2,3,5,7,8,10], 'major':[0,2,4,5,7,9,11], 'dorian':[0,2,3,5,7,9,10]}

def yin(x, sr, fmin=75, fmax=700, win=1024, hop=256, thr=0.15):
    tmin, tmax = int(sr/fmax), int(sr/fmin)
    n = (len(x)-win)//hop
    f0 = np.full(n, np.nan); rms = np.zeros(n)
    B = 2048
    for b0 in range(0, n, B):
        idx = np.arange(b0, min(n, b0+B))
        fr = np.stack([x[i*hop:i*hop+win] for i in idx])
        rms[idx] = np.sqrt((fr**2).mean(1))
        F = np.fft.rfft(fr, 2*win)
        ac = np.fft.irfft(F*np.conj(F))[:, :tmax+1]
        cs = np.cumsum(fr**2, 1)
        e0 = cs[:, -1:]
        tail = np.concatenate([np.zeros((len(idx),1)), cs], 1)
        # energy of x[t:win] for each tau
        taus = np.arange(tmax+1)
        e_t = e0 - tail[:, taus]
        e_head = tail[:, win - taus]
        d = e_head + e_t - 2*ac
        d[:, 0] = 1
        cm = d[:, 1:] * np.arange(1, tmax+1) / np.maximum(np.cumsum(d[:, 1:], 1), 1e-12)
        cm = np.concatenate([np.ones((len(idx),1)), cm], 1)
        for k, row in enumerate(cm):
            r = row[tmin:]
            below = np.where(r < thr)[0]
            if not len(below): continue
            t = below[0]
            while t+1 < len(r) and r[t+1] < r[t]: t += 1
            T = t + tmin
            if 1 <= T < tmax:
                a, bb, c = row[T-1], row[T], row[T+1]
                den = a - 2*bb + c
                T = T + (0.5*(a-c)/den if den else 0)
            f0[idx[k]] = sr / T
    return f0, rms

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wav'); ap.add_argument('--root', default='F'); ap.add_argument('--scale', default='minor')
    ap.add_argument('--start', type=float, default=0); ap.add_argument('--end', type=float, default=None)
    a = ap.parse_args()
    sr, x = wavfile.read(a.wav)
    s0 = int(a.start*sr); s1 = int(a.end*sr) if a.end else len(x)
    x = np.asarray(x[s0:s1], dtype=np.float64)
    if x.ndim > 1: x = x.mean(1)
    x /= (np.abs(x).max() or 1)
    x = resample_poly(x, 1, 4)
    sr2 = sr/4
    f0, rms = yin(x, sr2)
    hop_s = 256/sr2
    gate = rms > max(0.02, np.percentile(rms, 60)*0.5)
    cents = 1200*np.log2(f0/440.0) + 6900  # midi*100
    cents[~gate] = np.nan
    root = NOTES.index(a.root); deg = set((root+i) % 12 for i in SCALES[a.scale])
    # segment notes: consecutive voiced frames within 60 ct of the running note median
    notes = []; cur = []
    def flush():
        if len(cur) >= 6:
            c = np.array(cur); notes.append(c)
    for v in cents:
        if np.isnan(v): flush(); cur = []; continue
        if cur and abs(v - np.median(cur[-5:])) > 60: flush(); cur = []
        cur.append(v)
    flush()
    rows = []
    for c in notes:
        core = c[len(c)//5: len(c)-len(c)//5] if len(c) >= 10 else c
        center = np.median(core)
        midi = int(np.round(center/100)); off = center - midi*100
        drift = np.percentile(core, 90) - np.percentile(core, 10)
        rows.append((midi, off, drift, len(c)*hop_s))
    if not rows: print('no notes'); return
    R = np.array(rows)
    ab = np.abs(R[:,1]); dur = R[:,3]
    inkey = np.array([int(m) % 12 in deg for m in R[:,0]])
    print(f'file: {a.wav.split("/")[-1]}  {len(x)/sr2/60:.1f} min  sr {sr}')
    print(f'notes: {len(R)}  (>=140 ms)   voiced time {dur.sum()/60:.1f} min')
    print(f'center offset |ct|: median {np.median(ab):.1f}  p75 {np.percentile(ab,75):.1f}  p90 {np.percentile(ab,90):.1f}  mean signed {R[:,1].mean():+.1f}')
    for t in (10, 15, 20, 25, 30):
        print(f'  notes off by > {t} ct: {100*(ab>t).mean():.0f} %')
    print(f'in-note drift (p10-p90 range, ct): median {np.median(R[:,2]):.0f}  p75 {np.percentile(R[:,2],75):.0f}  p90 {np.percentile(R[:,2],90):.0f}')
    print(f'out of {a.root} {a.scale}: {100*(~inkey).mean():.0f} % of notes; by pitch class:')
    pcs = {}
    for m, ik in zip(R[:,0], inkey):
        if not ik: pcs[NOTES[int(m)%12]] = pcs.get(NOTES[int(m)%12], 0)+1
    print('   ', dict(sorted(pcs.items(), key=lambda kv:-kv[1])))
    hist = {}
    for m in R[:,0]: hist[NOTES[int(m)%12]] = hist.get(NOTES[int(m)%12], 0)+1
    print('all notes by pitch class:', dict(sorted(hist.items(), key=lambda kv:-kv[1])))
    print('per pitch class: count, median signed offset ct, median drift ct')
    for pc in sorted(set(int(m)%12 for m in R[:,0])):
        sel = (R[:,0].astype(int)%12)==pc
        print(f'   {NOTES[pc]:>3} n={sel.sum():3d}  offset {np.median(R[sel,1]):+5.1f}  drift {np.median(R[sel,2]):4.0f}  dur {np.median(R[sel,3]):.2f}s')
    print(f'range: {NOTES[int(R[:,0].min())%12]}{int(R[:,0].min())//12-1} - {NOTES[int(R[:,0].max())%12]}{int(R[:,0].max())//12-1}')
    # what a Correct Pitch center % leaves behind
    for pct in (25, 30, 35, 40, 45, 50):
        res = ab*(1-pct/100)
        print(f'  center {pct}%: residual median {np.median(res):.1f} ct, notes still > 25 ct: {100*(res>25).mean():.0f} %')

if __name__ == '__main__':
    main()
