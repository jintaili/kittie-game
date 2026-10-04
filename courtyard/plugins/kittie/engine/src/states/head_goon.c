#pragma bank 255
#include "states/head_goon.h"
#include "states/kittie.h"
#include "data_manager.h"
#include "bankdata.h"
#include "actor.h"
void head_goon_init(void) BANKED { head_goon_gate_init(); kittie_start_stage(3); }
void head_goon_update(void) BANKED { kittie_update(); }

#define F(x) ((INT16)((x)*16))
#define BALL_WORLD 0
extern UBYTE boss_phase,boss_timer,boss_health,boss_resume_open,ball_armed[6];
extern UBYTE kittie_door,kittie_gate,kittie_health,kittie_hurt,kittie_ground,kittie_joy;
extern INT16 kittie_x,kittie_y,kittie_vy,goon_x[3],goon_y[3];
extern INT8 kittie_knock,goon_dir[3];
extern INT16 ball_x[6],ball_y[6],ball_vx[6],ball_vy[6];
extern UBYTE ball_state[6],ball_cooldown[6],courtyard_defeated,bell_ring[2];
static INT16 magnitude(INT16 v) {return v<0?-v:v;}
static void sound(UBYTE kind) {
    NR52_REG=0x80;NR50_REG=0x55;NR51_REG|=0x11;
    NR10_REG=kind==2?0x26:0x16;NR11_REG=0x80;NR12_REG=0x82;
    NR13_REG=kind==1?0xd8:0x70;NR14_REG=0x87;
}
/* Target and horizontal velocity are captured once per visible wind-up.
   The40-update hop rises35.6px; ordinary walking remains0.75px/update. */
