# -*- coding: utf-8 -*-
import csv
import html
import json
import sys
from pathlib import Path
from urllib.parse import quote, urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import DOCTORS, FILTERS, PRICES, SERVICES, SIGNS, STEPS, UTM_ROWS

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "tools" / "site_config.json").read_text(encoding="utf-8"))
ORIGIN = CONFIG["publicOrigin"].rstrip("/")
GA_ID = CONFIG["gaMeasurementId"]
SOCIAL = CONFIG["social"]
PHONE_TEXT = "+7\u00a0(900)\u00a0404-04-40"
PHONE_TEL = "+79004040440"
EMAIL = "reception@belaya-liniya.example"
ADDRESS = "614\u00a0115, г.\u00a0Новоозёрск, ул.\u00a0Садовая, д.\u00a03, пом.\u00a01"
LICENSE = "Лицензия на медицинскую деятельность №\u00a0Л041-99999-99/00000001"
WARNING = "Имеются противопоказания. Необходима консультация специалиста."
MAP = "https://yandex.ru/maps/?text=" + quote("Новоозёрск, улица Садовая, 3")

NAV = [
    ("services.html", "Услуги"),
    ("doctors.html", "Врачи"),
    ("prices.html", "Цены"),
    ("checkup.html", "Памятка"),
    ("contacts.html", "Запись"),
]


def esc(value):
    return html.escape(str(value), quote=True)


def money(value):
    text = esc(value)
    while True:
        updated = __import__("re").sub(r"(\d) (\d)", lambda match: match.group(1) + "\u00a0" + match.group(2), text)
        if updated == text:
            return text
        text = updated


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


def service_by_id(service_id):
    for service in SERVICES:
        if service["id"] == service_id:
            return service
    raise KeyError(service_id)


def social_links(section):
    items = [
        ("instagram", "Instagram", SOCIAL["instagram"]),
        ("vk", "ВКонтакте", SOCIAL["vk"]),
        ("telegram", "Telegram", SOCIAL["telegram"]),
        ("youtube", "YouTube", SOCIAL["youtube"]),
    ]
    links = []
    for network, label, href in items:
        links.append(
            f'<a href="{esc(href)}" target="_blank" rel="noopener noreferrer" data-event="social_click" data-network="{network}" data-page-section="{section}">{label}</a>'
        )
    return '<div class="socials">' + "".join(links) + "</div>"


def header(active):
    links = []
    for href, label in NAV:
        current = ' aria-current="page"' if href == active else ""
        links.append(f'<a href="{href}"{current}>{label}</a>')
    return f"""
    <div class="header-wrap">
      <div class="topbar">
        <div class="wrap topbar__inner">
          <span>Новоозёрск, ул.&nbsp;Садовая, д.&nbsp;3, пом.&nbsp;1</span>
          <span>Пн–сб 09:00–21:00 · Вс 10:00–16:00</span>
        </div>
      </div>
      <header class="header">
        <a class="logo" href="index.html">
          <svg class="logo__tooth" viewBox="0 0 48 60" aria-hidden="true">
            <path fill="#12A3A0" d="M10 11C5 12 2 19 3.5 27 4.5 32 6.7 35 7.8 37.2 8.2 42 7.6 48 8.2 52 9.4 56.2 13.8 56.4 15 53.6 16 50.5 16.8 45 18 40.5 19.6 35.4 21.8 32.4 24 32.4 26.2 32.4 28.4 35.4 30 40.5 31.2 45 32 50.5 33 53.6 34.2 56.4 38.6 56.2 39.8 52 40.4 48 39.8 42 40.2 37.2 41.3 35 43.5 32 44.5 27 46 19 43 12 38 11 34 10.2 31 14.2 28.8 16.2 27.2 17.6 25.6 18.2 24 18.2 22.4 18.2 20.8 17.6 19.2 16.2 17 14.2 14 10.2 10 11z"/>
            <rect fill="#fff" x="14.6" y="19.2" width="18.8" height="2.15"/>
          </svg>
          <span>
            <span class="logo__name">Белая линия</span>
            <span class="logo__sub">стоматологическая клиника</span>
          </span>
        </a>
        <input class="nav-check" id="nav-toggle" type="checkbox">
        <nav class="nav" id="site-nav" aria-label="Основное меню">{''.join(links)}</nav>
        <a class="phone-link" href="tel:{PHONE_TEL}" data-event="contact_click" data-contact-type="phone">
          <span class="phone-link__full">{PHONE_TEXT}</span>
          <span class="phone-link__short">Позвонить</span>
        </a>
        <label class="nav-toggle" for="nav-toggle">Меню</label>
      </header>
    </div>"""


