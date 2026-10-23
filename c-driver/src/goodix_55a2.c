#include "goodix_55a2.h"

const uint8_t gx55a2_psk[32] = {0};

void gx55a2_merge_halves(const uint16_t *raw, uint16_t *out)
{
    /* Two halves: cols 1..52 and 57..108 of each 112-wide row.
     * Same finger captured twice -> average for better SNR. */
    for (int r = 0; r < GX55A2_IMG_H; r++) {
        for (int k = 0; k < GX55A2_IMG_W; k++) {
            uint32_t a = raw[r * GX55A2_FRAME_W + 1 + k];
            uint32_t b = raw[r * GX55A2_FRAME_W + 57 + k];
            out[r * GX55A2_IMG_W + k] = (uint16_t)((a + b) / 2);
        }
    }
}
