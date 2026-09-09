# StreamView Analytics — EV1

Solución de Visual Analytics para el catálogo audiovisual de StreamView Analytics. Proyecto de la
asignatura ADY1104 (Visualización de Datos), Etapa 1.

## Equipo

- Felipe Ahumada Silva
- Francisca Carrasco Lozano

## Contexto

StreamView Analytics es una plataforma de streaming digital que necesita transformar el volumen de
datos de su catálogo en conocimiento accionable para distintas áreas de la organización (Directorio,
Marketing, Data & Analytics, entre otras). Este proyecto analiza dos datasets del catálogo (películas
y series), identifica hallazgos relevantes y los comunica mediante un notebook de análisis
exploratorio, un dashboard interactivo y un informe ejecutivo con su presentación.

El hallazgo central del proyecto es que la popularidad de un título y su calificación de calidad son
señales independientes entre sí, evidencia que se desarrolla en detalle en el informe ejecutivo y en
la presentación.

## Estructura del proyecto

```text
EV1/
├── data/           dos CSV originales sin modificar (Netflix Movies / TV Shows Detailed up to 2025)
├── notebooks/      analisis_exploratorio.ipynb, el análisis exploratorio completo (17 visualizaciones)
├── images/         los 17 PNG que genera el notebook al ejecutarse
├── dashboard/      app.py, el dashboard ejecutivo interactivo (Streamlit)
├── entregables/    informe ejecutivo (PDF) y presentación (PPTX) de la Etapa 1
└── docs/           documentación del caso semestral
```

## Datos

- `netflix_movies_detailed_up_to_2025.csv`, 16.000 películas, 18 columnas.
- `netflix_tv_shows_detailed_up_to_2025.csv`, 16.000 filas antes de depuración (15.991 series únicas
  tras eliminar 9 duplicados por `show_id`), 16 columnas.

Ambos comparten variables como título, país, idioma, año de estreno, géneros, popularidad, cantidad
de votos y calificación promedio. `budget` y `revenue` solo existen en el dataset de películas, y
solo el 22,1% de las películas tiene ambos valores registrados y coherentes entre sí. El detalle
completo de la auditoría de calidad de datos está en la Sección 2 del notebook.

## Cómo ejecutar

### Notebook de análisis exploratorio

Requiere `pandas` y `matplotlib`.

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

Carga los CSV directo desde `data/`, aplica la misma limpieza de datos que el notebook y expone un
selector de perfil (Directorio, Marketing, Data & Analytics) que filtra el contenido según la
necesidad real de cada stakeholder, más filtros por tipo, país, idioma, género y año.

## Entregables

- `entregables/Informe_Ejecutivo_EV1_StreamView_Analytics.pdf`, el informe ejecutivo, cubre problema
  de negocio, objetivos, audiencia, fuentes de datos, análisis exploratorio, justificación de
  representaciones gráficas, storytelling, dashboard, evaluación crítica, conclusiones y
  recomendaciones.
- `entregables/Presentacion_EV1_StreamView_Analytics.pptx`, la presentación ejecutiva para la
  defensa del proyecto, con notas de orador.