def footer():
    return f"""
    <footer class="footer">
      <div class="wrap footer-grid">
        <div>
          <p class="footer-label">Клиника</p>
          <strong>Белая линия</strong>
          <p>{ADDRESS}</p>
          <p><a href="{esc(MAP)}" target="_blank" rel="noopener noreferrer" data-event="map_open" data-map-service="yandex">Открыть на Яндекс Картах</a></p>
          <p>{LICENSE}</p>
          <p><a href="files/license.pdf" data-event="license_open" data-page-section="footer">Открыть файл лицензии</a></p>
        </div>
        <div>
          <p class="footer-label">Запись</p>
          <p>Пн–сб 09:00–21:00<br>Вс 10:00–16:00</p>
          <p><a href="tel:{PHONE_TEL}" data-event="contact_click" data-contact-type="phone">{PHONE_TEXT}</a></p>
          <p><a href="mailto:{EMAIL}" data-event="contact_click" data-contact-type="email">{EMAIL}</a></p>
          <p><a href="privacy.html">Политика конфиденциальности</a></p>
        </div>
        <div>
          <p class="footer-label">Соцсети</p>
          {social_links("footer")}
        </div>
      </div>
      <div class="wrap">
        <p class="warning">{WARNING}</p>
        <p class="legal">ООО «Белая линия» · ИНН 9904301776 · КПП 990401001 · ОГРН 1209900007731</p>
      </div>
    </footer>"""


def document(filename, title, description, body, active, robots="index, follow"):
    url = f"{ORIGIN}/{filename}"
    image = f"{ORIGIN}/img/og.jpg"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="{robots}">
  <meta name="theme-color" content="#22303A">
  <link rel="canonical" href="{esc(url)}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:url" content="{esc(url)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{esc(image)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <link rel="icon" href="img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/styles.css">
  <script async src="https://www.googletagmanager.com/gtag/js?id={esc(GA_ID)}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{esc(GA_ID)}');
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Dentist",
    "name": "Белая линия",
    "url": "{esc(ORIGIN)}/",
    "telephone": "{PHONE_TEL}",
    "email": "{EMAIL}",
    "address": {{
      "@type": "PostalAddress",
      "postalCode": "614115",
      "addressLocality": "Новоозёрск",
      "streetAddress": "ул. Садовая, д. 3, пом. 1",
      "addressCountry": "RU"
    }}
  }}
  </script>
</head>
<body>
  <a class="skip-link" href="#content">К содержанию</a>
  {header(active)}
  <main id="content">
    {body}
  </main>
  {footer()}
  <script src="js/config.js" defer></script>
  <script src="js/utm.js" defer></script>
  <script src="js/analytics.js" defer></script>
  <script src="js/main.js" defer></script>
  <script src="js/form.js" defer></script>
