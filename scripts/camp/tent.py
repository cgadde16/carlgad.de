"""Base camp scene (/about/): the inside of the tent, canvas Round 35 A2 ("TentWhole").

Writes src/components/camp/TentScene.astro (SVG + one hotspot button per object):
    python3 -I scripts/camp/tent.py src/components/camp/TentScene.astro
Edit this script, never the .astro. Object labels and the card texts live in src/data/camp.ts.
"""
import sys

INK = 'stroke="#14171a" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"'


def g(body):
    return f'<g fill="none" {INK}>{body}</g>'


# ---------- objects: (w, h, svg) in local coords ----------
O = {}
O['laptop'] = (120, 86, g(
    '<path d="M6 76 H114 L120 86 H0 Z" fill="#e5ded0"/>'
    '<rect x="12" y="2" width="96" height="72" rx="4" fill="#3b3a36"/>'
    '<rect x="18" y="8" width="84" height="58" fill="#fbf8f1" stroke-width="1"/>'
    '<path d="M24 18 H62 M24 27 H84 M24 36 H54 M24 45 H76 M24 54 H48" stroke="#4D7C0F" stroke-width="2"/>'
    '<path d="M66 18 H80" stroke="#C2410C" stroke-width="2"/><path d="M48 81 H72" stroke-width="1.2"/>'))
O['journal'] = (120, 56, g(
    '<path d="M60 12 C44 5 18 5 3 9 L2 52 C18 47 44 47 60 54 Z" fill="#fbf8f1"/>'
    '<path d="M60 12 C76 5 102 5 117 9 L118 52 C102 47 76 47 60 54 Z" fill="#fbf8f1"/>'
    '<path d="M60 12 V54" stroke-width="1.2"/>'
    '<path d="M12 19 H50 M12 27 H52 M12 35 H44 M70 19 H108 M70 27 H104" stroke="#a39d92" stroke-width="1"/>'
    '<path d="M76 46 L114 30" stroke="#1E3A8A" stroke-width="3"/>'
    '<path d="M38 8 V0 L42 4 L46 0 V8" fill="#C2410C" stroke="none"/>'))
O['map'] = (120, 60, g(
    '<path d="M0 10 L30 4 L60 10 L90 4 L120 10 L120 56 L90 50 L60 56 L30 50 L0 56 Z" fill="#fbf8f1"/>'
    '<path d="M30 4 V50 M60 10 V56 M90 4 V50" stroke-width="1"/>'
    '<path d="M70 40 C80 36 92 42 104 38" stroke="#5d7f99" stroke-width="1.4"/>'
    '<path d="M12 44 C28 30 46 40 62 26 C78 14 94 26 108 18" stroke="#C2410C" stroke-dasharray="3 4"/>'
    '<circle cx="12" cy="44" r="3" fill="#14171a" stroke="none"/><circle cx="108" cy="18" r="3.5" fill="#C2410C" stroke="none"/>'))
O['phrasebook'] = (52, 68,  # the phrasebook: blue cover with two speech bubbles (canvas r48 Kit A)
    '<g fill="none" stroke="#14171a" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"><path d="M8 6 L48 2 L52 6 V66 L12 68 L8 64 Z" fill="#e5ded0"/><rect x="4" y="2" width="44" height="62" rx="3" fill="#3e6596"/><path d="M12 14 H34 C37 14 38 16 38 18 V26 C38 28 37 30 34 30 H20 L15 35 V30 H12 C10 30 9 28 9 26 V18 C9 16 10 14 12 14 Z" fill="#fbf8f1" stroke-width="1"/><path d="M22 34 H40 C42 34 43 35 43 37 V43 C43 45 42 46 40 46 H38 V50 L34 46 H22 C20 46 19 45 19 43 V37 C19 35 20 34 22 34 Z" fill="#efe8da" stroke-width="1"/></g>')
