---
name: Bekat
description: A link shortener on the owner's own domain, drawn as a metro network of coloured lines and stations.
colors:
  granite: "#2a2d33"
  granite-raised: "#363a42"
  granite-ink: "#f3f4f6"
  granite-muted: "#b7bcc5"
  marble: "#eceef1"
  marble-sunken: "#e3e6ea"
  panel: "#ffffff"
  stone: "#d5d9df"
  stone-strong: "#c4c9d1"
  control-edge: "#8a919c"
  ink: "#1b1e23"
  ink-2: "#4a505b"
  ink-3: "#5e6470"
  bronze: "#8c5d28"
  bronze-rule: "#a26f35"
  line-red: "#d7262e"
  line-blue: "#1c5fb8"
  line-green: "#1e9a55"
  line-violet: "#7a4fb5"
  line-amber: "#c7860f"
  line-teal: "#0b95a8"
  line-slate: "#6b7280"
  status-warn-ink: "#7a4a00"
  status-warn-bg: "#fff1d6"
  status-danger-ink: "#9b1c1c"
  status-danger-bg: "#fdecec"
  status-off-ink: "#4a505b"
  status-off-bg: "#e8ebef"
  status-ok-ink: "#135c35"
  status-ok-bg: "#e3f4ea"
  focus: "#2a2d33"
  focus-on-granite: "#f3f4f6"
  selection: "#efe2cf"
typography:
  display:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "3.5rem"
    fontWeight: 680
    lineHeight: 1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 650
    lineHeight: 1.2
  subhead:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "1.375rem"
    fontWeight: 650
    lineHeight: 1.2
  title:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 650
    lineHeight: 1.2
  body:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "'ss01'"
  body-sm:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  control:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 560
    lineHeight: 1
  label:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 560
    lineHeight: 1.5
  sign:
    fontFamily: "Golos Text Variable, Golos Text, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.5
    letterSpacing: "0.04em"
  code:
    fontFamily: "Red Hat Mono Variable, Red Hat Mono, ui-monospace, monospace"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.5
    fontFeature: "'tnum'"
  code-specimen:
    fontFamily: "Red Hat Mono Variable, Red Hat Mono, ui-monospace, monospace"
    fontSize: "1.375rem"
    fontWeight: 600
    lineHeight: 1.2
rounded:
  sm: "4px"
  md: "6px"
  lg: "10px"
  pill: "999px"
spacing:
  s-1: "4px"
  s-2: "8px"
  s-3: "12px"
  s-4: "16px"
  s-5: "20px"
  s-6: "24px"
  s-8: "32px"
  s-10: "40px"
  s-12: "48px"
components:
  top-bar:
    backgroundColor: "{colors.granite}"
    textColor: "{colors.granite-ink}"
    height: "56px"
  nav-link:
    textColor: "{colors.granite-muted}"
    typography: "{typography.control}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "36px"
  nav-link-active:
    backgroundColor: "{colors.granite-raised}"
    textColor: "{colors.granite-ink}"
  button-primary:
    backgroundColor: "{colors.granite}"
    textColor: "{colors.granite-ink}"
    typography: "{typography.control}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "36px"
  button-primary-hover:
    backgroundColor: "{colors.granite-raised}"
  button-primary-lg:
    backgroundColor: "{colors.granite}"
    textColor: "{colors.granite-ink}"
    rounded: "{rounded.md}"
    padding: "0 20px"
    height: "44px"
  button-secondary:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "36px"
  button-secondary-hover:
    backgroundColor: "{colors.marble}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink-2}"
    typography: "{typography.control}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "36px"
  button-ghost-hover:
    backgroundColor: "{colors.marble-sunken}"
    textColor: "{colors.ink}"
  button-danger:
    backgroundColor: "{colors.status-danger-ink}"
    textColor: "{colors.panel}"
    typography: "{typography.control}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "36px"
  button-shorten-on-granite:
    backgroundColor: "{colors.granite-ink}"
    textColor: "{colors.granite}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "30px"
  input:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "36px"
  input-ticket:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "44px"
  panel:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.lg}"
    padding: "16px 20px 20px"
  ticket-window:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.lg}"
    padding: "20px 24px"
  segmented:
    backgroundColor: "{colors.marble-sunken}"
    rounded: "{rounded.md}"
    padding: "3px"
  segment:
    textColor: "{colors.ink-2}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "0 12px"
    height: "28px"
  segment-selected:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
  tag-chip:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.pill}"
    padding: "0 8px 0 7px"
    height: "22px"
  badge-warn:
    backgroundColor: "{colors.status-warn-bg}"
    textColor: "{colors.status-warn-ink}"
    rounded: "{rounded.pill}"
    padding: "0 8px"
    height: "22px"
  badge-danger:
    backgroundColor: "{colors.status-danger-bg}"
    textColor: "{colors.status-danger-ink}"
    rounded: "{rounded.pill}"
    padding: "0 8px"
    height: "22px"
  badge-off:
    backgroundColor: "{colors.status-off-bg}"
    textColor: "{colors.status-off-ink}"
    rounded: "{rounded.pill}"
    padding: "0 8px"
    height: "22px"
  badge-ok:
    backgroundColor: "{colors.status-ok-bg}"
    textColor: "{colors.status-ok-ink}"
    rounded: "{rounded.pill}"
    padding: "0 8px"
    height: "22px"
  tooltip:
    backgroundColor: "{colors.granite}"
    textColor: "{colors.granite-muted}"
    rounded: "{rounded.md}"
    padding: "6px 10px"
  toast:
    backgroundColor: "{colors.granite}"
    textColor: "{colors.granite-ink}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  dialog:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    width: "560px"
