# Base map generator

Builds `src/data/basemap.json`: Europe in a Lambert azimuthal equal-area projection (centre 10E 52N, R = 6371.0088 km),
fitted to a 1000 x 1199 viewBox. The frame (`FRAME_PTS`, padding, W = 1000, H = 1199) is fixed in `proj.py`;
route coordinates elsewhere in the site depend on it, so do not change it.

JSON layout: `{W, H, proj:{lon0,lat0,R,X0,Y1,scale}, land, lakes, borders, rivers}`. `land`/`lakes` are closed
rings for `fill-rule="evenodd"`, `borders`/`rivers` are open polylines. To project a point yourself:
`x = (raw_x_km - X0) * scale`, `y = (Y1 - raw_y_km) * scale` (see `raw()` in `proj.py`).

Sources (Natural Earth 10m, `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/<name>.geojson`):
`ne_10m_land`, `ne_10m_lakes`, `ne_10m_admin_0_boundary_lines_land`, `ne_10m_rivers_lake_centerlines`
(rivers with `scalerank <= 7`, lake centerlines dropped). They are downloaded into `dl/` (git-ignored) if missing.

Run from the repo root (no dependencies besides Python 3):

    python3 -I scripts/basemap/build_basemap.py

Tuning knobs are at the top of `geo.py`: Douglas-Peucker `EPS` (viewBox units), `MIN_AREA` / `LAKE_MIN_AREA`,
`MIN_LINE`, and the clip margin `PADC`. Coordinates are written with 1 decimal.
