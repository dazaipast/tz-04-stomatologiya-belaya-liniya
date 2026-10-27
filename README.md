# Белая линия — сайт клиники

| Что | Ссылка |
| --- | --- |
| Сайт на Vercel | https://PROJECT.vercel.app |
| Таблица заявок «BelayaLiniya — Leads» | вставить ссылку после создания таблицы |
| Отчёт Looker Studio «БЕЛАЯ ЛИНИЯ — hygiene_nov_2026» | вставить ссылку после сборки отчёта |
| Instagram | https://www.instagram.com/belaya_liniya_dent/ |
| ВКонтакте | https://vk.com/belaya_liniya_dent |
| Telegram | https://t.me/belaya_liniya_dent |
| YouTube | https://www.youtube.com/@belaya_liniya_dent |
| Reel с автоответами | вставить ссылку на Reel после публикации |

Идентификатор ресурса GA4: `G-XXXXXXXXXX`

Доступ Viewer к ресурсу GA4 выдан: ___ (e-mail Заказчика)

Сайт — статические HTML, CSS и JavaScript без сборки. CRM HubSpot из раздела 9 не подключалась. Лист `crm_import` в таблице готовит данные для импорта, но в HubSpot они не загружаются.

## Что уже сделано в коде

- 8 страниц и `404.html`, шапка, подвал, предупреждение и лицензия.
- События раздела 4, включая `map_open` и `license_open`, в `js/analytics.js`.
- UTM сохраняются в `sessionStorage`. Реестр — `docs/utm.csv`, QR — `docs/qr-u-12.png`, афиша — `docs/afisha.pdf`.
- Форма записи и приёмник `apps-script/Code.gs`.
- Прайс, памятка и файл лицензии в `files/`.

## Что подключить своими аккаунтами

1. Замените адрес и идентификатор GA4:

```text
python tools/set_public_url.py https://имя.vercel.app G-ВАШИД
```

2. Создайте ресурс GA4 по `docs/ga4.md`.
3. Создайте таблицу и веб-приложение Apps Script по `docs/leads.md`, затем снова запустите команду выше и третьим аргументом передайте URL вида `https://script.google.com/macros/s/.../exec`.
4. Опубликуйте ссылки из реестра и настройте ManyChat по `docs/utm.md` и `docs/manychat.md`.
5. Соберите исследования GA4 и отчёт Looker Studio по `docs/looker-studio.md`. Снимки положите в `screens/`.
6. После проверок заполните числа в `docs/report.md`.

Локальный просмотр: `python -m http.server 8080`

Не получилось: подключить живые кабинеты GA4, Google Таблицу, Apps Script, соцсети, ManyChat, Looker Studio и Vercel — для них нужен аккаунт исполнителя. CRM HubSpot не подключалась по решению исполнителя.

Нейросеть использовалась для: структуры сайта, текстов, вёрстки, портретов врачей, PDF, QR и журнала в `docs/prompts.md`.
