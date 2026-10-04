#ifndef KITTIE_HUD_H
#define KITTIE_HUD_H
#include <gbdk/platform.h>
void kittie_hud_reset(void) BANKED;
void kittie_hud_update(void) BANKED;
void kittie_hud_close(void) BANKED;
void kittie_hud_sync(UBYTE health,UBYTE inventory,UBYTE score) BANKED;
#endif
