#!/usr/bin/env python3
"""
drumrack_tool.py -- Audition, curate, rename and rack drum-machine one-shots,
                    and build Ableton Drum Racks. Digitakt-ready too.

TWO STEPS:

  1) SCAN  -- analyze a library and build a self-contained audition web page per
              machine. Open it, play each sample, tick the ones you want to keep,
              and click "Download picks". Nothing is copied or renamed in this step.

        python drumrack_tool.py scan "/path/to/SAMPLES MAC"

  2) BUILD -- after you've saved your picks, build clean-renamed copies + one
              Ableton Drum Rack (.adg) per machine, using ONLY the samples you kept.

        python drumrack_tool.py build "/path/to/SAMPLES MAC"
        python drumrack_tool.py build "/path/to/SAMPLES MAC" --convert

NON-DESTRUCTIVE: your original files are never renamed or moved (so existing
Ableton projects keep working) unless you explicitly pass --in-place.

Each immediate sub-folder of the library is treated as one machine. Use --flat to
point either command at a single machine's folder directly.

Requires:  pip install numpy soundfile scipy
"""
import os, sys, re, gzip, base64, argparse, csv, shutil, math, io, json, html
import numpy as np
import soundfile as sf
try:
    from scipy.signal import resample_poly
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

# ---- embedded Ableton Drum Rack template (from a real Live 12.3 rack) ----
_HEAD   = gzip.decompress(base64.b64decode("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")).decode()
_BRANCH = gzip.decompress(base64.b64decode("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")).decode()
_TAIL   = gzip.decompress(base64.b64decode("H4sIAIOcQWoC/+Pi5LTRdypKzEvOCChKLU4tKbbjAgoFpZaUFuWhiCvoA2Vs9N2L8ksLXFLLMpNTIRJ2XDb6jkk5qSX5eXZcAA9fiaZPAAAA")).decode()
T_BASENAME = "RX5_Kick_03_aOrig"
T_PATH_PRIMARY = "/Users/amir/Music/Ableton/User Library/Samples/Imported/RX5_Kick_03_aOrig.wav"
T_PATH_SOURCE  = "/Users/amir/Desktop/SAMPLES MAC/Tape Drum Machines Vol.2/Samples/RX-5/RX5_Kick_03_aOrig.wav"

AUDIO_EXT = (".wav", ".aif", ".aiff", ".flac")

# ---------------------------------------------------------------- type detection
TYPE_RULES = [
    (r"\b(bd|kick|bassdrum|bass_drum|kik|bdrum)\b", "BD", True),
    (r"\b(sd|snare|snr|sn)\b",                       "SD", False),
    (r"\b(rim|rimshot|rs)\b",                        "RS", False),
    (r"\b(clap|clp|cp|hclp)\b",                      "CP", False),
    (r"\b(oh|ohh|openhat|open_hat|hho)\b",           "OH", False),
    (r"\b(ch|chh|closedhat|closed_hat|hh|hhc|hat|hihat)\b", "CH", False),
    (r"\b(ride|rd|ride_cymbal)\b",                   "RD", False),
    (r"\b(crash|cr|crsh)\b",                         "CR", False),
    (r"\b(cym|cymbal|cy)\b",                         "CY", False),
    (r"\b(lt|lowtom|low_tom|tom_lo|toml)\b",         "LT", True),
    (r"\b(mt|midtom|mid_tom|tom_mid|tomm)\b",        "MT", True),
    (r"\b(ht|hitom|hi_tom|high_tom|tom_hi|tomh)\b",  "HT", True),
    (r"\b(tom|tm)\b",                                "TM", True),
    (r"\b(cb|cowbell|cow)\b",                        "CB", True),
    (r"\b(clave|cl|clav)\b",                         "CL", True),
    (r"\b(conga|cga|cng)\b",                         "CG", True),
    (r"\b(bongo|bng)\b",                             "BG", True),
    (r"\b(shaker|shk|sh)\b",                         "SH", False),
    (r"\b(tamb|tambourine|tmb|tb)\b",                "TB", False),
    (r"\b(maraca|mar|mrc)\b",                        "MA", False),
    (r"\b(perc|prc|pc)\b",                           "PC", False),
    (r"\b(fx|sfx|effect|noise)\b",                   "FX", False),
]
TYPE_LABEL = {"BD":"Kick","SD":"Snare","RS":"Rimshot","CP":"Clap","CH":"Closed Hat",
    "OH":"Open Hat","RD":"Ride","CR":"Crash","CY":"Cymbal","LT":"Low Tom","MT":"Mid Tom",
    "HT":"Hi Tom","TM":"Tom","CB":"Cowbell","CL":"Clave","CG":"Conga","BG":"Bongo",
    "SH":"Shaker","TB":"Tambourine","MA":"Maraca","PC":"Perc","FX":"FX","XX":"?"}
