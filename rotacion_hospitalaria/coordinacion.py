"""CoordinacionDeResidentes: une el plan de rotación con los residentes."""

from __future__ import annotations

from .plan import PlanDeRotacion, PlanVacioError
from .residente import Residente
from .servicio import ServicioHospitalario


class CoordinacionDeResidentes:
    """Gestiona el plan de rotación y la ubicación de cada residente."""

    def __init__(self, plan: PlanDeRotacion | None = None) -> None:
        self.plan = plan if plan is not None else PlanDeRotacion()
        self._residentes: dict[str, Residente] = {}

    # ----------------------------------------------------------------- residentes
    @property
    def residentes(self) -> list[Residente]:
        return list(self._residentes.values())

    def registrar_residente(self, nombre: str, servicio_inicial: str | None = None) -> Residente:
        """Registra un residente en el servicio indicado o en el de ingreso."""
        if self.plan.esta_vacio():
            raise PlanVacioError("Agrega al menos un servicio antes de registrar residentes.")
        clave = nombre.strip().lower()
        if clave in self._residentes:
            raise ValueError(f"El residente '{nombre.strip()}' ya está registrado.")

        if servicio_inicial:
            servicio = self.plan.obtener_servicio(servicio_inicial)
        else:
            servicio = self.plan.servicio_de_ingreso
        residente = Residente(nombre, servicio)
        self._residentes[clave] = residente
        return residente

    def obtener_residente(self, nombre: str) -> Residente:
        residente = self._residentes.get(nombre.strip().lower())
        if residente is None:
            raise ValueError(f"No hay ningún residente registrado como '{nombre.strip()}'.")
        return residente

    def retirar_residente(self, nombre: str) -> Residente:
        residente = self.obtener_residente(nombre)
        del self._residentes[residente.nombre.lower()]
        return residente

    def rotar_residente(self, nombre: str) -> Residente:
        residente = self.obtener_residente(nombre)
        residente.rotar()
        return residente

    def devolver_residente(self, nombre: str) -> Residente:
        residente = self.obtener_residente(nombre)
        residente.devolver()
        return residente

    def rotar_a_todos(self) -> int:
        """Fin de periodo: todos los residentes pasan a su próximo servicio."""
        for residente in self._residentes.values():
            residente.rotar()
        return len(self._residentes)

    def residentes_en(self, servicio: ServicioHospitalario) -> list[Residente]:
        return [r for r in self._residentes.values() if r.servicio_actual is servicio]

    # ------------------------------------------------------------------ servicios
    def retirar_servicio(self, nombre: str) -> tuple[ServicioHospitalario, list[Residente]]:
        """Cierra un servicio y reubica a sus residentes en el próximo servicio.

        Devuelve (servicio_retirado, residentes_reubicados).
        """
        servicio = self.plan.obtener_servicio(nombre)
        afectados = self.residentes_en(servicio)
        if len(self.plan) == 1 and self._residentes:
            raise ValueError(
                "No se puede cerrar el único servicio del plan mientras haya residentes registrados."
            )

        destino = servicio.proximo_servicio  # se guarda antes de desenlazarlo
        self.plan.retirar_servicio(servicio.nombre)
        for residente in self._residentes.values():
            if residente.servicio_actual is servicio:
                residente.servicio_actual = destino
            if residente.servicio_de_inicio is servicio:
                residente.servicio_de_inicio = destino
        return servicio, afectados
