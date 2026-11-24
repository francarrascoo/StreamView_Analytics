"""Captura tarjetas individuales del dashboard para el informe y la presentación.

Cada figura es una tarjeta completa (pregunta + respuesta + gráfico), la fila de KPIs
o una pestaña entera. Uso (con el dashboard corriendo):
    cd entregables/fuente && python capturar_figuras.py --url http://localhost:8501 --salida ../evidencias/figuras
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

from capturar_evidencias import esperar_render

# (archivo, vista, pestaña, qué capturar: "kpis" | "pestana" | texto de la pregunta de la tarjeta)
FIGURAS = [
    ("f1_scorecard", "Directorio", "Resumen", "kpis"),
    ("f2_mercados", "Directorio", "Resumen", "¿Dónde están las películas mejor evaluadas?"),
    ("f3_trayectorias", "Directorio", "Avance hacia la meta", "pestana"),
    ("f4_k1_generos", "Contenidos y Adquisición", "Géneros", "¿Qué géneros de película comprar?"),
    ("f5_series_sin_votos", "Marketing", "Participación", "¿Dónde pedir calificaciones primero?"),
    ("f6_rentabilidad_nota", "Directorio", "Rentabilidad", "¿Invertir en calidad (K1) rinde?"),
    ("f7_produccion", "Contenidos y Adquisición", "Directores y actores", "pestana"),
    ("f8_calidad_popularidad", "Data & Analytics", "Popularidad y nota", "¿La buena nota atrae público?"),
    ("f9_k3_generos", "Marketing", "Participación", "¿En qué series falta participación del público?"),
    ("f10_decisiones", "Directorio", "Resumen", "¿Qué hacer ahora?"),
    ("f11_top10", "Marketing", "Qué promover", "¿Qué títulos destacar en campañas?"),
    ("f12_resumen_directorio", "Directorio", "Resumen", "pantalla"),
    ("f13_participacion_marketing", "Marketing", "Participación", "pantalla"),
    ("f14_rentabilidad_mercado", "Directorio", "Rentabilidad", "¿Rinden las películas de los mercados de K2?"),
    ("f15_peliculas_mercados", "Marketing", "Qué promover", "¿Qué películas de Japón, Corea del Sur y México destacar?"),
]

JS_CAJA = """(que) => {
  const main = document.querySelector('[data-testid="stMain"]');
  let el = null;
  if (que === "kpis") el = [...main.querySelectorAll('.kpi-grid')].find(e => e.offsetParent !== null);
  else if (que === "pantalla") return {x: 0, y: 0, width: window.innerWidth, height: window.innerHeight};
  else if (que === "pestana") el = [...main.querySelectorAll('[role="tabpanel"]')].find(e => e.offsetParent !== null);
  else {
    const q = [...main.querySelectorAll('.q')].find(e => e.offsetParent !== null && e.innerText.trim().toUpperCase().startsWith(que.toUpperCase()));
    el = q && q.closest('[data-testid="stLayoutWrapper"]');
  }
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {x: r.left - 6, y: r.top + window.scrollY - 6, width: r.width + 12, height: r.height + 12};
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8501")
    ap.add_argument("--salida", required=True)
    args = ap.parse_args()
    out = Path(args.salida)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page.goto(args.url)
        esperar_render(page, 5)
        for archivo, vista, pestana, que in FIGURAS:
            page.locator('[data-testid="stMain"] [data-testid="stButtonGroup"]').first.get_by_text(vista, exact=True).click()
            esperar_render(page)
            page.locator('[data-baseweb="tab"]').filter(has_text=pestana).first.click()
            esperar_render(page, 2)
            caja = page.evaluate(JS_CAJA, que)
            if not caja:
                print("NO ENCONTRADO", archivo)
                continue
            page.screenshot(path=str(out / f"{archivo}.png"), clip=caja)
            print("ok", archivo)
        browser.close()


if __name__ == "__main__":
    main()