TONAL_BAND = {"BD":(30,250),"TM":(60,400),"LT":(50,250),"MT":(70,320),"HT":(90,450),
    "CB":(200,1500),"CL":(200,2500),"CG":(80,600),"BG":(120,900)}
ORDER = ["BD","SD","RS","CP","CH","OH","RD","CR","CY","LT","MT","HT","TM",
         "CB","CL","CG","BG","SH","TB","MA","PC","FX","XX"]

def detect_type(filename):
    low = " " + re.sub(r"[^a-z0-9]+", " ", filename.lower()) + " "
    for pat, code, tonal in TYPE_RULES:
        if re.search(pat, low):
            return code, tonal
    return "XX", False

# ---------------------------------------------------------------- pitch / notes
NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
OCTAVE_OFFSET = {"ableton": -2, "scientific": -1}
OCTAVE_MODE = "ableton"

def hz_to_note(f):
    if not f or f <= 0:
        return None, None, None
    midi = 69 + 12 * math.log2(f / 440.0)
    m = int(round(midi))
    cents = int(round((midi - m) * 100))
    return f"{NOTE_NAMES[m % 12]}{m // 12 + OCTAVE_OFFSET[OCTAVE_MODE]}", m, cents

def note_to_midi(token):
    mm = re.match(r"^([A-Ga-g])(#|b)?(-?\d+)$", token.strip())
    if not mm:
        return None
    base = {"c":0,"d":2,"e":4,"f":5,"g":7,"a":9,"b":11}[mm.group(1).lower()]
    if mm.group(2) == "#": base += 1
    if mm.group(2) == "b": base -= 1
    return base + (int(mm.group(3)) - OCTAVE_OFFSET[OCTAVE_MODE]) * 12

def _autocorr_pitch(seg, sr, lo, hi):
    seg = seg - np.mean(seg)
    if np.max(np.abs(seg)) < 1e-9:
        return None
    n = len(seg); seg = seg * np.hanning(n)
    nfft = 1 << int(math.ceil(math.log2(2 * n)))
    spec = np.fft.rfft(seg, nfft)
    acf = np.fft.irfft(spec * np.conj(spec), nfft)[:n]
    min_lag = max(2, int(sr / hi)); max_lag = min(n - 1, int(sr / lo))
    if max_lag <= min_lag:
        return None
    lag = min_lag + int(np.argmax(acf[min_lag:max_lag + 1]))
    if 1 <= lag < n - 1:
        a0, b0, c0 = acf[lag-1], acf[lag], acf[lag+1]
        d = (a0 - 2*b0 + c0)
        lag = lag + (0.5 * (a0 - c0) / d if d else 0.0)
    return sr / lag if lag else None

def get_fundamental(y, sr, band):
    if y.ndim > 1:
        y = y.mean(axis=1)
    y = y.astype(np.float64)
    peak = np.max(np.abs(y))
    if peak < 1e-6:
        return None
    y = y / peak
    above = np.where(np.abs(y) > 0.02)[0]
    if len(above) < 2:
        return None
    start, end = above[0], above[-1]
    lo, hi = band
    a = max(start + int(0.40 * (end - start)), start + int(0.012 * sr))
    min_len = int(4 * sr / lo)
    if end - a < min_len:
        a = max(start + int(0.012 * sr), end - min_len)
    seg = y[a:end + 1]
    if len(seg) < int(sr / hi) * 4:
        return None
    f = _autocorr_pitch(seg, sr, lo, hi)
    if f is None or f < lo * 0.5 or f > hi * 1.5:
        return None
    return float(f)

