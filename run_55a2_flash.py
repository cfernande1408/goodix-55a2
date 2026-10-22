#!/usr/bin/env python3
"""Flasheo GUARDADO del 55a2 (GF3208): borra la app de fabrica y flashea
firmware/5503/GF3208_RTSEC_APP_10062.bin + PSK. Reutiliza driver_5503."""
import random
import re
from time import sleep

import driver_5503 as d

PID = 0x55A2
EXPECTED_IAP = d.IAP_FIRMWARE
MY_DIE = r"GF320[0-9]_RTSEC_APP_100[0-9]{2}"


def read_state(dev):
    fw = dev.firmware_version()
    iap = EXPECTED_IAP if fw == EXPECTED_IAP else dev.get_iap_version(25)
    return fw, iap


def main():
    dev = d.init_device(PID)
    fw, iap = read_state(dev)
    print(f"Firmware: {fw}")
    print(f"IAP:      {iap}")

    if iap != EXPECTED_IAP:
        raise SystemExit(f"ABORTADO: IAP inesperado ({iap}). No se toca nada.")

    if re.fullmatch(d.WORKING_FIRMWARE, fw):
        print("Ya estas en el firmware de trabajo 10062.")
        if not d.check_psk(dev):
            print("Escribiendo PSK de desarrollo (reversible)...")
            if not d.write_psk(dev):
                raise SystemExit("Fallo al escribir PSK")
        print("Listo. Ejecuta el script de captura cuando quieras.")
        return

    if not re.fullmatch(MY_DIE, fw):
        raise SystemExit(f"ABORTADO: firmware inesperado ({fw}). No se toca nada.")

    print("\n*** PASO IRREVERSIBLE ***")
    print(f"  - Se BORRARA la app de fabrica: {fw}")
    print(f"  - Se flasheara: firmware/5503/{d.TARGET_FIRMWARE}.bin (GF3208)")
    print("  - Se escribira la PSK de desarrollo.")
    print("  Red de seguridad: el IAP NO se toca; si algo falla, el chip")
    print("  queda en IAP y se puede volver a flashear.")
    code = random.randint(1000, 9999)
    if input(f"\nEscribe {code} para confirmar: ").strip() != str(code):
        raise SystemExit("Abortado. No se ha tocado nada.")

    print("\n[1/3] Borrando app...")
    d.erase_firmware(dev)
    sleep(2)
    dev = d.init_device(PID)
    fw2, iap2 = read_state(dev)
    print(f"      Tras borrar -> firmware={fw2}")
    if fw2 != EXPECTED_IAP and iap2 != EXPECTED_IAP:
        raise SystemExit(f"ABORTADO: estado raro tras borrar (fw={fw2}, iap={iap2}).")

    if not d.check_psk(dev):
        print("[2/3] Escribiendo PSK...")
        if not d.write_psk(dev):
            raise SystemExit("Fallo al escribir PSK")
    else:
        print("[2/3] PSK ya valida.")

    print("[3/3] Flasheando GF3208_RTSEC_APP_10062...")
    d.update_firmware(dev)
    sleep(2)
    dev = d.init_device(PID)
    fw3, _ = read_state(dev)
    print(f"\n[OK] Firmware tras flasheo: {fw3}")
    if re.fullmatch(d.WORKING_FIRMWARE, fw3):
        print("     Flasheo correcto. Siguiente paso: script de captura.")
    else:
        print("     Firmware inesperado tras flasheo; parame y lo miramos.")


if __name__ == "__main__":
    main()
