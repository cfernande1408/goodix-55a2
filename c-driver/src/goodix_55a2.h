/* Device constants for Goodix 27c6:55a2 (GF3208).
 * Derived from reverse-engineering (see goodix-55a2 repo NOTES.md). */
#ifndef GOODIX_55A2_H
#define GOODIX_55A2_H
#include <stdint.h>

#define GX55A2_VID            0x27C6
#define GX55A2_PID            0x55A2
#define GX55A2_EP_OUT         0x01
#define GX55A2_EP_IN          0x82

/* Raw frame geometry */
#define GX55A2_FRAME_W        112   /* raw columns (2 halves + separators) */
#define GX55A2_FRAME_H        88
#define GX55A2_FRAME_PX       (112 * 88)   /* 9856 */
#define GX55A2_TLS_FRAME_LEN  14788        /* bytes over TLS incl. 4-byte tail */

/* Merged image geometry (two 52-col halves averaged) */
#define GX55A2_IMG_W          52
#define GX55A2_IMG_H          88

/* Firmware / IAP identifiers */
#define GX55A2_TARGET_FW      "GF3208_RTSEC_APP_10062"
#define GX55A2_IAP_FW         "MILAN_RTSEC_IAP_10027"

/* DAC-calibrated device config (header 0x30), extracted from the Windows
 * driver's UPLOAD_CONFIG. Per-sensor; this one is for the dev unit.
 * A production driver recomputes DAC from a calibration pass. */
extern const uint8_t gx55a2_device_config[256];

/* Development PSK (32 zero bytes) used with the community firmware. */
extern const uint8_t gx55a2_psk[32];

/* Merge the raw 112x88 frame into a 52x88 image (average the two halves).
 * raw: GX55A2_FRAME_PX uint16 pixels (row-major). out: GX55A2_IMG_W*IMG_H. */
void gx55a2_merge_halves(const uint16_t *raw, uint16_t *out);

#endif
