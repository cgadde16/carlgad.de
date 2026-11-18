# Rebuilds the four passes figure icons (motorcycle, bicycle, hiking, skiing) as standalone 64x64 SVGs:
# raw.py takes one still frame per figure from scripts/fig_astro.py (and figgen.py), then this script scales it
# to fit the 64 box using the ink bounding boxes in bbox.json (regenerate with measure.py) and writes the SVGs.
"""Usage (from the repo root): python3 -I scripts/icons/build.py src/components/passes/icons"""
import os, re, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src', 'components', 'passes', 'icons')
names = ['motorcycle', 'bicycle', 'hiking', 'skiing']
bb = json.load(open(os.path.join(HERE, 'bbox.json')))
INK, PAPERS, CREAM = '#14171A', ('#F4F5F2', '#F7F3EA'), '#F7F3EA'
MAIN = 1.8          # px weight of the generator's 1.7 line at 64px display size
GROUND, MAXW, MAXH, MAXS = 56, 58, 50, 1.15
WK = MAIN / 1.7     # final px per generator stroke unit

tmp = tempfile.mkdtemp()
subprocess.run([sys.executable, '-I', os.path.join(HERE, 'raw.py'), tmp], check=True, stdout=subprocess.DEVNULL)

def clean(raw):
    raw = re.sub(r'<circle class="puff"[^>]*></circle>', '', raw)       # invisible exhaust puffs
    raw = re.sub(r'\s(class|style)="[^"]*"', '', raw)
    raw = raw.replace(INK, 'currentColor')
    for p in PAPERS:
        raw = raw.replace(p, CREAM)
    return raw

os.makedirs(out, exist_ok=True)
for n in names:
    x0, y0, x1, y1 = bb[n]
    w, h = x1 - x0, y1 - y0
    s = min(MAXW / w, MAXH / h, MAXS)
    tx = 32 - s * (x0 + x1) / 2
    ty = GROUND
    raw = clean(open(os.path.join(tmp, n + '.raw.txt')).read())
    k = WK / s
    raw = re.sub(r'stroke-width="([\d.]+)"', lambda m: f'stroke-width="{float(m.group(1)) * k:.2f}"', raw)
    # wrap group has no stroke-width: give it the default (1) scaled like the rest
    raw = raw.replace('<g fill="none"', f'<g stroke-width="{k:.2f}" fill="none"', 1)
    body = f'<g transform="translate({tx:.2f} {ty}) scale({s:.3f})">{raw}</g>'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">{body}</svg>\n'
    open(os.path.join(out, n + '.svg'), 'w').write(svg)
    print(n, 'scale', round(s, 3), 'size', round(w * s, 1), 'x', round(h * s, 1))
