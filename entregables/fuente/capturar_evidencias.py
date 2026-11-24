"""Captura pantallas del dashboard para las evidencias antes/después.

Recorre cada perfil y cada pestaña del dashboard y guarda una captura de página
completa por combinación. Se usó para generar entregables/evidencias/antes/ (versión EP4,
commit 221f72f) y entregables/evidencias/despues/ (versión EP5 optimizada).

Uso (con el dashboard corriendo):
    python entregables/fuente/capturar_evidencias.py --url http://localhost:8501 --salida entregables/evidencias/despues

Requiere playwright (pip install playwright) y Google Chrome instalado; usa el
Chrome del sistema, así que no hace falta descargar navegadores.
"""
import argparse
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright



def slug(texto):
    texto = texto.lower()
    for a, b in zip("áéíóúñ", "aeioun"):
        texto = texto.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "_", texto).strip("_")


def esperar_render(page, segundos=2.5):
    # Streamlit muestra un indicador "Running..." mientras recalcula
    page.wait_for_load_state("networkidle")
    time.sleep(segundos)
    try:
        page.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=20000)
    except Exception:
        pass
    time.sleep(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8501")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--ancho", type=int, default=1440)
    args = ap.parse_args()
    out = Path(args.salida)
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": args.ancho, "height": 900}, device_scale_factor=1)
        page.goto(args.url)
        esperar_render(page, 5)
        selector = page.locator('[data-testid="stMain"] [data-testid="stButtonGroup"]').first
        perfiles = [t.strip() for t in selector.locator('button').all_inner_texts()]
        for perfil in perfiles:
            radio = selector.get_by_text(perfil, exact=True)
            radio.click()
            esperar_render(page)
            tabs = page.locator('[data-baseweb="tab"]')
            n = tabs.count()
            nombres = [tabs.nth(i).inner_text().strip() for i in range(n)]
            for i, nombre in enumerate(nombres):
                page.locator('[data-baseweb="tab"]').nth(i).click()
                esperar_render(page, 1.5)
                archivo = out / f"{slug(perfil)}__{i + 1}_{slug(nombre)}.png"
                # Streamlit desplaza un contenedor interno, no la página: se agranda la ventana
                # al alto del contenido para que la captura incluya todo
                alto = page.evaluate("document.querySelector('[data-testid=\"stMain\"]').scrollHeight")
                page.set_viewport_size({"width": args.ancho, "height": max(900, int(alto) + 40)})
                esperar_render(page, 1.5)
                page.screenshot(path=str(archivo), full_page=True)
                page.set_viewport_size({"width": args.ancho, "height": 900})
                print("ok", archivo)
        browser.close()


if __name__ == "__main__":
    main()
