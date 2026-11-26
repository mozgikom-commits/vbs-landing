/**
 * vbs-landing — прокси для заявок в Telegram.
 * Токен бота живёт только здесь (секрет Cloudflare), в HTML его нет.
 *
 * Секреты:
 *   wrangler secret put TG_BOT_TOKEN
 *   wrangler secret put TG_CHAT_ID
 */

const ALLOWED_ORIGIN = 'https://mozgikom-commits.github.io';
const ALLOWED_REFERER_HOST = 'https://mozgikom-commits.github.io/';

const MIN_FILL_MS = 2500;          // быстрее человек форму не заполнит
const MAX_AGE_MS = 60 * 60 * 1000; // вкладка, открытая час назад, уже не считается
const THROTTLE_MS = 20000;         // не чаще одной заявки в 20 секунд с IP
const MAX_PER_HOUR = 15;           // и не больше 15 в час с IP
const MAX_BODY_BYTES = 4096;

const hits = new Map(); // ip -> { last, count, hourStart }

function corsHeaders(origin) {
  const allow = origin === ALLOWED_ORIGIN ? origin : ALLOWED_ORIGIN;
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin'
  };
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), {
    status: status,
    headers: Object.assign({ 'Content-Type': 'application/json; charset=utf-8' }, headers || {})
  });
}

function digits(value) {
  return String(value == null ? '' : value).replace(/\D/g, '');
}

function rateLimited(ip, now) {
  const rec = hits.get(ip);
  if (!rec) {
    hits.set(ip, { last: now, count: 1, hourStart: now });
    return false;
  }
  if (now - rec.last < THROTTLE_MS) return true;
  if (now - rec.hourStart > 3600000) {
    rec.count = 1;
    rec.hourStart = now;
  } else {
    rec.count += 1;
  }
  rec.last = now;
  return rec.count > MAX_PER_HOUR;
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const cors = corsHeaders(origin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== 'POST') {
      return json({ ok: false, error: 'method_not_allowed' }, 405, cors);
    }

    const referer = request.headers.get('Referer') || '';
    const originOk = origin === ALLOWED_ORIGIN;
    // Браузер по умолчанию режет Referer до корня (strict-origin-when-cross-origin),
    // поэтому проверяем только хост, а не путь до /vbs-landing/.
    const refererOk = !referer || referer.indexOf(ALLOWED_REFERER_HOST) === 0;
    if (!originOk || !refererOk) {
      return json({ ok: false, error: 'forbidden_origin' }, 403, cors);
    }

    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (rateLimited(ip, Date.now())) {
      return json({ ok: false, error: 'too_many_requests' }, 429, cors);
    }

    const raw = await request.text();
    if (raw.length > MAX_BODY_BYTES) {
      return json({ ok: false, error: 'payload_too_large' }, 413, cors);
    }

    let data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      return json({ ok: false, error: 'bad_json' }, 400, cors);
    }
    if (!data || typeof data !== 'object') {
      return json({ ok: false, error: 'bad_json' }, 400, cors);
    }

    // ловушка для ботов: поле скрыто от людей, автозаполнялки его находят
    if (String(data.website || '').trim() !== '') {
      return json({ ok: true }, 200, cors);
    }

    const now = Date.now();
    const ts = Number(data.ts);
    if (!ts || now - ts < MIN_FILL_MS || now - ts > MAX_AGE_MS) {
      return json({ ok: false, error: 'stale_form' }, 400, cors);
    }

    const name = String(data.name || '').trim().slice(0, 80);
    const phoneDigits = digits(data.phone);
    const age = parseInt(data.age, 10);
    const role = String(data.role || 'не выбрано').trim().slice(0, 80);

    if (name.length < 2) {
      return json({ ok: false, error: 'bad_name' }, 400, cors);
    }
    if (phoneDigits.length !== 11 || phoneDigits.charAt(0) !== '7') {
      return json({ ok: false, error: 'bad_phone' }, 400, cors);
    }
    if (!Number.isInteger(age) || age < 18 || age > 60) {
      return json({ ok: false, error: 'bad_age' }, 400, cors);
    }

    const phonePretty = '+7 (' + phoneDigits.slice(1, 4) + ') ' + phoneDigits.slice(4, 7) +
      '-' + phoneDigits.slice(7, 9) + '-' + phoneDigits.slice(9, 11);

    const text = [
      '🔔 Новая заявка — ВБС, Приморский край',
      '👤 Имя: ' + name,
      '📞 Телефон: ' + phonePretty,
      '🎂 Возраст: ' + age,
      '🎯 Направление: ' + (role || 'не выбрано'),
      '🕒 ' + new Date(now).toLocaleString('ru-RU', { timeZone: 'Asia/Vladivostok' }) + ' (Владивосток)'
    ].join('\n');

    if (!env.TG_BOT_TOKEN || !env.TG_CHAT_ID) {
      return json({ ok: false, error: 'not_configured' }, 500, cors);
    }

    let tg;
    try {
      tg = await fetch('https://api.telegram.org/bot' + env.TG_BOT_TOKEN + '/sendMessage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: env.TG_CHAT_ID,
          text: text,
          disable_web_page_preview: true
        })
      });
    } catch (e) {
      return json({ ok: false, error: 'telegram_unreachable' }, 502, cors);
    }

    if (!tg.ok) {
      return json({ ok: false, error: 'telegram_error' }, 502, cors);
    }

    return json({ ok: true }, 200, cors);
  }
};
