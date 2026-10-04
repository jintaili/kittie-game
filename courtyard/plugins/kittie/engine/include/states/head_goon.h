#ifndef HEAD_GOON_H
#define HEAD_GOON_H
#include <gbdk/platform.h>
void head_goon_init(void) BANKED;
void head_goon_update(void) BANKED;
void head_goon_update_boss(void) BANKED;
void head_goon_gate_init(void) BANKED;
void head_goon_sync_gates(void) BANKED;
void head_goon_reset_attack(void) BANKED;
void head_goon_sync_target(void) BANKED;
#endif
