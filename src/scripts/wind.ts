/*! Fog and wind streaks adapted from Marvin Gülhan's webpage, https://github.com/Marff16/webpage (CC BY 4.0). */
// One gusting wind (the same one the crows in Birds.astro fly on) drives fog puffs drifting along the
// ridges and faint streaks in the sky. Everything lives in MountainScene's <svg>, in its 1440x810 scene
// units: the fog sits between the ridge layers, so it never washes over the figures or the signs.

const NS = 'http://www.w3.org/2000/svg';
const SCENE_W = 1440;
// the ridges run on past the 1440 box for wide windows (MountainScene)
const RIDGE_X0 = -1100;
const RIDGE_X1 = 2540;

// Wind strength at a given x and time. Evaluating it at (t - x / speed) makes each gust roll across
// from left to right instead of hitting everywhere at once.
function wind(x: number, t: number) {
  const p = t - x / 420;
  return 0.55 + 0.32 * Math.sin(p * 0.33) + 0.18 * Math.sin(p * 0.87 + 1.3) + 0.07 * Math.sin(p * 2.1 + 0.4);
}

const rand = (min: number, max: number) => min + Math.random() * (max - min);

// Height of a ridge's top edge for every 4 scene units of x, read off its path.
function ridgeTop(path: SVGPathElement) {
  const top = new Array<number>((RIDGE_X1 - RIDGE_X0) / 4 + 1).fill(Infinity);
  const len = path.getTotalLength();
  for (let s = 0; s <= len; s += 2) {
    const p = path.getPointAtLength(s);
    const i = Math.round((p.x - RIDGE_X0) / 4);
    if (i >= 0 && i < top.length && p.y < top[i]) top[i] = p.y;
  }
  return (x: number) => top[Math.max(0, Math.min(top.length - 1, Math.round((x - RIDGE_X0) / 4)))];
}

interface Puff { el: SVGEllipseElement; x: number; dy: number; rx: number; ry: number; speed: number }
interface Streak { el: SVGPathElement; x: number; y: number; length: number; amp: number; phase: number; speed: number; age: number; life: number }

