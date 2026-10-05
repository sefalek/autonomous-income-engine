from __future__ import annotations

import json
import os
from pathlib import Path

from .ai import generate_product_spec
from .notifications import send_email, send_telegram
from .product import build_product
from .research import collect
from .scoring import rank
from .state import load_json, save_json

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))


def run() -> None:
    requested_topic = os.getenv("PRODUCT_TOPIC", "").strip()
    topics = [requested_topic] if requested_topic else CONFIG["topics"]

    opportunities = rank(collect(topics, CONFIG["max_candidates"]))
    save_json(str(ROOT / "state" / "opportunities.json"), opportunities)

    eligible = [
        x for x in opportunities
        if x["opportunity_score"] >= CONFIG["min_opportunity_score"]
    ]

    if requested_topic:
        eligible.insert(0, {
            "source": "manual-topic",
            "title": requested_topic,
            "url": "",
            "summary": f"User requested a product around: {requested_topic}",
            "score_hint": 100,
            "opportunity_score": 100,
        })

    if not eligible and not requested_topic:
        print("No opportunity passed the threshold.")
        return

    if not eligible and requested_topic:
        eligible = [{
            "source": "manual-topic",
            "title": requested_topic,
            "url": "",
            "summary": f"User requested a product around: {requested_topic}",
            "score_hint": 100,
            "opportunity_score": 100,
        }]

    spec = generate_product_spec(eligible[:CONFIG["top_candidates_for_ai"]])
    if not spec.get("title") or not spec.get("deliverables"):
        raise RuntimeError("Incomplete product specification")

    product_dir = build_product(spec, str(ROOT / "dist"))
    history = load_json(str(ROOT / "state" / "history.json"), [])
    history.append({
        "title": spec["title"],
        "price_usd": spec.get("price_usd"),
        "source_score": eligible[0]["opportunity_score"],
        "requested_topic": requested_topic or None,
        "product_dir": str(product_dir.relative_to(ROOT)),
    })
    save_json(str(ROOT / "state" / "history.json"), history[-100:])

    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    (site / "latest.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    zip_path = product_dir.with_suffix(".zip")
    xlsx_path = product_dir / "tracking-template.xlsx"
    pdf_path = product_dir / "quick-start-guide.pdf"

    title = str(spec["title"])
    price = str(spec.get("price_usd", "?"))
    score = str(eligible[0]["opportunity_score"])
    topic_label = requested_topic or "Otomatik araştırma"

    message = (
        "Yeni ürün oluşturuldu.\n\n"
        f"Ürün: {title}\n"
        f"Fiyat: USD {price}\n"
        f"Skor: {score}/100"
    )

    email_sent = send_email(
        subject=f"Autonomous Income Engine - {title}",
        html=(
            "<h2>Yeni ürün oluşturuldu</h2>"
            f"<p><b>Ürün:</b> {title}</p>"
            f"<p><b>Fiyat:</b> USD {price}</p>"
            f"<p><b>Fırsat skoru:</b> {score}/100</p>"
            f"<p><b>Konu:</b> {topic_label}</p>"
        ),
        attachments=[xlsx_path, pdf_path, zip_path],
    )

    telegram_sent = send_telegram(message, xlsx_path)

    print(json.dumps({
        "spec": spec,
        "email_sent": email_sent,
        "telegram_sent": telegram_sent,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
