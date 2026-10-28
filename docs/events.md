# События GA4

Единственный вызов `gtag("event", …)` находится в `js/analytics.js`, строка 33, функция `send`. Имена и параметры обрезаются до 40 и 100 символов. Имя, телефон и e-mail в аналитику не передаются.

Режим `debug_mode` в коде не включался.

## Автоматические события

Их собирает расширенная статистика потока. Отдельного `gtag("event")` для них нет. Тег `gtag('config', 'G-7BTPH14B6G')` стоит в `<head>` каждой страницы, включая `404.html`.

| Событие | Когда | Параметры |
| --- | --- | --- |
| page_view | открытие страницы | page_location, page_title |
| scroll | прокрутка до 90 % | percent_scrolled |
| click | переход на внешний сайт | link_url, outbound |
| file_download | ссылка на PDF: `files/prices.pdf`, `files/checkup.pdf`, `files/license.pdf` | file_name, file_extension |
| form_start | первое действие с формой `#lead-form` | form_id |
| form_submit | отправка формы | form_id |

## Свои события

| Событие | Где срабатывает | Строка отправки | Пример параметров |
| --- | --- | --- | --- |
| cta_click | кнопки записи: главная, врачи, памятка, отправка формы | `js/analytics.js:102` | button_name=`hero_promo`, page_section=`hero` |
| service_view | карточка услуги | `js/analytics.js:102` | service_name=`Профессиональная гигиена` |
| select_service | «Записаться на эту услугу» | `js/analytics.js:102` | service_name=`Детский приём`, price_from=`1200` |
| doctor_view | карточка врача | `js/analytics.js:102` | doctor_id=`lebedev`, specialty=`хирург-имплантолог` |
| doctor_filter | кнопки фильтра на `doctors.html` | `js/analytics.js:102` | specialty=`ортодонт` |
| price_search | поле поиска, через 1 секунду после ввода | `js/analytics.js:117` | search_term=`имплант`, results_count=`7` |
| promo_copy | кнопка «Скопировать» на `checkup.html` | `js/analytics.js:98` | promo_code=`CHECK500` |
| contact_click | телефон и e-mail | `js/analytics.js:102` | contact_type=`phone` |
| messenger_click | Telegram и WhatsApp на странице записи | `js/analytics.js:102` | messenger=`telegram` |
| social_click | соцсети в подвале и на `thanks.html` | `js/analytics.js:102` | network=`instagram`, page_section=`footer` |
| form_error | форма не прошла проверку или приёмник вернул ошибку | вызов `js/form.js:61`, отправка `js/analytics.js:33` | field_name=`phone`, error_type=`format` |
| generate_lead | только после ответа `{ "ok": true }` | вызов `js/form.js:163`, отправка `js/analytics.js:33` | lead_service=`hygiene`, lead_source=`instagram` |
| map_open | ссылка на Яндекс Карты | `js/analytics.js:102` | map_service=`yandex` |
| license_open | файл лицензии | `js/analytics.js:102` | page_section=`footer` |

При ошибке приёмника `error_type` равен `server`.

## Пользовательские параметры

В Admin → Custom definitions, область Event:

| Параметр | События |
| --- | --- |
| button_name | cta_click |
| page_section | cta_click, social_click |
| service_name | service_view, select_service |
| specialty | doctor_view, doctor_filter |
| search_term | price_search |
| lead_service | generate_lead |
| messenger | messenger_click |

Ключевые события ресурса, и только они: `generate_lead`, `contact_click`, `messenger_click`.
