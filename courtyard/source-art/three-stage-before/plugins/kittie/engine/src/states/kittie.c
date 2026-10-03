#pragma bank 255
#include "states/kittie.h"
#include "actor.h"
#include "camera.h"
#include "input.h"
#include "trigger.h"
#include "states/kittie_levels.h"
#include <string.h>

/* Signed 12.4 physics; GB Studio actor positions use 11.5. */
#define F(x) ((INT16)((x) * 16))
#define FLOOR_Y 128
#define ANIM_PAUSED 255
#define BALL_WORLD 0
#define BALL_HELD 1
#define BALL_LOST 2
#define INVENTORY_CAPACITY 3
INT16 kittie_x, kittie_y, kittie_vx, kittie_vy;
INT16 ball_x[BALL_COUNT], ball_y[BALL_COUNT], ball_vx[BALL_COUNT], ball_vy[BALL_COUNT];
UBYTE ball_state[BALL_COUNT], ball_cooldown[BALL_COUNT];
UBYTE kittie_gate, kittie_won, kittie_ground, kittie_tick;
UBYTE kittie_swat_pose, kittie_coyote, kittie_jump_buffer, kittie_hurt;
UBYTE kittie_health, kittie_inventory, kittie_dead, kittie_door;
INT8 kittie_facing, kittie_knock;
INT16 goon_x[GOON_COUNT], goon_y[GOON_COUNT];
UBYTE goon_state[GOON_COUNT], goon_timer[GOON_COUNT];
INT8 goon_dir[GOON_COUNT];
UBYTE kittie_idle, kittie_cuddle, kittie_settle;
UBYTE kittie_stage;
/* Cache active geometry once. Repeated configuration-pointer reads were
   expensive enough to skip native frames during collision checks. */
static INT16 level_width, solids[MAX_LEVEL_SOLIDS][4], gaps[MAX_LEVEL_GAPS][3];
static INT16 ball_spawns[BALL_COUNT][2], goon_limits[GOON_COUNT][2];
static INT16 bell_x[2], bell_y[2], camera_entry[2], camera_center[2];
static UBYTE solid_count, gap_count, first_gate, last_gate, entry_door;
static UBYTE player_solid_start, ball_solid_start[BALL_COUNT];
#define LEVEL_WIDTH level_width
#define SOLID_COUNT solid_count
#define GAP_COUNT gap_count
#define FIRST_GATE_SOLID first_gate
#define LAST_GATE_SOLID last_gate
#define ENTRY_DOOR_SOLID entry_door
static const UBYTE ball_actor[BALL_COUNT] = {1,8,9,10,11,12};
/* The held ball travels over the ears; it never slides across his face. */
static const INT8 carry_arc[7][2] = {{-4,-16},{-3,-22},{4,-25},{12,-22},{20,-16},{20,-9},{15,-3}};

