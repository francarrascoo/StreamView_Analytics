# Guía de defensa EP6 · StreamView Analytics

Guía de estudio para la presentación grupal (10 min) y la defensa individual (hasta 5 min de preguntas por
persona). **La nota es individual y las preguntas pueden ser sobre cualquier parte del proyecto**, no solo sobre
las láminas que cada uno expone, así que ambos deben dominar toda la guía.

Material de apoyo: `entregables/Presentacion_EP6_StreamView_Analytics.pptx` (las notas del orador traen el guion
de cada lámina), `entregables/Informe_Ejecutivo_EP5_StreamView_Analytics.pdf`, `entregables/evidencias/registro_cambios.md` y
el dashboard (`streamlit run dashboard/app.py`).

## 1. Plan de los 10 minutos

| Lámina | Contenido | Presenta | Tiempo |
|---|---|---|---|
| 1 | Portada | Felipe | 0:20 |
| 2 | Problema, audiencia y cambio de métricas a KPIs | Francisca | 1:00 |
| 3 | Los 3 KPIs hoy | Felipe | 1:00 |
| 4 | Hallazgo: mercados (K1, K2) | Francisca | 0:50 |
| 5 | Hallazgo: participación en series (K3) | Felipe | 0:50 |
| 6 | Hallazgo: invertir en calidad rinde (evidencia de K1 y K2) | Francisca | 0:50 |
| 7 | **Demo en vivo** (4 escenarios) | Francisca | 2:15 |
| 8 | Antes y después | Felipe | 0:40 |
| 9 | Por qué estos gráficos | Francisca | 0:30 |
| 10-11 | Fortalezas, y limitaciones con mitigación | Felipe / Francisca | 0:30 c/u |
| 12-13 | Mejoras priorizadas, y recomendaciones e impacto | Felipe / Francisca | 0:20 c/u |
| 14 | Decisión que pedimos | Felipe | 0:10 |

Si falta tiempo, acortar las láminas 10 a 12: lo mismo está en el informe y se puede retomar en las preguntas.
**No leer las láminas** (condición explícita de la pauta): cada lámina tiene una frase principal; decirla con
palabras propias y mostrar la evidencia.

### Antes de entrar

- [ ] Dashboard abierto en `http://localhost:8501`, perfil Directorio, sin filtros. Probarlo 10 minutos antes.
- [ ] Presentación en modo presentador (para ver las notas).
- [ ] Respaldo si falla la demo: `entregables/evidencias/escenarios/*.png` y `entregables/evidencias/despues/*.png`.
- [ ] Terminal lista con `python dashboard/tests/test_kpis.py`, por si preguntan cómo se verificó.

## 2. Guion de la demostración (lámina 7)

1. **Directorio → Resumen.** Leer la frase de arriba: "Ningún KPI cumple su meta todavía. La mejor calidad de
   cine está en mercados que casi no compramos". Mostrar los 3 KPIs (K1 en riesgo; K2 y K3 no cumplen; pasar el
   mouse sobre una tarjeta muestra fórmula y responsable) y la tarjeta *¿Qué hacer ahora?*.
2. **Contenidos y Adquisición → Mercados.** Botón **Filtros** → Género = Terror: "K1 cae a 7%, no cumple".
   Cambiar a Documental: "sube a 64%, cumple; la frase principal y los títulos se recalculan solos".
3. **Directorio → Filtros → País = Japón.** "K1 51% y K3 63%: cumplen. K2 dice 'sin datos' y explica
   por qué: mide la mezcla de países. El ranking no se recorta: Japón aparece en negrita como 1° de 16".
4. **Marketing → Participación**, Filtros: Tipo = Serie e Idioma = coreano. "K3 en riesgo (44%), los géneros
   con menos participación del segmento y 414 series con público que aún no tienen 10 votos: dónde pedir
   calificaciones".
5. **Reiniciar filtros.** Directorio, pestaña *Avance hacia la meta*: "las metas son realistas: K1 ya la superó
   con los estrenos de 2019-2021, K2 en 2020 y K3 llega a 49,7% en 2024". Si sobra tiempo, pestaña *Rentabilidad*:
   "las bien evaluadas recuperan su presupuesto 77% frente a 58%".

