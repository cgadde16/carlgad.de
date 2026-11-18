"""Ducati Panigale V4 in the site's ink style, with an upright rider (canvas Round 16, rider draft 4).

The outline was traced roughly from a side photo (Matti Blume, Wikimedia Commons, CC BY-SA 4.0,
"Ducati Panigale V4 - Tuning World Bodensee 2018"). Points are in the 0.6-scale photo (px) and are
mapped to units of ~23 mm by the real wheelbase (1469 mm). Facing right, ground at y = 0, centred
between the axles. Wheels spin (class "spin fast"), body and rider bob, the exhaust puffs.

    panigale_svg(paper, ink) -> SVG markup (strokes and fills set inside; no outer style needed)
"""
import math

ENGINE, METAL = '#5d646a', '#b8bdc2'
VISOR = '#8b9097'

# photo reference (0.6-scale image): axles, tyre radii, real wheelbase
_R, _F, _RR, _RF, _WB_MM = (210, 478), (935, 510), 161, 145, 1469
_K = _WB_MM / 23 / math.dist(_R, _F)                  # units per photo px
RR, RF = _RR * _K, _RF * _K                            # tyre radii in units (~14.2, ~12.8)
_GROUND = _F[1] + _RF
_MID = (_R[0] + _F[0]) / 2
_TILT = (_F[1] - _R[1]) + (_RF - _RR)                  # the photo's rear wheel stands on a paddock stand


_W = [1.0]                                             # line-weight factor, set per drawing


def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def sw_(v):
    return f(v * _W[0])


def P(x, y):
    t = (_F[0] - x) / (_F[0] - _R[0])
    return ((x - _MID) * _K, (y + _TILT * t - _GROUND) * _K)


def pts(lst):
    return [P(*p) for p in lst]


def rpath(points, rad=0.0):
    """Closed path through points, corners rounded by rad (scalar or per point)."""
    n = len(points)
    rad = rad if isinstance(rad, (list, tuple)) else [rad] * n
    s = ''
    for i, p in enumerate(points):
        r = rad[i]
        lead = 'M' if i == 0 else ' L'
        if not r:
            s += f'{lead}{f(p[0])} {f(p[1])}'
            continue
        a, b = points[i - 1], points[(i + 1) % n]
        ta, tb = min(r / math.dist(p, a), 0.5), min(r / math.dist(p, b), 0.5)
        pa = (p[0] + (a[0] - p[0]) * ta, p[1] + (a[1] - p[1]) * ta)
        pb = (p[0] + (b[0] - p[0]) * tb, p[1] + (b[1] - p[1]) * tb)
        s += f'{lead}{f(pa[0])} {f(pa[1])} Q{f(p[0])} {f(p[1])} {f(pb[0])} {f(pb[1])}'
    return s + ' Z'


def path(d, fill, sw, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke-width="{sw_(sw)}"{extra}></path>'


def ln(points, sw, extra=''):
    return f'<path d="M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in points) + f'" fill="none" stroke-width="{sw_(sw)}"{extra}></path>'


def circ(c, r, fill='none', sw=1.0, extra=''):
    return f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" fill="{fill}" stroke-width="{sw_(sw)}"{extra}></circle>'


def arc_pts(c, r, a0, a1, n=8):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def ik(a, b, l1, l2, bend=1):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    d = min(L, l1 + l2 - 0.01)
    x = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - x * x))
    ux, uy = dx / L, dy / L
    return (a[0] + ux * x - bend * uy * h, a[1] + uy * x + bend * ux * h)


def wheel(c, r, spokes, ink, paper, single=False):
    o = [circ(c, r, sw=3.0), circ(c, r - 3.2, sw=0.7)]
    sp = ''.join(ln([(c[0] + 2 * math.cos(a), c[1] + 2 * math.sin(a)),
                     (c[0] + (r - 3.6) * math.cos(a + d), c[1] + (r - 3.6) * math.sin(a + d))], 0.9)
                 for k in range(spokes) for a in (2 * math.pi * k / spokes,) for d in (-0.12, 0.12))
    hidden = circ(c, r - 3.6, 'none', 0, ' stroke="none"')   # keeps the spin box centred on the axle
    o.append(f'<g class="spin fast">{hidden}{sp}</g>')
    o.append(circ(c, 3.4, paper, 1.2) + circ(c, 1.2, ink, 0) if single else circ(c, 1.8, ink, 0))
    return ''.join(o)


