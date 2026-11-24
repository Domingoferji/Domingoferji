"""Genera la franja del Tanatorio Virgen del Rosario (ancho A4, 300 dpi)."""
from PIL import Image, ImageDraw, ImageFont
W, H = 2480, 480
CREAM = (246, 238, 226)
top, bot = (126, 86, 51), (101, 67, 40)
im = Image.new("RGB", (W, H))
d = ImageDraw.Draw(im)
for y in range(H):
    t = y / (H - 1)
    d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))

def centered(text, font, y, x0=0, x1=W):
    w = d.textlength(text, font=font)
    d.text(((x0 + x1 - w) / 2, y), text, font=font, fill=CREAM)
    return w

serif = ImageFont.truetype("/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf", 128)
sans = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 66)
sansm = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 112)

centered("Tanatorio Virgen del Rosario", serif, 30)
centered("Villacarrillo - C/. Rafael Alberti, 64", sans, 190)

# línea del teléfono con icono de WhatsApp
tel = "608 859 572 - 616 607 792"
tw = d.textlength(tel, font=sansm)
icon = 104
gap = 34
x = (W - (icon + gap + tw)) / 2
y = 300
d.text((x + icon + gap, y), tel, font=sansm, fill=CREAM)
cx, cy, r = x + icon / 2, y + 62, icon / 2
d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=CREAM, width=8)
d.polygon([(cx - r + 4, cy + r - 6), (cx - r - 6, cy + r + 14), (cx - r + 26, cy + r - 16)], fill=CREAM)
# auricular: arco grueso con extremos redondeados
hx, hy, hr = cx + 17, cy - 17, 40
d.arc((hx - hr, hy - hr, hx + hr, hy + hr), 90, 180, fill=CREAM, width=13)
for ex, ey in ((hx, hy + hr), (hx - hr, hy)):
    d.ellipse((ex - 11, ey - 11, ex + 11, ey + 11), fill=CREAM)
im.save("banner_tanatorio.png", dpi=(300, 300))
