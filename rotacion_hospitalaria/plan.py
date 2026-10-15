"""PlanDeRotacion: lista circular doblemente enlazada de servicios hospitalarios.

     ┌──────────────────────────────────────────────────────────────┐
     ▼                                                              │
  [Urgencias] ⇄ [Medicina Interna] ⇄ [Pediatría] ⇄ [Cirugía] ───────┘
     ▲                                            (Cirugía rota de nuevo a
     └── servicio_de_ingreso                       Urgencias, y Urgencias
                                                   tiene como previo a Cirugía)

- Cada servicio apunta a su próximo servicio y a su servicio previo.
- Ningún enlace queda en None: al terminar el último servicio el ciclo
  vuelve a empezar.
- La referencia de entrada es el servicio por el que ingresan los residentes.
"""

from __future__ import annotations

from collections.abc import Iterator

from .servicio import ServicioHospitalario


class PlanVacioError(ValueError):
    """Se intentó una operación que necesita servicios en un plan vacío."""


class PlanDeRotacion:
    """Ciclo de servicios por los que rotan los residentes."""

    def __init__(self) -> None:
        self.servicio_de_ingreso: ServicioHospitalario | None = None
        self.cantidad_servicios: int = 0

    # ------------------------------------------------------------------ consultas
    def esta_vacio(self) -> bool:
        return self.servicio_de_ingreso is None

    def __len__(self) -> int:
        return self.cantidad_servicios

    def buscar_servicio(self, nombre: str) -> ServicioHospitalario | None:
        """Busca un servicio por nombre, sin distinguir mayúsculas. O(n)."""
        nombre_buscado = nombre.strip().lower()
        for servicio in self.recorrer_hacia_adelante():
            if servicio.nombre.lower() == nombre_buscado:
                return servicio
        return None

    def obtener_servicio(self, nombre: str) -> ServicioHospitalario:
        """Como buscar_servicio, pero falla si el servicio no existe."""
        self._exigir_servicios()
        servicio = self.buscar_servicio(nombre)
        if servicio is None:
            raise ValueError(f"El servicio '{nombre.strip()}' no está en el plan de rotación.")
        return servicio

    def semanas_del_ciclo(self) -> int:
        """Semanas que tarda un residente en completar una vuelta al plan."""
        return sum(servicio.semanas for servicio in self.recorrer_hacia_adelante())

    # ----------------------------------------------------------------- recorridos
    def recorrer_hacia_adelante(
        self, desde: ServicioHospitalario | None = None
    ) -> Iterator[ServicioHospitalario]:
        """Una vuelta completa siguiendo el orden de rotación."""
        yield from self._dar_vuelta(desde, hacia_adelante=True)

    def recorrer_hacia_atras(
        self, desde: ServicioHospitalario | None = None
    ) -> Iterator[ServicioHospitalario]:
        """Una vuelta completa en sentido contrario al de la rotación."""
        yield from self._dar_vuelta(desde, hacia_adelante=False)

    def _dar_vuelta(
        self, desde: ServicioHospitalario | None, hacia_adelante: bool
    ) -> Iterator[ServicioHospitalario]:
        # Como la lista es circular, la vuelta termina al regresar al servicio
        # de partida. Sin este control el recorrido sería infinito.
        if self.servicio_de_ingreso is None:
            return
        partida = desde if desde is not None else self.servicio_de_ingreso
        actual = partida
        while True:
            yield actual
            actual = actual.proximo_servicio if hacia_adelante else actual.servicio_previo
            if actual is partida:
                break

    # ----------------------------------------------------------------- inserción
    def agregar_al_final(self, nombre: str, semanas: int) -> ServicioHospitalario:
        """Agrega un servicio como el último del ciclo (antes de volver al ingreso)."""
        nuevo = self._crear_servicio(nombre, semanas)
        if self.servicio_de_ingreso is None:
            self._agregar_primer_servicio(nuevo)
        else:
            ultimo = self.servicio_de_ingreso.servicio_previo
            self._enlazar_entre(nuevo, ultimo, self.servicio_de_ingreso)
        return nuevo

    def agregar_como_ingreso(self, nombre: str, semanas: int) -> ServicioHospitalario:
        """Agrega un servicio y lo vuelve la puerta de entrada al plan."""
        nuevo = self.agregar_al_final(nombre, semanas)
        # En una lista circular el "inicio" es solo la referencia de entrada.
        # El servicio quedó justo antes del ingreso anterior, así que basta
        # con mover la referencia.
        self.servicio_de_ingreso = nuevo
        return nuevo

    def agregar_despues_de(
        self, nombre_servicio: str, nombre: str, semanas: int
    ) -> ServicioHospitalario:
        """Agrega un servicio inmediatamente después de otro que ya está en el plan."""
        anterior_en_plan = self.obtener_servicio(nombre_servicio)
        nuevo = self._crear_servicio(nombre, semanas)
        self._enlazar_entre(nuevo, anterior_en_plan, anterior_en_plan.proximo_servicio)
        return nuevo

    # ------------------------------------------------------------------ remoción
    def retirar_servicio(self, nombre: str) -> ServicioHospitalario:
        """Saca un servicio del plan reconectando a sus dos vecinos.

        Si era el servicio de ingreso, el ingreso pasa al próximo servicio.
        """
        servicio = self.obtener_servicio(nombre)

        if self.cantidad_servicios == 1:
            self.servicio_de_ingreso = None
        else:
            previo, proximo = servicio.servicio_previo, servicio.proximo_servicio
            previo.proximo_servicio = proximo
            proximo.servicio_previo = previo
            if servicio is self.servicio_de_ingreso:
                self.servicio_de_ingreso = proximo

        servicio.proximo_servicio = servicio.servicio_previo = None
        self.cantidad_servicios -= 1
        return servicio

    # ---------------------------------------------------------------- auxiliares
    def _crear_servicio(self, nombre: str, semanas: int) -> ServicioHospitalario:
        nuevo = ServicioHospitalario(nombre, semanas)
        if self.buscar_servicio(nuevo.nombre) is not None:
            raise ValueError(f"El servicio '{nuevo.nombre}' ya está en el plan de rotación.")
        return nuevo

    def _agregar_primer_servicio(self, servicio: ServicioHospitalario) -> None:
        # Con un solo servicio, sus dos enlaces apuntan a sí mismo:
        # eso es lo que mantiene la lista circular.
        servicio.proximo_servicio = servicio
        servicio.servicio_previo = servicio
        self.servicio_de_ingreso = servicio
        self.cantidad_servicios = 1

    def _enlazar_entre(
        self,
        nuevo: ServicioHospitalario,
        previo: ServicioHospitalario,
        proximo: ServicioHospitalario,
    ) -> None:
        nuevo.servicio_previo = previo
        nuevo.proximo_servicio = proximo
        previo.proximo_servicio = nuevo
        proximo.servicio_previo = nuevo
        self.cantidad_servicios += 1

    def _exigir_servicios(self) -> None:
        if self.esta_vacio():
            raise PlanVacioError("El plan de rotación está vacío. Primero agrega un servicio.")
