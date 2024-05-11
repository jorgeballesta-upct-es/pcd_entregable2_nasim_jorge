from __future__ import annotations
from abc import ABC, abstractmethod
import random
from typing import List
import time, asyncio
from generar_datos_no_asincrona import generador_sensor_datos
from abc import ABC, abstractmethod
from typing import Any, Optional
from functools import reduce
import asyncio
# Estructura Observer
class Sujeto(ABC):
    """
    La interfaz Sujeto declara un conjunto de métodos para gestionar los observadores.
    """

    @abstractmethod
    def adjuntar(self, observador: Observador) -> None:
        """
        Adjunta un observador al sujeto.
        """
        pass

    @abstractmethod
    def desadjuntar(self, observador: Observador) -> None:
        """
        Desadjunta un observador del sujeto.
        """
        pass

    @abstractmethod
    def notificar(self) -> None:
        """
        Notifica a todos los observadores sobre un evento.
        """
        pass


"""
    Realmente el único observador es el sistema que gestiona que los datos, y el único sujeto es el invernadero.
    En el invernadero podría tratarse los observadores de forma más compleja, como por ejemplo, tratandolos según
    una sección específica del invernadero y demás.
"""


class Observador(ABC):
    """
    La interfaz Observador declara el método actualizar, utilizado por los sujetos.
    """

    @abstractmethod
    def actualizar(self, estado) -> str:
        """
        Recibe una actualización del sujeto.
        """
        pass


"""
Los Observadores Concretos reaccionan a las actualizaciones emitidas por el Sujeto al que habían sido
adjuntados. En este caso solo tenemos un observador concreto, que es el sistema, el cual quiere ser notificado
cada vez que cambie el estado del invernadero. Podrían existir más observadores, cada uno con sus propios
deseos de cuando quieren ser notificados.
"""

##implementación del sujeto (Invernadero) con estructura observer.
class Invernadero(Sujeto):
    """
    El Sujeto posee un estado importante (temperatura) y notifica a los observadores cuando cambia.
    """

    _estado = None          #(timestamp, t)

    """
    Por simplicidad, el estado del Sujeto, esencial para todos los
    suscriptores, se almacena en esta variable.
    """

    _observadores: List[Observador] = []

    """
    Lista de suscriptores. En la vida real, la lista de suscriptores puede ser almacenada
    de forma más comprensible (categorizada por tipo de evento, etc.).
    """

    def adjuntar(self, observador: Observador) -> None:
        print("Invernadero: Se adjuntó un observador.")
        self._observadores.append(observador)

    def desadjuntar(self, observador: Observador) -> None:
        self._observadores.remove(observador)

    """
    Los métodos de gestión de suscripción.
    """

    def notificar(self, estado) -> None:
        """
        Activa una actualización en cada suscriptor.
        """

        print("Invernadero: Notificando a los observadores...")
        for observador in self._observadores:
            observador.actualizar(estado)
    
    """
        Realmente, una clase Invernadero como tal, debería tener su propia lógica de negocios.
        Es decir, que tenga un desarrollo en el que se complete todas sus funcionalidades, como podría
        ser almacenar el stock, gestionar los empleados...
    """

    def modificar_estado(self, estado):
        print("\nInvernadero: Acabo de cambiar de estado.")
        self._estado = estado
        self.notificar(estado)

    def iniciar_sensor(self, duracion):
        print("\nInvernadero: Comienzo a tomar datos del sensor")
        fin = time.time() + duracion
        while fin > time.time():
            dato = generador_sensor_datos()
            self.modificar_estado(dato)
            time.sleep(5)