def helmet(hc, ink, paper, k=1.25):
    def H(p):
        return (hc[0] + p[0] * k, hc[1] + p[1] * k)
    shell = [H((-4.6, 2.6))] + [H((5 * math.cos(math.radians(a)), 5 * math.sin(math.radians(a))))
                                 for a in range(160, 356, 19)] + [H((5.6, 1.2)), H((5.0, 3.6)), H((1.0, 4.6))]
    visor = [H(p) for p in ((0.6, -1.9), (4.4, -2.2), (5.4, -0.2), (1.2, 0.4))]
    spoiler = [H(p) for p in ((-3.0, -4.1), (-5.5, -2.9), (-4.9, -2.0))]      # small, low lip (not a peak)
    return (path(rpath(shell, 0), ink, 0.6) + path(rpath(visor, 0), VISOR, 0) + path(rpath(spoiler, 0.5), ink, 0.6))


def rider(ink, paper, angle=52, look=(1, -0.55), lw=2.6, tw=5.8):
    """Upright cruise: back at ~52 deg, arms almost straight, head up."""
    hip, hand, peg = P(452, 212), P(830, 212), P(410, 415)
    tl = 22
    a = math.radians(-angle)
    sh = (hip[0] + tl * math.cos(a), hip[1] + tl * math.sin(a))
    arm = max(13, math.dist(sh, hand) / 2 / 0.985)
    knee = ik(hip, peg, 18.5, 18.5, bend=-1)
    elbow = ik(sh, hand, arm, arm, bend=1)
    n = math.hypot(*look)
    hc = (sh[0] + 8 * look[0] / n, sh[1] + 8 * look[1] / n)
    halo = f' stroke="{paper}"'
    leg, boot, arm_pts = [hip, knee, peg], [(peg[0] - 3.4, peg[1] + 0.3), (peg[0] + 4.2, peg[1] + 0.9)], [sh, elbow, hand]
    far = f'<g opacity="0.55">{ln([sh, (elbow[0] - 1.5, elbow[1]), (hand[0] - 1.5, hand[1])], lw)}</g>'
    under = ln(leg, lw * 1.2 + 2, halo) + ln(boot, lw * 1.15 + 2, halo) + ln([hip, sh], tw + 1.8, halo) + ln(arm_pts, lw + 1.8, halo)
    return (far + under + ln([hip, sh], tw) + ln([sh, (hc[0] - 0.8, hc[1] + 2.6)], max(lw, tw * 0.55)) + helmet(hc, ink, paper)
            + ln(leg, lw * 1.2) + ln(boot, lw * 1.15) + ln(arm_pts, lw))


