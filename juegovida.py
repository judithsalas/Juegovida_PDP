import multiprocessing
import numpy as np
import pandas as pd
import time
import tkinter as tk
from tkinter import messagebox, filedialog
import os

# --- Configuración ---
FILAS = 20
COLUMNAS = 20
GENERACIONES = 100
PROCESOS = 4
TAM_CELDA = 20
ARCHIVO_ESTADO = "estado.npy"
ARCHIVO_ESTADISTICAS = "estadisticas.csv"

# --- Contar vecinos vivos ---
def contar_vecinos(matriz, fila, col):
    vecinos = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1),          (0, 1),
               (1, -1), (1, 0), (1, 1)]
    return sum(matriz[(fila+dx)%FILAS][(col+dy)%COLUMNAS] for dx, dy in vecinos)

# --- Proceso por bloque ---
def actualizar_bloque(inicio_fila, fin_fila, matriz_compartida, nueva_matriz_compartida, barrera, queue):
    matriz = np.frombuffer(matriz_compartida.get_obj(), dtype=np.int8).reshape((FILAS, COLUMNAS))
    nueva_matriz = np.frombuffer(nueva_matriz_compartida.get_obj(), dtype=np.int8).reshape((FILAS, COLUMNAS))

    while True:
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

        queue.put(celulas_vivas_bloque)
        barrera.wait()

        if inicio_fila == 0:
            matriz[:, :] = nueva_matriz[:, :]

        barrera.wait()

# --- Inicializar patrón en el centro ---
def inicializar_matriz(tipo):
    matriz = np.zeros((FILAS, COLUMNAS), dtype=np.int8)

    patrones = {
        "Planeador": np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]]),
        "Explosionador": np.array([[0, 1, 0], [1, 1, 1], [1, 0, 1], [0, 1, 0]]),
        "Pentaminó R": np.array([[0, 1, 1], [1, 1, 0], [0, 1, 0]]),
        "Nave Ligera (LWSS)": np.array([
            [0, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0]
        ]),
        "Pulsar": np.array([
            [0,0,1,1,1,0,0],
            [0,0,0,0,0,0,0],
            [0,0,1,1,1,0,0]
        ]),
        "Cañón de Glider": np.array([
            [0,0,0,0,1,0,0,0,0],
            [0,0,0,0,0,1,0,0,0],
            [0,0,1,1,0,1,1,0,0],
            [0,0,1,1,0,1,1,0,0],
            [0,0,0,0,1,0,0,0,0]
        ])
    }

    if tipo == "Aleatorio":
        return np.random.choice([0, 1], size=(FILAS, COLUMNAS))

    patron = patrones.get(tipo)
    if patron is not None:
        pf, pc = patron.shape
        inicio_fila = (FILAS - pf) // 2
        inicio_col = (COLUMNAS - pc) // 2
        matriz[inicio_fila:inicio_fila+pf, inicio_col:inicio_col+pc] = patron
        return matriz

    return matriz