Remarcar al pasar por las pantallas las reglas de diseño (lámina 8): todo cabe en una pantalla, la conclusión va
arriba a la izquierda, cada pregunta tiene su tarjeta con un gráfico, y las escalas y colores son los mismos en
todas las pantallas.

## 3. Cifras que hay que saber de memoria

| Dato | Valor |
|---|---|
| Títulos integrados | 31.991 (16.000 películas + 15.991 series; 9 series duplicadas removidas) |
| K1 Películas bien evaluadas | 25,8% → meta 30% · en riesgo · Contenidos y Adquisición |
| K2 Películas de Japón, Corea del Sur, México | 13,5% → meta 18% · no cumple · Contenidos y Adquisición |
| K3 Series con 10+ votos | 38,4% → meta 50% · no cumple · Producto (con Marketing) |
| Regla de estado | Cumple ≥ meta; en riesgo hasta 15% bajo la meta (alerta = meta × 0,85); no cumple bajo eso |
| Mercados | Japón 51%, Corea del Sur 47%, México 43% frente a EE.UU. 23%; EE.UU. = 50% de las películas |
| Géneros (K1) | 9 de 18 cumplen K1; Documental 64%, Animación 53%, Música 53%; Terror 7%, Suspenso 13% |
| Géneros (K3) | 8 de 16 cumplen K3; Conversación 14%, Reality 23%, Documental 28%; Fantasía y Ciencia ficción 69% |
| Series con público sin votos | 4.501 (popularidad sobre la típica de las series y menos de 10 votos); cerrar K3 = ~1.850 series más con votos |
| Rentabilidad (evidencia, no KPI) | Recuperan su presupuesto: bien evaluadas 77% frente a 58%; de nota bajo 5 a 8 o más, 42% → 89%; mercados de K2 70% (179 películas) frente a EE.UU. 66%; solo 21,7% de las películas tiene finanzas confiables |
| Cohortes y la meta | K1 2019-2021 (31-32%) · K2 2020 (19%), pero 10% en 2024 · K3 llega a 49,7% en 2024 |
| Accesibilidad | Texto secundario 3,58:1 → 7,92:1; estados verde 5,1:1, ámbar 4,9:1, rojo 5,4:1; modo oscuro de 5,6:1 a 16:1 |

## 4. Preguntas cruzadas probables, por indicador de la rúbrica

### IE26 · Justifica la selección de representaciones (12%)

*Para el 100%: decir variables, objetivo, audiencia y la alternativa que se descartó.*

- **¿Por qué un gráfico de bala y no un velocímetro?** La variable es una proporción que se compara contra una
  meta y dos umbrales. La bala muestra valor, meta, brecha y rangos en poco espacio y en escala lineal; el
  velocímetro usa ángulos (difíciles de comparar), ocupa más espacio y es decorativo. Audiencia: Directorio, que
  necesita comparar los 3 KPIs de un vistazo.
- **¿Por qué no un mapa para los países?** Es una variable categórica (16 países con al menos 200 películas)
  medida en proporción, y la pregunta es un ranking contra una meta. En un mapa el área del país distorsiona
  (EE.UU. dominaría la imagen aunque tiene la peor proporción) y no se ordena. Barras ordenadas: la longitud es el
  canal más preciso.
- **¿Por qué las trayectorias van de 0 a 100% si se ven planas?** Porque usamos la misma escala en todas las
  pantallas, que es una regla de diseño del tablero: así no se exageran diferencias pequeñas y nadie compara escalas
  distintas por error. La cifra exacta está escrita en el título de cada tarjeta y los años sobre la meta van en verde.
- **¿Por qué no hay treemap ni áreas, si el caso los pedía?** Estaban en EP4 y los reemplazamos por barras:
  comparar áreas es menos preciso que comparar longitudes (Knaflic recomienda barras para datos categóricos). Es una
  decisión justificada en el informe (sección 7), no una omisión.
- **¿Por qué los filtros están en un botón y no a la izquierda?** La lectura empieza arriba a la izquierda (patrón
  en "Z"); ese lugar es para la conclusión. Los filtros son secundarios y el botón muestra cuántos hay activos.