static INT16 magnitude(INT16 v) { return v < 0 ? -v : v; }
static UBYTE solid_begin(INT16 left, UBYTE index) {
    /* Authored rectangles have monotone right edges. Reuse the nearby row. */
    while (index<SOLID_COUNT && solids[index][2]<=left) ++index;
    while (index && solids[index-1][2]>left) --index;
    return index;
}
static void sound(UBYTE kind) {
    NR52_REG = 0x80; NR50_REG = 0x77; NR51_REG |= 0x11;
    NR10_REG = kind == 2 ? 0x26 : 0x16;
    NR11_REG = 0x80; NR12_REG = 0x82;
    NR13_REG = kind == 1 ? 0xD8 : (kind == 2 ? 0x70 : 0xB0);
    NR14_REG = 0x87;
}
static UBYTE solid_open(UBYTE i) {
    return (i == FIRST_GATE_SOLID && (kittie_gate & 1)) ||
        (i == LAST_GATE_SOLID && (kittie_gate & 2)) ||
        (i == ENTRY_DOOR_SOLID && !kittie_door);
}
static INT16 floor_at(INT16 x, INT16 radius) {
    UBYTE j;
    for (j = 0; j < GAP_COUNT; ++j)
        if (x-radius >= gaps[j][0] && x+radius <= gaps[j][1]) return gaps[j][2];
    return F(FLOOR_Y);
}
static void die(void) {
    kittie_health = 0; kittie_dead = 36;
    kittie_vx = kittie_vy = 0; sound(2);
}
static void throw_ball(void) {
    UBYTE n, i;
    if (!kittie_inventory || kittie_swat_pose) return;
    for (n = 0; n < BALL_COUNT; ++n) if (ball_state[n] == BALL_HELD) break;
    if (n == BALL_COUNT) return;
    --kittie_inventory;
    ball_state[n] = BALL_WORLD; ball_cooldown[n] = 12;
    ball_x[n] = kittie_x + kittie_facing * F(20);
    ball_y[n] = kittie_y - F(8);
    ball_vx[n] = kittie_facing * 48; ball_vy[n] = INPUT_UP ? -56 : -5;
    /* Release against a wall, never through it. */
    for (i = 0; i < SOLID_COUNT; ++i) {
        if (solid_open(i) || ball_y[n]+F(4) <= solids[i][1] || ball_y[n]-F(4) >= solids[i][3]) continue;
        if (kittie_facing > 0 && kittie_x < solids[i][0] && ball_x[n]+F(4) > solids[i][0]) {
            ball_x[n] = solids[i][0]-F(4); break;
        }
        if (kittie_facing < 0 && kittie_x > solids[i][2] && ball_x[n]-F(4) < solids[i][2]) ball_x[n] = solids[i][2]+F(4);
    }
    kittie_swat_pose = 14; sound(0);
}
static void update_balls(void) {
    UBYTE n, i, grounded;
    INT16 old, left, right, top, bottom;
    for (n = 0; n < BALL_COUNT; ++n) {
        if (ball_state[n] != BALL_WORLD) continue;
        /* Resting pickups already sit on authored surfaces. */
        if (!ball_vx[n] && !ball_vy[n] && !ball_cooldown[n]) continue;
        if (ball_cooldown[n]) --ball_cooldown[n];
        ball_x[n] += ball_vx[n];
        if (ball_x[n] < F(4)) { ball_x[n] = F(4); ball_vx[n] = magnitude(ball_vx[n]); }
        if (ball_x[n] > F(LEVEL_WIDTH-4)) { ball_x[n] = F(LEVEL_WIDTH-4); ball_vx[n] = -magnitude(ball_vx[n]); }
        ball_solid_start[n]=solid_begin(ball_x[n]-F(4),ball_solid_start[n]);
        for (i = ball_solid_start[n]; i < SOLID_COUNT; ++i) {
            if (solids[i][0] >= ball_x[n]+F(4)) break;
            if (solids[i][2] <= ball_x[n]-F(4) || solid_open(i)) continue;
            left=solids[i][0]; right=solids[i][2]; top=solids[i][1]; bottom=solids[i][3];
            if (ball_y[n]+F(4)>top && ball_y[n]-F(4)<bottom) {
                if (ball_vx[n]>0) { ball_x[n]=left-F(4); ball_vx[n]=-ball_vx[n]; }
                else if (ball_vx[n]<0) { ball_x[n]=right+F(4); ball_vx[n]=-ball_vx[n]; }
            }
        }
        old=ball_y[n]; ball_vy[n]+=2;
        if (ball_vy[n]>64) ball_vy[n]=64;
        ball_y[n]+=ball_vy[n]; grounded=0;
        for (i = ball_solid_start[n]; i < SOLID_COUNT; ++i) {
            if (solids[i][0] >= ball_x[n]+F(4)) break;
            if (solids[i][2] <= ball_x[n]-F(4) || solid_open(i)) continue;
            top=solids[i][1]; bottom=solids[i][3];
            if (old+F(4)<=top && ball_y[n]+F(4)>=top && ball_vy[n]>0) {
                ball_y[n]=top-F(4); ball_vy[n]=ball_vy[n]>10 ? -ball_vy[n]/2 : 0; grounded=1;
            } else if (old-F(4)>=bottom && ball_y[n]-F(4)<bottom && ball_vy[n]<0) {
                ball_y[n]=bottom+F(4); ball_vy[n]=-ball_vy[n]/2;
            }
        }
        top=floor_at(ball_x[n],F(4))-F(4);
        if (ball_y[n]>=top) { ball_y[n]=top; ball_vy[n]=ball_vy[n]>10 ? -ball_vy[n]/2 : 0; grounded=1; }
        if (ball_y[n]<F(4)) { ball_y[n]=F(4); ball_vy[n]=4; }
        if (grounded) {
            if (ball_vx[n]>0) { ball_vx[n]-=2; if (ball_vx[n]<0) ball_vx[n]=0; }
            else if (ball_vx[n]<0) { ball_vx[n]+=2; if (ball_vx[n]>0) ball_vx[n]=0; }
        }
        if (ball_y[n]>F(150)) { ball_state[n]=BALL_LOST; continue; }
        for (i=0;i<2;++i) {
            left=bell_x[i]; top=bell_y[i];
            if (!(kittie_gate & (1<<i)) && magnitude(ball_x[n]-left)<F(12) && magnitude(ball_y[n]-top)<F(12)) {
                kittie_gate |= (1<<i); ball_vx[n]=-ball_vx[n]/2; sound(1);
            }
        }
    }
}
static void collect_balls(void) {
    UBYTE n;
    if (kittie_inventory == INVENTORY_CAPACITY) return;
    for (n=0;n<BALL_COUNT;++n) {
        if (ball_state[n]==BALL_WORLD && !ball_cooldown[n] && magnitude(ball_x[n]-kittie_x)<F(14) &&
            magnitude(ball_y[n]-(kittie_y-F(8)))<F(14)) {
            ball_state[n]=BALL_HELD; ++kittie_inventory; sound(1);
            if (kittie_inventory==INVENTORY_CAPACITY) break;
        }
    }
}
static void update_goons(void) {
    UBYTE j,n;
    INT16 distance;
    for (j=0;j<GOON_COUNT;++j) {
        if (goon_state[j]==5) continue;
        if (goon_state[j]==4) {
            goon_x[j]+=goon_dir[j]*32; goon_y[j]-=16;
            if (!--goon_timer[j]) goon_state[j]=5;
            continue;
        }
        distance=kittie_x-goon_x[j];
        if (magnitude(distance)>F(120)) continue;
        if (goon_timer[j]) --goon_timer[j];
        if (!goon_state[j]) {
            goon_x[j]+=goon_dir[j]*8;
            if (magnitude(distance)<F(58) && kittie_y>F(104)) {
                goon_state[j]=1; goon_timer[j]=26; goon_dir[j]=distance<0?-1:1;
            }
        } else if (goon_state[j]==1 && !goon_timer[j]) { goon_state[j]=2; goon_timer[j]=24; }
        else if (goon_state[j]==2) {
            goon_x[j]+=goon_dir[j]*32;
            if (!goon_timer[j]) { goon_state[j]=3; goon_timer[j]=36; }
        } else if (goon_state[j]==3 && !goon_timer[j]) goon_state[j]=0;
        if (goon_x[j]<goon_limits[j][0]) { goon_x[j]=goon_limits[j][0]; goon_dir[j]=1; }
        if (goon_x[j]>goon_limits[j][1]) { goon_x[j]=goon_limits[j][1]; goon_dir[j]=-1; }
        for (n=0;n<BALL_COUNT;++n) {
            if (ball_state[n]==BALL_WORLD && magnitude(ball_vx[n])>=12 &&
                magnitude(ball_x[n]-goon_x[j])<F(12) && magnitude(ball_y[n]-F(120))<F(12)) {
                goon_state[j]=4; goon_timer[j]=24; goon_dir[j]=ball_vx[n]>0?1:-1;
                ball_vx[n]=-ball_vx[n]/2; ball_vy[n]=-24; sound(1); break;
            }
        }
        if (goon_state[j]!=4 && !kittie_hurt && magnitude(kittie_x-goon_x[j])<F(15) && kittie_y>F(112) && kittie_y<F(144)) {
            --kittie_health;
            if (!kittie_health) { die(); return; }
            kittie_hurt=60; kittie_vy=-32; kittie_knock=distance<0?-1:1;
            kittie_ground=0; sound(2);
        }
    }
}
static void update_camera(void) {
    INT16 target, current;
    target = kittie_x / 16 + 16;
    if (!(kittie_gate & 1) && kittie_x >= camera_entry[0] && kittie_x < solids[FIRST_GATE_SOLID][2]) target = camera_center[0];
    if (!(kittie_gate & 2) && kittie_x >= camera_entry[1]) target = camera_center[1];
    if (target < 80) target = 80;
    if (target > LEVEL_WIDTH - 80) target = LEVEL_WIDTH - 80;
    current = camera_x >> 5;
    if (current < target) { current += 4; if (current > target) current = target; }
    if (current > target) { current -= 4; if (current < target) current = target; }
    camera_x = ((UINT16)current) << 5;
    camera_y = PX_TO_SUBPX(72);
}
static void sync_actors(void) {
    UBYTE frame,j,a,held=0;
    INT8 carry_x,carry_y;
    PLAYER.pos.x=((UINT16)(kittie_x-F(8)))<<1;
    PLAYER.pos.y=((UINT16)(kittie_y-F(8)))<<1;
    actor_set_dir(&PLAYER,kittie_facing>0?DIR_RIGHT:DIR_LEFT,FALSE);
    PLAYER.anim_tick=ANIM_PAUSED;
    if (kittie_swat_pose) frame=kittie_swat_pose>6?7:8;
    else if (!kittie_ground) frame=9;
    else if (kittie_vx) frame=3+((kittie_tick>>3)&3);
    else if (kittie_inventory && kittie_cuddle) frame=kittie_cuddle==6 ? 11+((kittie_idle>>4)&1) : (kittie_idle<160 ? 10 : 13);
    else frame=(kittie_tick>>5)%3;
    actor_set_frame_offset(&PLAYER,frame);
    if (kittie_hurt && (kittie_tick&4)) PLAYER.flags|=ACTOR_FLAG_HIDDEN;
    else PLAYER.flags&=~ACTOR_FLAG_HIDDEN;
    carry_x=carry_arc[kittie_cuddle][0]; carry_y=carry_arc[kittie_cuddle][1];
    if (!kittie_cuddle && kittie_ground) {
        if (kittie_vx && ((kittie_tick>>3)&3)==1) --carry_y;
        if (kittie_settle>3) ++carry_y;
    }
    for (j=0;j<BALL_COUNT;++j) {
        a=ball_actor[j]; actors[a].flags|=ACTOR_FLAG_HIDDEN;
        if (ball_state[j]==BALL_WORLD && magnitude(ball_x[j]-kittie_x)<F(120)) {
            actors[a].pos.x=((UINT16)(ball_x[j]-F(8)))<<1;
            actors[a].pos.y=((UINT16)ball_y[j])<<1;
            actors[a].flags&=~ACTOR_FLAG_HIDDEN;
        } else if (ball_state[j]==BALL_HELD && !held) {
            actors[a].pos.x=((UINT16)(kittie_x+kittie_facing*F(carry_x)-F(8)))<<1;
            actors[a].pos.y=((UINT16)(kittie_y+F(carry_y)))<<1;
            actors[a].flags&=~ACTOR_FLAG_HIDDEN; held=1;
        }
    }
    actors[2].pos.x=((UINT16)(solids[FIRST_GATE_SOLID][0]-F(2)))<<1;
    actors[3].pos.x=((UINT16)(solids[LAST_GATE_SOLID][0]-F(2)))<<1;
    actors[2].pos.y=actors[3].pos.y=((UINT16)56)<<5;
    if ((kittie_gate&1) || magnitude(solids[FIRST_GATE_SOLID][0]+F(2)-((camera_x>>5)*16))>F(80)) actors[2].flags|=ACTOR_FLAG_HIDDEN; else actors[2].flags&=~ACTOR_FLAG_HIDDEN;
    if ((kittie_gate&2) || magnitude(solids[LAST_GATE_SOLID][0]+F(2)-((camera_x>>5)*16))>F(80)) actors[3].flags|=ACTOR_FLAG_HIDDEN; else actors[3].flags&=~ACTOR_FLAG_HIDDEN;
    for (j=0;j<GOON_COUNT;++j) {
        actors[4+j].pos.x=((UINT16)(goon_x[j]-F(8)))<<1;
        actors[4+j].pos.y=((UINT16)(goon_y[j]-F(8)))<<1;
        actors[4+j].anim_tick=ANIM_PAUSED;
        actor_set_frame_offset(&actors[4+j],goon_state[j]==4?3:(goon_state[j]==1||goon_state[j]==2?2:((kittie_tick>>3)&1)));
        if (goon_state[j]==5 || magnitude(goon_x[j]-kittie_x)>F(110)) actors[4+j].flags|=ACTOR_FLAG_HIDDEN;
        else actors[4+j].flags&=~ACTOR_FLAG_HIDDEN;
    }
    actors[7].pos.x=((UINT16)solids[ENTRY_DOOR_SOLID][0])<<1; actors[7].pos.y=((UINT16)8)<<5;
    if (kittie_door && magnitude(solids[ENTRY_DOOR_SOLID][0]+F(4)-((camera_x>>5)*16))<F(80)) actors[7].flags&=~ACTOR_FLAG_HIDDEN; else actors[7].flags|=ACTOR_FLAG_HIDDEN;
    actors[13].pos.x=((UINT16)8)<<5; actors[14].pos.x=((UINT16)128)<<5;
    actors[13].pos.y=actors[14].pos.y=((UINT16)8)<<5;
    actors[13].anim_tick=actors[14].anim_tick=ANIM_PAUSED;
    actor_set_frame_offset(&actors[13],kittie_health);
    actor_set_frame_offset(&actors[14],kittie_inventory);
}
static void reset_level(void) {
    UBYTE i;
    trigger_reset();
    kittie_x=F(32); kittie_y=F(128); kittie_vx=kittie_vy=0;
    kittie_health=3; kittie_inventory=kittie_dead=kittie_door=0;
    kittie_gate=kittie_won=kittie_tick=kittie_swat_pose=0;
    kittie_coyote=kittie_jump_buffer=kittie_hurt=0;
    kittie_ground=1; kittie_facing=1; kittie_knock=0;
    kittie_idle=kittie_cuddle=kittie_settle=0;
    player_solid_start=0;
    for (i=0;i<BALL_COUNT;++i) {
        ball_x[i]=ball_spawns[i][0]; ball_y[i]=ball_spawns[i][1];
        ball_vx[i]=ball_vy[i]=0; ball_state[i]=BALL_WORLD; ball_cooldown[i]=0;
        ball_solid_start[i]=0;
    }
    for (i=0;i<GOON_COUNT;++i) {
        goon_x[i]=goon_limits[i][0]+(goon_limits[i][1]-goon_limits[i][0])/2;
        goon_y[i]=F(128); goon_state[i]=goon_timer[i]=0; goon_dir[i]=-1;
    }
    camera_settings=CAMERA_UNLOCKED;
    camera_x=PX_TO_SUBPX(80); camera_y=PX_TO_SUBPX(72);
    for (i=1;i<15;++i) { actors[i].flags|=ACTOR_FLAG_PERSISTENT; activate_actor(&actors[i]); }
    actors[13].flags|=ACTOR_FLAG_PINNED; actors[14].flags|=ACTOR_FLAG_PINNED;
    sync_actors();
}
void kittie_start_stage(UBYTE stage) BANKED {
    const KittieLevel *level;
    kittie_stage=stage<2 ? stage : 0;
    level=&levels[kittie_stage];
    level_width=level->width; solid_count=level->solid_count; gap_count=level->gap_count;
    first_gate=level->first_gate; last_gate=level->last_gate; entry_door=level->entry_door;
    memcpy(solids,level->solid_data,solid_count*sizeof(solids[0]));
    memcpy(gaps,level->gap_data,gap_count*sizeof(gaps[0]));
    memcpy(ball_spawns,level->ball_data,sizeof(ball_spawns));
    memcpy(goon_limits,level->goon_data,sizeof(goon_limits));
    memcpy(bell_x,level->bell_x,sizeof(bell_x)); memcpy(bell_y,level->bell_y,sizeof(bell_y));
    memcpy(camera_entry,level->camera_entry,sizeof(camera_entry));
    memcpy(camera_center,level->camera_center,sizeof(camera_center));
    reset_level();
}
void kittie_init(void) BANKED { kittie_start_stage(0); }
void kittie_update(void) BANKED {
    INT16 old,left,right,top,bottom;
    UBYTE i;
    if (INPUT_START_PRESSED) { reset_level(); return; }
    if (kittie_dead) {
        if (!--kittie_dead) reset_level();
        else sync_actors();
        return;
    }
    if (kittie_won) return;
    ++kittie_tick;
    if (kittie_swat_pose) --kittie_swat_pose;
    if (kittie_hurt) --kittie_hurt;
    if (kittie_settle) --kittie_settle;
    if (kittie_ground) kittie_coyote=6; else if (kittie_coyote) --kittie_coyote;
    if (INPUT_A_PRESSED) kittie_jump_buffer=6; else if (kittie_jump_buffer) --kittie_jump_buffer;
    if (INPUT_LEFT) { kittie_vx=-26; kittie_facing=-1; }
    else if (INPUT_RIGHT) { kittie_vx=26; kittie_facing=1; }
    else kittie_vx=0;
    if (kittie_hurt>48) kittie_vx=kittie_knock*24;
    if (kittie_jump_buffer && kittie_coyote) { kittie_vy=-58; kittie_ground=0; kittie_coyote=kittie_jump_buffer=0; }
    if (!INPUT_A && kittie_vy<-24) kittie_vy=-24;
    if (INPUT_B_PRESSED) throw_ball();
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
    player_solid_start=solid_begin(kittie_x-F(9),player_solid_start);
    for (i = player_solid_start; i < SOLID_COUNT; ++i) {
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
    for (i = player_solid_start; i < SOLID_COUNT; ++i) {
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
    if (kittie_y>F(150)) { die(); sync_actors(); return; }
    if (kittie_x>=solids[ENTRY_DOOR_SOLID][2]+F(10)) kittie_door=1;
    update_balls(); update_goons();
    if (!kittie_dead) collect_balls();
    if (kittie_ground && !kittie_coyote) kittie_settle=6;
    if (kittie_inventory && kittie_ground && !kittie_vx && !kittie_hurt && !kittie_swat_pose) {
        if (kittie_idle<230) ++kittie_idle; else kittie_idle=0;
    } else kittie_idle=0;
    if (!kittie_inventory || kittie_swat_pose) kittie_cuddle=0;
    else if (kittie_tick&1) {
        if (kittie_idle>=90 && kittie_idle<160) { if (kittie_cuddle<6) ++kittie_cuddle; }
        else if (kittie_cuddle) --kittie_cuddle;
    }
    sync_actors(); update_camera();
    if ((kittie_gate&2) && kittie_x>F(LEVEL_WIDTH-40)) {
        if (trigger_activate_at_intersection(&PLAYER.bounds,&PLAYER.pos,FALSE)) kittie_won=1;
    }
}
