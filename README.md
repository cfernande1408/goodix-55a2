# Goodix 27c6:55a2 (GF3208) — Linux reverse-engineering

WIP para llevar el sensor Goodix 27c6:55a2 (Lenovo ThinkBook 14s Yoga ITL)
a Linux/libfprint. No soportado por upstream ni goodix-fp-dump.

## Estado
- [x] Sensor identificado: GF3208, fw stock GF3208_RTSEC_APP_10063,
      IAP MILAN_RTSEC_IAP_10027.
- [x] Flasheado a GF3208_RTSEC_APP_10062 + PSK conocida (reusando driver_5503).
      Reversible: el IAP no se toca nunca.
- [x] TLS, protocolo de control y subida de config funcionando.
- [x] Pipeline de imagen devuelve frames del tamaño correcto (7684 B).
- [ ] BLOQUEO: frames todo a cero. Falta la calibracion de DAC
      (MilanSetRegDac / dacAdjust) que Windows hace antes de capturar.
- [ ] Replicar calibracion -> imagen real -> driver C para libfprint.

## Uso
Los scripts importan goodix/protocol/tool/driver_5503 de goodix-fp-dump,
asi que se ejecutan dentro de ese clon:

    git clone --recurse-submodules https://github.com/mpi3d/goodix-fp-dump.git
    cp *.py *.hex goodix-fp-dump/
    cd goodix-fp-dump
    sudo apt install -y python3-usb python3-crcmod python3-periphery python3-spidev
    sudo python3 probe_55a2.py
    sudo python3 run_55a2_flash.py
    sudo python3 capture_cfg.py config_0x90.hex

Ver NOTES.md para el log completo de ingenieria inversa.
