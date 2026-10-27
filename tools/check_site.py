# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    "index.html",
    "services.html",
    "doctors.html",
    "prices.html",
    "checkup.html",
    "contacts.html",
    "thanks.html",
    "privacy.html",
    "404.html",
]
NEED = [
    "gtag('config'",
    "js/analytics.js",
    "Имеются противопоказания",
    "Л041-99999-99/00000001",
    "og:image",
    "og:title",
    "og:description",
    "<title>",
    'name="description"',
    "img/favicon.svg",
    'lang="ru"',
]
BAD = ["lorem", "ваш текст", "безболезненно", "навсегда", "гарантия 100"]
errors = []
for name in PAGES:
    text = (ROOT / name).read_text(encoding="utf-8").lower()
    original = (ROOT / name).read_text(encoding="utf-8")
    for item in NEED:
        if item.lower() not in text and item not in original:
            errors.append(f"missing {item} in {name}")
    for item in BAD:
        if item in text:
            errors.append(f"forbidden {item} in {name}")
    if "<textarea" in text:
        errors.append(f"textarea in {name}")

prices = (ROOT / "prices.html").read_text(encoding="utf-8")
rows = prices.count("data-price-row")
if rows < 30:
    errors.append(f"price rows {rows}")
doctors = (ROOT / "doctors.html").read_text(encoding="utf-8").count("data-doctor-id")
if doctors != 9:
    errors.append(f"doctors {doctors}")
contacts = (ROOT / "contacts.html").read_text(encoding="utf-8")
if "checked" in contacts:
    errors.append("consent is checked by default")
for field in ["name", "phone", "email", "service", "preferred_time", "consent", "request_id"]:
    if f'name="{field}"' not in contacts:
        errors.append(f"form field {field}")

for path in list((ROOT / "img").rglob("*")) + list((ROOT / "files").glob("*.pdf")):
    if path.is_file() and path.stat().st_size > 300 * 1024:
        errors.append(f"big file {path}")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)
print(f"ok pages={len(PAGES)} prices={rows} doctors={doctors}")
