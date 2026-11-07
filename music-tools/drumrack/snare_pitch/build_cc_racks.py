"""Build the two CC Snares racks from cc_racks_plan.csv. Originals are only read.
Writes: named full-quality copies   SAMPLES MAC/CC Snares/CC Snares 1|2/<note> <name>.wav  (the racks point here)
        Digitakt copies (48k/16 mono, -6 dB peak, like the rest of that set)  SAMPLES MAC/Digitakt/CC Snares/
        racks  User Library/User - Drum Racks/CC Snares/CC Snares 1|2.adg  (pads sorted low to high from C1)"""
import os,sys,csv,shutil,math
import soundfile as sf
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from drumrack_tool_v2 import write_adg, convert_for_digitakt
SAMPLES="/Users/amir/Desktop/SAMPLES MAC"
COPIES=os.path.join(SAMPLES,"CC Snares"); DT=os.path.join(SAMPLES,"Digitakt","CC Snares")
RACKS=os.path.expanduser("~/Music/Ableton/User Library/User - Drum Racks/CC Snares")
NAMES={  # source stem -> short pad name
 "CC_LSnare":"CC LSnare","Snare (Love And Caring)":"CC Love And Caring","Snare (Fleece)":"CC Fleece","Snare (Birds)":"CC Birds",
 "ULTIMATE_CC - snare - 14":"CC Ultimate 14","Snare (Crimewave)":"CC Crimewave","Snare (Good Time)":"CC Good Time",
 "Snare (Alice Practice)":"CC Alice Practice","Snare (Vanished)":"CC Vanished","CC_VSnare":"CC VSnare","ULTIMATE_CC - snare - 11":"CC Ultimate 11",
 "OLIVER_snare_clean_puncher":"Oliver Clean Puncher","@skeletone.store Witch House - Snare 6":"WH Skeletone 6",
 "TrTrap2_-_Snare-808_-_028":"TrTrap 808 028","Tom_SD_Int_aOrig":"SCI Tom SD","Snare 30":"ZeroG1 Snare 30","Snare 76":"ZeroG1 Snare 76",
 "Snare 5":"ZeroG1 Snare 5","OLIVER_snare_funk_puncher":"Oliver Funk Puncher","Snare 2":"ZeroG1 Snare 2",
 "OLIVER_snare_tight_control":"Oliver Tight Control","@skeletone.store Witch House - Snare 12":"WH Skeletone 12",
 "91V_AC_snare_hoard":"Angelcore Hoard","Sequentil_Circuit_TOM_Snare":"SCI TOM Snare","rf_insp130_downforce_F_snr":"Downforce Snr",
 "OLIVER_snare_timeless_pop":"Oliver Timeless Pop","TR505_SD_aOrig":"TR-505 SD","Snare 54":"ZeroG1 Snare 54",
 "TS_ADD_snare_crisp":"Analog Dance Crisp","RPM40_Snare1_aOrig":"RPM-40 Snare 1","@skeletone.store Witch House - Snare 4":"WH Skeletone 4",
 "Snare 47":"ZeroG1 Snare 47","Snare3_Oberheim_DMX":"DMX Snare 3","Akai XR-10 snare_07":"XR-10 Snare 07",
 "TS_ADD_snare_dry_room":"Analog Dance Dry Room","TRNSNT1 Snares & Claps Simple 010":"Eitan Simple 010","Snare2_Oberheim_DMX":"DMX Snare 2",
 "DS_LENNO_drum_snare_choice":"Lenno Choice","✧ SNARE - TORN":"WH Torn","TrTrap2_-_Snare-808_-_088":"TrTrap 808 088",
 "OLIVER_snare_mixready_slamborghini_xl":"Oliver Slamborghini","@skeletone.store Witch House - Snare 7":"WH Skeletone 7",
 "Snare 73":"ZeroG1 Snare 73","BOS_DHT_Snare_One_Shot_Hard_A#":"Dark Techno Hard","✧CYBRSNARE":"WH Cybrsnare",
 "Snare [D#] 13":"ZeroG1 Snare 13","BOS_LevIV_Snare_One_Shot_Short_Easy_D":"Leviathan Short Easy","DR110_SD_X2_C2S":"DR-110 SD",
 "KSHMR_Tight_Snare_36_F#":"KSHMR Tight 36","ZEN_MEL_snare_one_shot_classicniner":"Modern Electro Niner","Snare 29":"ZeroG1 Snare 29",
 "cs_kb800_snare_drum":"KB-800 Snare","RPM40_Snare2_aOrig":"RPM-40 Snare 2","NW_ESSA_snare_attack":"Electric Sunset Attack",
 "Snare 75":"ZeroG1 Snare 75","Snare 81":"ZeroG1 Snare 81","SD 20_Roland_R8":"R8 SD 20","91V_CC_snare_tight_mid":"Cruise Tight Mid","91V_AC_snare_slow":"Angelcore Slow",
 "TrTrap2_-_Snare-Hybrid_-_043":"TrTrap Hybrid 043","Kawai R-50e Ac. Snare":"R-50e Ac Snare","OLIVER_one_shot_snare_punchy_03":"Oliver Punchy 03",
}
ZG2={"Snare 7":"ZeroG2 Snare 7","Snare 1":"ZeroG2 Snare 1"}   # same stems on Disc 2
NN=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
def midi(n): n=n.split()[0]; return NN.index(n[:-1])+12*(int(n[-1])+2)
plan=list(csv.DictReader(open("cc_racks_plan.csv")))
if os.path.exists(COPIES) or os.path.exists(DT) or os.path.exists(RACKS): sys.exit("output folder already exists, stopping")
log=[]
for k in ("1","2"):
    rows=[r for r in plan if r["rack"]==k]
    rows.sort(key=lambda r:(midi(r["note"]),r["distance"]!="CC",r["distance"]))
    cdir=os.path.join(COPIES,"CC Snares "+k); os.makedirs(cdir); os.makedirs(DT,exist_ok=True)
    pads=[]
    for i,r in enumerate(rows):
        stem=os.path.splitext(os.path.basename(r["file"]))[0]
        nm=ZG2[stem] if ("DISC 2" in r["file"] and stem in ZG2) else NAMES[stem]
        name="%s %s"%(r["note"].split()[0],nm)
        dst=os.path.join(cdir,name+os.path.splitext(r["file"])[1].lower())
        if os.path.exists(dst): sys.exit("name clash: "+dst)
        shutil.copy2(r["file"],dst)
        convert_for_digitakt(r["file"],os.path.join(DT,name+".wav"))
        info=sf.info(dst)
        pads.append(dict(note=36+i,name=name,path=dst,frames=info.frames,sr=info.samplerate))
        log.append([k,NN[(36+i)%12]+str((36+i)//12-2),name,r["file"],dst])
    os.makedirs(RACKS,exist_ok=True)
    write_adg(os.path.join(RACKS,"CC Snares %s.adg"%k),pads)
with open("cc_racks_built.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["rack","pad","name","original","copy"]); w.writerows(log)
with open("undo_cc_racks.sh","w") as fh:
    fh.write("#!/bin/sh\n# removes only what build_cc_racks.py created; originals were never touched\n")
    for p in (COPIES,DT,RACKS): fh.write('rm -rf "%s"\n'%p)
print("built",len(log),"pads")
