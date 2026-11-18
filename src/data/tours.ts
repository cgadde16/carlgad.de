// Tours for the Tours page (/tours/), the notebook: one entry per tour, all drawn on the overview map and counted
// in its stamps. Subtitle, notes and stops are kept for tour pages that may come back (the per-tour spreads were removed).
//
// A track is either a GPX file in src/data/tours/ (`{ gpx: 'name.gpx' }`, distance computed from it)
// or hand-placed points (`{ parts: [[lon, lat], ...][] }`, drawn as smooth curves; several parts for
// gaps such as a ferry). Ferries are drawn dotted and are not part of the track.

export type Activity = 'moto' | 'bike' | 'hike' | 'ski';
export type LonLat = [number, number];

export interface ActivityInfo {
  label: string;
  /** Route and stamp colour. */
  color: string;
  /** Dash pattern for the route line in CSS px, or empty for a solid line. */
  dash: string;
  /** File name in src/components/passes/icons/ (without .svg). */
  icon: 'motorcycle' | 'bicycle' | 'hiking' | 'skiing';
}

// Colours differ in lightness as well as hue. All lines are solid (dash patterns were dropped on purpose).
export const activities: Record<Activity, ActivityInfo> = {
  moto: { label: 'Motorcycle', color: '#C2410C', dash: '', icon: 'motorcycle' },
  bike: { label: 'Bicycle', color: '#1E3A8A', dash: '', icon: 'bicycle' },
  hike: { label: 'Hiking', color: '#4D7C0F', dash: '', icon: 'hiking' },
  ski: { label: 'Skiing', color: '#0891B2', dash: '', icon: 'skiing' },
};

export const activityOrder: Activity[] = ['moto', 'bike', 'hike', 'ski'];

/** Activities without a tour yet: their stamp still shows, with this line instead of the km. */
/** "Next up" line at the bottom of the overview page. One entry per line; leave text empty to hide it. */
export const nextUp = { text: ['first ski tour this winter &', 'Berlin – Bratislava by bicycle'] };

export const upcoming: Partial<Record<Activity, string>> = { ski: 'First tour this winter' };

export interface Stop {
  name: string;
  at: LonLat;
}

export interface Tour {
  /** Used in the URL: /tours/#<id> opens this tour's spread. */
  id: string;
  activity: Activity;
  title: string;
  subtitle: string;
  when: string;
  /** Free text shown on the map's hover card, e.g. '12 days' or '24 h'. */
  duration?: string;
  /** Overrides the distance computed from the track (km). */
  km?: number;
  notes: string[];
  track: { gpx: string } | { parts: LonLat[][] };
  ferries?: LonLat[][];
  stops: Stop[];
}


const NOTES = ['[A few sentences about this tour: why I went, the best day, what went wrong.]'];

const s = (name: string, lon: number, lat: number): Stop => ({ name, at: [lon, lat] });