- **¿Por qué tablas para las series sin votos y las películas a destacar?** La tarea de Marketing es elegir
  títulos: necesita nombres y valores exactos. Una dispersión sirve para explorar la relación, no para elegir.
- **¿Por qué la escala logarítmica en la dispersión?** La popularidad es muy asimétrica (pocos títulos virales);
  en escala lineal el 95% de los puntos queda aplastado contra el eje. Está solo en la vista técnica (Data &
  Analytics) y rotulada "escala log".
- **¿Por qué barras horizontales para K3 por género?** 16 géneros con nombres largos y una proporción contra una
  meta: barras ordenadas de 0 a 100%, con la meta marcada y ✓ en verde para las que la superan.
- **¿Por qué columnas por tramo de nota en Rentabilidad?** La nota agrupada en 5 tramos ordenados es una variable
  ordinal; las columnas muestran que la recuperación sube de izquierda a derecha. Una dispersión ROI-nota tiene una
  cola larga ilegible para el Directorio.
- **¿Por qué color solo en lo importante?** Para dirigir la atención: azul = película, naranjo = serie,
  verde/ámbar/rojo = estado del KPI; todo lo demás en gris. Cambiamos el rojo de Streamlit por un primario neutro
  porque competía con el rojo de "no cumple".

### IE31 · Fortalezas con ejemplos verificables (14%)

*Para el 100%: cada fortaleza con algo que se pueda mostrar en el dashboard.*

1. **KPIs accionables:** la tarjeta K1 muestra 25,8% frente a 30%, faltan 4,2 pp, responsable Contenidos, y en la
   lista de decisiones qué hacer.
2. **Foco y diseño por audiencia:** 3 KPIs, uno por decisión; 4 perfiles: Contenidos ve K1 y K2, Marketing ve K3
   y el Directorio los tres.
3. **Títulos que dicen la conclusión y se recalculan:** con el filtro Japón, el título del gráfico de mercados
   pasa a "Japón 51% (puesto 1 de 16)".
4. **Honestidad ante pocos datos:** K2 muestra "sin datos suficientes" con el motivo; los rankings piden un mínimo
   de títulos y el dashboard avisa en vez de mostrar un ranking engañoso.
5. **Reglas contra sesgos:** 10+ votos, comparación dentro de formato, finanzas válidas; la rentabilidad se
   muestra como evidencia con su cobertura escrita, no como KPI.
6. **Accesibilidad:** contraste AA, ícono + texto en los estados, formato escrito en las barras del top 10, líneas
   punteadas y cuadrados para series.
7. **Reproducible:** la limpieza y los KPIs están en `dashboard/streamview/`, y `dashboard/tests/test_kpis.py` aprueba 5 de 5
   pruebas.

### IE32 · Limitaciones, sesgos y riesgos, con consecuencias y mitigación (17%)

*Para el 100%: causa → consecuencia → mitigación, sin confundir causa con efecto.*

| Causa | Consecuencia | Mitigación |
|---|---|---|
| No hay datos de reproducciones ni suscripciones | No se mide retención; K3 es una aproximación de engagement (votos en TMDB) | Rotulado en el tablero; KPI de retención como mejora M5 |
| Solo se califica con 10+ votos (sesgo de selección) | K1 describe las películas calificadas; en series solo el 38% tiene nota | Base n en cada tarjeta; K3 mide justamente esa cobertura |
| Correlación no es causalidad | Comprar más cine japonés podría no subir K1: lo que se exporta ya es una selección (sesgo de supervivencia) | 3 métodos de robustez; piloto medido por cohorte de adquisición |
| Solo 21,7% de las películas tiene finanzas válidas | La evidencia de rentabilidad describe sobre todo a grandes estudios; solo 179 películas de los mercados de K2 | No es KPI; aviso de cobertura en cada tarjeta; se pide completar los datos (R3) |
| La popularidad es un índice del momento de la extracción | Las listas de Marketing pueden variar entre extracciones; favorece lo reciente | Mediana; referencia fija por formato |
| Catálogo curado (1.000 + 1.000 por año) | No mide crecimiento ni "incorporaciones por año" | Trayectorias por cohorte de estreno, rotuladas |
| Metas definidas por el equipo | Podrían no reflejar la estrategia real | Basadas en línea base y cohortes; validarlas con los responsables (M1) |
| Umbral de alerta uniforme (15%) | K2 varía más que K1 entre años (19% → 10%); posibles falsas alarmas | Regla única y explicable; mejora M6 |
| Coproducciones suman en cada país | Las participaciones por país suman más de 100% | Rotulado en los gráficos |

