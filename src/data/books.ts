// Library shelf (canvas Round 24, B2 "bookcase with a note card"). 
// Books stand grouped by genre, its name set into the shelf edge below the group. Cloth tones are mixed at random
// (fixed per book), so the case doesn't read as a ranking.

export type Genre = 'mtn' | 'road' | 'sci' | 'bio' | 'nat' | 'fic';

/** Cloth tones, light to dark; each book gets one picked from its id (random-looking, but the same on every load). */
export const tones = ['#f3eee4', '#e9e2d4', '#e2dacb', '#d9d0bf', '#d2c8b5', '#c9beaa', '#c2b7a1', '#b9ad96'];

export function toneFor(id: string): string {
  let h = 0;
  for (const ch of id) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return tones[h % tones.length];
}

/** Tones for a row of books: as toneFor, but never the same tone twice in a row. */
export function rowTones(books: { id: string }[]): string[] {
  const out: string[] = [];
  for (const b of books) {
    let t = toneFor(b.id);
    if (t === out.at(-1)) t = tones[(tones.indexOf(t) + 3) % tones.length];
    out.push(t);
  }
  return out;
}

export const genres: Record<Genre, { label: string }> = {
  mtn: { label: 'Mountains' },
  road: { label: 'Road & travel' },
  sci: { label: 'Science & computing' },
  bio: { label: 'Biography' },
  nat: { label: 'Nature' },
  fic: { label: 'Fiction' },
};

/** Which genres stand on which shelf, left to right (top shelf first). */
export const shelfGenres: Genre[][] = [
  ['sci', 'bio', 'road', 'nat'], // academic, Biography, Road & travel next to it (user, 2026-11-17), Nature
  ['mtn', 'fic'], // everything else
];

export interface Book {
  id: string;
  t: string;
  a: string;
  g: Genre;
  /** When it was read, shown on the note only (e.g. 'Oct 2026' or 'reading now'). */
  m: string;
  /** Spine width / height in px. */
  w: number;
  h: number;
  /** Shorter spine title, if the full one is too long. */
  short?: string;
  /** Author as printed on the spine, if not the surname(s) (e.g. a publisher or series). */
  spineA?: string;
  what: string;
}

/** All books, newest first (the page regroups them by genre, see shelfGenres). No year labels on the boards. */
export const shelves: Book[][] = [
  [
    { id: 'shortest-ai', t: 'The Shortest History of AI', a: 'Toby Walsh', g: 'sci', m: 'Nov 2026', w: 50, h: 300, what: 'Artificial intelligence from Turing and the first thinking machines to today’s large language models.' },
    { id: 'anyone-builds', t: 'If Anyone Builds It, Everyone Dies', a: 'Eliezer Yudkowsky & Nate Soares', g: 'sci', m: 'Oct 2026', w: 70, h: 300, what: 'The case that building superhuman AI with today’s methods would end humanity, and why the authors want it stopped worldwide.' },
    { id: 'knight', t: 'A Knight of the Seven Kingdoms', a: 'George R. R. Martin', g: 'fic', m: 'Jul 2026', w: 58, h: 330, what: 'Three novellas set a century before the main series: the hedge knight Ser Duncan the Tall and his squire Egg on the roads of Westeros.' },
    { id: 'moto-europa', t: 'Legendäre Motorradtouren in Europa', a: 'Lonely Planet', spineA: 'Lonely Planet', g: 'road', m: 'May 2026', w: 58, h: 324, short: 'Legendäre Motorradtouren', what: '40 motorcycle routes in Europe: big passes, quiet back roads, riders\u2019 stories and maps, with incredibly beautiful pictures.' },
    { id: 'asoiaf', t: 'A Song of Ice and Fire', a: 'George R. R. Martin', g: 'fic', m: 'Jan – May 2026', w: 92, h: 310, what: 'All five books so far: Westeros, the war for the Iron Throne, and winter coming. One spine for the whole series.' },
  ],
  [
    { id: 'sunrise', t: 'Sunrise on the Reaping', a: 'Suzanne Collins', g: 'fic', m: 'Dec 2025', w: 64, h: 286, what: 'The Hunger Games, 24 years earlier: the young Haymitch Abernathy in the second Quarter Quell.' },
    { id: 'babel', t: 'Babel', a: 'R. F. Kuang', g: 'fic', m: 'Dec 2025', w: 74, h: 290, what: 'Oxford in the 1830s, where translation powers the magic behind the British Empire, and a student who starts to turn against it.' },
    { id: 'rad-europa', t: 'Legendäre Radtouren in Europa', a: 'Lonely Planet', spineA: 'Lonely Planet', g: 'road', m: 'Oct 2025', w: 56, h: 316, short: 'Legendäre Radtouren', what: 'The 50 most exciting cycling routes across Europe, as an illustrated book. The bicycle counterpart to the motorcycle tours next to it.' },
    { id: 'picasso', t: 'Life with Picasso', a: 'Françoise Gilot', g: 'bio', m: 'Aug 2025', w: 66, h: 280, what: 'The painter Françoise Gilot on her ten years with Picasso in post-war France: his studio, his work and his temper.' },
    { id: 'turing', t: 'Computing Machinery and Intelligence', a: 'Alan Turing', g: 'sci', m: 'Jun 2025', w: 46, h: 270, what: 'Do I really need to write a description for this one?' },
    { id: 'verne', t: 'Journey to the Centre of the Earth', a: 'Jules Verne', g: 'fic', m: 'Apr 2025', w: 60, h: 284, what: 'A professor, his nephew and an Icelandic guide climb down an extinct volcano to find a whole world underground.' },
  ],
];

/** Books being read now: they lie flat on the top shelf, stacked, the first one at the bottom. Empty when none. */
export const readingNow: Book[] = [
  {
    id: 'ethische', t: 'Ethische Intelligenz', a: 'Markus Gabriel', g: 'sci', m: 'reading now', w: 200, h: 48,
    what: 'How AI could help us make moral progress, if it is built around people and shared values rather than big tech.',
  },
  {
    id: 'clearing-air', t: 'Clearing the Air', a: 'Hannah Ritchie', g: 'nat', m: 'reading now', w: 200, h: 48,
    what: 'Hannah Ritchie answers fifty common questions about climate change and its solutions, backed by data and hopeful about how much we can still do.',
  },
];

/** What the note card says before a book is hovered or picked. */
export const intro = {
  label: '',
  t: 'Library',
  what: "Here is what I've read recently. Sadly not everything fits on the shelf, so these are my favourites. I like reading academic books, but sometimes I need a break and go back to fantasy or sci-fi.",
};