</body>
</html>
"""


def write_page(filename, title, description, body, active="", robots="index, follow"):
    text = document(filename, title, description, body, active, robots)
    (ROOT / filename).write_text(text, encoding="utf-8", newline="\n")


def service_slider(slides):
    items = "".join(f'<div class="slider__slide">{slide}</div>' for slide in slides)
    arrow_prev = (
        '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
        '<path d="M14.5 5.5 8 12l6.5 6.5" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    arrow_next = (
        '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
        '<path d="M9.5 5.5 16 12l-6.5 6.5" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    return f"""<div class="slider" data-slider aria-roledescription="карусель" aria-label="Услуги">
      <div class="slider__viewport">
        <div class="slider__track">{items}</div>
      </div>
      <div class="slider__nav">
        <button class="slider__arrow" type="button" data-slider-prev aria-label="Предыдущая услуга">{arrow_prev}</button>
        <p class="slider__count" data-slider-count aria-live="polite">1 из {len(slides)}</p>
        <button class="slider__arrow" type="button" data-slider-next aria-label="Следующая услуга">{arrow_next}</button>
      </div>
    </div>"""


def doctor_photo(doctor, eager=False):
    alt = f"{doctor['name']}, {doctor['specialty']}. Изображение создано нейросетью."
    loading = "eager" if eager else "lazy"
    return f"""
      <img src="img/doctors/{doctor['id']}.webp" width="720" height="960" alt="{esc(alt)}" loading="{loading}">
      <p class="ai-note">Изображение создано нейросетью</p>"""


def ops_list(doctor):
    items = "".join(
        f"<li><span>{esc(name)}</span><span>{money(price)}</span></li>"
        for name, price in doctor["ops"]
    )
    return f'<ul class="ops">{items}</ul>'


def doctor_stage(doctors):
    slides = []
    for doctor in doctors:
        slides.append(
            f"""<article class="stage__slide" id="doc-{doctor['id']}" data-specialty="{esc(doctor['key'])}">
              <figure class="stage__photo">
                <img src="img/doctors/{doctor['id']}.webp" width="720" height="960" alt="{esc(doctor['name'])}, {esc(doctor['specialty'])}. Изображение создано нейросетью." loading="lazy">
                <figcaption>Изображение создано нейросетью</figcaption>
              </figure>
              <div class="stage__card">
                <p class="kicker">{esc(doctor['specialty'])}</p>
                <h3>{esc(doctor['name'])}</h3>
                <dl class="stage__facts">
                  <div><dt>Стаж</dt><dd>{esc(doctor['years'])}</dd></div>
                  <div><dt>Диплом</dt><dd>{esc(doctor['edu'])}</dd></div>
                </dl>
                <p class="stage__advice"><span>Рекомендация</span>{esc(doctor['advice'])}</p>
                <h4>Проводит</h4>
                {ops_list(doctor)}
                <div class="actions">
                  <a class="btn" href="contacts.html?service={doctor['service']}" data-event="cta_click" data-button-name="doctor_{doctor['id']}" data-page-section="doctors">Записаться к врачу</a>
                  <a class="btn btn--ghost" href="doctors.html#doc-{doctor['id']}" data-event="doctor_view" data-doctor-id="{doctor['id']}" data-specialty="{esc(doctor['key'])}">Карточка врача</a>
                </div>
              </div>
            </article>"""
        )
    items = "".join(slides)
    arrow_prev = (
        '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
        '<path d="M14.5 5.5 8 12l6.5 6.5" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    arrow_next = (
        '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
        '<path d="M9.5 5.5 16 12l-6.5 6.5" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    return f"""<div class="stage" data-stage tabindex="0" aria-roledescription="карусель" aria-label="Врачи">
      <div class="stage__viewport">
        <div class="stage__track">{items}</div>
      </div>
      <div class="stage__nav">
        <button class="slider__arrow" type="button" data-stage-prev aria-label="Предыдущий врач">{arrow_prev}</button>
        <p class="slider__count" data-stage-count aria-live="polite">1 из {len(doctors)}</p>
        <button class="slider__arrow" type="button" data-stage-next aria-label="Следующий врач">{arrow_next}</button>
      </div>
    </div>"""


def page_index():
    links = []
    for service in SERVICES:
        links.append(
            f"""<a class="direction-card" href="services.html#{service['id']}" data-event="service_view" data-service-name="{esc(service['name'])}">
              <h3>{esc(service['name'])}</h3>
              <p>{esc(service['summary'])}</p>
              <span>{service['price']}</span>
            </a>"""
        )
    doctors = list(DOCTORS)
    steps = []
    for title, text in STEPS:
        steps.append(f"<li><h3>{esc(title)}</h3><p>{esc(text)}</p></li>")
    body = f"""
    <section class="hero hero--doctors">
      <div class="wrap">
        <div class="hero-intro">
          <p class="kicker">Акция с 1 ноября 2026 · гигиена и консультация 3&nbsp;900&nbsp;₽</p>
          <h1>Запишитесь к врачу</h1>
          <p class="lead">Листайте карточки: стаж, диплом, рекомендация и приёмы этого врача. Запись на карточке. Портреты созданы нейросетью.</p>
        </div>
        {doctor_stage(doctors)}
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="section__head">
          <div>
            <div class="rule" aria-hidden="true"></div>
            <h2>Направления</h2>
            <p>Шесть услуг. Фото и подробности — в разделе «Услуги».</p>
          </div>
          <a class="btn btn--ghost" href="services.html">Все услуги</a>
        </div>
        <div class="direction-list">{''.join(links)}</div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="rule" aria-hidden="true"></div>
        <h2>Как проходит первый приём</h2>
        <ol class="steps">{''.join(steps)}</ol>
      </div>
    </section>
    <section class="section section--cta">
      <div class="wrap">
        <div class="cta-band">
          <div>
            <h2>Гигиена и консультация за 3&nbsp;900&nbsp;₽</h2>
            <p>Оставьте заявку: администратор подтвердит удобное время.</p>
          </div>
          <a class="btn btn--light" href="contacts.html?service=hygiene" data-event="cta_click" data-button-name="final_promo" data-page-section="final">Записаться</a>
        </div>
      </div>
    </section>"""
    write_page(
        "index.html",
        "Белая линия — гигиена и консультация за 3 900 ₽",
        "Стоматология «Белая линия» в Новоозёрске. Акция: профессиональная гигиена и консультация за 3 900 ₽. Запись на приём.",
        body,
        "",
    )


def page_services():
    cards = []
    for service in SERVICES:
        if service["id"] == "kids":
            continue
        cards.append(
            f"""<article class="service-card service-card--photo" id="{service['id']}">
              <img class="service-card__bg" src="img/services/{service['id']}.webp" width="1400" height="1050" alt="{esc(service['name'])}. Изображение создано нейросетью.">
              <div class="service-card__body">
                <button class="card-hit" type="button" data-event="service_view" data-service-name="{esc(service['name'])}"><span class="visually-hidden">{esc(service['name'])}</span></button>
                <p class="ai-note">Изображение создано нейросетью</p>
                <h2>{esc(service['name'])}</h2>
                <p>{esc(service['text'])}</p>
                <p class="muted">{esc(service['duration'])}</p>
                <p class="price">{service['price']}</p>
                <a class="btn btn--light" href="contacts.html?service={service['code']}" data-event="select_service" data-service-name="{esc(service['name'])}" data-price-from="{service['price_from']}">Записаться на эту услугу</a>
              </div>
            </article>"""
        )
    kids = service_by_id("kids")
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div class="rule" aria-hidden="true"></div>
        <h1>Услуги</h1>
        <p class="lead">В клинике шесть направлений. Цену, которой нет в этом списке, администратор не называет по сайту.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        {service_slider(cards)}
      </div>
    </section>
    <section class="section band" id="kids">
      <div class="wrap split">
        <div>
          <div class="rule" aria-hidden="true"></div>
          <h2>Детская стоматология</h2>
          <p>{esc(kids['text'])}</p>
          <p>На приёме родитель остаётся рядом. Врач говорит, что увидел, без обещаний «как будет дальше»: это решается после осмотра.</p>
          <p class="muted">{esc(kids['duration'])}</p>
          <p class="price">{kids['price']}</p>
          <a class="btn" href="contacts.html?service=kids" data-event="select_service" data-service-name="{esc(kids['name'])}" data-price-from="{kids['price_from']}">Записаться на эту услугу</a>
        </div>
        <figure class="photo-panel">
          <img src="img/services/kids.webp" width="1400" height="1050" alt="Детский приём: ребёнок в кресле, рядом родитель и врач. Изображение создано нейросетью.">
          <figcaption>Изображение создано нейросетью</figcaption>
          <button class="card-hit" type="button" data-event="service_view" data-service-name="{esc(kids['name'])}"><span class="visually-hidden">Детский приём</span></button>
        </figure>
      </div>
    </section>"""
    write_page(
        "services.html",
        "Услуги — Белая линия",
        "Услуги клиники «Белая линия»: консультация, гигиена, лечение кариеса, имплантация, брекеты и детский приём.",
        body,
        "services.html",
    )


