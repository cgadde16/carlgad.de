"""Generate Round 12 figure artboards (three styles: sheet + scene each) for the design canvas.

Figures are skeletons posed with two-bone IK; animation is CSS only (flipbook frames,
transforms), so it works in the canvas runtime without scripts.
Usage: python3 -I figgen.py <base V0 dc.html> <out project dir> [--preview <html>]
"""
import math
import re
import sys

INK = '#14171A'
PAPER = '#F4F5F2'

STYLES = {
    'A': dict(key='A', name='Fine ink line', lw=1.7, tw=2.3, hr=4.0, neck=1.6, wheel=1.5, solid=False, detail=True,
              far=0.5,
              blurb='Thin ink strokes with small details (spokes, helmet, backpack straps, guy lines). '
                    'Matches the birds and the outlined signs; the quietest option.'),
    'B': dict(key='B', name='Solid silhouette', lw=3.6, tw=6.6, hr=4.7, neck=0.4, wheel=2.8, solid=True, detail=True,
              far=0.42,
              blurb='Filled ink shapes, far limbs paler, read as shadows in the mist. '
                    'Strongest at small sizes; closest to the mood of the reference site.'),
    'C': dict(key='C', name='Trail-map pictogram', lw=5.0, tw=6.4, hr=4.8, neck=3.0, wheel=3.4, solid=True,
              detail=False, far=0.4,
              blurb='Bold rounded limbs and a floating head, like the symbols on a trail map or a hut sign. '
                    'Fits the signpost theme; playful and very legible.'),
}


def f(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s


def pt(p):
    return f'{f(p[0])} {f(p[1])}'


def line(*pts):
    return 'M' + ' L'.join(pt(p) for p in pts)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def ik(h, t, a, b, key):
    """Joint between h and t for bone lengths a, b; of the two solutions pick the one maximising key(joint)."""
    dx, dy = t[0] - h[0], t[1] - h[1]
    d = max(abs(a - b) + 0.01, min(math.hypot(dx, dy), a + b - 0.01))
    base = math.atan2(dy, dx)
    al = math.acos((a * a + d * d - b * b) / (2 * a * d))
    c = [(h[0] + a * math.cos(base + s * al), h[1] + a * math.sin(base + s * al)) for s in (1, -1)]
    return max(c, key=key)


def path(d, w, extra=''):
    return f'<path d="{d}" stroke-width="{f(w)}"{extra}></path>'


def head(st, shoulder, direction):
    ux, uy = direction
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    c = (shoulder[0] + ux * (st['neck'] + st['hr'] + st['tw'] / 2), shoulder[1] + uy * (st['neck'] + st['hr'] + st['tw'] / 2))
    return c, f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(st["hr"])}" fill="{INK}" stroke="none"></circle>'


def far(st, inner):
    return f'<g opacity="{st["far"]}">{inner}</g>'


def flip(cls, frames, period):
    n = len(frames)
    out = [f'<g class="{cls}">']
    for k, fr in enumerate(frames):
        delay = ((n - k) % n) * period / n
        c = 'f f0' if k == 0 else 'f'
        out.append(f'<g class="{c}" style="animation-delay: -{delay:.3f}s">{fr}</g>')
    out.append('</g>')
    return ''.join(out)


def wrap(inner):
    return (f'<g fill="none" stroke="{INK}" stroke-linecap="round" stroke-linejoin="round">{inner}</g>')


