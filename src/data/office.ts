// Office page (canvas Round 29 A, "filing cabinet"): one drawer per topic, entries grouped by year
// (each in the year it ended, ongoing ones in the current year). Topic colours: OKLCH L 0.50, C 0.09, only the hue differs (Studies 255, Work 40, Projects 130, Publications 75, Clubs 200).

export type Topic = 'study' | 'work' | 'proj' | 'pub' | 'club';

export const topics: Record<Topic, { label: string; c: string; hash: string }> = {
  study: { label: 'Studies', c: '#3e6596', hash: 'studies' },
  work: { label: 'Work', c: '#8e503a', hash: 'work' },
  proj: { label: 'Projects', c: '#526d34', hash: 'projects' },
  pub: { label: 'Publications', c: '#815b1f', hash: 'publications' },
  club: { label: 'Clubs & competitions', c: '#007277', hash: 'clubs' },
};

/** Full name · city of each place, shown under the title of the roles that happened there. */
export const places = {
  tum: 'Technical University of Munich · Munich',
  fkie: 'Fraunhofer FKIE · Bonn',
  bsi: 'Federal Office for Information Security (BSI) · Bonn',
  bonn: 'University of Bonn · Bonn',
  brs: 'BRS Motorsport e.V. · Siegburg',
  school: 'Hans-Thoma-Gymnasium · Lörrach',
} as const;
export type Place = keyof typeof places;

export interface Role {
  k: Topic;
  /** Small uppercase label; roles with one are "extras" (slightly smaller title). Without one, the label is the topic's name (Studies, Work). */
  kick?: string;
  t: string;
  /** Shown on the right of the title. */
  when: string;
  /** Year it ended, or 'now' while it is still going on. Picks the year folder: ongoing roles go into the current year. */
  until: number | 'now';
  /** Where it happened; its full name and city go under the title. Departments go in the title. */
  at?: Place;
  /** Grey line under the title, e.g. the journal and co-authors of a publication. */
  sub?: string;
  /** Text under the title; *words between asterisks* are set in italics (e.g. paper titles), [label](url) becomes a link. */
  what?: string;
  link?: { href: string; label: string };
}

export const currently =
  'Reconstructing events from Kerberos-encrypted NFS traffic at Fraunhofer FKIE, with a publication planned. In parallel, the first semester of the M.Sc. in Informatics at TUM, moving from IT security towards machine learning, and this website.';


// One folder per year, newest first. Within a year: ongoing roles first, then by end date, newest first.
export const roles: Role[] = [
  { k: 'study', t: 'Informatics (M.Sc.)', when: 'Oct. 2026 – now', until: 'now', at: 'tum', what: 'Machine Learning and Analytics, with Scientific Computing and HPC, and Security and Privacy.' },
  { k: 'pub', kick: 'Publication · in preparation', t: 'Forensic Analysis of Encrypted NFS Traffic', when: 'Sep. 2026 – now', until: 'now', at: 'fkie' },
  { k: 'work', t: 'Student assistant, Cyber Analysis and Defense', when: 'Jul. 2025 – now', until: 'now', at: 'fkie', what: 'Independent research on the forensic analysis of network traffic, mainly encrypted protocols.' },
  { k: 'proj', kick: 'Project', t: 'This website', when: 'Nov. 2026', until: 2026, what: 'My old website was a bit overwhelming to land on, so I wanted something calmer. Built in Astro with help from Claude.' },
  { k: 'pub', kick: 'Publication', t: 'Forensic Analysis of Encrypted SMB Traffic', when: 'Sep. 2026', until: 2026, sub: 'Digital Threats: Research and Practice (ACM)', link: { href: 'https://doi.org/10.1145/3848131', label: 'doi:10.1145/3848131' } },
  { k: 'study', t: 'Cyber Security (B.Sc.)', when: 'Oct. 2022 – Mar. 2026', until: 2026, at: 'bonn', what: 'Grade 1.4. IT security, cryptography and digital forensics. Thesis on the analysis of encrypted SMB traffic.' },
  { k: 'proj', kick: 'Project', t: 'Event reconstruction with SCF', when: 'Jul. 2025 – Jan. 2026', until: 2026, at: 'fkie', what: 'Open-source implementation of [*Advancing Event Reconstruction in Network Forensics*](https://doi.org/10.1145/3712716.3712723).', link: { href: 'https://github.com/fkie-cad/SCF', label: 'github.com/fkie-cad/SCF' } },
  { k: 'work', t: 'Internship, Mobile Incident Response Team', when: 'Sep. – Oct. 2025', until: 2025, at: 'bsi', what: 'Six weeks in operational incident response. Contributed to a system for managing evidence.' },
  { k: 'club', kick: 'Student club', t: 'Formula Student: Aerodynamic Development', when: 'Jun. 2023 – Jun. 2025', until: 2025, at: 'brs', what: 'Design and manufacturing of aerodynamic components for a Formula Student race car, with a focus on the rear wing of the G24e.' },
  { k: 'proj', kick: 'Project', t: "Backstabber's Knife Collection", when: 'Jun. – Dec. 2024', until: 2024, at: 'bonn', what: "A framework that collects malicious packages automatically and adds them to the [Backstabber's Knife Collection](https://dl.acm.org/doi/10.1007/978-3-030-52683-2_2). The implementation is not open source." },
  { k: 'study', t: 'Abitur', when: '2013 – 2021', until: 2021, at: 'school', what: 'Grade 1.3. Majors: mathematics, computer science and physics.' },
  { k: 'club', kick: 'Student research centre', t: 'phænovum', when: 'Sep. 2018 – Mar. 2021', until: 2021, what: 'Research projects next to school, and the way into the competitions.' },
  { k: 'club', kick: 'Competition', t: 'Jugend forscht', when: 'Feb. 2019, Feb. 2020, Mar. 2021', until: 2021, sub: 'Freiburg and Heilbronn', what: '3rd place in the state competition, 1st and 3rd place in the regional competition.' },
  { k: 'club', kick: 'Competition', t: "German Young Physicists' Tournament (GYPT)", when: 'Mar. 2020', until: 2020, sub: 'Bad Honnef', what: '2nd place in the national final, 1st place in the regional round.' },
  { k: 'club', kick: 'Competition', t: 'International Conference of Young Scientists (ICYS)', when: 'Apr. 2019', until: 2019, sub: 'Kuala Lumpur, Malaysia', what: '3rd place.' },
];
