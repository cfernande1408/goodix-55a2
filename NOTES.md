# Notas RE — Goodix 55a2 / GF3208

## Dispositivo
- USB 27c6:55a2, iface vendor-specific, bulk 0x01 OUT / 0x82 IN, High Speed.
- Sin driver de kernel (Driver=[none]).
- fw stock GF3208_RTSEC_APP_10063 ; IAP MILAN_RTSEC_IAP_10027.
- chip id (reg 0x0000): 08 a4 00 22. read_firmware (0xf2) da timeout con la
  app en marcha -> no hay dump de fabrica.

## Flasheo
- Mismo dado GF3208 que el target 5503 de goodix-fp-dump
  (firmware/5503/GF3208_RTSEC_APP_10062.bin).
- run_55a2_flash.py: borra app -> IAP -> escribe PSK -> flashea 10062.
  El IAP nunca se escribe => recuperable.

## Candidatos DEVICE_CONFIG (de Wbdi.dll, 2022-08-15)
Cuatro configs de 256 B; firma XX 11 60 71 2c ...:
- 0x169a80 cab 0x90  (junto a codigo MilanFSeries/ChicagoHS.c)
- 0x16a070 cab 0x60  = GF3268 (== driver_55x4 DEVICE_CONFIG)
- 0x206f50 cab 0x58  = GF3258 (cuerpo == config 5503 del repo)
- 0x207990 cab 0x70  (region de tabla GF3226/GF3288/GF5288/GF5298)
DLL lista familias RTSEC: GF3208/GF3268/GF3206/GF3258. Checksum desconocido
(A5A5-sum NO cuadra); el chip acepta configs igualmente.

## Resultado
Probados 0x58, 0x90, 0x70 -> todos los frames a cero (7684 B, 5120 px, 0).
=> el bloqueo NO es el config. Falta la calibracion de DAC
(MilanGetRegDac / MilanSetRegDac / dacAdjust_version_00.00.06 en Wbdi.dll).

## Siguiente
1. VM Windows + usbmon capturando un enroll. El canal de control va en claro
   (solo la imagen va en TLS): el pcap deberia mostrar config (0x90) +
   register writes + bucle DAC-adjust + comando de imagen.
2. Replicar esa secuencia en capture_cfg.py.
3. Driver C para libfprint.
Alt: reversear MilanFSeries / MilanSetRegDac de Wbdi.dll con Ghidra.
