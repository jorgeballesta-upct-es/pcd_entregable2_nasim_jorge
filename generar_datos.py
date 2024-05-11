import random, time, asyncio
from datetime import datetime


async def generador_sensor_datos():
    while True:
        # Generar temperatura aleatoria entre 0 y 50 grados Celsius
        temperature = round(random.uniform(0, 50),2)
        
        # Obtener marca de tiempo actual
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #formato de año-mes-dia hora-minuto-segundo
        
        # Imprimir datos del sensor
        yield(timestamp, temperature)
        
        # Esperar 5 segundos antes de enviar el próximo dato
        await   asyncio.sleep(5)