# ── Cyclist ────────────────────────────────────────────────────────────────
def cyclist(st, frames=8):
    R, F, BB = (-23, -13), (23, -13), (-3, -12)
    S, Ht, Hb = (-10, -36), (15, -34), (17, -28)
    hip, sh = (-10, -39.5), (8, -50)
    hand = (21, -32)
    lw, w = st['lw'], st['wheel']
    static = []
    # wheels
    for c in (R, F):
        static.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="13" stroke-width="{f(w)}"></circle>')
        if st['detail']:
            sp = ''.join(path(line((c[0] + 12 * math.cos(a), c[1] + 12 * math.sin(a)),
                                   (c[0] - 12 * math.cos(a), c[1] - 12 * math.sin(a))), 0.8)
                         for a in (0, math.pi / 3, 2 * math.pi / 3))
            static.append(f'<g class="spin" opacity="0.7">{sp}</g>')
        else:
            static.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="1.6" fill="{INK}" stroke="none"></circle>')
    fw = 1.6 if not st['solid'] else (2.4 if st['detail'] else 3.0)
    static.append(path(line(R, BB, S, R), fw))
    static.append(path(line(S, Ht, Hb, BB), fw))
    static.append(path(line(Hb, F), fw))
    static.append(path(line(Ht, (20, -36), (22, -31), (19.5, -29.5)), fw))
    static.append(path(line((-14, -37), (-6, -37)), fw + 0.6))  # saddle
    # rider upper body
    elbow = ik(sh, hand, 11, 11, key=lambda p: p[1])
    static.append(far(st, path(line(sh, add(elbow, (-1.5, -0.6)), add(hand, (-1.5, 0))), lw)))
    static.append(path(line(hip, sh), st['tw']))
    static.append(path(line(sh, elbow, hand), lw))
    hc, hd = head(st, sh, (0.75, -0.66))
    static.append(hd)
    if st['detail']:
        # helmet shell and visor
        static.append(path(f'M{pt(add(hc, (-st["hr"] - 0.8, 0.6)))} A{f(st["hr"] + 1)} {f(st["hr"] + 1)} 0 0 1 '
                           f'{pt(add(hc, (st["hr"] + 1.4, 0.4)))}', 1.3 if not st['solid'] else 2.0))
    frs = []
    for k in range(frames):
        th = 2 * math.pi * k / frames
        out = []
        for side, op in ((1, None), (-1, st['far'])):
            a = th if side == 1 else th + math.pi
            foot = (BB[0] + 6 * math.cos(a), BB[1] + 6 * math.sin(a))
            knee = ik(hip, foot, 18, 18, key=lambda p: p[0])
            leg = path(line(hip, knee, foot), lw) + path(line(BB, foot), 1.4) + \
                path(line(add(foot, (-2.5, 0)), add(foot, (3.5, 0))), lw)
            out.append(far(st, leg) if op else leg)
        frs.append(''.join(reversed(out)))
    return wrap(''.join(static[:-0] if False else static) + flip('flip cyc', frs, 0.9))


