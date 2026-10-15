"""Residente: médico que avanza por el plan de rotación."""

from __future__ import annotations

from .servicio import ServicioHospitalario


class Residente:
    """Un residente ubicado en algún servicio del plan de rotación."""

    def __init__(self, nombre: str, servicio_inicial: ServicioHospitalario) -> None:
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            raise ValueError("El nombre del residente no puede estar vacío.")

        self.nombre: str = nombre_limpio
        self.servicio_actual: ServicioHospitalario = servicio_inicial
        self.servicio_de_inicio: ServicioHospitalario = servicio_inicial
        self.ciclos_completados: int = 0

    def rotar(self) -> ServicioHospitalario:
        """Pasa al próximo servicio del plan. O(1).

        Si regresa al servicio donde empezó, completó una vuelta al plan.
        """
        self.servicio_actual = self.servicio_actual.proximo_servicio
        if self.servicio_actual is self.servicio_de_inicio:
            self.ciclos_completados += 1
        return self.servicio_actual

    def devolver(self) -> ServicioHospitalario:
        """Regresa al servicio previo, por ejemplo para repetir una rotación. O(1).

        Gracias al enlace al servicio previo no hace falta recorrer todo el plan.
        """
        if self.servicio_actual is self.servicio_de_inicio and self.ciclos_completados > 0:
            self.ciclos_completados -= 1
        self.servicio_actual = self.servicio_actual.servicio_previo
        return self.servicio_actual

    def __repr__(self) -> str:
        return f"Residente(nombre={self.nombre!r}, servicio={self.servicio_actual.nombre!r})"
