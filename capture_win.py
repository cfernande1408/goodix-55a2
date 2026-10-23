#!/usr/bin/env python3
"""Captura 55a2 con config de Windows (DAC calibrado). Geometria 88x112."""
import os, select, socket, subprocess, sys, time
import driver_5503 as d
import goodix, tool

PID=0x55A2
W,H=88,112
FRAME=14788
MODE=bytes.fromhex("0d018b0084008c0088008096809180928085808c8086")
IMG=bytes.fromhex("01008b0084008c008800")

def read_exact(fd,n,timeout=6):
    buf=b""; end=time.time()+timeout
    while len(buf)<n and time.time()<end:
        r,_,_=select.select([fd],[],[],0.5)
        if r:
            c=os.read(fd,65536)
            if c: buf+=c
    return buf

def grab(dev,cli,fd,label):
    dev.mcu_switch_to_fdt_mode(MODE,True)
    cli.sendall(dev.mcu_get_image(IMG,goodix.FLAGS_TRANSPORT_LAYER_SECURITY_DATA)[9:])
    raw=read_exact(fd,FRAME)
    img=tool.decode_image(raw[:FRAME-4]) if len(raw)>=FRAME-4 else tool.decode_image(raw[:len(raw)//6*6])
    nz=sum(1 for v in img if v)
    print(f"   [{label}] bytes={len(raw)} px={len(img)} nz={nz} "
          f"min={min(img) if img else 0} max={max(img) if img else 0}")
    return img

def main():
    cfg=bytes.fromhex(open(sys.argv[1]).read().split('#')[0].strip())
    print("Config:",len(cfg),"B cab",cfg[:1].hex())
    os.system("pkill -f 's_server.*4433' 2>/dev/null"); time.sleep(0.3)
    dev=d.init_device(PID); print("Firmware:",dev.firmware_version())
    if not d.check_psk(dev): d.write_psk(dev)
    srv=subprocess.Popen(["openssl","s_server","-nocert","-psk",d.PSK.hex(),
        "-port","4433","-quiet"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    fd=srv.stdout.fileno()
    try:
        if not dev.reset(True,False,20)[0]: raise SystemExit("reset fail")
        dev.read_sensor_register(0x0000,4); dev.nop(); dev.read_otp(); dev.pov_image_check()
        cli=socket.socket(); cli.connect(("localhost",4433))
        try:
            tool.connect_device(dev,cli)
            print("upload_config ->",dev.upload_config_mcu(cfg))
            dev.set_drv_state(); dev.set_drv_state(); dev.mcu_get_pov_image()
            print("\n[1/2] fondo SIN dedo:")
            e=grab(dev,cli,fd,"empty"); tool.write_pgm(e,W,H,"empty.pgm")
            input("\n>>> dedo FIRME + Enter: ")
            print("[2/2] con dedo:")
            f=grab(dev,cli,fd,"finger"); tool.write_pgm(f,W,H,"finger.pgm")
            if len(e)==len(f) and e:
                diff=[abs(a-b) for a,b in zip(f,e)]
                tool.write_pgm(diff,W,H,"diff.pgm")
                print(f"   [diff] max={max(diff)} (crestas si >300)")
            print("\n[OK] empty.pgm / finger.pgm / diff.pgm")
        finally: cli.close()
    finally: srv.terminate()

if __name__=="__main__": main()
