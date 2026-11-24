# StreamView Analytics

Este repositorio reúne la solución de visualización que construimos para StreamView Analytics, una plataforma de
streaming que necesita decidir qué contenido adquirir, qué promover y dónde invertir a partir de su catálogo de
películas y series. Es nuestro proyecto de ADY1104 Visualización de Datos en Duoc UC. Esta versión corresponde a la
EP5, la revisión crítica y optimización de lo que fuimos construyendo durante el semestre, y es la misma que
presentamos en la defensa de la EP6.

Equipo: Felipe Ahumada Silva y Francisca Carrasco Lozano.

## Qué cambió en la EP5

La principal observación que recibimos fue que confundíamos métricas con KPIs. El dashboard mostraba cifras como
"26% bien evaluadas" o "1,9×" sin una meta contra la cual juzgarlas, así que no ayudaban a decidir.

Para corregirlo definimos tres KPIs, cada uno con su meta, plazo, umbral de alerta, responsable y la decisión que
gatilla. Cada uno responde a una de las decisiones centrales del caso: qué cine adquirir (K1), de qué mercados
hacerlo (K2) y cómo medir la participación del público en las series (K3). Todo lo demás en el tablero es evidencia
o contexto de esos tres indicadores.

Ahora el dashboard muestra cada KPI con su estado escrito (cumple, en riesgo o no cumple), un gráfico de bala
contra la meta, su evolución por año y las acciones que propone. También sumamos una vista para la gerencia de
Contenidos y Adquisición, respondimos las preguntas del caso que faltaban sobre directores y actores, agregamos una
vista de participación para Marketing y usamos la rentabilidad como evidencia de que invertir en calidad y en esos
mercados sí rinde. Por último, corregimos el contraste, la tipografía, las unidades y los gráficos que dependían
solo del color.

El informe ejecutivo de la EP5 explica cada cambio con su problema, la mejora y su fundamento.

## Los KPIs

Las metas son a diciembre de 2026 y se miden cada trimestre, con cada nueva extracción del catálogo. StreamView no
nos entregó metas, así que las definimos como supuestos del caso a partir de la línea base y de los años de estreno
que ya las alcanzaron: K1 entre 2019 y 2021, K2 en 2020, y K3 estuvo a punto de lograrlo en 2024 con 49,7%.

La regla de estado es la misma para los tres. Un KPI cumple si alcanza la meta, está en riesgo si queda hasta un 15%
por debajo de ella y no cumple si queda más abajo.

| KPI | Cómo se calcula | Línea base | Meta | Estado | Responsable |
|---|---|---|---|---|---|
| K1 Películas bien evaluadas | Películas con nota 7 o más, sobre las películas con al menos 10 votos | 25,8% | 30% o más | En riesgo | Contenidos y Adquisición |
| K2 Películas de mercados de alto desempeño | Películas de Japón, Corea del Sur o México, sobre las películas con país | 13,5% | 18% o más | No cumple | Contenidos y Adquisición |
| K3 Series que el público califica | Series con al menos 10 votos, sobre el total de series | 38,4% | 50% o más | No cumple | Producto, junto a Marketing |

Las cifras descriptivas, como el total de títulos, países, idiomas o presupuesto, aparecen como métricas de
contexto: no tienen meta, así que no son KPIs. Tampoco lo es la rentabilidad. El 63,6% de las películas recupera su
presupuesto, pero solo el 21,7% tiene datos financieros confiables, así que la usamos como evidencia: las películas
bien evaluadas recuperan su presupuesto el 77% de las veces, frente al 58% de las demás.

## Qué hay en el repositorio

| Carpeta | Contenido |
|---|---|
| dashboard | El dashboard interactivo (app.py, hecho con Streamlit y Plotly), el módulo streamview con la carga de datos y la definición de los KPIs, las pruebas y las dependencias |
| data | Los dos archivos CSV oficiales del caso, sin modificar |
| docs | El caso semestral |
| entregables | Los informes y presentaciones de cada etapa, en las carpetas EP1 y EP2, EP3 y EP4, y EP5 y EP6 |
| images | Los 17 gráficos que genera el notebook |
| notebooks | El análisis exploratorio, con la auditoría de calidad de datos, las métricas, los KPIs y las visualizaciones |

## Los datos

Trabajamos con los dos datasets oficiales del caso. El de películas tiene 16.000 registros y 18 columnas; el de
series tiene 16.000 filas y 16 columnas, con 15.991 series únicas porque 9 vienen duplicadas. Ambos son metadatos de
TMDB (popularidad, votos, nota, presupuesto e ingresos) de títulos estrenados entre 2010 y 2025, y los unimos en una
sola tabla de 31.991 títulos que distingue entre película y serie.

Los datos no incluyen reproducciones, suscripciones ni información de usuarios, así que la retención no se puede
medir. Por eso aproximamos el engagement con la participación del público en TMDB, que es justamente lo que mide K3.

En todo el proyecto aplicamos cuatro reglas de calidad, explicadas en detalle en la sección 2 del notebook:

1. La nota de un título solo cuenta si tiene al menos 10 votos, porque el 14% de los títulos no tiene votos y su
   nota aparece como 0.
2. Países, idiomas y géneros se comparan dentro de un mismo formato. Las series tienen el triple de popularidad
   típica que las películas, y mezclarlas produce una paradoja de Simpson.