# ---------------------------------------------------------------- analysis
def analyze_file(fp):
    try:
        info = sf.info(fp)
    except Exception as e:
        return None
    code, tonal = detect_type(os.path.basename(fp))
    hz = note = cents = None
    if tonal:
        try:
            y, _ = sf.read(fp, always_2d=False)
            hz = get_fundamental(np.asarray(y), info.samplerate, TONAL_BAND.get(code,(40,500)))
            if hz:
                note, _m, cents = hz_to_note(hz)
        except Exception:
            pass
    return dict(fp=os.path.abspath(fp), sr=info.samplerate, frames=info.frames,
                ch=info.channels, code=code, tonal=tonal, hz=hz, note=note, cents=cents,
                seconds=round(info.frames / info.samplerate, 3))

def analyze_machine(files):
    out = [a for a in (analyze_file(f) for f in files) if a]
    out.sort(key=lambda d: (ORDER.index(d["code"]) if d["code"] in ORDER else 99,
                            os.path.basename(d["fp"]).lower()))
    return out

# ---------------------------------------------------------------- audio preview
def make_preview_datauri(fp, max_sr=22050, max_seconds=2.5):
    y, sr = sf.read(fp, always_2d=True)
    y = y.mean(axis=1)
    if len(y) > int(max_seconds * sr):
        y = y[:int(max_seconds * sr)]
    if sr > max_sr:
        if HAVE_SCIPY:
            g = math.gcd(int(sr), max_sr)
            y = resample_poly(y, max_sr // g, sr // g)
        else:
            n = int(round(len(y) * max_sr / sr))
            y = np.interp(np.linspace(0, len(y)-1, n), np.arange(len(y)), y)
        sr = max_sr
    peak = np.max(np.abs(y)) if len(y) else 0
    if peak > 0:
        y = 0.98 * y / peak
    buf = io.BytesIO()
    sf.write(buf, y.astype(np.float32), sr, format="WAV", subtype="PCM_16")
    return "data:audio/wav;base64," + base64.b64encode(buf.getvalue()).decode()

# ---------------------------------------------------------------- audition HTML
HTML_TMPL = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Audition — __MACHINE__</title>
<style>
  :root{color-scheme:dark}
  body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#15171c;color:#e8eaed}
  header{position:sticky;top:0;background:#1d2026;border-bottom:1px solid #2c3038;padding:14px 20px;z-index:5}
  h1{font-size:18px;margin:0 0 6px}
  .sub{color:#9aa0aa;font-size:13px}
  .bar{margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  button{background:#2a2e37;color:#e8eaed;border:1px solid #3a3f4a;border-radius:8px;padding:7px 12px;font-size:13px;cursor:pointer}
  button:hover{background:#343945}
  button.primary{background:#3b82f6;border-color:#3b82f6;color:#fff}
  button.primary:hover{background:#2f6fd6}
  .count{margin-left:auto;font-size:13px;color:#9aa0aa}
  table{width:100%;border-collapse:collapse}
  td,th{padding:9px 14px;border-bottom:1px solid #23262d;text-align:left;font-size:14px}
  th{position:sticky;top:96px;background:#1d2026;color:#9aa0aa;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
  tr.kept{background:#171b22}
  tr.dropped{opacity:.4}
  .play{width:34px;height:34px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;padding:0;font-size:13px}
  .play.on{background:#3b82f6;border-color:#3b82f6;color:#fff}
  .ty{display:inline-block;min-width:30px;padding:2px 8px;border-radius:6px;background:#2a2e37;font-size:12px;text-align:center}
  .note{color:#86efac;font-variant-numeric:tabular-nums}
  .muted{color:#6b7280;font-size:12px}
  input[type=checkbox]{width:18px;height:18px;accent-color:#3b82f6}
  .fname{font-family:ui-monospace,Menlo,monospace;font-size:12.5px}
</style></head>
<body>
<header>
  <h1>__MACHINE__ <span class="muted">— audition &amp; pick</span></h1>
  <div class="sub">Play each sample, untick the ones you don't want, then download your picks.</div>
  <div class="bar">
    <button onclick="all(true)">Keep all</button>
    <button onclick="all(false)">Drop all</button>
    <button onclick="keepType('BD')">Only kicks</button>
    <button onclick="invert()">Invert</button>
    <button class="primary" onclick="download_()">⬇ Download picks</button>
    <span class="count"><span id="n">0</span> kept</span>
  </div>
</header>
<table>
  <thead><tr><th></th><th>Keep</th><th>Type</th><th>Note</th><th>Length</th><th>File</th></tr></thead>
  <tbody id="rows"></tbody>
</table>
<audio id="player"></audio>
<script>
const MACHINE = __MACHINE_JSON__;
const SAMPLES = __SAMPLES_JSON__;
const player = document.getElementById('player');
let playing = null;
function rows(){return document.querySelectorAll('#rows tr');}
function render(){
  const tb=document.getElementById('rows'); tb.innerHTML='';
  SAMPLES.forEach((s,i)=>{
    const tr=document.createElement('tr'); tr.dataset.i=i;
    tr.innerHTML=`<td><button class="play" data-i="${i}">▶</button></td>
      <td><input type="checkbox" ${s.keep?'checked':''} data-i="${i}"></td>
      <td><span class="ty">${s.code}</span> <span class="muted">${s.label}</span></td>
      <td class="note">${s.note?s.note+(s.cents?` <span class="muted">${s.cents>0?'+':''}${s.cents}c</span>`:''):'<span class=muted>—</span>'}</td>
      <td class="muted">${s.seconds}s</td>
      <td class="fname">${s.name}</td>`;
    tb.appendChild(tr);
  });
  tb.querySelectorAll('input[type=checkbox]').forEach(c=>c.addEventListener('change',e=>{
    SAMPLES[+e.target.dataset.i].keep=e.target.checked; paint();}));
  tb.querySelectorAll('.play').forEach(b=>b.addEventListener('click',e=>play(+e.currentTarget.dataset.i)));
  paint();
}
function play(i){
  document.querySelectorAll('.play').forEach(b=>{b.textContent='▶';b.classList.remove('on');});
  if(playing===i){playing=null;player.pause();return;}
  playing=i; const b=document.querySelector(`.play[data-i="${i}"]`); b.textContent='⏸'; b.classList.add('on');
  player.src=SAMPLES[i].audio; player.play();
}
player.addEventListener('ended',()=>{document.querySelectorAll('.play').forEach(b=>{b.textContent='▶';b.classList.remove('on');});playing=null;});
function paint(){
  let n=0;
  rows().forEach(tr=>{const s=SAMPLES[+tr.dataset.i];tr.className=s.keep?'kept':'dropped';if(s.keep)n++;});
  document.getElementById('n').textContent=n;
}
function all(v){SAMPLES.forEach(s=>s.keep=v);render();}
function invert(){SAMPLES.forEach(s=>s.keep=!s.keep);render();}
function keepType(t){SAMPLES.forEach(s=>s.keep=(s.code===t));render();}
function download_(){
  const keep=SAMPLES.filter(s=>s.keep).map(s=>s.path);
  const blob=new Blob([JSON.stringify({machine:MACHINE,keep:keep},null,2)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=MACHINE+'.picks.json';a.click();
}
render();
</script>
</body></html>
"""

def build_audition_html(machine, analyzed, out):
    samples = []
    for d in analyzed:
        try:
            audio = make_preview_datauri(d["fp"])
        except Exception:
            audio = ""
        samples.append({
            "path": d["fp"],
            "name": os.path.basename(d["fp"]),
            "code": d["code"],
            "label": TYPE_LABEL.get(d["code"], d["code"]),
            "note": d["note"] or "",
            "cents": d["cents"] if d["cents"] is not None else "",
            "seconds": d["seconds"],
            "keep": True,
            "audio": audio,
        })
    page = (HTML_TMPL
            .replace("__MACHINE__", html.escape(machine))
            .replace("__MACHINE_JSON__", json.dumps(machine))
            .replace("__SAMPLES_JSON__", json.dumps(samples)))
    ad = os.path.join(out, "audition")
    os.makedirs(ad, exist_ok=True)
    path = os.path.join(ad, f"{machine}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return path

# ---------------------------------------------------------------- .adg builder
def build_branch(idx, note, basename, abspath, frames, sr):
    s = _BRANCH
    s = s.replace(T_PATH_PRIMARY, abspath).replace(T_PATH_SOURCE, abspath)
    s = re.sub(r'(<BrowserContentPath Value=")[^"]*(")', r'\g<1>\g<2>', s)
    fname = os.path.basename(abspath)
    s = s.replace("Samples/Imported/" + T_BASENAME + ".wav", fname)
    s = re.sub(r'(<RelativePath Value=")[^"]*'+re.escape(T_BASENAME)+r'[^"]*(")', r'\g<1>'+fname+r'\g<2>', s)
    s = s.replace(T_BASENAME, basename)
    s = re.sub(r'(<OriginalFileSize Value=")\d+(")', r'\g<1>0\g<2>', s)
    s = re.sub(r'(<OriginalCrc Value=")\d+(")',      r'\g<1>0\g<2>', s)
    s = re.sub(r'(<DefaultDuration Value=")\d+(")',  r'\g<1>'+str(int(frames))+r'\g<2>', s)
    s = re.sub(r'(<DefaultSampleRate Value=")\d+(")',r'\g<1>'+str(int(sr))+r'\g<2>', s)
    s = re.sub(r'(<ReceivingNote Value=")-?\d+(")',  r'\g<1>'+str(int(note))+r'\g<2>', s)
    s = re.sub(r'(<DrumBranchPreset Id=")\d+(")',    r'\g<1>'+str(int(idx))+r'\g<2>', s, count=1)
    return s

def write_adg(path, pads):
    sep = "\n\t\t\t"
    branches = [build_branch(i, p["note"], p["name"], p["path"], p["frames"], p["sr"])
                for i, p in enumerate(pads)]
    xml = _HEAD + sep.join(branches) + _TAIL
    with gzip.open(path, "wb") as f:
        f.write(xml.encode("utf-8"))

# ---------------------------------------------------------------- conversion
def convert_for_digitakt(src, dst):
    y, sr = sf.read(src, always_2d=True); y = y.mean(axis=1)
    if sr != 48000:
        if HAVE_SCIPY:
            g = math.gcd(int(sr), 48000); y = resample_poly(y, 48000 // g, sr // g)
        else:
            n = int(round(len(y) * 48000 / sr)); y = np.interp(np.linspace(0,len(y)-1,n), np.arange(len(y)), y)
        sr = 48000
    peak = np.max(np.abs(y)) if len(y) else 0
    if peak > 1.0: y = y / peak
    sf.write(dst, y, sr, subtype="PCM_16")

# ---------------------------------------------------------------- folder walk
def sanitize(name):
    return re.sub(r"[^A-Za-z0-9]+", "", name) or "Machine"

def gather(root, flat):
    machines = {}
    if flat:
        files = [os.path.join(root,f) for f in os.listdir(root) if f.lower().endswith(AUDIO_EXT)]
        if files:
            machines[sanitize(os.path.basename(os.path.normpath(root)))] = sorted(files)
        return machines
    for entry in sorted(os.listdir(root)):
        d = os.path.join(root, entry)
        if not os.path.isdir(d):
            continue
        files = []
        for dp,_,fns in os.walk(d):
            for fn in fns:
                if fn.lower().endswith(AUDIO_EXT):
                    files.append(os.path.join(dp, fn))
        if files:
            machines[sanitize(entry)] = sorted(files)
    return machines

# ---------------------------------------------------------------- SCAN
def cmd_scan(args):
    root = os.path.abspath(args.library)
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "_DrumRackTool")
    os.makedirs(out, exist_ok=True)
    machines = gather(root, args.flat)
    if not machines:
        sys.exit("No audio files found. (Did you mean --flat?)")
    print(f"Scanning {len(machines)} machine(s) -> audition pages in {os.path.join(out,'audition')}\n")
    rows = []
    for m, files in machines.items():
        print(f"[{m}] {len(files)} file(s) ...", end=" ", flush=True)
        analyzed = analyze_machine(files)
        page = build_audition_html(m, analyzed, out)
        print(f"-> audition/{m}.html")
        for d in analyzed:
            rows.append([m, os.path.basename(d["fp"]), d["code"],
                         "" if d["hz"] is None else f"{d['hz']:.1f}", d["note"] or "",
                         "" if d["cents"] is None else f"{d['cents']:+d}", d["seconds"], d["sr"], d["ch"]])
    with open(os.path.join(out,"report.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["machine","file","type","pitch_hz","note","cents","seconds","samplerate","channels"]); w.writerows(rows)
    print(f"\nOpen the .html pages in {os.path.join(out,'audition')} , tick what you want,")
    print("click 'Download picks' for each, then run the BUILD step.")
    print(f"(By default build reads picks from your Downloads folder and {os.path.join(out,'picks')}.)")

# ---------------------------------------------------------------- picks
def load_picks(out, libroot):
    picks = {}
    dirs = [os.path.join(out,"picks"), os.path.join(out,"audition"), libroot,
            os.path.expanduser("~/Downloads"), os.getcwd()]
    seen = set()
    for d in dirs:
        if not d or not os.path.isdir(d) or d in seen:
            continue
        seen.add(d)
        for fn in os.listdir(d):
            if not fn.endswith(".picks.json"):
                continue
            try:
                data = json.load(open(os.path.join(d, fn)))
            except Exception:
                continue
            m = data.get("machine"); keep = data.get("keep", [])
            if m:
                picks.setdefault(m, set()).update(os.path.abspath(p) for p in keep)
    return picks

# ---------------------------------------------------------------- BUILD
def cmd_build(args):
    global OCTAVE_MODE
    OCTAVE_MODE = args.octave
    root = os.path.abspath(args.library)
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "_DrumRackTool")
    os.makedirs(out, exist_ok=True)
    machines = gather(root, args.flat)
    if not machines:
        sys.exit("No audio files found. (Did you mean --flat?)")
    picks = load_picks(out, root)
    if picks:
        print(f"Loaded picks for: {', '.join(sorted(picks))}\n")
    elif not args.all:
        sys.exit("No '*.picks.json' files found. Run 'scan' first and download your picks,\n"
                 "or pass --all to build every sample.")

    map_start = note_to_midi(args.map_start) or 36
    tune_root = note_to_midi(args.tune_root) if args.tune_root else None
    all_rows = []
    for m, files in machines.items():
        analyzed = analyze_machine(files)
        keepset = picks.get(m)
        if keepset is not None:
            analyzed = [d for d in analyzed if d["fp"] in keepset]
        elif not args.all:
            print(f"[{m}] no picks — skipped")
            continue
        if not analyzed:
            print(f"[{m}] nothing kept — skipped")
            continue
        all_rows += process_machine(m, analyzed, args, out, map_start, tune_root)

    with open(os.path.join(out,"build_report.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["machine","original","renamed","type","pitch_hz","note","cents","seconds","samplerate","channels"]); w.writerows(all_rows)
    print(f"\nDone. {len(all_rows)} samples built.")
    print(f"  Renamed copies : {os.path.join(out,'renamed')}")
    if args.convert: print(f"  Digitakt copies: {os.path.join(out,'digitakt')}")
    print(f"  Drum Racks     : {os.path.join(out,'racks')}  (drag a .adg into Live)")
    if not args.in_place: print("\nYour original files were not touched.")

def process_machine(machine, analyzed, args, out, map_start, tune_root):
    rows=[]; counters={}; pads=[]; note=map_start
    ren_dir=os.path.join(out,"renamed",machine); dig_dir=os.path.join(out,"digitakt",machine)
    os.makedirs(ren_dir,exist_ok=True)
    if args.convert: os.makedirs(dig_dir,exist_ok=True)
    for d in analyzed:
        code=d["code"]; counters[code]=counters.get(code,0)+1; nn=f"{counters[code]:02d}"
        ptag=("_"+d["note"].replace("#","s")) if (d["note"] and args.pitch_tag) else ""
        base=(f"{code}_{machine}{ptag}_{nn}" if args.name_order=="type" else f"{machine}_{code}{ptag}_{nn}")
        newname=base+".wav"
        if args.in_place:
            dst=os.path.join(os.path.dirname(d["fp"]), base+os.path.splitext(d["fp"])[1])
            if os.path.abspath(dst)!=d["fp"]: os.rename(d["fp"],dst)
            rack_path=dst
        else:
            dst=os.path.join(ren_dir,newname)
            if d["fp"].lower().endswith(".wav"): shutil.copy2(d["fp"],dst)
            else:
                y,sr=sf.read(d["fp"]); sf.write(dst,y,sr)
            rack_path=dst
        if args.convert: convert_for_digitakt(d["fp"], os.path.join(dig_dir,newname))
        pads.append(dict(note=note, name=base, path=os.path.abspath(rack_path), frames=d["frames"], sr=d["sr"]))
        note+=1
        rows.append([machine, os.path.basename(d["fp"]), newname, code,
                     "" if d["hz"] is None else f"{d['hz']:.1f}", d["note"] or "",
                     "" if d["cents"] is None else f"{d['cents']:+d}", d["seconds"], d["sr"], d["ch"]])
    if pads:
        os.makedirs(os.path.join(out,"racks"),exist_ok=True)
        write_adg(os.path.join(out,"racks",f"{machine}.adg"), pads)
        print(f"[{machine}] {len(pads)} pad(s) -> racks/{machine}.adg")
    return rows

# ---------------------------------------------------------------- CLI
def main():
    ap=argparse.ArgumentParser(description="Audition, curate, rename and rack drum-machine one-shots.")
    sub=ap.add_subparsers(dest="cmd", required=True)

    sc=sub.add_parser("scan", help="analyze a library and build audition web pages")
    sc.add_argument("library"); sc.add_argument("--out", default=None)
    sc.add_argument("--flat", action="store_true", help="treat the folder itself as one machine")
    sc.add_argument("--octave", choices=["ableton","scientific"], default="ableton")
    sc.set_defaults(func=cmd_scan)

    bd=sub.add_parser("build", help="build renamed copies + Drum Racks from your picks")
    bd.add_argument("library"); bd.add_argument("--out", default=None)
    bd.add_argument("--flat", action="store_true")
    bd.add_argument("--all", action="store_true", help="build every sample (ignore picks)")
    bd.add_argument("--convert", action="store_true", help="also write Digitakt 48k/16-bit mono copies")
    bd.add_argument("--name-order", choices=["machine","type"], default="machine")
    bd.add_argument("--in-place", action="store_true", help="rename originals (destructive)")
    bd.add_argument("--no-pitch-tag", dest="pitch_tag", action="store_false")
    bd.add_argument("--tune-root", default=None)
    bd.add_argument("--map-start", default="C1")
    bd.add_argument("--octave", choices=["ableton","scientific"], default="ableton")
    bd.set_defaults(func=cmd_build, pitch_tag=True)

    # scan needs octave too for note labels
    args=ap.parse_args()
    if args.cmd=="scan":
        global OCTAVE_MODE; OCTAVE_MODE=args.octave
    args.func(args)

if __name__=="__main__":
    main()
