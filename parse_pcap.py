#!/usr/bin/env python3
"""Extrae la secuencia de comandos Goodix de una captura usbmon (pcapng).
Uso: python3 parse_pcap.py captura.pcap [dev]  (dev=7 por defecto)"""
import struct, sys
def pcapng(path):
    d=open(path,'rb').read(); off=0; out=[]
    while off+8<=len(d):
        bt,bl=struct.unpack('<II',d[off:off+8]); b=d[off:off+bl]
        if bt==6:
            cl,=struct.unpack('<I',b[20:24]); out.append(b[28:28+cl])
        if bl==0:break
        off+=bl
    return out
def usb(r):
    if len(r)<64:return None
    return dict(ev=r[8:9].decode('latin1'),ep=r[10],dev=r[11],
                data=r[64:64+struct.unpack('<I',r[36:40])[0]])
CMD={0x00:"NOP",0x20:"GET_IMAGE",0x32:"FDT_DOWN",0x34:"FDT_UP",0x36:"FDT_MODE",
0x80:"WRITE_REG",0x82:"READ_REG",0x90:"UPLOAD_CONFIG",0x94:"SET_PDSCAN",0x96:"ENABLE_CHIP",
0xa2:"RESET",0xa4:"ERASE",0xa6:"READ_OTP",0xa8:"FW_VER",0xac:"SET_POV_CFG",0xae:"QUERY_STATE",
0xc4:"SET_DRV_STATE",0xd0:"REQ_TLS",0xd2:"GET_POV_IMG",0xd6:"POV_CHECK",0xe0:"PSK_WRITE",
0xe4:"PSK_READ",0xf6:"IAP_VER"}
dev=int(sys.argv[2]) if len(sys.argv)>2 else 7
recs=[r for p in pcapng(sys.argv[1]) if (r:=usb(p)) and r['dev']==dev]
stream=b"".join(r['data'] for r in recs if r['ev']=='S' and not(r['ep']&0x80) and r['data'])
i=0
while i+4<=len(stream):
    fl=stream[i]; pl=int.from_bytes(stream[i+1:i+3],'little'); ck=stream[i+3]
    if fl in(0xa0,0xb0,0xb2) and pl<=1024 and (sum(stream[i:i+3])&0xff)==ck and i+4+pl<=len(stream):
        body=stream[i+4:i+4+pl]
        if fl==0xa0:
            cmd=body[0]; cl=int.from_bytes(body[1:3],'little')
            print(f"{CMD.get(cmd,hex(cmd)):14} {body[3:3+max(0,cl-1)].hex()}")
        i+=4+pl
    else: i+=1
