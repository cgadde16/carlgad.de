"""Write src/components/Figures.astro: fine-ink-line figures that play once on hover.
Reuses the pose code in figgen.py. Usage: python3 -I fig_astro.py <out .astro>"""
import math
import re
import os
import sys

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figgen.py'), encoding='utf-8').read()
src = src[: src.rindex('\nmain()')]
ns = {'__name__': 'figgen'}
exec(src, ns)
ns['PAPER'] = '#F7F3EA'   # the site's --paper (warm cream); figgen keeps its own for the design canvas
st = ns['STYLES']['A']
cyclist, hiker, climber, camp = ns['cyclist'], ns['hiker'], ns['climber'], ns['camp']
sample, TRAIL, RIDGE2, INK = ns['sample'], ns['TRAIL'], ns['RIDGE2'], ns['INK']


def keyframes(name, pts, flipx=False, travel=78, count=36, maxang=14):
    """Travel along pts for travel% of the run, fade out, jump back to the start and fade in there."""
    if flipx:
        pts = list(reversed(pts))
    acc = [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    L = acc[-1]

    def at(s):
        j = 0
        while j < len(acc) - 2 and acc[j + 1] < s:
            j += 1
        p = pts[j]
        q = pts[min(j + 3, len(pts) - 1)]
        r = pts[max(j - 3, 0)]
        ang = math.degrees(math.atan2(q[1] - r[1], q[0] - r[0])) - (180 if flipx else 0)
        ang = max(-maxang, min(maxang, ((ang + 180) % 360) - 180))
        return p, ang

    def tf(p, ang):
        return f'translate({p[0]:.1f}px, {p[1]:.1f}px) rotate({ang:.1f}deg)'

    out = []
    for i in range(count + 1):
        pct = travel * i / count
        p, ang = at(L * i / count)
        op = 1.0 if pct < travel - 6 else max(0.0, (travel - pct) / 6)
        out.append(f'  {pct:.2f}% {{ transform: {tf(p, ang)}; opacity: {op:.2f}; }}')
    p0, a0 = at(0)
    out.append(f'  {travel + 0.01:.2f}% {{ transform: {tf(p0, a0)}; opacity: 0; }}')
    out.append(f'  100% {{ transform: {tf(p0, a0)}; opacity: 1; }}')
    return f'@keyframes {name} {{\n' + '\n'.join(out) + '\n}', tf(p0, a0)


def clip(pts, xmin, xmax):
    return [p for p in pts if xmin <= p[0] <= xmax]


css = []
marks = []


def hit(x, y, w, h):
    return f'<rect class="hit" x="{x}" y="{y}" width="{w}" height="{h}" fill="transparent"></rect>'


def motorcycle(st):
    """Supersport in the spirit of a Yamaha R9 (no badges): pointed nose with a central air duct,
    winglet, short sharp tail, underbelly exhaust, USD fork, multi-spoke wheels; tucked rider.
    Facing right, ground at y=0. Wheels spin, body bobs, exhaust puffs."""
    path, line, ik, head, far, wrap = ns['path'], ns['line'], ns['ik'], ns['head'], ns['far'], ns['wrap']
    lw = st['lw'] + 0.5
    paper = ns['PAPER']
    R, F = (-26, -13), (26, -13)
    out = []
    for c in (R, F):
        out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="13" stroke-width="3"></circle>')     # fat tyre
        out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="9.6" stroke-width="0.7"></circle>')  # rim
        sp = ''.join(path(line((c[0] + 2 * math.cos(a), c[1] + 2 * math.sin(a)),
                               (c[0] + 9.4 * math.cos(a + d), c[1] + 9.4 * math.sin(a + d))), 0.9)
                     for k in range(5) for a in (2 * math.pi * k / 5,) for d in (-0.13, 0.13))  # 5 split spokes
        out.append(f'<g class="spin fast">{sp}</g>')
        out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="1.8" fill="{INK}" stroke="none"></circle>')
    out.append(f'<circle cx="{F[0]}" cy="{F[1]}" r="6.2" stroke-width="0.7"></circle>')     # brake disc
    for i in range(3):
        out.append(f'<circle class="puff" style="animation-delay: -{i * 0.3:.1f}s" cx="-9" cy="-8.5" r="2" '
                   f'fill="{INK}" stroke="none" opacity="0"></circle>')
    body = []
    # long swingarm (box section) and frame spar
    body.append(f'<path d="M-26 -15 L-6 -23.5 L-5 -19.5 L-26 -11.5 Z" fill="{paper}" stroke-width="1.4"></path>')
    body.append(path(line((15, -37), (-6, -22)), 2))
    # engine underside and short underbelly exhaust
    body.append(f'<path d="M-6 -19 L9 -16 L8 -11 L-5 -12 Z" fill="{paper}" stroke-width="1.1"></path>')
    body.append(path('M-3 -16.5 L6 -14.6 M-3 -14 L5.5 -12.6', 0.6))
    body.append(f'<path d="M-8 -10.5 L9 -10 Q11 -10 11 -8 L10 -7 L-8 -7.5 Z" fill="{INK}" stroke-width="0.8"></path>')
    # upside-down fork: thick outer tubes at the top, thin sliders down to the axle
    body.append(path(line((15.5, -37), (21, -25)), 3.4))
    body.append(path(line((21, -25), F), 1.9))
    body.append(path('M17 -23.5 A11 11 0 0 1 33.5 -18', 1.4))                      # low front fender
    body.append(path('M-35 -21 A13 13 0 0 1 -22 -27.5', 1.1))                      # hugger
    # short, sharp, high tail with a tail light and a slim plate hanger
    body.append(f'<path d="M-5 -30 L-17 -34 L-29 -39.5 L-28 -35.5 L-17 -30 L-8 -27 Z" fill="{paper}" stroke-width="1.4"></path>')
    body.append(path(line((-6, -32), (-17, -35.5)), 3))
    body.append(path(line((-29, -39.5), (-28.3, -37)), 1.8))
    body.append(path(line((-20, -31), (-30, -27), (-31.5, -24)), 0.9))
    # sculpted tank
    body.append(f'<path d="M-5 -33 C-1 -39 8 -41 15 -39 L12 -33 L-3 -30 Z" fill="{INK}" stroke-width="1"></path>')
    # full fairing: pointed nose with the central duct notch, chin, belly pan
    body.append(f'<path d="M15 -39 L25 -38 L29.5 -32.5 L25.5 -31 L28 -27.5 L18.5 -19 L4 -13.5 L-6 -18 L-2 -28 L12 -33 Z" '
                f'fill="{paper}" stroke-width="1.5"></path>')
    body.append(path('M25.5 -31 L29.5 -32.5', 1.6))                                # duct opening
    body.append(path('M19 -35.8 L24.5 -34.6', 1.2))                                # headlight / position-light slit
    body.append(f'<path d="M12 -29 L23 -27.5 L13.5 -25.5 Z" fill="{INK}" stroke="none"></path>')  # winglet
    body.append(f'<path d="M0 -25 L11 -27 L8.5 -23.6 L-1.5 -22.2 Z" fill="none" stroke-width="0.8"></path>')  # side vent
    body.append(f'<path d="M15 -39 C18 -44.5 22 -44.5 25 -38" fill="{INK}" fill-opacity="0.22" stroke-width="1"></path>')  # smoked screen
    body.append(path(line((18, -37), (19.5, -40.5)), 0.9) + f'<path d="M18.5 -41.5 L22 -41 L21.5 -39.8 L18.8 -40.2 Z" fill="{INK}" stroke="none"></path>')  # mirror
    # tucked rider: hip on the seat, chest on the tank, head behind the screen, rear-set pegs
    hip, sh, hand, peg = (-12, -37), (7, -45.5), (16, -37.5), (-10, -21)
    knee = ik(hip, peg, 12.5, 12.5, key=lambda p: p[0])
    elbow = ik(sh, hand, 8.5, 8.5, key=lambda p: p[1])
    body.append(far(st, path(line(sh, (elbow[0] - 1.5, elbow[1]), (hand[0] - 1.5, hand[1])), lw)))
    body.append(path(line(hip, sh), st['tw'] + 1.6))
    hc, _ = head(st, sh, (1, -0.35))
    body.append(f'<circle cx="{hc[0]:.1f}" cy="{hc[1]:.1f}" r="5" fill="{INK}" stroke="none"></circle>')   # helmet
    body.append(path(f'M{hc[0] + 1.5:.1f} {hc[1] - 0.8:.1f} L{hc[0] + 5.3:.1f} {hc[1] + 0.6:.1f}', 1.3, f' stroke="{paper}"'))  # visor
    body.append(path(f'M{hc[0] - 4.5:.1f} {hc[1] - 2:.1f} L{hc[0] - 7:.1f} {hc[1] - 3:.1f}', 1.4))  # helmet spoiler
    body.append(path(line(hip, knee, peg), lw) + path(line((peg[0] - 2.5, peg[1]), (peg[0] + 3.5, peg[1] + 0.5)), lw))
    body.append(path(line(sh, elbow, hand), lw))
    out.append(f'<g class="bob">{"".join(body)}</g>')
    return wrap(''.join(out))


# Motorcycle on the dotted trail: Panigale V4 traced from a photo, upright rider (canvas Round 16, draft 4).
# The old freehand supersport, motorcycle() above, is no longer used.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panigale                                            # noqa: E402

# Hovered, it rides up the road to the crest of the front ridge, over it and down the far side, vanishing
# behind the ridge; it does not come back (once per visit, like the far cyclist).
RIDGE_FRONT = [((0, 700), (200, 650), (380, 690), (560, 660)), ((560, 660), (760, 628), (900, 690), (1100, 650))]
_crest = sample(RIDGE_FRONT, 600)


def crest_y(x):
    return min(_crest, key=lambda p: abs(p[0] - x))[1]


_road = clip(sample(TRAIL), 160, 600)
# where the road reaches the crest (the road climbs from below the crest line onto it)
_xc, _yc = next(p for p in _road if p[1] <= crest_y(p[0]) + 0.3)
_up = [p for p in _road if p[0] <= _xc]
# down the far side: tangent continues from the crest, then bends downhill behind the ridge
_down = [ns['bez']((_xc, _yc), (_xc + 30, _yc - 3), (_xc + 75, _yc + 18), (_xc + 125, _yc + 78), i / 120)
         for i in range(1, 121)]
_ride = _up + _down


def keyframes_once(name, pts, count=48, maxang=28):
    """Travel the whole path and stay at the end (used with animation-fill-mode forwards)."""
    acc = [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))

    def at(s):
        j = next((k for k in range(len(acc) - 1) if acc[k + 1] >= s), len(acc) - 2)
        p, q, r = pts[j], pts[min(j + 3, len(pts) - 1)], pts[max(j - 3, 0)]
        ang = max(-maxang, min(maxang, math.degrees(math.atan2(q[1] - r[1], q[0] - r[0]))))
        return f'translate({p[0]:.1f}px, {p[1]:.1f}px) rotate({ang:.1f}deg)'
    rows = [f'  {100 * i / count:.2f}% {{ transform: {at(acc[-1] * i / count)}; }}' for i in range(count + 1)]
    return f'@keyframes {name} {{\n' + '\n'.join(rows) + '\n}', at(0)


