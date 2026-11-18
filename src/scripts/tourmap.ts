// Pan and zoom for TourMap (src/components/passes/TourMap.astro) by moving the SVG viewBox.
// The view starts fitted to the visible routes and refits (animated) on a 'tourmap:refit' event,
// e.g. after the notebook hides an activity. Wheel, drag, pinch, double-click, the +/-/fit buttons
// and the keyboard (when the map has focus: + - 0 and the arrow keys) all move it.

// The fit math lives in tourmap-fit.js, which Notebook.astro also inlines to fit the maps before first paint.
import { tmAspect, tmClamp, tmFitView, tmFrame, tmMaxView, tmSetView, tmDeclutter, tmSyncCasings } from './tourmap-fit.js';

type VB = { x: number; y: number; w: number; h: number };
const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

class TourMap {
  el: HTMLElement;
  svg: SVGSVGElement;
  W: number;
  H: number;
  vb: VB;
  touched = false; // the visitor moved the map: resizes keep their view instead of refitting
  anim = 0;
  pointers = new Map<number, { x: number; y: number }>();
  pinchDist = 0;
  declutterTimer = 0;
  tip: HTMLElement;
  hovered: SVGGElement | null = null;
  downAt: { x: number; y: number } | null = null; // where a touch/pen press started, to tell a tap from a pan

  constructor(el: HTMLElement) {
    this.el = el;
    this.svg = el.querySelector('svg.tm-svg')!;
    [this.W, this.H] = tmFrame(this.svg);
    this.vb = { x: 0, y: 0, w: this.W, h: this.H };

    new ResizeObserver(() => this.onResize()).observe(el);
    el.addEventListener('tourmap:refit', () => {
      this.touched = false;
      this.animateTo(this.fitView());
    });
    el.querySelectorAll<HTMLButtonElement>('[data-zoom]').forEach((b) =>
      b.addEventListener('click', () => {
        const z = b.dataset.zoom;
        if (z === 'fit') {
          this.touched = false;
          this.animateTo(this.fitView());
        } else this.zoomBy(z === 'in' ? 1 / 1.6 : 1.6, null, true);
      }),
    );
    this.tip = el.querySelector('.tm-tip')!;
    this.bindPointer();
    this.bindKeys();
    this.bindHover();
  }

  /** Show the info card for a route (always in the map's top-left corner, see .tm-tip), or hide it (route = null). */
  showTip(route: SVGGElement | null) {
    if (route !== this.hovered) {
      this.hovered?.classList.remove('is-hover');
      this.hovered = route;
      this.el.classList.toggle('has-hover', !!route);
      if (!route) {
        tmSyncCasings(this.el);
        this.tip.hidden = true;
        return;
      }
      route.classList.add('is-hover');
      tmSyncCasings(this.el);
      this.tip.style.setProperty('--c', route.style.getPropertyValue('--c'));
      this.tip.querySelector('.tm-tip-title')!.textContent = route.dataset.title ?? '';
      this.tip.querySelector('.tm-tip-meta')!.textContent = route.dataset.meta ?? '';
      this.tip.hidden = false;
    }
  }

  routeAt(target: EventTarget | null) {
    const hit = (target as Element | null)?.closest?.('.tm-hit');
    const route = hit?.closest<SVGGElement>('.tm-route');
    return route && !route.classList.contains('is-hidden') ? route : null;
  }

  bindHover() {
    const svg = this.svg;
    // mouse: hover; touch and pen: a tap on a route shows its card, a tap elsewhere hides it
    svg.addEventListener('pointermove', (e) => {
      if (e.pointerType !== 'mouse') {
        const d = this.downAt;
        if (d && Math.hypot(e.clientX - d.x, e.clientY - d.y) > 8) this.showTip(null); // panning
        return;
      }
      if (this.pointers.size) return this.showTip(null); // dragging
      this.showTip(this.routeAt(e.target));
    });
    svg.addEventListener('pointerleave', (e) => {
      if (e.pointerType === 'mouse') this.showTip(null);
    });
    svg.addEventListener('pointerdown', (e) => {
      this.downAt = e.pointerType === 'mouse' ? null : { x: e.clientX, y: e.clientY };
      if (e.pointerType === 'mouse') this.showTip(null);
    });
    svg.addEventListener('pointerup', (e) => {
      if (e.pointerType === 'mouse') {
        // pointer capture during the drag retargets events to the svg, so look up what is under the pointer
        const under = document.elementFromPoint(e.clientX, e.clientY);
        return this.showTip(this.routeAt(under));
      }
      const d = this.downAt;
      this.downAt = null;
      if (!d || Math.hypot(e.clientX - d.x, e.clientY - d.y) > 8) return;
      const under = document.elementFromPoint(e.clientX, e.clientY);
      this.showTip(this.routeAt(under));
    });
  }

  aspect() {
    return tmAspect(this.svg, this.W, this.H);
  }

  /** Smallest view showing the whole frame (contain). */
  maxView(aspect: number): VB {
    return tmMaxView(this.W, this.H, aspect);
  }

  /** View fitted to the visible routes, or the whole frame if none are visible. */
  fitView(): VB {
    return tmFitView(this.el);
  }

  clamp(v: VB): VB {
    return tmClamp(v, this.W, this.H);
  }

  apply(v: VB) {
    this.vb = v;
    tmSetView(this.el, this.svg, v);
    if (this.hovered) this.showTip(null); // the route may have moved away from the pointer; the next pointer move brings it back
    clearTimeout(this.declutterTimer);
    this.declutterTimer = window.setTimeout(() => this.declutter(), 90);
  }

  /** Hide stop names that would overlap one already shown: the first and last stop win, then route order. */
  declutter() {
    tmDeclutter(this.svg);
  }

