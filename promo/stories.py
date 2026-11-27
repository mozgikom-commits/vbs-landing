# -*- coding: utf-8 -*-
"""10 вариантов агитационной сторис: белый фон, крупная типографика, стрелка вниз."""
import os, random, math
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'stories')
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920
WHITE = (255, 255, 255)
INK   = (11, 18, 32)
BLUE  = (0, 57, 166)
RED   = (213, 43, 30)
MUTED = (82, 97, 122)
BORDER= (210, 219, 232)
ALT   = (238, 242, 248)

F_OSWALD = os.path.join(ROOT, 'fonts/Oswald-var.ttf')
F_INTER = os.path.join(ROOT, 'fonts/Inter-var.ttf')
HERO = os.path.join(ROOT, '..', 'hero.webp')
LOGO = os.path.join(ROOT, '..', 'logo.png')

def font(fam, size, weight='Regular'):
    f = ImageFont.truetype(F_OSWALD if fam == 'o' else F_INTER, size)
    if weight != 'Regular':
        try: f.set_variation_by_name(weight)
        except Exception: pass
    return f

def logo(size):
    return Image.open(LOGO).convert('RGBA').resize((size, size), Image.LANCZOS)

def put_logo(im, xy, size):
    lg = logo(size); im.paste(lg, xy, lg)

