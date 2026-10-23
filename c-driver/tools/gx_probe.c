/* C replica de probe_55a2.py: abre el device, lee firmware + OTP (solo lectura). */
#include <stdio.h>
#include "../src/goodix_usb.h"
#include "../src/goodix_proto.h"

static int xfer(gx_usb *u, uint8_t cmd, const uint8_t *pl, int pln,
                uint8_t *reply, int *rlen)
{
    int r = gx_cmd_send(u, cmd, pl, pln, 1);
    if (r) return r;
    for (int i = 0; i < 6; i++) {
        uint8_t rc; int rl;
        r = gx_pack_recv(u, &rc, reply, &rl, 1500);
        if (r == LIBUSB_ERROR_TIMEOUT) continue;
        if (r) return r;
        if (rc == cmd) { if (rlen) *rlen = rl; return 0; }
    }
    return LIBUSB_ERROR_TIMEOUT;
}

int main(void)
{
    gx_usb u;
    int r = gx_usb_open(&u);
    if (r) { fprintf(stderr, "open fallo: %s\n", libusb_error_name(r)); return 1; }
    printf("Dispositivo 27c6:55a2 abierto.\n");
    gx_usb_drain(&u);

    uint8_t rep[4096]; int rl;
    { uint8_t p[2] = {0,0};
      if (xfer(&u, GX_CMD_FIRMWARE_VER, p, 2, rep, &rl) == 0) {
          rep[rl < 4096 ? rl : 4095] = 0;
          printf("Firmware: %s\n", (char *)rep);
      } else printf("Firmware: (sin respuesta)\n"); }

    { uint8_t p[2] = {0,0};
      if (xfer(&u, GX_CMD_READ_OTP, p, 2, rep, &rl) == 0) {
          printf("OTP (%d B): ", rl);
          for (int i = 0; i < rl; i++) printf("%02x", rep[i]);
          printf("\n");
      } else printf("OTP: (sin respuesta)\n"); }

    gx_usb_close(&u);
    printf("OK. Nada escrito en el sensor.\n");
    return 0;
}
