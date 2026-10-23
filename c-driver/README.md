# Goodix 55a2 (GF3208) — C driver foundation

C port of the working Python reference (see repo root). Built in layers,
each verified byte-for-byte against the Python implementation.

## Status
- [x] Protocol layer (`goodix_proto.c`): message pack/protocol framing +
      checksums. Verified against goodix-fp-dump outputs (`make test`).
- [x] Device constants (`goodix_55a2.h/.c`): PID, geometry 88x112 raw /
      52x88 merged, DAC-calibrated config (from config_win.hex), PSK.
- [x] Image assembly: merge the two 52-col halves (`gx55a2_merge_halves`).
- [ ] USB transport (libusb / libfprint async I/O).
- [ ] TLS 1.2 PSK session (image data channel).
- [ ] Init + capture state machine (reset, OTP, config, FDT, get_image).
- [ ] libfprint image-device integration + NBIS minutiae matching.

## Build & test
    make test        # builds and runs test_proto + test_merge

`src/gx55a2_config.c` is generated from `../config_win.hex` by the Makefile.

## libfprint integration plan
Target the `libfprint-goodixtls` fork (same TLS/PSK family as 5503/55x4).
The 55a2 is a GF3208 die, so the driver mirrors the 5503 driver with:
- USB id 27c6:55a2
- this DAC-calibrated config
- 88x112 raw geometry, two-half merge -> 52x88 image
- software finger-detection (threshold on frame-vs-baseline delta) or
  the hardware FDT thresholds captured in NOTES.md.
