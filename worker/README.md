# Прокси для заявок (Cloudflare Worker)

Токен Telegram-бота живёт только в секретах воркера. В `index.html` его быть не должно:
страница на GitHub Pages публичная, любой мог открыть исходник и писать от имени бота.

## Что делает воркер

- принимает `POST` с JSON `{ name, phone, age, role, website, ts }`
- проверяет `Origin` и `Referer` — только `https://mozgikom-commits.github.io/vbs-landing/`
- ловушка для ботов: поле `website` должно быть пустым
- отсекает отправку быстрее 2,5 секунд после загрузки страницы (и старше часа)
- проверяет телефон (ровно 11 цифр, начинается с 7), возраст (18–60), длину имени
- троттлинг по IP: не чаще 1 заявки в 20 секунд, не больше 15 в час
- пересылает текст в Telegram Bot API от своего имени

## Деплой

```bash
cd worker
npx wrangler@latest deploy            # нужен CLOUDFLARE_API_TOKEN или wrangler login
npx wrangler@latest secret put TG_BOT_TOKEN
npx wrangler@latest secret put TG_CHAT_ID
```

После деплоя wrangler печатает адрес вида
`https://vbs-lead-proxy.<account-subdomain>.workers.dev` — его нужно прописать
в `index.html` в константу `LEAD_ENDPOINT`, после чего удалить оттуда
`TG_BOT_TOKEN` / `TG_CHAT_ID`.

## Проверка

```bash
curl -i -X POST https://vbs-lead-proxy.<sub>.workers.dev \
  -H 'Origin: https://mozgikom-commits.github.io' \
  -H 'Referer: https://mozgikom-commits.github.io/vbs-landing/' \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"Тест\",\"phone\":\"+7 (924) 123-45-67\",\"age\":\"27\",\"role\":\"\",\"website\":\"\",\"ts\":$(( $(date +%s) * 1000 - 5000 ))}"
```

Ответ `{"ok":true}` — заявка ушла в Telegram. Повторный запрос в течение 20 секунд даст `429`.