---

# Design System: Bekat

## Overview

**Creative North Star: "The Tashkent Metro"**

Bekat treats a set of short links as a metro network. Collections are lines, each with its own colour; links are stations along them; clicks are passengers through the turnstiles. The materials are those of a Tashkent Metro station: a polished granite top bar, a cool marble floor, white platform panels edged with hairline stone, bronze station lettering, and one band of glazed ceramic tile. The line colours are the brightest colours in the interface, and apart from the tile band they always mean a collection or a tag.

The interface is an operating tool, not a showcase. Density is moderate and even: 36px controls, 12px table cell padding, panels on a 20px grid gap, a 1360px page. Standard web controls are used throughout; the world contributes the palette, the two typefaces, the density and one signature component, the line map. Motion is short and confined to state changes. Page content does not animate in on load.

The world rejects the category default of a grey sidebar, a blue accent, rows of stat tiles and a lone line chart. Navigation sits in a horizontal granite bar, interface accents come from granite and bronze, and the clicks chart is a bar strip in granite with today's bar in bronze.

**Key Characteristics:**
- Granite top bar over a marble ground; white panels with 1px stone borders and no resting shadow.
- Seven line colours reserved for collection and tag identity, assigned in a fixed order.
- Bronze for signage: station codes on the line map, table column signs, the spike annotation, link underlines, the wordmark marker.
- Golos Text for the interface; Red Hat Mono for short codes, the short-link host and click times.
- One ornament: a single 18px ceramic tile band under the top bar.
- The line map: collections drawn as 4px coloured lines with links as white stations sized by clicks.
- 150 to 200ms ease-out on state changes; one 240ms arrival when a new link is created.

## Colors

A cool stone neutral family carries the interface; six line colours plus slate carry identity; bronze carries signage; four muted status pairs carry state.