def panigale_svg(paper, ink, uid='pani', weight=1.0, wheels='mixed', rider_lw=2.6, rider_tw=5.8):
    """weight scales every line; wheels: 'mixed' (real sizes, hub nut only at the back),
    'front' (both wheels like the front one) or 'rear' (both like the rear one, hub nut on both)."""
    _W[0] = weight
    rr, rf = {'mixed': (RR, RF), 'front': (RF, RF), 'rear': (RR, RR)}[wheels]
    nut_r, nut_f = wheels in ('mixed', 'rear'), wheels == 'rear'
    R, F = (P(*_R)[0], -rr), (P(*_F)[0], -rf)
    smoke = ' fill-opacity="0.2"'
    wheel_parts = [wheel(R, rr, 5, ink, paper, single=nut_r), wheel(F, rf, 5, ink, paper, single=nut_f)]
    if wheels == 'mixed':
        wheel_parts.append(circ(F, rf * 0.55, sw=0.8))                     # front brake disc (identical wheels: none)
    o = []
    o.append(path(rpath(pts([(372, 318), (425, 372), (232, 505), (192, 455)]), 2.5), paper, 1.3))     # single-sided swingarm
    if nut_r:
        o.append(circ(R, 3.4, paper, 1.2) + circ(R, 1.2, ink, 0))
    top = P(842, 205)
    mid = (F[0] + (top[0] - F[0]) * 0.55, F[1] + (top[1] - F[1]) * 0.55)
    o.append(ln([mid, top], 3.6) + ln([F, mid], 2.0))                                              # fork
    o.append(ln(arc_pts(F, rf + 2, 205, 300), 1.8))                                                # front fender
    tail = rpath(pts([(195, 121), (296, 137), (342, 203), (442, 258), (446, 290), (372, 254), (206, 138)]),
                 [0.4, 2, 3, 2, 1, 3, 0.4])
    side = rpath(pts([(776, 198), (962, 243), (1001, 298), (1006, 324), (990, 346), (935, 356), (832, 368),
                      (786, 420), (779, 560), (700, 505), (612, 470), (586, 400), (600, 326), (650, 291), (770, 266)]),
                 [1, 3, 2, 1, 2, 2, 3, 3, 1, 3, 2, 3, 3, 2, 1])
    belly = rpath(pts([(447, 470), (560, 456), (640, 470), (776, 505), (763, 592), (640, 593), (560, 562), (472, 507)]),
                  [2, 3, 2, 1, 2, 2, 3, 2])
    parts = [
        path(rpath(pts([(358, 298), (562, 286), (602, 326), (586, 400), (612, 470), (447, 472), (386, 500), (358, 420)]), 3),
             ENGINE, 1.0),
        circ(P(570, 462), 2.4, 'none', 0.7, ' stroke="#9aa1a7"'),
        path(tail, paper, 1.4),
        path(rpath(pts([(296, 140), (344, 205), (462, 232), (506, 240), (500, 253), (440, 262), (340, 216)]), 1.5), ink, 0.6),
        path(rpath(pts([(500, 242), (516, 194), (582, 162), (690, 159), (766, 190), (776, 262), (650, 276), (560, 289)]),
                   [1, 4, 4, 3, 2, 1, 2, 2]), paper, 1.4),
        path(belly, paper, 1.4),
        path(rpath(pts([(386, 500), (470, 494), (592, 560), (586, 583), (400, 541)]), 2), METAL, 1.1),
        path(side, paper, 1.5),
        path(rpath(pts([(790, 192), (806, 140), (880, 103), (916, 140), (963, 243)]), [1, 3, 3, 2, 1]), ink, 1.0, smoke),
        path(rpath(pts([(1006, 324), (990, 304), (972, 296), (994, 344)]), 0.5), ink, 0),
        ln(pts([(968, 280), (1000, 300)]), 1.3),
        ln(pts([(800, 300), (930, 330)]), 0.8),
    ]
    cf, cr = rf + 2.0, rr + 1.6
    defs = (f'<defs><mask id="m{uid}" maskUnits="userSpaceOnUse" x="-90" y="-120" width="180" height="150">'
            f'<rect x="-90" y="-120" width="180" height="150" fill="#fff" stroke="none"></rect>'
            f'{circ(F, cf, "#000", 0)}{circ(R, cr, "#000", 0)}</mask>'
            f'<clipPath id="c{uid}"><path d="{tail} {side} {belly}"></path></clipPath></defs>')
    o.append(f'<g mask="url(#m{uid})">{"".join(parts)}</g>')
    o.append(f'<g clip-path="url(#c{uid})">{circ(F, cf, "none", 1.5)}{circ(R, cr, "none", 1.4)}</g>')
    o.append(rider(ink, paper, lw=rider_lw, tw=rider_tw))
    ex = P(393, 522)                                                                               # exhaust outlet
    puffs = ''.join(f'<circle class="puff" style="animation-delay: -{i * 0.3:.1f}s" cx="{f(ex[0] - 1)}" cy="{f(ex[1])}" '
                    f'r="2" fill="{ink}" stroke="none" opacity="0"></circle>' for i in range(3))
    return (f'<g fill="none" stroke="{ink}" stroke-linecap="round" stroke-linejoin="round">{defs}{puffs}'
            f'{"".join(wheel_parts)}<g class="bob">{"".join(o)}</g></g>')


def extent():
    """(xmin, ymin, xmax) of the drawing in units, for the hit box."""
    R, F = P(*_R)[0], P(*_F)[0]
    return R - RR - 1.5, -80, F + RF + 1.5