O['jersey'] = (100, 84,  # a cycling jersey, front view: dark grey with a light ridge line across the chest (canvas r48 Kit B)
    '<g fill="none" stroke="#14171a" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"><defs><clipPath id="jcB"><path d="M30 8 L42 4 C46 11 54 11 58 4 L70 8 L96 24 L87 42 L74 35 L75 82 L25 82 L26 35 L13 42 L4 24 Z"/></clipPath></defs><path d="M30 8 L42 4 C46 11 54 11 58 4 L70 8 L96 24 L87 42 L74 35 L75 82 L25 82 L26 35 L13 42 L4 24 Z" fill="#4a4f52"/><g clip-path="url(#jcB)" stroke="none"><path d="M0 52 L18 40 L30 46 L44 32 L56 42 L66 34 L80 44 L100 36 V84 H0 Z" fill="#6b7175"/><path d="M0 52 L18 40 L30 46 L44 32 L56 42 L66 34 L80 44 L100 36" fill="none" stroke="#efe8da" stroke-width="1.8"/></g><path d="M30 8 L42 4 C46 11 54 11 58 4 L70 8 L96 24 L87 42 L74 35 L75 82 L25 82 L26 35 L13 42 L4 24 Z"/><path d="M50 9 V82" stroke-width="1" stroke-dasharray="2 2.5"/><path d="M42 4 C46 11 54 11 58 4" fill="#2f3335" stroke-width="1.2"/></g>')
O['boots'] = (120, 72, g(  # a pair of hiking boots, side view
    '<path d="M48 6 H72 L74 30 C88 32 100 38 102 50 V60 H40 L42 38 C44 28 46 16 48 6 Z" fill="#7a5c40"/>'
    '<path d="M40 60 H102 V68 H40 Z" fill="#3b3a36"/><path d="M52 14 H68 M52 22 H70 M52 30 H72" stroke="#efe8da" stroke-width="1.2"/>'
    '<path d="M14 2 H38 L40 26 C54 28 66 34 68 46 V56 H6 L8 34 C10 24 12 12 14 2 Z" fill="#8f6f4e"/>'
    '<path d="M6 56 H68 V64 H6 Z" fill="#3b3a36"/><path d="M18 10 H34 M18 18 H36 M18 26 H38" stroke="#efe8da" stroke-width="1.2"/>'))
O['bikehelmet'] = (140, 80,  # bike helmet and a water bottle on the floor, side view (canvas r48 Floor C); floor contact at y 68
    '<g transform="translate(0 68)" ' + INK + '>' + '<path d="M0 -6 C0 -40 26 -52 52 -50 C74 -48 88 -34 90 -12 L84 -6 Z" fill="#efe8da"/><path d="M16 -30 L28 -40 M34 -36 L46 -46 M54 -34 L64 -44 M70 -26 L78 -36" stroke="#3b3a36" stroke-width="3.2"/><path d="M0 -6 H84 V0 H0 Z" fill="#3b3a36"/><path d="M84 -12 L100 -10 L98 -4 L84 -6" fill="#3b3a36"/><path d="M10 0 C14 10 30 12 40 4" fill="none" stroke="#3b3a36" stroke-width="1.6"/><rect x="112" y="-58" width="24" height="58" rx="5" fill="#3e6596"/><rect x="116" y="-68" width="16" height="12" rx="3" fill="#3b3a36"/><rect x="112" y="-38" width="24" height="12" fill="#fbf8f1" stroke-width="1"/>' + '</g>')