3. En las finanzas solo usamos montos desde US$10.000 y retornos de hasta 50 veces, porque hay presupuestos de US$1.
   Así quedan 3.468 películas (21,7%), y por eso la rentabilidad es evidencia y no un KPI.
4. La popularidad se resume con la mediana por sus valores extremos, una categoría necesita al menos 200 títulos
   para entrar a un ranking y 2025 queda fuera de las tendencias, porque menos del 10% de sus títulos tiene votos
   suficientes.

## Cómo ejecutarlo

Necesitas Python 3.9 o superior. Desde la carpeta principal del repositorio, crea un entorno e instala las
dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r dashboard/requirements.txt
```

Para abrir el dashboard:

```bash
streamlit run dashboard/app.py
```

Se abre en el navegador, en localhost:8501. Para funcionar solo necesita Streamlit, pandas y Plotly; el resto de
las dependencias es para el notebook.

Para comprobar que los KPIs están bien calculados:

```bash
python dashboard/tests/test_kpis.py
```

La prueba revisa que el catálogo integrado tenga 31.991 títulos, que cada línea base coincida con los datos, que
las metas y alertas sean coherentes, que los estados se asignen bien y que los filtros recalculen los KPIs.

Para abrir el notebook, o volver a generar todos sus resultados y los 17 gráficos de la carpeta images:

```bash
cd notebooks
jupyter notebook analisis_exploratorio.ipynb
python -m nbconvert --to notebook --execute --inplace analisis_exploratorio.ipynb
```

## Cómo funciona el dashboard

Lo diseñamos siguiendo Storytelling with Data, de Cole Nussbaumer Knaflic, con siete reglas. Todo se entiende de un
vistazo y sin scroll, porque cada pestaña cabe en una pantalla de 1440 por 900. Lo importante va arriba a la
izquierda, y ahí una frase resume la conclusión. Cada pregunta tiene su propia tarjeta con un solo gráfico. Evitamos
la jerga y las cifras de más, usamos barras para comparar magnitudes, nada en 3D, y mantenemos las mismas escalas y
colores en todas las pantallas.

También lo revisamos con las Human Interface Guidelines de Apple. El dashboard sigue el modo claro u oscuro del
sistema, usa su misma fuente, ofrece controles segmentados para elegir la vista y el orden, incluye un resumen en
texto de cada gráfico para lectores de pantalla y nunca distingue algo solo por color: el estado va escrito, la raya
de la meta muestra qué barras la superan y las series van rayadas.

Arriba hay un selector que adapta las pestañas, los KPIs y el nivel de detalle a cada público:

| Vista | Pregunta que responde | Pestañas | KPIs |
|---|---|---|---|
| Directorio (ejecutiva) | ¿Cumplimos las metas y dónde invertir? | Resumen, Avance hacia la meta, Catálogo y Rentabilidad | K1, K2 y K3 |
| Contenidos y Adquisición (analítica) | ¿Qué mercados y géneros adquirir? | Mercados, Géneros, Directores y actores | K1 y K2 |
| Marketing | ¿Cómo aumentar la participación del público y qué destacar? | Participación, Qué promover y Segmentos | K3 |
| Data & Analytics (técnica) | ¿Las cifras son confiables? | KPIs y calidad de datos, Catálogo, Popularidad y nota, Tendencia y Finanzas | K1, K2 y K3, más la ficha técnica |

Cada vista abre con una frase que resume su conclusión y que se recalcula con los filtros. Debajo están las
tarjetas de KPI, con el valor, el estado escrito y en color, la meta, los puntos que faltan y un gráfico de bala
donde la barra es el valor y la raya vertical es la meta. Al pasar el mouse sobre una tarjeta se ven la fórmula y el
responsable. Luego viene una tarjeta por pregunta, con la pregunta en gris, la respuesta como título y un solo
gráfico o tabla. La tarjeta "¿Qué hacer ahora?" muestra, para cada KPI fuera de meta, su responsable y la acción
acordada.

El botón Filtros, arriba a la derecha, permite elegir tipo, rango de años, país, idioma y género. Al aplicarlos se
recalculan la frase principal, los KPIs, los estados, los gráficos, los títulos y las decisiones, y aparece un botón
para quitar los filtros. El filtro de país destaca el país elegido en lugar de recortar los rankings. K2 no se evalúa
con ese filtro, porque mide justamente la mezcla de países, y el dashboard lo explica en pantalla.

Los colores significan lo mismo en todas las pantallas: azul para películas, naranjo rayado para series, verde para
lo que supera la meta, gris para el contexto y un tono oscuro para destacar a EE.UU. El verde, el ámbar y el rojo de
los estados siempre van acompañados de texto. Todo porcentaje va de 0 a 100%, las barras comparan magnitudes, las
líneas se usan solo para mostrar el tiempo y los gráficos de dispersión solo para relaciones, en la vista técnica.

## Entregables

La carpeta entregables está ordenada por etapa del semestre. En EP1 y EP2 están el informe ejecutivo y la
presentación de la primera etapa. En EP3 y EP4 están el informe ejecutivo de la EP3, la infografía de mercados y la
presentación de la EP4. En EP5 y EP6 están el informe ejecutivo final de la EP5 y la presentación para la defensa
de la EP6, en PowerPoint y PDF. Las etapas anteriores se conservan como referencia del antes y el después.