# ── Hiker ──────────────────────────────────────────────────────────────────
def hiker(st, frames=10):
    lw = st['lw']
    frs = []
    for k in range(frames):
        p = k / frames
        bob = -0.9 * math.cos(4 * math.pi * p)
        hip = (0, -29 + bob)
        sh = (3.5, -48 + bob)
        parts = []

        def foot(q):
            q %= 1
            if q < 0.6:
                return (10 - 20 * q / 0.6, 0)
            r = (q - 0.6) / 0.4
            return (-10 + 20 * r, -6 * math.sin(math.pi * r))

        def arm(q, opacity):
            fwd = math.cos(2 * math.pi * q)
            hand = (sh[0] - 1 - 7 * fwd, sh[1] + 15)
            el = ik(sh, hand, 9.5, 9, key=lambda pp: -pp[0])
            g = path(line(sh, el, hand), lw)
            # trekking pole, planted a little ahead of the hand
            g += path(line(add(hand, (0, -2)), (hand[0] + 6, 0.5)), 1.1 if not st['solid'] else 1.6)
            return far(st, g) if opacity else g

        for q, is_far in ((p + 0.5, True), (p, False)):
            ft = foot(q)
            kn = ik(hip, ft, 15, 15, key=lambda pp: pp[0])
            leg = path(line(hip, kn, ft), lw) + path(line(add(ft, (-1.5, 0)), add(ft, (3.5, 0))), lw)
            parts.append(far(st, leg) if is_far else leg)
        parts.insert(0, arm(p, True))
        # backpack behind the torso
        if st['key'] == 'C':
            parts.append(f'<rect x="{f(sh[0] - 11)}" y="{f(sh[1] - 1)}" width="7" height="15" rx="3" '
                         f'fill="{INK}" stroke="none"></rect>')
        elif st['solid']:
            parts.append(f'<rect x="{f(sh[0] - 10.5)}" y="{f(sh[1] - 2)}" width="7.5" height="16" rx="2" '
                         f'fill="{INK}" stroke="none" transform="rotate(6 {f(sh[0] - 6)} {f(sh[1] + 6)})"></rect>')
        else:
            parts.append(f'<rect x="{f(sh[0] - 10.5)}" y="{f(sh[1] - 2)}" width="7.5" height="16" rx="2" '
                         f'fill="{PAPER}" stroke-width="1.3" transform="rotate(6 {f(sh[0] - 6)} {f(sh[1] + 6)})"></rect>')
            parts.append(path(line((sh[0] - 4, sh[1] + 1), (sh[0] - 1, sh[1] + 9)), 0.9))
        parts.append(path(line(hip, sh), st['tw']))
        hc, hd = head(st, sh, (0.25, -1))
        parts.append(hd)
        if st['detail']:
            brim = 1.2 if not st['solid'] else 1.8
            parts.append(path(line(add(hc, (-st['hr'] - 2, -st['hr'] + 1.2)), add(hc, (st['hr'] + 3, -st['hr'] + 1.6))), brim))
            parts.append(f'<path d="M{pt(add(hc, (-st["hr"] + 0.5, -st["hr"] + 1.2)))} q{f(st["hr"] - 0.5)} '
                         f'-{f(st["hr"] + 0.4)} {f(2 * st["hr"] - 0.5)} 0.2" fill="{INK}" stroke="none"></path>')
        parts.append(arm(p + 0.5, False))
        frs.append(''.join(parts))
    return wrap(flip('flip hik', frs, 1.1))


# ── Climber ────────────────────────────────────────────────────────────────
def climber(st, frames=8, rope_to=None):
    """Facing a wall on the left at x = -12. rope_to: anchor point for a static rope (sheet)."""
    lw = st['lw']
    A = dict(hip=(3, -22), sh=(0, -40), hn=(-12, -52), hf=(-12, -39), fn=(-12, -12), ff=(-12, -2))
    B = dict(hip=(3, -25), sh=(0, -43), hn=(-12, -40), hf=(-12, -55), fn=(-12, -3), ff=(-12, -15))
    frs = []
    for k in range(frames):
        t = (1 - math.cos(2 * math.pi * k / frames)) / 2
        P = {n: (A[n][0] + (B[n][0] - A[n][0]) * t, A[n][1] + (B[n][1] - A[n][1]) * t) for n in A}
        parts = []
        # far limbs first
        e = ik(P['sh'], P['hf'], 9.5, 9.5, key=lambda q: q[1])
        kn = ik(P['hip'], P['ff'], 12, 12, key=lambda q: q[0])
        parts.append(far(st, path(line(P['sh'], e, P['hf']), lw) + path(line(P['hip'], kn, P['ff']), lw)))
        parts.append(path(line(P['hip'], P['sh']), st['tw']))
        hc, hd = head(st, P['sh'], (-0.45, -1))
        parts.append(hd)
        if st['detail']:
            parts.append(path(f'M{pt(add(hc, (-st["hr"] - 0.6, 0.8)))} A{f(st["hr"] + 1)} {f(st["hr"] + 1)} 0 0 1 '
                              f'{pt(add(hc, (st["hr"] + 0.8, 0.8)))}', 1.3 if not st['solid'] else 2.0))
            parts.append(f'<circle cx="{f(P["hip"][0] + 1.5)}" cy="{f(P["hip"][1] + 1)}" r="1.6" stroke-width="1"></circle>')
        e = ik(P['sh'], P['hn'], 9.5, 9.5, key=lambda q: q[1])
        kn = ik(P['hip'], P['fn'], 12, 12, key=lambda q: q[0])
        parts.append(path(line(P['sh'], e, P['hn']), lw) + path(line(P['hip'], kn, P['fn']), lw))
        if rope_to:
            parts.insert(0, path(f'M{pt(P["hip"])} Q{f(P["hip"][0] + 3)} {f((P["hip"][1] + rope_to[1]) / 2)} {pt(rope_to)}', 0.9))
        frs.append(''.join(parts))
    return wrap(flip('flip clm', frs, 2.4))