# Floor group, front left (sizes from the table: ~2.5 px per cm at the floor's depth): a folding camp stool (~45 cm),
# and next to it on the floor a thermos (~30 cm) and a tin cup (~8 cm), at different depths.
O['stool'] = (104, 114, g(  # folding stool, side view: two outlined tube legs in the same grey crossing at a bolt,
    # rubber feet along the legs, a sagging fabric seat; floor contact at y 114
    '<path d="M89.9 110.6 L15.9 10.6 L12.1 13.4 L86.1 113.4 Z" fill="#b3aea4" stroke-width="1.1"/><path d="M90.6 110.1 L86.4 104.5 L81.3 108.3 L85.4 113.9 Z" fill="#3b3a36" stroke-width="1.1"/><path d="M13.9 113.4 L87.9 13.4 L84.1 10.6 L10.1 110.6 Z" fill="#b3aea4" stroke-width="1.1"/><path d="M14.6 113.9 L18.7 108.3 L13.6 104.5 L9.4 110.1 Z" fill="#3b3a36" stroke-width="1.1"/><circle cx="50" cy="61.5" r="3.2" fill="#3b3a36" stroke-width="1"/><circle cx="50" cy="61.5" r="1" fill="#b3aea4" stroke="none"/><path d="M2 2 C26 12 74 12 98 2 L96 10 C74 20 26 20 4 10 Z" fill="#3e6596"/><path d="M8 8.5 C30 16 70 16 92 8.5" fill="none" stroke="#2b4a72" stroke-width="1"/>'))
O['cup'] = (34, 26, g(  # tin cup with a handle; floor contact at y 26
    '<path d="M2 2 H26 L24 23 C24 25 22 26 20 26 H8 C6 26 4 25 4 23 Z" fill="#c9cdc8"/>'
    '<path d="M26 6 C34 6 34 18 25 18" fill="none"/>'))
O['thermos'] = (36, 98, g(  # thermos flask; floor contact at y 98
    '<rect x="2" y="16" width="30" height="82" rx="6" fill="#4D7C0F"/>'
    '<rect x="0" y="2" width="34" height="16" rx="4" fill="#3b3a36"/>'
    '<rect x="2" y="48" width="30" height="10" fill="#fbf8f1" stroke-width="1"/>'))
O['camera'] = (70, 52, g(
    '<rect x="2" y="12" width="66" height="38" rx="5" fill="#efe8da"/>'
    '<rect x="12" y="4" width="22" height="10" rx="2" fill="#fbf8f1"/>'
    '<circle cx="40" cy="31" r="14" fill="#fbf8f1"/><circle cx="40" cy="31" r="7" fill="#3b3a36"/>'
    '<circle cx="60" cy="19" r="2.5"/><path d="M2 22 H18" stroke-width="1"/>'))
O['mug'] = (44, 46, g(
    '<path d="M14 2 C11 -4 17 -8 14 -14 M24 2 C21 -4 27 -8 24 -14" stroke="#a39d92" stroke-width="1.2"/>'
    '<path d="M4 8 H34 V38 C34 42 30 45 26 45 H12 C8 45 4 42 4 38 Z" fill="#fbf8f1"/>'
    '<ellipse cx="19" cy="8" rx="15" ry="3.5" fill="#3b3a36"/>'
    '<path d="M34 14 C44 14 44 32 34 32"/>'))
O['lantern'] = (44, 72, g(
    '<path d="M22 0 V7" stroke-width="1.2"/><circle cx="22" cy="10" r="3"/>'
    '<path d="M10 22 L16 13 H28 L34 22 Z" fill="#3b3a36"/>'
    '<rect x="11" y="22" width="22" height="34" rx="3" fill="#f3d27a"/>'
    '<path d="M22 46 C17 40 20 34 22 30 C24 34 27 40 22 46 Z" fill="#C2410C" stroke="none"/>'
    '<path d="M11 30 H33 M11 48 H33" stroke-width="1"/>'
    '<rect x="9" y="56" width="26" height="7" rx="2" fill="#3b3a36"/>'))
O['sock'] = (26, 40, g('<path d="M4 0 H18 V24 C18 30 24 30 24 36 C24 40 16 40 12 38 C6 36 4 30 4 24 Z" fill="#fbf8f1"/><path d="M4 6 H18" stroke-width="1"/>'))


