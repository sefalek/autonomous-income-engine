from __future__ import annotations

import base64
import os
from pathlib import Path

import requests


def _mime(path: Path) -> str:
    return {
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pdf": "application/pdf",
        ".zip": "application/zip",
        ".json": "application/json",
    }.get(path.suffix.lower(), "application/octet-stream")


def _resend_attachment(path: Path) -> dict:
    return {
        "filename": path.name,
        "content": base64.b64encode(path.read_bytes()).decode("ascii"),
        "content_type": _mime(path),
    }


def send_email(subject: str, html: str, attachments: list[Path]) -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    to = os.getenv("NOTIFY_EMAIL_TO")
    sender = os.getenv("NOTIFY_EMAIL_FROM", "onboarding@resend.dev")
    if not api_key or not to:
        return False

    payload = {
        "from": sender,
        "to": [to],
        "subject": subject,
        "html": html,
        "attachments": [_resend_attachment(p) for p in attachments if p.exists()],
    }
    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return True


def send_telegram(message: str, document: Path | None = None) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False

    base = f"https://api.telegram.org/bot{token}"
    response = requests.post(
        f"{base}/sendMessage",
        data={"chat_id": chat_id, "text": message},
        timeout=30,
    )
    response.raise_for_status()

    if document and document.exists():
        with document.open("rb") as handle:
            response = requests.post(
                f"{base}/sendDocument",
                data={"chat_id": chat_id, "caption": document.name},
                files={"document": (document.name, handle, _mime(document))},
                timeout=60,
            )
            response.raise_for_status()
    return True
