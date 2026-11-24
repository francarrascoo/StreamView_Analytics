"""Arma las imágenes comparativas antes/después.

Antes: recortes de las capturas de la versión EP4 (entregables/evidencias/antes/, commit 221f72f).
Después: tarjetas y pantallas de la versión EP5 capturadas con capturar_figuras.py.
Salida: entregables/evidencias/comparativas/*.png, que usan el informe y la presentación.
Uso:  python entregables/fuente/comparativas.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
EV = RAIZ / "entregables" / "evidencias"
OUT = EV / "comparativas"
ANCHO = 1050  # ancho de cada panel

# (salida, (antes: archivo, recorte), (después: archivo, recorte o None para la imagen completa))
PARES = [
    ("c1_kpis", ("antes/directorio__1_resumen.png", (320, 420, 1370, 770)),
     ("figuras/f12_resumen_directorio.png", None)),
    ("c2_mercados_meta", ("antes/directorio__1_resumen.png", (320, 1305, 1370, 1830)),
     ("figuras/f2_mercados.png", None)),
    ("c3_top10_formato", ("antes/marketing__2_titulos_destacados.png", (330, 1020, 1300, 1475)),
     ("figuras/f11_top10.png", None)),
    ("c4_metricas_no_kpis", ("antes/marketing__1_oportunidades.png", (330, 430, 1365, 780)),
     ("figuras/f13_participacion_marketing.png", None)),
]


def fuente(tam):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def cargar(archivo, caja):
    img = Image.open(EV / archivo).convert("RGB")
    if caja:
        img = img.crop(caja)
    return img.resize((ANCHO, round(img.height * ANCHO / img.width)), Image.LANCZOS)


def panel(img, rotulo, color):
    pad, cab = 24, 64
    lienzo = Image.new("RGB", (img.width + 2 * pad, img.height + cab + pad), "white")
    d = ImageDraw.Draw(lienzo)
    d.rectangle([0, 0, lienzo.width, cab - 12], fill=color)
    d.text((pad, 12), rotulo, fill="white", font=fuente(30))
    lienzo.paste(img, (pad, cab))
    d.rectangle([0, 0, lienzo.width - 1, lienzo.height - 1], outline="#d0d7de", width=2)
    return lienzo


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for nombre, (fa, ca), (fd, cd) in PARES:
        a = panel(cargar(fa, ca), "ANTES · versión EP4", "#57606a")
        b = panel(cargar(fd, cd), "DESPUÉS · versión EP5", "#24292f")
        comp = Image.new("RGB", (a.width + b.width + 30, max(a.height, b.height)), "white")
        comp.paste(a, (0, 0))
        comp.paste(b, (a.width + 30, 0))
        comp.save(OUT / f"{nombre}.png", optimize=True)
        print("ok", nombre, comp.size)


if __name__ == "__main__":
    main()
