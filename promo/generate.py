# -*- coding: utf-8 -*-
"""Генератор рекламного комплекта ВБС (Pillow)."""
import os, qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT
os.makedirs(OUT, exist_ok=True)

URL = 'https://mozgikom-commits.github.io/vbs-landing/'

BG = (18, 20, 17)
CARD = (29, 33, 27)
ACCENT = (232, 111, 28)
ACCENT_DARK = (52, 40, 26)
OLIVE = (109, 124, 89)
TEXT = (242, 244, 240)
MUTED = (156, 163, 150)
WHITE = (255, 255, 255)
BOX = (46, 52, 42)

F_OSWALD = os.path.join(ROOT, 'fonts/Oswald-var.ttf')
F_INTER = os.path.join(ROOT, 'fonts/Inter-var.ttf')

def font(family, size, weight='Regular'):
    f = ImageFont.truetype(F_OSWALD if family == 'o' else F_INTER, size)
    if weight != 'Regular':
        try: f.set_variation_by_name(weight)
        except Exception: pass
    return f

def logo(size):
    im = Image.open(os.path.join(ROOT, '..', 'logo.png')).convert('RGBA')
    return im.resize((size, size), Image.LANCZOS)

def put_logo(canvas, box_xy, size, alpha=1.0):
    lg = logo(size)
    if alpha < 1.0:
        a = lg.split()[3].point(lambda v: int(v * alpha))
        lg.putalpha(a)
    canvas.paste(lg, box_xy, lg)

def qr_image(url, px):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
    q.add_data(url); q.make(fit=True)
    im = q.make_image(fill_color='black', back_color='white').convert('RGB')
    return im.resize((px, px), Image.NEAREST)

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def hud(canvas, box, radius=0, fill=CARD, outline=BOX, ow=4, tick=1.0, ticks=True):
    d = ImageDraw.Draw(canvas)
    if radius: d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=ow)
    else: d.rectangle(box, fill=fill, outline=outline, width=ow)
    if ticks:
        x0, y0, x1, y1 = box
        L = int(46 * tick); W = max(4, int(7 * tick)); inset = int(12 * tick)
        for (cx, cy, dx, dy) in ((x0 + inset, y0 + inset, 1, 1), (x1 - inset, y1 - inset, -1, -1)):
            d.line([(cx, cy + L * dy), (cx, cy)], fill=ACCENT, width=W)
            d.line([(cx, cy), (cx + L * dx, cy)], fill=ACCENT, width=W)
    return d

