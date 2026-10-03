#pragma bank 255
#include "states/banquet.h"
#include "states/kittie.h"
void banquet_init(void) BANKED { kittie_start_stage(2); }
void banquet_update(void) BANKED { kittie_update(); }
