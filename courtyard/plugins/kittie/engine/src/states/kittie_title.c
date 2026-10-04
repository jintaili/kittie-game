#pragma bank 255
#include "states/kittie_title.h"
#include "states/kittie_music.h"
#include "actor.h"
#include "system.h"
#include "vm.h"
#include "input.h"
#include "ui.h"
#include "states/kittie_hud.h"
#include "scroll.h"
#include "data/game_globals.h"

/* The published v1 save has these first two globals. Appending score globals
   must never move its unlock slot. The compiler emits numeric IDs in order. */
#if VAR_STAGE_UNLOCK != 0 || VAR_STAGE_CHOICE != 1 || VAR_COURTYARD_BEST != 5 || VAR_COURTYARD_SAVE_VERSION != 6 || VAR_GROVE_BEST != 8 || VAR_VILLA_BEST != 9 || VAR_BANQUET_BEST != 10 || VAR_SAVE_SCHEMA != 11 || VAR_SAVE_FAMILY_KH != 12 || VAR_SAVE_FAMILY_OP != 13 || VAR_BOSS_BEST != 14 || VAR_TITLE_SELECTOR != 15
#error Kittie save variable layout changed
#endif
#define COURTYARD_SAVE_VERSION 19537
#define PUBLISHED_V1_SIGNATURE 0xb98c5e87UL
/* The two reviewed pilot-review-2 cartridges use the same validated schema. */
#define REVIEWED_PILOT_NATIVE_SIGNATURE 0xcadc4227UL
#define REVIEWED_PILOT_WEB_SIGNATURE 0x3229ed9cUL
#define FINAL_PILOT_NATIVE_SIGNATURE 0xbdc3d81cUL
#define FINAL_PILOT_WEB_SIGNATURE 0x7acafe8bUL
#define FOUR_STAGE_SAVE_VERSION 19538
#define FIVE_STAGE_SAVE_VERSION 19539
/* Our versioned progress family is stable across official compiler exports.
   These words are written only by a genuine stage-clear result script. */
#define SAVE_FAMILY_KH 0x4b48u
#define SAVE_FAMILY_OP 0x4f50u

