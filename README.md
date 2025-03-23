# Juego de la Vida de Conway - Versión Paralela con Cola de Mensajes

Este proyecto es una versión mejorada y paralelizada del **Juego de la Vida de Conway**, programado en Python. Incorpora varios conceptos de **Programación Paralela y Distribuida (PPD)**, incluyendo **memoria compartida**, **sincronización mediante colas de mensajes**, y **análisis de rendimiento**. Permite guardar y cargar estados de la simulación, así como generar estadísticas detalladas.

## Características Principales

### Ejecución Paralela
- Usa `multiprocessing.Process` para ejecutar 4 procesos en paralelo.
- Cada proceso gestiona una porción de la matriz (división por filas).

### Sincronización por Cola de Mensajes
- Cada proceso cuenta las **células vivas en su bloque** y envía el dato al proceso principal mediante una **`multiprocessing.Queue`**.
- El proceso principal **recibe los conteos** y suma el total, generando estadísticas de forma segura y sincronizada.

### Guardar y Cargar Estado
- El estado final de la simulación se guarda como archivo binario `estado.npy`.
- Puedes cargar este estado en futuras simulaciones.

### Estadísticas de Simulación
- Se mide el número total de **células vivas por generación**.
- Se mide el **tiempo de ejecución por generación**.
- Los datos se exportan automáticamente a `estadisticas.csv`.

### Configuración Inicial Personalizada
Al iniciar el programa, puedes elegir:
1. Estado aleatorio.
2. Cargar estado desde archivo (`estado.npy`).
3. Introducir coordenadas de células vivas manualmente.

## Archivos Generados
| Archivo             | Descripción                                          |
|---------------------|------------------------------------------------------|
| `estado.npy`        | Matriz binaria del estado final (formato NumPy)      |
| `estadisticas.csv`  | Células vivas y tiempo por generación (CSV)         |

## Requisitos
- Python 3.8+
- Librerías: `numpy`, `pandas`

Instalación:
```bash
pip install numpy pandas
```

## Ejecución del Programa
```bash
python juego_vida.py
```

### Flujo:
1. Selecciona opción de configuración.
2. Se inicia la simulación en consola.
3. Al finalizar, se generan `estado.npy` y `estadisticas.csv`.

## Conceptos de Programación Paralela Aplicados
- **Decomposición de dominio**: División de la matriz por filas.
- **Memoria compartida**: Matrices compartidas entre procesos.
- **Cola de mensajes**: Sincronización segura y eficiente para enviar datos.
- **Medición de rendimiento**: Tiempo por generación y total.
- **Persistencia de datos**: Guardado de estado para futuras simulaciones.

## Notas Adicionales
- El archivo `estado.npy` no es legible directamente; puede cargarse en Python o convertirse a `.txt` o `.csv` si se desea.
- Puedes modificar el tamaño de la matriz y el número de procesos en las constantes al inicio del código.