INT16 boss_target_x,boss_hop_vx,boss_hop_vy;
UBYTE boss_hops_left,boss_hop_age,boss_hop_remainder,boss_hop_error;
static INT8 boss_hop_sign;
static void wind_up(void) {
    INT16 delta;
    boss_target_x=kittie_x;
    if(boss_target_x<F(184)) boss_target_x=F(184);
    if(boss_target_x>F(304)) boss_target_x=F(304);
    delta=boss_target_x-goon_x[0];
    boss_hop_sign=delta<0?-1:1;
    goon_dir[0]=boss_hop_sign;
    boss_hop_vx=delta/40;
    boss_hop_remainder=magnitude(delta)%40;
    boss_hop_error=boss_hop_age=0;boss_hop_vy=-60;
    boss_phase=6;boss_timer=28;
}
void head_goon_reset_attack(void) BANKED {
    boss_target_x=F(280);boss_hop_vx=boss_hop_vy=0;
    boss_hops_left=boss_hop_age=boss_hop_remainder=boss_hop_error=0;
}
void head_goon_update_boss(void) BANKED {
    UBYTE n;
    INT16 distance;
    if(boss_phase==0) {
        if(kittie_door) {boss_phase=1;boss_timer=30;}
        return;
    }
    if(boss_phase==5) return;
    if(boss_phase==1 || boss_phase==4) {
        if(!--boss_timer) {boss_phase=2;boss_timer=54;}
        return;
    }
    if(boss_phase==2) {
        goon_x[0]+=goon_dir[0]*12;
        if(goon_x[0]<F(184)) {goon_x[0]=F(184)+(F(184)-goon_x[0]);goon_dir[0]=1;}
        if(goon_x[0]>F(304)) {goon_x[0]=F(304)-(goon_x[0]-F(304));goon_dir[0]=-1;}
        if(!--boss_timer) {boss_hops_left=boss_health==3?1:2;wind_up();}
    } else if(boss_phase==6) {
        if(!--boss_timer) boss_phase=7;
    } else if(boss_phase==7) {
        ++boss_hop_age;
        goon_x[0]+=boss_hop_vx;
        boss_hop_error+=boss_hop_remainder;
        if(boss_hop_error>=40) {boss_hop_error-=40;goon_x[0]+=boss_hop_sign;}
        boss_hop_vy+=3;goon_y[0]+=boss_hop_vy;
        if(boss_hop_age==40) {
            goon_x[0]=boss_target_x;goon_y[0]=F(128);
            --boss_hops_left;
            if(boss_hops_left) {boss_phase=8;boss_timer=12;}
            else {boss_phase=3;boss_timer=72;}
            sound(0);
        }
    } else if(boss_phase==8) {
        if(!--boss_timer) wind_up();
    } else if(boss_phase==3 && !--boss_timer) {
        boss_phase=2;boss_timer=54;
    }
    for(n=0;n<1;++n) {
        if(!ball_armed[n] || ball_state[n]!=BALL_WORLD || magnitude(ball_vx[n])<12 ||
           magnitude(ball_x[n]-goon_x[0])>=F(16) ||
           ball_y[n]<=goon_y[0]-F(32) || ball_y[n]>=goon_y[0]+F(4)) continue;
        ball_armed[n]=0;
        ball_vx[n]=-ball_vx[n]/2;ball_vy[n]=-24;ball_cooldown[n]=12;
        if(boss_phase==3) {
            --boss_health;++courtyard_defeated;kittie_joy=36;sound(1);
            boss_phase=boss_health?4:5;boss_timer=24;
            if(!boss_health) {kittie_gate|=2;bell_ring[1]=48;}
        } else {
            NR10_REG=0;NR11_REG=0xc0;NR12_REG=0x61;NR13_REG=0xf4;NR14_REG=0x87;
        }
        break;
    }
    distance=kittie_x-goon_x[0];
    /* No floor-level invisible shield during flight. Running underneath is
       safe once the visible feet clear Kittie's existing16px body bounds. */
    if(boss_phase!=3 && boss_phase!=4 && boss_phase!=5 && !kittie_hurt &&
       magnitude(distance)<F(18) && kittie_y>goon_y[0]-F(28) && kittie_y-F(16)<goon_y[0]) {
        --kittie_health;
        if(!kittie_health) return;
        kittie_hurt=60;kittie_vy=-32;kittie_knock=distance<0?-1:1;kittie_ground=0;sound(2);
    }
}
void head_goon_sync_target(void) BANKED {
    actors[5].flags|=ACTOR_FLAG_HIDDEN;
    if(boss_phase!=6 && boss_phase!=7) return;
    actors[5].pos.x=((UINT16)(boss_target_x-F(8)))<<1;
    actors[5].pos.y=((UINT16)136)<<5;
    actors[5].anim_tick=255;
    actor_set_frame_offset(&actors[5],boss_phase==7 || boss_timer<12?1:0);
    actors[5].flags&=~ACTOR_FLAG_HIDDEN;
}

static UBYTE gate_tile[2],gate_attr[2],gate_state[2],gate_pixels[16];
static UBYTE reverse_bits(UBYTE v) {
    v=((v&0x55)<<1)|((v&0xaa)>>1);v=((v&0x33)<<2)|((v&0xcc)>>2);return (v<<4)|(v>>4);
}
void head_goon_gate_init(void) BANKED {
    UBYTE j;UINT16 offset;
    for(j=0;j<2;++j) {
        offset=j?40:20;
        gate_tile[j]=ReadBankedUBYTE(image_ptr+offset,image_bank);
        gate_attr[j]=ReadBankedUBYTE(image_attr_ptr+offset,image_attr_bank);
        gate_state[j]=255;
    }
}
void head_goon_sync_gates(void) BANKED {
    UBYTE j,closed,row,src,lo,hi;
    for(j=0;j<2;++j) {
        closed=j?!(kittie_gate&2):kittie_door;
        if(closed==gate_state[j]) continue;
        gate_state[j]=closed;
        for(row=0;row<8;++row) {
            src=(gate_attr[j]&0x40)?7-row:row;
            hi=closed?(j?0x44:0x48):0;
            lo=closed?(src==3?0x7c:hi):0;
            gate_pixels[row*2]=(gate_attr[j]&0x20)?reverse_bits(lo):lo;
            gate_pixels[row*2+1]=(gate_attr[j]&0x20)?reverse_bits(hi):hi;
        }
        VBK_REG=(gate_attr[j]>>3)&1;set_bkg_data(gate_tile[j],1,gate_pixels);
    }
    VBK_REG=0;
}