class Scene:
    def __init__(self, vw, vh):
        self.vw, self.vh = vw, vh
        self.parts, self.hots = [], []

    def raw(self, s):
        self.parts.append(s)

    def put(self, name, x, y, s=1.0, key=None, label=None, rot=0):
        w, h, body = O[name]
        sw, sh = w * s, h * s
        tr = f'translate({x:g} {y:g})'
        if rot:
            tr += f' rotate({rot:g} {sw/2:g} {sh/2:g})'
        if s != 1:
            tr += f' scale({s:g})'
        self.parts.append(f'<g transform="{tr}">{body}</g>')
        if key:
            p = 6
            pc = lambda v, tot: f'{v / tot * 100:.2f}%'
            self.hots.append({'k': key, 'label': label, 'up': (y + sh + p) / self.vh > 0.85,
                              'x': pc(x - p, self.vw), 'y': pc(y - p, self.vh),
                              'w': pc(sw + 2 * p, self.vw), 'h': pc(sh + 2 * p, self.vh)})

    def svg(self, label, defs=''):
        return (f'<svg viewBox="0 0 {self.vw} {self.vh}" role="img" aria-label="{label}" style="display: block; width: 100%; height: auto">'
                f'<defs>{defs}</defs>' + ''.join(self.parts) + '</svg>')


def glow(id_, cx, cy, r, op=0.5):
    return (f'<radialGradient id="{id_}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r}">'
            f'<stop offset="0" stop-color="#f3d27a" stop-opacity="{op}"/><stop offset="0.45" stop-color="#f3d27a" stop-opacity="{op*0.35:.3f}"/>'
            f'<stop offset="1" stop-color="#f3d27a" stop-opacity="0"/></radialGradient>')


def table_front(sc, x0, x1, y, depth, floor, wood='#d8c3a0', edge='#b89b70'):
    sc.raw(g(f'<path d="M{x0+30} {y} H{x1-30} L{x1} {y+depth} H{x0} Z" fill="{wood}"/>'
             f'<rect x="{x0}" y="{y+depth}" width="{x1-x0}" height="10" fill="{edge}"/>'
             f'<path d="M{x0+40} {y+depth+10} L{x0+110} {floor} M{x0+110} {y+depth+10} L{x0+40} {floor} '
             f'M{x1-40} {y+depth+10} L{x1-110} {floor} M{x1-110} {y+depth+10} L{x1-40} {floor}" stroke-width="2.2"/>'))


# ---------- scene: 1440 x 1000, the page is the tent ----------
S = Scene(1440, 1000)
DOOR = 'M720 330 C690 390 600 600 560 780 H880 C840 600 750 390 720 330 Z'
S.raw('<path d="M0 0 H720 V300 L470 780 L90 1000 H0 Z" fill="#ddd3c0"/>'
      '<path d="M1440 0 H720 V300 L970 780 L1350 1000 H1440 Z" fill="#ddd3c0"/>'
      '<path d="M720 300 L470 780 H970 Z" fill="#e5ded0"/>'
      '<path d="M720 100 L210 930 M720 200 L340 855 M720 100 L1230 930 M720 200 L1100 855" stroke="#cbc1ad" stroke-width="1.3" fill="none"/>'
      '<g clip-path="url(#doorW)"><rect x="540" y="320" width="360" height="470" fill="#fbf8f1"/>'
      '<path d="M550 560 C600 520 640 540 690 500 C730 470 770 520 810 500 C840 488 870 500 890 496 V780 H550 Z" fill="#ece6da"/>'
      '<path d="M550 650 C630 624 750 646 890 630 V780 H550 Z" fill="#e5ded0"/>'
      '<path d="M550 650 C630 624 750 646 890 630" fill="none" stroke="#14171a" stroke-width="1.2"/>'
      '<path d="M630 432 l7 -4 l7 4 M660 412 l6 -3 l6 3" fill="none" stroke="#14171a" stroke-width="1.1" stroke-linecap="round"/></g>'
      f'<path d="{DOOR}" fill="none" stroke="#14171a" stroke-width="1.4"/>'
      '<path d="M720 320 C686 384 592 598 550 780 M720 320 C754 384 848 598 890 780" fill="none" stroke="#14171a" stroke-width="1" stroke-dasharray="2 4"/>'
      '<path d="M720 330 C700 372 650 470 612 560 C634 548 668 494 690 440 C704 400 714 364 720 330 Z" fill="#d3c9b6" stroke="#14171a" stroke-width="1.2" stroke-linejoin="round"/>'
      '<path d="M618 552 L604 576" stroke="#14171a" stroke-width="1.2"/>'
      '<path d="M90 1000 L470 780 H970 L1350 1000 Z" fill="#cfc5b2"/>'
      '<path d="M720 0 V300 L470 780 L90 1000 M720 300 L970 780 L1350 1000 M470 780 H970" fill="none" stroke="#14171a" stroke-width="1.5" stroke-linejoin="round"/>'
      '<circle cx="720" cy="200" r="300" fill="url(#glowW)"/>'
      '<path d="M1000 246 C1110 262 1310 266 1440 254" fill="none" stroke="#14171a" stroke-width="1.2"/>'  # the note's cord (keep in sync with .card top in about/index.astro)
      '<circle cx="720" cy="134" r="4" fill="none" stroke="#14171a" stroke-width="1.2"/>')
