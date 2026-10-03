#pragma bank 255
#include "states/kittie_title.h"
#include "states/kittie_music.h"
#include "actor.h"
void kittie_title_init(void) BANKED {
    PLAYER.flags|=ACTOR_FLAG_HIDDEN;
    kittie_music_start(3);
}
void kittie_title_update(void) BANKED { kittie_music_update(); }
