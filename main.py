import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psutil
import time
import threading
from cryptography.fernet import Fernet
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

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
        Ahora con actualización verdaderamente continua.
        """
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.set_title("CPU Use - Real time")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("CPU (%)")
        line, = ax.plot([], [], lw=2, color='#1f77b4')
        
        # Agregamos un texto que muestre el valor actual de CPU
        cpu_text = ax.text(0.018, 0.8, '', transform=ax.transAxes, fontsize=6)
        
        def init():
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 100)
            line.set_data([], [])
            return line, cpu_text
                
        def update(frame):
            # Si no hay suficientes datos, no hacemos nada
            if len(self.time_points) < 2:
                return line, cpu_text
            
            # Convertir tiempos absolutos a tiempo relativo
            start_time = self.time_points[0]
            times = [t - start_time for t in self.time_points]
            
            # Actualizar los datos de la línea
            line.set_data(times, self.cpu_usage)
            
            # Ajustar el eje X dinámicamente para mostrar una ventana deslizante
            current_max = max(times)
            visible_range = 20  # Ventana de 20 segundos
            
            # Esto creará un efecto de desplazamiento continuo del eje X
            ax.set_xlim(current_max - visible_range, current_max)
            
            # Actualizar el texto con el valor actual de CPU y el tiempo transcurrido
            if self.cpu_usage:
                cpu_text.set_text(f'CPU: {self.cpu_usage[-1]:.1f}% | Tiempo: {current_max:.1f}s')
            
            return line, cpu_text
    
        # Crear una función para seguir agregando datos incluso después de que termine el procesamiento
        def continuous_monitoring():
            while plt.fignum_exists(fig.number):  # Mientras la figura siga abierta
                usage = self.monitor_resources()
                self.cpu_usage.append(usage['cpu'])
                self.time_points.append(time.time())
                time.sleep(0.1)  # Actualizar cada 100ms para mayor fluidez
        
        # Iniciar el monitoreo continuo en un hilo separado
        monitoring_thread = threading.Thread(target=continuous_monitoring)
        monitoring_thread.daemon = True  # Terminar cuando cierre la ventana
        monitoring_thread.start()
        
        # Configurar la animación con intervalo más corto
        ani = FuncAnimation(
            fig, 
            update, 
            init_func=init, 
            interval=100,  # Actualizar cada 100ms para mayor fluidez
            blit=True,
            save_count=1000,  # Mayor cantidad de frames en caché
            cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()


def main():
    # Inicializamos el procesador de datos
    dp = DataProcessor("ruta_al_archivo.csv")
    
    # Ejecutamos el procesamiento de datos en un hilo separado
    processing_thread = threading.Thread(target=dp.process_data)
    processing_thread.daemon = True  # Terminar si se cierra la ventana principal
    processing_thread.start()
    
    # Iniciamos el gráfico en tiempo real (ahora con monitoreo continuo incorporado)
    dp.realtime_plot()
    
    # Si llegamos aquí, es porque el usuario cerró la ventana del gráfico
    print("Gráfico cerrado. Finalizando programa.")

if __name__ == "__main__":
    main()