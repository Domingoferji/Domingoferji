"""Genera una esquela con el mismo diseño que el modelo. Edita DATOS y ejecuta."""
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image, ImageDraw

DATOS = {
    "foto": None,  # ruta a la foto (se recorta en óvalo); None = hueco con marcador
    "nombre": "Nombre\nApellido1 Apellido2",
    "fecha_fallecimiento": "24 de Noviembre de 2026",
    "edad": "68",
    "padres": "Nombre del padre.",
    "esposa": "Nombre de la esposa",
    "hijos": "Hijo 1 y Hijo 2.",
    "otros": "Hijas políticas, hermanos, cuñados, nietos y demás familia.",
    "entierro_dia": "MIERCOLES 25 DE NOVIEMBRE",
    "entierro_hora": "10:30 de la mañana",
    "lugar": "Parroquia de la Asunción de Villacarrillo.",
    "domicilio": "calle Arz Carrillo 1.",
    "velatorio": "TANATORIO VIRGEN DEL ROSARIO",
}
FONT = "Times New Roman"

def oval(src, out):
    w, h = 460, 720
    if src:
        im = Image.open(src).convert("RGB")
        r = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * r), int(im.height * r)))
        l, t = (im.width - w) // 2, (im.height - h) // 2
        im = im.crop((l, t, l + w, t + h))
    else:
        im = Image.new("RGB", (w, h), (200, 200, 200))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, w - 1, h - 1), fill=255)
    bg = Image.new("RGB", (w, h), "white")
    bg.paste(im, mask=mask)
    bg.save(out)

def run(p, text, size, bold=False):
    r = p.add_run(text)
    r.font.name = FONT
    r._element.rPr.rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", FONT)
    r.font.size = Pt(size)
    r.bold = bold
    return r

def par(doc, align=None, after=6, before=0, left=0):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    f = p.paragraph_format
    f.space_after, f.space_before, f.left_indent = Pt(after), Pt(before), Cm(left)
    return p

def build(d, out="esquela.docx"):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin = s.right_margin = Cm(3)
    s.top_margin = s.bottom_margin = Cm(2)
    C = WD_ALIGN_PARAGRAPH.CENTER

    oval(d["foto"], "foto_oval.png")
    p = par(doc, C, after=24)
    p.add_run().add_picture("foto_oval.png", height=Cm(6.2))

    p = par(doc, C, after=10)
    lines = d["nombre"].split("\n")
    for i, ln in enumerate(lines):
        r = run(p, ln, 36, True)
        if i < len(lines) - 1:
            r.add_break()

    p = par(doc, C, after=10); run(p, f"Falleció el {d['fecha_fallecimiento']}", 12, True)
    p = par(doc, C, after=10); run(p, f"A los {d['edad']} AÑOS DE EDAD", 12, True)
    p = par(doc, C, after=14); run(p, "D.E.P", 12, True)

    for lab, key in (("Padres:", "padres"), ("Esposa:", "esposa"), ("Hijos:", "hijos")):
        p = par(doc, after=2, left=-0.9)
        run(p, lab + " ", 14, True); run(p, d[key], 14)
    p = par(doc, after=14, left=-0.9); run(p, d["otros"], 14, True)

    p = par(doc, after=0, left=-0.8)
    run(p, "Al participarle tan sensible pérdida, comunican que el entierro tendrá lugar mañana, ", 13)
    run(p, d["entierro_dia"] + ", ", 13, True)
    run(p, "a las ", 13); run(p, d["entierro_hora"] + " en ", 13, True)
    run(p, d["lugar"] + " ", 13, True)
    run(p, f"El difunto vivía en la {d['domicilio']} Se vela en ", 13)
    run(p, d["velatorio"], 13, True)
    doc.save(out)

if __name__ == "__main__":
    build(DATOS, sys.argv[1] if len(sys.argv) > 1 else "esquela.docx")
