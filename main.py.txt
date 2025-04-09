import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psutil
import time
import threading
from cryptography.fernet import Fernet
from matplotlib.animation import FuncAnimation

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path  # En este ejemplo no se usa para leer un archivo real, sino que simulamos datos.
        self.result = None
        self.cleaned_data = []
        # Generamos una llave de encriptación y creamos una instancia de cifrado.
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        # Listas para almacenar registros de recursos para el gráfico en tiempo real.
        self.cpu_usage = []
        self.time_points = []

    def process_chunk(self, chunk):
        """
        Simula la limpieza y procesamiento de un chunk de datos.
        En este ejemplo:
        - Se eliminan filas con valores NaN en la columna 'value'
        - Se agrega una nueva columna 'processed' elevando al cuadrado el valor.
        """
        cleaned = chunk.dropna(subset=['value'])
        cleaned['processed'] = cleaned['value'] ** 2
        return cleaned

    def process_data(self, chunksize=1000):
        """
        Simula el procesamiento de datos por chunks, como si se leyera un archivo pesado.
        Se generan 10 chunks de datos aleatorios. En cada iteración se:
          - Procesa el chunk.
          - Espera un poco para simular tiempo de procesamiento.
          - Mide y guarda el uso de CPU y memoria.
        """
        print("Iniciando el procesamiento de datos...")
        for i in range(10):  # Simulamos 10 chunks
            # Generamos un chunk de datos aleatorios.
            data = pd.DataFrame({'value': np.random.randn(chunksize)})
            chunk_cleaned = self.process_chunk(data)
            self.cleaned_data.append(chunk_cleaned)
            
            # Simula tiempo de procesamiento
            time.sleep(0.5)
            
            # Monitoreo de recursos
            usage = self.monitor_resources()
            self.cpu_usage.append(usage['cpu'])
            self.time_points.append(time.time())
            print(f"Chunk {i+1} procesado. CPU: {usage['cpu']}%, Memoria: {usage['memory']}%")
        
        # Combina todos los datos procesados.
        self.result = pd.concat(self.cleaned_data, ignore_index=True)
        print("Procesamiento completado.")

    def monitor_resources(self):
        """Obtiene y devuelve el uso de CPU y memoria."""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        return {'cpu': cpu, 'memory': memory}

    def get_encrypted_result(self):
        """
        Convierte el DataFrame resultado a CSV y lo encripta.
        Esto simula proteger la información sensible luego de un procesamiento exitoso.
        """
        csv_data = self.result.to_csv(index=False).encode('utf-8')
        encrypted_data = self.cipher.encrypt(csv_data)
        return encrypted_data

    def realtime_plot(self):
        """
        Genera un gráfico en tiempo real que muestra el uso de CPU.
        Se utiliza FuncAnimation de matplotlib para actualizar el gráfico cada 500 ms.
        """
        plt.style.use('seaborn')
        fig, ax = plt.subplots()
        ax.set_title("Uso de CPU en Tiempo Real")
        ax.set_xlabel("Tiempo (s)")
        ax.set_ylabel("CPU (%)")
        line, = ax.plot([], [], lw=2)

        def init():
            ax.set_xlim(0, 10)  # Límite inicial del eje X, se ajustará dinámicamente.
            ax.set_ylim(0, 100)
            line.set_data([], [])
            return line,

        def update(frame):
            if len(self.time_points) < 2:
                return line,
            # Convertir tiempos absolutos a tiempo relativo (segundos desde el inicio)
            start_time = self.time_points[0]
            times = [t - start_time for t in self.time_points]
            line.set_data(times, self.cpu_usage)
            # Ajustar el eje X para mostrar los últimos 10 segundos.
            ax.set_xlim(max(0, times[-1]-10), times[-1]+1)
            return line,

        ani = FuncAnimation(fig, update, init_func=init, interval=500, blit=True)
        plt.show()

def main():
    # Inicializamos el procesador de datos. 'ruta_al_archivo.csv' es un placeholder en este ejemplo.
    dp = DataProcessor("ruta_al_archivo.csv")
    
    # Ejecutamos el procesamiento de datos en un hilo separado para poder actualizar el gráfico en tiempo real.
    processing_thread = threading.Thread(target=dp.process_data)
    processing_thread.start()
    
    # Iniciamos el gráfico en tiempo real (la ventana se mantiene abierta mientras se actualiza).
    dp.realtime_plot()
    
    # Esperamos a que se complete el procesamiento.
    processing_thread.join()
    
    # Una vez finalizado, obtenemos los datos procesados encriptados.
    encrypted = dp.get_encrypted_result()
    print("\nDatos procesados y encriptados. Llave de cifrado (guárdala de manera segura):")
    print(dp.key.decode())
    # En un entorno real, podrías guardar 'encrypted' en un archivo o enviarlo a un servidor.

if __name__ == "__main__":
    main()