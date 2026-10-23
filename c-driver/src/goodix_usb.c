#include "goodix_usb.h"
#include "goodix_proto.h"
#include "goodix_55a2.h"
#include <string.h>

int gx_usb_open(gx_usb *u)
{
    int r;
    memset(u, 0, sizeof(*u));
    u->iface = 0;
    if ((r = libusb_init(&u->ctx)) < 0) return r;
    u->h = libusb_open_device_with_vid_pid(u->ctx, GX55A2_VID, GX55A2_PID);
    if (!u->h) { libusb_exit(u->ctx); u->ctx = NULL; return LIBUSB_ERROR_NO_DEVICE; }
    if (libusb_kernel_driver_active(u->h, u->iface) == 1)
        libusb_detach_kernel_driver(u->h, u->iface);
    /* Reset para recuperar el device de un estado previo (toggles/halts). */
    if (libusb_reset_device(u->h) == LIBUSB_ERROR_NOT_FOUND) {
        libusb_close(u->h);
        u->h = libusb_open_device_with_vid_pid(u->ctx, GX55A2_VID, GX55A2_PID);
        if (!u->h) { libusb_exit(u->ctx); u->ctx = NULL; return LIBUSB_ERROR_NO_DEVICE; }
    }
    libusb_set_configuration(u->h, 1);
    if ((r = libusb_claim_interface(u->h, u->iface)) < 0) {
        libusb_close(u->h); libusb_exit(u->ctx); u->h = NULL; u->ctx = NULL;
        return r;
    }
    libusb_clear_halt(u->h, GX55A2_EP_OUT);
    libusb_clear_halt(u->h, GX55A2_EP_IN);
    return 0;
}

void gx_usb_close(gx_usb *u)
{
    if (u->h) { libusb_release_interface(u->h, u->iface); libusb_close(u->h); }
    if (u->ctx) libusb_exit(u->ctx);
    u->h = NULL; u->ctx = NULL;
}

int gx_usb_write(gx_usb *u, const uint8_t *data, int len, unsigned ms)
{
    uint8_t buf[8192];
    int padded = (len + 0x3f) & ~0x3f;
    if (padded > (int)sizeof(buf)) return LIBUSB_ERROR_OVERFLOW;
    memcpy(buf, data, (size_t)len);
    if (padded > len) memset(buf + len, 0, (size_t)(padded - len));
    int tx = 0;
    return libusb_bulk_transfer(u->h, GX55A2_EP_OUT, buf, padded, &tx, ms);
}

int gx_usb_read(gx_usb *u, uint8_t *buf, int maxlen, int *got, unsigned ms)
{
    int tx = 0;
    int r = libusb_bulk_transfer(u->h, GX55A2_EP_IN, buf, maxlen, &tx, ms);
    if (got) *got = tx;
    return r;
}

void gx_usb_drain(gx_usb *u)
{
    uint8_t tmp[2048]; int got;
    while (gx_usb_read(u, tmp, sizeof(tmp), &got, 100) == 0 && got > 0)
        ;
}

int gx_cmd_send(gx_usb *u, uint8_t cmd, const uint8_t *payload, int plen, int checksum)
{
    uint8_t pkt[4096];
    size_t n = gx_build_command(pkt, cmd, payload, (size_t)plen, checksum);
    return gx_usb_write(u, pkt, (int)n, 1000);
}

int gx_pack_recv(gx_usb *u, uint8_t *out_cmd, uint8_t *payload, int *plen, unsigned ms)
{
    uint8_t buf[4096]; int got = 0;
    int r = gx_usb_read(u, buf, sizeof(buf), &got, ms);
    if (r != 0) return r;
    if (got < 4) return LIBUSB_ERROR_TIMEOUT;
    int body_len = buf[1] | (buf[2] << 8);
    uint8_t *body = buf + 4;
    if (got - 4 < body_len) body_len = got - 4;
    if (buf[0] == GX_FLAGS_MSG_PROTOCOL && body_len >= 3) {
        if (out_cmd) *out_cmd = body[0];
        int clen = (body[1] | (body[2] << 8)) - 1;
        if (clen < 0) clen = 0;
        if (clen > body_len - 3) clen = body_len - 3;
        if (payload) memcpy(payload, body + 3, (size_t)clen);
        if (plen) *plen = clen;
        return 0;
    }
    if (out_cmd) *out_cmd = buf[0];
    if (payload) memcpy(payload, body, (size_t)body_len);
    if (plen) *plen = body_len;
    return 0;
}
