# Building Frankenstengine — site policy

This is the public site for the Frankenstengine project. It also doubles as
the live workshop / build-in-public log. The rules below exist so the site
stays simple, safe, and cheap to run.

## Static-first, live-gen-later

**Default:** every demo on this site is either client-side (runs entirely in
the visitor's browser, no server involved) or pre-recorded (clips, GIFs,
images).

**Why:**
- No per-visitor API cost.
- No abuse vector — nobody can script the page to drain a generation budget.
- No API-key handling problem.
- No latency-on-the-critical-path that breaks the demo experience.

**Live generative-AI endpoints arrive only when:**
1. There's a server-side proxy on a platform we already use (Vercel functions,
   or a small endpoint on an existing VPS). The API key is **never** in client
   code.
2. The endpoint is rate-limited per-IP and per-day-globally.
3. There's a Cloudflare Turnstile (or equivalent) gate.
4. There's a hard daily budget cap. Hit the cap, the endpoint returns 429
   gracefully — it does not silently keep spending.
5. The feature is gated by a waitlist or magic-link auth. No anonymous live
   generation.

If any of those is missing, it's not ready to ship.

## Webcam / privacy

The `/parallax/` demo uses the visitor's webcam to track head position. This
is genuinely client-side: MediaPipe's face landmarker runs in the browser
via WASM. Nothing leaves the visitor's device. The privacy line on the page
must remain accurate. If that ever changes (e.g. a future demo that uploads
frames), the privacy line **must** be rewritten before the change ships.

## Third-party scripts

CDN imports (jsDelivr for Three.js, MediaPipe) are **version-pinned** in the
import map and inline imports. SRI on raw ES module imports isn't fully
viable yet, so the trust assumption is on the CDN + npm provenance. If we
need stronger guarantees, mirror the modules into `/vendor/` and serve them
from the same origin.

A `Content-Security-Policy` meta tag on each page restricts script and
connect sources. Update the CSP if you add a new external domain — don't
just remove the meta.

## Hygiene basics

- **Branch-only workflow.** No direct pushes to `main` from a local clone.
  Open a PR, eyeball the diff, merge intentionally.
- **No secrets in the repo.** A `.env` file should never be committed. If a
  pre-commit gitleaks hook isn't set up locally yet, run it before pushing
  any branch that touches new files.
- **No analytics that ship visitor data off-site without disclosure.**
  GitHub Pages basic stats are fine. Anything beyond that needs a notice.
- **No third-party tracking pixels.** This site exists to demonstrate
  craft; tracking pixels signal the opposite of what we're building.

## Adding a new demo page

1. Static HTML in its own directory (`/your-demo/index.html`). Same fonts,
   palette, and scanline overlay as `/lab/`.
2. CSP meta on every page. Add to the existing whitelist; don't remove.
3. If it uses webcam / mic / sensors, the privacy line is mandatory and
   must be plain-language.
4. Link from `/lab/` so it's discoverable.
5. Note it in the "Recent" list on `/lab/` until it's stable.

## Staging

A separate public repo `Jonohobs/frankenstengine-staging` mirrors this site
for staging. It deploys via GitHub Pages to
`https://jonohobs.github.io/frankenstengine-staging/`. Production
(`frankenstengine.com`) only updates when a PR is merged to `main` here.

`staging.frankenstengine.com` as a custom subdomain is a separate decision
— it requires a DNS change in Cloudflare and is not yet authorised.
