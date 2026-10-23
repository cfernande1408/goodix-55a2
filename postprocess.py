#!/usr/bin/env python3
"""Post-proceso de imagen del 55a2 (GF3208).
El sensor entrega un frame 88x112: dos mitades de 52 col (mismo dedo,
capturado 2 veces) separadas por columnas de ceros. Promediarlas ->
imagen 52x88 con mejor SNR.
Uso: python3 postprocess.py finger.pgm empty.pgm salida.png"""
import sys
import numpy as np
from PIL import Image, ImageOps

def load_pgm(p):
    t = open(p).read().split()
    assert t[0] == "P2"
    return np.array([int(x) for x in t[4:]], float).reshape(88, 112)

def merge_halves(img):
    A = img[:, 1:53]      # cols 1..52
    B = img[:, 57:109]    # cols 57..108
    return (A + B) / 2.0  # 88x52, mismo dedo -> promedio

def enhance(a, up=10):
    lo, hi = np.percentile(a, 2), np.percentile(a, 98)
    a = np.clip((a - lo) / (hi - lo + 1e-6) * 255, 0, 255).astype('uint8')
    im = ImageOps.equalize(Image.fromarray(a, 'L'))
    return im.resize((a.shape[1] * up, a.shape[0] * up), Image.LANCZOS)

def main():
    finger = load_pgm(sys.argv[1])
    out = sys.argv[3] if len(sys.argv) > 3 else "fingerprint.png"
    img = merge_halves(finger)
    if len(sys.argv) > 2:                 # restar fondo si hay empty
        img = np.abs(merge_halves(finger) - merge_halves(load_pgm(sys.argv[2])))
    enhance(img).save(out)
    print(f"guardado {out}  ({img.shape[1]}x{img.shape[0]})")

if __name__ == "__main__":
    main()