def page_doctors():
    filters = []
    for key in FILTERS:
        pressed = "true" if key == "все" else "false"
        label = "Все" if key == "все" else key[:1].upper() + key[1:]
        filters.append(
            f'<button type="button" data-event="doctor_filter" data-specialty="{esc(key)}" aria-pressed="{pressed}">{esc(label)}</button>'
        )
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div class="rule" aria-hidden="true"></div>
        <h1>Врачи</h1>
        <p class="lead">Девять врачей: четыре терапевта, хирург-имплантолог, два ортодонта, детский стоматолог и гигиенист. Имена вымышленные, портреты созданы нейросетью. На карточке стаж, диплом, рекомендация и приёмы.</p>
        <div class="filters" role="group" aria-label="Фильтр по специальности">{''.join(filters)}</div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        {doctor_stage(DOCTORS)}
      </div>
    </section>"""
    write_page(
        "doctors.html",
        "Врачи — Белая линия",
        "Врачи клиники «Белая линия»: терапевты, хирург-имплантолог, ортодонты, детский стоматолог и гигиенист.",
        body,
        "doctors.html",
    )


def page_prices():
    rows = []
    for direction, position, price in PRICES:
        search = f"{direction} {position} {price}"
        rows.append(
            f'<tr data-price-row data-search="{esc(search)}"><td>{esc(direction)}</td><td>{esc(position)}</td><td>{money(price)}</td></tr>'
        )
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div class="rule" aria-hidden="true"></div>
        <h1>Цены</h1>
        <p class="lead">В таблице только шесть услуг клиники. Повторные строки — разные поводы визита с той же опубликованной ценой.</p>
        <div class="search-row">
          <div>
            <label for="price-search">Поиск по прайсу</label>
            <input id="price-search" type="search" data-event="price_search" data-price-search placeholder="Например, кариес" autocomplete="off">
          </div>
          <a class="btn btn--ghost" href="files/prices.pdf" download>Скачать прайс PDF</a>
        </div>
        <p data-price-count>Показано {len(PRICES)} из {len(PRICES)}</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <div class="table-wrap">
          <table>
            <caption class="visually-hidden">Прайс-лист клиники Белая линия</caption>
            <thead><tr><th>Услуга</th><th>Позиция</th><th>Цена</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        <p class="empty-note" data-price-empty hidden>По этому запросу позиций нет. Попробуйте «гигиена» или «кариес».</p>
      </div>
    </section>"""
    write_page(
        "prices.html",
        "Цены — Белая линия",
        "Цены стоматологии «Белая линия»: консультация 900 ₽, гигиена от 3 900 ₽ по акции, лечение кариеса от 5 200 ₽.",
        body,
        "prices.html",
    )


