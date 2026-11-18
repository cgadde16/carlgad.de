"""404 scene (src/pages/404.astro): canvas Round 36 A ("NotFoundFog", v2).

The site's hiker takes his last two steps along a dotted trail on the middle ridge, stops where it fades into
the fog (all within a second) and then loops through confused poses (peers into the fog with a hand at his brow, looks around)
while a question mark bobs above him. Ridges, fog and birds as on the home page.

Writes src/components/LostScene.astro:
    python3 -I scripts/lost/lost.py src/components/LostScene.astro
Edit this script, never the .astro. The figure comes from scripts/figgen.py (walking flipbook) and a copy of
fig_astro.hiker_pose with two extras (forward elbow, dangling pole).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '..', 'figgen.py'), encoding='utf-8').read()
src = src[: src.rindex('\nmain()')]                  # figgen runs main() on import
ns = {'__name__': 'figgen'}
exec(src, ns)
ns['PAPER'] = '#F7F3EA'                              # the site's --paper
st = ns['STYLES']['A']
INK, PAPER = ns['INK'], ns['PAPER']
path, line, add, far, ik = ns['path'], ns['line'], ns['add'], ns['far'], ns['ik']

TORSO, POLE = math.hypot(3.5, 19), 36.5              # as in fig_astro: torso and pole of the walking hiker
LEAN_REF = math.degrees(math.atan2(3.5, 19))


def pose(P):
    """One hiker frame (facing right, feet at y 0). As fig_astro.hiker_pose, plus: nelbow 'fwd' lifts the near
    elbow forward (hand to the head), ntip None lets that pole dangle from the hand, nhand_fn places the hand
    relative to the head centre. Returns (svg, head centre)."""
    lw, hr = st['lw'], st['hr']
    hip, a = P['hip'], math.radians(P['lean'])
    sh = (hip[0] + TORSO * math.sin(a), hip[1] - TORSO * math.cos(a))

    def arm(hand, tip, fwd=False):
        el = ik(sh, hand, 9.5, 9, key=(lambda q: q[0] - 0.3 * q[1]) if fwd else (lambda q: -q[0]))
        if tip is None:
            tip = (hand[0] + 2.5, hand[1] + POLE)
        d = math.hypot(hand[0] - tip[0], hand[1] - tip[1])
        top = (tip[0] + (hand[0] - tip[0]) * POLE / d, tip[1] + (hand[1] - tip[1]) * POLE / d)
        return path(line(sh, el, hand), lw) + path(line(top, tip), 1.1)

    def leg(ft):
        kn = ik(hip, ft, 15, 15, key=lambda q: q[0])
        return path(line(hip, kn, ft), lw) + path(line(add(ft, (-1.5, 0)), add(ft, (3.5, 0))), lw)

    pack = (f'<g transform="rotate({P["lean"] - LEAN_REF:.1f} {sh[0]:.1f} {sh[1]:.1f})">'
            f'<rect x="{sh[0] - 10.5:.1f}" y="{sh[1] - 2:.1f}" width="7.5" height="16" rx="2" fill="{PAPER}" '
            f'stroke-width="1.3" transform="rotate(6 {sh[0] - 6:.1f} {sh[1] + 6:.1f})"></rect>'
            + path(line((sh[0] - 4, sh[1] + 1), (sh[0] - 1, sh[1] + 9)), 0.9) + '</g>')
    hc, hd = ns['head'](st, sh, P['look'])
    cap = (path(line(add(hc, (-hr - 2, -hr + 1.2)), add(hc, (hr + 3, -hr + 1.6))), 1.2)
           + f'<path d="M{ns["pt"](add(hc, (-hr + 0.5, -hr + 1.2)))} q{ns["f"](hr - 0.5)} -{ns["f"](hr + 0.4)} '
             f'{ns["f"](2 * hr - 0.5)} 0.2" fill="{INK}" stroke="none"></path>')
    near = P['nhand_fn'](hc) if 'nhand_fn' in P else P['nhand']
    body = (far(st, arm(P['fhand'], P['ftip'])) + far(st, leg(P['ffoot'])) + leg(P['nfoot']) + pack
            + path(line(hip, sh), st['tw']) + hd + cap + arm(near, P['ntip'], P.get('nelbow') == 'fwd'))
    return ns['wrap'](body), hc


# standing still and unsure: feet apart, poles planted wide
LOST = dict(hip=(0.8, -29.4), lean=4, nfoot=(5, 0), ffoot=(-4, 0), nhand=(7, -32), fhand=(-1.5, -32.5),
            ntip=(11, 0.5), ftip=(-7, 0.5), look=(0.25, -1))
AHEAD = dict(LOST, look=(0.5, -1))
PEER = dict(LOST, lean=13, look=(0.6, -1), nelbow='fwd', ntip=None, nhand_fn=lambda hc: (hc[0] + 4.5, hc[1] - 1.5))

# the confused loop: (pose, mirrored, seconds)
# it starts with peering into the fog, so he reads as lost within a second of the page opening. (A head-scratch
# with the dangling pole was tried: its two alternating frames made the pole flick, the user didn't want it.)
FIRST = [(PEER, False, 1.8)]
SEQ = FIRST + [(LOST, False, 0.5), (LOST, True, 1.3), (AHEAD, True, 0.5), (LOST, False, 0.5),
               (AHEAD, False, 0.4), (LOST, True, 1.0), (LOST, False, 0.4)]
T_FIRST = sum(s for _, _, s in FIRST)
CYCLE = round(sum(s for _, _, s in SEQ), 2)

S = 0.85                                             # figure scale (home page: 0.5)
TRAIL = ((466, 519), (473, 518.5), (481, 520), (488, 523))  # the last two steps of the trail; he stops at its end


def bez(t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(*TRAIL))


pts = [bez(i / 40) for i in range(41)]
acc = [0.0]
for p, q in zip(pts, pts[1:]):
    acc.append(acc[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
T_WALK = round(acc[-1] / (30 * S), 1)               # ~30 u/s per unit of scale matches his stride
walk_kf = ''.join(f'{100 * s / acc[-1]:.1f}% {{ transform: translate({x:.1f}px, {y:.1f}px); }} '
                  for (x, y), s in list(zip(pts, acc))[::4] + [(pts[-1], acc[-1])])

frames, frame_css = [], []
t = 0.0
for i, (P, mirrored, dur) in enumerate(SEQ):
    body, _ = pose(P)
    a, b = 100 * t / CYCLE, 100 * (t + dur) / CYCLE
    t += dur
    if i == 0:
        kf = f'0% {{ visibility: visible; }} {b:.3f}%, 100% {{ visibility: hidden; }}'
    else:
        kf = (f'0%, {a - 0.001:.3f}% {{ visibility: hidden; }} {a:.3f}% {{ visibility: visible; }} '
              + (f'{b:.3f}%, 100% {{ visibility: hidden; }}' if b < 99.999 else '100% { visibility: visible; }'))
    frame_css.append(f'@keyframes lost-f{i} {{ {kf} }}\n'
                     f'.lost-f{i} {{ animation: lost-f{i} {CYCLE}s step-end {T_WALK}s infinite both; }}')
    frames.append(f'<g class="lost-f lost-f{i}"><g transform="scale({-S if mirrored else S} {S})">{body}</g></g>')

_, hc0 = pose(LOST)
q2a, q2b, q2c = (100 * T_FIRST * k / CYCLE for k in (0.2, 0.8, 1.15))
qx, qy = hc0[0] * S, hc0[1] * S - 13

css = f'''
.lost-scene {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block; }}
.lost-fog {{ animation: lost-drift 26s ease-in-out infinite alternate; }}
.lost-fog.f2 {{ animation-duration: 34s; animation-direction: alternate-reverse; }}
.lost-fog.f3 {{ animation-duration: 42s; }}
@keyframes lost-drift {{ from {{ transform: translateX(-60px); }} to {{ transform: translateX(70px); }} }}

/* walking flipbook (figgen.hiker) */
.lost-walk .flip .f {{ visibility: hidden; }}
.lost-walk .flip .f0 {{ visibility: visible; }}
.lost-walk .hik .f {{ animation: lost-flip10 1.1s step-end infinite; }}
@keyframes lost-flip10 {{ 0% {{ visibility: visible; }} 10.3%, 100% {{ visibility: hidden; }} }}

/* walk in ({T_WALK}s), then the confused loop ({CYCLE}s) */
.lost-walker {{ transform: translate({pts[-1][0]:.1f}px, {pts[-1][1]:.1f}px); animation: lost-walk-in {T_WALK}s linear 1 both; }}
@keyframes lost-walk-in {{ {walk_kf}}}
.lost-walk {{ animation: lost-hide {T_WALK}s step-end 1 both; }}
.lost-stand {{ animation: lost-show {T_WALK}s step-end 1 both; }}
@keyframes lost-hide {{ 0% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
@keyframes lost-show {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
.lost-f {{ visibility: hidden; }}
.lost-f0 {{ visibility: visible; }}
{chr(10).join(frame_css)}

/* the question mark pops up as he stops and bobs; a smaller one comes and goes while he peers into the fog */
.lost-q1 {{ transform-box: fill-box; transform-origin: 50% 100%;
  animation: lost-qpop 0.45s cubic-bezier(0.3, 1.6, 0.5, 1) {max(0.0, T_WALK - 0.2):.1f}s both, lost-qbob 2.4s ease-in-out {T_WALK + 0.3:.1f}s infinite; }}
@keyframes lost-qpop {{ from {{ transform: scale(0); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
@keyframes lost-qbob {{ 0%, 100% {{ transform: translateY(0) rotate(-4deg); }} 50% {{ transform: translateY(-3px) rotate(5deg); }} }}
.lost-q2 {{ opacity: 0; animation: lost-q2 {CYCLE}s ease-in-out {T_WALK}s infinite; }}
@keyframes lost-q2 {{ 0% {{ opacity: 0; transform: translate(0, 0); }} {q2a:.1f}% {{ opacity: 0.8; }}
  {q2b:.1f}% {{ opacity: 0.8; transform: translate(3px, -6px); }} {q2c:.1f}%, 100% {{ opacity: 0; transform: translate(4px, -8px); }} }}

@media (prefers-reduced-motion: reduce) {{
  .lost-fog, .lost-walker, .lost-walk, .lost-stand, .lost-f, .lost-q1, .lost-q2 {{ animation: none; }}
  .lost-walk {{ opacity: 0; }}
}}
'''

QFONT = 'font-family="Instrument Serif, Georgia, serif" font-style="italic" fill="currentColor"'
figure = (f'<g class="lost-walker">'
          f'<g class="lost-walk"><g transform="scale({S})" opacity="0.85">{ns["hiker"](st)}</g></g>'
          f'<g class="lost-stand"><g opacity="0.85">{"".join(frames)}</g>'
          f'<text class="lost-q1" x="{qx:.1f}" y="{qy:.1f}" text-anchor="middle" font-size="30" {QFONT}>?</text>'
          f'<text class="lost-q2" x="{qx + 13:.1f}" y="{qy - 9:.1f}" text-anchor="middle" font-size="19" {QFONT}>?</text>'
          '</g></g>')

puff = 'fill="url(#lost-puff)"'
astro = f'''---
// GENERATED by scripts/lost/lost.py; edit the script, not this file.
// 404 scene: the hiker walks into the fog, stops where the trail fades and looks around, confused.
---

<svg class="lost-scene" viewBox="0 0 1440 810" preserveAspectRatio="xMidYMax slice" role="img"
  aria-label="A hiker walks along a trail into the fog, stops where it fades, peers into the fog and looks around, confused. A question mark floats above him.">
  <defs>
    <filter id="lost-mist" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="2.2"></feGaussianBlur></filter>
    <radialGradient id="lost-puff">
      <stop offset="0" style="stop-color: var(--paper); stop-opacity: 1"></stop>
      <stop offset="1" style="stop-color: var(--paper); stop-opacity: 0"></stop>
    </radialGradient>
  </defs>
  <path filter="url(#lost-mist)" fill="var(--ridge-back)" d="M0 520 C120 470 200 500 300 450 C380 410 430 470 520 440 C640 400 700 330 780 400 C860 470 940 430 1040 380 C1140 330 1200 420 1290 400 C1360 386 1410 420 1440 410 L1440 810 L0 810 Z"></path>
  <g class="lost-fog f3"><ellipse cx="300" cy="450" rx="340" ry="70" {puff}></ellipse><ellipse cx="900" cy="420" rx="420" ry="80" {puff}></ellipse><ellipse cx="1350" cy="430" rx="260" ry="60" {puff}></ellipse></g>
  <path filter="url(#lost-mist)" fill="var(--ridge-mid)" d="M0 600 C140 560 240 590 360 540 C460 500 540 560 660 530 C800 495 880 560 1000 520 C1120 480 1220 540 1440 500 L1440 810 L0 810 Z"></path>
  <path d="M60 590 C150 566 250 572 330 551 C390 530 440 516 488 523" fill="none" stroke="currentColor" stroke-width="1.4" stroke-dasharray="1 7" stroke-linecap="round" opacity="0.7"></path>
  <path d="M520 530 C580 544 630 536 690 526" fill="none" stroke="currentColor" stroke-width="1.4" stroke-dasharray="1 7" stroke-linecap="round" opacity="0.16"></path>
  {figure}
  <g class="lost-fog"><ellipse cx="660" cy="535" rx="190" ry="46" {puff}></ellipse><ellipse cx="1060" cy="515" rx="330" ry="58" {puff}></ellipse><ellipse cx="140" cy="580" rx="220" ry="40" {puff} opacity="0.7"></ellipse></g>
  <path filter="url(#lost-mist)" fill="var(--ridge-front)" d="M0 700 C200 650 380 690 560 660 C760 628 900 690 1100 650 C1240 624 1360 660 1440 640 L1440 810 L0 810 Z"></path>
  <g class="lost-fog f2"><ellipse cx="420" cy="660" rx="380" ry="54" {puff} opacity="0.85"></ellipse><ellipse cx="1180" cy="640" rx="300" ry="50" {puff} opacity="0.85"></ellipse></g>
  <g fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.55"><path d="M330 214 q5 -5 10 0 q5 -5 10 0"></path><path d="M362 200 q4 -4 8 0 q4 -4 8 0"></path></g>
</svg>

<style is:global>{css}</style>
'''

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'src', 'components', 'LostScene.astro')
with open(out, 'w', encoding='utf-8') as fh:
    fh.write(astro)
print(f'LostScene: walk {T_WALK}s, loop {CYCLE}s, {len(SEQ)} frames -> {out}')
