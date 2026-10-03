#pragma bank 255
#include "states/kittie.h"
#include "actor.h"
#include "camera.h"
#include "input.h"
#include "trigger.h"
#include "states/kittie_level.h"

/* Signed 12.4 physics; GB Studio actor and camera positions use 11.5. */
#define F(x) ((INT16)((x) * 16))
#define FLOOR_Y 128
#define ANIM_PAUSED 255
INT16 kittie_x, kittie_y, kittie_vx, kittie_vy;
INT16 kittie_ball_x, kittie_ball_y, kittie_ball_vx, kittie_ball_vy;
UBYTE kittie_gate, kittie_won, kittie_ground, kittie_swat, kittie_tick;
UBYTE kittie_court, kittie_ball_active, kittie_swat_pose;
INT8 kittie_facing;

static INT16 magnitude(INT16 value) { return value < 0 ? -value : value; }
static UBYTE solid_open(UBYTE i) {
    return (i == FIRST_GATE_SOLID && (kittie_gate & 1)) ||
           (i == LAST_GATE_SOLID && (kittie_gate & 2));
}
static void reset_ball(void) {
    if (!kittie_court) return;
    kittie_ball_x = F(kittie_court == 1 ? 364 : 1080);
    kittie_ball_y = F(123);
    kittie_ball_vx = kittie_ball_vy = 0;
    kittie_ball_active = 1;
}
static void ring_bell(void) {
    kittie_gate |= kittie_court == 1 ? 1 : 2;
    /* No music in this prototype; a short hardware pulse marks the latch. */
    NR52_REG = 0x80; NR50_REG = 0x77; NR51_REG |= 0x11;
    NR10_REG = 0x16; NR11_REG = 0x80; NR12_REG = 0x92;
    NR13_REG = 0xC0; NR14_REG = 0x87;
}
static void update_camera(void) {
    INT16 target, current;
    target = kittie_x / 16 + 16;
    if (!(kittie_gate & 1) && kittie_x >= F(328) && kittie_x < F(470)) target = 392;
    if (!(kittie_gate & 2) && kittie_x >= F(1052)) target = 1112;
    if (target < 80) target = 80;
    if (target > LEVEL_WIDTH - 80) target = LEVEL_WIDTH - 80;
    current = camera_x >> 5;
    if (current < target) { current += 4; if (current > target) current = target; }
    if (current > target) { current -= 4; if (current < target) current = target; }
    camera_x = ((UINT16)current) << 5;
    camera_y = PX_TO_SUBPX(72);
}
static void sync_actors(void) {
    UBYTE frame;
    PLAYER.pos.x = ((UINT16)(kittie_x - F(8))) << 1;
    PLAYER.pos.y = ((UINT16)(kittie_y - F(8))) << 1;
    actor_set_dir(&PLAYER, kittie_facing > 0 ? DIR_RIGHT : DIR_LEFT, FALSE);
    PLAYER.anim_tick = ANIM_PAUSED;
    if (kittie_swat_pose) frame = kittie_swat_pose > 6 ? 7 : 8;
    else if (!kittie_ground) frame = 9;
    else if (kittie_vx) frame = 3 + ((kittie_tick >> 3) & 3);
    else frame = (kittie_tick >> 5) % 3;
    actor_set_frame_offset(&PLAYER, frame);
    actors[1].pos.x = ((UINT16)(kittie_ball_x - F(8))) << 1;
    actors[1].pos.y = ((UINT16)kittie_ball_y) << 1;
    if (kittie_ball_active) actors[1].flags &= ~ACTOR_FLAG_HIDDEN;
    else actors[1].flags |= ACTOR_FLAG_HIDDEN;
    actors[2].pos.x = F(460) * 2; actors[3].pos.x = ((UINT16)1182) << 5;
    actors[2].pos.y = actors[3].pos.y = F(56) * 2;
    if (kittie_gate & 1) actors[2].flags |= ACTOR_FLAG_HIDDEN;
    else actors[2].flags &= ~ACTOR_FLAG_HIDDEN;
    if (kittie_gate & 2) actors[3].flags |= ACTOR_FLAG_HIDDEN;
    else actors[3].flags &= ~ACTOR_FLAG_HIDDEN;
}
void kittie_init(void) BANKED {
    UBYTE i;
    trigger_reset();
    kittie_x = F(32); kittie_y = F(FLOOR_Y); kittie_vx = kittie_vy = 0;
    kittie_ball_x = F(364); kittie_ball_y = F(123);
    kittie_ball_vx = kittie_ball_vy = 0;
    kittie_gate = kittie_won = kittie_swat = kittie_tick = 0;
    kittie_court = kittie_ball_active = kittie_swat_pose = 0;
    kittie_ground = 1; kittie_facing = 1;
    camera_settings = CAMERA_UNLOCKED;
    camera_x = PX_TO_SUBPX(80); camera_y = PX_TO_SUBPX(72);
    for (i = 1; i < 4; ++i) {
        actors[i].flags |= ACTOR_FLAG_PERSISTENT;
        activate_actor(&actors[i]);
    }
    sync_actors();
}
void kittie_update(void) BANKED {
    INT16 old, dx, left, right, top, bottom, bell_x, bell_y;
    UBYTE i;
    if (INPUT_START_PRESSED) { kittie_init(); return; }
    if (kittie_won) return;
    ++kittie_tick;
    if (kittie_swat_pose) --kittie_swat_pose;
    if (!kittie_court && kittie_x >= F(328)) { kittie_court = 1; reset_ball(); }
    if (kittie_court == 1 && kittie_x > F(510)) kittie_ball_active = 0;
    if (kittie_court < 2 && kittie_x >= F(1016)) { kittie_court = 2; reset_ball(); }
    if (INPUT_SELECT_PRESSED && (kittie_court == 2 || kittie_x < F(510))) reset_ball();
    if (INPUT_LEFT) { kittie_vx = -26; kittie_facing = -1; }
    else if (INPUT_RIGHT) { kittie_vx = 26; kittie_facing = 1; }
    else kittie_vx = 0;
    if (INPUT_A_PRESSED && kittie_ground) { kittie_vy = -58; kittie_ground = 0; }
    if (!INPUT_A && kittie_vy < -24) kittie_vy = -24;
    if (INPUT_B_PRESSED) { kittie_swat = 10; kittie_swat_pose = 14; }
    if (kittie_swat) {
        --kittie_swat;
        dx = (kittie_ball_x - kittie_x) * kittie_facing;
        if (kittie_ball_active && dx > -F(5) && dx < F(30) && magnitude(kittie_ball_y - (kittie_y - F(8))) < F(22)) {
            kittie_ball_vx = kittie_facing * 48;
            kittie_ball_vy = INPUT_UP ? -56 : -5;
            kittie_swat = 0;
        }
    }
    kittie_x += kittie_vx;
    if (kittie_x < F(20)) kittie_x = F(20);
    if (kittie_x > F(LEVEL_WIDTH - 20)) kittie_x = F(LEVEL_WIDTH - 20);
    for (i = 0; i < SOLID_COUNT; ++i) {
        if (solids[i][0] >= kittie_x + F(9)) break;
        if (solids[i][2] <= kittie_x - F(9)) continue;
        if (solid_open(i)) continue;
        left = solids[i][0]; right = solids[i][2]; top = solids[i][1]; bottom = solids[i][3];
        if (kittie_y > top && kittie_y - F(16) < bottom && kittie_x + F(9) > left && kittie_x - F(9) < right) {
            if (kittie_vx > 0) kittie_x = left - F(9);
            else if (kittie_vx < 0) kittie_x = right + F(9);
        }
    }
    old = kittie_y; kittie_vy += 3;
    if (kittie_vy > 64) kittie_vy = 64;
    kittie_y += kittie_vy; kittie_ground = 0;
    for (i = 0; i < SOLID_COUNT; ++i) {
        if (solids[i][0] >= kittie_x + F(9)) break;
        if (solids[i][2] <= kittie_x - F(9)) continue;
        if (solid_open(i)) continue;
        left = solids[i][0]; right = solids[i][2]; top = solids[i][1]; bottom = solids[i][3];
        if (kittie_x + F(9) > left && kittie_x - F(9) < right) {
            if (old <= top && kittie_y >= top && kittie_vy >= 0) { kittie_y = top; kittie_vy = 0; kittie_ground = 1; }
            else if (old - F(16) >= bottom && kittie_y - F(16) < bottom && kittie_vy < 0) { kittie_y = bottom + F(16); kittie_vy = 0; }
        }
    }
    if (kittie_y >= F(FLOOR_Y)) { kittie_y = F(FLOOR_Y); kittie_vy = 0; kittie_ground = 1; }
    if (kittie_ball_active) {
        kittie_ball_x += kittie_ball_vx;
        if (kittie_ball_x < F(6)) { kittie_ball_x = F(6); kittie_ball_vx = magnitude(kittie_ball_vx); }
        if (kittie_ball_x > F(LEVEL_WIDTH - 6)) { kittie_ball_x = F(LEVEL_WIDTH - 6); kittie_ball_vx = -magnitude(kittie_ball_vx); }
        for (i = 0; i < SOLID_COUNT; ++i) {
        if (solids[i][0] >= kittie_ball_x + F(5)) break;
        if (solids[i][2] <= kittie_ball_x - F(5)) continue;
            if (solid_open(i)) continue;
            left = solids[i][0]; right = solids[i][2]; top = solids[i][1]; bottom = solids[i][3];
            if (kittie_ball_y + F(5) > top && kittie_ball_y - F(5) < bottom && kittie_ball_x + F(5) > left && kittie_ball_x - F(5) < right) {
                if (kittie_ball_vx > 0) { kittie_ball_x = left - F(5); kittie_ball_vx = -kittie_ball_vx; }
                else if (kittie_ball_vx < 0) { kittie_ball_x = right + F(5); kittie_ball_vx = -kittie_ball_vx; }
            }
        }
        old = kittie_ball_y; kittie_ball_vy += 2;
        if (kittie_ball_vy > 64) kittie_ball_vy = 64;
        kittie_ball_y += kittie_ball_vy;
        for (i = 0; i < SOLID_COUNT; ++i) {
        if (solids[i][0] >= kittie_ball_x + F(5)) break;
        if (solids[i][2] <= kittie_ball_x - F(5)) continue;
            if (solid_open(i)) continue;
            left = solids[i][0]; right = solids[i][2]; top = solids[i][1]; bottom = solids[i][3];
            if (kittie_ball_x + F(5) > left && kittie_ball_x - F(5) < right) {
                if (old + F(5) <= top && kittie_ball_y + F(5) >= top && kittie_ball_vy > 0) { kittie_ball_y = top - F(5); kittie_ball_vy = -kittie_ball_vy / 2; }
                else if (old - F(5) >= bottom && kittie_ball_y - F(5) < bottom && kittie_ball_vy < 0) { kittie_ball_y = bottom + F(5); kittie_ball_vy = -kittie_ball_vy / 2; }
            }
        }
        if (kittie_ball_y > F(123)) { kittie_ball_y = F(123); kittie_ball_vy = kittie_ball_vy > 10 ? -kittie_ball_vy / 2 : 0; }
        if (kittie_ball_y < F(8)) { kittie_ball_y = F(8); kittie_ball_vy = 4; }
        if ((kittie_tick & 7) == 0 && kittie_ball_y >= F(121)) {
            if (kittie_ball_vx > 0) --kittie_ball_vx;
            else if (kittie_ball_vx < 0) ++kittie_ball_vx;
        }
        bell_x = F(kittie_court == 1 ? 430 : 1148);
        bell_y = F(kittie_court == 1 ? 80 : 120);
        if (!(kittie_gate & (kittie_court == 1 ? 1 : 2)) && magnitude(kittie_ball_x - bell_x) < F(13) && magnitude(kittie_ball_y - bell_y) < F(13)) ring_bell();
    }
    sync_actors(); update_camera();
    if ((kittie_gate & 2) && kittie_x > F(1240)) {
        if (trigger_activate_at_intersection(&PLAYER.bounds, &PLAYER.pos, FALSE)) kittie_won = 1;
    }
}
