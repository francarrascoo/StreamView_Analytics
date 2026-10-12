# StreamView Analytics — EV2

Solución de Visual Analytics para el catálogo audiovisual de StreamView Analytics. Proyecto de la
asignatura ADY1104 (Visualización de Datos), Etapa 3 (evaluación crítica y rediseño) y presentación
ejecutiva con defensa técnica.

## Equipo

- Felipe Ahumada Silva
- Francisca Carrasco Lozano

## Contexto

StreamView Analytics es una plataforma de streaming digital que necesita transformar el volumen de
datos de su catálogo en conocimiento accionable para distintas áreas de la organización (Directorio,
Marketing, Data & Analytics, entre otras). Este proyecto analiza dos datasets del catálogo (películas
y series), identifica hallazgos relevantes y los comunica mediante un notebook de análisis
exploratorio, un dashboard interactivo con una vista por público, una infografía, un informe
ejecutivo y una presentación.

En esta etapa revisamos la solución de la Etapa 1, volvimos a calcular cada cifra publicada y
rediseñamos la comunicación según la audiencia. La revisión corrigió cuatro hallazgos que no
resistieron (entre ellos el central de la Etapa 1, "la popularidad no depende de la calificación"),
porque los títulos sin votos se promediaban como nota 0 y algunas comparaciones mezclaban películas
con series.

El hallazgo central del proyecto es ahora que **StreamView debería priorizar películas de Japón,
Corea del Sur y México**: el 49% de las películas del catálogo son de EE.UU., pero esos tres mercados,
que aportan solo el 13%, tienen la mayor proporción de películas bien evaluadas (5 de cada 10 en
Japón, frente a 2 de cada 10 en EE.UU.). La ventaja se mantiene con tres métodos distintos
(comparación directa, mismo género y año, y promedio bayesiano con controles) y se limita a
películas, porque en series no hay una diferencia consistente. La evidencia se desarrolla en la
Sección 4.11 del notebook, la infografía, el informe ejecutivo y la presentación.

## Estructura del proyecto

```text
EV2/
├── data/           dos CSV originales sin modificar (Netflix Movies / TV Shows Detailed up to 2025)
├── notebooks/      analisis_exploratorio.ipynb, el análisis exploratorio revisado en la Etapa 3 (17 visualizaciones)
├── images/         los 17 PNG que genera el notebook al ejecutarse
├── dashboard/      app.py, el dashboard interactivo por perfil (Streamlit + Plotly), y requirements.txt
├── entregables/    infografía, informe ejecutivo y presentación de la Etapa 3, y entregables de la Etapa 1
└── docs/           documentación del caso semestral
```

## Datos

- `netflix_movies_detailed_up_to_2025.csv`, 16.000 películas, 18 columnas.
- `netflix_tv_shows_detailed_up_to_2025.csv`, 16.000 filas antes de depuración (15.991 series únicas
  tras eliminar 9 duplicados por `show_id`), 16 columnas.

Ambos comparten variables como título, país, idioma, año de estreno, géneros, popularidad, cantidad
de votos y calificación promedio, y se integran en una sola tabla de 31.991 títulos con una columna
que indica si cada uno es película o serie. Para que la unión sea consistente se separan las
categorías combinadas de series (`Action & Adventure` pasa a `Action` y `Adventure`), `War & Politics`
se funde en `War`, `Unknown` se trata como dato faltante y los dos códigos del chino mandarín se
unifican (82 idiomas en total). `budget` y `revenue` solo existen en el dataset de películas.

Tres reglas de calidad cambian los resultados y se aplican en todo el proyecto:

1. **Calificación solo con 10 o más votos.** 4.560 títulos (14%) no tienen votos y su calificación
   viene en 0, que no es una nota real. Cubre al 89% de las películas y al 38% de las series.
2. **Comparar países, idiomas y géneros dentro de un mismo formato.** Las series tienen el triple de
   popularidad típica que las películas (36,2 frente a 10,9); mezclarlas premia a los segmentos con
   más series (paradoja de Simpson).
3. **Finanzas solo con montos de al menos US$10.000 y retorno de hasta 50 veces.** Hay presupuestos
   de US$1 o US$5. Quedan 3.468 películas (21,7%) con datos confiables y ninguna serie.

