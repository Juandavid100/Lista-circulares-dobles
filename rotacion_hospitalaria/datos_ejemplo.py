"""Plan de rotación de ejemplo para demostraciones y pruebas manuales."""

from __future__ import annotations

from .coordinacion import CoordinacionDeResidentes

SERVICIOS_DE_EJEMPLO = [
    ("Medicina Interna", 8),
    ("Urgencias", 4),
    ("Pediatría", 6),
    ("Ginecología y Obstetricia", 6),
    ("Cirugía General", 8),
    ("Unidad de Cuidado Intensivo", 4),
]

RESIDENTES_DE_EJEMPLO = [
    ("Laura Benavides", "Medicina Interna"),
    ("Mateo Rosero", "Urgencias"),
    ("Valentina Ortega", "Pediatría"),
    ("Santiago Guerrero", "Cirugía General"),
    ("Daniela Muñoz", "Cirugía General"),
    ("Andrés Chamorro", "Unidad de Cuidado Intensivo"),
]


def cargar_plan_de_ejemplo(coordinacion: CoordinacionDeResidentes) -> None:
    """Reemplaza el contenido actual por el plan y los residentes de ejemplo."""
    for residente in coordinacion.residentes:
        coordinacion.retirar_residente(residente.nombre)
    while not coordinacion.plan.esta_vacio():
        coordinacion.plan.retirar_servicio(coordinacion.plan.servicio_de_ingreso.nombre)

    for nombre, semanas in SERVICIOS_DE_EJEMPLO:
        coordinacion.plan.agregar_al_final(nombre, semanas)
    for nombre, servicio in RESIDENTES_DE_EJEMPLO:
        coordinacion.registrar_residente(nombre, servicio)