D_MOTO = 6.8
# 90 % of the first version (0.75), with lines thinned to the fine-ink figures (limbs ~1.2, torso ~2 scene units
# on screen, like the hiker and skier) and their 85 % opacity
MOTO_SCALE = 0.6075  # 90% of the earlier 0.675 (user, 2026-11-16)
MOTO_STYLE = dict(weight=0.72, rider_lw=2.4, rider_tw=4.4, wheels='front')
kf, base = keyframes_once('ride-near', _ride)
css += [kf, f'.ride-near {{ transform: {base}; }}',
        f'.play .ride-near {{ animation: ride-near {D_MOTO}s ease-in 1 forwards; }}',
        '.moto-fig.done .spin, .moto-fig.done .bob, .moto-fig.done .puff { animation: none; }']
# mask: hide whatever is below the crest line beyond the point where the road crosses it (soft edge like the
# blurred ridges); everything else, including the climb up the near face, stays visible
_beyond = [p for p in _crest if p[0] >= _xc]
_hide = ('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in _beyond) + f' L1100 900 L{_xc:.1f} 900 Z')
_px0, _py0, _px1 = panigale.extent()
marks.append(f'''<defs><filter id="moto-mist" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="1.6"></feGaussianBlur></filter>
    <mask id="behind-front-ridge" maskUnits="userSpaceOnUse" x="0" y="0" width="1440" height="900">
      <rect x="0" y="0" width="1440" height="900" fill="#fff"></rect><path d="{_hide}" fill="#000" filter="url(#moto-mist)"></path></mask></defs>''')
marks.append(f'''<g class="fig moto-fig" data-play="{D_MOTO}" data-once="moto" mask="url(#behind-front-ridge)">
    <g class="ride-near"><g transform="translate(0 {2 * MOTO_SCALE:g}) scale({MOTO_SCALE})" opacity="0.85">{hit(round(_px0), _py0, round(_px1 - _px0), 82)}{panigale.panigale_svg(ns['PAPER'], INK, **MOTO_STYLE)}</g></g>
  </g>''')
print(f'motorcycle: crest at x {_xc:.0f}, y {_yc:.0f}; vanishes behind the front ridge after {D_MOTO}s')

# Far cyclist on the second ridge. Hovered, he stands up and sprints uphill into a gust coming down off the
# ridge (its own streaks, blowing right to left), slows to a stall with his legs still pumping, and is then
# blown backwards down the slope, feet off the pedals, out of the left side of the picture (once per visit).
# Bike and rider in cyclist units (as figgen.cyclist), drawn at scale 0.36.
BK_R, BK_F, BK_BB = (-23, -13), (23, -13), (-3, -12)
BK_S, BK_HT, BK_HB, BK_BAR = (-10, -36), (15, -34), (17, -28), (21, -32)
BK_SCALE, BK_TORSO = 0.45, math.hypot(18, 10.5)  # was 0.36; 125% to match the camp on the same middle ridge (2026-11-16)


def bike(st, spin):
    """Wheels (spokes in a group with class spin, which CSS turns) and frame."""
    path, line = ns['path'], ns['line']
    out = []
    for c in (BK_R, BK_F):
        out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="13" stroke-width="{st["wheel"]}"></circle>')
        sp = ''.join(path(line((c[0] + 12 * math.cos(a), c[1] + 12 * math.sin(a)),
                               (c[0] - 12 * math.cos(a), c[1] - 12 * math.sin(a))), 0.8)
                     for a in (0, math.pi / 3, 2 * math.pi / 3))
        out.append(f'<g class="{spin}" opacity="0.7">{sp}</g>')
    fw = 1.6
    out.append(path(line(BK_R, BK_BB, BK_S, BK_R), fw) + path(line(BK_S, BK_HT, BK_HB, BK_BB), fw)
               + path(line(BK_HB, BK_F), fw) + path(line(BK_HT, (20, -36), (22, -31), (19.5, -29.5)), fw)
               + path(line((-14, -37), (-6, -37)), fw + 0.6))  # saddle
    return ''.join(out)


def bike_rider(st, P):
    """The rider from a pose: hip, sh, feet (on the pedals or not), look; both hands on the bars."""
    lw, ik, path, line, add, far = st['lw'], ns['ik'], ns['path'], ns['line'], ns['add'], ns['far']
    hip, sh, hr = P['hip'], P['sh'], st['hr']
    knee_up = P.get('knee_up', False)

    def leg(ft, crank):
        kn = ik(hip, ft, 18, 18, key=(lambda q: -q[1]) if knee_up else (lambda q: q[0]))
        g = path(line(hip, kn, ft), lw) + path(line(add(ft, (-2.5, 0)), add(ft, (3.5, 0))), lw)
        return (path(line(BK_BB, crank), 1.4) if crank else '') + g

    el = ik(sh, BK_BAR, 11, 11, key=lambda q: q[1])
    hc, hd = ns['head'](st, sh, P['look'])
    helmet = path(f'M{ns["pt"](add(hc, (-hr - 0.8, 0.6)))} A{ns["f"](hr + 1)} {ns["f"](hr + 1)} 0 0 1 '
                  f'{ns["pt"](add(hc, (hr + 1.4, 0.4)))}', 1.3)
    return (far(st, leg(P['ffoot'], P.get('fcrank'))) + far(st, path(line(sh, add(el, (-1.5, -0.6)), add(BK_BAR, (-1.5, 0))), lw))
            + path(line(hip, sh), st['tw']) + hd + helmet + leg(P['nfoot'], P.get('ncrank'))
            + path(line(sh, el, BK_BAR), lw))


def pedals(th):
    """Feet on the pedals at crank angle th (near foot), the far one opposite."""
    n = (BK_BB[0] + 6 * math.cos(th), BK_BB[1] + 6 * math.sin(th))
    f_ = (BK_BB[0] - 6 * math.cos(th), BK_BB[1] - 6 * math.sin(th))
    return dict(nfoot=n, ffoot=f_, ncrank=n, fcrank=f_)


def sprint_pose(th):
    """Out of the saddle over the cranks, hips swaying onto the downstroke pedal."""
    hip = (-1 + 1.2 * math.sin(th), -41 + 0.8 * math.cos(2 * th))
    a = math.radians(35)
    return dict(hip=hip, sh=(hip[0] + BK_TORSO * math.cos(a), hip[1] - BK_TORSO * math.sin(a)), look=(0.85, -0.5), **pedals(th))


SEATED = dict(hip=(-10, -39.5), sh=(8, -50), look=(0.75, -0.66), **pedals(0))
# blown backwards: back on the saddle, legs off the pedals stuck out straight in front and flailing, head down
BLOWN = [dict(SEATED, look=(0.8, -0.45), nfoot=(24, -31), ffoot=(21, -19), ncrank=None, fcrank=None),
         dict(SEATED, look=(0.8, -0.45), nfoot=(22, -21), ffoot=(24, -33), ncrank=None, fcrank=None)]
SPRINT_N, SPRINT_P = 8, 0.5                                # fast cadence

# s(t): distance along the ridge from the start (scene units); speeds in scene units/s
BK_X0 = 300
_bt, _bs, _bv, _dt = 0.0, 0.0, 0.0, 1 / 120
T_ACC, T_FADE_V, T_STALL, T_PUSH = 0.6, 2.4, 4.2, 4.7      # top speed, wind takes over, stalled, blown back
_track = [(0.0, 0.0)]
_bike_r = list(reversed([p for p in sample(RIDGE2[:1]) if p[0] <= 400]))   # right to left from x 400
(_ax, _ay), (_bx, _by) = _bike_r[-6], _bike_r[-1]
_bike_r += [(_bx + (_bx - _ax) * t, _by + (_by - _ay) * t) for t in range(1, 80) if _bx + (_bx - _ax) * t > -70]
_bike_r.reverse()                                          # left to right again, from x about -70
_bacc = [0.0]
for _p, _q in zip(_bike_r, _bike_r[1:]):
    _bacc.append(_bacc[-1] + math.hypot(_q[0] - _p[0], _q[1] - _p[1]))
_s0 = next(a for a, p in zip(_bacc, _bike_r) if p[0] >= BK_X0)


def bike_at(s):
    """Point and slope angle on the ridge at distance s from the start (negative: back down the slope)."""
    s += _s0
    j = max(0, min(len(_bacc) - 2, next((i for i, a in enumerate(_bacc) if a > s), len(_bacc) - 1) - 1))
    u = (s - _bacc[j]) / max(1e-9, _bacc[j + 1] - _bacc[j])
    p, q = _bike_r[j], _bike_r[j + 1]
    x, y = p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u
    r0, r1 = _bike_r[max(0, j - 3)], _bike_r[min(len(_bike_r) - 1, j + 4)]
    ang = max(-14, min(14, math.degrees(math.atan2(r1[1] - r0[1], r1[0] - r0[0]))))
    return x, y, ang


while True:
    if _bt < T_ACC:
        _bv = 28 * _bt / T_ACC
    elif _bt < T_FADE_V:
        _bv = 28 - 16 * (_bt - T_ACC) / (T_FADE_V - T_ACC)
    elif _bt < T_STALL:
        _bv = 12 * (1 - (_bt - T_FADE_V) / (T_STALL - T_FADE_V))
    elif _bt < T_PUSH:
        _bv = 0
    else:
        _bv -= 65 * _dt                                    # the gust and the slope roll him back, faster and faster
    _bs += _bv * _dt
    _bt += _dt
    _track.append((_bt, _bs))
    if bike_at(_bs)[0] < -40:                              # all of him past the left edge (half length ~13 units)
        break
D_BIKE = math.ceil(_bt * 100) / 100
bpc = lambda tt: f'{min(100.0, 100 * tt / D_BIKE):.3f}%'
_bkf, _last = [], -1.0
for _t, _s in _track:
    if _t - _last >= 0.08 or _t == _track[-1][0]:
        x, y, ang = bike_at(_s)
        at = '100%' if _t == _track[-1][0] else bpc(_t)
        _bkf.append(f'  {at} {{ transform: translate({x:.1f}px, {y:.1f}px) rotate({ang:.1f}deg); }}')
        _last = _t
_bx0, _by0, _ba0 = bike_at(0)

# the gust: wavy streaks blowing right to left around him, thickest while he stalls
_gusts = []
for i, (d0, y_off) in enumerate([(0.7, -20), (1.2, -34), (1.6, -8), (2.0, -27), (2.3, -14), (2.7, -40), (3.0, -22),
                                  (3.3, -6), (3.6, -31), (3.9, -17), (4.2, -36), (4.5, -11), (4.8, -26), (5.3, -18),
                                  (5.8, -30), (6.3, -12)]):
    x_c = bike_at(max(0.0, min(55.0, 12 * d0)))[0] + 25 + (i % 3) * 14
    y_c = bike_at(0)[1] + y_off
    _gusts.append(f'<g transform="translate({x_c:.0f} {y_c:.0f})"><path class="gust" style="animation-delay: {d0:.2f}s" '
                  f'd="M0 0 q6 -2.5 12 0 t12 0 t12 0 t12 0"></path></g>')
css += ['@keyframes ride-far {\n' + '\n'.join(_bkf) + '\n}',
        f'.ride-far {{ transform: translate({_bx0:.1f}px, {_by0:.1f}px) rotate({_ba0:.1f}deg); }}',
        f'.play .ride-far {{ animation: ride-far {D_BIKE}s linear 1 forwards; }}',
        # seated until hovered, sprinting until the wind wins, then blown back
        '.play .bike-seated { opacity: 0; }',
        '.bike-sprint, .bike-blown { opacity: 0; }',
        f'@keyframes show-sprint {{ 0% {{ opacity: 1; }} {bpc(T_PUSH)}, 100% {{ opacity: 0; }} }}',
        f'@keyframes show-blown {{ 0% {{ opacity: 0; }} {bpc(T_PUSH)}, 100% {{ opacity: 1; }} }}',
        f'.play .bike-sprint {{ animation: show-sprint {D_BIKE}s step-end 1 forwards; }}',
        f'.play .bike-blown {{ animation: show-blown {D_BIKE}s step-end 1 forwards; }}',
        f'.play .sprint .f {{ animation: flip8 {SPRINT_P}s step-end infinite; }}',
        '.play .flail .f { animation: flip2 0.24s step-end infinite; }',
        '@keyframes flip2 { 0% { visibility: visible; } 50.6%, 100% { visibility: hidden; } }',
        '.spin-back { transform-box: fill-box; transform-origin: center; }',
        '.play .spin-back { animation: spin 0.28s linear infinite reverse; }',
        '.bike-fig.done .flip .f, .bike-fig.done .spin, .bike-fig.done .spin-back { animation: none; }',
        '.gust { opacity: 0; }',
        '@keyframes gust { 0% { opacity: 0; transform: translate(0, 0); } 25% { opacity: 0.3; } '
        '100% { opacity: 0; transform: translate(-110px, 3px); } }',
        '.play .gust { animation: gust 0.9s linear 1; }']
print(f'far cyclist: stall at x {bike_at(_track[next(i for i, (t, _) in enumerate(_track) if t >= T_STALL)][1])[0]:.0f}, '
      f'blown out of the picture after {D_BIKE}s')
_sprint_frames = [ns['wrap'](bike_rider(st, sprint_pose(2 * math.pi * k / SPRINT_N))) for k in range(SPRINT_N)]
_blown_frames = [ns['wrap'](bike_rider(st, p)) for p in BLOWN]
marks.append(f'''<g class="fig bike-fig" data-play="{D_BIKE}" data-once="bike">
    <g fill="none" stroke="{INK}" stroke-width="0.5" stroke-linecap="round">{''.join(_gusts)}</g>
    <g class="ride-far"><g transform="scale({BK_SCALE})" opacity="0.75">
      <g class="bike-seated">{hit(-60, -100, 120, 110)}{ns['wrap'](bike(st, 'spin') + bike_rider(st, SEATED))}</g>
      <g class="bike-sprint">{ns['wrap'](bike(st, 'spin'))}{ns['flip']('flip sprint', _sprint_frames, SPRINT_P)}</g>
      <g class="bike-blown">{ns['wrap'](bike(st, 'spin-back'))}{ns['flip']('flip flail', _blown_frames, 0.24)}</g>
    </g></g>
  </g>''')

def timed(frames, end):
    """Frames (start, svg) shown once each, back to back with no overlap (a double frame shows as a ghost):
    each one until the next starts, the last until end. Times in whole milliseconds so the slots tile exactly."""
    ms = [round(t0 * 1000) for t0, _ in frames] + [round(end * 1000)]
    return ns['wrap'](''.join(f'<g class="tf" style="animation-delay: {a / 1000:.3f}s; animation-duration: {(b - a) / 1000:.3f}s">{svg}</g>'
                              for (_, svg), a, b in zip(frames, ms, ms[1:])))


# Camp: tent, fire and a stump to sit on. The fire flickers and smokes all the time (CSS in FLIP); it is
# not a hover figure any more. Camp and hiker are both drawn at scale 0.5, so their units match.
CAMP = (931, 535)
SPOT = 38                        # camp x where the hiker stands up: the origin of his own frames
LOG_X, LOG_R = 50, 5.5                  # a tree stump still in the ground as the seat; cut face at y -2 * LOG_R
_top = -2 * LOG_R
STUMP_D = (f'M{LOG_X - 5} {_top} L{LOG_X - 4.7} -4 C{LOG_X - 4.7} -2 {LOG_X - 6.5} -0.6 {LOG_X - 9} 0 '
           f'L{LOG_X + 9} 0 C{LOG_X + 6.5} -0.6 {LOG_X + 4.7} -2 {LOG_X + 4.7} -4 L{LOG_X + 5} {_top} Z')
STUMP_TOP = f'cx="{LOG_X}" cy="{_top}" rx="5" ry="1.5"'
stump = (f'<path d="{STUMP_D}" fill="{ns["PAPER"]}" stroke-width="1.3"></path>'
         f'<ellipse {STUMP_TOP} fill="{ns["PAPER"]}" stroke-width="1.1"></ellipse>'
         f'<ellipse cx="{LOG_X}" cy="{_top}" rx="2.4" ry="0.6" stroke-width="0.7"></ellipse>'
         + ns['path'](f'M{LOG_X - 1.5} 0 C{LOG_X - 1} -1.4 {LOG_X - 0.6} -2.4 {LOG_X} -3.4', 0.9)       # middle root
         + ns['path'](f'M{LOG_X + 2.2} {_top + 3} L{LOG_X + 2} {_top + 6.5}', 0.7))                     # bark
marks.append(f'''<g>
    <g transform="translate({CAMP[0]} {CAMP[1]}) scale(0.5)" opacity="0.85">{camp(st, sitter=False)}</g>
  </g>''')


# Hiker at the fire: sits on the stump facing it, resting on his poles. Hovered, he pushes himself up, turns
# and walks off to the right along the second ridge until he is out of the picture (once per page load).
# Sitting and standing up are drawn facing right in his own frame (origin where he stands, feet at y 0)
# and mirrored, so he faces the fire; the walk is the plain hiker flipbook, unmirrored.
TORSO, POLE = math.hypot(3.5, 19), 36.5                # torso and pole length as in the walking hiker
LEAN_REF = math.degrees(math.atan2(3.5, 19))           # torso lean the backpack is drawn for


def hiker_pose(st, P):
    """One hiker frame from a pose: hip, lean (deg, forward), feet, hands, pole tips, look (head direction)."""
    lw, ik, path, line, add, far = st['lw'], ns['ik'], ns['path'], ns['line'], ns['add'], ns['far']
    hip, a = P['hip'], math.radians(P['lean'])
    sh = (hip[0] + TORSO * math.sin(a), hip[1] - TORSO * math.cos(a))

    def arm(hand, tip):
        el = ik(sh, hand, 9.5, 9, key=lambda q: -q[0])  # elbow out behind
        d = math.hypot(hand[0] - tip[0], hand[1] - tip[1])
        top = (tip[0] + (hand[0] - tip[0]) * POLE / d, tip[1] + (hand[1] - tip[1]) * POLE / d)
        return path(line(sh, el, hand), lw) + path(line(top, tip), 1.1)

    def leg(ft):
        kn = ik(hip, ft, 15, 15, key=lambda q: q[0])    # knee forward
        return path(line(hip, kn, ft), lw) + path(line(add(ft, (-1.5, 0)), add(ft, (3.5, 0))), lw)

    hr = st['hr']
    pack = (f'<g transform="rotate({P["lean"] - LEAN_REF:.1f} {sh[0]:.1f} {sh[1]:.1f})">'
            f'<rect x="{sh[0] - 10.5:.1f}" y="{sh[1] - 2:.1f}" width="7.5" height="16" rx="2" fill="{ns["PAPER"]}" '
            f'stroke-width="1.3" transform="rotate(6 {sh[0] - 6:.1f} {sh[1] + 6:.1f})"></rect>'
            + path(line((sh[0] - 4, sh[1] + 1), (sh[0] - 1, sh[1] + 9)), 0.9) + '</g>')
    hc, hd = ns['head'](st, sh, P['look'])
    cap = (path(line(add(hc, (-hr - 2, -hr + 1.2)), add(hc, (hr + 3, -hr + 1.6))), 1.2)
           + f'<path d="M{ns["pt"](add(hc, (-hr + 0.5, -hr + 1.2)))} q{ns["f"](hr - 0.5)} -{ns["f"](hr + 0.4)} '
             f'{ns["f"](2 * hr - 0.5)} 0.2" fill="{INK}" stroke="none"></path>')
    return (far(st, arm(P['fhand'], P['ftip'])) + far(st, leg(P['ffoot'])) + leg(P['nfoot']) + pack
            + path(line(hip, sh), st['tw']) + hd + cap + arm(P['nhand'], P['ntip']))


_seat = SPOT - LOG_X                                   # stump centre in his (mirrored) frame
SIT = dict(hip=(_seat + 0.5, -2 * LOG_R - 1.4), lean=5, nfoot=(2.5, 0), ffoot=(-0.5, 0),
           nhand=(0.8, -19.5), fhand=(-0.5, -20), ntip=(1.5, 0.5), ftip=(0, 0.5), look=(0.45, -1))
PUSH = dict(SIT, hip=(_seat + 2, -2 * LOG_R - 2.5), lean=32, nhand=(2, -21), fhand=(0.5, -21.5), look=(0.5, -1))
STAND = dict(SIT, hip=(0.8, -29.4), lean=8, nhand=(4.5, -33.5), fhand=(3, -34), look=(0.25, -1))


def pose_at(u):
    """Sit -> push (lean in, weight onto the feet) -> stand, u in 0..1."""
    a, b, v = (SIT, PUSH, u / 0.4) if u < 0.4 else (PUSH, STAND, (u - 0.4) / 0.6)
    mix = lambda x, y: tuple(x[i] + (y[i] - x[i]) * v for i in range(2)) if isinstance(x, tuple) else x + (y - x) * v
    return {k: mix(a[k], b[k]) for k in a}


HIK_P, HIK_N = 1.1, 10                                 # walking flipbook period and frames (figgen.hiker)
UP_N = 10                                              # stand-up frames, one walking slot each
T_UP = 13 * HIK_P / HIK_N                              # turn and set off on a slot boundary: walking frame 3,
                                                       # near foot under him, far one swinging through
WALK_V = 20 / (0.6 * HIK_P) * 0.5                      # stance foot speed, scene units/s: feet do not slide
smooth = lambda x: x * x * (3 - 2 * x)
up_frames = [((k - 1) * HIK_P / HIK_N, hiker_pose(st, pose_at(smooth(k / UP_N)))) for k in range(1, UP_N + 1)]

# path: from where he stands at the camp onto the ridge line (the camp sits ~3 units below it), along it
# and past the right edge of the picture
_start = (CAMP[0] + SPOT * 0.5, CAMP[1])
_r = [p for p in sample(RIDGE2[2:]) if p[0] >= _start[0]]
(_ax, _ay), (_bx, _by) = _r[-6], _r[-1]
_r += [(_bx + (_bx - _ax) * t, _by + (_by - _ay) * t) for t in range(1, 60) if _bx + (_bx - _ax) * t < 1458]
_acc = [0.0]
for _p, _q in zip(_r, _r[1:]):
    _acc.append(_acc[-1] + math.hypot(_q[0] - _p[0], _q[1] - _p[1]))
_off = _start[1] - _r[0][1]
_route = [(x, y + _off * (1 - smooth(min(1.0, s / 40)))) for (x, y), s in zip(_r, _acc)]
T_WALK = _acc[-1] / WALK_V
D_CAMP = math.ceil((T_UP + T_WALK) * 100) / 100     # rounded up: a keyframe past 100% is dropped
pc = lambda tt: f'{min(100.0, 100 * tt / D_CAMP):.3f}%'


def _tf(i):
    j0, j1 = max(0, i - 4), min(len(_route) - 1, i + 4)
    ang = math.degrees(math.atan2(_route[j1][1] - _route[j0][1], _route[j1][0] - _route[j0][0]))
    ang = max(-4.0, min(4.0, 0.3 * ang))               # walkers stay upright; just a hint of the slope,
    ang *= smooth(min(1.0, _acc[i] / 40))              # none while he sits at the camp
    return f'translate({_route[i][0]:.1f}px, {_route[i][1]:.1f}px) rotate({ang:.1f}deg)'


_kf = [f'  0%, {pc(T_UP)} {{ transform: {_tf(0)}; }}']
_step = max(1, len(_route) // 80)
for i in list(range(_step, len(_route) - 1, _step)) + [len(_route) - 1]:
    at = '100%' if i == len(_route) - 1 else pc(T_UP + _acc[i] / WALK_V)   # an end short of 100% falls back
    _kf.append(f'  {at} {{ transform: {_tf(i)}; }}')                        # to the start position
css += ['@keyframes camp-walk {\n' + '\n'.join(_kf) + '\n}', f'.camp-walk {{ transform: {_tf(0)}; }}',
        f'.play .camp-walk {{ animation: camp-walk {D_CAMP}s linear 1 forwards; }}',
        # sitting until hovered, stand-up frames (.tf, timed), then the walking flipbook from T_UP on
        '.play .sit-part { opacity: 0; }',
        '.walk-part { opacity: 0; }',
        f'@keyframes show-walk {{ 0% {{ opacity: 0; }} {pc(T_UP)}, 100% {{ opacity: 1; }} }}',
        f'.play .walk-part {{ animation: show-walk {D_CAMP}s step-end 1 forwards; }}',
        '.camp-fig.done .flip .f { animation: none; }']
print(f'camp hiker: up {T_UP:.2f}s, walk {_acc[-1]:.0f} u in {T_WALK:.1f}s at {WALK_V:.1f} u/s, run {D_CAMP}s')
marks.append(f'''<g class="fig camp-fig" data-play="{D_CAMP}" data-once="camp">
    <g class="camp-walk">
      <g class="sit-part"><g transform="scale(-0.5 0.5)" opacity="0.85">{hit(-20, -42, 34, 44)}{ns['wrap'](hiker_pose(st, SIT))}</g></g>
      <g transform="scale(-0.5 0.5)" opacity="0.85">{timed(up_frames, T_UP)}</g>
      <g class="walk-part"><g transform="scale(0.5 0.5)" opacity="0.85">{hiker(st)}</g></g>
    </g>
  </g>''')
# the stump goes in front of him: he sits on its top and, setting off, walks behind it (its fill hides his
# feet; legs drawn across it looked like he walked through it). An opaque backing keeps him from
# showing through the 0.85 opacity.
marks.append(f'''<g>
    <g transform="translate({CAMP[0]} {CAMP[1]}) scale(0.5)" fill="{ns['PAPER']}" stroke="{ns['PAPER']}" stroke-width="1.4"><path d="{STUMP_D}"></path><ellipse {STUMP_TOP}></ellipse></g>
    <g transform="translate({CAMP[0]} {CAMP[1]}) scale(0.5)" opacity="0.85">{ns['wrap'](stump)}</g>
  </g>''')


# One skeleton for the ski tourer and the downhill skier, so the two can be blended into each other.
# A pose is a dict of points and numbers; rider() draws any pose, tour_pose()/ski_pose() give the two
# looping gaits by phase, and blend() mixes two poses key by key.
SKI_N, SKI_P = 12, 0.8          # downhill pump loop: frames, period (s)
TOUR_N, TOUR_P = 16, 1.6        # skinning stride loop
# preferred side for knees and elbows, and which way the boots point (all flip with the body in the crash)
# The ski tourer / skier on the far ridge, figure units -> scene units (was 0.7; 80% so he reads as farther away
# than the camp and the cyclist, 2026-11-16). The crash physics converts with it too.
SKI_SCALE = 0.56
UPRIGHT = dict(kdir=(1, 0), edir=(0, 1), nbdir=(1, 0), fbdir=(1, 0))
HREF = math.degrees(math.atan2(0.42, 1))   # head tilt the goggle offsets are drawn for


def rot(v, deg):
    a = math.radians(deg)
    c, s_ = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s_, v[0] * s_ + v[1] * c)


def tour_pose(ph):
    """Skinning uphill: skis slide (never lift), opposite pole planted."""
    fwd = math.cos(ph)                       # near foot forward at +1
    bob = -0.6 * math.cos(2 * ph)
    sh = (3.5, -29 + bob)
    nf, ff = 6 * fwd, -6 * fwd
    nh, fh = (sh[0] + 1 - 5.5 * fwd, -18 + bob), (sh[0] + 1 + 5.5 * fwd, -18 + bob)   # far arm swings with the near leg
    return dict(hip=(0, -15.5 + bob), sh=sh, hdir=(0.3, -1), thigh=8.5,
                nfoot=(nf, -1.6), ffoot=(ff, -1.6),
                nski=(nf - 13, 0, nf + 13, 0, 1.4), fski=(ff - 13, 0, ff + 13, 0, 1.4), **UPRIGHT,
                nhand=nh, ngrip=(nh[0], nh[1] - 3), ntip=(nh[0] - 2.5, 0.8),
                fhand=fh, fgrip=(fh[0], fh[1] - 3), ftip=(fh[0] - 2.5, 0.8),
                pack=(sh[0] - 6, sh[1] + 5.5, 8))


def pack_for(hip, sh):
    vx, vy = sh[0] - hip[0], sh[1] - hip[1]
    n = math.hypot(vx, vy)
    return ((hip[0] + sh[0]) / 2 + 4 * vy / n, (hip[1] + sh[1]) / 2 - 4 * vx / n, math.degrees(math.atan2(vx, -vy)))


def ski_pose(ph):
    """Downhill tuck with a gentle crouch-and-pump."""
    c = 1.5 * math.sin(ph)
    hip, sh = (-5, -15 + c), (3, -28 + 0.8 * c)
    pack = pack_for(hip, sh)                                    # backpack sits behind the torso, tilted with it
    nh, fh = (10, -18 + c), (8, -19 + c)
    return dict(hip=hip, sh=sh, hdir=(0.55, -1), thigh=9.5,
                nfoot=(0, -1.8), ffoot=(2.5, -2.8),
                nski=(-14, 0, 13, 0, 1.5), fski=(-11, -1.3, 14, -1.3, 1.3), **UPRIGHT,
                nhand=nh, ngrip=nh, ntip=(-6, 1.5),
                fhand=fh, fgrip=fh, ftip=(-8, 0.5),
                pack=pack)


def blend(a, b, u):
    mix = lambda x, y: x + (y - x) * u
    return {k: tuple(mix(x, y) for x, y in zip(a[k], b[k])) if isinstance(a[k], tuple) else mix(a[k], b[k]) for k in a}


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def ski_d(ski):
    """Path of a ski (tail x, y, tip x, y, width): straight base, tip curling up off the base line."""
    x0, y0, x1, y1, _ = ski
    d = unit((x1 - x0, y1 - y0))
    q, e = (x1 + 3 * d[0], y1 + 3 * d[1]), (x1 + 4 * d[0] + 2.3 * d[1], y1 + 4 * d[1] - 2.3 * d[0])
    return f'M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f} Q{q[0]:.1f} {q[1]:.1f} {e[0]:.1f} {e[1]:.1f}'


def knee(p, foot):
    k = p['kdir']
    return ns['ik'](p['hip'], foot, p['thigh'], p['thigh'], key=lambda q: q[0] * k[0] + q[1] * k[1])


def elbow(p, hand):
    e = p['edir']
    return ns['ik'](p['sh'], hand, 7.5, 7.5, key=lambda q: q[0] * e[0] + q[1] * e[1])


def rider(st, p):
    """Draw a pose facing right, ski bases at y=0. Far side first and faint, then pack, torso, head, near side."""
    path, line, ik, head, far = ns['path'], ns['line'], ns['ik'], ns['head'], ns['far']
    lw, hip, sh = st['lw'], p['hip'], p['sh']

    def leg_and_ski(foot, ski, bdir):
        b = unit(bdir)
        g = (path(line(hip, knee(p, foot), foot), lw)
             + path(line((foot[0] - 1.5 * b[0], foot[1] - 1.5 * b[1]), (foot[0] + 3 * b[0], foot[1] + 3 * b[1])), lw + 0.4))
        return g + (path(ski_d(ski), ski[4]) if ski else '')

    def arm_and_pole(hand, grip, tip):
        return path(line(sh, elbow(p, hand), hand), lw) + path(line(grip, tip), 0.9)

    cx, cy, tilt = p['pack']
    hc, hd = head(st, sh, p['hdir'])
    r = st['hr']
    turn = math.degrees(math.atan2(p['hdir'][0], -p['hdir'][1])) - HREF      # beanie and goggles turn with the head
    g0, g1 = rot((0.8, -0.9), turn), rot((4.2, -0.2), turn)
    return ''.join([
        far(st, leg_and_ski(p['ffoot'], p['fski'], p['fbdir']) + arm_and_pole(p['fhand'], p['fgrip'], p['ftip'])),
        f'<rect x="{cx - 3.5:.1f}" y="{cy - 6.5:.1f}" width="7" height="13" rx="2" fill="{ns['PAPER']}" '
        f'stroke-width="1.2" transform="rotate({tilt:.1f} {cx:.1f} {cy:.1f})"></rect>',                  # backpack
        path(line(hip, sh), st['tw']),
        hd,
        f'<path d="M{hc[0] - r:.1f} {hc[1] - 0.5:.1f} a{r:.1f} {r:.1f} 0 0 1 {2 * r:.1f} 0 l0.8 1.2 '
        f'l-{2 * r + 1.6:.1f} 0 z" fill="{INK}" stroke="none" transform="rotate({turn:.0f} {hc[0]:.1f} {hc[1]:.1f})"></path>',  # beanie
        path(f'M{hc[0] + g0[0]:.1f} {hc[1] + g0[1]:.1f} L{hc[0] + g1[0]:.1f} {hc[1] + g1[1]:.1f}', 1.4, f' stroke="{ns["PAPER"]}"'),  # goggles
        leg_and_ski(p['nfoot'], p['nski'], p['nbdir']),
        arm_and_pole(p['nhand'], p['ngrip'], p['ntip']),
    ])


def skier(st):
    """Downhill skier, pump loop as a flipbook, snow spray behind the skis."""
    frs = [rider(st, ski_pose(2 * math.pi * k / SKI_N)) for k in range(SKI_N)]
    # snow spray: small flakes kicked up behind the skis, arcing back down (not smoke puffs)
    flake = 'M-2 0 L2 0 M-1 -1.7 L1 1.7 M-1 1.7 L1 -1.7'
    spray = ''.join(
        f'<path class="flake" style="--dx: {dx}px; --dy: {dy}px; animation-delay: -{dl:.2f}s" '
        f'transform="translate({x0} -1)" d="{flake}" stroke-width="0.8" opacity="0"></path>'
        for x0, dx, dy, dl in ((-13, -7, -3, 0.0), (-14, -11, -2, 0.12), (-12, -5, -4.5, 0.24), (-15, -13, -3, 0.36),
                               (-13, -9, -5, 0.48), (-14, -6, -1.5, 0.6)))
    return ns['wrap'](spray + ns['flip']('flip ski', frs, SKI_P))


def tourer(st):
    """Ski tourer skinning uphill, stride loop as a flipbook."""
    frs = [rider(st, tour_pose(2 * math.pi * k / TOUR_N)) for k in range(TOUR_N)]
    return ns['wrap'](ns['flip']('flip tour', frs, TOUR_P))


# Ski tourer: skins up the right flank of the middle peak, goes straight over the crest into downhill,
# skis down into the valley, carries the speed over the second (smaller) summit to the left and
# crashes on its far side (wobble, falls, slides, both skis stick in the snow), then disappears for good
# (once per page load; the skis and the groove stay). Speeds come from the terrain; all timings are in seconds.
RIDGE1 = [((0, 520), (120, 470), (200, 500), (300, 450)), ((300, 450), (380, 410), (430, 470), (520, 440)),
          ((520, 440), (640, 400), (700, 330), (780, 400)), ((780, 400), (860, 470), (940, 430), (1040, 380))]
fpts = sample(RIDGE1)
up = list(reversed(clip(fpts, 690, 800)))          # moving left = uphill on the right flank
down = list(reversed(clip(fpts, 205, 688)))        # crest -> valley -> second summit -> its far side
route = up + down


def cum(pp):
    acc = [0.0]
    for p0, p1 in zip(pp, pp[1:]):
        acc.append(acc[-1] + math.hypot(p1[0] - p0[0], p1[1] - p0[1]))
    return acc


racc = cum(route)
A = cum(up)[-1]


def idx(sd):
    j = 0
    while j < len(racc) - 2 and racc[j + 1] < sd:
        j += 1
    return j


def frame_at(sd):
    """Position and tilt of the figure's frame at distance sd along the route, between the samples."""
    def ang_at(j):
        q, r = route[min(j + 3, len(route) - 1)], route[max(j - 3, 0)]
        ang = math.degrees(math.atan2(q[1] - r[1], q[0] - r[0])) - 180
        return max(-30, min(30, ((ang + 180) % 360) - 180))
    j = idx(sd)
    f = max(0.0, min(1.0, (sd - racc[j]) / max(1e-9, racc[j + 1] - racc[j])))
    (x0, y0), (x1, y1) = route[j], route[j + 1]
    return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, ang_at(j) + (ang_at(j + 1) - ang_at(j)) * f


def where(sd):
    x, y, a = frame_at(sd)
    return f'translate({x:.1f}px, {y:.1f}px) rotate({a:.1f}deg)'


# landmarks along the route (distance from the start)
j_top2 = min((j for j in range(len(route)) if 250 <= route[j][0] <= 450), key=lambda j: route[j][1])
j_val = max((j for j in range(len(route)) if route[j_top2][0] < route[j][0] < 650), key=lambda j: route[j][1])
S_TOP2, S_VAL = racc[j_top2], racc[j_val]
y_crest = route[len(up) - 1][1]

# speed: climbing pace on the way up; downhill, v^2 grows with the height lost and loses a bit to
# friction, tuned so he is down to about half his valley speed on the second summit
T_CLIMB = 7.4
V0 = A / T_CLIMB
K = 170.0
drop = lambda sd: route[idx(sd)][1] - y_crest
vv2 = V0 ** 2 + K * drop(S_VAL)
F = (V0 ** 2 + K * drop(S_TOP2) - 0.25 * vv2) / ((S_TOP2 - A) - 0.25 * (S_VAL - A))
speed = lambda sd: math.sqrt(max(64.0, V0 ** 2 + K * drop(sd) - F * (sd - A)))

S_WOB = S_TOP2 + 16                                  # over the second top, starting down: catches an edge
times, sd, t = [], A, T_CLIMB                        # integrate the descent
while sd < S_WOB:
    times.append((t, sd))
    t += 2.0 / speed(sd)
    sd += 2.0
t_wob, v_wob = round(t, 3), speed(S_WOB)          # whole ms, like the frame slots

# The crash, in seconds after the edge catch (poses in CRASH below): the skis release at T_REL, he hits the
# snow at T_IMP, rolls over his shoulder onto his back, slides feet first to a stop at T_STOP, settles by T_SET.
T_REL, T_IMP, T_STOP, T_SET, T_LIE, T_FADE = 0.40, 0.62, 2.22, 2.65, 0.1, 0.5
t_rel, t_imp, t_stop = t_wob + T_REL, t_wob + T_IMP, t_wob + T_STOP
t_fade = t_wob + T_SET + T_LIE
t_gone = t_fade + T_FADE
v_imp = 0.85 * v_wob                                 # the catch takes some speed off; he flies on to the impact


def s_at(tt):
    """Distance along the route during the crash: braking on the catch, flying, then sliding to a stop."""
    u = min(tt, t_rel) - t_wob
    s = S_WOB + v_wob * u + (v_imp - v_wob) * u * u / (2 * T_REL)
    if tt > t_rel:
        s += v_imp * (min(tt, t_imp) - t_rel)
    if tt > t_imp:
        u, T = min(tt, t_stop) - t_imp, T_STOP - T_IMP
        s += v_imp * u - v_imp * u * u / (2 * T)
    return s


S_REL, S_IMP, S_STOP = s_at(t_rel), s_at(t_imp), s_at(t_stop)
D = round(t_gone, 2)                                 # one run, ends with him gone
# rounded down, fine: a step keyframe then switches at (or a hair before) the ms its frame slot starts
P = lambda tt: f'{math.floor(1e6 * tt / D + 1e-6) / 1e4:.4f}%'
t_at = lambda target: next(tt for tt, sd in times if sd >= target)
print(f'run {D}s: crest {T_CLIMB}s, valley {t_at(S_VAL):.1f}s at {speed(S_VAL):.0f} u/s, second top {t_at(S_TOP2):.1f}s at '
      f'{speed(S_TOP2):.0f} u/s, edge catch {t_wob:.1f}s, impact {t_imp:.1f}s, stop {t_stop:.1f}s, slide {S_STOP - S_IMP:.0f} u')

kf = []
for i in range(31):                                  # skinning up, steady pace
    kf.append(f'  {P(T_CLIMB * i / 30)} {{ transform: {where(A * i / 30)}; opacity: 1; }}')
for tt, sd in times[1::3]:                           # downhill, valley, over the second top
    kf.append(f'  {P(tt)} {{ transform: {where(sd)}; opacity: 1; }}')
crash_kf = {P(t_wob + 0.04 * i): t_wob + 0.04 * i for i in range(int(T_STOP / 0.04) + 1)}
crash_kf.update({P(tt): tt for tt in (t_wob, t_rel, t_imp, t_stop)})   # the events land exactly on a keyframe
kf += [f'  {pc} {{ transform: {where(s_at(tt))}; opacity: 1; }}' for pc, tt in sorted(crash_kf.items(), key=lambda kv: kv[1])]
lie = where(S_STOP)
kf += [f'  {P(t_fade)} {{ transform: {lie}; opacity: 1; }}', f'  100% {{ transform: {lie}; opacity: 0; }}']


T_DESC = t_wob - T_CLIMB

# Over the crest the tourer straightens into the downhill tuck through in-between frames: both gaits keep
# running on their own clocks (the same clocks as their flipbooks) while the blend eases from one to the other.
T_M0, T_M1, M_N = T_CLIMB - 0.22, T_CLIMB + 0.22, 11
M_DT = (T_M1 - T_M0) / M_N
# At each handoff (tourer -> in-between frames -> downhill skier -> crash) the outgoing part stays up this much
# longer, so both show for about two display frames. With exact handoffs Chrome now and then drew neither
# for one frame just before the switch (seen in real-time captures, never in the paused timeline); the poses
# match at each handoff, so the overlap doesn't show.
T_OVER = 0.04


def morph_frames(st):
    out = []
    for i in range(M_N):
        t = T_M0 + i * M_DT
        u = (i + 1) / (M_N + 1)
        u = u * u * (3 - 2 * u)                                           # ease in and out
        pose = blend(tour_pose(2 * math.pi * t / TOUR_P), ski_pose(2 * math.pi * t / SKI_P), u)
        out.append((t, rider(st, pose)))
    return timed(out, T_M1 + T_OVER)


# ── The crash ──────────────────────────────────────────────────────────────
# Keyposes are posed in the figure's own frame (facing +x = downhill, ski bases on y = 0). Each is also kept in
# body coordinates (turned upright by -phi about the middle of the torso), and the in-betweens are splined there,
# so the body bends and turns instead of points sliding along straight lines. While the skis are on, feet and
# skis are splined in the frame so they stay on the snow. After the release the body is set down on the snow
# (or held at its height in the air) frame by frame.
PTS = ('hip', 'sh', 'nfoot', 'ffoot', 'nhand', 'ngrip', 'ntip', 'fhand', 'fgrip', 'ftip')
VECS = ('hdir', 'kdir', 'edir', 'nbdir', 'fbdir')
ON_SKIS = {'nfoot', 'ffoot', 'nbdir', 'fbdir', 'nski', 'fski'}
TORSO, POLE, H_AIR, CRASH_FPS = 15.3, 22.0, 2.0, 25


def xf(p, phi, P, inverse=False):
    """Frame -> body coordinates (inverse: body -> frame)."""
    def pt(v):
        if inverse:
            r = rot(v, phi)
            return (r[0] + P[0], r[1] + P[1])
        return rot((v[0] - P[0], v[1] - P[1]), -phi)
    turn = phi if inverse else -phi
    out = {}
    for k, v in p.items():
        if v is None or k == 'thigh':
            out[k] = v
        elif k in PTS:
            out[k] = pt(v)
        elif k in VECS:
            out[k] = rot(v, turn)
        elif k in ('nski', 'fski'):
            out[k] = (*pt(v[:2]), *pt(v[2:4]), v[4])
        elif k == 'pack':
            out[k] = (*pt(v[:2]), v[2] + turn)
    return out


def lowest(p):
    """Lowest drawn point of a pose without skis or pole tips (y, x), stroke widths included."""
    pts = [(p['hip'], 1.15), (p['sh'], 1.15), (p['nhand'], 0.85), (p['fhand'], 0.85),
           (elbow(p, p['nhand']), 0.85), (elbow(p, p['fhand']), 0.85)]
    for f, b in (('nfoot', 'nbdir'), ('ffoot', 'fbdir')):
        u = unit(p[b])
        pts += [(knee(p, p[f]), 0.85), ((p[f][0] + 3 * u[0], p[f][1] + 3 * u[1]), 1.05),
                ((p[f][0] - 1.5 * u[0], p[f][1] - 1.5 * u[1]), 1.05)]
    hc = ns['head'](st, p['sh'], p['hdir'])[0]
    pts.append(((hc[0], hc[1] + st['hr']), 0))
    cx, cy, tilt = p['pack']
    pts += [((cx + c[0], cy + c[1]), 0.3) for c in (rot((sx * 3.5, sy * 6.5), tilt) for sx in (-1, 1) for sy in (-1, 1))]
    (x, y), m = max(pts, key=lambda q: q[0][1] + q[1])
    return y + m, x


def shift(p, dy):
    return xf(p, 0, (0, -dy))


def pre(t, phi, hip, nhand, npole, fhand, fpole, hdir, nfoot, nski, ffoot, fski, kdir=(1, 0)):
    """Keypose with the skis still on, posed in the frame; skis as (angle, width) set under the foot."""
    sh = (hip[0] + TORSO * math.sin(math.radians(phi)), hip[1] - TORSO * math.cos(math.radians(phi)))
    p = dict(hip=hip, sh=sh, hdir=hdir, thigh=9.5, kdir=kdir, edir=(0, 1), pack=pack_for(hip, sh),
             nhand=nhand, ngrip=nhand, fhand=fhand, fgrip=fhand)
    for side, hand, pole in (('n', nhand, npole), ('f', fhand, fpole)):
        u = unit(pole)
        p[side + 'tip'] = (hand[0] + POLE * u[0], hand[1] + POLE * u[1])
    for side, foot, ski in (('n', nfoot, nski), ('f', ffoot, fski)):
        d = (math.cos(math.radians(ski[0])), math.sin(math.radians(ski[0])))
        base = (foot[0] - 1.7 * d[1], foot[1] + 1.7 * d[0])
        p[side + 'foot'], p[side + 'bdir'] = foot, d
        p[side + 'ski'] = (base[0] - 12.5 * d[0], base[1] - 12.5 * d[1], base[0] + 13.5 * d[0], base[1] + 13.5 * d[1], ski[1])
    return keypose(t, p, phi, True)


def keypose(t, frame, phi, on_skis):
    P = ((frame['hip'][0] + frame['sh'][0]) / 2, (frame['hip'][1] + frame['sh'][1]) / 2)
    return dict(t=t, phi=phi, P=P, frame=frame, body=xf(frame, phi, P), on=on_skis)


def post(t, phi, px, nfoot, ffoot, nhand, npole, fhand, fpole, hdir, kdir=(1, 0), edir=(0, 1), bdir=(1, 0)):
    """Keypose after the release, in body coordinates (upright, facing +x): feet from the hip, hands from the
    shoulder. phi turns it into the frame; it is then set down on the snow."""
    hip, sh = (0, TORSO / 2), (0, -TORSO / 2)
    b = dict(hip=hip, sh=sh, hdir=hdir, thigh=9.5, kdir=kdir, edir=edir, nbdir=bdir, fbdir=bdir, nski=None, fski=None,
             pack=(-4, 0, 0), nfoot=(hip[0] + nfoot[0], hip[1] + nfoot[1]), ffoot=(hip[0] + ffoot[0], hip[1] + ffoot[1]))
    for side, hand, pole in (('n', nhand, npole), ('f', fhand, fpole)):
        h = (sh[0] + hand[0], sh[1] + hand[1])
        u = unit(pole)
        b[side + 'hand'] = b[side + 'grip'] = h
        b[side + 'tip'] = (h[0] + POLE * u[0], h[1] + POLE * u[1])
    f = xf(b, phi, (px, 0), inverse=True)
    f = shift(f, -lowest(f)[0] - h_air(t_wob + t))
    return keypose(t, f, phi, False)


k_wob = int(t_wob / (SKI_P / SKI_N)) % SKI_N                 # the downhill frame showing at the edge catch
K0 = ski_pose(2 * math.pi * k_wob / SKI_N)
K3 = pre(T_REL, 63, (2, -15), (27, -13), (-0.3, -1), (24, -11), (0.25, -1), (1, -0.35),
         (-5, -6.5), (16, 1.5), (-3, -4.2), (10, 1.3), kdir=(0.5, 1))       # thrown over the tips, skis come off
_h0 = -lowest(dict(K3['frame'], nski=None, fski=None))[0]


def h_air(tt):
    """Height of the body's lowest point above the snow: from the release on a short arc down to the impact."""
    if tt < t_rel or tt >= t_imp:
        return 0.0
    s = (tt - t_rel) / (t_imp - t_rel)
    return _h0 * (1 - s) + 4 * H_AIR * s * (1 - s)


CRASH = [
    keypose(0, K0, math.degrees(math.atan2(K0['sh'][0] - K0['hip'][0], K0['hip'][1] - K0['sh'][1])), True),
    # the edge catches: skis shoot ahead, he is thrown back, arms fly up, the far ski kicks up
    pre(0.12, 2, (-6, -16), (4, -38), (0.45, 0.89), (-16, -37), (-0.55, 0.83), (-0.15, -1),
        (0, -1.8), (0, 1.5), (3, -6.5), (-12, 1.3)),
    # lurches forward, the near ski's tip digs in, the far ski slaps down
    pre(0.27, 45, (-3, -14), (19, -19), (0.55, 0.835), (14, -33), (0.3, -1), (0.7, -1),
        (1, -3.3), (8, 1.5), (3, -2.8), (0, 1.3)),
    K3,
    # impact: dives into the snow chest first, arms out ahead
    post(T_IMP, 90, 8, (-1.5, 17), (1.5, 16.5), (3, -13.5), (-1, 0.3), (0.5, -13.8), (-1, -0.2), (0.2, -1),
         kdir=(1, 0.2), bdir=(1, 0.3)),
    # rolls over the shoulder, tucked
    post(0.80, 180, 5, (5, -2), (3, 0), (9, 9), (0.3, 1), (8, 6), (-0.2, 1), (0.9, -0.45), kdir=(1, -0.5)),
    # comes out of the roll onto his back, legs swinging downhill, arms flung up
    post(0.98, 258, 2.5, (5, 14), (2, 16.5), (10, -6), (0.9, -0.4), (11, 4), (1, 0.3), (0.4, -1)),
    # slides feet first on his back, arms out
    post(1.18, 268, 0.5, (4, 15.5), (0.5, 17.5), (9, -9), (1, -0.6), (7, 7), (0.8, 0.6), (0.5, -1)),
    # stopped, flat on the snow, arms and poles down along him (clear of the stuck ski)
    post(T_STOP, 272, 0, (1.5, 17.5), (-0.5, 17.8), (1.5, 12.5), (0.08, 1), (-1, 13), (0.1, 1), (0.1, -1)),
    # settles: near knee comes up, lifts his head
    post(T_SET, 270, 0, (6, 11), (0.5, 17.8), (2.5, 12), (0.1, 1), (-1, 13), (0.1, 1), (0.8, -1)),
]


def hermite(ts, vals, i, tt):
    """Catmull-Rom between keys i and i+1 (non-uniform times); vals[j] is None where key j can't be used."""
    def tangent(j):
        if j == len(ts) - 1:
            return None                                       # comes to rest on the last keypose
        lo = j - 1 if j > 0 and vals[j - 1] is not None else j
        hi = j + 1 if vals[j + 1] is not None else j
        return [(b - a) / (ts[hi] - ts[lo]) for a, b in zip(vals[lo], vals[hi])]
    p0, p1 = vals[i], vals[i + 1]
    dt = ts[i + 1] - ts[i]
    s = (tt - ts[i]) / dt
    m0, m1 = tangent(i), tangent(i + 1) or [0] * len(p0)
    h = (2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2)
    return tuple(h[0] * a + h[1] * dt * ma + h[2] * b + h[3] * dt * mb for a, b, ma, mb in zip(p0, p1, m0, m1))


def crash_pose(tt):
    """The crash pose at tt seconds after the edge catch, in the frame."""
    ts = [k['t'] for k in CRASH]
    i = max(j for j in range(len(ts) - 1) if ts[j] <= tt)
    on = CRASH[i]['on'] and CRASH[i + 1]['on']
    tup = lambda v: v if isinstance(v, tuple) else (v,)
    phi = hermite(ts, [(k['phi'],) for k in CRASH], i, tt)[0]
    P = hermite(ts, [k['P'] for k in CRASH], i, tt)
    body, frame = {}, {}
    for key in CRASH[0]['body']:
        space = 'frame' if on and key in ON_SKIS else 'body'
        vals = [tup(k[space][key]) if k[space][key] is not None and (space == 'body' or k['on']) else None for k in CRASH]
        if vals[i] is None or vals[i + 1] is None:
            frame[key] = None                                 # skis gone
            continue
        v = hermite(ts, vals, i, tt)
        (frame if space == 'frame' else body)[key] = v if len(v) > 1 else v[0]
    p = {**xf(body, phi, P, inverse=True), **frame}
    if not on:
        p = shift(p, -lowest(p)[0] - h_air(t_wob + tt))
    return p


def crash_frames(st):
    """Sample the crash at up to CRASH_FPS; a new frame only where something moved, each up until the next."""
    ts = [k['t'] for k in CRASH]
    samples = []
    for t0, t1 in zip(ts, ts[1:]):
        n = math.ceil((t1 - t0) * CRASH_FPS)
        samples += [t0 + (t1 - t0) * k / n for k in range(n)]
    samples.append(ts[-1])
    keep, last = [], None
    for tt in samples:
        p = crash_pose(tt)
        sig = [c for k in PTS for c in p[k]] + [p['nski'] is None]
        if last is None or sig[-1] != last[-1] or max(abs(a - b) for a, b in zip(sig[:-1], last[:-1])) > 0.5:
            keep.append((tt, p))
            last = sig
    print(f'crash: {len(keep)} frames from {len(samples)} samples')
    return timed([(t_wob + tt, rider(st, p)) for tt, p in keep], t_gone + 0.05)


# The lost skis: they take over from the figure's skis exactly at the release, in a frame fixed where he was
# then, and end up as a yard sale: the far ski drops off and stays put, the near one tumbles on and sticks tail
# first in the snow between it and him.
FX, FY, FA = frame_at(S_REL)


def to_local(q):
    r = rot((q[0] - FX, q[1] - FY), -FA)
    return (r[0] / -SKI_SCALE, r[1] / SKI_SCALE)


_j = idx(S_REL)
GROUND = [to_local(q) for q in route[max(0, _j - 30): _j + 90]]
assert all(b[0] > a[0] for a, b in zip(GROUND, GROUND[1:])), 'route must run along +x in the release frame'


def ground(x):
    for (x0, y0), (x1, y1) in zip(GROUND, GROUND[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return GROUND[-1][1] if x > GROUND[-1][0] else GROUND[0][1]


slope = lambda x: math.degrees(math.atan2(ground(x + 2) - ground(x - 2), 4))
_g = rot((0, 220), -FA)
GRAV = (_g[0] / -SKI_SCALE, _g[1] / SKI_SCALE)                   # gravity in the release frame
VF = v_imp / SKI_SCALE                                     # his speed there, in figure units


def ski_motion(ski, kind):
    """Keyframes (t, x, y, angle) of a lost ski's middle, from the release on."""
    x0, y0, x1, y1, _ = ski
    c, a0, hl = ((x0 + x1) / 2, (y0 + y1) / 2), math.degrees(math.atan2(y1 - y0, x1 - x0)), math.hypot(x1 - x0, y1 - y0) / 2
    v = (0.75 * VF, -70) if kind == 'stick' else (0.1 * VF, -10)
    fly = lambda tt: (c[0] + v[0] * tt + GRAV[0] * tt * tt / 2, c[1] + v[1] * tt + GRAV[1] * tt * tt / 2)
    out, tt = [], 0.1
    if kind == 'stick':                              # tumbles, lands tail first leaning back at 60 degrees
        while v[1] + GRAV[1] * tt < 0 or fly(tt)[1] < ground(fly(tt)[0]) - (hl * math.sin(math.radians(60)) - 2.5):
            tt += 0.005
        T, land = tt, fly(tt)
        a_end = slope(land[0]) - 120
        tail = (land[0] - hl * math.cos(math.radians(a_end)), 0)
        tail = (tail[0], ground(tail[0]) + 2.5)
        end = (tail[0] + hl * math.cos(math.radians(a_end)), tail[1] + hl * math.sin(math.radians(a_end)))
        fix = (end[0] - land[0], end[1] - land[1])
        for k in range(int(T / 0.03) + 1):
            u = min(1, k * 0.03 / T)
            q = fly(u * T)
            out.append((u * T, q[0] + fix[0] * u, q[1] + fix[1] * u, a0 + (a_end + 360 - a0) * u))   # +1 turn
        for k in range(1, 13):                       # quivers about the buried tail
            u = k * 0.03
            a = a_end + 360 + 7 * math.exp(-9 * u) * math.sin(38 * u)
            out.append((T + u, tail[0] + hl * math.cos(math.radians(a)), tail[1] + hl * math.sin(math.radians(a)), a))
    else:                                            # a low hop, lands flat and skids to a stop
        while v[1] + GRAV[1] * tt < 0 or fly(tt)[1] < ground(fly(tt)[0]):
            tt += 0.005
        T, land = tt, fly(tt)
        a_end = slope(land[0])
        for k in range(int(T / 0.03) + 1):
            u = min(1, k * 0.03 / T)
            q = fly(u * T)
            out.append((u * T, q[0], q[1] + (ground(land[0]) - land[1]) * u, a0 + (a_end - a0) * (u * u * (3 - 2 * u))))
        vx, dec, x, k = v[0] + GRAV[0] * T, 220.0, land[0], 1
        stop = vx / dec
        while True:
            u = min(k * 0.03, stop)
            xx = x + vx * u - dec * u * u / 2
            out.append((T + u, xx, ground(xx), slope(xx)))
            if u >= stop:
                break
            k += 1
    return hl, out


def ski_kf(name, motion):
    kfs = [f'0%, {P(t_rel)} {{ transform: translate({motion[0][1]:.1f}px, {motion[0][2]:.1f}px) rotate({motion[0][3]:.1f}deg); }}']
    kfs += [f'{P(t_rel + tt)} {{ transform: translate({x:.1f}px, {y:.1f}px) rotate({a:.1f}deg); }}' for tt, x, y, a in motion[1:]]
    tt, x, y, a = motion[-1]
    kfs.append(f'100% {{ transform: translate({x:.1f}px, {y:.1f}px) rotate({a:.1f}deg); }}')
    return f'@keyframes {name} {{ ' + ' '.join(kfs) + ' }'


lost = {}
for key, kind, name in (('nski', 'stick', 'lski-a'), ('fski', 'slide', 'lski-b')):
    hl, motion = ski_motion(K3['frame'][key], kind)
    lost[name] = (hl, K3['frame'][key][4], motion)
_end = to_local(frame_at(S_STOP)[:2])
print('lost skis end at x', ', '.join(f'{m[-1][1]:.0f}' for _, _, m in lost.values()), f'(release frame); he stops at x {_end[0]:.0f}')

# snow kicked up where he hits, in a frame fixed at the impact
IX, IY, IA = frame_at(S_IMP)
_ix = -SKI_SCALE * (lowest(crash_pose(T_IMP))[1])          # contact point, scene units (the figure is mirrored)


css += ['@keyframes tour {\n' + '\n'.join(kf) + '\n}', f'.tour-run {{ transform: {where(0)}; }}',
        f'.play .tour-run {{ animation: tour {D}s linear 1 forwards; }}',
        # which figure is showing: tourer until T_M0, in-between frames, downhill skier from T_M1 to the edge (each + T_OVER)
        # catch, then the crash frames (opacity, not visibility: flipbook frames set their own)
        '.ski-part { opacity: 0; }',
        f'@keyframes show-tour {{ 0% {{ opacity: 1; }} {P(T_M0 + T_OVER)}, 100% {{ opacity: 0; }} }}',
        f'@keyframes show-ski {{ 0% {{ opacity: 0; }} {P(T_M1)} {{ opacity: 1; }} {P(t_wob + T_OVER)}, 100% {{ opacity: 0; }} }}',
        f'.play .tour-part {{ animation: show-tour {D}s step-end 1 forwards; }}',
        f'.play .ski-part {{ animation: show-ski {D}s step-end 1 forwards; }}',
        # one-off frames (crest, crash): each is up for its own slot, set by its inline delay and duration
        # switched with visibility, like the flipbooks: an opacity-only animation is started on the compositor,
        # one display frame apart from the rest, which left a blank frame at the ski-to-crash handoff
        '.tf { visibility: hidden; }',
        '@keyframes tframe { 0%, 100% { visibility: visible; } }',
        '.play .tf { animation: tframe 1s linear 1; }',
        # pumping and snow spray only while skiing (frame delays are shifted to the descent)
        # Both flipbooks run from the start of the hover (hidden while not in use) and are never cut off
        # mid-run: delayed or limited flipbooks leave moments with no frame showing. Once the run is over
        # the page adds .done, which stops them.
        # (three parts, like the .play .xyz .f rules it has to beat once Astro scopes every part)
        '.tour-fig.done .flip .f, .tour-fig.done .flake { animation: none; }',
        '.flake { transform-box: fill-box; transform-origin: center; }',
        '@keyframes flake { 0% { opacity: 0.9; translate: 0 0; rotate: 0deg; } 55% { opacity: 0.8; translate: var(--dx) var(--dy); } '
        '100% { opacity: 0; translate: calc(var(--dx) * 1.5) calc(var(--dy) * 0.2); rotate: 120deg; } }',
        f'.play .flake {{ animation: flake 0.7s ease-out {max(1, round(T_DESC / 0.7))}; }}',
        # the lost skis appear at the release, in place of the figure's own (which its frames stop drawing)
        '.lski { opacity: 0; transform-box: view-box; transform-origin: 0 0; }',
        f'@keyframes lski-show {{ 0% {{ opacity: 0; }} {P(t_rel)}, 100% {{ opacity: 1; }} }}',
        *[ski_kf(name, m) for name, (_, _, m) in lost.items()],
        *[f'.play .lski.{name[-1]} {{ animation: lski-show {D}s step-end 1 forwards, {name} {D}s linear 1 forwards; }}'
          for name in lost],
        '.burst { opacity: 0; transform-box: fill-box; transform-origin: center; }',
        f'@keyframes burst {{ 0%, {P(t_imp - 0.01)} {{ opacity: 0; transform: translate(0, 0) scale(0.4); }} '
        f'{P(t_imp + 0.06)} {{ opacity: 0.4; transform: translate(0, 0) scale(0.8); }} '
        f'{P(t_imp + 0.9)} {{ opacity: 0; transform: translate(var(--dx), -5px) scale(1.7); }} 100% {{ opacity: 0; }} }}',
        f'.play .burst {{ animation: burst {D}s ease-out 1; }}']
# only the snow spray waits for the descent; the pose flipbook runs from the start, hidden
ski_svg = re.sub(r'(class="flake" style="[^"]*?animation-delay: )-([0-9.]+)s',
                 lambda m: f'{m.group(1)}{T_CLIMB - float(m.group(2)):.3f}s', skier(st))
groove = [route[j] for j in range(len(route)) if S_IMP <= racc[j] <= S_STOP]
glen = cum(groove)[-1]
groove_d = 'M' + ' L'.join(f'{x:.1f} {y + 1:.1f}' for x, y in groove)
ftrk = [p for p in fpts if 800 <= p[0] <= 838]
skin = ' '.join(f'M{ftrk[0][0]:.1f} {ftrk[0][1] + d:.1f} ' + ' '.join(f'L{x:.1f} {y + d:.1f}' for x, y in ftrk[1:]) for d in (-0.3, 1.2))
bursts = ''.join(f'<circle class="burst" style="--dx: {dx}px" cx="{_ix + cx:.1f}" cy="-1.2" r="{r}" fill="{INK}"></circle>'
                 for cx, dx, r in ((-4, -7, 1.6), (-1, -2, 2), (2, 3, 1.8), (5, 6, 1.4)))
lost_svg = ''.join(
    f'<g{" opacity=" + chr(34) + str(st["far"]) + chr(34) if name == "lski-b" else ""}>'
    f'<path class="lski {name[-1]}" d="{ski_d((-hl, 0, hl, 0, w))}" stroke-width="{w:.1f}" opacity="0"></path></g>'
    for name, (hl, w, _) in reversed(list(lost.items())))
marks.append(f'''<g class="fig tour-fig" data-play="{D}" data-once="tour">
    <g transform="translate({FX:.1f} {FY:.1f}) rotate({FA:.1f}) scale(-{SKI_SCALE} {SKI_SCALE})" opacity="0.85">{ns['wrap'](lost_svg)}</g>
    <g transform="translate({IX:.1f} {IY:.1f}) rotate({IA:.1f})">{bursts}</g>
    <g class="tour-run">
      <g class="morph"><g transform="scale(-{SKI_SCALE} {SKI_SCALE})" opacity="0.85">{morph_frames(st)}</g></g>
      <g class="tour-part"><g transform="scale(-{SKI_SCALE} {SKI_SCALE})" opacity="0.85">{hit(-20, -40, 42, 44)}{tourer(st)}</g></g>
      <g class="ski-part"><g transform="scale(-{SKI_SCALE} {SKI_SCALE})" opacity="0.85">{ski_svg}</g></g>
      <g class="crash"><g transform="scale(-{SKI_SCALE} {SKI_SCALE})" opacity="0.85">{crash_frames(st)}</g></g>
    </g>
  </g>''')


def climber_block(name, spire, anchor, rope_len, climb, place, mirror):
    """A spire, a top rope from anchor down to the harness, and a climber that goes up and is lowered."""
    sx = -0.5 if mirror else 0.5
    ratio = (rope_len - climb) / rope_len
    css.extend([
        f'@keyframes {name}-up {{ 0% {{ transform: translate(0, 0); }} 70% {{ transform: translate(0, -{climb}px); }} '
        f'100% {{ transform: translate(0, 0); }} }}',
        f'@keyframes {name}-rope {{ 0% {{ transform: scaleY(1); }} 70% {{ transform: scaleY({ratio:.3f}); }} '
        f'100% {{ transform: scaleY(1); }} }}',
        f'.play .{name}-up {{ animation: {name}-up 10s ease-in-out 1; }}',
        f'.{name}-rope {{ transform-box: view-box; transform-origin: {anchor[0]}px {anchor[1]}px; }}',
        f'.play .{name}-rope {{ animation: {name}-rope 10s ease-in-out 1; }}',
    ])
    return f'''<g class="fig" data-play="10">
    <path d="{spire}" fill="{INK}" opacity="0.13"></path>
    <line class="{name}-rope" x1="{anchor[0]}" y1="{anchor[1]}" x2="{anchor[0]}" y2="{anchor[1] + rope_len}" stroke="{INK}" stroke-width="0.9" opacity="0.7"></line>
    <circle cx="{anchor[0]}" cy="{anchor[1]}" r="1.4" fill="{INK}" opacity="0.8"></circle>
    <g class="{name}-up"><g transform="translate({place[0]} {place[1]}) scale({sx} 0.5)" opacity="0.85">{hit(-20, -62, 36, 70)}{climber(st)}</g></g>
  </g>'''




FLIP = '''
.flip .f { visibility: hidden; }
.flip .f0 { visibility: visible; }
.play .cyc .f { animation: flip8 0.9s step-end infinite; }
.play .hik .f { animation: flip10 1.1s step-end infinite; }
.play .clm .f { animation: flip8 2.4s step-end infinite; }
.play .ski .f { animation: flipski SKI_Ps step-end infinite; }
.play .tour .f { animation: fliptour TOUR_Ps step-end infinite; }
@keyframes flipski { 0% { visibility: visible; } SKI_PCT%, 100% { visibility: hidden; } }
@keyframes fliptour { 0% { visibility: visible; } TOUR_PCT%, 100% { visibility: hidden; } }
/* each frame stays up a hair longer than its slot (~3 ms), so rounded start offsets never leave a gap */
@keyframes flip8 { 0% { visibility: visible; } 12.85%, 100% { visibility: hidden; } }
@keyframes flip10 { 0% { visibility: visible; } 10.3%, 100% { visibility: hidden; } }
.spin { transform-box: fill-box; transform-origin: center; }
.play .spin { animation: spin 0.9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.play .spin.fast { animation-duration: 0.22s; }
.bob { transform-box: fill-box; }
.play .bob { animation: bob 0.3s ease-in-out infinite alternate; }
@keyframes bob { from { transform: translate(0, 0); } to { transform: translate(0, -0.7px); } }
.puff { transform-box: fill-box; transform-origin: center; }
.play .puff { animation: puff 1.2s linear infinite; }
@keyframes puff { 0% { transform: translate(0, 0) scale(0.5); opacity: 0.4; } 100% { transform: translate(-16px, -7px) scale(2); opacity: 0; } }
/* the camp fire burns and smokes all the time, not only on hover */
.flame { transform-box: fill-box; transform-origin: 50% 100%; }
@keyframes flick { from { transform: scale(1, 1) skewX(0deg); } to { transform: scale(0.86, 1.16) skewX(-5deg); } }
.smoke { transform-box: fill-box; transform-origin: center; }
@media (prefers-reduced-motion: no-preference) {
  .flame { animation: flick 0.45s ease-in-out infinite alternate; }
  .smoke { animation: smoke 4.2s linear infinite; }
}
/* rises steeply so it clears the hiker's face */
@keyframes smoke { 0% { transform: translate(0, 0) scale(0.5); opacity: 0.45; } 100% { transform: translate(8px, -48px) scale(2.1); opacity: 0; } }
.fig { pointer-events: auto; }
'''

astro = f'''---
// Scene figures in the fine-ink-line style (Round 12, style A). Generated from the pose
// script; each figure stands still and plays its animation once when hovered.
// Lives inside SceneFigures' <svg> (1440x810 scene units, above the title); the hover script is
// in SceneFigures, because a module script inside <svg> does not run.
---

<g class="figures">
  {chr(10).join('  ' + m for m in marks)}
</g>

<style>
{FLIP.replace('SKI_PCT', f'{100 / SKI_N + 0.3 / SKI_P:.2f}').replace('TOUR_PCT', f'{100 / TOUR_N + 0.3 / TOUR_P:.2f}')
     .replace('SKI_P', f'{SKI_P}').replace('TOUR_P', f'{TOUR_P}')}
{chr(10).join(css)}
</style>

'''
open(sys.argv[1], 'w', encoding='utf-8').write(astro)
print('wrote', sys.argv[1], len(astro))
