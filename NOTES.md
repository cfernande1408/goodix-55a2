# RE notes — Goodix 55a2 / GF3208

## Device
- USB 27c6:55a2, vendor-specific iface, bulk EP 0x01 OUT / 0x82 IN, High Speed.
- No kernel driver claims it (Driver=[none]).
- Stock firmware: GF3208_RTSEC_APP_10063 ; IAP: MILAN_RTSEC_IAP_10027.
- chip id (reg 0x0000): 08 a4 00 22 ; OTP readable.
- read_firmware (cmd 0xf2) times out on the running app -> no factory dump.

## Flashing
- Same GF3208 die as goodix-fp-dump's 5503 target
  (firmware/5503/GF3208_RTSEC_APP_10062.bin).
- run_55a2_flash.py: erase app -> IAP -> write PSK (white box) ->
  flash 10062. IAP never written => recoverable.

## DEVICE_CONFIG candidates (from Wbdi.dll, driver dated 2022-08-15)
Four 256-byte configs; signature `XX 11 60 71 2c ...`:
- 0x169a80 header 0x90  (near MilanFSeries/ChicagoHS.c code)
- 0x16a070 header 0x60  = GF3268 (matches driver_55x4 DEVICE_CONFIG)
- 0x206f50 header 0x58  = GF3258 (body == repo 5503 config; next to
                          "GF3258 DN2" string)
- 0x207990 header 0x70  (table region w/ GF3226/GF3288/GF5288/GF5298)
DLL lists RTSEC families GF3208/GF3268/GF3206/GF3258 and a "GF3208"
string at 0x205f9c. Config checksum algo unknown (A5A5-sum does NOT match);
device accepts configs regardless (lenient).

## Result
Tried configs 0x58, 0x90, 0x70 -> every frame all-zero (7684 B, 5120 px, 0).
=> config choice is not the blocker. Missing step = DAC calibration
(MilanGetRegDac / MilanSetRegDac / dacAdjust_version_00.00.06 in Wbdi.dll).

## Next
1. Windows VM + usbmon capture of an enrollment. Control channel is
   plaintext (only image data is inside TLS), so the pcap should reveal:
   config upload (cmd 0x90) + register writes + DAC-adjust loop + image cmd.
2. Replicate that sequence in capture_cfg.py.
3. libfprint C driver.
Alt: reverse MilanFSeries / MilanSetRegDac in Wbdi.dll with Ghidra.