### IE33 · Oportunidades de mejora priorizadas (20%)

*Para el 100%: priorizar por impacto y esfuerzo y conectar cada mejora con una brecha.*

- **Hacer ahora** (impacto alto, esfuerzo bajo): M1 validar metas con los responsables (todo depende de que las
  acepten); M2 exportar la lista de series con público sin votos a CSV; M7 prueba de usabilidad con 5 usuarios por perfil, midiendo el tiempo
  para responder cada pregunta.
- **Planificar** (impacto alto, esfuerzo alto): M5 KPIs de retención reales (brecha: no hay datos de consumo); M8
  fecha real de incorporación (brecha: no se miden adquisiciones); M4 despliegue corporativo con acceso por perfil.
- **Mejoras rápidas** (impacto medio, esfuerzo bajo): M6 umbral según la volatilidad de cada KPI; M9 borde en las
  barras grises (1,69:1) y revisión automática de accesibilidad.
- **Evaluar después:** M3 alertas por correo cuando un KPI cambia de estado.
- **Si preguntan "¿cuál harían primero?":** M1, porque es barata y todas las decisiones se apoyan en las metas.

### IE35 · Recomendaciones vinculadas a hallazgos, KPIs y decisiones (17%)

*Para el 100%: hallazgo → KPI → decisión concreta → responsable.*

- **R1** (H1 mercados + H2 géneros → K1, K2 → Contenidos y Adquisición): cuota de licencias para Japón, Corea del
  Sur y México hasta llegar al 18%; priorizar Animación, Documental y Música; no renovar películas bajo 5,0.
- **R2** (H3 participación → K3 → Producto y Marketing): pedir calificación al terminar un episodio y destacar las
  series con público sin votos, partiendo por Conversación, Reality y Documental.
- **R3** (H4 rentabilidad → K1 y K2 como criterio → Gerencia General y Data & Analytics): exigir nota y mercado del
  segmento antes de aprobar presupuestos altos; pedir presupuesto e ingresos en cada renovación.

### IE36 · Impacto esperado: valor, para quién, en qué decisión y cómo verificarlo (20%)

*Para el 100%: las cuatro partes en cada respuesta.*

- **R1:** *Para quién:* Contenidos y Adquisición. *Decisión:* qué licencias comprar y renovar. *Valor:* si K2
  llega a 18% con las tasas actuales (48,6% de bien evaluadas en esos mercados frente a 22,8% en el resto), K1
  sube ~1,2 pp; los ~3 pp restantes (≈600 películas bien evaluadas) deben venir de la mezcla de géneros.
  *Verificación:* piloto donde se compara la calidad de las compras nuevas contra la línea base, con K1 y K2 por
  trimestre.
- **R2:** *Para quién:* Producto y Marketing. *Decisión:* diseño del flujo de calificación y qué series destacar.
  *Valor:* cerrar los 11,6 puntos de K3 son ~1.850 series más con votos suficientes para decidir renovaciones; las
  4.501 series con público sin votos son el primer objetivo. *Verificación:* K3 trimestral y proporción de series de
  la lista que pasan a 10+ votos.
- **R3:** *Para quién:* Gerencia General y Data & Analytics. *Decisión:* aprobar inversiones. *Valor:* como las
  bien evaluadas recuperan su presupuesto 77% frente a 58%, usar K1 y K2 como criterio reduce las películas que no
  se pagan. *Verificación:* tasa de recuperación de las compras nuevas por cohorte y cobertura financiera trimestral.
- **Regla general:** si un KPI no se mueve en dos trimestres, se revisa la decisión que lo sostiene.

## 5. Preguntas difíciles: cómo responderlas

- **"¿Por qué ningún KPI cumple? ¿El tablero está mal?"** Porque las metas son a diciembre de 2026, no describen
  el estado actual. Un KPI que ya cumple no orienta decisiones. Lo que valida las metas es que cohortes del mismo
  catálogo ya las alcanzaron.