def page_checkup():
    items = "".join(f"<li>{esc(sign)}</li>" for sign in SIGNS)
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div class="rule" aria-hidden="true"></div>
        <h1>7 признаков, что пора к стоматологу</h1>
        <p class="lead">Короткий список для себя или для ребёнка 3–14 лет. Это не диагноз: чтобы понять, что происходит, нужен осмотр.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap split">
        <ol class="checklist">{items}</ol>
        <div>
          <div class="promo">
            <div>
              <h2>Промокод</h2>
              <code>CHECK500</code>
              <p>Скидка 500&nbsp;₽. Назовите код администратору, когда будете записываться.</p>
            </div>
            <button class="btn" type="button" data-event="promo_copy" data-promo-code="CHECK500"><span data-copy-label>Скопировать</span></button>
          </div>
          <p data-copy-status role="status"></p>
          <div class="actions">
            <a class="btn btn--ghost" href="files/checkup.pdf" download>Скачать памятку PDF</a>
            <a class="btn" href="contacts.html?service=hygiene" data-event="cta_click" data-button-name="checkup_book" data-page-section="checkup">Записаться</a>
          </div>
        </div>
      </div>
    </section>"""
    write_page(
        "checkup.html",
        "Памятка пациенту — Белая линия",
        "7 признаков, что пора к стоматологу. Памятка клиники «Белая линия» и промокод CHECK500 на 500 ₽.",
        body,
        "checkup.html",
    )


def page_contacts():
    options = ['<option value="">Выберите услугу</option>']
    labels = {
        "consult": "Консультация — 900 ₽",
        "hygiene": "Профессиональная гигиена — акция 3 900 ₽",
        "treatment": "Лечение кариеса — от 5 200 ₽",
        "implant": "Имплантация под ключ — от 48 000 ₽",
        "braces": "Брекеты — от 65 000 ₽",
        "kids": "Детский приём — 1 200 ₽",
    }
    for service in SERVICES:
        options.append(f'<option value="{service["code"]}">{esc(labels[service["code"]])}</option>')
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div class="rule" aria-hidden="true"></div>
        <h1>Запись и контакты</h1>
        <p class="lead">Администратор перезвонит и подтвердит время. Сведения о здоровье, жалобы и диагноз на сайте не собираем.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap contact-grid">
        <form id="lead-form" novalidate>
          <div id="form-alert" class="form-alert" role="alert" hidden></div>
          <input type="hidden" name="request_id">
          <div class="field" data-field="name">
            <label for="name">Имя</label>
            <input id="name" name="name" type="text" autocomplete="name" maxlength="60" aria-describedby="name-error" required>
            <p class="field-error" id="name-error"></p>
          </div>
          <div class="field" data-field="phone">
            <label for="phone">Телефон</label>
            <input id="phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 900 000-00-00" aria-describedby="phone-error" required>
            <p class="field-error" id="phone-error"></p>
          </div>
          <div class="field" data-field="email">
            <label for="email">E-mail, если удобно</label>
            <input id="email" name="email" type="email" autocomplete="email" aria-describedby="email-error">
            <p class="field-error" id="email-error"></p>
          </div>
          <div class="field" data-field="service">
            <label for="service">Услуга</label>
            <select id="service" name="service" aria-describedby="service-error" required>{''.join(options)}</select>
            <p class="field-error" id="service-error"></p>
          </div>
          <div class="field" data-field="preferred_time">
            <label for="preferred_time">Удобное время</label>
            <select id="preferred_time" name="preferred_time" aria-describedby="time-error" required>
              <option value="">Выберите время</option>
              <option value="morning">Утро</option>
              <option value="day">День</option>
              <option value="evening">Вечер</option>
              <option value="weekend">Выходные</option>
            </select>
            <p class="field-error" id="time-error"></p>
          </div>
          <p class="muted">Клиника работает пн–сб 09:00–21:00, вс 10:00–16:00. Точный час подтвердит администратор.</p>
          <div class="field" data-field="consent">
            <label class="consent">
              <input type="checkbox" name="consent" value="yes" aria-describedby="consent-error">
              <span>Соглашаюсь на обработку персональных данных по <a href="privacy.html">политике конфиденциальности</a>.</span>
            </label>
            <p class="field-error" id="consent-error"></p>
          </div>
          <button class="btn" type="submit" data-event="cta_click" data-button-name="contacts_submit" data-page-section="contacts">Отправить заявку</button>
        </form>
        <div class="info-card">
          <h2>Как связаться</h2>
          <p><a href="tel:{PHONE_TEL}" data-event="contact_click" data-contact-type="phone">{PHONE_TEXT}</a></p>
          <p><a href="mailto:{EMAIL}" data-event="contact_click" data-contact-type="email">{EMAIL}</a></p>
          <p>{ADDRESS}</p>
          <div class="messenger-row socials">
            <a href="{esc(SOCIAL['telegram'])}" target="_blank" rel="noopener noreferrer" data-event="messenger_click" data-messenger="telegram">Telegram</a>
            <a href="{esc(SOCIAL['whatsapp'])}" target="_blank" rel="noopener noreferrer" data-event="messenger_click" data-messenger="whatsapp">WhatsApp</a>
          </div>
          <p><a href="{esc(MAP)}" target="_blank" rel="noopener noreferrer" data-event="map_open" data-map-service="yandex">Открыть адрес на Яндекс Картах</a></p>
          <p>{LICENSE}</p>
          <p><a href="files/license.pdf" data-event="license_open" data-page-section="contacts">Открыть файл лицензии</a></p>
        </div>
      </div>
    </section>"""
    write_page(
        "contacts.html",
        "Запись на приём — Белая линия",
        "Запись на приём в клинику «Белая линия»: форма, телефон +7 (900) 404-04-40, Садовая, 3.",
        body,
        "contacts.html",
    )


