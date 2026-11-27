# posters_output — финальные плакаты

Собраны из HTML/CSS (никаких «рисовалок»), поэтому русский текст без опечаток и артефактов.

## Файлы

| Файл | Макет |
|---|---|
| Плакат_1_Гранж.png / .pdf | Тёмный агитационный: «ВОЙСКА БПЛА», слоган, выплаты, QR |
| Плакат_2_Типографика.png / .pdf | Белый, гигантские вертикальные буквы, фото-панель |
| Плакат_3_Кинопостер.png / .pdf | Кинопостер: дым, крупный заголовок, строка кредитов |

Все — A4, 2480×3508 px (300 dpi). PDF — та же страница A4.

## Исходники

- `poster1.html`, `poster2.html`, `poster3.html` — вёрстка, размер холста 1240×1754 px (= A4 в 150 dpi)
- `fonts/` — Bebas Neue, Russo One, Oswald, Inter (все OFL)
- `img/qr.png` — QR на https://mozgikom-commits.github.io/vbs-landing/

## Пересборка

```bash
# PNG в 2× (2480×3508)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --allow-file-access-from-files --force-device-scale-factor=2 \
  --window-size=1240,1754 --screenshot=out.png poster1.html

# PDF
python3 -c "from PIL import Image; Image.open('out.png').convert('RGB').save('out.pdf','PDF',resolution=300)"
```

Текст правится прямо в HTML — шрифты встроены локально, без интернета.
