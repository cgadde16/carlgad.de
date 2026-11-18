// Page turning for the Tours notebook (src/components/passes/Notebook.astro) and the activity stamps.
// Spread k shows leaves 0..k-1 turned. The URL hash names the open spread (#overview, #todo), so a
// spread can be linked and the back button works. Arrow keys turn pages unless a map has focus.

const STAGGER = 140; // ms between leaves when jumping several pages

export function initNotebook() {
  const nb = document.querySelector<HTMLElement>('[data-notebook]');
  if (!nb || nb.dataset.ready) return;
  nb.dataset.ready = '1';

  const ids: string[] = JSON.parse(nb.dataset.spreads ?? '[]');
  // data-turning="off" on the notebook: stay on the first spread, ignore corners, arrow keys, links and the hash
  const turning = nb.dataset.turning !== 'off';
  const leaves = [...nb.querySelectorAll<HTMLElement>('.nb-leaf')];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const stacked = window.matchMedia('(max-width: 959px)');
  let cur = 0;
  let timers: number[] = [];

  // Unturned leaves lie in reverse order (first on top), turned ones in order (last turned on top).
  const restack = (moving?: HTMLElement) =>
    leaves.forEach((leaf, i) => {
      const turned = leaf.classList.contains('is-turned');
      leaf.style.zIndex = leaf === moving ? String(leaves.length + 10) : String(turned ? i + 1 : leaves.length - i);
    });

  const turnLeaf = (leaf: HTMLElement, turned: boolean) => {
    if (leaf.classList.contains('is-turned') === turned) return;
    leaf.classList.add('is-moving');
    restack(leaf);
    leaf.classList.toggle('is-turned', turned);
    // the faces' shading transitions bubble up too: wait for the leaf's own transform
    let fallback = 0;
    const done = () => {
      clearTimeout(fallback);
      leaf.removeEventListener('transitionend', onEnd);
      leaf.classList.remove('is-moving');
      restack();
    };
    const onEnd = (e: TransitionEvent) => {
      if (e.target === leaf && e.propertyName === 'transform') done();
    };
    if (reduced) done();
    else {
      leaf.addEventListener('transitionend', onEnd);
      fallback = window.setTimeout(done, 1500);
    }
  };

  // Faces that are not showing must not be reachable with Tab.
  const updateInert = () => {
    leaves.forEach((leaf, i) => {
      const front = leaf.querySelector<HTMLElement>('.nb-front')!;
      const back = leaf.querySelector<HTMLElement>('.nb-back')!;
      if (stacked.matches) {
        front.inert = false;
        back.inert = false;
      } else {
        front.inert = i !== cur; // leaf cur's front is the open right page
        back.inert = i !== cur - 1; // leaf cur-1's back is the open left page
      }
    });
    const base = nb.querySelectorAll<HTMLElement>('.nb-base');
    if (!stacked.matches) {
      base[0].inert = cur !== 0;
      base[1].inert = cur !== leaves.length;
    } else base.forEach((b) => (b.inert = false));
  };

  const show = (k: number, updateHash = true) => {
    if (!turning) return;
    k = Math.max(0, Math.min(leaves.length, k));
    timers.forEach(clearTimeout);
    timers = [];
    const forward = k > cur;
    const order = forward ? leaves.slice(cur, k) : leaves.slice(k, cur).reverse();
    order.forEach((leaf, n) => {
      const run = () => turnLeaf(leaf, forward);
      if (n === 0 || reduced) run();
      else timers.push(window.setTimeout(run, n * STAGGER));
    });
    cur = k;
    updateInert();
    if (updateHash) history.replaceState(null, '', k === 0 ? location.pathname : `#${ids[k]}`);
  };

  const fromHash = () => {
    const k = ids.indexOf(decodeURIComponent(location.hash.slice(1)));
    return k < 0 ? 0 : k;
  };

  nb.addEventListener('click', (e) => {
    const t = (e.target as Element).closest<HTMLElement>('[data-turn], [data-goto]');
    if (!t) return;
    e.preventDefault();
    if (!turning) return;
    if (t.dataset.turn) show(cur + (t.dataset.turn === 'next' ? 1 : -1));
    else {
      const k = ids.indexOf(t.dataset.goto ?? '');
      if (stacked.matches) document.getElementById(`page-${ids[k]}`)?.scrollIntoView({ behavior: 'smooth' });
      else show(k);
    }
  });

  document.addEventListener('keydown', (e) => {
    if (stacked.matches || e.altKey || e.ctrlKey || e.metaKey) return;
    if ((e.target as Element).closest?.('input, textarea, [data-tourmap]')) return;
    if (e.key === 'ArrowRight') show(cur + 1);
    else if (e.key === 'ArrowLeft') show(cur - 1);
  });
  window.addEventListener('hashchange', () => show(fromHash(), false));
  stacked.addEventListener('change', updateInert);

  // Activity stamps: hide that activity's routes on the overview map, refit it, update the km total.
  const overview = nb.querySelector<HTMLElement>('.nb-overview-map');
  const total = nb.querySelector<HTMLElement>('[data-total]');
  nb.querySelectorAll<HTMLButtonElement>('.stamp[data-activity]').forEach((stamp) =>
    stamp.addEventListener('click', () => {
      const a = stamp.dataset.activity!;
      const on = stamp.getAttribute('aria-pressed') !== 'true';
      stamp.setAttribute('aria-pressed', String(on));
      overview?.querySelectorAll(`.tm-route[data-activity="${a}"]`).forEach((g) => g.classList.toggle('is-hidden', !on));
      overview?.dispatchEvent(new CustomEvent('tourmap:refit'));
      if (total) {
        let sum = 0;
        nb.querySelectorAll<HTMLElement>('.stamp[data-activity][aria-pressed="true"]').forEach((s) => {
          sum += Number(s.dataset.km ?? 0);
        });
        total.textContent = sum.toLocaleString('en-US');
      }
    }),
  );
  // start on the spread named in the URL, without animating there
  const start = turning ? fromHash() : 0;
  nb.classList.add('no-anim');
  leaves.forEach((leaf, i) => leaf.classList.toggle('is-turned', i < start));
  cur = start;
  restack();
  if (turning) show(start, false);
  else updateInert();
  requestAnimationFrame(() => requestAnimationFrame(() => nb.classList.remove('no-anim')));
}
