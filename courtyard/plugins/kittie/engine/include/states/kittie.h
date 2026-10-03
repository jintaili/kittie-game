#ifndef KITTIE_STATE_H
#define KITTIE_STATE_H
#include <gbdk/platform.h>
void kittie_init(void) BANKED;
void kittie_update(void) BANKED;
void kittie_start_stage(UBYTE stage) BANKED;
#endif