def wall(top=-95, bottom=8, solid=False):
    d = (f'M-12 {bottom} L-13 -20 L-11.5 -38 L-13.5 -60 L-12 -78 L-14 {top} L-40 {top} L-40 {bottom} Z')
    return f'<path d="{d}" fill="{INK}" opacity="{0.16 if not solid else 0.22}" stroke="none"></path>'


# ── Camp ───────────────────────────────────────────────────────────────────
def camp(st, sitter=True):
    """Tent and fire; sitter=False leaves out the man on the log (the site seats its own hiker there)."""
    lw = st['lw']
    out = []
    # tent
    if st['solid']:
        out.append(f'<path d="M-24 0 L-5 -23 L14 0 Z" fill="{INK}" stroke="none"></path>')
        out.append(f'<path d="M-5 -23 L-1 0 L-9 0 Z" fill="{PAPER}" stroke="none" opacity="0.85"></path>')
        if st['detail']:
            out.append(path(line((-5, -23), (-7, -27)), 1.4) + path(line((-5, -23), (-3, -27)), 1.4))
    else:
        out.append(f'<path d="M-24 0 L-5 -23 L14 0 Z" fill="{PAPER}" stroke-width="1.6"></path>')
        out.append(path(line((-5, -23), (-5, 0)), 1.2) + path(line((-5, -9), (1, 0)), 1.2))
        out.append(path(line((-5, -23), (-7.5, -27)), 1.2) + path(line((-5, -23), (-2.5, -27)), 1.2))
        out.append(path(line((-24, 0), (-30, 1)), 0.9) + path(line((14, 0), (20, 1)), 0.9))
    # fire: logs, flame, smoke
    fx = 27
    out.append(path(line((fx - 6, 0.5), (fx + 6, -2)), lw) + path(line((fx - 6, -2), (fx + 6, 0.5)), lw))
    out.append(f'<path class="flame" d="M{fx} -14 C{fx + 4} -9 {fx + 5} -5 {fx + 2.5} -2 C{fx + 1} -0.5 {fx - 1} -0.5 '
               f'{fx - 2.5} -2 C{fx - 5} -5 {fx - 2} -9 {fx} -14 Z" fill="{INK if st["solid"] else PAPER}" '
               f'stroke-width="{1.4 if not st["solid"] else 0}"></path>')
    for i in range(3):
        out.append(f'<circle class="smoke" style="animation-delay: -{i * 1.4:.1f}s" cx="{fx}" cy="-17" r="2.6" '
                   f'fill="{INK}" stroke="none" opacity="0"></circle>')
    if not sitter:
        return wrap(''.join(out))
    # sitter on a log, facing the fire
    log = path(line((38, -2.5), (52, -2.5)), 4.5 if st['solid'] else 3.2)
    hip, sh = (45, -8), (43, -25)
    kn, ft = (36, -12), (35.5, 0)
    hand = (34.5, -15)
    out.append(log)
    e_far = ik(sh, add(hand, (1.5, -1)), 8.5, 8.5, key=lambda q: q[1])
    out.append(far(st, path(line(sh, e_far, add(hand, (1.5, -1))), lw) + path(line(hip, add(kn, (1.5, -0.5)), add(ft, (2.5, 0))), lw)))
    out.append(path(line(hip, sh), st['tw']))
    hc, hd = head(st, sh, (-0.35, -1))
    out.append(hd)
    if st['detail']:
        out.append(f'<path d="M{pt(add(hc, (-st["hr"], -0.5)))} a{f(st["hr"])} {f(st["hr"])} 0 0 1 {f(2 * st["hr"])} 0 '
                   f'l1 1.4 l-{f(2 * st["hr"] + 2)} 0 z" fill="{INK}" stroke="none"></path>')  # beanie
    out.append(path(line(hip, kn, ft), lw) + path(line(add(ft, (-3.5, 0)), add(ft, (1, 0))), lw))
    e = ik(sh, hand, 8.5, 8.5, key=lambda q: q[1])
    out.append(path(line(sh, e, hand), lw))
    return wrap(''.join(out))