def plate(canvas, center_xy, text, f, pad_x, pad_y, border=ACCENT, bg=ACCENT_DARK, fg=ACCENT, bw=4):
    d = ImageDraw.Draw(canvas)
    w = tw(d, text, f); b = d.textbbox((0, 0), text, font=f); h = b[3] - b[1]
    cx, cy = center_xy
    box = [cx - w // 2 - pad_x, cy - h // 2 - pad_y, cx + w // 2 + pad_x, cy + h // 2 + pad_y]
    d.rectangle(box, fill=bg, outline=border, width=bw)
    d.text((cx, cy), text, font=f, fill=fg, anchor='mm')
    return box

# ---------- 1. Плакат А4 ----------
def build_poster():
    W, H = 2480, 3508
    M = 150
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)

    put_logo(im, (W - 1050, 2050), 1050, alpha=0.035)

    d.rectangle([0, 0, W, 26], fill=ACCENT)

    y = 150
    put_logo(im, ((W - 400) // 2, y), 400); y += 430

    plate(im, (W // 2, y + 45), 'МИНОБОРОНЫ РФ  •  ПРИМОРСКИЙ КРАЙ, С. ПОКРОВКА', font('o', 50, 'Medium'), 44, 26)
    y += 130

    d.text((W // 2, y), 'ВОЙСКА БЕСПИЛОТНЫХ СИСТЕМ:', font=font('o', 128, 'Bold'), fill=TEXT, anchor='ma')
    y += 165
    d.text((W // 2, y), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 128, 'Bold'), fill=ACCENT, anchor='ma')
    y += 200

    # выплаты
    box_h = 400
    w1 = 1060
    hud(im, [M, y, M + w1, y + box_h], radius=10)
    d.text((M + w1 // 2, y + 90), '2 000 000 ₽', font=font('o', 120, 'Bold'), fill=ACCENT, anchor='ma')
    d.text((M + w1 // 2, y + 265), 'единовременно', font=font('i', 54), fill=TEXT, anchor='ma')
    d.text((M + w1 // 2, y + 330), 'при заключении контракта', font=font('i', 44), fill=MUTED, anchor='ma')

    x2 = W - M - w1
    hud(im, [x2, y, x2 + w1, y + box_h], radius=10)
    d.text((x2 + w1 // 2, y + 90), 'от 210 000 ₽/мес.', font=font('o', 96, 'Bold'), fill=ACCENT, anchor='ma')
    d.text((x2 + w1 // 2, y + 265), 'довольствие', font=font('i', 54), fill=TEXT, anchor='ma')
    d.text((x2 + w1 // 2, y + 330), 'в зоне СВО', font=font('i', 44), fill=MUTED, anchor='ma')
    y += box_h + 90

    # QR
    qr_px = 940
    pad = 64
    qx = (W - qr_px) // 2
    outer = [qx - pad, y, qx + qr_px + pad, y + qr_px + 2 * pad]
    d.rounded_rectangle(outer, radius=48, fill=ACCENT)
    d.rounded_rectangle([outer[0] + 16, outer[1] + 16, outer[2] - 16, outer[3] - 16], radius=36, fill=WHITE)
    im.paste(qr_image(URL, qr_px), (qx, y + pad))
    y = outer[3] + 60

    d.text((W // 2, y), 'НАВЕДИ КАМЕРУ И ПОДАЙ ЗАЯВКУ ОНЛАЙН', font=font('o', 74, 'SemiBold'), fill=TEXT, anchor='ma')
    y += 110

    # буллиты
    bullets = ['100% служба только в войсках БПЛА', 'Бесплатное обучение с нуля',
               'Диплом оператора БВС', '41 социальная гарантия']
    f_b = font('i', 50, 'SemiBold')
    cols = [M + 30, W // 2 + 40]
    rows = [y, y + 78]
    for i, b in enumerate(bullets):
        x = cols[i % 2]; yy = rows[i // 2]
        d.text((x, yy), '▪', font=font('i', 50, 'Bold'), fill=ACCENT, anchor='la')
        d.text((x + 46, yy), b, font=f_b, fill=TEXT, anchor='la')
    y = rows[1] + 120

    d.line([(M, y), (W - M, y)], fill=BOX, width=4)
    y += 56

    d.text((W // 2, y), 'ПРИМОРСКИЙ КРАЙ, С. ПОКРОВКА  •  ПУНКТ ОТБОРА', font=font('o', 66, 'SemiBold'), fill=TEXT, anchor='ma')
    y += 96
    d.text((W // 2, y), 'Октябрьский район Приморского края. Точный расчёт выплат — в пункте отбора.',
           font=font('i', 36), fill=MUTED, anchor='ma')
    y += 90

    d.rectangle([0, H - 26, W, H], fill=ACCENT)

    im.save(os.path.join(OUT, 'Плакат_А4_ВБС.png'), 'PNG')
    im.save(os.path.join(OUT, 'Плакат_А4_ВБС.pdf'), 'PDF', resolution=300)
    return y, ['Плакат_А4_ВБС.png', 'Плакат_А4_ВБС.pdf']

# ---------- 2. Квадратный пост ----------
def build_square():
    S = 1080
    im = Image.new('RGB', (S, S), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, S, 10], fill=ACCENT)

    put_logo(im, (56, 58), 148)
    d.text((228, 82), 'ВОЙСКА БЕСПИЛОТНЫХ СИСТЕМ', font=font('o', 33, 'Bold'), fill=TEXT, anchor='la')
    d.text((228, 130), 'Приморский край • с. Покровка', font=font('i', 24), fill=MUTED, anchor='la')

    d.text((56, 240), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 82, 'Bold'), fill=TEXT, anchor='la')
    d.text((56, 330), 'В ВОЙСКАХ БПЛА', font=font('o', 82, 'Bold'), fill=ACCENT, anchor='la')

    hud(im, [56, 452, 500, 690], radius=8, tick=0.8)
    d.text((278, 500), '2 000 000 ₽', font=font('o', 68, 'Bold'), fill=ACCENT, anchor='ma')
    d.text((278, 600), 'единовременно', font=font('i', 26), fill=TEXT, anchor='ma')
    d.text((278, 638), 'при заключении контракта', font=font('i', 20), fill=MUTED, anchor='ma')

    hud(im, [524, 452, 1024, 690], radius=8, tick=0.8)
    d.text((774, 500), 'от 210 000 ₽/мес.', font=font('o', 56, 'Bold'), fill=ACCENT, anchor='ma')
    d.text((774, 600), 'довольствие', font=font('i', 26), fill=TEXT, anchor='ma')
    d.text((774, 638), 'в зоне СВО', font=font('i', 20), fill=MUTED, anchor='ma')

    bullets = ['100% служба только в войсках БПЛА', 'Бесплатное обучение с нуля',
               'Диплом оператора БВС', '41 социальная гарантия']
    f_b = font('i', 30, 'SemiBold')
    y = 742
    for b in bullets:
        d.text((60, y), '▪', font=font('i', 30, 'Bold'), fill=ACCENT, anchor='la')
        d.text((94, y), b, font=f_b, fill=TEXT, anchor='la')
        y += 50

    box = [56, 946, 1024, 1024]
    d.rounded_rectangle(box, radius=12, fill=ACCENT)
    d.text((540, 985), 'ПОДРОБНОСТИ И ЗАЯВКА — ПО ССЫЛКЕ В ПОСТЕ',
           font=font('o', 34, 'SemiBold'), fill=(17, 19, 16), anchor='mm')

    im.save(os.path.join(OUT, 'Пост_Telegram_Instagram_1080x1080.png'), 'PNG')
    return ['Пост_Telegram_Instagram_1080x1080.png']

# ---------- 3. Сторис ----------
def build_story():
    W, H = 1080, 1920
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 12], fill=ACCENT)

    put_logo(im, ((W - 190) // 2, 246), 190)
    plate(im, (W // 2, 500), 'ПРИМОРСКИЙ КРАЙ  •  С. ПОКРОВКА', font('o', 32, 'Medium'), 36, 18)

    d.text((W // 2, 566), 'ВОЙСКА БЕСПИЛОТНЫХ', font=font('o', 72, 'Bold'), fill=TEXT, anchor='ma')
    d.text((W // 2, 654), 'СИСТЕМ', font=font('o', 72, 'Bold'), fill=TEXT, anchor='ma')
    d.text((W // 2, 752), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 58, 'Bold'), fill=ACCENT, anchor='ma')

    hud(im, [70, 860, 1010, 1080], radius=8, tick=0.9)
    d.text((540, 900), '2 000 000 ₽', font=font('o', 86, 'Bold'), fill=ACCENT, anchor='ma')
    d.text((540, 1010), 'единовременно при заключении', font=font('i', 26), fill=TEXT, anchor='ma')

    hud(im, [70, 1110, 1010, 1300], radius=8, tick=0.9)
    d.text((540, 1150), 'от 210 000 ₽/мес.', font=font('o', 64, 'Bold'), fill=ACCENT, anchor='ma')
    d.text((540, 1240), 'довольствие в зоне СВО', font=font('i', 26), fill=TEXT, anchor='ma')

    frame = [70, 1350, 1010, 1690]
    d.rounded_rectangle(frame, radius=24, outline=ACCENT, width=6)
    d.text((540, 1450), 'ПЕРЕХОДИ ПО ССЫЛКЕ НИЖЕ', font=font('o', 54, 'SemiBold'), fill=ACCENT, anchor='mm')
    d.text((540, 1530), 'здесь будет стикер-ссылка', font=font('i', 28), fill=MUTED, anchor='mm')

    d.text((540, 1800), '100% БПЛА • бесплатное обучение • диплом оператора БВС',
           font=font('i', 24), fill=MUTED, anchor='mm')

    im.save(os.path.join(OUT, 'Сторис_Telegram_Instagram_1080x1920.png'), 'PNG')
    return ['Сторис_Telegram_Instagram_1080x1920.png']

poster_end, files = build_poster()
files += build_square()
files += build_story()
print('низ плаката: y =', poster_end, '(полотно 3508)')
print('CREATED:')
for c in files:
    print('  %-46s %5d KB' % (c, os.path.getsize(os.path.join(OUT, c)) // 1024))
