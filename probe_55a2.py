#!/usr/bin/env python3
"""
Probe de SOLO LECTURA para el sensor Goodix 27c6:55a2.
NO borra firmware. NO escribe firmware. NO toca la PSK.
Ejecutar desde la raíz del repo:  sudo python3 probe_55a2.py
"""
import goodix
import protocol

PID = 0x55A2
PMK_HASH_55X4 = bytes.fromhex(
    "81b8ff490612022a121a9449ee3aad2792f32b9f3141182cd01019945ee50361")


def safe(label, fn):
    try:
        r = fn()
        print(f"[OK]  {label}: {r!r}")
        return r
    except Exception as e:
        print(f"[--]  {label}: {type(e).__name__}: {e}")
        return None


def main():
    print(f"== Probe solo-lectura 27c6:{PID:04x} (no se escribe nada) ==\n")
    dev = goodix.Device(PID, protocol.USBProtocol)

    safe("nop", dev.nop)
    fw = safe("firmware_version", dev.firmware_version)
    safe("read_otp", dev.read_otp)
    safe("get_iap_version(25)", lambda: dev.get_iap_version(25))
    safe("chip_id (reg 0x0000)", lambda: dev.read_sensor_register(0x0000, 4))

    def psk_state():
        ok, flags, psk = dev.preset_psk_read(0xbb020007)
        if not ok:
            return "no legible"
        return f"flags=0x{flags:08x} coincide_PSK_linux={psk == PMK_HASH_55X4}"
    safe("preset_psk_read", psk_state)

    print("\n== Fin. No se ha escrito nada en el sensor. ==")
    if fw:
        print(f">> FIRMWARE DETECTADO: {fw!r}  <-- pegame esta linea")


if __name__ == "__main__":
    main()
