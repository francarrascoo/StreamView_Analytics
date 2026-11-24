// Presentación ejecutiva EP6 · StreamView Analytics
// Genera entregables/Presentacion_EP6_StreamView_Analytics.pptx
// Uso: cd entregables/fuente && npm install && node presentacion_ep6.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const RAIZ = path.resolve(__dirname, "..", "..");
const EV = (p) => path.join(RAIZ, "entregables", "evidencias", p);
const SALIDA = path.join(RAIZ, "entregables", "Presentacion_EP6_StreamView_Analytics.pptx");
const APPLY_THEME = process.env.APPLY_THEME_JS;

const THEME = {
  name: "StreamView EP6",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "24292F", lt1: "FFFFFF", dk2: "57606A", lt2: "F6F8FA",
    accent1: "2A78D6", accent2: "C85526", accent3: "1A7F37", accent4: "9A6700", accent5: "CF222E", accent6: "0F766E",
    hlink: "2A78D6", folHlink: "57606A",
  },
};
const HEX = THEME.colors;
const LINEA = "D0D7DE";
const GRIS_BARRA = "6E7781"; // gris de contexto con etiqueta blanca legible (4,6:1)

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13,33 x 7,5 in
pres.title = "StreamView Analytics · Presentación ejecutiva EP6";
pres.author = "Felipe Ahumada Silva y Francisca Carrasco Lozano";
pres.subject = "ADY1104 Visualización de Datos · EP6";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "PORTADA",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.6, fontSize: 44, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.8, w: 11.0, h: 1.2, fontSize: 20, color: C.background1, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: C.background1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.32, w: 12.1, h: 0.95, fontSize: 30, bold: true, color: C.text1, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "StreamView Analytics · Presentación ejecutiva EP6", options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.text2, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.text2, align: "right" },
});
pres.defineSlideMaster({
  title: "SECCION",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.8, w: 11.7, h: 1.2, fontSize: 40, bold: true, color: C.background1, align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.1, w: 11.7, h: 0.8, fontSize: 18, color: C.background1, align: "left", margin: 0 }, text: "" } },
  ],
});

// ------------------------------------------------------------------ ayudas
const ESTADO = {
  ok: { t: "✓ Cumple", c: C.accent3 },
  riesgo: { t: "! En riesgo", c: C.accent4 },
  no: { t: "✕ No cumple", c: C.accent5 },
};
const ESTADO_OSCURO = { ok: "3FB950", riesgo: "D29922", no: "F85149" }; // contraste > 4,5:1 sobre #24292F
function pastilla(slide, x, y, est, w = 1.45, fondo = C.background1) {
  const col = fondo === C.text1 ? ESTADO_OSCURO[est] : ESTADO[est].c;
  slide.addText(ESTADO[est].t, {
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.5, x, y, w, h: 0.36, isTextBox: true,
    fill: { color: fondo }, line: { color: col, width: 1.5 },
    color: col, bold: true, fontSize: 12, align: "center", valign: "middle", margin: 0, objectName: "estado",
  });
}
function texto(slide, t, o) {
  slide.addText(t, Object.assign({ isTextBox: true, margin: 0, color: C.text1, fontSize: 14, valign: "top" }, o));
}
function tarjeta(slide, x, y, w, h, nombre) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: LINEA, width: 1 }, objectName: nombre || "tarjeta" });
}
function tamanoPng(archivo) {   // ancho y alto reales del PNG (bytes 16-23 de la cabecera IHDR)
  const b = fs.readFileSync(EV(archivo));
  return [b.readUInt32BE(16), b.readUInt32BE(20)];
}
function imagen(slide, archivo, x, y, w, alt, hMax = 99) {
  const [pxW, pxH] = tamanoPng(archivo);
  let ancho = w, alto = w * pxH / pxW;
  if (alto > hMax) { alto = hMax; ancho = hMax * pxW / pxH; x += (w - ancho) / 2; }
  slide.addImage({ path: EV(archivo), x, y, w: ancho, h: alto, altText: alt, objectName: alt.slice(0, 40) });
}
function tabla(slide, filas, x, y, w, colW, fs = 12, rowH = undefined) {
  const rows = filas.map((f, i) => f.map((celda) => ({
    text: celda,
    options: i === 0
      ? { bold: true, color: C.background1, fill: { color: C.text1 }, fontSize: fs }
      : { color: C.text1, fill: { color: i % 2 ? C.background1 : C.background2 }, fontSize: fs },
  })));
  slide.addTable(rows, { x, y, w, colW, border: { type: "solid", pt: 0.75, color: LINEA }, margin: 0.08, valign: "middle", fontFace: THEME.bodyFontFace, rowH });
}
function nueva(seccion, layout = "CONTENIDO") {
  return pres.addSlide({ masterName: layout, sectionTitle: seccion });
}

// ================================================================== 1. PORTADA
pres.addSection({ title: "Apertura" });
let s = nueva("Apertura", "PORTADA");
s.addText("StreamView Analytics", { placeholder: "title" });
s.addText("De métricas a KPIs: un tablero que dice dónde actuar", { placeholder: "body" });
pastilla(s, 0.8, 1.15, "ok", 1.45, C.text1);
pastilla(s, 2.4, 1.15, "riesgo", 1.6, C.text1);
pastilla(s, 4.15, 1.15, "no", 1.7, C.text1);
texto(s, "Presentación ejecutiva y defensa técnica · EP6 · ADY1104 Visualización de Datos\nFelipe Ahumada Silva · Francisca Carrasco Lozano · Noviembre 2026",
  { x: 0.8, y: 5.9, w: 11.5, h: 0.8, fontSize: 14, color: C.background1 });
s.addNotes("Presenta: Felipe (20 s). Somos el equipo consultor de StreamView. En EP5 revisamos el dashboard que entregamos en EP4 y lo optimizamos. Hoy mostramos qué cambió, por qué, qué encontramos y qué recomendamos decidir. Las tres pastillas son el código que van a ver en todo el tablero: cumple, en riesgo y no cumple.");

