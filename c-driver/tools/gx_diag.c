/* Diagnostico USB autonomo: imprime rc de cada paso de init. */
#include <stdio.h>
#include <libusb-1.0/libusb.h>

int main(void){
    libusb_context *ctx; 
    int r = libusb_init(&ctx);
    printf("init rc=%d\n", r);
    libusb_device_handle *h = libusb_open_device_with_vid_pid(ctx, 0x27c6, 0x55a2);
    if (!h){ printf("open NULL (device no encontrado o sin permisos)\n"); return 1; }
    printf("open OK\n");

    int cfg = -99; libusb_get_configuration(h, &cfg);
    printf("config actual = %d\n", cfg);

    int kd = libusb_kernel_driver_active(h, 0);
    printf("kernel_driver_active = %d\n", kd);
    if (kd == 1){ r = libusb_detach_kernel_driver(h,0); printf("detach rc=%d\n", r); }

    r = libusb_set_configuration(h, 1);
    printf("set_configuration(1) rc=%d (%s)\n", r, libusb_error_name(r));

    r = libusb_claim_interface(h, 0);
    printf("claim_interface(0) rc=%d (%s)\n", r, libusb_error_name(r));

    r = libusb_clear_halt(h, 0x01); printf("clear_halt(OUT) rc=%d\n", r);
    r = libusb_clear_halt(h, 0x82); printf("clear_halt(IN)  rc=%d\n", r);

    unsigned char tmp[65536]; int got;
    int drained=0;
    while (libusb_bulk_transfer(h, 0x82, tmp, 2048, &got, 100)==0 && got>0) drained+=got;
    printf("drenados %d bytes previos\n", drained);

    /* firmware_version pack (10 bytes), rellenado a 64 */
    unsigned char pkt[64] = {0xa0,0x06,0x00,0xa6,0xa8,0x03,0x00,0x00,0x00,0xff};
    int tx=0;
    r = libusb_bulk_transfer(h, 0x01, pkt, 64, &tx, 1000);
    printf("write rc=%d (%s) tx=%d\n", r, libusb_error_name(r), tx);

    for (int i=0;i<4;i++){
        got=0;
        r = libusb_bulk_transfer(h, 0x82, tmp, sizeof tmp, &got, 1500);
        printf("read[%d] rc=%d (%s) got=%d: ", i, r, libusb_error_name(r), got);
        for (int j=0;j<got && j<64;j++) printf("%02x", tmp[j]);
        printf("\n");
    }
    libusb_close(h); libusb_exit(ctx);
    return 0;
}
