"""Captura escenarios de decisión con filtros activos (verificación técnica de EP5 y guion de la demo EP6).

Cada escenario elige una vista, abre el botón "Filtros", aplica filtros como lo haría
un usuario y guarda la pantalla (1440 x 900, sin scroll). Demuestra que los filtros
recalculan la frase principal, los KPIs, los estados, los gráficos y los títulos.

Uso (con el dashboard corriendo):
    cd entregables/fuente && python capturar_escenarios.py --url http://localhost:8501 --salida ../evidencias/escenarios
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

from capturar_evidencias import esperar_render

ESCENARIOS = [
    # (archivo, vista, pestaña, filtros {etiqueta del filtro: [opciones]}, tipo de contenido)
    ("1_contenidos_genero_terror", "Contenidos y Adquisición", "Mercados", {"Género": ["Terror"]}, None),
    ("2_contenidos_genero_documental", "Contenidos y Adquisición", "Mercados", {"Género": ["Documental"]}, None),
    ("3_directorio_pais_japon", "Directorio", "Resumen", {"País": ["Japón"]}, None),
    ("4_marketing_series_coreano", "Marketing", "Participación", {"Idioma": ["coreano"]}, "Serie"),
    ("5_directorio_rentabilidad_animacion", "Directorio", "Rentabilidad", {"Género": ["Animación"]}, None),
]


def abrir_filtros(page):
    esperar_render(page, 1)
    cuerpo = page.locator('[data-testid="stPopoverBody"]')
    if not cuerpo.is_visible():           # si ya está abierto, otro clic lo cerraría
        page.locator('[data-testid="stPopoverButton"]').first.click()
        cuerpo.wait_for()
    return cuerpo


def elegir(page, etiqueta, opcion):
    cuerpo = abrir_filtros(page)
    caja = cuerpo.locator('[data-testid="stMultiSelect"]').filter(has_text=etiqueta)
    caja.locator("input").click()
    caja.locator("input").fill(opcion)
    page.locator('li[role="option"]').filter(has_text=opcion).first.click()
    page.keyboard.press("Escape")
    esperar_render(page, 1.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8501")
    ap.add_argument("--salida", required=True)
    args = ap.parse_args()
    out = Path(args.salida)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        for archivo, vista, pestana, filtros, tipo in ESCENARIOS:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(args.url)
            esperar_render(page, 5)
            page.locator('[data-testid="stMain"] [data-testid="stButtonGroup"]').first.get_by_text(vista, exact=True).click()
            esperar_render(page)
            if tipo:
                cuerpo = abrir_filtros(page)
                cuerpo.locator('[data-testid="stButtonGroup"]').first.get_by_text(tipo, exact=True).click()
                esperar_render(page, 2)
            for etiqueta, opciones in filtros.items():
                for o in opciones:
                    elegir(page, etiqueta, o)
            page.mouse.click(5, 5)  # cierra el panel de filtros si quedó abierto
            page.locator('[data-baseweb="tab"]').filter(has_text=pestana).first.click()
            esperar_render(page, 2)
            page.screenshot(path=str(out / f"{archivo}.png"))
            print("ok", archivo)
            page.close()
        browser.close()


if __name__ == "__main__":
    main()