# --- GUI del Juego de la Vida ---
class JuegoVidaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego de la Vida")

        self.running = False
        self.pausado = False
        self.generation_index = 0
        self.historial_vivas = []
        self.tiempos_generacion = []

        self.opciones = [
            "Aleatorio", "Planeador", "Explosionador", "Pentaminó R",
            "Nave Ligera (LWSS)", "Pulsar", "Cañón de Glider"
        ]
        self.tipo_simulacion = tk.StringVar(value=self.opciones[0])

        self.menu_opciones = tk.OptionMenu(root, self.tipo_simulacion, *self.opciones)
        self.menu_opciones.pack(pady=5)

        self.btn_iniciar = tk.Button(root, text="▶ Iniciar Simulación", command=self.toggle_simulacion)
        self.btn_iniciar.pack(pady=5)

        self.btn_cargar = tk.Button(root, text="Cargar Patrón desde Archivo", command=self.cargar_patron)
        self.btn_cargar.pack(pady=5)

        self.canvas = tk.Canvas(root, width=COLUMNAS*TAM_CELDA, height=FILAS*TAM_CELDA, bg='white')
        self.canvas.pack(pady=10)

        self.btn_guardar = tk.Button(root, text="Guardar Estado", command=self.guardar_estado)
        self.btn_guardar.pack(side='left', padx=10, pady=10)

        self.btn_salir = tk.Button(root, text="Salir", command=root.destroy)
        self.btn_salir.pack(side='right', padx=10, pady=10)

        self.tipo_simulacion.trace_add("write", lambda *_: self.actualizar_preview())

        self.matriz = inicializar_matriz(self.tipo_simulacion.get())
        self.dibujar_matriz()
        self.actualizar_preview()

    def actualizar_preview(self):
        self.matriz = inicializar_matriz(self.tipo_simulacion.get())
        self.dibujar_matriz()
        self.running = False
        self.pausado = False
        self.generation_index = 0
        self.historial_vivas = []
        self.tiempos_generacion = []
        self.btn_iniciar.config(text="▶ Iniciar Simulación")

    def dibujar_matriz(self):
        self.canvas.delete("all")
        for i in range(FILAS):
            for j in range(COLUMNAS):
                color = '#00CC66' if self.matriz[i][j] == 1 else 'white'
                self.canvas.create_rectangle(
                    j*TAM_CELDA, i*TAM_CELDA,
                    (j+1)*TAM_CELDA, (i+1)*TAM_CELDA,
                    fill=color, outline='gray')

    def toggle_simulacion(self):
        if not self.running:
            self.running = True
            self.pausado = False
            self.btn_iniciar.config(text="⏸ Pausar Simulación")
            self.simular()
        elif not self.pausado:
            self.pausado = True
            self.btn_iniciar.config(text="▶ Reanudar Simulación")
        else:
            self.pausado = False
            self.btn_iniciar.config(text="⏸ Pausar Simulación")
            self.simular()

    def simular(self):
        self.matriz_compartida = multiprocessing.Array('b', FILAS * COLUMNAS)
        self.nueva_matriz_compartida = multiprocessing.Array('b', FILAS * COLUMNAS)
        matriz_np = np.frombuffer(self.matriz_compartida.get_obj(), dtype=np.int8).reshape((FILAS, COLUMNAS))
        matriz_np[:, :] = self.matriz[:, :]

        self.barrera = multiprocessing.Barrier(PROCESOS)
        self.queue = multiprocessing.Queue()

        self.procesos = []
        filas_por_proceso = FILAS // PROCESOS

        for i in range(PROCESOS):
            inicio_fila = i * filas_por_proceso
            fin_fila = (i + 1) * filas_por_proceso if i != PROCESOS - 1 else FILAS
            p = multiprocessing.Process(target=actualizar_bloque,
                                        args=(inicio_fila, fin_fila, self.matriz_compartida,
                                              self.nueva_matriz_compartida, self.barrera, self.queue))
            self.procesos.append(p)
            p.start()

        self.generar()

    def generar(self):
        if self.pausado or not self.running:
            return

        if self.generation_index >= GENERACIONES:
            for p in self.procesos:
                p.terminate()
            self.running = False
            self.btn_iniciar.config(text="▶ Iniciar Simulación")

            df = pd.DataFrame({
                'Generacion': list(range(1, self.generation_index + 1)),
                'Celulas_vivas': self.historial_vivas,
                'Tiempo_generacion': self.tiempos_generacion
            })
            df.to_csv(ARCHIVO_ESTADISTICAS, index=False)

            messagebox.showinfo("Fin", f"Simulación completada.\nCSV guardado en {ARCHIVO_ESTADISTICAS}")
            return

        inicio_gen = time.time()
        total_vivas = sum(self.queue.get() for _ in range(PROCESOS))
        fin_gen = time.time()

        self.historial_vivas.append(total_vivas)
        self.tiempos_generacion.append(fin_gen - inicio_gen)

        self.matriz = np.frombuffer(self.matriz_compartida.get_obj(), dtype=np.int8).reshape((FILAS, COLUMNAS)).copy()
        self.dibujar_matriz()
        self.generation_index += 1
        self.root.after(100, self.generar)

    def guardar_estado(self):
        np.save(ARCHIVO_ESTADO, self.matriz)
        messagebox.showinfo("Guardado", f"Estado guardado en '{ARCHIVO_ESTADO}'")

    def cargar_patron(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de patrón",
            filetypes=[("Archivos .npy", "*.npy"), ("Archivos .csv", "*.csv")]
        )
        if not archivo:
            return

        try:
            if archivo.endswith('.npy'):
                patron = np.load(archivo)
            elif archivo.endswith('.csv'):
                patron = np.loadtxt(archivo, delimiter=',', dtype=np.int8)
            else:
                messagebox.showerror("Error", "Formato de archivo no compatible.")
                return

            if not np.isin(patron, [0, 1]).all():
                messagebox.showerror("Error", "El patrón debe contener solo 0 y 1.")
                return

            pf, pc = patron.shape
            if pf > FILAS or pc > COLUMNAS:
                messagebox.showerror("Error", "El patrón es demasiado grande para el tablero.")
                return

            matriz = np.zeros((FILAS, COLUMNAS), dtype=np.int8)
            inicio_fila = (FILAS - pf) // 2
            inicio_col = (COLUMNAS - pc) // 2
            matriz[inicio_fila:inicio_fila+pf, inicio_col:inicio_col+pc] = patron

            self.matriz = matriz
            self.dibujar_matriz()
            self.running = False
            self.pausado = False
            self.generation_index = 0
            self.historial_vivas = []
            self.tiempos_generacion = []
            self.btn_iniciar.config(text="▶ Iniciar Simulación")
            messagebox.showinfo("Éxito", f"Patrón cargado desde: {os.path.basename(archivo)}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el patrón:\n{e}")

# --- Ejecutar ---
if __name__ == '__main__':
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = JuegoVidaGUI(root)
    root.mainloop()
