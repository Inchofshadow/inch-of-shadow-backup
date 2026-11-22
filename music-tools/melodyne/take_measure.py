"""Per-take pitch measurement for a Live set: reads every take-lane clip (and main lane) of the
audio tracks, maps it to its recorded file via warp markers, and scores pitch per take.
Read-only. Usage: python3 take_measure.py SET.als --root F --scale minor [--tracks "Lead,BV Pad 1"] [--csv out.csv]
"""
import argparse, gzip, os, sys, csv
import xml.etree.ElementTree as ET
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pitch_measure import yin, NOTES, SCALES

_cache = {}
def load(path):
    if path not in _cache:
        sr, x = wavfile.read(path)
        x = np.asarray(x, dtype=np.float64)
        if x.ndim > 1: x = x.mean(1)
        x /= (np.abs(x).max() or 1)
        x = resample_poly(x, 1, 4); sr2 = sr / 4
        f0, rms = yin(x, sr2)
        _cache[path] = (f0, rms, 256 / sr2, rms > max(0.02, np.percentile(rms, 60) * 0.5))
    return _cache[path]

def notes_in(f0, gate, i0, i1):
    cents = 1200*np.log2(f0[i0:i1]/440.0) + 6900
    cents[~gate[i0:i1]] = np.nan
    out, cur = [], []
    for v in cents:
        if np.isnan(v):
            if len(cur) >= 6: out.append(np.array(cur))
            cur = []; continue
        if cur and abs(v - np.median(cur[-5:])) > 60:
            if len(cur) >= 6: out.append(np.array(cur))
            cur = []
        cur.append(v)
    if len(cur) >= 6: out.append(np.array(cur))
    return out

def score(notes, deg):
    rows = []
    for c in notes:
        core = c[len(c)//5: len(c)-len(c)//5] if len(c) >= 10 else c
        ctr = np.median(core); m = int(np.round(ctr/100))
        rows.append((m, ctr - m*100, np.percentile(core, 90) - np.percentile(core, 10)))
    if not rows: return None
    R = np.array(rows); ab = np.abs(R[:, 1])
    return dict(n=len(R), med=np.median(ab), over25=100*(ab > 25).mean(), signed=R[:, 1].mean(),
                drift=np.median(R[:, 2]), outkey=100*np.mean([int(m) % 12 not in deg for m in R[:, 0]]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('als'); ap.add_argument('--root', default='F'); ap.add_argument('--scale', default='minor')
    ap.add_argument('--tracks', default=None); ap.add_argument('--csv', default=None)
    a = ap.parse_args()
    proj = os.path.dirname(os.path.abspath(a.als))
    root = ET.fromstring(gzip.open(a.als).read()).find('LiveSet')
    deg = set((NOTES.index(a.root) + i) % 12 for i in SCALES[a.scale])
    want = [t.strip() for t in a.tracks.split(',')] if a.tracks else None
    out = []
    for tr in root.find('Tracks'):
        if tr.tag != 'AudioTrack': continue
        name = tr.find('Name/EffectiveName').get('Value')
        if want and name not in want: continue
        inp = tr.find('DeviceChain/AudioInputRouting/Target').get('Value').split('/')[-1]
        lanes = [('main', tr.findall('DeviceChain/MainSequencer/Sample/ArrangerAutomation/Events/AudioClip'))]
        for i, l in enumerate(tr.findall('TakeLanes/TakeLanes/TakeLane'), 1):
            lanes.append((f'take {i}', l.findall('.//AudioClip')))
        for lname, clips in lanes:
            for c in clips:
                rp = c.find('.//FileRef/RelativePath')
                if rp is None or 'Recorded' not in rp.get('Value'): continue
                path = os.path.join(proj, rp.get('Value'))
                if not os.path.exists(path) or os.path.getsize(path) < 100000: continue
                wm = [(float(w.get('SecTime')), float(w.get('BeatTime'))) for w in c.findall('WarpMarkers/WarpMarker')]
                (s0, b0), (s1, b1) = wm[0], wm[-1]
                bps = (b1 - b0) / (s1 - s0)
                ls_ = float(c.find('Loop/LoopStart').get('Value'))
                a0, a1 = float(c.find('CurrentStart').get('Value')), float(c.find('CurrentEnd').get('Value'))
                t0 = s0 + (ls_ - b0) / bps; t1 = t0 + (a1 - a0) / bps
                f0, rms, hop, gate = load(path)
                sc = score(notes_in(f0, gate, int(max(t0, 0)/hop), int(t1/hop)), deg)
                bar0, bar1 = a0/4 + 1, a1/4 + 1
                row = dict(track=name, input=inp, lane=lname, clip=c.find('Name').get('Value'),
                           bars=f'{bar0:.0f}-{bar1:.0f}', file=os.path.basename(path), sec=f'{t0:.0f}-{t1:.0f}')
                row.update(sc or dict(n=0))
                out.append(row)
    for r in out:
        if r['n'] < 8:
            print(f"{r['track']:<9}{r['input']:<4}{r['lane']:<8} bars {r['bars']:<8} {r['clip']:<14} notes {r['n']:>3}  (too few to score)")
        else:
            print(f"{r['track']:<9}{r['input']:<4}{r['lane']:<8} bars {r['bars']:<8} {r['clip']:<14} notes {r['n']:>3}  med {r['med']:4.1f}ct  >25ct {r['over25']:3.0f}%  avg {r['signed']:+5.1f}  drift {r['drift']:3.0f}  out-key {r['outkey']:3.0f}%")
    if a.csv:
        with open(a.csv, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=sorted({k for r in out for k in r})); w.writeheader(); w.writerows(out)

if __name__ == '__main__':
    main()
