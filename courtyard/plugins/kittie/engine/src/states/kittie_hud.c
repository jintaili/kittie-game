#pragma bank 255
#include "states/kittie_hud.h"
#include "ui.h"
#include "interrupts.h"
#include "palette.h"
#include "states/kittie_hud_tiles.h"
#include <string.h>

static UBYTE hud_score;
static UBYTE hud_health, hud_inventory;
extern UBYTE overlay_cut_scanline;
static UBYTE hud_active, hud_pending;
static palette_entry_t hud_previous_palette;

void kittie_hud_close(void) BANKED {
    if (hud_active) {
        BkgPalette[7]=hud_previous_palette;
        set_bkg_palette(7,1,(UWORD *)&BkgPalette[7]);
        ui_set_pos(0,MENU_CLOSED_Y);
    }
    hud_active=hud_pending=0;
    overlay_cut_scanline=150;
    show_actors_on_overlay=FALSE;
}
void kittie_hud_update(void) BANKED {
    UBYTE row[20],attrs[20],i;
    if (!hud_pending) return;
    hud_previous_palette=BkgPalette[7];
    /* Sprite color zero is transparent, so its first visible color repeats
       the cream. Window pixels need a real pink fill at index one. */
    BkgPalette[7]=SprPalette[4];
    BkgPalette[7].c1=SprPalette[4].c2;
    BkgPalette[7].c2=RGB(31,30,25);
    set_bkg_palette(7,1,(UWORD *)&BkgPalette[7]);
    memset(row,0xc0,sizeof(row));
    for(i=0;i<20;++i) attrs[i]=0x8f;
    VBK_REG=1;set_bkg_data(0xc0,25,compact_hud_tiles);
    set_win_tiles(0,0,20,1,attrs);
    VBK_REG=0;set_win_tiles(0,0,20,1,row);
    overlay_cut_scanline=7;
    show_actors_on_overlay=TRUE;
    ui_set_pos(0,0);
    hud_active=1;hud_pending=0;
    hud_health=hud_inventory=255;hud_score=255;
}
void kittie_hud_reset(void) BANKED {
    hud_pending=!hud_active;
    hud_health=hud_inventory=hud_score=255;
}
void kittie_hud_sync(UBYTE health, UBYTE inventory, UBYTE score) BANKED {
    UBYTE tiles[3],i;
    if (!hud_active) return;
    if (hud_health!=health) {
        for(i=0;i<3;++i) tiles[i]=i<health?0xc2:0xc1;
        set_win_tiles(1,0,3,1,tiles);hud_health=health;
    }
    if (hud_inventory!=inventory) {
        for(i=0;i<3;++i) tiles[i]=i<inventory?0xc4:0xc3;
        set_win_tiles(16,0,3,1,tiles);hud_inventory=inventory;
    }
    if (hud_score!=score) {
        tiles[0]=0xc5+score*2;tiles[1]=tiles[0]+1;
        set_win_tiles(9,0,2,1,tiles);hud_score=score;
    }
}
