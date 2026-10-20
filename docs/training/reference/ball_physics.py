"""Pinned surface physics used to attribute rebounds, without an emulator."""
def physics(ball, door, gates):
    """Exact pinned Head Goon surface physics, in native sixteenth-pixel units."""
    b = dict(ball); events = []
    if b['state'] != 0 or not (b['vx'] or b['vy'] or b['cooldown']):
        return b, events
    b['cooldown'] = max(0, b['cooldown'] - 1)
    b['x'] += b['vx']
    if b['x'] < 64:
        b['x'] = 64; b['vx'] = abs(b['vx']); events.append('left_boundary')
    if b['x'] > 476 * 16:
        b['x'] = 476 * 16; b['vx'] = -abs(b['vx']); events.append('right_boundary')
    solids = [(160*16,168*16,door),(320*16,328*16,not gates & 2)]
    for left,right,closed in solids:
        if closed and left < b['x']+64 and right > b['x']-64 and b['y']+64>0 and b['y']-64<2048:
            if b['vx'] > 0:
                b['x']=left-64; b['vx']=-b['vx']; events.append('shutter')
            elif b['vx'] < 0:
                b['x']=right+64; b['vx']=-b['vx']; events.append('shutter')
    old_y=b['y']; b['vy']=min(64,b['vy']+2); b['y']+=b['vy']; grounded=False
    for left,right,closed in solids:
        if not closed or left>=b['x']+64 or right<=b['x']-64:
            continue
        if old_y+64<=0 and b['y']+64>=0 and b['vy']>0:
            b['y']=-64
            if b['vy']>10: events.append('surface_top')
            b['vy']=-int(b['vy']/2) if b['vy']>10 else 0; grounded=True
        elif old_y-64>=2048 and b['y']-64<2048 and b['vy']<0:
            b['y']=2112; b['vy']=-int(b['vy']/2); events.append('surface_bottom')
    if b['y']>=1984:
        b['y']=1984
        if b['vy']>10: events.append('floor')
        b['vy']=-int(b['vy']/2) if b['vy']>10 else 0; grounded=True
    if b['y']<64:
        b['y']=64; b['vy']=4; events.append('ceiling')
    if grounded:
        b['vx']=max(0,b['vx']-2) if b['vx']>0 else min(0,b['vx']+2)
    return b,events


def hit_reward(prior_surface_rebounds: int) -> float:
    """Same expression as the native boss-hit event hook."""
    return 20. * (.5 ** prior_surface_rebounds)
