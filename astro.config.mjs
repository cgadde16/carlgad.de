// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  // the final address (user, 2026-11-18); used for the absolute link-preview URLs in Base.astro
  site: 'https://carlgad.de',
  // lets temporary Cloudflare quick tunnels (*.trycloudflare.com) reach `astro preview`
  vite: { preview: { allowedHosts: ['.trycloudflare.com'] } },
  // this page was called Passes, then briefly Summit and Lookout (2026-11-15)
  redirects: { '/passes': '/tours/', '/summit': '/tours/', '/lookout': '/tours/' },
});
