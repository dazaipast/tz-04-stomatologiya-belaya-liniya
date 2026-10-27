# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlretrieve

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import DOCTORS, PRICES, SIGNS, UTM_ROWS

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "tools" / "site_config.json").read_text(encoding="utf-8"))
ORIGIN = CONFIG["publicOrigin"].rstrip("/")
ASSETS = Path(r"C:\Users\dazai\.cursor\projects\c-Users-dazai-OneDrive-Desktop-blue-line-dental\assets")
FONT_DIR = ROOT / "fonts"


def full_link(page, source, medium, campaign, content):
    fragment = ""
    path = page
    if "#" in page:
        path, fragment = page.split("#", 1)
        fragment = "#" + fragment
    query = urlencode(
        {
            "utm_source": source,
            "utm_medium": medium,
            "utm_campaign": campaign,
            "utm_content": content,
        }
    )
    return f"{ORIGIN}/{path}?{query}{fragment}"


def u12_url():
    row = next(item for item in UTM_ROWS if item[0] == "U-12")
    return full_link(row[7], row[3], row[4], row[5], row[6])


def ensure_fonts():
    FONT_DIR.mkdir(exist_ok=True)
    files = {
        "Manrope-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/manrope/static/Manrope-Regular.ttf",
        "Manrope-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/manrope/static/Manrope-Bold.ttf",
    }
    for name, url in files.items():
        target = FONT_DIR / name
        if target.exists() and target.stat().st_size > 10000:
            continue
        try:
            urlretrieve(url, target)
        except Exception:
            if target.exists():
                target.unlink()


def font_path(bold=False):
    preferred = FONT_DIR / ("Manrope-Bold.ttf" if bold else "Manrope-Regular.ttf")
    if preferred.exists() and preferred.stat().st_size > 10000:
        return preferred
    windows = Path(r"C:\Windows\Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf")
    return windows


def pil_font(size, bold=False):
    return ImageFont.truetype(str(font_path(bold)), size)


def crop_portrait(path):
    image = Image.open(path).convert("RGB")
    width, height = image.size
    target = 3 / 4
    if width / height > target:
        new_width = int(height * target)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target)
        top = max(0, int((height - new_height) * 0.12))
        if top + new_height > height:
            top = height - new_height
        image = image.crop((0, top, width, top + new_height))
    return image.resize((720, 960), Image.Resampling.LANCZOS)


def save_webp(image, path):
    quality = 74
    while quality >= 46:
        image.save(path, "WEBP", quality=quality, method=6)
        if path.stat().st_size <= 300 * 1024:
            return
        quality -= 8
    raise SystemExit(f"{path} больше 300 КБ")


def build_portraits():
    folder = ROOT / "img" / "doctors"
    folder.mkdir(parents=True, exist_ok=True)
    made = []
    for doctor in DOCTORS:
        source = ASSETS / f"doctor-{doctor['id']}.jpg"
        if not source.exists():
            source = ASSETS / f"doctor-{doctor['id']}.png"
        if not source.exists():
            raise SystemExit(f"Нет портрета {doctor['id']}: {source}")
        target = folder / f"{doctor['id']}.webp"
        save_webp(crop_portrait(source), target)
        made.append(target)
    return made


def build_og():
    image = Image.new("RGB", (1200, 630), "#F1F5F5")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 18, 630), fill="#0F8F8A")
    draw.text((72, 120), "Белая линия", font=pil_font(72, True), fill="#22303A")
    draw.text((72, 230), "Гигиена и консультация", font=pil_font(54, True), fill="#0B6460")
    draw.text((72, 320), "3 900 ₽", font=pil_font(92, True), fill="#0B6460")
    draw.text((72, 470), "Новоозёрск, ул. Садовая, 3", font=pil_font(32), fill="#22303A")
    target = ROOT / "img" / "og.jpg"
    image.save(target, "JPEG", quality=82, optimize=True)
    if target.stat().st_size > 300 * 1024:
        image.save(target, "JPEG", quality=60, optimize=True)
    return target


def build_qr(url):
    import qrcode

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#22303A", back_color="white").convert("RGB")
    target = ROOT / "docs" / "qr-u-12.png"
    image.save(target, "PNG")
    return target


def pdf_base():
    from fpdf import FPDF

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    regular = str(font_path(False))
    bold = str(font_path(True))
    pdf.add_font("Site", "", regular)
    pdf.add_font("Site", "B", bold)
    return pdf


def write_block(pdf, text, size=12, bold=False, height=7):
    pdf.set_font("Site", "B" if bold else "", size)
    pdf.multi_cell(0, height, text, new_x="LMARGIN", new_y="NEXT")


def write_warning(pdf):
    pdf.ln(6)
    write_block(pdf, "Имеются противопоказания. Необходима консультация специалиста.", size=12, bold=True)
    write_block(pdf, "Лицензия на медицинскую деятельность № Л041-99999-99/00000001")
    write_block(pdf, "ООО «Белая линия», 614115, г. Новоозёрск, ул. Садовая, д. 3, пом. 1")
    write_block(pdf, "+7 (900) 404-04-40")