S.put('lantern', 698, 136)
# the left wall: two lines with two socks and the camera
S.raw('<g class="wall-left">')
S.raw('<path d="M80 330 C180 362 320 372 470 360" fill="none" stroke="#14171a" stroke-width="1.2"/>')
# two socks side by side on the upper line; the camera hangs by its strap at the right of the lower line
# (canvas Round 47 F, two lines); empty pegs on both lines for things to come
PEG = '<rect x="{x}" y="{y}" width="8" height="18" fill="#d8c3a0" stroke="#14171a" stroke-width="1"/>'
# the phrasebook hangs from a peg on the upper line, left of the socks (peg drawn over its top)
# upper line, left to right, spread evenly between x 110 and 452 (24px margins and gaps; the socks hang as a pair):
# phrasebook on a peg, two socks, the cycling jersey pegged at both shoulders. Heights follow the line.
S.put('phrasebook', 134, 348.0, 1.1, 'lang', 'Phrasebook', rot=2)
S.raw(PEG.format(x=158.6, y=341.0))
S.put('sock', 215, 358.4, 1.3, rot=4)
S.put('sock', 255, 361.6, 1.3, rot=-3)
S.put('jersey', 313, 355.4, 1.15, 'bike', 'Cycling jersey')
S.raw(PEG.format(x=343.5, y=355.9) + PEG.format(x=389.5, y=355.2))
# the second line, lower on the wall
S.raw('<path d="M96 520 C200 550 340 558 478 544" fill="none" stroke="#14171a" stroke-width="1.2"/>'
      )
# the map hangs from the lower line by two pegs, left of the camera (pegs drawn over its top edge)
S.put('map', 168, 529.5, 1.15, 'route', 'Map', rot=4.6)
S.raw(PEG.format(x=176, y=532) + PEG.format(x=290, y=543))
AX, AY = 395, 550  # where the strap loops over the lower line
# The camera hangs centred under the loop (its centre x = AX). The strap runs from the two ends of the loop to the
# camera's lugs (local (4,16) and (66,16), after its scale 1.05 and 4 degree tilt: AX-32/AY+64.6 and AX+33/AY+69.1);
# the camera, drawn after, covers the strap ends. The loop arches over the line (the line is at y ~549.8 here).
S.raw(f'<path d="M{AX-4.5} {AY+1.5} L{AX-32} {AY+64.6} M{AX+4.5} {AY+1.5} L{AX+33} {AY+69.1}" fill="none" stroke="#3b3a36" stroke-width="2" stroke-linecap="round"/>'
      f'<path d="M{AX-4.5} {AY+1.5} C{AX-4.5} {AY-6} {AX+4.5} {AY-6} {AX+4.5} {AY+1.5}" fill="none" stroke="#3b3a36" stroke-width="2" stroke-linecap="round"/>')
