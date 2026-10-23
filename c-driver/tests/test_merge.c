#include <stdio.h>
#include <string.h>
#include "../src/goodix_55a2.h"
int main(void){
    static uint16_t raw[GX55A2_FRAME_PX];
    static uint16_t out[GX55A2_IMG_W*GX55A2_IMG_H];
    memset(raw,0,sizeof(raw));
    /* fila 0: half A col0 (idx 1)=100, half B col0 (idx 57)=200 -> avg 150 */
    raw[1]=100; raw[57]=200;
    /* fila 0: half A col1 (idx 2)=10, half B col1 (idx 58)=30 -> avg 20 */
    raw[2]=10;  raw[58]=30;
    gx55a2_merge_halves(raw,out);
    int ok = (out[0]==150) && (out[1]==20);
    printf("merge[0]=%d (exp 150)  merge[1]=%d (exp 20)  -> %s\n",
           out[0], out[1], ok?"OK":"FAIL");
    return ok?0:1;
}