const europeStops = [
  s('Bonn', 7.1, 50.735), s('Brussels', 4.352, 50.847), s('Paris', 2.349, 48.857), s('Bordeaux', -0.58, 44.838),
  s('Bilbao', -2.935, 43.263), s('Madrid', -3.703, 40.417), s('Valencia', -0.376, 39.47), s('Barcelona', 2.17, 41.39),
  s('Montpellier', 3.877, 43.611), s('Turin', 7.68, 45.07), s('Venice', 12.32, 45.44), s('Trieste', 13.776, 45.65),
  s('Ljubljana', 14.506, 46.051), s('Zadar', 15.231, 44.119), s('Dubrovnik', 18.094, 42.65), s('Kotor', 18.771, 42.425),
  s('Budva', 18.84, 42.287), s('Tirana', 19.819, 41.328), s('Meteora', 21.63, 39.72), s('Athens', 23.727, 37.984),
  s('Thessaloniki', 22.944, 40.64), s('Sofia', 23.322, 42.698), s('Pristina', 21.166, 42.663), s('Sarajevo', 18.413, 43.856),
  s('Belgrade', 20.457, 44.817), s('Timișoara', 21.227, 45.754), s('Budapest', 19.04, 47.498), s('Košice', 21.258, 48.717),
  s('Kraków', 19.945, 50.065), s('Vienna', 16.373, 48.208), s('Prague', 14.421, 50.088), s('Weimar', 11.329, 50.979),
  s('Bonn', 7.1, 50.735),
];
const bikeStops = [
  s('Bonn', 7.1, 50.735), s('Koblenz', 7.59, 50.355), s('Bingen', 7.9, 49.965), s('Landau', 8.12, 49.2),
  s('Strasbourg', 7.75, 48.58), s('Neuf-Brisach', 7.53, 48.03), s('Lörrach', 7.665, 47.615),
];
const berlinVeniceStops = [
  s('Berlin', 13.4, 52.52), s('Jena', 11.59, 50.93), s('Regensburg', 12.1, 49.02), s('Innsbruck', 11.4, 47.27),
  s('Venice', 12.32, 45.44),
];
const berlinLoerrachStops = [
  s('Berlin', 13.4, 52.52), s('Jena', 11.59, 50.93), s('Würzburg', 9.93, 49.79), s('Karlsruhe', 8.4, 49.01),
  s('Lörrach', 7.665, 47.615),
];
const swinoujscieStops = [s('Berlin', 13.4, 52.52), s('Schwedt', 14.283, 53.06), s('Świnoujście', 14.247, 53.91)];
const veronaLoerrachStops = [
  s('Verona', 10.99, 45.44), s('Parma', 10.33, 44.8), s('Rapallo', 9.23, 44.35), s('Genoa', 8.93, 44.41),
  s('Milan', 9.19, 45.46), s('Zurich', 8.54, 47.37), s('Lörrach', 7.665, 47.615),
];
const loerrachLuganoStops = [
  s('Lörrach', 7.665, 47.615), s('Basel', 7.59, 47.56), s('Lucerne', 8.31, 47.05), s('Gotthard Pass', 8.57, 46.56),
  s('Bellinzona', 9.02, 46.19), s('Lugano', 8.95, 46.0),
];
const bonnMonacoStops = [
  s('Bonn', 7.1, 50.735), s('Basel', 7.59, 47.56), s('Kandersteg', 7.675, 46.495), s('Turin', 7.68, 45.07),
  s('Monaco', 7.42, 43.74),
];
const olavStops = [
  s('Oslo', 10.768, 59.906), s('Granavollen', 10.53, 60.368), s('Gjøvik', 10.686, 60.797),
];
const blegiStops = [s('Luchsingen', 9.037, 46.967), s('Oberblegisee', 9.014, 46.98), s('Schattenstock', 8.965, 46.952)];
const oeschinenStops = [s('Kandersteg', 7.676, 46.498), s('Oeschinensee', 7.715, 46.498), s('Blüemlisalphütte', 7.772, 46.51)];
const trolltungaStops = [s('Tyssedal', 6.557, 60.117), s('Skjeggedal', 6.627, 60.133), s('Trolltunga', 6.754, 60.133)];

