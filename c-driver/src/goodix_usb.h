/* USB transport for Goodix 27c6:55a2 over libusb-1.0. */
#ifndef GOODIX_USB_H
#define GOODIX_USB_H
#include <stdint.h>
#include <libusb-1.0/libusb.h>

typedef struct {
    libusb_context *ctx;
    libusb_device_handle *h;
    int iface;
} gx_usb;

/* Open 27c6:55a2 and claim interface 0. Returns 0 on success, <0 libusb err. */
int  gx_usb_open(gx_usb *u);
void gx_usb_close(gx_usb *u);

/* Raw bulk I/O. Return 0 ok (or LIBUSB_ERROR_TIMEOUT), else libusb error. */
int  gx_usb_write(gx_usb *u, const uint8_t *data, int len, unsigned ms);
int  gx_usb_read(gx_usb *u, uint8_t *buf, int maxlen, int *got, unsigned ms);
void gx_usb_drain(gx_usb *u);                       /* empty pending IN data */

/* Send pack(protocol(cmd,payload)). Returns 0 ok. */
int  gx_cmd_send(gx_usb *u, uint8_t cmd, const uint8_t *payload, int plen, int checksum);
/* Receive one pack; outputs the protocol command and its payload.
 * Returns 0 ok, LIBUSB_ERROR_TIMEOUT on no data, <0 on error. */
int  gx_pack_recv(gx_usb *u, uint8_t *out_cmd, uint8_t *payload, int *plen, unsigned ms);

#endif
