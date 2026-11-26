# -*- coding: utf-8 -*-
"""Рекламный комплект ВБС в стиле текущего сайта: светлая тема, триколор, фото с лендинга."""
import os, random, qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT
URL = 'https://mozgikom-commits.github.io/vbs-landing/'

BG      = (255, 255, 255)
ALT     = (238, 242, 248)
INK     = (11, 18, 32)
BLUE    = (0, 57, 166)
RED     = (213, 43, 30)
MUTED   = (82, 97, 122)
BORDER  = (210, 219, 232)
WHITE   = (255, 255, 255)

F_OSWALD = os.path.join(ROOT, 'fonts/Oswald-var.ttf')
F_INTER = os.path.join(ROOT, 'fonts/Inter-var.ttf')
HERO = os.path.join(ROOT, '..', 'hero.webp')
LOGO = os.path.join(ROOT, '..', 'logo.png')

def font(family, size, weight='Regular'):
    f = ImageFont.truetype(F_OSWALD if family == 'o' else F_INTER, size)
    if weight != 'Regular':
        try: f.set_variation_by_name(weight)
        except Exception: pass
    return f

def logo(size):
    return Image.open(LOGO).convert('RGBA').resize((size, size), Image.LANCZOS)

def put_logo(canvas, xy, size):
    lg = logo(size)
    canvas.paste(lg, xy, lg)

def photo(path, box_w, box_h, focus_y=0.5):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    scale = max(box_w / w, box_h / h)
    nw, nh = int(w * scale + .5), int(h * scale + .5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - box_w) // 2
    top = int((nh - box_h) * focus_y)
    return im.crop((left, top, left + box_w, top + box_h))

