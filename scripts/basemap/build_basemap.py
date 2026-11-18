"""Build src/data/basemap.json (Natural Earth 10m, Lambert azimuthal equal-area, viewBox 1000 x H).
Usage (repo root): python3 -I scripts/basemap/build_basemap.py [out.json]   -- downloads missing sources into dl/."""
import json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo
from proj import W, H, X0, Y1, SCALE, LON0, LAT0, R

BASE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
SOURCES = ['ne_10m_land', 'ne_10m_lakes', 'ne_10m_admin_0_boundary_lines_land', 'ne_10m_rivers_lake_centerlines']
RIVER_MAX_SCALERANK = 7
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src', 'data', 'basemap.json')

os.makedirs(geo.DL, exist_ok=True)
for name in SOURCES:
    dst = os.path.join(geo.DL, name + '.geojson')
    if not os.path.exists(dst):
        print('downloading', name)
        urllib.request.urlretrieve(BASE + name + '.geojson', dst + '.part')
        os.replace(dst + '.part', dst)

def river(props):
    sr = props.get('scalerank')
    return sr is not None and sr <= RIVER_MAX_SCALERANK and props.get('featurecla') != 'Lake Centerline'

land = geo.polygons('ne_10m_land', geo.MIN_AREA)
lakes = geo.polygons('ne_10m_lakes', geo.LAKE_MIN_AREA)
borders = geo.lines('ne_10m_admin_0_boundary_lines_land')
rivers = geo.lines('ne_10m_rivers_lake_centerlines', keep=river, min_len=2.0)
print('land polys', len(land), 'lakes', len(lakes), 'border lines', len(borders), 'rivers', len(rivers))

data = {
    'W': W, 'H': H,
    'proj': {'lon0': LON0, 'lat0': LAT0, 'R': R, 'X0': X0, 'Y1': Y1, 'scale': SCALE},
    'land': ''.join(geo.path_d(p) for p in land),
    'lakes': ''.join(geo.path_d(p) for p in lakes),
    'borders': geo.path_d(borders, close=False),
    'rivers': geo.path_d(rivers, close=False),
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w') as f:
    json.dump(data, f, separators=(',', ':'))
print('wrote', OUT, os.path.getsize(OUT), 'bytes;', {k: len(v) for k, v in data.items() if isinstance(v, str)})