export const tours: Tour[] = [
  {
    id: 'around-europe',
    activity: 'moto',
    title: 'Around Europe',
    subtitle: 'a loop from Bonn: Paris and the Atlantic, across Spain, down the Adriatic to Athens, back north through the Balkans and Central Europe',
    when: 'June 2026',
    duration: '39 days', // 28 May to 5 July 2026
    km: 12187.4, // as ridden; the drawn GPX measures differently
    notes: NOTES,
    track: { gpx: 'around-europe.gpx' },
    stops: europeStops,
  },
  {
    id: 'bonn-monaco',
    activity: 'moto',
    title: 'Bonn to Monaco and back',
    subtitle: 'by train through the Lötschberg, over the Simplon and the Col de Tende',
    when: 'April 2023',
    duration: '5 days',
    km: 2324, // measured on the full-resolution GPX before thinning (both ways, without the car train)
    notes: NOTES,
    track: { gpx: 'bonn-monaco.gpx' },
    ferries: [[[7.675, 46.495], [7.755, 46.37]]], // Lötschberg car train, Kandersteg to Goppenstein
    stops: bonnMonacoStops,
  },
  {
    id: 'bonn-loerrach',
    activity: 'bike',
    title: 'Bonn to Lörrach',
    subtitle: 'down the Rhine valley in one go: left bank to Bingen, south through the Palatinate, then the French side',
    when: 'July 2026',
    duration: '20 h',
    km: 450, // as ridden; the drawn GPX measures a bit more
    notes: NOTES,
    track: { gpx: 'bonn-loerrach.gpx' },
    stops: bikeStops,
  },
  {
    id: 'berlin-venice',
    activity: 'bike',
    title: 'Berlin to Venice',
    subtitle: 'via Jena, Regensburg and the Brenner, in winter',
    when: 'January 2026',
    duration: '5 days',
    km: 1092, // as ridden: 22 + 330 + 160 + 105 + 269 + 206; the drawn GPX measures a bit more
    notes: NOTES,
    track: { gpx: 'berlin-venice.gpx' },
    stops: berlinVeniceStops,
  },
  {
    id: 'berlin-loerrach',
    activity: 'bike',
    title: 'Berlin to Lörrach',
    subtitle: 'via Jena, Würzburg and Karlsruhe',
    when: 'June 2025',
    duration: '4 days',
    km: 832, // as ridden; the drawn GPX measures a bit more
    notes: NOTES,
    track: { gpx: 'berlin-loerrach.gpx' },
    stops: berlinLoerrachStops,
  },
  {
    id: 'berlin-swinoujscie',
    activity: 'bike',
    title: 'Berlin to Świnoujście',
    subtitle: 'north to the Oder at Schwedt and down the river to the Baltic',
    when: 'May 2025',
    duration: '3 days',
    km: 282, // drawn line, measured before thinning; the real route is only known as far as Schwedt
    notes: NOTES,
    track: { gpx: 'berlin-swinoujscie.gpx' },
    stops: swinoujscieStops,
  },
  {
    id: 'verona-loerrach',
    activity: 'bike',
    title: 'Verona to Lörrach',
    subtitle: 'via Parma, Rapallo, Genoa, Milan and Zurich',
    when: 'September 2026',
    duration: '4 days',
    km: 500, // as ridden; some stretches were by train, the drawn line is continuous
    notes: NOTES,
    track: { gpx: 'verona-loerrach.gpx' },
    stops: veronaLoerrachStops,
  },
  {
    id: 'loerrach-lugano',
    activity: 'bike',
    title: 'Lörrach to Lugano',
    subtitle: 'via Basel, Lucerne and the Gotthard',
    when: 'August 2025',
    duration: '2 days',
    km: 314, // measured on the full-resolution GPX before thinning
    notes: NOTES,
    track: { gpx: 'loerrach-lugano.gpx' },
    stops: loerrachLuganoStops,
  },
  {
    id: 'oslo-gjovik',
    activity: 'hike',
    title: 'Oslo to Gjøvik',
    subtitle: 'the first stretch of the St. Olav Way to Trondheim: over Krokskogen, past Granavollen and through Toten to Lake Mjøsa',
    when: 'August 2025',
    duration: '6 days',
    km: 190, // estimated: 43k steps/day x 6 days x ~0.73 m (the official trail line measures 176)
    notes: NOTES,
    track: { gpx: 'oslo-gjovik.gpx' },
    stops: olavStops,
  },
  {
    id: 'tyssedal-trolltunga',
    activity: 'hike',
    title: 'Tyssedal to Trolltunga and back',
    subtitle: 'up from the Sørfjord past Skjeggedal to the rock above Ringedalsvatnet, with a night on the way',
    when: 'August 2026',
    duration: '2 days',
    km: 42, // as walked, there and back; the GPX draws one way (19.5 km)
    notes: NOTES,
    track: { gpx: 'tyssedal-trolltunga.gpx' },
    stops: trolltungaStops,
  },
  {
    id: 'luchsingen-oberblegisee',
    activity: 'hike',
    title: 'Luchsingen to Oberblegisee and back',
    subtitle: 'up from the Linth valley to the lake, then on to a night out on the ridge below the Schattenstock',
    when: 'July 2026',
    duration: '2 days',
    km: 23, // drawn line, there and back (11.6 km each way); the GPX draws one way
    notes: NOTES,
    track: { gpx: 'luchsingen-oberblegisee.gpx' },
    stops: blegiStops,
  },
  {
    id: 'kandersteg-bluemlisalp',
    activity: 'hike',
    title: 'Kandersteg to the Blüemlisalphütte and back',
    subtitle: 'past Oeschinensee and up the Hohtürli to the hut at 2,840 m, a night there and down the same way',
    when: 'August 2025',
    duration: '2 days',
    km: 23, // drawn line, there and back (11.5 km each way); the GPX draws one way
    notes: NOTES,
    track: { gpx: 'kandersteg-bluemlisalp.gpx' },
    stops: oeschinenStops,
  },
];