def tricolor(canvas, y, h, w):
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, y, w // 3, y + h], fill=WHITE)
    d.rectangle([w // 3, y, 2 * w // 3, y + h], fill=BLUE)
    d.rectangle([2 * w // 3, y, w, y + h], fill=RED)
    d.line([(0, y + h), (w, y + h)], fill=BORDER, width=2)

def torn(canvas, y, depth, color=WHITE, seed=7, step=70):
    d = ImageDraw.Draw(canvas)
    rnd = random.Random(seed)
    W, H = canvas.size
    pts = [(0, y + rnd.randint(-6, 6))]
    x = 0
    while x < W:
        x = min(W, x + step)
        pts.append((x, y + rnd.randint(-depth // 2, depth // 2)))
    pts += [(W, H), (0, H)]
    d.polygon(pts, fill=color)

def hud(canvas, box, radius=16, fill=WHITE, outline=BORDER, ow=4, tick=1.0, accent=BLUE):
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=ow)
    x0, y0, x1, y1 = box
    L = int(46 * tick); Wd = max(4, int(7 * tick)); inset = int(14 * tick)
    for (cx, cy, dx, dy) in ((x0 + inset, y0 + inset, 1, 1), (x1 - inset, y1 - inset, -1, -1)):
        d.line([(cx, cy + L * dy), (cx, cy)], fill=accent, width=Wd)
        d.line([(cx, cy), (cx + L * dx, cy)], fill=accent, width=Wd)
    return d

def plate(canvas, center, text, f, pad_x, pad_y, border=BLUE, bg=(244, 247, 252), fg=BLUE, bw=4):
    d = ImageDraw.Draw(canvas)
    w = d.textlength(text, font=f); b = d.textbbox((0, 0), text, font=f); h = b[3] - b[1]
    cx, cy = center
    box = [cx - w / 2 - pad_x, cy - h / 2 - pad_y, cx + w / 2 + pad_x, cy + h / 2 + pad_y]
    d.rectangle(box, fill=bg, outline=border, width=bw)
    d.text((cx, cy), text, font=f, fill=fg, anchor='mm')
    return box

def qr_image(px):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
    q.add_data(URL); q.make(fit=True)
    return q.make_image(fill_color='black', back_color='white').convert('RGB').resize((px, px), Image.NEAREST)

def shade(canvas, ph_h, W, strength=150):
    scrim = Image.new('RGBA', (W, ph_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    for i in range(ph_h):
        sd.line([(0, i), (W, i)], fill=(8, 15, 30, int(strength * (i / ph_h) ** 1.4)))
    canvas.paste(scrim, (0, 0), scrim)

def build_poster():
    W, H = 2480, 3508
    M = 150
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)

    ph_h = 880
    im.paste(photo(HERO, W, ph_h, focus_y=0.32), (0, 0))
    shade(im, ph_h, W, 140)
    torn(im, ph_h - 8, 100, color=BG, seed=11)
    tricolor(im, 0, 22, W)

    put_logo(im, ((W - 280) // 2, ph_h - 140), 280)

    y = ph_h + 190
    plate(im, (W // 2, y), 'МИНОБОРОНЫ РФ  •  ПРИМОРСКИЙ КРАЙ, С. ПОКРОВКА', font('o', 48, 'Medium'), 44, 26)
    y += 112

    d.text((W // 2, y), 'ВОЙСКА БЕСПИЛОТНЫХ СИСТЕМ:', font=font('o', 124, 'Bold'), fill=INK, anchor='ma')
    y += 158
    d.text((W // 2, y), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 124, 'Bold'), fill=BLUE, anchor='ma')
    y += 178

    w1 = 1060; box_h = 360
    hud(im, [M, y, M + w1, y + box_h], radius=18)
    d.text((M + w1 // 2, y + 78), '2 000 000 ₽', font=font('o', 118, 'Bold'), fill=RED, anchor='ma')
    d.text((M + w1 // 2, y + 228), 'единовременно', font=font('i', 50), fill=INK, anchor='ma')
    d.text((M + w1 // 2, y + 292), 'при заключении контракта', font=font('i', 38), fill=MUTED, anchor='ma')

    x2 = W - M - w1
    hud(im, [x2, y, x2 + w1, y + box_h], radius=18)
    d.text((x2 + w1 // 2, y + 78), 'от 210 000 ₽/мес.', font=font('o', 92, 'Bold'), fill=RED, anchor='ma')
    d.text((x2 + w1 // 2, y + 228), 'довольствие', font=font('i', 50), fill=INK, anchor='ma')
    d.text((x2 + w1 // 2, y + 292), 'в зоне СВО', font=font('i', 38), fill=MUTED, anchor='ma')
    y += box_h + 70

    qr_px = 860; pad = 52
    qx = (W - qr_px) // 2
    outer = [qx - pad, y, qx + qr_px + pad, y + qr_px + 2 * pad]
    d.rounded_rectangle(outer, radius=40, fill=BLUE)
    d.rounded_rectangle([outer[0] + 14, outer[1] + 14, outer[2] - 14, outer[3] - 14], radius=30, fill=WHITE)
    im.paste(qr_image(qr_px), (qx, y + pad))
    y = outer[3] + 44

    d.text((W // 2, y), 'НАВЕДИ КАМЕРУ И ПОДАЙ ЗАЯВКУ ОНЛАЙН', font=font('o', 68, 'SemiBold'), fill=BLUE, anchor='ma')
    y += 88

    bullets = ['100% служба только в войсках БПЛА', 'Бесплатное обучение с нуля',
               'Диплом оператора БВС', '41 социальная гарантия']
    cols = [M + 30, W // 2 + 40]
    rows = [y, y + 70]
    for i, b in enumerate(bullets):
        x = cols[i % 2]; yy = rows[i // 2]
        d.text((x, yy), '▪', font=font('i', 46, 'Bold'), fill=RED, anchor='la')
        d.text((x + 44, yy), b, font=font('i', 44, 'SemiBold'), fill=INK, anchor='la')
    y = rows[1] + 96

    d.line([(M, y), (W - M, y)], fill=BORDER, width=4)
    y += 48
    d.text((W // 2, y), 'ПРИМОРСКИЙ КРАЙ, С. ПОКРОВКА  •  ПУНКТ ОТБОРА', font=font('o', 60, 'SemiBold'), fill=INK, anchor='ma')
    y += 84
    d.text((W // 2, y), 'Октябрьский район Приморского края. Точный расчёт выплат — в пункте отбора.',
           font=font('i', 32), fill=MUTED, anchor='ma')

    tricolor(im, H - 22, 22, W)
    im.save(os.path.join(OUT, 'Плакат_А4_ВБС.png'), 'PNG')
    im.save(os.path.join(OUT, 'Плакат_А4_ВБС.pdf'), 'PDF', resolution=300)
    return y, ['Плакат_А4_ВБС.png', 'Плакат_А4_ВБС.pdf']

def build_square():
    S = 1080
    im = Image.new('RGB', (S, S), BG)
    d = ImageDraw.Draw(im)

    ph_h = 356
    im.paste(photo(HERO, S, ph_h, focus_y=0.28), (0, 0))
    shade(im, ph_h, S, 145)
    torn(im, ph_h - 6, 50, color=BG, seed=5, step=54)
    tricolor(im, 0, 10, S)

    put_logo(im, (44, ph_h - 14), 122)
    d.text((186, ph_h + 6), 'ВОЙСКА БЕСПИЛОТНЫХ СИСТЕМ', font=font('o', 30, 'Bold'), fill=INK, anchor='la')
    d.text((186, ph_h + 48), 'Приморский край • с. Покровка', font=font('i', 22), fill=MUTED, anchor='la')

    d.text((56, 494), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 72, 'Bold'), fill=INK, anchor='la')
    d.text((56, 574), 'В ВОЙСКАХ БПЛА', font=font('o', 72, 'Bold'), fill=BLUE, anchor='la')

    hud(im, [56, 674, 500, 894], radius=14, tick=0.8)
    d.text((278, 710), '2 000 000 ₽', font=font('o', 62, 'Bold'), fill=RED, anchor='ma')
    d.text((278, 798), 'единовременно', font=font('i', 24), fill=INK, anchor='ma')
    d.text((278, 834), 'при заключении контракта', font=font('i', 18), fill=MUTED, anchor='ma')

    hud(im, [524, 674, 1024, 894], radius=14, tick=0.8)
    d.text((774, 710), 'от 210 000 ₽/мес.', font=font('o', 50, 'Bold'), fill=RED, anchor='ma')
    d.text((774, 798), 'довольствие', font=font('i', 24), fill=INK, anchor='ma')
    d.text((774, 834), 'в зоне СВО', font=font('i', 18), fill=MUTED, anchor='ma')

    bullets = ['100% служба только в войсках БПЛА', 'Бесплатное обучение с нуля',
               'Диплом оператора БВС', '41 социальная гарантия']
    for i, b in enumerate(bullets):
        x = 60 if i % 2 == 0 else 560
        yy = 922 + (i // 2) * 40
        d.text((x, yy), '▪', font=font('i', 23, 'Bold'), fill=RED, anchor='la')
        d.text((x + 26, yy), b, font=font('i', 20, 'SemiBold'), fill=INK, anchor='la')

    box = [56, 1006, 1024, 1064]
    d.rounded_rectangle(box, radius=14, fill=BLUE)
    d.text((540, 1035), 'ПОДРОБНОСТИ И ЗАЯВКА — ПО ССЫЛКЕ В ПОСТЕ',
           font=font('o', 28, 'SemiBold'), fill=WHITE, anchor='mm')

    im.save(os.path.join(OUT, 'Пост_Telegram_Instagram_1080x1080.png'), 'PNG')
    return ['Пост_Telegram_Instagram_1080x1080.png']

def build_story():
    W, H = 1080, 1920
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)

    ph_h = 640
    im.paste(photo(HERO, W, ph_h, focus_y=0.28), (0, 0))
    shade(im, ph_h, W, 150)
    torn(im, ph_h - 6, 60, color=BG, seed=9, step=56)
    tricolor(im, 0, 12, W)

    put_logo(im, ((W - 176) // 2, ph_h - 96), 176)
    d.text((W // 2, ph_h + 104), 'ВОЙСКА БЕСПИЛОТНЫХ', font=font('o', 66, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, ph_h + 188), 'СИСТЕМ', font=font('o', 66, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, ph_h + 276), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 52, 'Bold'), fill=BLUE, anchor='ma')

    y = ph_h + 372
    hud(im, [70, y, 1010, y + 206], radius=16, tick=0.9)
    d.text((540, y + 30), '2 000 000 ₽', font=font('o', 80, 'Bold'), fill=RED, anchor='ma')
    d.text((540, y + 136), 'единовременно при заключении', font=font('i', 25), fill=INK, anchor='ma')

    y += 230
    hud(im, [70, y, 1010, y + 180], radius=16, tick=0.9)
    d.text((540, y + 26), 'от 210 000 ₽/мес.', font=font('o', 58, 'Bold'), fill=RED, anchor='ma')
    d.text((540, y + 112), 'довольствие в зоне СВО', font=font('i', 25), fill=INK, anchor='ma')

    frame = [70, 1430, 1010, 1756]
    d.rounded_rectangle(frame, radius=26, outline=BLUE, width=6)
    d.text((540, 1520), 'ПЕРЕХОДИ ПО ССЫЛКЕ НИЖЕ', font=font('o', 50, 'SemiBold'), fill=BLUE, anchor='mm')
    d.text((540, 1592), 'здесь будет стикер-ссылка', font=font('i', 26), fill=MUTED, anchor='mm')

    d.text((540, 1832), '100% БПЛА • бесплатное обучение • диплом оператора БВС',
           font=font('i', 23), fill=MUTED, anchor='mm')

    im.save(os.path.join(OUT, 'Сторис_Telegram_Instagram_1080x1920.png'), 'PNG')
    return ['Сторис_Telegram_Instagram_1080x1920.png']

end_y, files = build_poster()
files += build_square()
files += build_story()
print('низ плаката y =', end_y, '(3508)')
for f in files:
    print('  %-46s %5d KB' % (f, os.path.getsize(os.path.join(OUT, f)) // 1024))
