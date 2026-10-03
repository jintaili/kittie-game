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
INT16 kittie_checkpoint, goon_x[GOON_COUNT], goon_y[GOON_COUNT];
UBYTE goon_state[GOON_COUNT], goon_timer[GOON_COUNT];
INT8 goon_dir[GOON_COUNT];
UBYTE kittie_coyote, kittie_jump_buffer, kittie_hurt, kittie_ribbon;

static void sound(UBYTE kind) {
    NR52_REG = 0x80; NR50_REG = 0x77; NR51_REG |= 0x11;
    NR10_REG = kind == 2 ? 0x26 : 0x16;
    NR11_REG = 0x80; NR12_REG = 0x82;
    NR13_REG = kind == 1 ? 0xD8 : (kind == 2 ? 0x70 : 0xB0);
    NR14_REG = 0x87;
}
static INT16 floor_at(INT16 x, INT16 radius) {
    UBYTE j;
    for (j = 0; j < GAP_COUNT; ++j)
        if (x - radius >= gaps[j][0] && x + radius <= gaps[j][1]) return gaps[j][2];
    return F(FLOOR_Y);
}

static INT16 magnitude(INT16 value) { return value < 0 ? -value : value; }
static UBYTE solid_open(UBYTE i) {
    return (i == FIRST_GATE_SOLID && (kittie_gate & 1)) ||
           (i == LAST_GATE_SOLID && (kittie_gate & 2));
}
static void reset_ball(void) {
    UBYTE j;
    if (!kittie_court) return;
    if (kittie_court == 3) {
        kittie_ball_x = kittie_x + kittie_facing * F(24);
        kittie_ball_y = kittie_y - F(5);
        for (j = 0; j < SOLID_COUNT; ++j) {
            if (solid_open(j)) continue;
            if (kittie_ball_x + F(5) > solids[j][0] && kittie_ball_x - F(5) < solids[j][2] &&
                kittie_ball_y + F(5) > solids[j][1] && kittie_ball_y - F(5) < solids[j][3]) {
                kittie_ball_x = kittie_x; break;
            }
        }
    } else {
        kittie_ball_x = F(kittie_court == 1 ? 364 : 1080);
        kittie_ball_y = F(123);
    }
    kittie_ball_vx = kittie_ball_vy = 0;
    kittie_ball_active = 1;
}
static void respawn(void) {
    kittie_x = kittie_checkpoint; kittie_y = F(FLOOR_Y);
    kittie_vx = kittie_vy = 0; kittie_ground = 1;
    kittie_hurt = 48; kittie_facing = 1; reset_ball(); sound(2);
    camera_x = ((UINT16)(kittie_checkpoint / 16 + 16)) << 5;
}
static void update_goons(void) {
    UBYTE j;
    INT16 distance;
    for (j = 0; j < GOON_COUNT; ++j) {
        if (goon_state[j] == 5) continue;
        if (goon_state[j] == 4) {
            goon_x[j] += goon_dir[j] * 32;
            goon_y[j] -= 16;
            if (!--goon_timer[j]) goon_state[j] = 5;
            continue;
        }
        distance = kittie_x - goon_x[j];
        if (magnitude(distance) > F(120)) continue;
        if (goon_timer[j]) --goon_timer[j];
        if (!goon_state[j]) {
            goon_x[j] += goon_dir[j] * 8;
            if (magnitude(distance) < F(58) && kittie_y > F(104)) {
                goon_state[j] = 1; goon_timer[j] = 26;
                goon_dir[j] = distance < 0 ? -1 : 1;
            }
        } else if (goon_state[j] == 1 && !goon_timer[j]) {
            goon_state[j] = 2; goon_timer[j] = 24;
        } else if (goon_state[j] == 2) {
            goon_x[j] += goon_dir[j] * 32;
            if (!goon_timer[j]) { goon_state[j] = 3; goon_timer[j] = 36; }
        } else if (goon_state[j] == 3 && !goon_timer[j]) goon_state[j] = 0;
        if (goon_x[j] < goon_limits[j][0]) { goon_x[j] = goon_limits[j][0]; goon_dir[j] = 1; }
        if (goon_x[j] > goon_limits[j][1]) { goon_x[j] = goon_limits[j][1]; goon_dir[j] = -1; }
        if (kittie_ball_active && magnitude(kittie_ball_vx) >= 12 &&
            magnitude(kittie_ball_x - goon_x[j]) < F(12) &&
            magnitude(kittie_ball_y - F(120)) < F(12)) {
            goon_state[j] = 4; goon_timer[j] = 24;
            goon_dir[j] = kittie_ball_vx > 0 ? 1 : -1;
            kittie_ball_vx = -kittie_ball_vx / 2; kittie_ball_vy = -24;
            sound(1);
        } else if (!kittie_hurt && magnitude(kittie_x - goon_x[j]) < F(15) &&
                   kittie_y > F(112) && kittie_y < F(144)) {
            kittie_hurt = 60; kittie_vy = -32;
            kittie_facing = kittie_x < goon_x[j] ? 1 : -1;
            kittie_ground = 0; sound(2);
        }
    }
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
    UBYTE frame, j;
    PLAYER.pos.x = ((UINT16)(kittie_x - F(8))) << 1;
    PLAYER.pos.y = ((UINT16)(kittie_y - F(8))) << 1;
    actor_set_dir(&PLAYER, kittie_facing > 0 ? DIR_RIGHT : DIR_LEFT, FALSE);
    PLAYER.anim_tick = ANIM_PAUSED;
    if (kittie_swat_pose) frame = kittie_swat_pose > 6 ? 7 : 8;
    else if (!kittie_ground) frame = 9;
    else if (kittie_vx) frame = 3 + ((kittie_tick >> 3) & 3);
    else frame = (kittie_tick >> 5) % 3;
    actor_set_frame_offset(&PLAYER, frame);
    if (kittie_hurt && (kittie_tick & 4)) PLAYER.flags |= ACTOR_FLAG_HIDDEN;
    else PLAYER.flags &= ~ACTOR_FLAG_HIDDEN;
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
    for (j = 0; j < GOON_COUNT; ++j) {
        actors[4+j].pos.x = ((UINT16)(goon_x[j] - F(8))) << 1;
        actors[4+j].pos.y = ((UINT16)(goon_y[j] - F(8))) << 1;
        actors[4+j].anim_tick = ANIM_PAUSED;
        actor_set_frame_offset(&actors[4+j], goon_state[j] == 4 ? 3 :
            (goon_state[j] == 1 || goon_state[j] == 2 ? 2 : ((kittie_tick >> 3) & 1)));
        if (goon_state[j] == 5 || magnitude(goon_x[j] - kittie_x) > F(110)) actors[4+j].flags |= ACTOR_FLAG_HIDDEN;
        else actors[4+j].flags &= ~ACTOR_FLAG_HIDDEN;
    }
    actors[7].pos.x = ((UINT16)(kittie_won ? 1242 : 776)) << 5;
    actors[7].pos.y = ((UINT16)(kittie_won ? 97 : 72)) << 5;
    if (kittie_won ? !kittie_ribbon : kittie_ribbon) actors[7].flags |= ACTOR_FLAG_HIDDEN;
    else actors[7].flags &= ~ACTOR_FLAG_HIDDEN;
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
    kittie_checkpoint = F(496);
    kittie_coyote = kittie_jump_buffer = kittie_hurt = kittie_ribbon = 0;
    for (i = 0; i < GOON_COUNT; ++i) {
        goon_x[i] = (goon_limits[i][0] + goon_limits[i][1]) / 2;
        goon_y[i] = F(128); goon_state[i] = goon_timer[i] = 0; goon_dir[i] = -1;
    }
    camera_settings = CAMERA_UNLOCKED;
    camera_x = PX_TO_SUBPX(80); camera_y = PX_TO_SUBPX(72);
    for (i = 1; i < 8; ++i) {
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
    if (kittie_hurt) --kittie_hurt;
    if (kittie_ground) kittie_coyote = 6;
    else if (kittie_coyote) --kittie_coyote;
    if (INPUT_A_PRESSED) kittie_jump_buffer = 6;
    else if (kittie_jump_buffer) --kittie_jump_buffer;
    if (!kittie_court && kittie_x >= F(328)) { kittie_court = 1; reset_ball(); }
    if (kittie_court == 1 && kittie_x > F(488)) { kittie_court = 3; reset_ball(); }
    if (kittie_court == 3 && kittie_x >= F(1016)) { kittie_court = 2; reset_ball(); }
    if (kittie_court == 3 && kittie_x >= F(864)) kittie_checkpoint = F(864);
    if (INPUT_SELECT_PRESSED) reset_ball();
    if (INPUT_LEFT) { kittie_vx = -26; kittie_facing = -1; }
    else if (INPUT_RIGHT) { kittie_vx = 26; kittie_facing = 1; }
    else kittie_vx = 0;
    if (kittie_hurt > 48) kittie_vx = -kittie_facing * 24;
    if (kittie_jump_buffer && kittie_coyote) { kittie_vy = -58; kittie_ground = 0; kittie_coyote = kittie_jump_buffer = 0; }
    if (!INPUT_A && kittie_vy < -24) kittie_vy = -24;
    if (INPUT_B_PRESSED) { kittie_swat = 10; kittie_swat_pose = 14; }
    if (kittie_swat) {
        --kittie_swat;
        dx = (kittie_ball_x - kittie_x) * kittie_facing;
        if (kittie_ball_active && dx > -F(5) && dx < F(30) && magnitude(kittie_ball_y - (kittie_y - F(8))) < F(22)) {
            kittie_ball_vx = kittie_facing * 48;
            kittie_ball_vy = INPUT_UP ? -56 : -5;
            kittie_swat = 0;
            sound(0);
        }
    }
    kittie_x += kittie_vx;
    if (kittie_y > F(128)) {
        for (i = 0; i < GAP_COUNT; ++i) {
            if (kittie_x > gaps[i][0] && kittie_x < gaps[i][1]) {
                if (kittie_x - F(9) < gaps[i][0]) kittie_x = gaps[i][0] + F(9);
                if (kittie_x + F(9) > gaps[i][1]) kittie_x = gaps[i][1] - F(9);
            }
        }
    }
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
    top = floor_at(kittie_x, F(9));
    if (kittie_y >= top) { kittie_y = top; kittie_vy = 0; kittie_ground = 1; }
    if (kittie_y > F(164)) respawn();
    if (!kittie_ribbon && magnitude(kittie_x - F(784)) < F(14) && magnitude(kittie_y - F(80)) < F(10)) {
        kittie_ribbon = 1; sound(1);
    }
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
        top = floor_at(kittie_ball_x, F(5)) - F(5);
        if (kittie_ball_y > top) { kittie_ball_y = top; kittie_ball_vy = kittie_ball_vy > 10 ? -kittie_ball_vy / 2 : 0; }
        if (kittie_ball_y < F(8)) { kittie_ball_y = F(8); kittie_ball_vy = 4; }
        if ((kittie_tick & 7) == 0 && kittie_ball_y >= F(121)) {
            if (kittie_ball_vx > 0) --kittie_ball_vx;
            else if (kittie_ball_vx < 0) ++kittie_ball_vx;
        }
        bell_x = F(kittie_court == 1 ? 430 : 1148);
        bell_y = F(kittie_court == 1 ? 80 : 120);
        if (kittie_court != 3 && !(kittie_gate & (kittie_court == 1 ? 1 : 2)) && magnitude(kittie_ball_x - bell_x) < F(13) && magnitude(kittie_ball_y - bell_y) < F(13)) ring_bell();
        if (kittie_court == 3 && (kittie_ball_y > F(152) || magnitude(kittie_ball_x - kittie_x) > F(96) ||
            (kittie_ground && magnitude(kittie_ball_vx) < 12 &&
             (kittie_x - kittie_ball_x) * kittie_facing > F(24)))) reset_ball();
    }
    update_goons();
    sync_actors(); update_camera();
    if ((kittie_gate & 2) && kittie_x > F(1240)) {
        if (trigger_activate_at_intersection(&PLAYER.bounds, &PLAYER.pos, FALSE)) { kittie_won = 1; sync_actors(); }
    }
}