Además, la popularidad se resume con la mediana (tiene valores extremos), las categorías necesitan al
menos 200 títulos para entrar a un ranking, y 2025 queda fuera de las tendencias porque menos del 10%
de sus títulos tiene votos suficientes. El detalle de la auditoría de calidad de datos está en la
Sección 2 del notebook.

## Cómo ejecutar

### Notebook de análisis exploratorio

Es el análisis de la Etapa 1 revisado en la Etapa 3: auditoría de calidad de datos (Sección 2), KPIs
(Sección 3), 17 visualizaciones con títulos corregidos (Sección 4) y un resumen final con los
hallazgos verificados y las correcciones respecto de la Etapa 1 (Sección 5). Requiere `pandas` y
`matplotlib`.

```bash
cd notebooks
jupyter notebook analisis_exploratorio.ipynb
```

Para regenerar todas las salidas y los 17 PNG de `images/` desde cero:

```bash
python3 -m nbconvert --to notebook --execute --inplace analisis_exploratorio.ipynb
```

### Dashboard interactivo

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Queda disponible en `http://localhost:8501`. Requiere `streamlit>=1.51`, `pandas>=2.0` y
`plotly>=5.20`.

Carga los CSV directo desde `data/` y aplica la misma limpieza de datos que el notebook, de modo que
los dos productos entregan las mismas cifras. Un selector de perfil cambia las pestañas, los
gráficos, los KPIs y el nivel de detalle según el público:

| Perfil | Tipo de vista | Pestañas |
| --- | --- | --- |
| Directorio | Explicativa: la respuesta en una pantalla | Resumen, Catálogo, Finanzas |
| Marketing | Explicativa con exploración guiada | Oportunidades, Títulos destacados, Catálogo |
| Data & Analytics | Exploratoria: cobertura, tamaño de muestra y vistas técnicas (dispersión, treemap, áreas) | Catálogo, Popularidad y calidad, Finanzas |

Cada vista abre con la pregunta que responde, y cada gráfico lleva un título que dice la conclusión,
recalculado con los datos filtrados. El mensaje va en color y el contexto en gris; azul identifica a
las películas y naranjo a las series en todo el proyecto.

Los filtros por tipo, rango de años, país, idioma y género recalculan todos los KPIs, gráficos y
títulos, y un botón los reinicia. El filtro de país destaca en vez de recortar: los rankings por país
siguen comparando contra todos los países y muestran en qué puesto quedó cada uno de los
seleccionados. El mínimo de títulos por categoría baja en proporción a los filtros sin quedar bajo
30, y el dashboard avisa cuando una combinación no tiene datos suficientes en vez de mostrar un
ranking engañoso.

## Entregables

- `entregables/Infografia_Mercados_StreamView.pdf`, la infografía de una página sobre el hallazgo de
  mercados, pensada para el Directorio y la Gerencia de Contenidos y Adquisición: el ranking de
  películas bien evaluadas por país, la evidencia de robustez y tres recomendaciones.
- `entregables/Informe_Ejecutivo_EP3_StreamView_Analytics.pdf`, el informe ejecutivo de la Etapa 3,
  cubre problema de negocio, objetivos, audiencia, fuentes de datos e integración, análisis
  exploratorio, justificación de representaciones gráficas, storytelling, diseño del dashboard, KPIs
  de engagement, experiencia y retención, evaluación crítica con comparación antes y después,
  conclusiones y recomendaciones, más anexos de reproducibilidad y de robustez del hallazgo de
  mercados.
- `entregables/Presentacion_EP4_StreamView_Analytics.pptx`, la presentación ejecutiva y defensa
  técnica, con notas de orador: problema, datos, hallazgo, robustez, recomendaciones, navegación del
  dashboard, herramientas, antes y después, limitaciones y anexos de respaldo.
- `entregables/Informe_Ejecutivo_EV1_StreamView_Analytics.pdf` y
  `entregables/Presentacion_EV1_StreamView_Analytics.pptx`, el informe y la presentación de la
  Etapa 1, que se conservan como referencia para la comparación antes y después.
