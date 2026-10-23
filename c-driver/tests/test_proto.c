#include <stdio.h>
#include <string.h>
#include "../src/goodix_proto.h"

static int fails = 0;
static void hex(const uint8_t *b, size_t n, char *out) {
    for (size_t i = 0; i < n; i++) sprintf(out + 2*i, "%02x", b[i]);
}
static void check(const char *name, const uint8_t *got, size_t n, const char *exp) {
    char h[8192]; hex(got, n, h);
    if (strcmp(h, exp) == 0) { printf("  OK  %-14s %s\n", name, h); }
    else { printf("FAIL  %-14s\n    got %s\n    exp %s\n", name, h, exp); fails++; }
}

int main(void) {
    uint8_t out[4096]; size_t n;

    /* NOP: pack(protocol(00000000, NOP, checksum=False)) */
    { uint8_t p[] = {0,0,0,0};
      n = gx_build_command(out, GX_CMD_NOP, p, 4, 0);
      check("NOP", out, n, "a00800a80005000000000088"); }

    /* FW_VER: pack(protocol(0000, FIRMWARE_VER)) */
    { uint8_t p[] = {0,0};
      n = gx_build_command(out, GX_CMD_FIRMWARE_VER, p, 2, 1);
      check("FW_VER", out, n, "a00600a6a803000000ff"); }

    /* UPLOAD_CONFIG(aabbcc) */
    { uint8_t p[] = {0xaa,0xbb,0xcc};
      n = gx_build_command(out, GX_CMD_UPLOAD_CONFIG, p, 3, 1);
      check("UPCFG_AABBCC", out, n, "a00700a7900400aabbcce5"); }

    /* protocol-only (1122, 0x36) */
    { uint8_t p[] = {0x11,0x22};
      n = gx_encode_protocol(out, GX_CMD_FDT_MODE, p, 2, 1);
      check("PROTO_1122_36", out, n, "36030011223e"); }

    /* config checksum of config_win -> 0x58e8 */
    {
      extern const uint8_t gx55a2_device_config[256];
      uint16_t cs = gx_config_checksum(gx55a2_device_config, 254);
      printf("  config_win checksum = 0x%04x (esperado 0x58e8) -> %s\n",
             cs, cs == 0x58e8 ? "OK" : "FAIL");
      if (cs != 0x58e8) fails++;
    }

    printf(fails ? "\n%d FALLOS\n" : "\nTODO OK\n", fails);
    return fails ? 1 : 0;
}