def photo(bw, bh, fy=0.45, fx=0.5):
    im = Image.open(HERO).convert('RGB')
    w, h = im.size
    s = max(bw / w, bh / h)
    nw, nh = int(w * s + .5), int(h * s + .5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = int((nw - bw) * fx); top = int((nh - bh) * fy)
    return im.crop((left, top, left + bw, top + bh))

def circle_photo(d):
    im = photo(d, d, fy=0.35)
    mask = Image.new('L', (d, d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
    out = Image.new('RGBA', (d, d), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out

def rounded_photo(w, h, r=34, fy=0.45):
    im = photo(w, h, fy=fy)
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out

def tricolor(im, y, h, x0=0, x1=None):
    d = ImageDraw.Draw(im); x1 = x1 or im.width
    w = x1 - x0
    d.rectangle([x0, y, x0 + w // 3, y + h], fill=WHITE)
    d.rectangle([x0 + w // 3, y, x0 + 2 * w // 3, y + h], fill=BLUE)
    d.rectangle([x0 + 2 * w // 3, y, x1, y + h], fill=RED)

def plate(im, cx, cy, text, f, px=36, py=18, fg=BLUE, border=BLUE, bg=(244, 247, 252)):
    d = ImageDraw.Draw(im)
    tw = d.textlength(text, font=f); b = d.textbbox((0, 0), text, font=f); th = b[3] - b[1]
    d.rectangle([cx - tw / 2 - px, cy - th / 2 - py, cx + tw / 2 + px, cy + th / 2 + py], fill=bg, outline=border, width=3)
    d.text((cx, cy), text, font=f, fill=fg, anchor='mm')

def hud(im, box, r=18, fill=WHITE, outline=BORDER, ow=4, tick=0.8, accent=BLUE):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=ow)
    x0, y0, x1, y1 = box
    L = int(44 * tick); wd = max(4, int(7 * tick)); ins = int(14 * tick)
    for (cx, cy, dx, dy) in ((x0 + ins, y0 + ins, 1, 1), (x1 - ins, y1 - ins, -1, -1)):
        d.line([(cx, cy + L * dy), (cx, cy)], fill=accent, width=wd)
        d.line([(cx, cy), (cx + L * dx, cy)], fill=accent, width=wd)

def arrow(im, cx, y, w=56, label='ПОДРОБНЕЕ', fs=38, color=BLUE, gap=14, lw=10):
    d = ImageDraw.Draw(im)
    d.line([(cx, y), (cx, y + w)], fill=color, width=lw)
    d.line([(cx - w // 2, y + int(w * .42)), (cx, y + w)], fill=color, width=lw)
    d.line([(cx + w // 2, y + int(w * .42)), (cx, y + w)], fill=color, width=lw)
    d.text((cx, y + w + gap), label, font=font('o', fs, 'SemiBold'), fill=color, anchor='ma')

def base():
    im = Image.new('RGB', (W, H), WHITE)
    tricolor(im, 0, 12)
    return im

def save(im, name):
    im.save(os.path.join(OUT, name), 'PNG')
    return name

# 1 — классика
def s01():
    im = base(); d = ImageDraw.Draw(im)
    put_logo(im, ((W - 170) // 2, 150), 170)
    plate(im, W // 2, 400, 'ПРИМОРСКИЙ КРАЙ  •  С. ПОКРОВКА', font('o', 30, 'Medium'))
    d.text((W // 2, 480), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 74, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, 570), 'В ВОЙСКАХ БПЛА', font=font('o', 74, 'Bold'), fill=BLUE, anchor='ma')
    y = 690
    hud(im, [70, y, 1010, y + 210]); d.text((540, y + 30), '2 000 000 ₽', font=font('o', 88, 'Bold'), fill=RED, anchor='ma')
    d.text((540, y + 140), 'единовременно при заключении', font=font('i', 28), fill=MUTED, anchor='ma')
    y += 240
    hud(im, [70, y, 1010, y + 170]); d.text((540, y + 24), 'от 210 000 ₽/мес.', font=font('o', 62, 'Bold'), fill=RED, anchor='ma')
    d.text((540, y + 112), 'довольствие в зоне СВО', font=font('i', 28), fill=MUTED, anchor='ma')
    arrow(im, 540, 1430, 60, fs=42)
    return save(im, 'Сторис_вариант_01.png')

# 2 — фото в карточке сверху
def s02():
    im = base(); d = ImageDraw.Draw(im)
    card = rounded_photo(940, 620, r=34, fy=0.4)
    im.paste(card, (70, 150), card)
    d.rounded_rectangle([70, 150, 1010, 770], radius=34, outline=BORDER, width=4)
    put_logo(im, (70 + 940 - 130, 150 + 620 - 130), 130)
    d.text((W // 2, 850), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 66, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, 934), 'В ВОЙСКАХ БПЛА', font=font('o', 66, 'Bold'), fill=BLUE, anchor='ma')
    d.text((W // 2, 1080), '2 000 000 ₽', font=font('o', 96, 'Bold'), fill=RED, anchor='ma')
    d.text((W // 2, 1185), 'единовременно при заключении контракта', font=font('i', 28), fill=INK, anchor='ma')
    d.text((W // 2, 1250), 'от 210 000 ₽/мес. в зоне СВО', font=font('i', 32, 'SemiBold'), fill=BLUE, anchor='ma')
    arrow(im, 540, 1420, 56, fs=40)
    return save(im, 'Сторис_вариант_02.png')

# 3 — гигантская цифра
def s03():
    im = base(); d = ImageDraw.Draw(im)
    put_logo(im, ((W - 130) // 2, 120), 130)
    d.text((W // 2, 330), 'ВОЙСКА БЕСПИЛОТНЫХ СИСТЕМ', font=font('o', 46, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, 470), '2 000 000 ₽', font=font('o', 150, 'Bold'), fill=RED, anchor='ma')
    d.text((W // 2, 660), 'единовременно при заключении контракта', font=font('i', 30), fill=INK, anchor='ma')
    d.line([(140, 780), (940, 780)], fill=BORDER, width=4)
    d.text((W // 2, 860), 'от 210 000 ₽/мес.', font=font('o', 86, 'Bold'), fill=BLUE, anchor='ma')
    d.text((W // 2, 990), 'довольствие в зоне СВО', font=font('i', 30), fill=MUTED, anchor='ma')
    d.text((W // 2, 1140), '100% служба только в войсках БПЛА', font=font('o', 40, 'Medium'), fill=INK, anchor='ma')
    tricolor(im, 1220, 8, 240, 840)
    arrow(im, 540, 1330, 58, fs=40)
    return save(im, 'Сторис_вариант_03.png')

# 4 — две цветные полосы
def s04():
    im = base(); d = ImageDraw.Draw(im)
    put_logo(im, ((W - 140) // 2, 120), 140)
    d.text((W // 2, 320), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 62, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, 396), 'В ВОЙСКАХ БПЛА', font=font('o', 62, 'Bold'), fill=BLUE, anchor='ma')
    d.rectangle([70, 520, 1010, 760], fill=RED)
    d.text((540, 610), '2 000 000 ₽', font=font('o', 92, 'Bold'), fill=WHITE, anchor='mm')
    d.text((540, 700), 'единовременно при заключении', font=font('i', 26), fill=(255, 235, 232), anchor='mm')
    d.rectangle([70, 790, 1010, 1000], fill=BLUE)
    d.text((540, 870), 'от 210 000 ₽/мес.', font=font('o', 66, 'Bold'), fill=WHITE, anchor='mm')
    d.text((540, 950), 'довольствие в зоне СВО', font=font('i', 26), fill=(224, 234, 255), anchor='mm')
    d.text((W // 2, 1090), 'ПРИМОРСКИЙ КРАЙ, С. ПОКРОВКА', font=font('o', 36, 'Medium'), fill=MUTED, anchor='ma')
    arrow(im, 540, 1350, 58, fs=40)
    return save(im, 'Сторис_вариант_04.png')

# 5 — круглое фото
def s05():
    im = base(); d = ImageDraw.Draw(im)
    D = 760
    circle = circle_photo(D)
    im.paste(circle, ((W - D) // 2, 150), circle)
    d.ellipse([(W - D) // 2 - 6, 144, (W + D) // 2 + 6, 914], outline=BLUE, width=6)
    d.text((W // 2, 980), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 62, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, 1056), 'В ВОЙСКАХ БПЛА', font=font('o', 62, 'Bold'), fill=BLUE, anchor='ma')
    d.text((W // 2, 1170), '2 000 000 ₽   •   от 210 000 ₽/мес.', font=font('o', 44, 'SemiBold'), fill=RED, anchor='ma')
    arrow(im, 540, 1330, 58, fs=40)
    return save(im, 'Сторис_вариант_05.png')

# 6 — красная плашка
def s06():
    im = base(); d = ImageDraw.Draw(im)
    put_logo(im, ((W - 120) // 2, 110), 120)
    d.text((W // 2, 290), 'ПРИМОРСКИЙ КРАЙ', font=font('o', 34, 'Medium'), fill=MUTED, anchor='ma')
    d.rounded_rectangle([90, 380, 990, 700], radius=24, fill=RED)
    d.text((540, 480), '2 000 000 ₽', font=font('o', 104, 'Bold'), fill=WHITE, anchor='mm')
    d.text((540, 610), 'единовременно при заключении контракта', font=font('i', 26), fill=(255, 235, 232), anchor='mm')
    d.rounded_rectangle([90, 730, 990, 960], radius=24, outline=BLUE, width=5)
    d.text((540, 810), 'от 210 000 ₽/мес.', font=font('o', 70, 'Bold'), fill=BLUE, anchor='mm')
    d.text((540, 900), 'довольствие в зоне СВО', font=font('i', 26), fill=MUTED, anchor='mm')
    d.text((W // 2, 1040), 'СЛУЖБА ПО КОНТРАКТУ В ВОЙСКАХ БПЛА', font=font('o', 38, 'SemiBold'), fill=INK, anchor='ma')
    arrow(im, 540, 1330, 58, fs=40)
    return save(im, 'Сторис_вариант_06.png')

# 7 — синий блок
def s07():
    im = base(); d = ImageDraw.Draw(im)
    d.rectangle([0, 120, W, 880], fill=INK)
    tricolor(im, 0, 12)
    put_logo(im, ((W - 150) // 2, 180), 150)
    d.text((W // 2, 400), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 64, 'Bold'), fill=WHITE, anchor='ma')
    d.text((W // 2, 480), 'В ВОЙСКАХ БПЛА', font=font('o', 64, 'Bold'), fill=(127, 176, 255), anchor='ma')
    d.text((W // 2, 620), '2 000 000 ₽', font=font('o', 96, 'Bold'), fill=(255, 96, 80), anchor='ma')
    d.text((W // 2, 740), 'единовременно при заключении', font=font('i', 26), fill=(233, 239, 249), anchor='ma')
    d.text((W // 2, 960), 'от 210 000 ₽/мес.', font=font('o', 76, 'Bold'), fill=BLUE, anchor='ma')
    d.text((W // 2, 1080), 'довольствие в зоне СВО', font=font('i', 28), fill=MUTED, anchor='ma')
    d.text((W // 2, 1200), 'ПРИМОРСКИЙ КРАЙ, С. ПОКРОВКА', font=font('o', 34, 'Medium'), fill=INK, anchor='ma')
    arrow(im, 540, 1330, 58, fs=40)
    return save(im, 'Сторис_вариант_07.png')

# 8 — минимал
def s08():
    im = base(); d = ImageDraw.Draw(im)
    put_logo(im, ((W - 300) // 2, 380), 300)
    d.text((W // 2, 760), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 68, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, 850), 'В ВОЙСКАХ БПЛА', font=font('o', 68, 'Bold'), fill=BLUE, anchor='ma')
    plate(im, W // 2, 990, '2 000 000 ₽  •  от 210 000 ₽/мес.', font('o', 34, 'SemiBold'), 40, 22, fg=RED, border=RED, bg=(255, 244, 242))
    arrow(im, 540, 1180, 56, fs=38)
    d.text((W // 2, 1520), 'Приморский край, Октябрьский район', font=font('i', 26), fill=MUTED, anchor='ma')
    return save(im, 'Сторис_вариант_08.png')

# 9 — четыре факта
def s09():
    im = base(); d = ImageDraw.Draw(im)
    put_logo(im, ((W - 120) // 2, 100), 120)
    d.text((W // 2, 270), 'ПОЧЕМУ ВБС', font=font('o', 40, 'Medium'), fill=MUTED, anchor='ma')
    d.text((W // 2, 340), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 62, 'Bold'), fill=INK, anchor='ma')
    rows = [('2 000 000 ₽', 'единовременно при заключении'),
            ('от 210 000 ₽/мес.', 'довольствие в зоне СВО'),
            ('100% БПЛА', 'служба только в войсках беспилотной авиации'),
            ('41 гарантия', 'льготы, кредиты, жильё, медицина')]
    y = 520
    for big, small in rows:
        d.line([(70, y), (1010, y)], fill=BORDER, width=3)
        d.rectangle([70, y + 26, 82, y + 122], fill=RED if rows.index((big, small)) % 2 == 0 else BLUE)
        d.text((110, y + 26), big, font=font('o', 54, 'Bold'), fill=INK, anchor='la')
        d.text((110, y + 96), small, font=font('i', 26), fill=MUTED, anchor='la')
        y += 150
    d.line([(70, y), (1010, y)], fill=BORDER, width=3)
    arrow(im, 540, 1330, 58, fs=40)
    return save(im, 'Сторис_вариант_09.png')

# 10 — фото-полоса снизу
def s10():
    im = base(); d = ImageDraw.Draw(im)
    d.text((W // 2, 200), 'СЛУЖБА ПО КОНТРАКТУ', font=font('o', 66, 'Bold'), fill=INK, anchor='ma')
    d.text((W // 2, 286), 'В ВОЙСКАХ БПЛА', font=font('o', 66, 'Bold'), fill=BLUE, anchor='ma')
    d.text((W // 2, 430), '2 000 000 ₽', font=font('o', 118, 'Bold'), fill=RED, anchor='ma')
    d.text((W // 2, 570), 'единовременно при заключении контракта', font=font('i', 30), fill=INK, anchor='ma')
    d.text((W // 2, 660), 'от 210 000 ₽/мес. в зоне СВО', font=font('i', 34, 'SemiBold'), fill=BLUE, anchor='ma')
    arrow(im, 540, 790, 54, fs=38)
    strip = rounded_photo(940, 620, r=28, fy=0.4)
    im.paste(strip, (70, 1060), strip)
    d.rounded_rectangle([70, 1060, 1010, 1680], radius=28, outline=BORDER, width=4)
    put_logo(im, (70 + 940 - 110, 1060 + 620 - 110), 110)
    d.text((W // 2, 1740), 'Октябрьский район Приморского края', font=font('i', 26), fill=MUTED, anchor='ma')
    return save(im, 'Сторис_вариант_10.png')

names = [s01(), s02(), s03(), s04(), s05(), s06(), s07(), s08(), s09(), s10()]
for n in names:
    print('  %-30s %5d KB' % (n, os.path.getsize(os.path.join(OUT, n)) // 1024))
