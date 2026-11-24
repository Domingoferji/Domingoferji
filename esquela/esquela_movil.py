"""Esquela en formato vertical para móvil (1080 px de ancho), estilo tanatorio.
Edita DATOS y ejecuta:  python3 esquela_movil.py
"""
from PIL import Image, ImageDraw, ImageFont

DATOS = {
    "foto": "cristo.jpg",
    "nombre": "JUAN JOSÉ MARTÍNEZ GARCÍA",
    "falleció": "FALLECIÓ EL 24 DE NOVIEMBRE DE 2026",
    "edad": "A los 68 años de edad",
    "familia": [
        ("Padres: ", "José Martínez."),
        ("Esposa: ", "Nati López Coronado"),
        ("Hijos: ", "Jorge y Carlos Jesús."),
    ],
    "otros": "Hijas políticas, hermanos, cuñados, nietos y demás familia.",
    "aviso": [  # (texto, negrita)
        ("Al participarle tan sensible pérdida, comunican que el entierro tendrá lugar mañana, ", False),
        ("MIÉRCOLES 25 DE NOVIEMBRE, ", True),
        ("a las ", False), ("10:30 de la mañana ", True), ("en ", False),
        ("Parroquia de la Asunción de Villacarrillo.", True),
        (" El difunto vivía en la calle Arz Carrillo 1.", False),
    ],
    "velatorio": [("Se vela en: ", False), ("TANATORIO VIRGEN DEL ROSARIO", True)],
}

W, H = 1080, 1440          # tamaño final (3:4 vertical)
K = 2                      # supersampling para bordes suaves
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIFB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
CAL = "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
INTERM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"

def F(path, size):
    return ImageFont.truetype(path, int(size * K))

def banner(img, d, y0, h):
    top, bot, cream = (126, 86, 51), (101, 67, 40), (246, 238, 226)
    for y in range(h * K):
        t = y / (h * K - 1)
        d.line([(0, y0 * K + y), (W * K, y0 * K + y)],
               fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    def center(text, font, y):
        w = d.textlength(text, font=font)
        d.text(((W * K - w) / 2, y * K), text, font=font, fill=cream)
    center("Tanatorio Virgen del Rosario", F(CAL, 62), y0 + 16)
    center("Villacarrillo - C/. Rafael Alberti, 64", F(INTER, 33), y0 + 96)
    font = F(INTERM, 52)
    tel = "608 859 572 - 616 607 792"
    tw = d.textlength(tel, font=font) / K
    ic, gap = 50, 17
    x = (W - (ic + gap + tw)) / 2
    y = y0 + 144
    d.text(((x + ic + gap) * K, y * K), tel, font=font, fill=cream)
    cx, cy, r = (x + ic / 2) * K, (y + 33) * K, ic / 2 * K
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=cream, width=4 * K)
    d.polygon([(cx - r + 2 * K, cy + r - 3 * K), (cx - r - 3 * K, cy + r + 7 * K),
               (cx - r + 13 * K, cy + r - 8 * K)], fill=cream)
    hx, hy, hr = cx + 8 * K, cy - 8 * K, 19 * K
    d.arc((hx - hr, hy - hr, hx + hr, hy + hr), 90, 180, fill=cream, width=6 * K)
    for ex, ey in ((hx, hy + hr), (hx - hr, hy)):
        d.ellipse((ex - 5 * K, ey - 5 * K, ex + 5 * K, ey + 5 * K), fill=cream)

def oval_photo(src, w, h):
    im = Image.open(src).convert("RGB")
    b = int(min(im.size) * 0.03)  # quita el marco de la foto original
    im = im.crop((b, b, im.width - b, im.height - b))
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((l, t, l + w, t + h))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, w - 1, h - 1), fill=255)
    return im, mask

def wrap(segs, size, maxw, d):
    """segs: [(texto, negrita)] -> lista de líneas, cada una lista de (texto, negrita)."""
    words = []
    for text, b in segs:
        for i, wd in enumerate(text.split(" ")):
            if wd == "":
                continue
            words.append((wd, b))
    lines, cur, curw = [], [], 0
    fr, fb = F(SERIF, size), F(SERIFB, size)
    sp = d.textlength(" ", font=fr)
    for wd, b in words:
        w = d.textlength(wd, font=fb if b else fr)
        add = w if not cur else sp + w
        if cur and curw + add > maxw * K:
            lines.append(cur); cur, curw = [], 0; add = w
        cur.append((wd, b)); curw += add
    if cur: lines.append(cur)
    return lines

def draw_line(d, segs, size, y):
    fr, fb = F(SERIF, size), F(SERIFB, size)
    segs = [(t.strip(), b) for t, b in segs]
    sp = d.textlength(" ", font=fr)
    total = sum(d.textlength(t, font=fb if b else fr) for t, b in segs) + sp * (len(segs) - 1)
    x = (W * K - total) / 2
    for t, b in segs:
        f = fb if b else fr
        d.text((x, y * K), t, font=f, fill=(15, 15, 15))
        x += d.textlength(t, font=f) + sp

def build(D, out="esquela_movil.png"):
    img = Image.new("RGB", (W * K, H * K), "white")
    d = ImageDraw.Draw(img)
    BH = 228
    banner(img, d, H - BH, BH)

    y = 28
    ph, pw = 430, 275
    im, mask = oval_photo(D["foto"], pw * K, ph * K)
    img.paste(im, (int((W - pw) / 2 * K), y * K), mask)
    y += ph + 24

    # nombre: se ajusta el tamaño para que quepa a lo ancho
    size = 66
    while d.textlength(D["nombre"], font=F(SERIFB, size)) > (W - 90) * K:
        size -= 1
    draw_line(d, [(D["nombre"], True)], size, y)
    y += int(size * 1.22) + 6

    draw_line(d, [(D["falleció"], False)], 33, y); y += 48
    draw_line(d, [(D["edad"], False)], 36, y); y += 52
    draw_line(d, [("D.E.P", True)], 34, y); y += 54

    for lab, val in D["familia"]:
        draw_line(d, [(lab.strip(), True), (val, False)], 35, y); y += 49
    draw_line(d, [(D["otros"], False)], 33, y); y += 62

    for ln in wrap(D["aviso"], 36, 900, d):
        draw_line(d, ln, 36, y); y += 47
    y += 12
    draw_line(d, D["velatorio"], 33, y)
    print("fin del texto en y =", y + 40, " | banner empieza en", H - BH)
    img.resize((W, H), Image.LANCZOS).save(out, dpi=(144, 144))
    img.save(out.replace(".png", "_HD.png"))

if __name__ == "__main__":
    build(DATOS)
