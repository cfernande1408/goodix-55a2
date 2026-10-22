#!/usr/bin/env python3
"""Captura del 55a2 ya flasheado (GF3208_RTSEC_APP_10062).
Asegura PSK y lanza run_driver de driver_5503 (TLS + config + imagen)."""
import re

import driver_5503 as d

PID = 0x55A2


def main():
    dev = d.init_device(PID)
    fw = dev.firmware_version()
    print(f"Firmware: {fw}")

    if not re.fullmatch(d.WORKING_FIRMWARE, fw):
        raise SystemExit(
            f"ABORTADO: no estas en el firmware de trabajo ({fw}).")

    if not d.check_psk(dev):
        print("PSK no valida; escribiendola...")
        if not d.write_psk(dev):
            raise SystemExit("Fallo al escribir PSK")

    print("Lanzando captura. Sigue las instrucciones en pantalla.\n"
          "(Si se cuelga >30s esperando bytes, Ctrl-C: seria geometria.)\n")
    d.run_driver(dev)

    print("\n[OK] Captura terminada. Revisa en esta carpeta:")
    print("     clear-0.pgm, clear-1.pgm, fingerprint-0.pgm")


if __name__ == "__main__":
    main()
