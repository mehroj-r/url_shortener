# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React + Vite + TypeScript single-page app in `frontend/`, built to static files and served by the Django app on the same origin as the API (`url.mekhroj.uz`), so there is no CORS and no extra host configuration. The Django REST API lives in `backend/` of the same repository.

## Users

The owner and the people they invite: a small circle of fairly tech-comfortable people who create and share links for work, projects and personal use. It is not a public, anonymous-signup product: new accounts need a single-use invite created by an existing user.

## Product Purpose

A complete link shortener on the owner's own domain: create short links, organise them (collections and tags), and understand how they are clicked (a dashboard plus per-link analytics). Success means making and sharing a link takes seconds, and the question "is this link working, and where are the clicks coming from?" is answered at a glance.

## Positioning

The organisation and analytics of a paid link-management tool, on a domain and server the owner controls, for a small trusted group. Click data never leaves the owner's deployment.

## Operating Context

- Short links resolve at `https://url.mekhroj.uz/<code>`; unknown or inactive codes redirect to a configurable default URL.
- Links are shared in messages, posts and documents; clicks arrive from whatever app the link was opened in.
- Managing links (creating, organising, reviewing analytics) happens in the browser, on desktop and phone. (Assumed: no usage data exists yet.)

## Capabilities and Constraints

- Accounts: JWT auth (register, login, logout, token refresh), per-user data isolation, rate-limited auth endpoints. Sign-up is invite-only: signed-in users create single-use invite links.
- Links: a destination URL with a name, optionally in a collection; each can have one or more short codes. Codes are custom (letters, digits, `-`, `_`, up to 64 characters) or auto-generated (7 characters), can be deactivated, and are never reused after deletion.
- Collections: named groups, unique per user.
- Clicks: recorded on every redirect with time, IP, user agent and referrer.
- Being added alongside the frontend: invites, tags, link expiry, analytics aggregates (clicks over time, referrers, browsers, operating systems, devices), profile and password management, and search, filter and sort.
- The signed-in home is a dashboard overview, with creating a link always one step away.
- Open decisions: country-level analytics (needs a GeoIP database); UI language (English for now).

## Brand Commitments

The product is called **Spur** (a short branch off a main line), chosen by the owner on 2026-10-13 to replace the first name, Bekat. It lives on the domain `url.mekhroj.uz`. The only logo is the wordmark's mark: a short branch leaving a line, ending in a copper dot.

Must not feel like a generic SaaS admin template, and must not be slow or showy: speed and clarity over effects. The owner asked for a minimal, serious interface with no decoration, and for a dark theme alongside the light one (2026-10-13).

## Evidence on Hand

No real usage data yet (fresh database). No testimonials, customers or metrics exist; never fabricate them. Demonstration data in screenshots or empty states must be labelled as sample data.

## Product Principles

1. A link in seconds: creating and copying a short link is never more than one step away, wherever you are in the app.
2. Every number answers a question a link owner actually asks: is it being clicked, since when, from where, on what.
3. Organisation without ceremony: collections and tags help find links later and are never required to create one.
4. The owner's data stays on the owner's server.
