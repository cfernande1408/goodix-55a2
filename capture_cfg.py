#!/usr/bin/env python3
"""Captura 55a2 con un DEVICE_CONFIG dado. Lee con timeout y reporta si trae datos."""
import os, select, socket, subprocess, sys, time
import driver_5503 as d
import goodix, tool

PID = 0x55A2
MODE = bytes.fromhex("0d018b0084008c0088008096809180928085808c8086")
IMG_PAYLOAD = bytes.fromhex("01008b0084008c008800")


def read_until_idle(fd, idle=1.5, cap=200000):
    buf = b""
    while len(buf) < cap:
        r, _, _ = select.select([fd], [], [], idle)
        if not r:
            break
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        buf += chunk
    return buf


def grab(dev, tls_client, srv_fd, label):
    dev.mcu_switch_to_fdt_mode(MODE, True)
    tls_client.sendall(
        dev.mcu_get_image(IMG_PAYLOAD,
                          goodix.FLAGS_TRANSPORT_LAYER_SECURITY_DATA)[9:])
    time.sleep(0.15)
    raw = read_until_idle(srv_fd)
    img = tool.decode_image(raw[:len(raw)//6*6])
    nz = sum(1 for v in img if v != 0)
    print(f"   [{label}] bytes={len(raw)} px={len(img)} "
          f"no_cero={nz} min={min(img) if img else 0} max={max(img) if img else 0}")
    return raw


def main():
    cfg = bytes.fromhex(open(sys.argv[1]).read().split("#")[0].strip())
    print(f"Config: {len(cfg)} bytes, cabecera {cfg[:4].hex()}")
    os.system("pkill -f 's_server.*4433' 2>/dev/null")
    time.sleep(0.3)
    dev = d.init_device(PID)
    print("Firmware:", dev.firmware_version())
    if not d.check_psk(dev):
        d.write_psk(dev)
    srv = subprocess.Popen(
        ["openssl", "s_server", "-nocert", "-psk", d.PSK.hex(),
         "-port", "4433", "-quiet"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    srv_fd = srv.stdout.fileno()
    try:
        if not dev.reset(True, False, 20)[0]:
            raise ValueError("Reset failed")
        dev.read_sensor_register(0x0000, 4)
        dev.nop(); dev.read_otp(); dev.pov_image_check()
        tls_client = socket.socket()
        tls_client.connect(("localhost", 4433))
        try:
            tool.connect_device(dev, tls_client)
            print("upload_config_mcu ->", dev.upload_config_mcu(cfg))
            dev.set_drv_state(); dev.set_drv_state()
            dev.mcu_get_pov_image()
            print("\n[1/2] baseline SIN dedo:")
            raw0 = grab(dev, tls_client, srv_fd, "empty")
            tool.write_pgm(tool.decode_image(raw0[:len(raw0)//6*6]), 80, 64, "empty.pgm")
            input("\n>>> dedo FIRME + Enter: ")
            print("[2/2] con dedo:")
            raw1 = grab(dev, tls_client, srv_fd, "finger")
            tool.write_pgm(tool.decode_image(raw1[:len(raw1)//6*6]), 80, 64, "finger.pgm")
            print("\n[OK] empty.pgm / finger.pgm escritos.")
        finally:
            tls_client.close()
    finally:
        srv.terminate()


if __name__ == "__main__":
    main()
