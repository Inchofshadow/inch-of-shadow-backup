"""Every case below is a real file from SAMPLES MAC that got a wrong or 'Misc' (XX) name in Sep 2026.
Run:  python3 tests/test_detect_type.py"""
import importlib.util, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
s=importlib.util.spec_from_file_location("t",os.path.join(HERE,"..","drumrack_tool_v2.py")); t=importlib.util.module_from_spec(s); s.loader.exec_module(t)

CASES=[  # (filename, machine, expected code)
 # pack prefixes must not beat spelled-out words
 ("SIG_RS_drum_ride_crash_dark_hard.wav",None,"RD"),("TS_SD_crash_ride_smash.wav",None,"CR"),("FL_HT_Shaker_Closer.wav",None,"SH"),
 ("OS_HAF_SFX_C#_Old_Church_Bell_2.wav",None,"BL"),("SULLIVAN_KING_ride_bell_01.wav",None,"RD"),("CC_KickClapCC.wav",None,"BD"),
 # names containing 'rim' inside a word are not rims
 ("Grimes_Snare_02.wav",None,"SD"),("✧ KICK - CRIMINAL.wav",None,"BD"),("Kick (Crimewave) [E].wav",None,"BD"),
 ("Grimes_Hi_Hat_02 (Be a Body).wav",None,"CH"),("Grimes_Open_Hat_05.wav",None,"OH"),("Grimes_Crash_03.wav",None,"CR"),
 ("Grimes_Percussion_02.wav",None,"PC"),("Grimes_Percussion_21 (Skin - Rimshot_2).wav",None,"PC"),  # leftmost word wins; the pack filed it as Percussion
 # glued / abbreviated drum-machine names
 ("CLHAT1_YAMAHA_Rx11.wav","YamahaRX11","CH"),("OPHAT2_YAMAHA_Rx11.wav","YamahaRX11","OH"),("Snaredrum-01.wav",None,"SD"),
 ("UNIVOXsd.wav","Univox","SD"),("UNIVOXbd.wav","Univox","BD"),("UNIVOXch.wav","Univox","CH"),("UNIVOXoh.wav","Univox","OH"),
 ("Yamaha RX7 hard sd2.wav","Yamaha RX7","SD"),("Yamaha RX7 fbd.wav","Yamaha RX7","BD"),("LM1_BD1_aOrig.wav","LM1","BD"),
 # percussion vocabulary that used to fall through to XX
 ("Linn cabasa hard.wav","Linn","CA"),("Linn Sidestick.wav","Linn","RS"),("RX5_Castanet_aOrig.wav","RX5","CS"),
 ("Yamaha RX7 castnet.wav","Yamaha RX7","CS"),("Hitimb_Oberheim_DMX.wav","Oberheim_DMX","TI"),("bong_Oberheim_DMX.wav","Oberheim_DMX","BG"),
 ("Yamaha RX7 agogo hi.wav","Yamaha RX7","AG"),("Yamaha RX7 vibraslap.wav","Yamaha RX7","VS"),("Kawai_R-100_TRIALCH3.wav","Kawai_R-100","TR"),
 ("Kawai_R-100_CHIMECH3.wav","Kawai_R-100","CM"),("Kawai R-50e Finger Snap.wav","Kawai R-50e","SP"),("Finger.wav",None,"SP"),("Linn 9000 stick.wav","Linn 9000","PC"),("Stick_YAMAHA_RY-30.wav","YAMAHA_RY-30","PC"),
 ("RX-120 Cuica Low.wav","RX-120","CU"),("WistlTR-727.wav","TR-727","WH"),("Block.wav",None,"PC"),("Metal.wav",None,"ME"),
 # must keep working exactly as before
 ("TR808_BD_01.wav","TR808","BD"),("CR78_Metal_aOrig_R1.wav","CR78","ME"),("808 Rim.wav",None,"RS"),("Kick 03.wav",None,"BD"),
 ("HH Closed.wav",None,"CH"),("Bass Drum 2.wav",None,"BD"),("Sub Bass C.wav",None,"BS"),("Tom Lo.wav",None,"LT"),("Cowbell.wav",None,"CB"),
 # machine name == instrument word; but a bare pack code must never become a type
 ("Tom 02 Tom.wav","Tom","TM"),("CR78_01.wav","CR78","XX"),
]
bad=[]
for f,m,exp in CASES:
    got=t.detect_type(f,m)[0]
    if got!=exp: bad.append((f,m,got,exp))
for f,m,got,exp in bad: print("FAIL %-46s %-13s got %-3s want %s"%(f,m or "",got,exp))
print("%d of %d wrong"%(len(bad),len(CASES)))
sys.exit(1 if bad else 0)
