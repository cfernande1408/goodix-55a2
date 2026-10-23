# Goodix 27c6:55a2 (GF3208) — Linux reverse-engineering

Work in progress to bring the **Goodix 27c6:55a2** fingerprint sensor
(Lenovo ThinkBook 14s Yoga ITL) to Linux / libfprint. The device is
**not supported** by upstream libfprint or goodix-fp-dump.

## Status
- [x] Identify sensor: GF3208 die, stock fw `GF3208_RTSEC_APP_10063`,
      IAP `MILAN_RTSEC_IAP_10027`.
- [x] Flash community firmware `GF3208_RTSEC_APP_10062` + known (zero) PSK,
      reusing goodix-fp-dump's `driver_5503` (same GF3208 die).
      Reversible: the IAP bootloader is never touched.
- [x] TLS session, control protocol and config upload working.
- [x] Image pipeline returns frames of the right size (7684 B over TLS).
- [ ] **Blocker:** frames are all-zero. Uploading the DEVICE_CONFIG is not
      enough; the Windows driver runs a **DAC calibration**
      (`MilanSetRegDac` / `dacAdjust`) between config upload and capture.
      That sequence still has to be reverse-engineered.
- [x] Replicate DAC calibration -> real images (config_win.hex).
- [x] Auto finger-detection + capture (software FDT) - capture_auto.py
- [x] Image merge/background-subtract - clean fingerprint
- [ ] libfprint C driver (port the working Python reference)

## How to run
These scripts import `goodix`, `protocol`, `tool`, `driver_5503` from
goodix-fp-dump, so run them from inside that clone:

    git clone --recurse-submodules https://github.com/mpi3d/goodix-fp-dump.git
    cp *.py *.hex goodix-fp-dump/
    cd goodix-fp-dump
    sudo apt install -y python3-usb python3-crcmod python3-periphery python3-spidev
    sudo python3 probe_55a2.py        # read-only identification
    sudo python3 run_55a2_flash.py    # guarded flash (asks confirmation)
    sudo python3 capture_cfg.py config_0x90.hex   # try a config + capture

## Scripts
- `probe_55a2.py` — read-only: firmware, IAP, chip id, PSK state.
- `dump_fw_55a2.py` — read-only firmware dump attempt (app fw not readable).
- `run_55a2_flash.py` — guarded flash to GF3208_RTSEC_APP_10062 + PSK.
- `capture_cfg.py` — upload a DEVICE_CONFIG (hex file) and capture, with
  timeout + per-frame stats (nonzero/min/max).
- `config_0x90.hex`, `config_0x70.hex` — DEVICE_CONFIG candidates extracted
  from the Windows driver (see NOTES.md).

See `NOTES.md` for the full reverse-engineering log.
