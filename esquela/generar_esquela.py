"""Genera una esquela con el mismo diseño que el modelo. Edita DATOS y ejecuta."""
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image, ImageDraw

DATOS = {
    "foto": "cristo.jpg",  # ruta a la foto (se recorta en óvalo)
    "nombre": "Juan José\nMartínez García",
    "fecha_fallecimiento": "24 de Noviembre de 2026",
    "edad": "68",
    "padres": "José Martínez.",
    "esposa": "Nati López Coronado",
    "hijos": "Jorge y Carlos Jesús.",
    "otros": "Hijas políticas, hermanos, cuñados, nietos y demás familia.",
    "entierro_dia": "MIÉRCOLES 25 DE NOVIEMBRE",
    "entierro_hora": "10:30 de la mañana",
    "lugar": "Parroquia de la Asunción de Villacarrillo.",
    "domicilio": "calle Arz Carrillo 1.",
    "velatorio": "TANATORIO VIRGEN DEL ROSARIO",
}
FONT = "Times New Roman"

def oval(src, out):
    w, h = 920, 1440
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
    f.space_after, f.space_before = Pt(after), Pt(before)
    f.left_indent, f.right_indent = Cm(3 + left), Cm(3)
    return p

def anclar_abajo(pic, y_emu):
    """Convierte la imagen en flotante, anclada a la página en (0, y)."""
    from lxml import etree
    ns = {"wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}
    W = "{%s}" % ns["wp"]
    inline = pic._inline
    anchor = etree.SubElement(inline.getparent(), W + "anchor", nsmap=inline.nsmap)
    for k, v in dict(distT="0", distB="0", distL="0", distR="0", simplePos="0", relativeHeight="0",
                     behindDoc="1", locked="0", layoutInCell="1", allowOverlap="1").items():
        anchor.set(k, v)
    etree.SubElement(anchor, W + "simplePos", x="0", y="0")
    ph = etree.SubElement(anchor, W + "positionH", relativeFrom="page")
    etree.SubElement(ph, W + "posOffset").text = "0"
    pv = etree.SubElement(anchor, W + "positionV", relativeFrom="page")
    etree.SubElement(pv, W + "posOffset").text = str(int(y_emu))
    anchor.append(inline.find(W + "extent"))
    etree.SubElement(anchor, W + "effectExtent", l="0", t="0", r="0", b="0")
    etree.SubElement(anchor, W + "wrapNone")
    for tag in ("docPr", "cNvGraphicFramePr"):
        anchor.append(inline.find(W + tag))
    anchor.append(inline.find("{http://schemas.openxmlformats.org/drawingml/2006/main}graphic"))
    inline.getparent().remove(inline)

def build(d, out="esquela.docx"):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin = s.right_margin = Cm(0)  # franja a sangre; el texto lleva sangría de 3 cm
    s.top_margin = Cm(2)
    s.bottom_margin = Cm(4.4)
    s.footer_distance = Cm(0)
    # franja del tanatorio a sangre, pegada al borde inferior del folio
    fp = s.footer.paragraphs[0]
    fp.paragraph_format.space_before = fp.paragraph_format.space_after = Pt(0)
    fp.paragraph_format.line_spacing = 1
    pic = fp.add_run().add_picture("banner_tanatorio.png", width=Cm(21))
    anclar_abajo(pic, Cm(29.7) - pic.height)
    C = WD_ALIGN_PARAGRAPH.CENTER

    oval(d["foto"], "foto_oval.png")
    p = par(doc, C, after=6)
    p.add_run().add_picture("foto_oval.png", height=Cm(7.5))

    p = par(doc, C, after=4)
    p.paragraph_format.line_spacing = 0.95
    lines = d["nombre"].split("\n")
    for i, ln in enumerate(lines):
        r = run(p, ln, 40, True)
        if i < len(lines) - 1:
            r.add_break()

    p = par(doc, C, after=4); run(p, f"Falleció el {d['fecha_fallecimiento']}", 12, True)
    p = par(doc, C, after=4); run(p, f"A los {d['edad']} AÑOS DE EDAD", 12, True)
    p = par(doc, C, after=8); run(p, "D.E.P", 12, True)

    for lab, key in (("Padres:", "padres"), ("Esposa:", "esposa"), ("Hijos:", "hijos")):
        p = par(doc, after=2, left=-0.9)
        run(p, lab + " ", 14, True); run(p, d[key], 14)
    p = par(doc, after=8, left=-0.9); run(p, d["otros"], 14, True)

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