def build_pdfs(qr_path):
    files = ROOT / "files"
    files.mkdir(exist_ok=True)

    prices = pdf_base()
    prices.add_page()
    write_block(prices, "Белая линия. Прайс", size=18, bold=True, height=10)
    write_block(prices, "Опубликованы только услуги и цены из сведений клиники. Строки с одинаковой ценой — разные поводы визита.")
    prices.ln(2)
    for direction, position, price in PRICES:
        write_block(prices, f"{direction}. {position}", size=12, bold=True, height=6)
        write_block(prices, price, height=6)
        prices.ln(1)
    write_warning(prices)
    prices.output(files / "prices.pdf")

    checkup = pdf_base()
    checkup.add_page()
    write_block(checkup, "7 признаков, что пора к стоматологу", size=18, bold=True, height=10)
    write_block(checkup, "Список не заменяет осмотр.")
    checkup.ln(2)
    for index, sign in enumerate(SIGNS, start=1):
        write_block(checkup, f"{index}. {sign}")
    checkup.ln(2)
    write_block(checkup, "Промокод CHECK500 — скидка 500 ₽", size=14, bold=True, height=8)
    write_block(checkup, "Назовите код администратору при записи.")
    write_warning(checkup)
    checkup.output(files / "checkup.pdf")

    license_pdf = pdf_base()
    license_pdf.add_page()
    write_block(license_pdf, "Сведения о лицензии", size=18, bold=True, height=10)
    license_pdf.ln(4)
    write_block(license_pdf, "ООО «Белая линия»", size=13, height=8)
    write_block(license_pdf, "Лицензия на медицинскую деятельность № Л041-99999-99/00000001", size=13, height=8)
    write_block(license_pdf, "614115, г. Новоозёрск, ул. Садовая, д. 3, пом. 1", size=13, height=8)
    write_block(license_pdf, "+7 (900) 404-04-40", size=13, height=8)
    license_pdf.ln(4)
    write_block(license_pdf, "Имеются противопоказания. Необходима консультация специалиста.", size=13, bold=True, height=8)
    license_pdf.output(files / "license.pdf")

    poster = pdf_base()
    poster.add_page()
    poster.set_fill_color(15, 143, 138)
    poster.rect(0, 0, 12, 297, "F")
    poster.set_xy(22, 22)
    poster.set_font("Site", "B", 28)
    poster.multi_cell(110, 12, "Белая линия", new_x="LMARGIN", new_y="NEXT")
    poster.set_x(22)
    poster.set_font("Site", "", 14)
    poster.multi_cell(110, 8, "Стоматологическая клиника", new_x="LMARGIN", new_y="NEXT")
    poster.ln(8)
    poster.set_x(22)
    poster.set_font("Site", "B", 20)
    poster.multi_cell(160, 10, "Профессиональная гигиена и консультация", new_x="LMARGIN", new_y="NEXT")
    poster.set_x(22)
    poster.set_font("Site", "B", 36)
    poster.multi_cell(160, 16, "3 900 ₽", new_x="LMARGIN", new_y="NEXT")
    poster.set_x(22)
    poster.set_font("Site", "", 14)
    poster.multi_cell(110, 8, "Акция с 1 ноября 2026", new_x="LMARGIN", new_y="NEXT")
    poster.set_x(22)
    poster.multi_cell(110, 8, "Пн–сб 09:00–21:00, вс 10:00–16:00", new_x="LMARGIN", new_y="NEXT")
    poster.set_x(22)
    poster.multi_cell(110, 8, "ул. Садовая, д. 3, пом. 1, Новоозёрск", new_x="LMARGIN", new_y="NEXT")
    poster.set_x(22)
    poster.multi_cell(110, 8, "+7 (900) 404-04-40", new_x="LMARGIN", new_y="NEXT")
    poster.image(str(qr_path), x=128, y=175, w=58)
    poster.set_xy(22, 190)
    poster.set_font("Site", "B", 14)
    poster.multi_cell(90, 8, "Памятка и запись по QR-коду", new_x="LMARGIN", new_y="NEXT")
    poster.set_xy(22, 250)
    poster.set_font("Site", "B", 12)
    poster.multi_cell(170, 7, "Имеются противопоказания. Необходима консультация специалиста.", new_x="LMARGIN", new_y="NEXT")
    poster.set_x(22)
    poster.set_font("Site", "", 12)
    poster.multi_cell(170, 7, "Лицензия № Л041-99999-99/00000001", new_x="LMARGIN", new_y="NEXT")
    poster.output(ROOT / "docs" / "afisha.pdf")


def write_images_md(paths):
    lines = [
        "# Источники изображений",
        "",
        "Портреты врачей сгенерированы нейросетью в Cursor по запросу на учебный сайт. На карточках стоит подпись «Изображение создано нейросетью». Имена врачей вымышленные.",
        "",
        "| Файл | Что это | Источник |",
        "| --- | --- | --- |",
        "| img/favicon.svg | Значок сайта, бирюзовая линия | Нарисован в коде |",
        "| img/og.jpg | Превью ссылки 1200×630 | Собрано программой из текста и фирменных цветов |",
        "| docs/qr-u-12.png | QR строки U-12 | Собрано программой из полной ссылки реестра |",
    ]
    for path in paths:
        size = round(path.stat().st_size / 1024, 1)
        lines.append(f"| {path.relative_to(ROOT).as_posix()} | Портрет врача | Нейросеть, {size} КБ |")
    lines.append("")
    lines.append("Фотографии реальной клиники и чужие стоковые кадры не используются.")
    lines.append("")
    (ROOT / "docs" / "images.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main():
    ensure_fonts()
    portraits = build_portraits()
    build_og()
    url = u12_url()
    qr = build_qr(url)
    build_pdfs(qr)
    write_images_md(portraits)
    print("qr:", url)
    for path in portraits:
        print(path.name, path.stat().st_size)


if __name__ == "__main__":
    main()