# ── CSS shared by sheets and scenes ─────────────────────────────────────────
CSS = """
.flip .f{visibility:hidden}
.flip .f0{visibility:visible}
.cyc .f{animation:flip8 0.9s step-end infinite}
.hik .f{animation:flip10 1.1s step-end infinite}
.clm .f{animation:flip8 2.4s step-end infinite}
@keyframes flip8{0%{visibility:visible}12.5%,100%{visibility:hidden}}
@keyframes flip10{0%{visibility:visible}10%,100%{visibility:hidden}}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 0.9s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.flame{transform-box:fill-box;transform-origin:50% 100%;animation:flick 0.45s ease-in-out infinite alternate}
@keyframes flick{from{transform:scale(1,1) skewX(0deg)}to{transform:scale(0.86,1.16) skewX(-5deg)}}
.smoke{transform-box:fill-box;transform-origin:center;animation:smoke 4.2s linear infinite}
@keyframes smoke{0%{transform:translate(0,0) scale(0.5);opacity:0.45}100%{transform:translate(16px,-46px) scale(2.1);opacity:0}}
"""

REDUCED = """
@media (prefers-reduced-motion: reduce){
.flip .f,.spin,.flame,.smoke,.ride,.walk,.ascend,.rope{animation:none}
.smoke{opacity:0.25}
}
"""


# ── Paths in the scene ──────────────────────────────────────────────────────
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def sample(segs, n=400):
    pts = []
    for s in segs:
        for i in range(n):
            pts.append(bez(*s, i / n))
    pts.append(segs[-1][3])
    return pts


