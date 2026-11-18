"""Load, project, clip and simplify Natural Earth vectors into viewBox units."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proj import project, W, H

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, 'dl')   # Natural Earth downloads (git-ignored)
PADC = 6.0   # clip margin outside the frame (invisible, keeps frame edges free of stroke)
EPS = 0.15            # Douglas-Peucker tolerance, viewBox units
MIN_AREA = 0.5        # drop islands smaller than this (sq units)
LAKE_MIN_AREA = 0.5   # drop lakes smaller than this
MIN_LINE = 3.0        # drop border/river pieces shorter than this (units)

def load(name):
    with open(os.path.join(DL, name + '.geojson')) as f:
        return json.load(f)['features']

def area(ring):
    a = 0.0
    for i in range(len(ring)-1):
        a += ring[i][0]*ring[i+1][1] - ring[i+1][0]*ring[i][1]
    return a/2

def dp(pts, eps):
    n = len(pts)
    if n < 3: return list(pts)
    keep = [False]*n; keep[0] = keep[-1] = True
    stack = [(0, n-1)]
    e2 = eps*eps
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]; bx, by = pts[b]
        dx, dy = bx-ax, by-ay
        L2 = dx*dx+dy*dy
        md, mi = -1.0, -1
        for i in range(a+1, b):
            px, py = pts[i]
            if L2 == 0:
                d = (px-ax)**2+(py-ay)**2
            else:
                t = ((px-ax)*dx+(py-ay)*dy)/L2
                t = max(0, min(1, t))
                d = (px-ax-t*dx)**2+(py-ay-t*dy)**2
            if d > md: md, mi = d, i
        if md > e2:
            keep[mi] = True
            stack.append((a, mi)); stack.append((mi, b))
    return [p for p, k in zip(pts, keep) if k]

def quant(pts):
    """Round to the 0.1 output grid and drop consecutive duplicates."""
    out = []
    for x, y in pts:
        q = (round(x*10)/10, round(y*10)/10)
        if not out or q != out[-1]: out.append(q)
    return out

def clip_poly(ring, x0, y0, x1, y1):
    """Sutherland-Hodgman on an (open or closed) ring; returns open ring."""
    if ring[0] == ring[-1]: ring = ring[:-1]
    def run(pts, inside, inter):
        out = []
        if not pts: return out
        prev = pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev): out.append(inter(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(inter(prev, cur))
            prev = cur
        return out
    def ix(xc):
        return lambda p, q: (xc, p[1]+(q[1]-p[1])*(xc-p[0])/(q[0]-p[0]))
    def iy(yc):
        return lambda p, q: (p[0]+(q[0]-p[0])*(yc-p[1])/(q[1]-p[1]), yc)
    pts = ring
    pts = run(pts, lambda p: p[0] >= x0, ix(x0))
    pts = run(pts, lambda p: p[0] <= x1, ix(x1))
    pts = run(pts, lambda p: p[1] >= y0, iy(y0))
    pts = run(pts, lambda p: p[1] <= y1, iy(y1))
    return pts

def clip_line(pts, x0, y0, x1, y1):
    """Liang-Barsky per segment; returns list of polylines."""
    out = []; cur = []
    for i in range(len(pts)-1):
        (ax, ay), (bx, by) = pts[i], pts[i+1]
        dx, dy = bx-ax, by-ay
        t0, t1 = 0.0, 1.0; ok = True
        for p, q in ((-dx, ax-x0), (dx, x1-ax), (-dy, ay-y0), (dy, y1-ay)):
            if p == 0:
                if q < 0: ok = False; break
            else:
                r = q/p
                if p < 0:
                    if r > t1: ok = False; break
                    t0 = max(t0, r)
                else:
                    if r < t0: ok = False; break
                    t1 = min(t1, r)
        if not ok:
            if len(cur) > 1: out.append(cur)
            cur = []; continue
        p0 = (ax+t0*dx, ay+t0*dy); p1 = (ax+t1*dx, ay+t1*dy)
        if not cur: cur = [p0]
        elif t0 > 0:
            if len(cur) > 1: out.append(cur)
            cur = [p0]
        cur.append(p1)
        if t1 < 1:
            out.append(cur); cur = []
    if len(cur) > 1: out.append(cur)
    return out

def _polys(geom):
    if geom['type'] == 'Polygon': return [geom['coordinates']]
    if geom['type'] == 'MultiPolygon': return geom['coordinates']
    return []

def _lines(geom):
    if geom['type'] == 'LineString': return [geom['coordinates']]
    if geom['type'] == 'MultiLineString': return geom['coordinates']
    return []

def _in_window(coords):
    xs = [c[0] for c in coords]; ys = [c[1] for c in coords]
    return max(xs) >= -45 and min(xs) <= 80 and max(ys) >= 20 and min(ys) <= 85

def polygons(name, min_area, simplify=True):
    """-> list of polygons, each a list of rings (first = exterior), viewBox units, open rings."""
    res = []
    for ft in load(name):
        for poly in _polys(ft['geometry']):
            if not _in_window(poly[0]): continue
            rings = []
            for k, r in enumerate(poly):
                pr = [project(lo, la) for lo, la in r]
                pr = clip_poly(pr, -PADC, -PADC, W+PADC, H+PADC)
                if len(pr) < 3: 
                    if k == 0: break
                    continue
                pr = pr + [pr[0]]
                if simplify: pr = dp(pr, EPS)
                pr = quant(pr)
                if pr[0] != pr[-1]: pr.append(pr[0])
                if len(pr) < 4 or abs(area(pr)) < min_area:
                    if k == 0: break
                    continue
                rings.append(pr[:-1])
            if rings: res.append(rings)
    return res

def lines(name, keep=None, min_len=MIN_LINE):
    """-> list of open polylines (viewBox units). keep(properties) -> bool filters features."""
    res = []
    for ft in load(name):
        if keep and not keep(ft['properties']): continue
        for ln in _lines(ft['geometry']):
            if not _in_window(ln): continue
            pr = [project(lo, la) for lo, la in ln]
            for seg in clip_line(pr, -PADC, -PADC, W+PADC, H+PADC):
                seg = quant(dp(seg, EPS))
                if len(seg) >= 2:
                    L = sum(((seg[i+1][0]-seg[i][0])**2+(seg[i+1][1]-seg[i][1])**2)**.5 for i in range(len(seg)-1))
                    if L >= min_len: res.append(seg)
    return res

def f1(v):
    s = '%.1f' % v
    if s.endswith('.0'): s = s[:-2]
    if s == '-0': s = '0'
    return s

def path_d(rings, close=True):
    parts = []
    for r in rings:
        parts.append('M' + ' '.join(f1(x)+','+f1(y) for x, y in r) + ('Z' if close else ''))
    return ''.join(parts)
