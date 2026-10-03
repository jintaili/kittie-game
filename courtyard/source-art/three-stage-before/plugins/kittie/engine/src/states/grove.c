#pragma bank 255
#include "states/grove.h"
#include "states/kittie.h"
void grove_init(void) BANKED { kittie_start_stage(1); }
void grove_update(void) BANKED { kittie_update(); }
