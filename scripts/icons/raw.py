"""Exec the website's fig_astro.py (read only) into a namespace and produce one still frame per figure
as raw markup in generator units (ground at y=0, facing right). Usage: python3 -I raw.py <out dir>"""
import math, os, sys, tempfile, io, contextlib
SC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # <repo>/scripts
out = sys.argv[1]
src = open(os.path.join(SC, 'fig_astro.py'), encoding='utf-8').read()
tmp = os.path.join(tempfile.mkdtemp(), 'x.astro')                   # fig_astro writes an .astro file; discard it
sys.argv = ['fig_astro.py', tmp]
g = {'__name__': 'fig_astro', '__file__': os.path.join(SC, 'fig_astro.py')}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, 'fig_astro.py', 'exec'), g)
ns, st = g['ns'], g['st']
BIKE_TH = float(os.environ.get('BIKE_TH', math.pi/4))
HIK_K = int(os.environ.get('HIK_K', 1))
SKI_PH = float(os.environ.get('SKI_PH', math.pi/2))

res = {}
# motorcycle: the home page's Panigale with the same line style (puffs are opacity 0 and removed later)
res['motorcycle'] = g['panigale'].panigale_svg(ns['PAPER'], g['INK'], uid='icon', **g['MOTO_STYLE'])
# bicycle: seated pose, cranks at angle th
P = dict(g['SEATED'], **g['pedals'](BIKE_TH))
res['bicycle'] = ns['wrap'](g['bike'](st, 'spin') + g['bike_rider'](st, P))
# hiker: pick one frame of the figgen flipbook
orig = ns['flip']
ns['flip'] = lambda cls, frames, period: frames[HIK_K]
res['hiking'] = ns['hiker'](st, 10)
ns['flip'] = orig
# skier: downhill tuck pose
res['skiing'] = ns['wrap'](g['rider'](st, g['ski_pose'](SKI_PH)))
os.makedirs(out, exist_ok=True)
for k, v in res.items():
    open(os.path.join(out, k + '.raw.txt'), 'w').write(v)
print({k: len(v) for k, v in res.items()})
