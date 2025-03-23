# Juego de la Vida de Conway - Versión Paralela

Este proyecto es una implementación paralela del **Juego de la Vida de Conway** usando Python y el módulo `multiprocessing`. Ha sido desarrollado con mejoras funcionales y de rendimiento que lo diferencian de versiones básicas, incluyendo estadísticas, guardado/carga de estados y personalización del entorno.

## Características Destacadas

### Ejecución Paralela
- La matriz se divide en bloques y cada proceso actualiza una parte.
- Sincronización entre procesos usando barreras.
- Aceleración en matrices grandes (por defecto 50x50, escalable a 500x500).

### Estadísticas de Simulación
- Cuenta células vivas por generación.
- Mide tiempo de ejecución por generación.
- Exporta los datos a un archivo `estadisticas.csv` para análisis.

### Guardar y Cargar Estado
- Guarda el estado final de la simulación como `estado.npy`.
- Permite cargar el estado guardado para continuar la simulación o comparar resultados.

### Personalización del Entorno Inicial
Al iniciar el programa, puedes elegir:
1. Estado aleatorio.
2. Cargar estado desde archivo (`estado.npy`).
3. Configuración manual introduciendo coordenadas de células vivas.

## Requisitos
- Python 3.8+
- Módulos: `numpy`, `pandas`

Instalación:
```bash
pip install numpy pandas
```

## Ejecución
```bash
python juego_vida.py
```

### Flujo General:
1. Selecciona opción de entorno inicial.
2. Visualiza la evolución de la matriz (consola).
3. Al finalizar:
   - Se guarda `estado.npy` (estado final).
   - Se guarda `estadisticas.csv` (datos de simulación).

## Archivos Generados
- `estado.npy`: Matriz del estado final.
- `estadisticas.csv`: Datos por generación (células vivas, tiempo).

## Ideas Futuras
- Visualización gráfica con `pygame` o `matplotlib`.
- Exportar estados intermedios.
- Carga/guardado con nombres personalizados.
- Multi-mundos conectados o con ruido aleatorio.


