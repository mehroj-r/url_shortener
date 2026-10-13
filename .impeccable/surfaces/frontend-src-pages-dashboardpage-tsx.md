---
version: 1
slug: "frontend-src-pages-dashboardpage-tsx"
primary_target: "frontend/src/pages/DashboardPage.tsx"
related_targets: ["frontend/src/App.tsx"]
---

# Bekat app (signed-in surfaces)

Scope: the whole signed-in web app at `/app/` (dashboard, links, link detail, collections, tags, invites, settings) plus sign-in and invite sign-up. Visitor mode: Operate. Build path: code-led (no image generation).

Audience and job: the owner and invited people, tech-comfortable, on desktop and phone. They create and copy short links in seconds, keep them organised in collections and tags, and check whether a link is being clicked, since when, from where and on what.

Proof and content: real API data only (fresh database, so empty states matter). No country data (no GeoIP). Bot clicks are excluded from counts. Sample data only in empty-state illustrations, labelled as such.

Constraints: must not feel like a generic SaaS template; must not be slow or showy. Standard web controls everywhere; the world contributes type, palette, density and one signature move.

## Direction contract

THESIS: Your links run like the Tashkent Metro: collections are lines with their own colour, links are stations along them, clicks are passengers through the turnstiles. It refuses the category default of a grey sidebar, blue accent, stat tiles and a lone line chart.

OWN-WORLD: Polished granite (#2A2D33) owns the top bar; cool marble ground (#ECEEF1) under white platform panels with hairline stone borders. Line colours (red #D7262E, blue #1C5FB8, green #1E9A55, then amber, violet, teal) are the only saturated colour and always mean a collection or tag. Bronze (#A26F35) sets small station-signage labels. One glazed ceramic tile band (an eight-point star repeat in the line colours) runs once under the top bar. Golos Text for all interface text, Red Hat Mono for short codes and figures in tables.

STORY: The owner opens Bekat, sees today's turnstile count against its 30-day history with spikes marked, sees which lines carry traffic, shortens a new link at the ticket window without leaving the page, and opens any station for its sources, devices and recent passengers.

FIRST VIEWPORT: Granite top bar (Bekat wordmark, Dashboard / Links / Collections / Tags / Invites, search, user menu) above the ceramic band. Full-width ticket window: long URL, `url.mekhroj.com/` plus optional code, Shorten as the primary action. Then the dashboard heading with 7 / 30 / 90 day tabs. Left two thirds: the line map, each collection a coloured line with its links as stations sized by clicks. Right third: the turnstile panel, today's clicks large over a 30-day bar strip with the spike onset marked. Below: top links table, sources (referrers / devices / browsers tabs), recent clicks.

FORM: Tashkent Metro, first on the ordered grounded list, chosen by the user as Impeccable's pick over the roll's Registered Post (third). seed: none (unavailable)

Signature interaction: hovering or focusing a station highlights that link everywhere on the page (its row, its line) and clicking it opens the station page. Motion grammar: 150 to 200 ms exponential ease-out on state changes only; one authored moment, a newly created link arriving as a station on its line (240 ms); nothing on page load; reduced motion respected.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
