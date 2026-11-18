// View fitting for TourMap, shared by src/scripts/tourmap.ts (pan/zoom module) and an inline script in
// src/components/passes/Notebook.astro that fits every map before the first paint (module scripts run
// after it, so without that the maps flash the whole of Europe on load).
// Plain JS on purpose: Notebook.astro inlines this file's source (with `export ` stripped), so no
// TypeScript syntax and no imports here.

/** @typedef {{ x: number; y: number; w: number; h: number }} VB */

const PAD = 0.14; // margin around fitted routes, as a share of the route box
const MIN_FIT_W = { overview: 70, tour: 34 }; // smallest fitted view width (base-map units, ~3.5 km each)
const MIN_W = 18; // deepest zoom
const RESERVE_PX = 52; // strip on the right kept free of routes when fitting (zoom buttons)
const DOT_PX = 8; // a route whose longer side is shorter than this on screen is drawn as a dot (8: Oslo–Gjøvik stays a line zoomed out, even on phones)

/** @param {SVGSVGElement} svg @returns {[number, number]} */
export function tmFrame(svg) {
  const [w, h] = (svg.dataset.frame ?? '1000 1000').split(' ').map(Number);
  return [w, h];
}

/** @param {SVGSVGElement} svg @param {number} W @param {number} H */
export function tmAspect(svg, W, H) {
  const r = svg.getBoundingClientRect();
  return r.width > 0 && r.height > 0 ? r.width / r.height : W / H;
}

/** Smallest view showing the whole frame (contain). @returns {VB} */
export function tmMaxView(/** @type {number} */ W, /** @type {number} */ H, /** @type {number} */ aspect) {
  const w = Math.max(W, H * aspect);
  return { x: (W - w) / 2, y: (H - w / aspect) / 2, w, h: w / aspect };
}

/** @param {VB} v @param {number} W @param {number} H @returns {VB} */
export function tmClamp(v, W, H) {
  const aspect = v.w / v.h;
  const max = tmMaxView(W, H, aspect);
  const w = Math.min(Math.max(v.w, MIN_W), max.w);
  const h = w / aspect;
  let x = v.x + (v.w - w) / 2;
  let y = v.y + (v.h - h) / 2;
  // keep the view inside the frame; centre it where it is wider than the frame
  x = w >= W ? (W - w) / 2 : Math.min(Math.max(x, 0), W - w);
  y = h >= H ? (H - h) / 2 : Math.min(Math.max(y, 0), H - h);
  return { x, y, w, h };
}

/** View fitted to the visible routes, or the whole frame if none are visible. @param {HTMLElement} el @returns {VB} */
export function tmFitView(el) {
  const svg = /** @type {SVGSVGElement} */ (el.querySelector('svg.tm-svg'));
  const [W, H] = tmFrame(svg);
  const aspect = tmAspect(svg, W, H);
  const minFitW = MIN_FIT_W[el.dataset.variant === 'tour' ? 'tour' : 'overview'];
  const boxes = [...el.querySelectorAll('.tm-route:not(.is-hidden)')].map((g) =>
    ((/** @type {SVGGElement} */ (g)).dataset.bbox ?? '').split(' ').map(Number),
  );
  if (!boxes.length) return tmMaxView(W, H, aspect);
  let x0 = Math.min(...boxes.map((b) => b[0]));
  let y0 = Math.min(...boxes.map((b) => b[1]));
  let x1 = Math.max(...boxes.map((b) => b[2]));
  let y1 = Math.max(...boxes.map((b) => b[3]));
  const px = Math.max(x1 - x0, 8) * PAD;
  const py = Math.max(y1 - y0, 8) * PAD;
  x0 -= px;
  x1 += px;
  y0 -= py;
  y1 += py;
  // keep the routes clear of the zoom buttons on the right edge
  const r = svg.getBoundingClientRect();
  const share = r.width > 200 ? (r.width - RESERVE_PX) / r.width : 1;
  const wFit = Math.max(x1 - x0, (y1 - y0) * aspect * share, minFitW * share);
  const w = wFit / share;
  return tmClamp(
    {
      x: (x0 + x1) / 2 - wFit / 2,
      y: (y0 + y1) / 2 - w / aspect / 2,
      w,
      h: w / aspect,
    },
    W,
    H,
  );
}

/** Set a view: the viewBox plus --u (base-map units per CSS pixel, keeps markers and labels at screen size). */
export function tmSetView(/** @type {HTMLElement} */ el, /** @type {SVGSVGElement} */ svg, /** @type {VB} */ v) {
  svg.setAttribute('viewBox', `${v.x.toFixed(2)} ${v.y.toFixed(2)} ${v.w.toFixed(2)} ${v.h.toFixed(2)}`);
  const px = svg.getBoundingClientRect().width || 1;
  const u = v.w / px;
  el.style.setProperty('--u', u.toFixed(4));
  // routes shorter than DOT_PX on screen at this zoom are shown as a dot (overview map only)
  if (el.dataset.variant !== 'overview') return;
  el.querySelectorAll('.tm-route').forEach((g) => {
    const b = ((/** @type {SVGGElement} */ (g)).dataset.bbox ?? '').split(' ').map(Number);
    if (b.length === 4) g.classList.toggle('is-dot', Math.max(b[2] - b[0], b[3] - b[1]) / u < DOT_PX);
  });
  tmSyncCasings(el);
}

/** Casings sit in their own layer per activity (TourMap.astro): copy each route's state onto its casing. */
export function tmSyncCasings(/** @type {HTMLElement} */ el) {
  el.querySelectorAll('.tm-casing[data-for]').forEach((c) => {
    const r = el.querySelector(`.tm-route[data-id="${/** @type {SVGElement} */ (c).dataset.for}"]`);
    if (!r) return;
    for (const k of ['is-hidden', 'is-dot', 'is-hover']) c.classList.toggle(k, r.classList.contains(k));
  });
}

/** Hide stop labels that would overlap one already placed (end stops first). @param {SVGSVGElement} svg */
export function tmDeclutter(svg) {
  const labels = /** @type {SVGTextElement[]} */ ([...svg.querySelectorAll('.tm-route:not(.is-hidden) .tm-label')]);
  const box = svg.getBoundingClientRect();
  if (!labels.length || !box.width) return;
  const isEnd = (/** @type {SVGTextElement} */ l) => !!l.previousElementSibling?.classList.contains('tm-stop-end');
  const sorted = [...labels.filter(isEnd), ...labels.filter((l) => !isEnd(l))];
  /** @type {DOMRect[]} */
  const placed = [];
  for (const l of sorted) {
    const r = l.getBoundingClientRect();
    const hit = placed.some((p) => r.left < p.right + 6 && r.right > p.left - 6 && r.top < p.bottom + 2 && r.bottom > p.top - 2);
    l.style.visibility = hit ? 'hidden' : '';
    if (!hit) placed.push(r);
  }
}
