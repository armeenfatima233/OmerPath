# OmerPath Complete Front-End Prototype

A production-oriented interactive front-end prototype for OmerPath, an AI-guided scholarship discovery and application workspace.

## Run locally

Requirements: Node.js 20+ and npm.

```bash
npm install
npm run dev
```

Open the URL shown by Vite, normally `http://localhost:3000`.

For a production bundle:

```bash
npm run build
npm run preview
```

## Main routes

- `/` — public landing page with interactive quick matcher
- `/signup` — prototype sign-up
- `/login` — prototype login
- `/onboarding` — four-step profile onboarding
- `/dashboard` — workspace overview
- `/dashboard/scholarships` — search, filter, sorting, saved opportunities
- `/dashboard/scholarships/:id` — explainable match detail
- `/dashboard/applications` — application stage planner
- `/dashboard/passport` — document readiness, file upload simulation, controlled share dialog
- `/dashboard/advisor` — context-aware AI Advisor simulation
- `/dashboard/resources` — searchable resource library
- `/dashboard/notifications` — notification state management
- `/dashboard/profile` — editable profile
- `/dashboard/settings` — privacy/notification preferences and prototype reset

## What was fixed in this release

- Corrected all dashboard routes and sidebar URLs.
- Removed references to dashboard images that were missing from the original ZIP.
- Replaced placeholder CTA toasts with working front-end flows.
- Added sign-up, login, onboarding, scholarship detail, filtering, saving, applications, Passport, Advisor, profile, notifications, resources, and settings experiences.
- Added an interactive landing-page matcher rather than adding more decorative sections.
- Reduced landing-page repetition while keeping the existing warm editorial visual direction.
- Added visible prototype/source/freshness caveats so demo data is not presented as live verified scholarship data.
- Corrected the 15 August 2026 weekday to Saturday.
- Removed old 2024/2025 scholarship labels from the prototype content.
- Removed blue/plum UI accents from the active product experience.
- Added accessible names for icon-only controls, visible keyboard focus, reduced-motion support, and restored browser zoom support.
- Improved small-screen typography and mobile layouts.
- Added SEO/social metadata and hero image preload.
- Replaced the 1920px logo used at tiny UI sizes with an optimized 160px WebP mark.
- Removed Manus-specific Vite runtime/debug dependencies from the release configuration.
- Added localStorage persistence for interactive prototype state.

## Important prototype note

Opportunity records, dates, match scores, source states, and verification labels in this build are sample interface data. A production release should connect every scholarship to a live data pipeline and the official programme source, with server-side freshness checks and audit history.

The AI Advisor in this build is a deterministic front-end simulation. It demonstrates how profile, Passport, shortlist, and application context should shape answers; it is not connected to an LLM API.
