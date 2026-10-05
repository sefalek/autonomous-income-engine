# Autonomous Income Engine

Cloud-only, demand-driven digital product automation.

The engine researches public demand signals, scores opportunities, asks Gemini for a product specification, generates a product pack, updates a static storefront, and stores lightweight state.

Important: Payhip's current public API supports coupons and license keys, not product creation/upload. Therefore the default workflow does not claim to auto-publish to Payhip. It generates a ready-to-upload pack and sales copy. See https://payhip.com/api-reference

Stack:
- GitHub Actions
- Python
- Google Gemini free tier
- public RSS/JSON sources
- GitHub Pages
- Actions artifacts

No VPS, database, n8n Cloud, or always-on PC is required.

Required secret: GEMINI_API_KEY
Optional: GEMINI_MODEL

Run locally:
PYTHONPATH=src python -m income_engine.pipeline