##implementación del sistema gestor con estructura singleton. Además es un observador concreto del invernadero
class Gestion_datos(Observador):
    _instancia_unica = None

    def __init__(self):
        self.nombre = "Gestor 1"
        self._datos = []
        self._datos_60 = []
        self._datos_30 = []
        self._estrategia = None
        self._manejador = None

    @classmethod
    def obtener_instancia(cls):
        if not cls._instancia_unica:
            cls._instancia_unica = cls()
        return cls._instancia_unica

    @property
    def manejador(self) -> Manejador:
        return self._manejador

    @manejador.setter          #importante pasar una cadena de manejadores al gestor antes de inicializar el sensor.
    def manejador(self, manejador: Manejador) -> None:
        self._manejador = manejador

    def actualizar(self, estado) -> str:
        self._datos.append(estado[1])
        self._datos_60.append(estado[1])
        self._datos_30.append(estado[1])
        if len(self._datos_60) > 6: # 30 seg
            self._datos_30 = self._datos_60[-6:]
        if len(self._datos_60) > 12: # 60 seg
            self._datos_60 = self._datos_60[-12:]
        print(f"{self.nombre}: He recibido la notificación del estado actual del invernadero: {estado}")
        print(f"{self.nombre}: Ordenando pasos encadenados")
        print(f"datos totales: {self._datos}")
        print(f"datos últimos 30 segundos: {self._datos_30}")
        print(f"datos últimos 60 segundos: {self._datos_60}")
        self._manejador.manejar(self._datos_60, self._datos_30)



###implementación de manejadores que utilizará el sistema gestor de datos con cada notificación del invernadero
class Manejador(ABC):
    """
    La interfaz Manejador declara un método para construir la cadena de
    manejadores. También declara un método para ejecutar una solicitud.
    """

    @abstractmethod
    def establecer_siguiente(self, manejador: Manejador) -> Manejador:
        pass

    @abstractmethod
    def manejar(self, solicitud) -> Optional[str]:
        pass


class ManejadorAbstracto(Manejador):
    """
    El comportamiento de encadenamiento predeterminado se puede implementar
    dentro de una clase de manejador base.
    """

    _siguiente_manejador: Manejador = None

    def establecer_siguiente(self, manejador: Manejador) -> Manejador:
        self._siguiente_manejador = manejador
        return manejador

    @abstractmethod
    def manejar(self, datos_60: list, datos_30 : list) -> str:
        if self._siguiente_manejador:
            return self._siguiente_manejador.manejar(datos_60, datos_30)
        return None


"""
Todos los manejadores concretos manejan una solicitud o la pasan al siguiente
manejador en la cadena.
"""

class Umbral(ManejadorAbstracto):
    def manejar(self, datos_60: list, datos_30 : list) -> str:      #fijamos el Umbral por defecto en 10
        umbral = 10
        resultado = datos_60[-1] > umbral
        if resultado:
            resultado = "Si"
        else:
            resultado = "No"
        print(f"La temperatura {datos_60[-1]} excede del umbral {umbral}: {resultado}")
        return super().manejar(datos_60, datos_30)


class Cambio_drastico(ManejadorAbstracto):
    def cambio_drastico(self, l, umbral):
        diff = max(l) - min(l)
        return diff > umbral
    
    def manejar(self, datos_60: List, datos_30 : list) -> str:
        resultado = self.cambio_drastico(datos_30, 10)
        if resultado:
            resultado = "Si"
        else:
            resultado = "No"
        print(f"Comprobamos si durante los últimos 30 segs la temperatura ha aumentado en más de 10º: {resultado}")
        return super().manejar(datos_60, datos_30)
    
# Estructura Strategy

#Para el cómputo de los estadísticos, se utilizará la estructura strategy
class Estrategia(ABC):
    """
    La interfaz de Estrategia declara operaciones comunes a todas las versiones admitidas
    de algún algoritmo.

    El Contexto utiliza esta interfaz para llamar al algoritmo definido por las
    Estrategias Concretas.
    """

    @abstractmethod
    def realizar_algoritmo(self, datos: list):
        pass


"""
Las Estrategias Concretas implementan el algoritmo siguiendo la interfaz base de Estrategia
. La interfaz las hace intercambiables en el Contexto.
"""


