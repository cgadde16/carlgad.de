// Everything the home page shows lives here, so wording and links change in one place.

export const person = {
  name: 'Carl Gadde',
  tagline: 'Munich, 519 m above sea level',
};

export interface Sign {
  /** Place name on the plate. */
  label: string;
  /** Small text revealed on hover / keyboard focus. */
  detail: string;
  href: string;
}

// Subpages: Office, Tours, Library and Base camp.
export const signs: Sign[] = [
  { label: 'Office', detail: 'What I\'ve worked on', href: '/office/' },
  { label: 'Tours', detail: 'Where I\'ve been', href: '/tours/' },
  { label: 'Library', detail: 'What I\'ve been reading', href: '/library/' },
  { label: 'Base camp', detail: 'About me', href: '/about/' },
];

export type SocialKind = 'github' | 'linkedin' | 'scholar' | 'strava' | 'email';

export interface Social {
  kind: SocialKind;
  label: string;
  /** Leave empty to hide the icon. */
  href: string;
}

export const socials: Social[] = [
  { kind: 'github', label: 'GitHub', href: 'https://github.com/cgadde16' },
  { kind: 'linkedin', label: 'LinkedIn', href: 'https://www.linkedin.com/in/carl-gadde' },
  { kind: 'scholar', label: 'Google Scholar', href: 'https://scholar.google.com/citations?user=6evYNykAAAAJ' },
  { kind: 'strava', label: 'Strava', href: 'https://www.strava.com/athletes/187835311' },
  { kind: 'email', label: 'Email', href: 'mailto:carlgadde@proton.me' },
];
