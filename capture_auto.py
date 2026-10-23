#!/usr/bin/env python3
"""Captura automatica 55a2 (GF3208): detecta el dedo por software, espera a
que asiente y guarda la huella fusionada 52x88. Sin dependencias extra.
sudo python3 capture_auto.py config_win.hex"""
import os, select, socket, subprocess, sys, time, contextlib
import driver_5503 as d
import goodix, tool

PID=0x55A2; FRAME=14788
MODE=bytes.fromhex("0d018b0084008c0088008096809180928085808c8086")
IMG=bytes.fromhex("01008b0084008c008800")
ACTIVE=[c for c in range(112) if c not in (0,53,54,55,56,109,110,111)]
NULL=open(os.devnull,"w")

def read_exact(fd,n,timeout=5):
    buf=b""; end=time.time()+timeout
    while len(buf)<n and time.time()<end:
        r,_,_=select.select([fd],[],[],0.4)
        if r:
            c=os.read(fd,65536)
            if c: buf+=c
    return buf

def grab(dev,cli,fd):
    with contextlib.redirect_stdout(NULL):
        dev.mcu_switch_to_fdt_mode(MODE,True)
        cli.sendall(dev.mcu_get_image(IMG,goodix.FLAGS_TRANSPORT_LAYER_SECURITY_DATA)[9:])
    raw=read_exact(fd,FRAME)
    if len(raw)<FRAME-4: return None
    with contextlib.redirect_stdout(NULL):
        return tool.decode_image(raw[:FRAME-4])

def score(img,base):
    s=0
    for r in range(88):
        for c in ACTIVE: s+=abs(img[r*112+c]-base[r*112+c])
    return s/(88*len(ACTIVE))

def merge(img):
    out=[]
    for r in range(88):
        for k in range(52): out.append((img[r*112+1+k]+img[r*112+57+k])/2.0)
    return out

def write_pgm(px,path,base=None):
    if base is not None:
        mb=merge(base); px=[abs(a-b) for a,b in zip(px,mb)]
    with open(path,"w") as f:
        f.write("P2\n52 88\n4095\n")
        for r in range(88):
            f.write(" ".join("%4d"%int(px[r*52+k]) for k in range(52))+"\n")

def main():
    cfg=bytes.fromhex(open(sys.argv[1]).read().split('#')[0].strip())
    os.system("pkill -f 's_server.*4433' 2>/dev/null"); time.sleep(0.3)
    with contextlib.redirect_stdout(NULL):
        dev=d.init_device(PID)
        if not d.check_psk(dev): d.write_psk(dev)
    srv=subprocess.Popen(["openssl","s_server","-nocert","-psk",d.PSK.hex(),
        "-port","4433","-quiet"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    fd=srv.stdout.fileno()
    try:
        with contextlib.redirect_stdout(NULL):
            dev.reset(True,False,20); dev.read_sensor_register(0x0000,4)
            dev.nop(); dev.read_otp(); dev.pov_image_check()
        cli=socket.socket(); cli.connect(("localhost",4433))
        try:
            with contextlib.redirect_stdout(NULL):
                tool.connect_device(dev,cli); ok=dev.upload_config_mcu(cfg)
                dev.set_drv_state(); dev.set_drv_state(); dev.mcu_get_pov_image()
            print(f"upload_config -> {ok}\nCalibrando fondo (NO toques)...")
            base=grab(dev,cli,fd)
            THR=50.0
            print("Pon el dedo en el sensor...")
            best=None; bests=0; t0=time.time(); plateau=0
            while time.time()-t0<30:
                img=grab(dev,cli,fd)
                if img is None: continue
                sc=score(img,base)
                print(f"  score={sc:7.1f} {'DEDO' if sc>THR else '...'}      ",end="\r",flush=True)
                if sc>THR:
                    if sc>bests*1.01: bests=sc; best=img; plateau=0
                    else: plateau+=1
                    if plateau>=2: break         # score en meseta -> dedo asentado
                elif best is not None: break      # dedo retirado
            print()
            if best is None: print("No se detecto dedo (sube/baja THR)."); return
            print(f"Capturado (score={bests:.1f}).")
            write_pgm(merge(best),"finger_merged.pgm")
            write_pgm(merge(best),"finger_diff.pgm",base=base)
            print("[OK] finger_merged.pgm y finger_diff.pgm")
        finally: cli.close()
    finally: srv.terminate()

if __name__=="__main__": main()
