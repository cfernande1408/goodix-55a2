#include "goodix_proto.h"

size_t gx_encode_protocol(uint8_t *out, uint8_t cmd,
                          const uint8_t *payload, size_t payload_len,
                          int checksum)
{
    size_t n = 0;
    uint16_t plen = (uint16_t)(payload_len + 1);
    out[n++] = cmd;
    out[n++] = (uint8_t)(plen & 0xff);
    out[n++] = (uint8_t)(plen >> 8);
    for (size_t i = 0; i < payload_len; i++)
        out[n++] = payload[i];
    if (checksum) {
        uint32_t s = 0;
        for (size_t i = 0; i < n; i++) s += out[i];
        out[n++] = (uint8_t)((0xAA - s) & 0xff);
    } else {
        out[n++] = 0x88;
    }
    return n;
}

size_t gx_encode_pack(uint8_t *out, uint8_t flags,
                      const uint8_t *body, size_t body_len)
{
    size_t n = 0;
    out[n++] = flags;
    out[n++] = (uint8_t)(body_len & 0xff);
    out[n++] = (uint8_t)(body_len >> 8);
    out[n++] = (uint8_t)((out[0] + out[1] + out[2]) & 0xff);
    for (size_t i = 0; i < body_len; i++)
        out[n++] = body[i];
    return n;
}

size_t gx_build_command(uint8_t *out, uint8_t cmd,
                        const uint8_t *payload, size_t payload_len,
                        int checksum)
{
    uint8_t body[4096];
    size_t blen = gx_encode_protocol(body, cmd, payload, payload_len, checksum);
    return gx_encode_pack(out, GX_FLAGS_MSG_PROTOCOL, body, blen);
}

uint16_t gx_config_checksum(const uint8_t *cfg, size_t len_without_cs)
{
    uint32_t cs = 0xA5A5;
    for (size_t i = 0; i + 1 < len_without_cs; i += 2) {
        uint16_t w = (uint16_t)(cfg[i] | (cfg[i + 1] << 8));
        cs = (cs + w) & 0xffff;
    }
    return (uint16_t)((0x10000 - cs) & 0xffff);
}