def page_thanks():
    body = f"""
    <section class="page-hero">
      <div class="wrap">
        <div class="rule" aria-hidden="true"></div>
        <h1>Заявка принята</h1>
        <p>Номер вашей заявки:</p>
        <p class="request-id" data-request-id>Номер появится после отправки формы</p>
        <p>Администратор свяжется с вами по телефону, который вы указали.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap split">
        <div>
          <h2>Что взять на приём</h2>
          <ul>
            <li>Паспорт.</li>
            <li>Полис ДМС, если он есть.</li>
            <li>Промокод CHECK500, если хотите им воспользоваться.</li>
          </ul>
        </div>
        <div class="panel info-card">
          <h2>Мы в соцсетях</h2>
          {social_links("thanks")}
        </div>
      </div>
    </section>"""
    write_page(
        "thanks.html",
        "Заявка отправлена — Белая линия",
        "Заявка в клинику «Белая линия» отправлена. Номер заявки и что взять с собой на приём.",
        body,
        "",
        "noindex",
    )


def page_privacy():
    body = f"""
    <section class="page-hero">
      <div class="wrap prose">
        <div class="rule" aria-hidden="true"></div>
        <h1>Политика конфиденциальности</h1>
        <p>Политика описывает, как ООО «Белая линия» обрабатывает персональные данные посетителей сайта. Текст подготовлен с учётом Федерального закона №\u00a0152-ФЗ «О персональных данных».</p>
        <h2>Оператор</h2>
        <p>ООО «Белая линия», {ADDRESS}. ИНН 9904301776, КПП 990401001, ОГРН 1209900007731. Телефон {PHONE_TEXT}, e-mail {EMAIL}.</p>
        <h2>Какие данные обрабатываются</h2>
        <p>В заявке: имя, телефон, услуга, удобное время, номер заявки, метки источника перехода. E-mail — только если вы его указали. Технические события сайта уходят в Google Analytics 4 без имени, телефона и e-mail.</p>
        <h2>Какие данные не собираются</h2>
        <p>На сайте нет полей для жалоб, диагнозов и других сведений о здоровье. Такие сведения относятся к специальной категории, и форма их не запрашивает.</p>
        <h2>Цели</h2>
        <p>Связаться с вами, подтвердить запись и понять, из какого канала пришла заявка. Данные не продаются и не используются для обещаний результата лечения.</p>
        <h2>Основание</h2>
        <p>Согласие, которое вы отмечаете в форме. Без согласия заявка не отправляется. Согласие можно отозвать письмом на {EMAIL}.</p>
        <h2>Срок хранения</h2>
        <p>Заявка хранится, пока администратор ведёт запись до первого приёма или отказа, и удаляется по запросу. В аналитике остаются обезличенные события.</p>
        <h2>Кому передаются данные</h2>
        <p>Заявки записываются в Google Таблицу клиники. События без контактных данных получает Google Analytics 4. Доступ к таблице есть у сотрудников, которые ведут запись.</p>
        <h2>Ваши права</h2>
        <p>Вы можете запросить доступ к своим данным, уточнение или удаление. Напишите на {EMAIL} и укажите номер заявки, если он сохранился.</p>
      </div>
    </section>"""
    write_page(
        "privacy.html",
        "Политика конфиденциальности — Белая линия",
        "Политика обработки персональных данных ООО «Белая линия» в соответствии с 152-ФЗ.",
        body,
        "",
    )


