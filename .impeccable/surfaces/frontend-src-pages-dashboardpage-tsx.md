---
version: 1
slug: "frontend-src-pages-dashboardpage-tsx"
primary_target: "frontend/src/pages/DashboardPage.tsx"
related_targets: ["frontend/src/App.tsx"]
---

# Spur app (signed-in surfaces)

Scope: the whole signed-in web app at `/app/` (dashboard, links, link detail, collections, tags, invites, settings) plus sign-in and invite sign-up. Visitor mode: Operate. Build path: code-led (no image generation).

Audience and job: the owner and invited people, tech-comfortable, on desktop and phone. They create and copy short links in seconds, keep them organised in collections and tags, and check whether a link is being clicked, since when, from where and on what.

Proof and content: real API data only (fresh database, so empty states matter). No country data (no GeoIP). Bot clicks are excluded from counts. Sample data only in empty-state illustrations, labelled as such.

Constraints: must not feel like a generic SaaS template; must not be slow or showy. Standard web controls everywhere; the world contributes type, palette, density and one signature move.

## Direction contract

Refined 2026-10-13 at the owner's request: rename Bekat to Spur, remove the coloured decoration at the top (the ceramic tile band), add a dark theme, and make the interface more minimal and serious. The line map and layout stay; the metro world recedes from a costume into one device.

THESIS: Collections are drawn as lines with their own colour and links sit on them as stations sized by clicks; everything else is quiet, so the links and their numbers lead. It refuses the category default of a grey sidebar, blue accent, stat tiles and a lone line chart, and it refuses ornament.

OWN-WORLD: Cool stone neutrals in two composed themes. Light: a pale cool ground (#F3F4F6) under white panels with hairline borders (#DFE2E7) and a white top bar ruled off by the same hairline. Dark: a near-black cool ground (#0F1114) under raised panels (#16181C) with dark hairlines (#272A30), set as its own steps, not an inversion. The primary action is near-black on light and near-white on dark. Line colours (red, blue, green, violet, amber, teal, in that order, muted and validated per theme) are the only saturated colour and always mean a collection or tag. One copper accent (#A26F35 light, #C28A4C dark) marks today's bar, the spike rule and the wordmark's dot, and nothing else. No ornament. Golos Text for all interface text, Red Hat Mono for short codes, the host prefix and click times.

STORY: The owner opens Spur, sees today's clicks against their 30-day history with the latest spike marked, sees which collections carry traffic, shortens a new link at the top of the page without leaving it, and opens any link for its sources, devices and recent clicks. They can switch between light, dark and the system theme from the account menu or Settings.

FIRST VIEWPORT: A quiet top bar (Spur wordmark, Dashboard / Links / Collections / Tags / Invites with the current page underlined in ink, search, Shorten, account menu). Full-width create panel: long URL, `url.mekhroj.com/` plus optional code, Shorten as the primary action. Then the dashboard heading with 7 / 30 / 90 day tabs. Left two thirds: the Collections map, each collection a thin coloured line with its links as stations sized by clicks. Right third: the Clicks panel, today's clicks over a 30-day bar strip with the spike onset marked. Below: top links table, sources (referrers / devices / browsers / systems tabs), recent clicks.

FORM: Tashkent Metro, first on the ordered grounded list, chosen by the user as Impeccable's pick over the roll's Registered Post (third), then quietened at the user's request into Spur. seed: none (unavailable)

Signature interaction: hovering or focusing a station highlights that link everywhere on the page (its row, its line) and clicking it opens the link's page. Motion grammar: 150 to 200 ms exponential ease-out on state changes only; one authored moment, a newly created link arriving on its line (240 ms); nothing on page load; reduced motion respected.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
