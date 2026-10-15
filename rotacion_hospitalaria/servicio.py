"""ServicioHospitalario: elemento que se guarda en la lista circular doble.

Cada servicio del plan de rotación conoce el servicio al que rotan los
residentes cuando terminan (próximo) y el servicio del que vienen (previo).
"""

from __future__ import annotations


class ServicioHospitalario:
    """Un servicio del hospital por el que rotan los residentes."""

    def __init__(self, nombre: str, semanas: int) -> None:
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            raise ValueError("El nombre del servicio no puede estar vacío.")
        if semanas <= 0:
            raise ValueError("La duración del servicio debe ser de al menos 1 semana.")

        self.nombre: str = nombre_limpio
        self.semanas: int = semanas
        # Enlaces del plan de rotación (punteros de la lista doble).
        self.proximo_servicio: ServicioHospitalario | None = None
        self.servicio_previo: ServicioHospitalario | None = None

    def __repr__(self) -> str:
        return f"ServicioHospitalario(nombre={self.nombre!r}, semanas={self.semanas})"
