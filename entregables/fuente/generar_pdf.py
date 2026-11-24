"""Genera los PDF de los entregables a partir de su fuente HTML (usa el Chrome instalado).

Uso:  python entregables/fuente/generar_pdf.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
DOCUMENTOS = [
    (RAIZ / "entregables/fuente/informe_ep5.html", RAIZ / "entregables/Informe_Ejecutivo_EP5_StreamView_Analytics.pdf"),
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        for html, pdf in DOCUMENTOS:
            page.goto(html.as_uri())
            page.wait_for_load_state("networkidle")
            page.pdf(path=str(pdf), format="A4", print_background=True, prefer_css_page_size=True,
                     display_header_footer=True, header_template="<span></span>",
                     footer_template='<div style="font-size:8px;color:#57606a;width:100%;text-align:center">'
                                     'StreamView Analytics · Informe EP5 · <span class="pageNumber"></span> de '
                                     '<span class="totalPages"></span></div>')
            print("ok", pdf.relative_to(RAIZ))
        browser.close()


if __name__ == "__main__":
    main()
