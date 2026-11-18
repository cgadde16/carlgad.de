"""Lambert azimuthal equal-area (spherical), centre 10E 52N, to viewBox units (width 1000)."""
import math
LON0, LAT0 = 10.0, 52.0
R = 6371.0088
_p0, _l0 = math.radians(LAT0), math.radians(LON0)
_s0, _c0 = math.sin(_p0), math.cos(_p0)

def raw(lon, lat):
    """-> (x_km, y_km) north-up."""
    p, l = math.radians(lat), math.radians(lon)
    dl = l - _l0
    k = math.sqrt(2 / (1 + _s0*math.sin(p) + _c0*math.cos(p)*math.cos(dl)))
    return (R*k*math.cos(p)*math.sin(dl),
            R*k*(_c0*math.sin(p) - _s0*math.cos(p)*math.cos(dl)))

def inv_raw(x, y):
    """numpy-capable inverse: km -> (lon, lat) degrees."""
    import numpy as np
    rho = np.hypot(x, y)
    c = 2*np.arcsin(np.clip(rho/(2*R), -1, 1))
    sc, cc = np.sin(c), np.cos(c)
    with np.errstate(invalid='ignore', divide='ignore'):
        lat = np.arcsin(np.clip(cc*_s0 + np.where(rho > 0, y*sc*_c0/np.where(rho > 0, rho, 1), 0), -1, 1))
        lon = _l0 + np.arctan2(x*sc, rho*_c0*cc - y*_s0*sc)
    return np.degrees(lon), np.degrees(lat)

FRAME_PTS = [(-9.5,38.8),(-9.0,37.0),(26.3,35.0),(25.8,71.2),(5.1,62.2),(29.0,41.0)]
_pts = [raw(*p) for p in FRAME_PTS]
_xs = [p[0] for p in _pts]; _ys = [p[1] for p in _pts]
_w = max(_xs)-min(_xs); _h = max(_ys)-min(_ys)
_pad = 0.04
X0, X1 = min(_xs)-_pad*_w, max(_xs)+_pad*_w
Y0, Y1 = min(_ys)-_pad*_h, max(_ys)+_pad*_h
SCALE = 1000.0/(X1-X0)          # viewBox units per km
W = 1000
H = int(round((Y1-Y0)*SCALE))
SCALE_Y = SCALE                 # equal scale both axes (H rounded; sub-unit difference ignored)

def project(lon, lat):
    x, y = raw(lon, lat)
    return ((x-X0)*SCALE, (Y1-y)*SCALE)

def unproject_grid(px, py):
    """numpy arrays of viewBox coords -> lon, lat degrees."""
    return inv_raw(px/SCALE + X0, Y1 - py/SCALE)

if __name__ == '__main__':
    print('W', W, 'H', H, 'km/unit', 1/SCALE)
    for p in FRAME_PTS: print(p, project(*p))
    print('Munich', project(11.58, 48.14))
