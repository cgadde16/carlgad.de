// Base camp (/about/): what each object in the tent stands for, and the note it shows.
// The drawing and the hotspot positions come from scripts/camp/tent.py.

export type CampKey = 'who' | 'now' | 'route' | 'lang' | 'photo' | 'coffee' | 'bike';

/** Object name: tag under the object, button label and the kicker on the note. */
export const objects: Record<CampKey, string> = {
  who: 'Journal',
  now: 'Laptop',
  route: 'Map',
  lang: 'Phrasebook',
  photo: 'Camera',
  coffee: 'Coffee',
  bike: 'Cycling jersey',
};

export interface CampFact {
  title: string;
  /** Dot colour: activity colours as on Tours, ink for the rest. */
  c: string;
  text: string;
  /** Optional second line under a dashed rule. */
  more?: string;
}

// [Square brackets] mark text still to be filled in.
export const facts: Record<CampKey, CampFact> = {
  who: {
    title: 'Who I am',
    c: '#14171a',
    text: "Hi, I'm Carl. I finished my bachelor's in Cyber Security at the University of Bonn and now study Informatics at TUM in Munich. Alongside, I work as a student assistant at Fraunhofer FKIE.",
    more: 'Feel free to click around here.',
  },
  now: {
    title: 'Currently',
    c: '#C2410C',
    text: 'Reconstructing events from Kerberos-encrypted NFS traffic at Fraunhofer FKIE, with a publication planned. Next to it, the first semester at TUM. And what probably takes most of my time: planning the route for the next bicycle tour.',
  },
  route: {
    title: 'Tours I still talk about',
    c: '#5d646a',
    // one tour per line (.text keeps line breaks: white-space pre-line)
    text: 'Liked most: Around Europe on the motorbike, 39 days and 12,000 km.\nMost exhausting: Bonn to Lörrach by bike, 450 km in 20 hours.\nMost reckless: Berlin to Venice by bike, over the Alps in January.',
  },
  lang: { title: 'Languages', c: '#4D7C0F', text: 'German (native), English (C1), French (B1), Italian (A2).' },
  photo: { title: 'From the tours', c: '#5d646a', text: 'Some of my favourite pictures from all the tours.' },
  coffee: { title: 'Just decoration', c: '#14171a', text: "I don't really like coffee." },
  bike: {
    title: 'Help wanted',
    c: '#1E3A8A',
    text: "This is probably the biggest problem I'm currently facing: finding a good design for our cycling shirts. If you have any ideas, hit me up.",
  },
};

/** Shown as a stack on the left wall while the camera's note is open. Files go in public/photos/ (4:3 works best).
 */
export const photos: { src: string; caption: string }[] = [
  { src: '/photos/meteora.jpg', caption: 'Meteora, Greece' },
  { src: '/photos/umbrella-street.jpg', caption: 'Timișoara, Romania' },
  { src: '/photos/trolltunga.jpg', caption: 'Trolltunga, Norway' },
  { src: '/photos/coast.jpg', caption: 'Bilbao, Spain' }, // frame from a video
  { src: '/photos/snow-ride.jpg', caption: 'Achensee, Austria' }, // frame from a video
];

export const initialFact: CampKey = 'who';
