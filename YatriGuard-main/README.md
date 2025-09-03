# YatriGuard

YatriGuard is a safety-first travel assistant for India. It helps travelers generate a Digital ID, share trip details with emergency contacts, and access an SOS dashboard. The app supports multiple Indian languages and uses a modern, accessible UI.

## Features

- Multi-step Digital ID form with:
  - Aadhaar checksum (Verhoeff) validation
  - Demo mobile OTP verification
  - Final consent step
- Language support via lightweight i18n (`src/i18n/`)
- Dashboard with quick actions and SOS
- Responsive UI with shadcn/ui (Radix) + Tailwind
- Client-side routing (React Router)

## Tech Stack

- Vite + React + TypeScript
- Tailwind CSS + shadcn/ui (Radix UI)
- React Hook Form + Zod
- React Router
- date-fns, lucide-react

## Getting Started

Prerequisites: Node.js 18+ and npm

```bash
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Scripts

- npm run dev — Start dev server
- npm run build — Production build
- npm run build:dev — Development-mode build
- npm run preview — Preview prod build locally
- npm run lint — Lint the project

## Project Structure

```
public/            # Static assets
src/
  components/      # UI components (Navigation, Layout, ui/*)
  pages/           # Pages (Home, DigitalID, SignIn, Dashboard, etc.)
  i18n/            # I18n provider and translations
  hooks/, context/ # Custom hooks and providers
  assets/          # Images and media
```

Key files:
- src/pages/DigitalID.tsx — Multi-step Digital ID flow
- src/pages/SignIn.tsx — Email/Name sign-in with i18n validation
- src/i18n/I18nProvider.tsx — i18n context and `t()` helper
- src/i18n/translations.ts — Language dictionaries

## Internationalization

- Add/modify keys in `src/i18n/translations.ts` for each language
- Use in components with:
  ```ts
  const { t } = useI18n();
  t('some.key');
  ```

## Notes

- On Digital ID submit, the app simulates a short “blockchain processing” buffer with a spinner, then navigates to the dashboard.
- OTP flow is demo-only (code is logged to console in dev).

## Deployment

Build and serve the `dist/` folder on any static host (Netlify, Vercel, GitHub Pages, etc.):

```bash
npm run build
npm run preview  # optional local check
```

## License

MIT
