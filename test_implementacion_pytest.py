from Implementacion_no_asincrona import *
from statistics import mean, median, pstdev
from generar_datos_no_asincrona import generador_sensor_datos
import pytest
import asyncio

# Comprobacion instancia unica Singleton
def test_singleton():
    instancia1=Gestion_datos.obtener_instancia()
    instancia2=Gestion_datos.obtener_instancia()
    assert instancia1 is instancia2


# Suscripcion al observable
def test_suscribirse_desuscribirse():
    invernadero = Invernadero()
    gestor = Gestion_datos.obtener_instancia()
    invernadero.adjuntar(gestor)
    assert gestor in invernadero._observadores

    invernadero.desadjuntar(gestor)
    assert gestor not in Invernadero._observadores


# Estadisticos

def test_media():
    data = [[1, 4, 7], [1, 6,5, 2], [3, 45,23, 1]]
    media = Media()
    for d in data:
        assert mean(d) == media.realizar_algoritmo(d)

def test_mediana():
    mediana = Mediana()
    data = [[1, 4, 7], [1, 6,5, 2], [3, 45,23, 1]]
    for d in data:
        assert median(d) == mediana.realizar_algoritmo(d)

def test_desviacion_tipica():
    sd = Desviacion_tipica()
    data = [[1, 4, 7], [1, 6,5, 2], [3, 45,23, 1]]
    for d in data:
        print(pstdev(d), sd.realizar_algoritmo(d))
        assert pstdev(d) == sd.realizar_algoritmo(d)

#comprobar la generacion de datos 
def test_iniciar_sensor():
    invernadero = Invernadero()
    gestor = Gestion_datos.obtener_instancia()
    invernadero.adjuntar(gestor)

    ##estrategia
    estrategia_media = Media()
    estadisticos = Estadisticos(estrategia_media)
    umbral = Umbral()
    cambio_drastico = Cambio_drastico()
    estadisticos.establecer_siguiente(umbral).establecer_siguiente(cambio_drastico)

    #La cadena sigue el orden de estadisticos > umbral > cambio_drastico
    gestor.manejador = estadisticos
    invernadero.iniciar_sensor(21)
    assert len(gestor._datos) == 5
    
# comprobacion de COR
def test_cadena_responsabilidad():
    estrategia_media = Media()

    estadisticos = Estadisticos(estrategia_media)
    umbral = Umbral()
    cambio_drastico = Cambio_drastico()
    estadisticos.establecer_siguiente(umbral)
    assert estadisticos._siguiente_manejador == umbral
    umbral.establecer_siguiente(cambio_drastico)
    assert umbral._siguiente_manejador == cambio_drastico
    assert cambio_drastico._siguiente_manejador == None
