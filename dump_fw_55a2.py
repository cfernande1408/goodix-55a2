#!/usr/bin/env python3
"""Volcado SOLO LECTURA del firmware de fábrica del 55a2.
NO borra, NO escribe, NO toca la PSK. Solo read_firmware (0xf2)."""
import goodix
import protocol

PID = 0x55A2
OUT = "stock_GF3208_10063.bin"
TOTAL = 0x10000
CHUNK = 1024


def main():
    print(f"== Volcado solo-lectura 27c6:{PID:04x} ==\n")
    dev = goodix.Device(PID, protocol.USBProtocol)
    dev.nop()
    print("Firmware:", dev.firmware_version())
    data = bytearray()
    off = 0
    while off < TOTAL:
        n = min(CHUNK, TOTAL - off)
        try:
            blk = dev.read_firmware(off, n)
        except Exception as e:
            print(f"\n[stop] read_firmware fallo en 0x{off:x}: "
                  f"{type(e).__name__}: {e}")
            break
        if not blk:
            print(f"\n[stop] respuesta vacia en 0x{off:x}")
            break
        data += blk
        off += len(blk)
        print(f"  leidos 0x{off:05x} bytes...", end="\r")
    print()
    if data:
        with open(OUT, "wb") as f:
            f.write(data)
        print(f"[OK] Volcados {len(data)} bytes -> {OUT}")
    else:
        print("[--] No se pudo leer nada. No se ha tocado el chip.")


if __name__ == "__main__":
    main()
