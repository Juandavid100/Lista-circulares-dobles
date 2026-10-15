"""Plan de rotación de residentes médicos con una lista circular doblemente enlazada."""

from .coordinacion import CoordinacionDeResidentes
from .plan import PlanDeRotacion, PlanVacioError
from .residente import Residente
from .servicio import ServicioHospitalario

__all__ = [
    "CoordinacionDeResidentes",
    "PlanDeRotacion",
    "PlanVacioError",
    "Residente",
    "ServicioHospitalario",
]
