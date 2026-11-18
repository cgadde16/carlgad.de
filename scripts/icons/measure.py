"""Optional: re-measure each figure's ink bbox (generator units) and write bbox.json next to this script.
Needs ImageMagick (`magick RSVG:`), Pillow and numpy. Usage (repo root): python3 -I scripts/icons/measure.py"""
import os, sys, json, subprocess, tempfile, io
from PIL import Image
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
names = ['motorcycle', 'bicycle', 'hiking', 'skiing']
X0, Y0, W, H, S = -70, -80, 140, 95, 10
tmp = tempfile.mkdtemp()
subprocess.run([sys.executable, '-I', os.path.join(HERE, 'raw.py'), tmp], check=True, stdout=subprocess.DEVNULL)
bb = {}
for n in names:
    raw = open(os.path.join(tmp, n + '.raw.txt')).read().replace('#F4F5F2', '#F7F3EA')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{X0} {Y0} {W} {H}" width="{W*S}" height="{H*S}">'
           f'<rect x="{X0}" y="{Y0}" width="{W}" height="{H}" fill="#fff"/>{raw}</svg>')
    svgp = os.path.join(tmp, n + '.svg')
    open(svgp, 'w').write(svg)
    png = subprocess.run(['magick', 'RSVG:' + svgp, 'png:-'], check=True, capture_output=True).stdout
    a = np.array(Image.open(io.BytesIO(png)).convert('L')) < 235
    ys, xs = np.where(a)
    bb[n] = [round(float(v), 4) for v in (xs.min()/S + X0, ys.min()/S + Y0, (xs.max()+1)/S + X0, (ys.max()+1)/S + Y0)]
    print(n, bb[n])
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'bbox.json')
json.dump(bb, open(out, 'w'))