// ================================================================== 2. PROBLEMA + CAMBIO CLAVE
pres.addSection({ title: "Contexto y KPIs" });
s = nueva("Contexto y KPIs");
s.addText("Teníamos métricas; ahora tenemos KPIs que piden decisiones", { placeholder: "title" });
const bloques = [
  ["Problema", "StreamView decide qué adquirir, qué promover y dónde invertir con reportes que no coinciden entre áreas."],
  ["Audiencia", "Directorio · Contenidos y Adquisición · Marketing · Data & Analytics: un perfil del tablero para cada una."],
  ["Lo que corregimos", "En EP4 mostrábamos cifras sin meta (\"26% bien evaluadas\", \"Japón\"). Describían, pero no decían si había que actuar."],
  ["Ahora", "3 KPIs con meta a dic. 2026, responsable y la decisión que gatillan; el resto del tablero los respalda."],
];
bloques.forEach(([t, d], i) => {
  texto(s, [{ text: t, options: { bold: true, breakLine: true, fontSize: 15 } }, { text: d, options: { fontSize: 13, color: C.text2 } }],
    { x: 0.6 + i * 3.1, y: 1.35, w: 2.85, h: 1.6 });
});
imagen(s, "comparativas/c1_kpis.png", 0.6, 3.05, 12.1, "Antes y después: métricas sin meta frente a la vista del Directorio con KPIs, meta, estado y decisiones", 3.75);
s.addNotes("Presenta: Francisca (1 min). El caso plantea que cada área usa reportes distintos y que hay múltiples versiones de un mismo indicador. La observación que recibimos fue que confundíamos métricas con KPIs. Una métrica describe: 26% de las películas está bien evaluada. Un KPI compara contra una meta, tiene plazo y responsable, y gatilla una decisión. A la izquierda de la imagen está la versión EP4; a la derecha, la EP5. Las cifras de catálogo que el caso llama KPIs (total de títulos, países) las mantenemos, pero rotuladas como métricas de contexto: no tienen meta.");