def page_404():
    body = """
    <section class="page-hero">
      <div class="wrap">
        <div class="rule" aria-hidden="true"></div>
        <h1>Такой страницы нет</h1>
        <p class="lead">Ссылка устарела или в адресе опечатка. Можно вернуться на главную или сразу оставить заявку.</p>
        <div class="actions">
          <a class="btn" href="index.html">На главную</a>
          <a class="btn btn--ghost" href="contacts.html">Записаться</a>
        </div>
      </div>
    </section>"""
    write_page(
        "404.html",
        "Страница не найдена — Белая линия",
        "Страница не найдена на сайте стоматологии «Белая линия».",
        body,
        "",
        "noindex",
    )


def write_config():
    payload = "window.BL_CONFIG = " + json.dumps(
        {"appsScriptUrl": CONFIG.get("appsScriptUrl", "")},
        ensure_ascii=False,
        indent=2,
    ) + ";\n"
    (ROOT / "js" / "config.js").write_text(payload, encoding="utf-8", newline="\n")


def write_utm():
    path = ROOT / "docs" / "utm.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "номер",
                "канал",
                "размещение",
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_content",
                "страница",
                "полная ссылка",
                "короткая ссылка",
                "адрес публикации",
                "дата публикации",
            ]
        )
        for row in UTM_ROWS:
            number, channel, place, source, medium, campaign, content, page = row
            writer.writerow(
                [
                    number,
                    channel,
                    place,
                    source,
                    medium,
                    campaign,
                    content,
                    page,
                    full_link(page, source, medium, campaign, content),
                    "",
                    "",
                    "",
                ]
            )


def main():
    if len(PRICES) < 30:
        raise SystemExit("В прайсе меньше 30 позиций")
    page_index()
    page_services()
    page_doctors()
    page_prices()
    page_checkup()
    page_contacts()
    page_thanks()
    page_privacy()
    page_404()
    write_config()
    write_utm()
    print(f"pages: 9, prices: {len(PRICES)}, origin: {ORIGIN}")


if __name__ == "__main__":
    main()
