/* Goodix GF3208 (27c6:55a2) protocol layer for libfprint.
 * Message framing verified byte-for-byte against goodix-fp-dump (Python). */
#ifndef GOODIX_PROTO_H
#define GOODIX_PROTO_H
#include <stdint.h>
#include <stddef.h>

/* Transport (pack) flags */
#define GX_FLAGS_MSG_PROTOCOL 0xA0
#define GX_FLAGS_TLS          0xB0
#define GX_FLAGS_TLS_DATA     0xB2

/* Commands */
enum {
    GX_CMD_NOP            = 0x00,
    GX_CMD_MCU_GET_IMAGE  = 0x20,
    GX_CMD_FDT_DOWN       = 0x32,
    GX_CMD_FDT_UP         = 0x34,
    GX_CMD_FDT_MODE       = 0x36,
    GX_CMD_WRITE_REG      = 0x80,
    GX_CMD_READ_REG       = 0x82,
    GX_CMD_UPLOAD_CONFIG  = 0x90,
    GX_CMD_ENABLE_CHIP    = 0x96,
    GX_CMD_RESET          = 0xA2,
    GX_CMD_READ_OTP       = 0xA6,
    GX_CMD_FIRMWARE_VER   = 0xA8,
    GX_CMD_QUERY_STATE    = 0xAE,
    GX_CMD_ACK            = 0xB0,
    GX_CMD_SET_DRV_STATE  = 0xC4,
    GX_CMD_REQUEST_TLS    = 0xD0,
    GX_CMD_GET_POV_IMAGE  = 0xD2,
    GX_CMD_POV_IMAGE_CHK  = 0xD6,
    GX_CMD_PRESET_PSK_W   = 0xE0,
    GX_CMD_PRESET_PSK_R   = 0xE4,
    GX_CMD_GET_IAP_VER    = 0xF6,
};

/* Build a protocol-layer message (cmd + len + payload + checksum).
 * out must hold payload_len + 4 bytes. Returns bytes written. */
size_t gx_encode_protocol(uint8_t *out, uint8_t cmd,
                          const uint8_t *payload, size_t payload_len,
                          int checksum);

/* Wrap a protocol message in a transport pack (flags + len + checksum + body).
 * out must hold body_len + 4 bytes. Returns bytes written. */
size_t gx_encode_pack(uint8_t *out, uint8_t flags,
                      const uint8_t *body, size_t body_len);

/* Convenience: pack(protocol(...)). out must hold payload_len + 8. */
size_t gx_build_command(uint8_t *out, uint8_t cmd,
                        const uint8_t *payload, size_t payload_len,
                        int checksum);

/* Config checksum (last 2 bytes, little-endian): 0x10000-(0xA5A5+sum16). */
uint16_t gx_config_checksum(const uint8_t *cfg, size_t len_without_cs);

#endif