// ================================================================== 3. SCORECARD
s = nueva("Contexto y KPIs");
s.addText("Hoy ningún KPI cumple: K1 en riesgo, K2 y K3 fuera de meta", { placeholder: "title" });
const KP = [
  ["K1", "Películas bien evaluadas", 25.8, 30, "riesgo", "Contenidos y Adquisición", "¿Qué cine adquirir?"],
  ["K2", "Películas de mercados de alto desempeño", 13.5, 18, "no", "Contenidos y Adquisición", "¿De qué mercados?"],
  ["K3", "Series que el público califica", 38.4, 50, "no", "Producto (con Marketing)", "¿Participa el público?"],
];
const coma = (v) => v.toFixed(1).replace(".", ",");
KP.forEach(([id, nom, v, meta, est, resp, preg], i) => {
  const x = 0.6 + i * 4.15, y = 1.5, w = 3.85, h = 4.6;
  tarjeta(s, x, y, w, h, `KPI ${id}`);
  texto(s, preg, { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: 0.35, fontSize: 13, color: C.text2 });
  texto(s, id, { x: x + 0.25, y: y + 0.65, w: 0.8, h: 0.4, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
  pastilla(s, x + w - 1.8, y + 0.67, est, 1.55, C.background2);
  texto(s, nom, { x: x + 0.25, y: y + 1.2, w: w - 0.5, h: 0.75, fontSize: 18, bold: true });
  texto(s, `${coma(v)}%`, { x: x + 0.25, y: y + 2.0, w: w - 0.5, h: 0.9, fontSize: 44, bold: true, valign: "middle" });
  texto(s, `meta ≥ ${meta}% · faltan ${coma(meta - v)} puntos`, { x: x + 0.25, y: y + 2.9, w: w - 0.5, h: 0.4, fontSize: 14 });
  // gráfico de bala: tramo de alerta, valor y meta
  const bx = x + 0.25, bw = w - 0.5, by = y + 3.45, tope = meta * 1.3, px = (q) => bw * q / tope;
  s.addShape(pres.shapes.RECTANGLE, { x: bx, y: by, w: bw, h: 0.2, fill: { color: "EEF1F4" }, line: { type: "none" }, objectName: "bala fondo" });
  s.addShape(pres.shapes.RECTANGLE, { x: bx + px(meta * 0.85), y: by, w: px(meta * 0.15), h: 0.2, fill: { color: "D8DEE4" }, line: { type: "none" }, objectName: "bala alerta" });
  s.addShape(pres.shapes.RECTANGLE, { x: bx + px(meta), y: by, w: bw - px(meta), h: 0.2, fill: { color: "BCC5CE" }, line: { type: "none" }, objectName: "bala cumple" });
  s.addShape(pres.shapes.RECTANGLE, { x: bx, y: by + 0.065, w: px(v), h: 0.07, fill: { color: C.text1 }, line: { type: "none" }, objectName: "bala valor" });
  s.addShape(pres.shapes.RECTANGLE, { x: bx + px(meta) - 0.015, y: by - 0.07, w: 0.03, h: 0.34, fill: { color: C.text1 }, line: { type: "none" }, objectName: "bala meta" });
  texto(s, `Responsable: ${resp}`, { x: x + 0.25, y: y + 3.95, w: w - 0.5, h: 0.4, fontSize: 12, color: C.text2 });
});
texto(s, "Metas a diciembre de 2026 · en riesgo = hasta 15% bajo la meta · K1 ya superó su meta en 2019-2021, K2 en 2020 y K3 llega a 49,7% en 2024",
  { x: 0.6, y: 6.4, w: 12.1, h: 0.35, fontSize: 12, color: C.text2 });
s.addNotes("Presenta: Felipe (1 min 15 s). Elegimos tres KPIs, uno por cada decisión central del caso: qué cine adquirir (K1, películas bien evaluadas), de qué mercados (K2, peso de Japón, Corea del Sur y México) y si el público participa con las series (K3, series con al menos 10 votos). Cada tarjeta trae valor, meta, brecha, estado y responsable. La barra es un gráfico de bala: la línea vertical es la meta y la barra oscura el valor actual. Regla única: cumple si alcanza la meta; en riesgo si queda hasta 15% bajo ella. Que ninguno cumpla no es un error: las metas apuntan a 2026. Las inventamos nosotros porque el caso no las trae, pero no son arbitrarias: K1 ya superó su meta con los estrenos de 2019-2021, K2 en 2020 y K3 llega a 49,7% en 2024. Si preguntan por qué no hay un KPI de rentabilidad: solo 21,7% de las películas tiene datos financieros confiables; la usamos como evidencia, no como KPI.");

// ================================================================== 4. HALLAZGO MERCADOS
pres.addSection({ title: "Hallazgos" });
s = nueva("Hallazgos");
s.addText("Japón, Corea y México duplican la calidad de EE.UU.", { placeholder: "title" });
const paises = ["Japón", "Corea del Sur", "México", "India", "Suecia", "China", "Alemania", "España", "Reino Unido", "EE.UU."];
const vals = [51.0, 46.8, 42.8, 36.6, 27.7, 25.9, 25.5, 24.3, 24.0, 22.7];
const serie = (idx) => vals.map((v, i) => (idx.includes(i) ? v : 0));
s.addChart(
  [
    { type: pres.charts.BAR, data: [
        { name: "Mercados de K2", labels: paises, values: serie([0, 1, 2]) },
        { name: "Otros países", labels: paises, values: serie([3, 4, 5, 6, 7, 8]) },
        { name: "EE.UU. (mayor proveedor)", labels: paises, values: serie([9]) },
      ], options: { barGrouping: "stacked", chartColors: [HEX.accent1, GRIS_BARRA, HEX.dk1], barGapWidthPct: 45,
        showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: '0"%";;;', dataLabelColor: "FFFFFF", dataLabelFontSize: 12, dataLabelFontFace: "+mn-lt" } },
    { type: pres.charts.LINE, data: [{ name: "Meta K1: 30%", labels: paises, values: paises.map(() => 30) }],
      options: { chartColors: [HEX.dk1], lineDash: "dash", lineSize: 2, lineDataSymbol: "none" } },
  ],
  { x: 0.5, y: 1.35, w: 8.4, h: 5.3, barDir: "col", showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    valAxisMaxVal: 60, valAxisMinVal: 0, valAxisMajorUnit: 10, valAxisLabelFormatCode: '0"%"', valAxisLabelColor: HEX.dk2, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E6E9ED", size: 0.75 }, catGridLine: { style: "none" },
    showTitle: true, title: "Películas bien evaluadas (calificación ≥ 7, con 10+ votos) por país", titleFontSize: 13, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
    altText: "Porcentaje de películas bien evaluadas por país: Japón 51%, Corea del Sur 47%, México 43%, EE.UU. 23%; meta de K1 30%" }
);
texto(s, [{ text: "50%", options: { fontSize: 40, bold: true, breakLine: true } }, { text: "de las películas son de EE.UU., y solo 23% de ellas está bien evaluada", options: { fontSize: 14 } }], { x: 9.3, y: 1.5, w: 3.4, h: 1.6 });
texto(s, [{ text: "13,5%", options: { fontSize: 40, bold: true, breakLine: true, color: C.accent1 } }, { text: "aportan Japón, Corea del Sur y México (K2). Meta: 18%", options: { fontSize: 14 } }], { x: 9.3, y: 3.3, w: 3.4, h: 1.6 });
texto(s, "Robusto con 3 métodos (comparación directa, mismo género y año, promedio bayesiano) y bases de 236 a 871 películas por país.", { x: 9.3, y: 5.15, w: 3.4, h: 1.3, fontSize: 12, color: C.text2 });
s.addNotes("Presenta: Francisca (1 min). Qué ocurre: en Japón, Corea del Sur y México entre 43% y 51% de las películas está bien evaluada; en EE.UU., 23%. Sin embargo, EE.UU. aporta la mitad de las películas y esos tres mercados solo el 13,5%. Por qué elegimos columnas ordenadas con una línea de meta: comparamos magnitudes entre categorías, la longitud es el canal más preciso y la línea dice qué valor es suficiente. Descartamos un mapa: el área de EE.UU. dominaría la imagen y el hallazgo es un ranking, no un patrón geográfico. Riesgo que reconocemos: esto no prueba causalidad; lo que se exporta de esos países ya es una selección. Por eso recomendamos un piloto medido.");

// ================================================================== 5. HALLAZGO PARTICIPACIÓN (K3)
s = nueva("Hallazgos");
s.addText("En series, falta que el público califique", { placeholder: "title" });
const gen3 = ["Conversación", "Reality", "Documental", "Familia", "Telenovela", "Infantil", "Bélico", "Drama", "Comedia", "Misterio", "Animación", "Crimen", "Acción", "Aventura", "Fantasía", "Ciencia ficción"];
const val3 = [14.1, 23.5, 28.1, 30.8, 32.2, 35.2, 42.1, 44.0, 50.3, 58.7, 62.1, 62.1, 65.2, 65.2, 69.2, 69.2];
s.addChart(pres.charts.BAR, [
  { name: "Bajo la meta de K3 (50%)", labels: gen3, values: val3.map((v) => (v < 50 ? v : 0)) },
  { name: "Sobre la meta", labels: gen3, values: val3.map((v) => (v >= 50 ? v : 0)) },
], { x: 0.5, y: 1.35, w: 8.4, h: 5.3, barDir: "bar", barGrouping: "stacked", barGapWidthPct: 35, chartColors: [GRIS_BARRA, HEX.accent3],
  showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: '0"%";;;', dataLabelColor: "FFFFFF", dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
  catAxisOrientation: "maxMin", valAxisMaxVal: 100, valAxisMinVal: 0, valAxisHidden: true,
  catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
  valGridLine: { style: "none" }, catGridLine: { style: "none" },
  showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
  showTitle: true, title: "Series con 10 o más votos (K3) por género, de 0 a 100%", titleFontSize: 13, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
  altText: "K3 por género: Conversación 14%, Reality 23%, Documental 28%; Fantasía y Ciencia ficción 69%; meta 50%" });
texto(s, [{ text: "38%", options: { fontSize: 40, bold: true, breakLine: true } }, { text: "de las series tiene votos suficientes para saber si gusta (meta: 50%)", options: { fontSize: 14 } }], { x: 9.3, y: 1.5, w: 3.4, h: 1.6 });
texto(s, [{ text: "4.501", options: { fontSize: 40, bold: true, breakLine: true } }, { text: "series con público (popularidad sobre la típica) aún no tienen 10 votos: el primer lugar donde pedir calificaciones", options: { fontSize: 14 } }], { x: 9.3, y: 3.3, w: 3.4, h: 2.0 });
texto(s, "La cohorte 2024 ya llega a 49,7%: la meta es alcanzable.", { x: 9.3, y: 5.55, w: 3.4, h: 0.8, fontSize: 12, color: C.text2 });
s.addNotes("Presenta: Felipe (1 min). K3 mide si el público participa: sin al menos 10 votos no sabemos si una serie gusta ni si conviene renovarla. Hoy solo el 38% de las series llega a ese umbral. Los géneros con menos participación son Conversación (14%), Reality (23%) y Documental (28%); Fantasía y Ciencia ficción ya superan el 69%. Además hay 4.501 series con público que todavía no tienen 10 votos: ese es el primer lugar donde Producto y Marketing deben pedir calificaciones. Elegimos barras horizontales ordenadas porque comparamos 16 categorías con nombres largos en la misma escala de 0 a 100%; el verde marca las que superan la meta.");

// ================================================================== 6. HALLAZGO RENTABILIDAD (EVIDENCIA DE K1 Y K2)
s = nueva("Hallazgos");
s.addText("Invertir en calidad rinde", { placeholder: "title" });
const tramos = ["Nota bajo 5", "5 a 6", "6 a 7", "7 a 8", "8 o más"];
const recup = [42.0, 49.2, 62.1, 76.3, 88.9];
s.addChart(pres.charts.BAR, [
  { name: "Películas bajo nota 7", labels: tramos, values: recup.map((v, i) => (i < 3 ? v : 0)) },
  { name: "Películas bien evaluadas (K1)", labels: tramos, values: recup.map((v, i) => (i >= 3 ? v : 0)) },
], { x: 0.5, y: 1.35, w: 8.4, h: 5.3, barDir: "col", barGrouping: "stacked", barGapWidthPct: 45, chartColors: [GRIS_BARRA, HEX.dk1],
  showValue: true, dataLabelPosition: "inEnd", dataLabelFormatCode: '0"%";;;', dataLabelColor: "FFFFFF", dataLabelFontSize: 13, dataLabelFontFace: "+mn-lt",
  valAxisMaxVal: 100, valAxisMinVal: 0, valAxisMajorUnit: 25, valAxisLabelFormatCode: '0"%"', valAxisLabelColor: HEX.dk2, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt",
  catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
  valGridLine: { color: "E6E9ED", size: 0.75 }, catGridLine: { style: "none" },
  showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
  showTitle: true, title: "Películas que recuperan su presupuesto en taquilla, según su nota", titleFontSize: 13, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
  altText: "Recuperan su presupuesto: nota bajo 5, 42%; 5 a 6, 49%; 6 a 7, 62%; 7 a 8, 76%; 8 o más, 89%" });
texto(s, [{ text: "77% vs 58%", options: { fontSize: 34, bold: true, breakLine: true } }, { text: "de las películas bien evaluadas recupera su presupuesto, frente a las demás: subir K1 también es una decisión financiera", options: { fontSize: 14 } }], { x: 9.3, y: 1.5, w: 3.4, h: 2.2 });
texto(s, [{ text: "70% vs 66%", options: { fontSize: 34, bold: true, breakLine: true, color: C.accent1 } }, { text: "Japón, Corea del Sur y México frente a EE.UU.: la cuota de K2 no sacrifica rentabilidad", options: { fontSize: 14 } }], { x: 9.3, y: 3.85, w: 3.4, h: 1.9 });
texto(s, "Solo 3.468 películas (21,7%) tienen datos financieros confiables, y 179 de los mercados de K2: es evidencia, no un KPI.", { x: 9.3, y: 5.85, w: 3.4, h: 0.8, fontSize: 12, color: C.text2 });
s.addNotes("Presenta: Francisca (1 min). La rentabilidad no es un KPI, pero respalda a K1 y K2. La proporción de películas que recuperan su presupuesto sube con la nota: de 42% (nota bajo 5) a 89% (8 o más). Las bien evaluadas recuperan el 77% de las veces y las demás el 58%. Y las de Japón, Corea del Sur y México recuperan al menos tanto como las de EE.UU. (70% frente a 66%), aunque con solo 179 películas: no decimos que rindan más, sino que la cuota de K2 no sacrifica rentabilidad. Advertencia: solo 21,7% de las películas tiene datos financieros confiables, sobre todo grandes estudios.");

// ================================================================== 6. DEMO
pres.addSection({ title: "Demostración y mejoras" });
s = nueva("Demostración y mejoras");
s.addText("Demo: de la vista a la decisión en cuatro pasos", { placeholder: "title" });
const pasos = [["1", "Vista", "Control segmentado: Directorio, Contenidos, Marketing o Data & Analytics"], ["2", "Pestaña", "La pregunta de esa audiencia"], ["3", "Filtros", "Botón arriba a la derecha: tipo, años, país, idioma y género"], ["4", "KPI + decisión", "Estado frente a la meta y acción del responsable"]];
pasos.forEach(([n, t, d], i) => {
  const x = 0.6 + i * 3.1;
  s.addShape(pres.shapes.OVAL, { x, y: 1.5, w: 0.6, h: 0.6, fill: { color: C.text1 }, line: { type: "none" }, objectName: `paso ${n}` });
  texto(s, n, { x, y: 1.5, w: 0.6, h: 0.6, fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle" });
  texto(s, [{ text: t, options: { bold: true, fontSize: 15, breakLine: true } }, { text: d, options: { fontSize: 12, color: C.text2 } }], { x: x + 0.75, y: 1.45, w: 2.2, h: 1.0 });
});
const escenarios = [
  ["Directorio", "Resumen, sin filtros", "3 KPIs: K1 en riesgo, K2 y K3 no cumplen. La lista de decisiones dice quién actúa.", "riesgo"],
  ["Contenidos y Adquisición", "Mercados · Filtros: género Terror, luego Documental", "K1 cae a 7% (no cumple) y sube a 64% (cumple): qué género adquirir.", "ok"],
  ["Directorio", "Resumen · Filtros: país Japón", "K1 y K3 cumplen. K2 explica que no se evalúa con filtro de país.", "ok"],
  ["Marketing", "Participación · Filtros: series en coreano", "K3 en riesgo (44%) y 414 series con público sin 10 votos: dónde pedir calificaciones.", "riesgo"],
];
escenarios.forEach(([perfil, accion, resultado, est], i) => {
  const x = 0.6 + (i % 2) * 6.2, y = 2.85 + Math.floor(i / 2) * 1.95, w = 5.9, h = 1.75;
  tarjeta(s, x, y, w, h, `escenario ${i + 1}`);
  texto(s, `Escenario ${i + 1} · ${perfil}`, { x: x + 0.25, y: y + 0.18, w: w - 2.1, h: 0.35, fontSize: 14, bold: true, valign: "middle" });
  pastilla(s, x + w - 1.8, y + 0.17, est, 1.55, C.background2);
  texto(s, accion, { x: x + 0.25, y: y + 0.6, w: w - 0.5, h: 0.3, fontSize: 12, color: C.text2 });
  texto(s, resultado, { x: x + 0.25, y: y + 0.95, w: w - 0.5, h: 0.65, fontSize: 14 });
});
s.addNotes("Presenta: Francisca, con el dashboard abierto (2 min 30 s). Usamos la misma versión entregada en EP5: streamlit run dashboard/app.py. Recorrido: (1) Directorio, Resumen: leer en voz alta la frase de arriba (la conclusión), el estado de los KPIs y la lista de qué hacemos. (2) Contenidos y Adquisición, pestaña Mercados: botón Filtros, género Terror y luego Documental; la tarjeta K1 cambia de no cumple a cumple y la frase principal y los títulos se recalculan. (3) Directorio, filtro País Japón: K2 muestra 'sin datos' con el motivo, porque mide la mezcla de países; el ranking por país compara contra todos y destaca Japón. (4) Marketing, pestaña Participación, Tipo Serie e Idioma coreano: K3 del segmento, géneros con menos participación y series con público sin votos. Terminar con Reiniciar filtros. Respaldo, si falla la demo: evidencias/escenarios/*.png.");

// ================================================================== 7. ANTES / DESPUÉS
s = nueva("Demostración y mejoras");
s.addText("Antes y después: del dato al objetivo, legible para todos", { placeholder: "title" });
imagen(s, "comparativas/c2_mercados_meta.png", 0.6, 1.35, 12.1, "Antes y después del gráfico de mercados: se agrega la línea de meta de K1", 3.7);
const tiles = [["1 pantalla", "por pestaña: la conclusión arriba y una tarjeta por pregunta"], ["0 a 100%", "la misma escala y los mismos colores en todas las pantallas"], ["Claro y oscuro", "sigue el modo del sistema (guías de Apple); texto chico a 7,9:1"], ["43 mejoras", "problema, mejora, fundamento y evidencia en el registro"]];
tiles.forEach(([v, d], i) => {
  const x = 0.6 + i * 3.1, y = 5.25, w = 2.85, h = 1.45;
  tarjeta(s, x, y, w, h, `mejora ${i + 1}`);
  texto(s, v, { x: x + 0.2, y: y + 0.15, w: w - 0.4, h: 0.55, fontSize: 22, bold: true, valign: "middle" });
  texto(s, d, { x: x + 0.2, y: y + 0.72, w: w - 0.4, h: 0.65, fontSize: 12, color: C.text2 });
});
s.addNotes("Presenta: Felipe (1 min). Arriba, el mismo gráfico en EP4 y en EP5: agregamos la meta de K1 como línea de referencia y marcamos con estrella los mercados de K2. Así la comparación entre barras pasa a ser una comparación contra el objetivo. Abajo, cuatro mejoras. Rediseñamos con Storytelling with Data: cada pestaña cabe en una pantalla, arriba a la izquierda va una frase con la conclusión y cada pregunta tiene su tarjeta con un solo gráfico. Todo porcentaje va de 0 a 100% y cada color significa lo mismo en todas las pantallas (azul película, naranjo serie, verde supera la meta). Luego lo revisamos con las Human Interface Guidelines de Apple: sigue el modo claro u oscuro del sistema, usa controles segmentados, describe cada gráfico en texto para lectores de pantalla y nunca distingue solo por color (✓ en lo que supera la meta, rayado en las series). Contraste del texto secundario de 3,6 a 7,9:1. En total, 43 mejoras documentadas; la última concentró el tablero en tres KPIs en entregables/evidencias/registro_cambios.md con problema, mejora, fundamento y evidencia. También cambiamos el color primario rojo de Streamlit por uno neutro, porque competía con el rojo de 'no cumple'.");

// ================================================================== 8. DECISIONES TÉCNICAS
pres.addSection({ title: "Evaluación crítica" });
s = nueva("Evaluación crítica");
s.addText("Por qué estos gráficos y no otros", { placeholder: "title" });
tabla(s, [
  ["Representación", "Datos", "Por qué", "Alternativa descartada"],
  ["Tarjeta KPI con gráfico de bala", "Proporción vs meta y umbral", "Valor, meta, brecha y rangos en poco espacio", "Velocímetro: ángulos difíciles de comparar"],
  ["Barras ordenadas con línea de meta", "16-18 categorías × proporción", "La longitud compara con precisión; la línea dice qué es suficiente", "Mapa: el área de EE.UU. distorsiona; torta: no compara 16 partes"],
  ["Línea de KPI por año con meta", "Año de estreno × proporción", "Muestra tendencia y si la meta ya se alcanzó", "Barras por año: sugieren totales"],
  ["Tablas de series sin votos y películas a destacar", "Títulos, votos, nota", "Marketing necesita nombres exactos, no magnitudes", "Dispersión: sirve para explorar, no para elegir"],
  ["Dispersión en escala log", "Popularidad × calificación", "Muestra la forma de la relación (vista técnica)", "Solo el coeficiente: oculta la forma"],
  ["Barras por idioma y por año", "Conteos por categoría y año", "Longitudes desde una base común", "Treemap y áreas: comparar áreas es impreciso"],
], 0.6, 1.4, 12.1, [2.75, 2.45, 3.75, 3.15], 14, [0.45, 0.72, 0.72, 0.72, 0.72, 0.72, 0.72]);
texto(s, "Sin distorsiones: barras desde cero · todo porcentaje de 0 a 100% en todas las pantallas · mínimo de títulos por categoría · películas con películas y series con series.",
  { x: 0.6, y: 6.45, w: 12.1, h: 0.4, fontSize: 12, color: C.text2 });
s.addNotes("Presenta: Francisca (1 min). Cada decisión considera variables, objetivo, audiencia y alternativas. Bala en vez de velocímetro: más compacto y comparable. Barras ordenadas en vez de mapa o torta. Línea para el tiempo. Tabla cuando la tarea es buscar nombres. Dispersión con escala logarítmica solo en la vista técnica, porque la popularidad es muy asimétrica. Reemplazamos el treemap y las áreas que pedía el caso por barras, porque comparar áreas es menos preciso que comparar longitudes. Pregunta probable: '¿por qué las trayectorias van de 0 a 100% si se ven planas?'. Porque usamos la misma escala en todas las pantallas para no exagerar diferencias pequeñas; la cifra exacta va escrita en el título de cada tarjeta.");

// ================================================================== 9. FORTALEZAS
s = nueva("Evaluación crítica");
s.addText("Fortalezas verificables en el dashboard", { placeholder: "title" });
const fort = [
  ["✓", "KPIs accionables", "Cada tarjeta trae meta, brecha, responsable y la decisión que gatilla. Ej.: K1 25,8% frente a 30%."],
  ["◎", "Foco y diseño por audiencia", "3 KPIs y 4 perfiles; cada vista abre con su conclusión y solo sus KPIs."],
  ["↻", "Títulos que se recalculan", "Con el filtro Japón, la conclusión y los estados cambian solos: K1 51% cumple."],
  ["≡", "Reglas contra sesgos", "Calificación con 10+ votos, comparación dentro de formato, finanzas válidas, mínimo de 200 títulos."],
  ["Aa", "Accesible", "Contraste AA, modo claro y oscuro, ✓ y rayado además del color, resumen en texto de cada gráfico."],
  ["⟲", "Reproducible y verificado", "Fuente única en dashboard/streamview, 5/5 pruebas automáticas, capturas regenerables."],
];
fort.forEach(([ic, t, d], i) => {
  const x = 0.6 + (i % 3) * 4.15, y = 1.45 + Math.floor(i / 3) * 2.6, w = 3.85, h = 2.35;
  tarjeta(s, x, y, w, h, `fortaleza ${i + 1}`);
  s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.25, w: 0.65, h: 0.65, fill: { color: C.text1 }, line: { type: "none" }, objectName: `icono ${i + 1}` });
  texto(s, ic, { x: x + 0.25, y: y + 0.25, w: 0.65, h: 0.65, fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle" });
  texto(s, t, { x: x + 1.05, y: y + 0.3, w: w - 1.25, h: 0.55, fontSize: 16, bold: true, valign: "middle" });
  texto(s, d, { x: x + 0.25, y: y + 1.05, w: w - 0.5, h: 1.15, fontSize: 14, color: C.text1 });
});
s.addNotes("Presenta: Felipe (1 min). Seis fortalezas, cada una comprobable en vivo: abrir una tarjeta y mostrar responsable y decisión; cambiar de perfil; aplicar el filtro Japón; mostrar la ficha técnica en Data & Analytics; señalar el texto 'serie / película' en las barras del top 10; correr python dashboard/tests/test_kpis.py.");

// ================================================================== 10. LIMITACIONES
s = nueva("Evaluación crítica");
s.addText("Limitaciones, sesgos y riesgos, con su mitigación", { placeholder: "title" });
tabla(s, [
  ["Riesgo o sesgo", "Consecuencia en la decisión", "Mitigación"],
  ["Sin datos de consumo (reproducciones, suscripciones)", "No se mide retención; K3 aproxima el engagement con los votos de TMDB", "Rotulado explícito; KPI de retención como mejora prioritaria"],
  ["Sesgo de selección: solo títulos con 10+ votos", "K1 describe las películas calificadas; en series solo el 38% tiene nota", "K3 mide justamente esa cobertura"],
  ["Causalidad no demostrada en mercados", "Comprar más cine japonés podría no subir K1 (lo exportado ya es una selección)", "3 métodos de robustez; piloto de adquisición medido por cohorte"],
  ["Sesgo financiero: 21,7% con datos", "La evidencia de rentabilidad describe sobre todo a grandes estudios", "No es KPI, es evidencia; se rotula y se pide completar los datos"],
  ["Metas definidas por el equipo", "Podrían no reflejar la estrategia real", "Basadas en línea base y cohortes recientes; validarlas con cada responsable"],
], 0.6, 1.45, 12.1, [3.6, 4.4, 4.1], 15, [0.5, 0.9, 0.9, 0.9, 0.9, 0.9]);
s.addNotes("Presenta: Francisca (1 min 15 s). El riesgo más importante es de interpretación: K3 no es retención. El catálogo no trae reproducciones ni suscripciones, y lo decimos en el tablero. Segundo: sesgo de selección, porque solo calificamos títulos con 10 o más votos; en series eso es el 38%, y K3 existe justamente para vigilarlo. Tercero: correlación no es causalidad. Que Japón tenga mejores notas no garantiza que comprar más películas japonesas suba K1, porque lo que se exporta ya está filtrado; por eso proponemos un piloto medido. Cuarto: finanzas con 21,7% de cobertura; por eso la rentabilidad no es un KPI, sino evidencia rotulada. Quinto: las metas son supuestos nuestros y deben validarse con los responsables.");

// ================================================================== 11. MEJORAS PRIORIZADAS
pres.addSection({ title: "Propuesta de valor" });
s = nueva("Propuesta de valor");
s.addText("Mejoras pendientes, priorizadas por impacto y esfuerzo", { placeholder: "title" });
const cuad = [
  [1.55, 1.45, "E9F4EC", "1 · Hacer ahora", "M1 Validar metas y umbrales con cada responsable\nM2 Exportar la lista de series sin votos a CSV\nM7 Prueba de usabilidad: 5 usuarios por perfil"],
  [7.2, 1.45, "FBF6E9", "2 · Planificar", "M5 KPIs de retención reales (reproducciones, churn)\nM8 Fecha real de incorporación al catálogo\nM4 Despliegue corporativo con acceso por perfil"],
  [1.55, 4.1, C.background2, "3 · Mejoras rápidas", "M6 Umbral de alerta según la volatilidad de cada KPI\nM9 Borde en barras grises y revisión automática de accesibilidad"],
  [7.2, 4.1, "FDF0F0", "4 · Evaluar después", "M3 Alertas por correo cuando un KPI cambia de estado"],
];
cuad.forEach(([x, y, fill, t, d], i) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.45, h: 2.45, rectRadius: 0.08, fill: { color: fill }, line: { color: LINEA, width: 1 }, objectName: `cuadrante ${i + 1}` });
  texto(s, t, { x: x + 0.25, y: y + 0.2, w: 5.0, h: 0.4, fontSize: 16, bold: true });
  texto(s, d, { x: x + 0.25, y: y + 0.7, w: 5.0, h: 1.6, fontSize: 14, paraSpaceAfter: 4 });
});
texto(s, "Impacto\nalto", { x: 0.5, y: 1.45, w: 0.95, h: 2.45, fontSize: 12, bold: true, color: C.text2, valign: "middle", align: "center" });
texto(s, "Impacto\nmedio", { x: 0.5, y: 4.1, w: 0.95, h: 2.45, fontSize: 12, bold: true, color: C.text2, valign: "middle", align: "center" });
texto(s, "Esfuerzo bajo", { x: 1.55, y: 6.6, w: 5.45, h: 0.3, fontSize: 12, bold: true, color: C.text2, align: "center" });
texto(s, "Esfuerzo alto", { x: 7.2, y: 6.6, w: 5.45, h: 0.3, fontSize: 12, bold: true, color: C.text2, align: "center" });
s.addNotes("Presenta: Felipe (1 min). Priorizamos por impacto en la decisión y por esfuerzo (tiempo y datos nuevos). Primero, validar metas con cada responsable: todo lo demás depende de que las acepten, y es un taller de una hora. La de mayor impacto a largo plazo es tener datos de reproducción para medir retención de verdad, pero requiere datos que hoy no tenemos: por eso va a planificar. Cada mejora nace de una brecha que mostramos en la lámina anterior.");

// ================================================================== 12. RECOMENDACIONES E IMPACTO
s = nueva("Propuesta de valor");
s.addText("Cada recomendación se apoya en un KPI y se puede verificar", { placeholder: "title" });
tabla(s, [
  ["Recomendación (responsable)", "Evidencia", "KPI", "Impacto esperado", "Cómo se verifica"],
  ["R1 Cuota de licencias para Japón, Corea del Sur y México; priorizar Animación, Documental y Música (Contenidos y Adquisición)", "Duplican la calidad de EE.UU.; 9 de 18 géneros ya cumplen", "K1 25,8 → 30%\nK2 13,5 → 18%", "K2 en meta aporta ~1,2 puntos a K1; la mezcla de géneros, el resto", "Piloto: calidad de las compras nuevas frente a la línea base, trimestral"],
  ["R2 Pedir calificación al terminar un episodio y destacar las series con público sin votos, partiendo por Conversación, Reality y Documental (Producto y Marketing)", "Solo 38% de las series tiene 10+ votos; 4.501 series con público sin votos", "K3 38,4 → 50%", "~1.850 series más evaluables para decidir renovaciones", "K3 trimestral; series que pasan a 10+ votos"],
  ["R3 Usar la nota y el mercado (K1, K2) como criterio de inversión y completar los datos financieros (Gerencia General, Data & Analytics)", "Bien evaluadas recuperan 77% frente a 58%; 21,7% con datos", "K1 y K2 como criterio", "Menos películas que no recuperan su presupuesto", "Tasa de recuperación de las compras nuevas por cohorte"],
], 0.6, 1.4, 12.1, [3.6, 2.6, 1.6, 2.2, 2.1], 14, [0.5, 1.55, 1.55, 1.4]);
s.addNotes("Presenta: Francisca (1 min 30 s). Cada recomendación sale de un hallazgo y mueve un KPI o lo usa como criterio. R1: si K2 llega a 18% con las tasas actuales, K1 sube cerca de 1,2 puntos; el resto debe venir de la mezcla de géneros. Se mide con un piloto: la calidad de las compras nuevas contra la línea base. R2: cerrar los 11,6 puntos de K3 equivale a unas 1.850 series más con 10 votos; las 4.501 series con público sin votos son el primer objetivo. Se mide con K3 trimestral. R3: como las bien evaluadas recuperan su presupuesto más seguido (77% frente a 58%), K1 y K2 sirven también como criterio de inversión; y hay que completar los datos financieros para que esa evidencia represente a todo el catálogo. Para quién: Directorio y cuatro gerencias. Cómo sabremos si funcionó: el mismo dashboard recalcula los KPIs cada trimestre.");

// ================================================================== 13. CIERRE
s = nueva("Propuesta de valor", "PORTADA");
s.addText("Lo que pedimos decidir hoy", { placeholder: "title" });
s.addText("Aprobar las 3 metas a 2026 y sus responsables, y revisar el tablero cada trimestre: si un KPI no se mueve en dos trimestres, se revisa la decisión que lo sostiene.", { placeholder: "body" });
pastilla(s, 0.8, 5.6, "no", 1.7, C.text1);
texto(s, "→", { x: 2.6, y: 5.55, w: 0.5, h: 0.45, fontSize: 22, color: C.background1, align: "center", valign: "middle" });
pastilla(s, 3.15, 5.6, "riesgo", 1.6, C.text1);
texto(s, "→", { x: 4.85, y: 5.55, w: 0.5, h: 0.45, fontSize: 22, color: C.background1, align: "center", valign: "middle" });
pastilla(s, 5.4, 5.6, "ok", 1.45, C.text1);
texto(s, "Así se verá el impacto de cada decisión en el dashboard", { x: 7.1, y: 5.6, w: 5.5, h: 0.4, fontSize: 14, color: C.background1, valign: "middle" });
s.addNotes("Presenta: Felipe (30 s). Cerramos con una decisión concreta: aprobar las metas y los responsables. El éxito se verá cuando los KPIs pasen de no cumple a en riesgo y luego a cumple. Gracias; quedamos atentos a sus preguntas. En las láminas de anexo están la ficha técnica de los KPIs, las trayectorias y las reglas de calidad.");

// ================================================================== ANEXOS
pres.addSection({ title: "Anexos" });
s = nueva("Anexos", "SECCION");
s.addText("Anexos de respaldo", { placeholder: "title" });
s.addText("Ficha técnica de los KPIs · trayectorias contra la meta · reglas de calidad y verificación", { placeholder: "body" });
s.addNotes("Láminas para responder preguntas cruzadas; no se exponen en los 10 minutos.");

s = nueva("Anexos");
s.addText("A1 · Ficha técnica de los KPIs", { placeholder: "title" });
tabla(s, [
  ["KPI", "Fórmula", "Base", "Meta", "Decisión si no cumple"],
  ["K1 Películas bien evaluadas", "Películas con calificación ≥ 7 / películas con 10+ votos", "25,8%", "≥ 30%", "Priorizar géneros y mercados sobre 30%; no renovar películas bajo 5,0"],
  ["K2 Mercados de alto desempeño", "Películas de Japón, Corea del Sur o México / películas con país", "13,5%", "≥ 18%", "Cuota de licencias para los 3 mercados"],
  ["K3 Series que el público califica", "Series con 10+ votos / series", "38,4%", "≥ 50%", "Pedir calificación al terminar un episodio; destacar series con público sin votos"],
], 0.6, 1.4, 12.1, [2.55, 4.0, 0.9, 0.9, 3.75], 14, [0.5, 1.1, 1.1, 1.1]);
texto(s, "Plazo de todas las metas: diciembre de 2026 · medición trimestral · en riesgo = hasta 15% bajo la meta · definición única en dashboard/streamview/kpis.py",
  { x: 0.6, y: 6.55, w: 12.1, h: 0.35, fontSize: 11, color: C.text2 });
s.addNotes("Respaldo para preguntas sobre fórmulas y metas. Detalle de la justificación de cada meta en la ficha técnica del dashboard (Data & Analytics) y en la sección 4 del informe.");

s = nueva("Anexos");
s.addText("A2 · Las metas son alcanzables", { placeholder: "title" });
imagen(s, "figuras/f3_trayectorias.png", 0.6, 1.35, 12.1, "Trayectoria de K1, K2 y K3 por año de estreno contra su meta", 4.0);
[["K1", "31-32% en 2019-2021; los estrenos de 2024 quedan a 1 punto (29,0%)."],
 ["K2", "19% en 2020, pero 10% en 2024: se aleja; por eso pedimos una cuota de licencias."],
 ["K3", "sube cada año, de 30% (2010) a 49,7% (2024): la cohorte reciente ya roza la meta."]].forEach(([k, t], i) => {
  texto(s, [{ text: `${k}: `, options: { bold: true } }, { text: t }], { x: 0.6 + i * 4.15, y: 5.5, w: 3.85, h: 0.85, fontSize: 14 });
});
texto(s, "Cada punto son los títulos estrenados ese año. 2025 se excluye: menos del 10% de sus títulos tiene votos suficientes.", { x: 0.6, y: 6.45, w: 12.1, h: 0.35, fontSize: 12, color: C.text2 });
s.addNotes("Respaldo para la pregunta '¿cómo saben que las metas son realistas?'.");

s = nueva("Anexos");
s.addText("A3 · Reglas de calidad y verificación técnica", { placeholder: "title" });
tabla(s, [
  ["Regla", "Por qué", "KPIs"],
  ["Calificación solo con 10+ votos", "14% de los títulos no tiene votos y su calificación viene en 0", "K1, K3"],
  ["Comparar dentro de un formato", "Las series tienen el triple de popularidad: paradoja de Simpson", "Rankings de K1"],
  ["Finanzas ≥ US$10.000 y retorno ≤ 50 veces", "Hay presupuestos de US$1; quedan 3.468 películas", "Finanzas"],
  ["Mediana de popularidad; ≥ 200 títulos por categoría", "Valores extremos y rankings con pocos casos", "Rankings"],
], 0.6, 1.4, 7.4, [2.6, 3.7, 1.1], 14, [0.5, 1.0, 1.0, 1.0, 1.0]);
tarjeta(s, 8.35, 1.4, 4.35, 4.5, "verificación");
texto(s, [
  { text: "Verificación técnica", options: { bold: true, fontSize: 16, breakLine: true } },
  { text: "python dashboard/tests/test_kpis.py → 5/5 pruebas", options: { breakLine: true } },
  { text: "31.991 títulos integrados; 9 duplicados removidos", options: { breakLine: true } },
  { text: "Línea base de los 3 KPIs = datos", options: { breakLine: true } },
  { text: "Filtros recalculan KPIs y estados", options: { breakLine: true } },
  { text: "Mismo módulo en notebook y dashboard", options: {} },
], { x: 8.6, y: 1.6, w: 3.9, h: 4.2, fontSize: 14, paraSpaceAfter: 8 });
s.addNotes("Respaldo para preguntas sobre calidad de datos. Detalle en la Sección 2 del notebook y en el README.");

(async () => {
  await pres.writeFile({ fileName: SALIDA });
  if (APPLY_THEME) {
    const { applyTheme } = require(APPLY_THEME);
    await applyTheme(SALIDA, THEME);
  }
  console.log("ok", SALIDA);
})();
