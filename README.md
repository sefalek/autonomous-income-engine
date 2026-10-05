# Autonomous Income Engine

Cloud-only, demand-driven digital product automation.

The engine has two modes:

1. **Autonomous mode:** leave the topic empty and the engine researches public demand signals and chooses an opportunity.
2. **Manual topic mode:** from GitHub Actions → Run workflow, enter a topic such as `restaurant inventory`, `freelancer pricing`, or `Excel cash-flow tracker`. The engine researches that topic and generates a product pack around it.

Each run can generate:
- Excel workbook
- PDF quick-start guide
- product specification
- ZIP package

### Notifications

After a successful product build, the workflow can:
- email the Excel + PDF + ZIP via Resend
- send a Telegram notification and the Excel file via Telegram

Required GitHub Actions secrets:
- `GEMINI_API_KEY`
- `RESEND_API_KEY`
- `NOTIFY_EMAIL_TO`
- `NOTIFY_EMAIL_FROM` (optional; defaults to `onboarding@resend.dev`)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Notification integrations are optional. If their secrets are absent, product generation still works.

Important: Payhip's current public API supports coupons and license keys, not product creation/upload. Therefore the default workflow does not claim to auto-publish to Payhip. It generates a ready-to-upload pack and sales copy.

Stack:
- GitHub Actions
- Python
- Google Gemini
- public RSS/JSON sources
- GitHub Pages
- Actions artifacts

No VPS, database, n8n Cloud, or always-on PC is required.