  animateTo(target: VB, ms = 650) {
    cancelAnimationFrame(this.anim);
    if (reducedMotion()) return this.apply(target);
    const from = { ...this.vb };
    // zoom in log space so large zoom changes feel even
    const lw0 = Math.log(from.w);
    const lw1 = Math.log(target.w);
    const cx0 = from.x + from.w / 2;
    const cy0 = from.y + from.h / 2;
    const cx1 = target.x + target.w / 2;
    const cy1 = target.y + target.h / 2;
    const aspect = target.w / target.h;
    const t0 = performance.now();
    const step = (now: number) => {
      const t = Math.min(1, (now - t0) / ms);
      const e = t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
      const w = Math.exp(lw0 + (lw1 - lw0) * e);
      const cx = cx0 + (cx1 - cx0) * e;
      const cy = cy0 + (cy1 - cy0) * e;
      this.apply({ x: cx - w / 2, y: cy - w / aspect / 2, w, h: w / aspect });
      if (t < 1) this.anim = requestAnimationFrame(step);
    };
    this.anim = requestAnimationFrame(step);
  }

  onResize() {
    const aspect = this.aspect();
    if (!this.touched) return this.apply(this.fitView());
    // keep centre and width, adapt height to the new shape
    const cx = this.vb.x + this.vb.w / 2;
    const cy = this.vb.y + this.vb.h / 2;
    const w = this.vb.w;
    this.apply(this.clamp({ x: cx - w / 2, y: cy - w / aspect / 2, w, h: w / aspect }));
  }

  /** Client point -> base-map units. */
  toMap(clientX: number, clientY: number) {
    const r = this.svg.getBoundingClientRect();
    return {
      x: this.vb.x + ((clientX - r.left) / r.width) * this.vb.w,
      y: this.vb.y + ((clientY - r.top) / r.height) * this.vb.h,
    };
  }

  /** Zoom by factor (<1 = in) around a client point, or the centre. */
  zoomBy(factor: number, at: { x: number; y: number } | null, animate = false) {
    this.touched = true;
    const v = this.vb;
    const p = at ? this.toMap(at.x, at.y) : { x: v.x + v.w / 2, y: v.y + v.h / 2 };
    const w = v.w * factor;
    const h = v.h * factor;
    const next = this.clamp({
      x: p.x - (p.x - v.x) * factor,
      y: p.y - (p.y - v.y) * factor,
      w,
      h,
    });
    if (animate) this.animateTo(next, 300);
    else {
      cancelAnimationFrame(this.anim);
      this.apply(next);
    }
  }

  panBy(dxPx: number, dyPx: number) {
    this.touched = true;
    const r = this.svg.getBoundingClientRect();
    const k = this.vb.w / (r.width || 1);
    cancelAnimationFrame(this.anim);
    this.apply(
      this.clamp({
        ...this.vb,
        x: this.vb.x - dxPx * k,
        y: this.vb.y - dyPx * k,
      }),
    );
  }

  bindPointer() {
    const svg = this.svg;
    svg.addEventListener(
      'wheel',
      (e) => {
        e.preventDefault();
        const dy = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
        this.zoomBy(Math.exp(Math.max(-1, Math.min(1, dy / 300))), {
          x: e.clientX,
          y: e.clientY,
        });
      },
      { passive: false },
    );
    svg.addEventListener('dblclick', (e) => this.zoomBy(e.shiftKey ? 2 : 0.5, { x: e.clientX, y: e.clientY }, true));
    svg.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      svg.setPointerCapture(e.pointerId);
      this.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      this.pinchDist = 0;
    });
    svg.addEventListener('pointermove', (e) => {
      const prev = this.pointers.get(e.pointerId);
      if (!prev) return;
      const cur = { x: e.clientX, y: e.clientY };
      if (this.pointers.size === 1) {
        this.panBy(cur.x - prev.x, cur.y - prev.y);
      } else if (this.pointers.size === 2) {
        this.pointers.set(e.pointerId, cur);
        const [a, b] = [...this.pointers.values()];
        const dist = Math.hypot(a.x - b.x, a.y - b.y);
        if (this.pinchDist)
          this.zoomBy(this.pinchDist / dist, {
            x: (a.x + b.x) / 2,
            y: (a.y + b.y) / 2,
          });
        this.pinchDist = dist;
      }
      this.pointers.set(e.pointerId, cur);
    });
    const end = (e: PointerEvent) => {
      this.pointers.delete(e.pointerId);
      this.pinchDist = 0;
    };
    svg.addEventListener('pointerup', end);
    svg.addEventListener('pointercancel', end);
  }

  bindKeys() {
    this.svg.addEventListener('keydown', (e) => {
      const step = 60;
      const keys: Record<string, () => void> = {
        '+': () => this.zoomBy(1 / 1.6, null, true),
        '=': () => this.zoomBy(1 / 1.6, null, true),
        '-': () => this.zoomBy(1.6, null, true),
        '0': () => {
          this.touched = false;
          this.animateTo(this.fitView());
        },
        ArrowLeft: () => this.panBy(step, 0),
        ArrowRight: () => this.panBy(-step, 0),
        ArrowUp: () => this.panBy(0, step),
        ArrowDown: () => this.panBy(0, -step),
      };
      const fn = keys[e.key];
      if (fn && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        e.stopPropagation(); // don't also turn the notebook page
        fn();
      }
    });
  }
}

export function initTourMaps() {
  document.querySelectorAll<HTMLElement>('[data-tourmap]').forEach((el) => {
    if (el.dataset.ready) return;
    el.dataset.ready = '1';
    new TourMap(el);
  });
}