### Primary
- **Polished Granite** (#2a2d33): the top bar, primary buttons, checked checkboxes and radios, pressed tag toggles, chart bars, the share bars in tables, tooltips, toasts and the links bulk-action bar. It is also the focus ring colour on light surfaces.
- **Raised Granite** (#363a42): hover state of primary buttons, the active and hovered nav item, the account button.
- **Granite Ink** (#f3f4f6): text on granite; the background of the top bar's Shorten button; the focus ring on granite.
- **Granite Muted** (#b7bcc5): inactive nav items, placeholder and icon colour in the top-bar search, secondary text in tooltips.

### Secondary
- **Station Bronze** (#8c5d28): bronze text. Station codes on the line map, uppercase column signs in tables, the "Spike from" annotation on the clicks chart.
- **Bronze Rule** (#a26f35): bronze strokes and marks, never text. Link underlines, the wordmark's station marker, the 2px underline on the active nav item, the spike onset line, today's bar in the daily chart, the underline on the "View as table" toggle.

### Tertiary
The line colours, used only as collection and tag identity, assigned in this order:
- **Line Red** (#d7262e)
- **Line Blue** (#1c5fb8)
- **Line Green** (#1e9a55)
- **Line Violet** (#7a4fb5)
- **Line Amber** (#c7860f)
- **Line Teal** (#0b95a8)
- **Line Slate** (#6b7280): links with no collection, and the first choice in the tag colour picker.

### Neutral
- **Ink** (#1b1e23): primary text, headings, table figures.
- **Ink 2** (#4a505b): secondary text, field labels, ghost button text, inactive segments.
- **Ink 3** (#5e6470): tertiary text, hints, the short-link host prefix, the map key, chart ticks, closed station rings.
- **Marble** (#eceef1): the page ground; row hover; dialog footers; empty tracks behind share bars.
- **Marble Sunken** (#e3e6ea): segmented control trough, ghost button hover, row dividers inside panels, selected table rows.
- **Platform White** (#ffffff): panels, inputs, dialogs, menus, station discs.
- **Stone** (#d5d9df): panel and dialog borders, table header rule, tag chip border.
- **Stone Strong** (#c4c9d1): secondary button border, tag toggle border, chart baseline, scrollbar thumb, quiet hour bars.
- **Control Edge** (#8a919c): input and select borders at rest (3.2:1 on white); secondary button border on hover.
- **Selection** (#efe2cf): text selection, a pale bronze.

### Status
Each pair is an ink on a tint, and every badge carries an icon and a word.
- **Warn** (#7a4a00 on #fff1d6): expiring within a week.
- **Danger** (#9b1c1c on #fdecec): expired codes, field and form errors, destructive buttons, the error toast.
- **Off** (#4a505b on #e8ebef): paused.
- **OK** (#135c35 on #e3f4ea): the confirmation strip after a link is created, and the "Waiting" badge on an unused invite.

### Named Rules
**The Line Colour Rule.** Line colours mean a collection or a tag and nothing else. Buttons, links, focus rings, selection, charts and status never use them. The ceramic tile band is the one place they appear as ornament, and it repeats all six in their fixed order.

**The Fixed Order Rule.** Line colours are offered and assigned in the order red, blue, green, violet, amber, teal, with slate for no collection. The order is part of the identity; do not reshuffle it per screen.

**The Bronze Split Rule.** Bronze text uses Station Bronze (#8c5d28, 5.7:1 on white). Bronze Rule (#a26f35, 4.3:1 on white) is for lines, underlines and marks only.

**The Quiet Health Rule.** A healthy link shows no badge. Status colour appears only when a link is paused, expired, expiring within a week or in error.

## Typography

**Display Font:** Golos Text Variable (with Golos Text, system-ui, sans-serif)
**Body Font:** Golos Text Variable (same stack)
**Label/Mono Font:** Red Hat Mono Variable (with Red Hat Mono, ui-monospace, monospace)

**Character:** Golos Text is a plain grotesque with full Latin and Cyrillic, set with stylistic set 1 (`ss01`) on all text. Red Hat Mono marks short codes as station names and makes the host prefix exactly measurable in `ch`.

### Hierarchy
- **Display** (680, 3.5rem, line-height 1, -0.02em): the single large figure in a clicks panel, today's click count. One per panel, never a row of them.
- **Headline** (650, 1.75rem, 1.2): page titles (Dashboard, Links, Collections, a link's name, the sign-in card).
- **Subhead** (650, 1.375rem, 1.2): section headings that sit above a group of panels, such as "Clicks" on a link page.
- **Title** (650, 1.125rem, 1.2): panel and dialog titles.
- **Body** (400, 0.9375rem, 1.5): default text. Explanatory text is capped at 52 to 68ch.
- **Body Small** (400, 0.875rem, 1.5): table cells, inputs, sentences inside panels, menu items.
- **Control** (560, 0.875rem, line-height 1): button and nav labels. Small buttons drop to 0.8125rem; large ones rise to 0.9375rem.
- **Label** (560, 0.8125rem): field labels, segments, tag toggles. Hints and meta lines use the same size at 400.
- **Sign** (600, 0.75rem, 0.04em, uppercase, Station Bronze): table column headers only.
- **Code** (Red Hat Mono 500, 0.875rem, tabular figures): short codes, the `url.mekhroj.com/` host prefix, click timestamps.
- **Code Specimen** (Red Hat Mono 600, 1.375rem, 1.2): a link's short code set large on its page, host prefix at 1.125rem in Ink 3.

Headings use `text-wrap: balance`. Figures in tables and charts are Golos Text with tabular numerals, right-aligned.

### Named Rules
**The Code Face Rule.** Anything a person would type after the slash, and the host before it, is set in Red Hat Mono. Everything else is Golos Text.

**The Signage Rule.** Uppercase, letter-spaced bronze labels are column signs in table headers. They are not used as headings or as labels above headings.

## Layout

Pages sit in a centred container of 1360px with 24px side padding, 24px above and 48px below. At 820px and below the padding drops to 16px at the sides and top and 40px below. Spacing is on a 4px module (4, 8, 12, 16, 20, 24, 32, 40, 48).

Vertical rhythm: 24px between the major blocks of the dashboard, 20px between blocks on other pages, 20px gaps between panels in a grid. Inside a panel: 16px above the header, 20px at the sides and bottom, 16px between header and body. Field labels sit 6px above their control; form rows are 12 to 16px apart.

Panel grids run two or three columns on wide screens and collapse in steps: three columns become two at 1180px, and everything becomes a single column between 760px and 860px depending on the page.

The top bar is sticky, 56px tall, and shares the 1360px container. The search field hides at 1080px. At 820px the nav collapses into a menu button that opens a granite drop-down list, and the Shorten button drops its label and keeps its plus icon. The ceramic band sits under the bar and scrolls away with the page.

Tables scroll horizontally inside their panel and shed lower-priority columns as the width drops (at 1100px, 720px and 640px) rather than wrapping. The first and last columns sit flush with the panel's padding.

Control heights: 36px by default, 30px small, 44px for the primary create field and its button, 28px for segments and small icon buttons, 32px for icon buttons, 22px for badges and chips.

## Elevation & Depth

Depth comes from material, not from shadow. The marble ground is darker than the white panels, and panels are separated from it by a 1px stone border. Resting panels have no shadow. Two shadows exist: one for the one raised object on a page, one for things that float above the page.

### Shadow Vocabulary
- **Raised** (`box-shadow: 0 1px 2px rgb(27 30 35 / 0.06), 0 4px 12px rgb(27 30 35 / 0.06)`): the ticket window (the create-link panel at the top of the dashboard) and the sign-in card.
- **Overlay** (`box-shadow: 0 8px 24px rgb(27 30 35 / 0.16), 0 2px 6px rgb(27 30 35 / 0.08)`): dialogs, the account menu, the chart tooltip, toasts, the sticky bulk-action bar.
- **Selected segment** (`box-shadow: 0 1px 2px rgb(27 30 35 / 0.12)`): the white pressed segment inside its marble trough.
- **Active nav underline** (`box-shadow: inset 0 -2px 0 #a26f35`): a bronze rule under the current page in the top bar.

Dialog backdrops are Ink at 45% (`rgb(27 30 35 / 0.45)`).

### Named Rules
**The Flat Platform Rule.** Panels rest flat on the marble with a stone hairline. Only the page's single creation surface is raised, and only overlays cast the overlay shadow.

## Shapes

Corners are gently rounded and never pill-shaped on containers: 4px for segments, skeletons and small marks; 6px for buttons, inputs, nav items, tooltips and toasts; 10px for panels, dialogs, menus and the bulk bar. Badges, tag chips, tag toggles, the line map terminus and scrollbar thumbs are full pills (999px).

Circles carry identity. A collection or tag is a 10px filled line dot (7px inside a tag chip, 8px in a tag toggle). Colour swatches are 28px discs with a 2px white gap and a 1px Stone Strong ring; the chosen one gets a 2px Ink ring and a check.

Lines are 4px thick with 2px rounded ends wherever they appear: the line map track, its 4 by 16px end bar, the line sample beside each collection, and the horizontal bar of the wordmark's station marker. Stations are white discs with a 3px ring in the line colour (2px when the station has no clicks) and a 2px white halo that cuts the track.

Borders are 1px throughout. Within a panel, rows are divided by 1px Marble Sunken; the panel edge and table header rule are 1px Stone.

## Components

### Buttons
Solid and plain. Granite is the filled button for the main action on a surface; danger is filled only for deletes.
- **Shape:** gently rounded (6px), 36px tall, 16px side padding, 560 weight label, icon gap 8px.
- **Primary:** Polished Granite with Granite Ink text. Hover to Raised Granite.
- **Secondary:** white with a 1px Stone Strong border and Ink text. Hover: Control Edge border on Marble.
- **Ghost:** transparent with Ink 2 text. Hover: Marble Sunken with Ink text. Used for icon buttons (32px square, 28px small).
- **Danger:** Danger ink (#9b1c1c) with white text, for deletes: in confirmation dialogs and the bulk-action bar.
- **Shorten on granite:** in the top bar, the one inverted button: Granite Ink background, Granite text, small size, plus icon. Present on every signed-in page; the `n` key opens the same create dialog.
- **Sizes:** small 30px (12px padding, 0.8125rem), large 44px (20px padding, 0.9375rem).
- **Disabled:** 55% opacity, not-allowed cursor. **Loading:** a 14px ring spinner in the current text colour appears before the label.
- **Transitions:** background, border and text colour at 150ms on the shared ease-out.

### Chips and Badges
- **Tag chip:** white pill, 22px, 1px Stone border, Ink 2 text at 0.75rem 560, preceded by a 7px line dot in the tag's colour.
- **Tag toggle:** white pill, 28px, 1px Stone Strong border; pressed turns solid Polished Granite with Granite Ink text. The line dot stays visible.
- **Status badge:** 22px pill in a status pair, 0.75rem 600, always a 12px icon followed by a word.

### Cards / Containers
- **Corner Style:** 10px.
- **Background:** Platform White on the Marble ground.
- **Shadow Strategy:** none at rest; see Elevation & Depth.
- **Border:** 1px Stone.
- **Internal Padding:** 16px top, 20px sides and bottom; the title row is a flex row with actions (a text link or a segmented control) at the right.
- **Stale data:** while a panel refetches, its previous content dims to 60% opacity over 200ms instead of being replaced by a skeleton. Skeletons (Marble Sunken to Marble shimmer, 1.4s) appear only on first load.
- **Empty state:** left-aligned title at 0.9375rem and a sentence of up to 52ch that explains what will appear and how to get it.

### Inputs / Fields
- **Style:** white, 36px, 1px Control Edge border, 6px radius, 12px side padding, Ink 3 placeholder. Hover darkens the border to Ink 3.
- **Focus:** 2px Polished Granite outline inset by 1px, border to granite.
- **Error:** border to Danger ink; the message sits below the control in Danger ink with an icon. Form-level errors are a Danger tint block with 12px padding.
- **Disabled:** Marble background.
- **Short code field:** the `url.mekhroj.com/` host is an inset prefix in Red Hat Mono, Ink 3; the input text is Red Hat Mono, and its left padding is calculated in `ch` so the code starts exactly after the slash.
- **Select:** same box with a 12px chevron drawn in Ink 2 and 32px right padding.
- **Segmented control:** a Marble Sunken trough with 3px padding and 2px gaps; segments are 28px, 4px radius, Ink 2 text; the selected segment is white with Ink text and the selected-segment shadow. Used for date ranges and for switching a panel's breakdown.

### Navigation
- **Top bar:** sticky, 56px, Polished Granite. From left: the Bekat wordmark (1.25rem, 700, -0.01em) with its bronze station marker (a ring crossed by a 4px bar), the five nav items, the search field, the Shorten button, and a 32px round account button with initials.
- **Nav items:** 36px, 12px padding, Granite Muted text at 0.875rem 560. Hover and current page: Raised Granite background, Granite Ink text; the current page adds a 2px bronze underline.
- **Search on granite:** 34px, 260px wide, a field one step darker than the bar with a border one step lighter, Granite Ink text, Granite Muted icon and placeholder. Its two greys are literals in the shell stylesheet, not tokens.
- **Focus on granite:** the focus ring switches to Granite Ink.
- **Account menu:** a white popover, 10px radius, overlay shadow, anchored to the right edge of the page container.
- **Mobile:** below 820px the nav moves into a menu button that opens a granite list of 36px items (the nav plus Settings) under the bar.

### Ceramic Band
An 18px strip directly under the top bar, aria-hidden. On an off-white ground it repeats a 108 by 18px tile of six eight-point stars (two 12.4px squares, one rotated 45 degrees) in the six line colours in their fixed order, with a 1px Stone rule below. It appears once per screen, including the sign-in and invite screens.

### Line Map
The signature component. Each collection is a row: a label column (150 to 200px) with the line dot, the collection name at 620 weight linking to its filtered links list, and a meta line of link and click counts; then the track.
- **Track:** a 4px line in the collection's colour with a 4 by 16px end bar at the right, drawn behind the stations at the centre of the largest marker.
- **Stations:** links on the line, ordered by clicks and spread across the track, with room for one station per 112px of track (84px on tracks under 480px). Each is a white disc with a 3px ring in the line colour; disc size runs from 12px to 26px on a square-root scale of clicks in the selected range, on one scale for the whole map. A station with no clicks gets a 2px ring.
- **Station names:** the short code below each disc, Red Hat Mono 0.8125rem in Station Bronze, truncated with an ellipsis.
- **States:** a closed station (paused or expired) has a dashed Ink 3 ring and an Ink 3 code; a station expiring within a week gets an extra 2px Warn ring outside its white halo. A key above the map explains size and both states.
- **Overflow:** when a line has more links than fit, the last slot is a terminus pill (24px tall, 2px line-colour border) reading "+n" and linking to the filtered list.
- **Highlight:** hovering or focusing a station or its Top links row, or hovering one of its Recent clicks entries, highlights the link everywhere on the page: the station's disc fills with the line colour and scales to 1.12 over 200ms, its code turns Ink at 600, and its rows in Top links and Recent clicks take a Marble background. A focused or hovered station also shows a granite tooltip with the link name, its clicks and any state. Clicking opens the link's page.
- **Arrival:** a newly created link's station scales in from 0.3 with a fade over 240ms. This is the only authored entrance in the app; the confirmation strip in the create form uses the same 240ms timing.
- **Narrow screens:** below 640px the label stacks above the track and stations are 72px wide.

### Clicks Chart
Daily clicks as a bar strip: Polished Granite bars at 82% opacity, today's bar in Bronze Rule, a 1px Stone Strong baseline and Marble Sunken gridline, Ink 3 tick labels. The onset of the latest spike is a 1.5px Bronze Rule line with a bronze "Spike from" label above the plot. Hover shows a granite tooltip and a crosshair. A "View as table" text toggle, underlined in bronze, reveals the same data as a table.

## Do's and Don'ts

### Do:
- **Do** use Polished Granite (#2a2d33) for every interface accent that is not identity: primary buttons, chart bars, share bars, tooltips, toasts, focus rings.
- **Do** show a collection or tag as a line dot (10px, 7px in chips) or a 4px line in its line colour, next to its name in text.
- **Do** set short codes, the host prefix and click times in Red Hat Mono, with the host in Ink 3 and the code in Ink.
- **Do** separate panels from the marble ground with a 1px Stone (#d5d9df) border, and rows inside panels with 1px Marble Sunken (#e3e6ea).
- **Do** keep state transitions at 150 to 200ms on `cubic-bezier(0.16, 1, 0.3, 1)`, and respect reduced motion.
- **Do** pair every status colour with an icon and a word.
- **Do** dim stale data to 60% while it refetches rather than flashing a skeleton.
- **Do** keep creating a link one step away: the Shorten button in the top bar on every signed-in page.

### Don't:
- **Don't** use a line colour for a button, link, focus ring, chart bar or status.
- **Don't** add a second ceramic band or any other ornament; the tile band under the top bar is the only one.
- **Don't** set text in Bronze Rule (#a26f35); bronze text is Station Bronze (#8c5d28).
- **Don't** put a shadow on a resting panel; Raised is for the single creation surface, Overlay for floating layers.
- **Don't** use uppercase letter-spaced signage outside table column headers.
- **Don't** add entrance animation to page content on load; panels and rows appear without motion.
- **Don't** show a badge on a healthy link.
