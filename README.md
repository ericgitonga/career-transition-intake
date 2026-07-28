# Career Transition Intake

Client onboarding form for the Career Transition Planning service.
Collects structured intake responses across 10 sections, compiles them into a PDF, and emails the PDF and any uploaded documents to the consultant automatically via [Resend](https://resend.com).

The public-facing marketing page lives in a separate repo,
**[career-transition](https://github.com/ericgitonga/career-transition)** (Next.js on
Vercel) — kept separate because it's a different stack on a different platform. Its
call-to-action links to this service's client entry point.

## Deployment

Deployed to [Render](https://render.com) as a Python (Flask + gunicorn) web service.
Render redeploys automatically on every push to `main` — no CI/CD workflow required.

See **[hosting.pdf](hosting.pdf)** for full setup instructions.
