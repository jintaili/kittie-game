#pragma bank 255
#include "states/kittie_music.h"

/* Original four-bar themes in C major, A minor and C major. Pulse 2 plays the melody, wave plays a soft bass.
   Pulse 1 remains available for ball, bell and hurt sound effects. */
static const UINT16 pitch[] = {1547,1602,1650,1673,1714,1750,1783,1798,1825,1849,1860,1881,1899,1915,1923};
static const UBYTE tunes[4][32] = {
 {7,9,11,9,7,4,2,4,6,7,8,6,4,2,1,2,7,9,11,14,11,9,7,4,6,4,2,1,2,4,7,255},
 {5,7,9,12,9,7,5,2,3,5,7,9,7,5,3,255,5,7,9,12,11,9,7,5,2,4,6,7,6,2,5,255},
 {4,7,9,11,9,7,4,255,6,8,11,12,11,8,6,255,4,7,9,12,11,9,7,4,2,6,8,11,9,7,4,255},
 {7,7,11,14,11,9,7,9,6,6,8,11,8,7,6,4,7,9,11,14,12,11,9,7,6,4,6,8,11,9,7,255}
};
static const UINT16 bass[4][8] = {
 {1046,1046,711,711,856,856,711,1046},
 {856,856,547,547,1046,711,457,856},
 {711,711,856,856,1046,1046,711,711},
 {1046,1046,711,711,856,547,711,1046}
};
static UBYTE tune, music_tick, note;
void kittie_music_start(UBYTE stage) BANKED {
    UBYTE i;
    volatile UBYTE *wave=(volatile UBYTE *)0xff30;
    tune=stage<5?stage:0; music_tick=0; note=0;
    NR52_REG=0x80; NR50_REG=0x55; NR51_REG|=0x66;
    NR22_REG=0; NR30_REG=0;
    if(tune==4) return;
    NR30_REG=0;
    for(i=0;i<16;++i) wave[i]=i<8 ? (i*2)*17 : (15-i)*34;
    NR30_REG=0x80; NR32_REG=0x60;
}
void kittie_music_update(void) BANKED {
    UINT16 f;
    UBYTE n;
    if(tune==4) return;
    if(music_tick) { --music_tick; return; }
    music_tick=tune==3?13:16;
    n=tunes[tune][note];
    if(n!=255) {
        f=pitch[n]; NR21_REG=0x80; NR22_REG=0x62;
        NR23_REG=(UBYTE)f; NR24_REG=0x80|(f>>8);
    } else NR22_REG=0;
    if(!(note&3)) {
        f=bass[tune][note>>2]; NR33_REG=(UBYTE)f; NR34_REG=0x80|(f>>8);
    }
    note=(note+1)&31;
}
