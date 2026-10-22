#!/usr/bin/env python3
"""Captura MANUAL del 55a2 (GF3208_RTSEC_APP_10062), sin FDT.
Dispara baseline sin dedo y, tras pulsar Enter con el dedo puesto, captura.
Genera empty.pgm y finger.pgm. Necesita openssl."""
import os
import socket
import subprocess
import time

import driver_5503 as d
import goodix
import tool

PID = 0x55A2
W, H = d.SENSOR_WIDTH, d.SENSOR_HEIGHT
MODE = bytes.fromhex("0d018b0084008c0088008096809180928085808c8086")
IMG_PAYLOAD = bytes.fromhex("01008b0084008c008800")
IMG_BYTES = 7684


def grab(dev, tls_client, tls_server, path):
    dev.mcu_switch_to_fdt_mode(MODE, True)
    tls_client.sendall(
        dev.mcu_get_image(IMG_PAYLOAD,
                          goodix.FLAGS_TRANSPORT_LAYER_SECURITY_DATA)[9:])
    tls_server.stdout.flush()
    time.sleep(0.1)
    raw = tls_server.stdout.read(IMG_BYTES)
    img = tool.decode_image(raw[:-4])
    tool.write_pgm(img, W, H, path)
    print(f"      -> {path} ({len(img)} px)")


def main():
    os.system("pkill -f 's_server.*4433' 2>/dev/null")
    time.sleep(0.3)

    dev = d.init_device(PID)
    print("Firmware:", dev.firmware_version())
    if not d.check_psk(dev):
        print("Escribiendo PSK...")
        d.write_psk(dev)

    tls_server = subprocess.Popen(
        ["openssl", "s_server", "-nocert", "-psk", d.PSK.hex(),
         "-port", "4433", "-quiet"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        if not dev.reset(True, False, 20)[0]:
            raise ValueError("Reset failed")
        dev.read_sensor_register(0x0000, 4)
        dev.nop()
        dev.read_otp()
        dev.pov_image_check()

        tls_client = socket.socket()
        tls_client.connect(("localhost", 4433))
        try:
            tool.connect_device(dev, tls_client)
            if not dev.upload_config_mcu(d.DEVICE_CONFIG):
                raise ValueError("Failed to upload config")
            dev.set_drv_state()
            dev.set_drv_state()
            dev.mcu_get_pov_image()

            print("\n[1/2] Baseline SIN dedo (no toques)...")
            grab(dev, tls_client, tls_server, "empty.pgm")

            input("\n>>> Pon el dedo y MANTENLO firme, luego pulsa Enter: ")
            print("[2/2] Capturando con dedo...")
            grab(dev, tls_client, tls_server, "finger.pgm")

            print("\n[OK] Listo: empty.pgm y finger.pgm")
        finally:
            tls_client.close()
    finally:
        tls_server.terminate()


if __name__ == "__main__":
    main()