- **"¿Cuál es la diferencia entre una métrica y un KPI?"** La métrica describe ("25,8% bien evaluadas"). El KPI es
  una métrica ligada a un objetivo de negocio, con meta, plazo, responsable y decisión ("25,8% frente a 30% a
  diciembre de 2026, en riesgo: Contenidos prioriza estos géneros y mercados"). Por eso "total de títulos" quedó
  como métrica de contexto.
- **"¿De dónde sacaron las metas?"** Son supuestos del caso: StreamView no entrega metas. Las fijamos con dos
  condiciones: mejor que la línea base y ya alcanzada por alguna cohorte de estreno (K1 y K2) o muy cerca (K3,
  49,7% en 2024). La
  justificación está en la ficha técnica del dashboard.
- **"¿Por qué 15% para 'en riesgo'?"** Es una regla única, simple y explicable para los tres. Reconocemos que KPIs
  más volátiles, como K2, podrían necesitar otro umbral (mejora M6).
- **"¿Por qué solo tres KPIs?"** Uno por cada decisión central: qué cine adquirir (K1), de qué mercados (K2) y si
  el público participa (K3). Probamos con seis, pero la rentabilidad solo se mide en el 21,7% de las películas y la
  visibilidad no correspondía a una decisión central: más indicadores dispersaban la atención. La rentabilidad
  quedó como evidencia de K1 y K2 (pestaña Rentabilidad) y la cobertura financiera como métrica de calidad de datos.
- **"¿Por qué la rentabilidad no es un KPI?"** Porque solo 21,7% de las películas tiene datos financieros
  confiables, sobre todo grandes estudios: una meta sobre esa base no representa al catálogo. Sirve como evidencia:
  la calidad rinde (77% frente a 58%) y los mercados de K2 no rinden menos (70% frente a 66%).
- **"¿K3 mide retención?"** No. Mide participación en TMDB; es el mejor indicador de
  engagement disponible. La retención necesita datos de la plataforma (M5).
- **"¿Por qué K2 dice 'sin datos' con el filtro de país?"** K2 mide la mezcla de países del catálogo. Si se
  filtra Japón, K2 sería 100% por definición, un valor engañoso, así que el dashboard lo explica en vez de
  mostrarlo.
- **"¿Por qué los rankings no mezclan películas y series?"** Las series tienen el triple de popularidad típica y
  mejor calificación. Mezclarlas premia a los países o géneros con más series (paradoja de Simpson): en EP1,
  "Filipinas triplica a EE.UU." era un efecto de composición.
- **"¿Cómo saben que el dashboard muestra los mismos números que el informe?"** Ambos usan el mismo módulo
  (`dashboard/streamview/`), y `dashboard/tests/test_kpis.py` verifica que la línea base de cada KPI coincide con los datos.
- **"¿Qué cambiaron respecto de EP4?"** 43 cambios (`entregables/evidencias/registro_cambios.md`); los principales: 3 KPIs con
  meta, perfil de Contenidos, línea de meta en los rankings, trayectorias, listas accionables para Marketing, accesibilidad, el rediseño con Storytelling with Data y la revisión con las Human Interface Guidelines de Apple.
- **"¿Qué tomaron de las guías de Apple?"** Lo aplicable a un dashboard: modo claro u oscuro según el sistema
  (Dark Mode, sin un ajuste propio), controles segmentados para elegir vista y orden (Segmented controls), un
  resumen en texto de cada gráfico para lectores de pantalla y el uso de patrones y ✓ además del color (Charts,
  Color), textos sin "nosotros" y estados vacíos que dicen qué hacer (Writing), y respeto por "reducir movimiento" y
  "aumentar contraste" (Accessibility). Apple también respalda el eje fijo de 0 a 100% cuando los límites tienen
  sentido, como la carga de una batería.
- **"¿Por qué el modo oscuro no tiene un botón propio?"** Porque Apple recomienda no ofrecer un ajuste de apariencia
  dentro de la app: el tablero sigue la preferencia que la persona ya eligió en su sistema.
- **"Si muestran algo distinto a EP5…"** La versión que se presenta es la misma de EP5. Si se hiciera un ajuste
  posterior, la pauta exige identificarlo y justificarlo explícitamente.