export function startWind(svg: SVGSVGElement) {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const bands = [...svg.querySelectorAll<SVGGElement>('.fog')].map((g) => ({
    g,
    top: ridgeTop(svg.querySelector<SVGPathElement>(`.${g.dataset.ridge}`)!),
    puffs: [] as Puff[],
  }));
  const streakLayer = svg.querySelector<SVGGElement>('.streaks');

  // The part of the scene's x range that is on screen (wide windows show more than the 1440 box).
  function visibleX() {
    const ctm = svg.getScreenCTM();
    if (!ctm) return { x0: 0, x1: SCENE_W };
    const inv = ctm.inverse();
    const x0 = new DOMPoint(0, 0).matrixTransform(inv).x;
    const x1 = new DOMPoint(document.documentElement.clientWidth, 0).matrixTransform(inv).x;
    return { x0: Math.max(RIDGE_X0, x0), x1: Math.min(RIDGE_X1, x1) };
  }

  function makePuff(band: (typeof bands)[number], scattered: boolean, el?: SVGEllipseElement): Puff {
    const rx = rand(130, 280);
    if (!el) {
      el = document.createElementNS(NS, 'ellipse');
      el.setAttribute('rx', '1');
      el.setAttribute('ry', '1');
      el.setAttribute('fill', 'url(#fog-puff)');
      band.g.appendChild(el);
    }
    el.setAttribute('opacity', rand(0.2, 0.4).toFixed(2));
    // centred a little above the ridge's edge, so its upper half lies in the valley behind it
    const { x0, x1 } = visibleX();
    return { el, x: scattered ? rand(x0 - rx, x1 + rx) : x0 - rx, dy: rand(-16, 4), rx, ry: rx * rand(0.12, 0.22), speed: rand(4, 10) };
  }

  function placePuff(f: Puff, top: (x: number) => number) {
    f.el.setAttribute('transform', `translate(${f.x.toFixed(1)} ${(top(f.x) + f.dy).toFixed(1)}) scale(${f.rx.toFixed(1)} ${f.ry.toFixed(1)})`);
  }

  for (const band of bands) {
    // four puffs per 1440 units of visible ridge
    const vis = visibleX();
    const n = Math.max(4, Math.round((4 * (vis.x1 - vis.x0)) / SCENE_W));
    for (let i = 0; i < n; i++) band.puffs.push(makePuff(band, true));
    for (const f of band.puffs) placePuff(f, band.top);
  }
  if (reducedMotion || !streakLayer) return; // a still mist, no streaks

  // The part of the sky the streaks may use, in scene units: the visible top down to just above the back
  // ridge, minus the band the name and tagline occupy.
  function skyHeight(pad: number) {
    const ctm = svg.getScreenCTM();
    if (!ctm) return 200;
    const inv = ctm.inverse();
    const toScene = (y: number) => new DOMPoint(0, y).matrixTransform(inv).y;
    const visTop = Math.max(0, toScene(0));
    const min = visTop + 30;
    const max = Math.max(min + 40, Math.min(visTop + 0.55 * (810 - visTop), 470));
    let lo = Infinity;
    let hi = -Infinity;
    document.querySelectorAll('.title h1, .title .tagline').forEach((el) => {
      const r = el.getBoundingClientRect();
      lo = Math.min(lo, toScene(r.top) - pad);
      hi = Math.max(hi, toScene(r.bottom) + pad);
    });
    const above = Math.max(0, Math.min(max, lo) - min);
    const below = Math.max(0, max - Math.max(min, hi));
    if (above + below === 0) return min;
    const r = rand(0, above + below);
    return r < above ? min + r : Math.max(min, hi) + (r - above);
  }

  let streaks: Streak[] = [];
  let nextStreak = 0;

  function makeStreak(): Streak {
    const amp = rand(3, 7);
    const el = document.createElementNS(NS, 'path');
    streakLayer!.appendChild(el);
    const { x0, x1 } = visibleX();
    return { el, x: x0 + rand(-0.2, 0.6) * (x1 - x0), y: skyHeight(amp + 8), length: rand(90, 210), amp, phase: rand(0, Math.PI * 2), speed: rand(120, 200), age: 0, life: rand(2.5, 4) };
  }

  function drawStreak(s: Streak) {
    // fade in, hold, fade out over its life
    const k = s.age / s.life;
    const alpha = 0.18 * Math.min(1, k * 4, (1 - k) * 4);
    let d = '';
    for (let i = 0; i <= 24; i++) {
      const px = s.x - s.length + (s.length * i) / 24;
      const py = s.y + Math.sin(px / 52 + s.phase) * s.amp;
      d += `${i ? 'L' : 'M'}${px.toFixed(1)} ${py.toFixed(1)}`;
    }
    s.el.setAttribute('d', d);
    s.el.setAttribute('opacity', alpha.toFixed(3));
  }

  let last = performance.now();
  function frame(now: number) {
    const dt = Math.min(0.05, (now - last) / 1000); // no jumps after the tab was in the background
    last = now;
    const t = now / 1000;

    for (const band of bands) {
      band.puffs.forEach((f, i) => {
        f.x += f.speed * (0.4 + wind(f.x, t)) * dt;
        if (f.x - f.rx > visibleX().x1) band.puffs[i] = f = makePuff(band, false, f.el);
        placePuff(f, band.top);
      });
    }

    if (t > nextStreak) {
      streaks.push(makeStreak());
      // gusty moments bring streaks more often
      nextStreak = t + rand(1.5, 3.5) / Math.max(wind(SCENE_W / 2, t), 0.3);
    }
    streaks = streaks.filter((s) => {
      s.age += dt;
      if (s.age < s.life) return true;
      s.el.remove();
      return false;
    });
    for (const s of streaks) {
      s.x += s.speed * dt;
      drawStreak(s);
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