S.put('camera', AX - 37, AY + 50, 1.05, 'photo', 'Camera', rot=4)
S.raw('</g>')
table_front(S, 490, 950, 690, 50, 860)
S.put('laptop', 530, 600, 1.3, 'now', 'Laptop')
S.put('journal', 700, 655, 1.1, 'who', 'Journal')
# boots removed from the floor at the user's request (2026-11-17); O['boots'] kept in case they come back
S.put('stool', 300, 925 - 114)  # stool a little back, away from the wall
S.put('thermos', 410, 958 - 98 * 0.84, 0.84)  # thermos on the floor right of the stool, a bit nearer
S.put('cup', 378, 978 - 26 * 0.9, 0.9)  # tin cup on the floor in front, between stool and thermos
S.put('bikehelmet', 1020, 945 - 68)  # decoration only, front right of the floor
S.put('mug', 860, 716 - 46 * 1.15, 1.15, 'coffee', 'Coffee')  # on the table, where the camera stood


# ---------- emit ----------
DEFS = f'<clipPath id="doorW"><path d="{DOOR}"/></clipPath>' + glow('glowW', 720, 200, 300, 0.32)
LABEL = ('Inside a tent: the door is open to the mountains, a camp table with laptop, journal and a coffee, '
         'a phrasebook, two socks, a cycling jersey, a map and a camera on two lines, and on the floor a folding stool with a thermos and a tin cup, a bike helmet and a water bottle')

buttons = '\n'.join(
    f'  <button type="button" class="hot{" up" if h["up"] else ""}" data-k="{h["k"]}" aria-pressed={{initialFact === \'{h["k"]}\' ? \'true\' : \'false\'}} '
    f'aria-label={{objects.{h["k"]}}} style="left: {h["x"]}; top: {h["y"]}; width: {h["w"]}; height: {h["h"]}">'
    f'<span class="tag">{{objects.{h["k"]}}}</span></button>'
    for h in S.hots)

OUT = f'''---
// GENERATED by scripts/camp/tent.py: edit the script, not this file.
// The tent fills the page; each object is a transparent button laid over its drawing.
import {{ objects, initialFact }} from '../../data/camp';
---

<div class="scene">
  {S.svg(LABEL, DEFS)}
{buttons}
</div>

<style>
  .scene {{ position: relative; }}
  .scene svg {{ display: block; width: 100%; height: auto; }}
  .hot {{
    position: absolute; padding: 0; margin: 0; border: 0; background: transparent; cursor: pointer;
    border-radius: 10px; outline-offset: 3px; transition: background 160ms ease;
  }}
  .hot:hover {{ background: rgba(251, 248, 241, 0.22); }}
  .hot:focus-visible {{ outline: 2px solid var(--ink); }}
  /* the current item is not marked at all (user request): tags show on hover and keyboard focus only */
  .tag {{
    position: absolute; left: 50%; top: 100%; transform: translate(-50%, 6px); z-index: 2;
    white-space: nowrap; padding: 3px 9px; background: #fbf8f1; border: 1.2px solid var(--ink); border-radius: 2px;
    font-size: 12px; font-weight: 500; color: var(--ink); opacity: 0; transition: opacity 160ms ease; pointer-events: none;
  }}
  /* items near the bottom edge get their tag above them: a tag below would hang out of the scene and, even while
     invisible, make the page a few px taller than the tent (a light strip showed when scrolling) */
  .hot.up .tag {{ top: auto; bottom: 100%; transform: translate(-50%, -6px); }}
  .hot:hover .tag, .hot:focus-visible .tag {{ opacity: 1; }}
</style>
'''

with open(sys.argv[1], 'w') as fh:
    fh.write(OUT)
print(sys.argv[1], len(OUT), 'bytes,', len(S.hots), 'hotspots')
