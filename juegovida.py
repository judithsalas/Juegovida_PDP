import multiprocessing
import numpy as np
import pandas as pd
import time
import os

# --- Configuración del Juego de la Vida ---
FILAS = 50
COLUMNAS = 50
GENERACIONES = 100
PROCESOS = 4
ARCHIVO_ESTADO = "estado.npy"
ARCHIVO_ESTADISTICAS = "estadisticas.csv"

# --- Inicialización de la matriz ---
def inicializar_matriz():
    print("\n== JUEGO DE LA VIDA - OPCIONES INICIALES ==")
    print("1 - Estado aleatorio")
    print("2 - Cargar estado desde archivo")
    print("3 - Configurar manualmente")
    opcion = input("\nSelecciona una opción: ")

    if opcion == '1':  # Aleatorio
        return np.random.choice([0, 1], size=(FILAS, COLUMNAS))
    elif opcion == '2':  # Cargar desde archivo
        if os.path.exists(ARCHIVO_ESTADO):
            return np.load(ARCHIVO_ESTADO)
        else:
            print(f"\n⚠ No se encontró '{ARCHIVO_ESTADO}', generando aleatoria.")
            return np.random.choice([0, 1], size=(FILAS, COLUMNAS))
    elif opcion == '3':  # Manual
        matriz = np.zeros((FILAS, COLUMNAS), dtype=np.int8)
        print("\nIntroduce coordenadas (fila,col) de células vivas, 'fin' para terminar:")
        while True:
            entrada = input("Coordenada: ")
            if entrada.lower() == 'fin':
                break
            try:
                f, c = map(int, entrada.strip().split(','))
                if 0 <= f < FILAS and 0 <= c < COLUMNAS:
                    matriz[f][c] = 1
            except:
                print("⚠ Formato inválido. Usa: fila,col")
        return matriz
    else:
        print("\n⚠ Opción inválida. Generando aleatoria.")
        return np.random.choice([0, 1], size=(FILAS, COLUMNAS))

# --- Contar vecinos vivos ---
def contar_vecinos(matriz, fila, col):
    vecinos = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1),          (0, 1),
               (1, -1), (1, 0), (1, 1)]
    conteo = 0
    for dx, dy in vecinos:
        nf, nc = (fila + dx) % FILAS, (col + dy) % COLUMNAS
        conteo += matriz[nf][nc]
    return conteo

# --- Proceso por bloque ---
def actualizar_bloque(inicio_fila, fin_fila, matriz_compartida, nueva_matriz_compartida, barrera, queue):
    matriz = np.frombuffer(matriz_compartida.get_obj(), dtype=np.int8).reshape((FILAS, COLUMNAS))
    nueva_matriz = np.frombuffer(nueva_matriz_compartida.get_obj(), dtype=np.int8).reshape((FILAS, COLUMNAS))

    for _ in range(GENERACIONES):
        celulas_vivas_bloque = 0
        for i in range(inicio_fila, fin_fila):
            for j in range(COLUMNAS):
                vecinos = contar_vecinos(matriz, i, j)
                if matriz[i][j] == 1 and (vecinos < 2 or vecinos > 3):
                    nueva_matriz[i][j] = 0
                elif matriz[i][j] == 0 and vecinos == 3:
                    nueva_matriz[i][j] = 1
                else:
                    nueva_matriz[i][j] = matriz[i][j]
                celulas_vivas_bloque += nueva_matriz[i][j]

        # Enviar el conteo por la cola
        queue.put(celulas_vivas_bloque)

        barrera.wait()

        if inicio_fila == 0:
            matriz[:, :] = nueva_matriz[:, :]

        barrera.wait()

# --- Mostrar la matriz ---
def imprimir_matriz(matriz):
    os.system('cls' if os.name == 'nt' else 'clear')
    for fila in matriz:
        print(''.join(['█' if celula else ' ' for celula in fila]))
    print("\n" + "="*COLUMNAS)

# --- Main ---
if __name__ == '__main__':
    multiprocessing.freeze_support()
    matriz_inicial = inicializar_matriz()

    matriz_compartida = multiprocessing.Array('b', FILAS * COLUMNAS)
    nueva_matriz_compartida = multiprocessing.Array('b', FILAS * COLUMNAS)
    matriz_np = np.frombuffer(matriz_compartida.get_obj(), dtype=np.int8).reshape((FILAS, COLUMNAS))
    matriz_np[:, :] = matriz_inicial[:, :]

    barrera = multiprocessing.Barrier(PROCESOS)
    queue = multiprocessing.Queue()

    procesos = []
    filas_por_proceso = FILAS // PROCESOS

    for i in range(PROCESOS):
        inicio_fila = i * filas_por_proceso
        fin_fila = (i + 1) * filas_por_proceso if i != PROCESOS - 1 else FILAS
        p = multiprocessing.Process(target=actualizar_bloque,
                                    args=(inicio_fila, fin_fila, matriz_compartida, nueva_matriz_compartida, barrera, queue))
        procesos.append(p)
        p.start()

    celulas_vivas_historial = []
    tiempos_generacion = []
    inicio_total = time.time()

    for _ in range(GENERACIONES):
        inicio_gen = time.time()
        imprimir_matriz(matriz_np)

        total_vivas = 0
        for _ in range(PROCESOS):
            total_vivas += queue.get()

        celulas_vivas_historial.append(total_vivas)
        fin_gen = time.time()
        tiempos_generacion.append(fin_gen - inicio_gen)
        time.sleep(0.1)

    for p in procesos:
        p.join()

    # Guardar estadísticas
    df = pd.DataFrame({
        'Generacion': list(range(1, GENERACIONES + 1)),
        'Celulas_vivas': celulas_vivas_historial,
        'Tiempo_generacion': tiempos_generacion
    })
    df.to_csv(ARCHIVO_ESTADISTICAS, index=False)

    # Guardar estado final
    np.save(ARCHIVO_ESTADO, matriz_np)

    tiempo_total = time.time() - inicio_total
    print(f"\n⏱ Tiempo total: {tiempo_total:.2f} segundos")
    print(f" Estado final guardado en '{ARCHIVO_ESTADO}'")
    print(f" Estadísticas guardadas en '{ARCHIVO_ESTADISTICAS}'")
