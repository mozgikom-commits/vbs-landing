# -*- coding: utf-8 -*-
"""Агитационные макеты ВБС: плакат A4, пост, сторис, статус.
Стиль сайта: светлая тема, триколор, фото с лендинга крупно и без затемнения."""
import os, random, qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT
URL = 'https://mozgikom-commits.github.io/vbs-landing/'

BG     = (255, 255, 255)
INK    = (11, 18, 32)
BLUE   = (0, 57, 166)
RED    = (213, 43, 30)
MUTED  = (82, 97, 122)
BORDER = (210, 219, 232)
WHITE  = (255, 255, 255)

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
    lg = logo(size); canvas.paste(lg, xy, lg)

def photo(box_w, box_h, focus_y=0.5, focus_x=0.5):
    im = Image.open(HERO).convert('RGB')
    w, h = im.size
    scale = max(box_w / w, box_h / h)
    nw, nh = int(w * scale + .5), int(h * scale + .5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = int((nw - box_w) * focus_x)
    top = int((nh - box_h) * focus_y)
    return im.crop((left, top, left + box_w, top + box_h))

def tricolor(canvas, y, h):
    d = ImageDraw.Draw(canvas); W = canvas.width
    d.rectangle([0, y, W // 3, y + h], fill=WHITE)
    d.rectangle([W // 3, y, 2 * W // 3, y + h], fill=BLUE)
    d.rectangle([2 * W // 3, y, W, y + h], fill=RED)

def torn(canvas, y, depth, color=BG, seed=7, step=70):
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

def hud(canvas, box, radius=16, tick=1.0, accent=BLUE, fill=WHITE, outline=BORDER, ow=4):
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=ow)
    x0, y0, x1, y1 = box
    L = int(44 * tick); Wd = max(4, int(7 * tick)); inset = int(14 * tick)
    for (cx, cy, dx, dy) in ((x0 + inset, y0 + inset, 1, 1), (x1 - inset, y1 - inset, -1, -1)):
        d.line([(cx, cy + L * dy), (cx, cy)], fill=accent, width=Wd)
        d.line([(cx, cy), (cx + L * dx, cy)], fill=accent, width=Wd)
    return d

def down_hint(canvas, cx, y, w, label, f, color=BLUE, gap=16, lw=None):
    d = ImageDraw.Draw(canvas)
    lw = lw or max(6, w // 7)
    d.line([(cx, y), (cx, y + w)], fill=color, width=lw)
    d.line([(cx - w // 2, y + int(w * 0.45)), (cx, y + w)], fill=color, width=lw)
    d.line([(cx + w // 2, y + int(w * 0.45)), (cx, y + w)], fill=color, width=lw)
    d.text((cx, y + w + gap), label, font=f, fill=color, anchor='ma')

def qr_image(px):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
    q.add_data(URL); q.make(fit=True)
    return q.make_image(fill_color='black', back_color='white').convert('RGB').resize((px, px), Image.NEAREST)

def top_band(im, h, text, f):
    W = im.width
    band = Image.new('RGB', (W, h), (8, 15, 30))
    im.paste(Image.blend(im.crop((0, 0, W, h)), band, 0.55), (0, 0))
    ImageDraw.Draw(im).text((W // 2, h // 2), text, font=f, fill=WHITE, anchor='mm')

# --------- 1. Плакат A4 ---------
def build_poster():
    W, H = 2480, 3508
    M = 150
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)

    ph_h = 1640
    im.paste(photo(W, ph_h, focus_y=0.42), (0, 0))
    torn(im, ph_h - 8, 90, seed=11, step=80)
    tricolor(im, 0, 22)
    top_band(im, 150, 'МИНОБОРОНЫ РФ  •  ПРИМОРСКИЙ КРАЙ, С. ПОКРОВКА', font('o', 46, 'Medium'))

    y = ph_h + 40
    put_logo(im, (M, y), 210)
    d.text((M + 250, y + 12), 'ВОЙСКА', font=font('o', 64, 'Bold'), fill=INK, anchor='la')
    d.text((M + 250, y + 82), 'БЕСПИЛОТНЫХ СИСТЕМ', font=font('o', 64, 'Bold'), fill=BLUE, anchor='la')
    y += 240

    d.text((W // 2, y), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 118, 'Bold'), fill=INK, anchor='ma')
    y += 160

    w1 = 1060; box_h = 330
    hud(im, [M, y, M + w1, y + box_h], radius=18)
    d.text((M + w1 // 2, y + 64), '2 000 000 ₽', font=font('o', 116, 'Bold'), fill=RED, anchor='ma')
    d.text((M + w1 // 2, y + 226), 'единовременно при заключении', font=font('i', 40), fill=MUTED, anchor='ma')

    x2 = W - M - w1
    hud(im, [x2, y, x2 + w1, y + box_h], radius=18)
    d.text((x2 + w1 // 2, y + 64), 'от 210 000 ₽/мес.', font=font('o', 90, 'Bold'), fill=RED, anchor='ma')
    d.text((x2 + w1 // 2, y + 226), 'довольствие в зоне СВО', font=font('i', 40), fill=MUTED, anchor='ma')
    y += box_h + 70

    qr_px = 620; pad = 40
    qx = (W - qr_px) // 2
    d.rounded_rectangle([qx - pad, y, qx + qr_px + pad, y + qr_px + 2 * pad], radius=34, fill=BLUE)
    d.rounded_rectangle([qx - pad + 12, y + 12, qx + qr_px + pad - 12, y + qr_px + 2 * pad - 12], radius=26, fill=WHITE)
    im.paste(qr_image(qr_px), (qx, y + pad))
    y += qr_px + 2 * pad + 40

    d.text((W // 2, y), 'НАВЕДИ КАМЕРУ И ПОДАЙ ЗАЯВКУ ОНЛАЙН', font=font('o', 62, 'SemiBold'), fill=BLUE, anchor='ma')
    y += 100
    d.text((W // 2, y), 'Приморский край, Октябрьский район, с. Покровка  •  пункт отбора', font=font('i', 40), fill=INK, anchor='ma')

    tricolor(im, H - 22, 22)
    im.save(os.path.join(OUT, 'Плакат_А4_ВБС.png'), 'PNG')
    im.save(os.path.join(OUT, 'Плакат_А4_ВБС.pdf'), 'PDF', resolution=300)
    return y, ['Плакат_А4_ВБС.png', 'Плакат_А4_ВБС.pdf']

# --------- 2. Пост 1080 ---------
def build_square():
    S = 1080
    im = Image.new('RGB', (S, S), BG)
    d = ImageDraw.Draw(im)

    ph_h = 640
    im.paste(photo(S, ph_h, focus_y=0.45), (0, 0))
    torn(im, ph_h - 6, 46, seed=5, step=48)
    tricolor(im, 0, 10)
    top_band(im, 96, 'ПРИМОРСКИЙ КРАЙ • С. ПОКРОВКА', font('o', 30, 'Medium'))

    y = ph_h + 22
    d.text((44, y), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 58, 'Bold'), fill=INK, anchor='la')
    d.text((44, y + 70), 'В ВОЙСКАХ БПЛА', font=font('o', 58, 'Bold'), fill=BLUE, anchor='la')
    y += 158

    hud(im, [44, y, 520, y + 128], radius=14, tick=0.55)
    d.text((282, y + 24), '2 000 000 ₽', font=font('o', 54, 'Bold'), fill=RED, anchor='ma')
    d.text((282, y + 92), 'единовременно', font=font('i', 23), fill=MUTED, anchor='ma')

    hud(im, [560, y, 1036, y + 128], radius=14, tick=0.55)
    d.text((798, y + 24), 'от 210 000 ₽/мес.', font=font('o', 43, 'Bold'), fill=RED, anchor='ma')
    d.text((798, y + 92), 'в зоне СВО', font=font('i', 23), fill=MUTED, anchor='ma')

    down_hint(im, 540, 946, 44, 'ПОДРОБНЕЕ', font('o', 34, 'SemiBold'), gap=10, lw=8)

    im.save(os.path.join(OUT, 'Пост_1080x1080.png'), 'PNG')
    return ['Пост_1080x1080.png']

# --------- 3. Сторис 1080x1920 ---------
def build_story():
    W, H = 1080, 1920
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)

    ph_h = 1120
    im.paste(photo(W, ph_h, focus_y=0.45), (0, 0))
    torn(im, ph_h - 6, 60, seed=9, step=54)
    tricolor(im, 0, 12)
    top_band(im, 108, 'МИНОБОРОНЫ РФ • ПРИМОРСКИЙ КРАЙ', font('o', 34, 'Medium'))

    y = ph_h + 40
    d.text((W // 2, y), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 68, 'Bold'), fill=INK, anchor='ma')
    y += 84
    d.text((W // 2, y), 'В ВОЙСКАХ БПЛА', font=font('o', 68, 'Bold'), fill=BLUE, anchor='ma')
    y += 110

    hud(im, [70, y, 1010, y + 170], radius=16, tick=0.7)
    d.text((540, y + 24), '2 000 000 ₽', font=font('o', 72, 'Bold'), fill=RED, anchor='ma')
    d.text((540, y + 118), 'единовременно при заключении', font=font('i', 26), fill=MUTED, anchor='ma')
    y += 192

    hud(im, [70, y, 1010, y + 146], radius=16, tick=0.7)
    d.text((540, y + 20), 'от 210 000 ₽/мес.', font=font('o', 52, 'Bold'), fill=RED, anchor='ma')
    d.text((540, y + 96), 'довольствие в зоне СВО', font=font('i', 26), fill=MUTED, anchor='ma')
    y += 200

    down_hint(im, 540, y, 60, 'ПОДРОБНЕЕ', font('o', 44, 'SemiBold'), gap=14, lw=11)

    im.save(os.path.join(OUT, 'Сторис_1080x1920.png'), 'PNG')
    return ['Сторис_1080x1920.png']

# --------- 4. Статус 1080x1920 ---------
def build_status():
    W, H = 1080, 1920
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)

    ph_h = 1180
    im.paste(photo(W, ph_h, focus_y=0.45), (0, 0))
    torn(im, ph_h - 6, 56, seed=21, step=60)
    tricolor(im, 0, 12)

    y = ph_h + 26
    d.text((W // 2, y), '2 000 000 ₽', font=font('o', 112, 'Bold'), fill=RED, anchor='ma')
    y += 144
    d.text((W // 2, y), 'единовременно при заключении контракта', font=font('i', 32), fill=INK, anchor='ma')
    y += 56
    d.text((W // 2, y), 'от 210 000 ₽/мес. в зоне СВО', font=font('i', 32, 'SemiBold'), fill=BLUE, anchor='ma')
    y += 62
    d.text((W // 2, y), '100% служба только в войсках БПЛА', font=font('i', 28), fill=MUTED, anchor='ma')

    down_hint(im, 540, y + 88, 58, 'ПОДРОБНЕЕ', font('o', 42, 'SemiBold'), gap=14, lw=10)

    im.save(os.path.join(OUT, 'Статус_1080x1920.png'), 'PNG')
    return ['Статус_1080x1920.png']

end_y, files = build_poster()
files += build_square()
files += build_story()
files += build_status()
print('низ плаката y =', end_y, '(3508)')
for f in files:
    print('  %-32s %5d KB' % (f, os.path.getsize(os.path.join(OUT, f)) // 1024))
