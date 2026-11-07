"""Change the preset name stored INSIDE a Serum preset file (what Serum's browser shows).
.fxp  (Serum 1): 28-byte prgName at offset 28 + the same name inside the zlib chunk (fixed-width field);
                 byteSize (offset 4) and chunkSize (offset 56) rewritten after recompression.
.serumpreset (Serum 2): "presetName" in the JSON header; u32 LE length at offset 9 rewritten. Body untouched.
Every file is backed up to serum_sort/backups/<same path> before writing."""
import struct,zlib,json,os,re,shutil,sys
HERE=os.path.dirname(os.path.abspath(__file__)); BK=os.path.join(HERE,"backups")
def backup(p):
    t=os.path.join(BK,p.lstrip("/")); os.makedirs(os.path.dirname(t),exist_ok=True)
    if not os.path.exists(t): shutil.copy2(p,t)
def read_name(p):
    d=open(p,'rb').read()
    if d[:4]==b'CcnK': return d[28:56].split(b'\x00')[0].decode('latin1')
    s=d.index(b'{'); e=d.index(b'}',s)+1; return json.loads(d[s:e])["presetName"]
def rename_fxp(p,new):
    """header prgName (28 bytes) + the fixed name field inside the chunk at offset 18802 (34 bytes; parameters follow at 18836, author at 18848)."""
    nb=new.encode('latin1')
    if len(nb)>27: raise ValueError("fxp name max 27 chars: %r"%new)
    d=open(p,'rb').read(); assert d[:4]==b'CcnK' and d[8:12]==b'FPCh'
    raw=bytearray(zlib.decompress(d[60:]))
    NAME_OFF,NAME_END=18802,18832   # name field; parameter floats start at 18832/18836 depending on layout
    if len(raw) not in (172736,28232,34016): raise ValueError("unexpected chunk size %d"%len(raw))
    raw[NAME_OFF:NAME_END]=nb+b'\x00'*(NAME_END-NAME_OFF-len(nb))
    comp=zlib.compress(bytes(raw),9)
    hdr=bytearray(d[:60]); hdr[28:56]=nb+b'\x00'*(28-len(nb))
    body=bytes(hdr)+comp
    body=body[:4]+struct.pack(">I",len(body))+body[8:56]+struct.pack(">I",len(comp))+body[60:]
    assert zlib.decompress(body[60:])==bytes(raw) and body[28:56].split(b'\x00')[0]==nb
    backup(p); open(p,'wb').write(body)
def rename_serumpreset(p,new):
    d=open(p,'rb').read(); s=d.index(b'{'); e=d.index(b'}',s)+1
    assert d[:8]==b'XferJson' and struct.unpack("<I",d[9:13])[0]==e-s, "unexpected header"
    h=json.loads(d[s:e]); h["presetName"]=new
    js=json.dumps(h,separators=(",",":"),ensure_ascii=False).encode('utf-8')
    body=d[:9]+struct.pack("<I",len(js))+d[13:s]+js+d[e:]
    backup(p); open(p,'wb').write(body)
def rename(p,new):
    (rename_fxp if p.lower().endswith(".fxp") else rename_serumpreset)(p,new); return read_name(p)
if __name__=="__main__":
    for p,new in zip(sys.argv[1::2],sys.argv[2::2]): print(os.path.basename(p),"->",rename(p,new))
