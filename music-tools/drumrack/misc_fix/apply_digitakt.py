"""Move Digitakt/Machines/Misc files into their real type folders, using the same new
names as the Ableton side. LinnDrumLM2 was done as the test rack, so it is listed by hand."""
import json,os,shutil
HERE=os.path.dirname(os.path.abspath(__file__))
DT="/Users/amir/Desktop/SAMPLES MAC/Digitakt/Machines"
m={r["old"]:(r["type"],r["new"]) for r in json.load(open(os.path.join(HERE,"misc_renames.json"))) if r.get("new")}
m.update({"Misc 01 LinnDrumLM2.wav":("Cabasa","Cabasa 01 LinnDrumLM2.wav"),
          "Misc 02 LinnDrumLM2.wav":("Cabasa","Cabasa 02 LinnDrumLM2.wav"),
          "Misc 03 LinnDrumLM2.wav":("Sidestick","Sidestick 01 LinnDrumLM2.wav")})
FOLDER={"Kick":"Kicks","Snare":"Snares","HiHat":"HiHats","OpenHat":"OpenHats","Crash":"Cymbals",
        "Ride":"Cymbals","China":"Cymbals","Cymbal":"Cymbals","Clap":"Claps","Tom":"Toms"}
src=os.path.join(DT,"Misc"); moved=[]; problems=[]
for f in sorted(os.listdir(src)):
    if not f.endswith(".wav"): continue
    if f not in m: problems.append("no mapping: "+f); continue
    t,new=m[f]; dst=os.path.join(DT,FOLDER.get(t,"Percs"),new)
    if os.path.exists(dst): problems.append("exists: "+dst); continue
    shutil.move(os.path.join(src,f),dst); moved.append((f,os.path.relpath(dst,DT)))
for a,b in moved: print("  %-34s -> %s"%(a,b))
left=[f for f in os.listdir(src) if not f.startswith(".")]
print("\nmoved %d  problems %d  left in Misc: %d"%(len(moved),len(problems),len(left)))
for p in problems: print("  PROBLEM",p)
if not left:
    for junk in os.listdir(src): os.remove(os.path.join(src,junk))   # only .DS_Store can remain
    os.rmdir(src); print("empty Misc folder removed")
