# Goodix 55a2 (GF3208) — C driver foundation

C port of the working Python reference (see repo root). Built in layers,
each verified against the Python implementation.

## Status
- [x] Protocol layer (`goodix_proto.c`): pack/protocol framing + checksums.
      Verified byte-for-byte (`make test`).
- [x] Device constants (`goodix_55a2.h/.c`): PID, geometry 88x112 / 52x88,
      DAC-calibrated config (from config_win.hex), PSK.
- [x] Image assembly: merge the two 52-col halves (`gx55a2_merge_halves`).
- [x] USB transport (`goodix_usb.c`, libusb-1.0): open/claim, bulk I/O,
      command send + pack receive. Probe tool reads firmware + OTP.
- [ ] TLS 1.2 PSK session (image data channel).
- [ ] Init + capture state machine (reset, OTP, config, FDT, get_image).
- [ ] libfprint image-device integration + NBIS minutiae matching.

## Build & test
    make test            # protocol + merge unit tests (no deps)

    sudo apt install libusb-1.0-0-dev
    make probe           # builds gx_probe
    sudo ./gx_probe      # opens 27c6:55a2, prints firmware + OTP (read-only)

`src/gx55a2_config.c` is generated from `../config_win.hex` by the Makefile.

## Files
- `src/goodix_proto.*` — message framing + checksums
- `src/goodix_55a2.*`  — device constants, config, half-merge
- `src/goodix_usb.*`   — libusb transport + command/pack helpers
- `tools/gx_probe.c`   — read-only probe (C replica of probe_55a2.py)
- `tests/`             — unit tests

## libfprint integration plan
Target the `libfprint-goodixtls` fork (same TLS/PSK family as 5503/55x4).
The 55a2 is a GF3208 die, so the driver mirrors the 5503 driver with the
55a2 USB id, this DAC-calibrated config, 88x112 raw geometry with two-half
merge -> 52x88, and software finger-detection (threshold on frame-vs-baseline
delta) or the hardware FDT thresholds recorded in NOTES.md.