class Media(Estrategia):
    def realizar_algoritmo(self, l: List) -> List:
        suma = reduce(lambda x, y : x + y, l)
        return round(suma / len(l), 2)


class Mediana(Estrategia):
    def realizar_algoritmo(self, l: List) -> List:
        lista_ordenada = sorted(l)
        if len(lista_ordenada) % 2 != 0: #con elementos impares devuelvo el elemento central de la lista ordenada
            result = lista_ordenada[len(lista_ordenada) // 2]
        else: #con elementos pares devuelvo la media de los dos elementos centrales.
            result1= lista_ordenada[len(lista_ordenada) // 2]
            result2 = lista_ordenada[len(lista_ordenada) // 2 - 1]
            lista_medianas = [result1] + [result2]
            result = Media().realizar_algoritmo(lista_medianas)
        return result
    
class Desviacion_tipica(Estrategia):
    def __aux_sd(self, l):      #función auxiliar que utilizará el algoritmo
        valor_medio = Media().realizar_algoritmo(l)
        def f(n):
            return (n - valor_medio)**2
        return f
    
    def realizar_algoritmo(self, l: List):
        elementos_cuadrado =  list(map(self.__aux_sd(l), l))
        result = Media().realizar_algoritmo(elementos_cuadrado) ** (1 / 2)
        return round(result, 2)

class Estadisticos(ManejadorAbstracto):     #importante pasar una estrategia a este manejador. Se le puede pasar al constructor o cambiarlo en el tiempo de ejecución
    def __init__(self, estrategia : Estrategia) -> None:
        """
        Por lo general, el Estadistico acepta una estrategia a través del constructor, pero
        también proporciona un setter para cambiarla en tiempo de ejecución.
        """
        self._estrategia = estrategia

    @property
    def estrategia(self) -> Estrategia:
        """
        El sistema mantiene una referencia a uno de los objetos de Estrategia. El
        sistema no conoce la clase concreta de una estrategia. Debería funcionar
        con todas las estrategias a través de la interfaz de Estrategia.
        """
        return self._estrategia

    @estrategia.setter          #importante pasar una estrategia al gestor antes de inicializar el sensor.
    def estrategia(self, estrategia: Estrategia) -> None:
        """
        Por lo general, el sistema permite reemplazar un objeto de Estrategia en tiempo de ejecución.
        """
        self._estrategia = estrategia 

    def manejar(self, datos_60: list, datos_30 : list) -> str:
        print(f"Estadistico de la temperatura según la estrategia establecida: {type(self._estrategia).__name__}")
        resultado = self._estrategia.realizar_algoritmo(datos_60)
        if isinstance(self._estrategia, Media):
            print(f"Cálculo de la media: {resultado}")
        elif isinstance(self._estrategia, Mediana):
            print(f"Cálculo de la mediana: {resultado}")
        else: ##ojo, controlar si realmente viene de desviación tipica. Controlar posibles errores...
            print(f"Cálculo de la desviación típica: {resultado}")
        return super().manejar(datos_60, datos_30)


if __name__=="__main__":
    invernadero = Invernadero()
    gestor = Gestion_datos.obtener_instancia()
    invernadero.adjuntar(gestor)


    ##estrategias
    estrategia_media = Media()
    estrategia_mediana = Mediana()
    estrategia_desviacion_tipica = Desviacion_tipica()

    estadisticos = Estadisticos(estrategia_media)
    umbral = Umbral()
    cambio_drastico = Cambio_drastico()
    estadisticos.establecer_siguiente(umbral).establecer_siguiente(cambio_drastico)

    #La cadena sigue el orden de estadisticos > umbral > cambio_drastico
    gestor.manejador = estadisticos

    # Iniciar el sensor de datos
    (invernadero.iniciar_sensor(20))        #Especificar tiempo de ejecucion del sensor