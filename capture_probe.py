#!/usr/bin/env python3
"""Diagnostico: muestra el 'score' en vivo (sin dedo vs con dedo).
sudo python3 capture_probe.py config_win.hex"""
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
    with contextlib.redirect_stdout(NULL):      # silencia prints de la libreria
        dev.mcu_switch_to_fdt_mode(MODE,True)
        cli.sendall(dev.mcu_get_image(IMG,goodix.FLAGS_TRANSPORT_LAYER_SECURITY_DATA)[9:])
    raw=read_exact(fd,FRAME)
    if len(raw)<FRAME-4: return None
    with contextlib.redirect_stdout(NULL):
        return tool.decode_image(raw[:FRAME-4])

def score(img,base):
    s=0; n=0
    for r in range(88):
        for c in ACTIVE:
            i=r*112+c; s+=abs(img[i]-base[i]); n+=1
    return s/n

def main():
    cfg=bytes.fromhex(open(sys.argv[1]).read().split('#')[0].strip())
    os.system("pkill -f 's_server.*4433' 2>/dev/null"); time.sleep(0.3)
    with contextlib.redirect_stdout(NULL):
        dev=d.init_device(PID); 
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
            print(f"upload_config -> {ok}")
            print("Calibrando fondo (NO toques, 3 frames)...")
            base=grab(dev,cli,fd)
            print("Ahora MUEVE: deja el sensor libre unos segundos y luego PON EL DEDO.")
            print("Observa el score:\n")
            for i in range(60):
                img=grab(dev,cli,fd)
                if img is None:
                    print(f"{i:2}  (frame vacio)"); continue
                sc=score(img,base)
                bar="#"*int(min(sc,2000)/40)
                print(f"{i:2}  score={sc:7.1f}  {bar}")
        finally: cli.close()
    finally: srv.terminate()

if __name__=="__main__": main()