static void load_progress(void) {
    const UBYTE *save=(const UBYTE *)0xA000u;
    const UINT16 *vars=(const UINT16 *)(0xA000u+9);
    UINT32 signature;
    UINT16 size, unlock, best;
    UBYTE i;
    VM_GLOBAL(VAR_STAGE_UNLOCK)=VM_GLOBAL(VAR_COURTYARD_BEST)=0;
    VM_GLOBAL(VAR_GROVE_BEST)=VM_GLOBAL(VAR_VILLA_BEST)=VM_GLOBAL(VAR_BANQUET_BEST)=0;
    VM_GLOBAL(VAR_SAVE_FAMILY_KH)=VM_GLOBAL(VAR_SAVE_FAMILY_OP)=0;
    VM_GLOBAL(VAR_BOSS_BEST)=0;
    ENABLE_RAM_MBC5;
    SWITCH_RAM_BANK(0, RAM_BANKS_ONLY);
    signature=*((const UINT32 *)save);
    size=*((const UINT16 *)(save+4));
    /* The first block includes the heap and all context stacks. Full-state
       loading is intentionally avoided across different cartridge builds. */
    if (size<9+sizeof(script_memory) || size>8192 ||
        *((const UINT16 *)(save+6))!=sizeof(script_memory) || save[8]!=0) return;
    unlock=vars[VAR_STAGE_UNLOCK];
    /* The compiler's signature includes transient asset versions. Validate
       our own progress family, layout and bounds; never load foreign state. */
    if (vars[VAR_SAVE_FAMILY_KH]==SAVE_FAMILY_KH &&
        vars[VAR_SAVE_FAMILY_OP]==SAVE_FAMILY_OP &&
        (vars[VAR_SAVE_SCHEMA]==FOUR_STAGE_SAVE_VERSION || vars[VAR_SAVE_SCHEMA]==FIVE_STAGE_SAVE_VERSION)) {
        if (vars[VAR_SAVE_SCHEMA]==FOUR_STAGE_SAVE_VERSION) {
            if (unlock>4) return;
            if (unlock>=3) ++unlock;
        } else {
            if (unlock>5 || vars[VAR_BOSS_BEST]>500 || vars[VAR_BOSS_BEST]%100) return;
        }
        best=vars[VAR_COURTYARD_BEST];
        if (best>900 || best%100) return;
        for (i=VAR_GROVE_BEST;i<=VAR_BANQUET_BEST;++i)
            if (vars[i]>900 || vars[i]%100) return;
        VM_GLOBAL(VAR_STAGE_UNLOCK)=unlock;
        if (vars[VAR_SAVE_SCHEMA]==FIVE_STAGE_SAVE_VERSION) VM_GLOBAL(VAR_BOSS_BEST)=vars[VAR_BOSS_BEST];
        VM_GLOBAL(VAR_COURTYARD_BEST)=best;
        for (i=VAR_GROVE_BEST;i<=VAR_BANQUET_BEST;++i) VM_GLOBAL(i)=vars[i];
        VM_GLOBAL(VAR_SAVE_FAMILY_KH)=SAVE_FAMILY_KH;
        VM_GLOBAL(VAR_SAVE_FAMILY_OP)=SAVE_FAMILY_OP;
        return;
    }
    if (unlock>3) return;
    if (unlock>=2) unlock+=2; /* Both insertions preserve old Banquet access. */
    if (signature==PUBLISHED_V1_SIGNATURE) {
        VM_GLOBAL(VAR_STAGE_UNLOCK)=unlock;
        return; /* Unused v1 heap words are not score data. */
    }
    if ((signature!=REVIEWED_PILOT_NATIVE_SIGNATURE && signature!=REVIEWED_PILOT_WEB_SIGNATURE &&
         signature!=FINAL_PILOT_NATIVE_SIGNATURE && signature!=FINAL_PILOT_WEB_SIGNATURE) ||
        vars[VAR_COURTYARD_SAVE_VERSION]!=COURTYARD_SAVE_VERSION) return;
    best=vars[VAR_COURTYARD_BEST];
    if (best>900 || best%100) return;
    VM_GLOBAL(VAR_STAGE_UNLOCK)=unlock;
    VM_GLOBAL(VAR_COURTYARD_BEST)=best;
}
extern void ui_draw_frame(UBYTE x,UBYTE y,UBYTE width,UBYTE height) BANKED;
static UBYTE selector_open,selector_row,selector_top;
static const char * const stage_names[]={"COURTYARD","OLIVE GROVE","VILLA","HEAD GOON","BANQUET"};
static const UBYTE best_slots[]={VAR_COURTYARD_BEST,VAR_GROVE_BEST,VAR_VILLA_BEST,VAR_BOSS_BEST,VAR_BANQUET_BEST};
static void draw_selector(void) {
    UBYTE row,index,p=0,col;UINT16 score;const char *name;
    ui_draw_frame(0,0,20,6);
    for (row=0;row<4;++row) {
        index=selector_top+row;col=0;
        ui_text_data[p++]=index==selector_row?'>':' ';++col;
        name=stage_names[index];
        while (*name) { ui_text_data[p++]=*name++;++col; }
        ui_text_data[p++]=' ';++col;
        if (index>VM_GLOBAL(VAR_STAGE_UNLOCK)) {
            name="LOCKED";while (*name) {ui_text_data[p++]=*name++;++col;}
        } else {
            score=VM_GLOBAL(best_slots[index]);
            ui_text_data[p++]='0'+score/100;ui_text_data[p++]='0';ui_text_data[p++]='0';col+=3;
        }
        while(col<17) {ui_text_data[p++]=' ';++col;}
        ui_text_data[p++]=(!row && selector_top)?'^':(row==3 && !selector_top?'v':' ');
        if(row<3) ui_text_data[p++]='\n';
    }
    ui_text_data[p]=0;
    text_options=TEXT_OPT_DEFAULT;text_draw_speed=0;text_ff=TRUE;text_ff_joypad=FALSE;
    text_bkg_fill=TEXT_BKG_FILL_W;vwf_direction=UI_PRINT_LEFTTORIGHT;
    text_render_base_addr=GetWinAddr();text_palette=UI_DEFAULT_PALETTE;overlay_priority=0x80;
    ui_set_start_tile(TEXT_BUFFER_START,0);text_drawn=FALSE;
    ui_set_pos(0,96);
}
void kittie_title_init(void) BANKED {
    kittie_hud_close();
    PLAYER.flags|=ACTOR_FLAG_HIDDEN;
    VM_GLOBAL(VAR_TITLE_SELECTOR)=VM_GLOBAL(VAR_STAGE_CHOICE)=0;
    selector_open=selector_row=selector_top=0;
    load_progress();
    kittie_music_start(4);
}
void kittie_title_update(void) BANKED {
    kittie_music_update();
    if (!VM_GLOBAL(VAR_TITLE_SELECTOR)) return;
    if (!selector_open) {
        if (INPUT_A_PRESSED || INPUT_START_PRESSED) {selector_open=1;draw_selector();}
        return;
    }
    if (INPUT_B_PRESSED) {selector_open=0;ui_set_pos(0,MENU_CLOSED_Y);return;}
    if (INPUT_DOWN_PRESSED && selector_row<4) {
        ++selector_row;if(selector_row>=selector_top+4) ++selector_top;draw_selector();
    } else if (INPUT_UP_PRESSED && selector_row) {
        --selector_row;if(selector_row<selector_top) --selector_top;draw_selector();
    } else if ((INPUT_A_PRESSED || INPUT_START_PRESSED) && selector_row<=VM_GLOBAL(VAR_STAGE_UNLOCK)) {
        VM_GLOBAL(VAR_STAGE_CHOICE)=selector_row+1;VM_GLOBAL(VAR_TITLE_SELECTOR)=0;
        selector_open=0;ui_set_pos(0,MENU_CLOSED_Y);
    }
}