def motion_keyframes(name, pts, count, fade=(4, 94), flipx=False, xmin=None, xmax=None):
    if xmin is not None:
        pts = [p for p in pts if xmin <= p[0] <= xmax]
    if flipx:
        pts = list(reversed(pts))
    # resample by arc length
    acc = [0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    L = acc[-1]
    out = []
    j = 0
    for i in range(count + 1):
        s = L * i / count
        while j < len(acc) - 2 and acc[j + 1] < s:
            j += 1
        p = pts[j]
        q = pts[min(j + 3, len(pts) - 1)] if j + 3 < len(pts) else pts[-1]
        r = pts[max(j - 3, 0)]
        ang = math.degrees(math.atan2(q[1] - r[1], q[0] - r[0]))
        if flipx:
            ang -= 180
        ang = max(-14, min(14, ((ang + 180) % 360) - 180))
        pct = 100 * i / count
        op = 1
        if pct < fade[0]:
            op = pct / fade[0]
        elif pct > fade[1]:
            op = max(0, (100 - pct) / (100 - fade[1]))
        out.append(f'{pct:.2f}%{{transform:translate({p[0]:.1f}px,{p[1]:.1f}px) rotate({ang:.1f}deg);opacity:{op:.2f}}}')
    return f'@keyframes {name}{{' + ''.join(out) + '}'


TRAIL = [((-20, 746), (160, 706), (300, 736), (420, 706)), ((420, 706), (520, 682), (470, 660), (580, 654))]
RIDGE2 = [((0, 600), (140, 560), (240, 590), (360, 540)), ((360, 540), (460, 500), (540, 560), (660, 530)),
          ((660, 530), (800, 495), (880, 560), (1000, 520)), ((1000, 520), (1120, 480), (1220, 540), (1440, 500))]


def scene_figures(st):
    k = st['key']
    css = [
        motion_keyframes(f'ride{k}', sample(TRAIL), 40),
        motion_keyframes(f'far{k}', sample(RIDGE2[:1]), 30, fade=(6, 90), xmin=40, xmax=360),
        motion_keyframes(f'walk{k}', sample(RIDGE2[2:]), 24, fade=(6, 86), flipx=True, xmin=962, xmax=1075),
        f'.ride{k}{{animation:ride{k} 42s linear infinite}}',
        f'.far{k}{{animation:far{k} 70s linear infinite;animation-delay:-38s}}',
        f'.walk{k}{{animation:walk{k} 46s linear infinite;animation-delay:-12s}}',
        # climber goes up 30 units in 26s, is lowered back in 5s
        f'@keyframes asc{k}{{0%{{transform:translate(0,0)}}84%{{transform:translate(0,-30px)}}100%{{transform:translate(0,0)}}}}',
        f'@keyframes rope{k}{{0%{{transform:scaleY(1)}}84%{{transform:scaleY({(58 - 30) / 58:.3f})}}100%{{transform:scaleY(1)}}}}',
        f'.ascend{k}{{animation:asc{k} 31s ease-in-out infinite}}',
        f'.rope{k}{{transform-box:view-box;transform-origin:1011.5px 325px;animation:rope{k} 31s ease-in-out infinite}}',
    ]
    spire = (f'<path d="M990 400 L999 364 L1000 346 L1004 328 L1019 323 L1027 347 L1037 377 L1047 400 Z" '
             f'fill="{INK}" opacity="{0.13 if not st["solid"] else 0.18}"></path>')
    # climber hip sits at local (-3,-22); place wall face at x=1167..1170
    climber_g = (f'<line class="rope rope{k}" x1="1011.5" y1="325" x2="1011.5" y2="383" stroke="{INK}" stroke-width="0.9" '
                 f'opacity="0.7"></line>'
                 f'<g class="ascend ascend{k}"><g transform="translate(1010 394) scale(0.5)" opacity="0.85">'
                 f'{climber(st)}</g></g>'
                 f'<circle cx="1011.5" cy="325" r="1.4" fill="{INK}" opacity="0.8"></circle>')
    figs = [
        spire,
        climber_g,
        f'<g transform="translate(931 535) scale(0.5)" opacity="0.85">{camp(st)}</g>',
        f'<g class="walk walk{k}"><g transform="scale(-0.5 0.5)" opacity="0.8">{hiker(st)}</g></g>',
        f'<g class="ride far{k}"><g transform="scale(0.36)" opacity="0.75">{cyclist(st)}</g></g>',
        f'<g class="ride ride{k}"><g transform="scale(0.95)" opacity="0.9">{cyclist(st)}</g></g>',
    ]
    return '\n    '.join(figs), '\n'.join(css)


# ── Artboards ───────────────────────────────────────────────────────────────
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
         '&amp;family=Inter:wght@400;500&amp;display=swap">')

CELLS = [
    ('Cyclist', '-42 -76 84 84', 'cyclist',
     'Rides the dotted trail in from the left and fades into the mist; wheels spin, legs pedal. '
     'A second, tiny one crosses the far ridge.'),
    ('Hiker', '-30 -70 64 76', 'hiker',
     'Walks along the ridge towards camp with trekking poles; a slight bob in every step.'),
    ('Climber', '-44 -100 70 110', 'climber',
     'Moves up the rock spire one reach at a time on a top rope, then is lowered back down.'),
    ('Camp', '-34 -54 92 60', 'camp',
     'Tent, a flickering campfire and someone warming their hands; smoke drifts right with the wind.'),
]


def figure_svg(st, kind):
    if kind == 'cyclist':
        return cyclist(st)
    if kind == 'hiker':
        return hiker(st)
    if kind == 'climber':
        return wall(solid=st['solid']) + climber(st, rope_to=(-14, -96)) + \
            f'<circle cx="-14" cy="-96" r="1.6" fill="{INK}"></circle>'
    return camp(st)


