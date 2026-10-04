#pragma bank 255
#include "states/villa.h"
#include "states/kittie.h"
void villa_init(void) BANKED { kittie_start_stage(2); }
void villa_update(void) BANKED { kittie_update(); }