def sheet(st, title_prefix):
    cells = []
    for name, vb, kind, text in CELLS:
        vbx, vby, vbw, vbh = map(float, vb.split())
        ground = (f'<path d="M{f(vbx + 4)} 0.8 L{f(vbx + vbw - 4)} 0.8" stroke="{INK}" stroke-width="0.6" '
                  f'stroke-dasharray="1 3" opacity="0.5"></path>') if kind != 'climber' else ''
        cells.append(f'''<figure style="margin: 0; display: flex; flex-direction: column; gap: 14px">
      <div style="height: 330px; border: 1px solid #D9DBD6; border-radius: 4px; background: #FAFBF8; display: flex; align-items: center; justify-content: center">
        <svg role="img" aria-label="{name}, {st['name'].lower()} style" viewBox="{vb}" style="width: 100%; height: 300px">{ground}{figure_svg(st, kind)}</svg>
      </div>
      <figcaption style="display: flex; flex-direction: column; gap: 6px">
        <span style="font-family: 'Instrument Serif', Georgia, serif; font-size: 26px; line-height: 1">{name}</span>
        <span style="font-size: 14px; line-height: 1.45; color: #3C4248">{text}</span>
      </figcaption>
    </figure>''')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Figures, {st['name'].lower()}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
body{{margin:0}}
a{{color:#14171A}}a:hover{{color:#5A6066}}
{CSS}{REDUCED}
</style>
</helmet>
<div style="width: 1440px; height: 810px; box-sizing: border-box; padding: 56px 64px; background: #F4F5F2; color: #14171A; font-family: Inter, system-ui, sans-serif; display: flex; flex-direction: column; gap: 36px">
  <header style="display: flex; flex-direction: column; gap: 10px; max-width: 900px">
    <span style="font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: #3C4248">Round 12 · Figures · style {st['key']}</span>
    <h1 style="margin: 0; font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; font-size: 56px; line-height: 1">{title_prefix}{st['name']}</h1>
    <p style="margin: 0; font-size: 17px; line-height: 1.5; color: #3C4248">{st['blurb']}</p>
  </header>
  <div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 28px">
    {''.join(cells)}
  </div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1440,"height":810}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


OLD_FIGURES = ['M1118 344', 'translate(1184 392)', 'translate(928 535)', 'translate(968 529)',
               'translate(352 536)', 'translate(266 690)']


def scene(st, base):
    figs, css = scene_figures(st)
    lines = base.split('\n')
    kept = [ln for ln in lines if not any(m in ln for m in OLD_FIGURES)]
    src = '\n'.join(kept)
    assert src.count('</svg>') >= 1
    first = src.index('  </svg>')
    src = src[:first] + '    ' + figs + '\n' + src[first:]
    src = src.replace('a{color:#14171A}a:hover{color:#5A6066}',
                      'a{color:#14171A}a:hover{color:#5A6066}\n' + CSS + '\n' + css + '\n' + REDUCED, 1)
    src = re.sub(r'<title>.*?</title>', f'<title>Home with {st["name"].lower()} figures</title>', src, count=1)
    assert 'translate(266 690)' not in src
    return src


def main():
    base_path, out_dir = sys.argv[1], sys.argv[2]
    base = open(base_path, encoding='utf-8').read().replace('>Campus / Office<', '>Office<')
    preview = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == '--preview' else None
    prev = []
    for k, st in STYLES.items():
        s = sheet(st, f'{k} · ')
        sc = scene(st, base)
        open(f'{out_dir}/Fig{k}.dc.html', 'w', encoding='utf-8').write(s)
        open(f'{out_dir}/FigScene{k}.dc.html', 'w', encoding='utf-8').write(sc)
        if preview:
            body = re.search(r'<x-dc>(.*)</x-dc>', s, re.S).group(1)
            body = body.replace('<helmet>', '').replace('</helmet>', '')
            prev.append(body)
            sb = re.search(r'<x-dc>(.*)</x-dc>', sc, re.S).group(1).replace('<helmet>', '').replace('</helmet>', '')
            prev.append(f'<div style="width:1440px;height:810px;position:relative;overflow:hidden">{sb}</div>')
    if preview:
        open(preview, 'w', encoding='utf-8').write(
            '<!doctype html><meta charset="utf-8"><body style="margin:0">' + ''.join(prev) + '</body>')
    print('ok')


main()
