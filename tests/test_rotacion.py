"""Pruebas del plan de rotación. Ejecutar con: python -m unittest -v"""

import unittest

from rotacion_hospitalaria import CoordinacionDeResidentes, PlanDeRotacion, PlanVacioError

SERVICIOS = [("Urgencias", 4), ("Pediatría", 6), ("Cirugía", 8), ("Ginecología", 6)]


def nombres(elementos):
    return [e.nombre for e in elementos]


class PruebaPlan(unittest.TestCase):
    def setUp(self):
        self.plan = PlanDeRotacion()

    def cargar_servicios(self):
        for nombre, semanas in SERVICIOS:
            self.plan.agregar_al_final(nombre, semanas)

    def assertEnlacesCirculares(self):
        """Invariante: todos los enlaces son recíprocos y el ciclo se cierra."""
        if self.plan.esta_vacio():
            self.assertEqual(len(self.plan), 0)
            return
        adelante = list(self.plan.recorrer_hacia_adelante())
        self.assertEqual(len(adelante), len(self.plan))
        for servicio in adelante:
            self.assertIs(servicio.proximo_servicio.servicio_previo, servicio)
            self.assertIs(servicio.servicio_previo.proximo_servicio, servicio)
        atras = list(self.plan.recorrer_hacia_atras())
        self.assertEqual(atras[1:], adelante[1:][::-1])


class TestInsercion(PruebaPlan):
    def test_plan_nuevo_esta_vacio(self):
        self.assertTrue(self.plan.esta_vacio())
        self.assertEqual(list(self.plan.recorrer_hacia_adelante()), [])

    def test_un_solo_servicio_se_enlaza_consigo_mismo(self):
        urgencias = self.plan.agregar_al_final("Urgencias", 4)
        self.assertIs(urgencias.proximo_servicio, urgencias)
        self.assertIs(urgencias.servicio_previo, urgencias)
        self.assertEnlacesCirculares()

    def test_agregar_al_final_respeta_el_orden(self):
        self.cargar_servicios()
        self.assertEqual(nombres(self.plan.recorrer_hacia_adelante()),
                         ["Urgencias", "Pediatría", "Cirugía", "Ginecología"])
        self.assertEqual(self.plan.servicio_de_ingreso.servicio_previo.nombre, "Ginecología")
        self.assertEnlacesCirculares()

    def test_agregar_como_ingreso(self):
        self.cargar_servicios()
        self.plan.agregar_como_ingreso("Medicina Interna", 8)
        self.assertEqual(self.plan.servicio_de_ingreso.nombre, "Medicina Interna")
        self.assertEqual(nombres(self.plan.recorrer_hacia_adelante())[:2],
                         ["Medicina Interna", "Urgencias"])
        self.assertEnlacesCirculares()

    def test_agregar_despues_de_otro(self):
        self.cargar_servicios()
        nuevo = self.plan.agregar_despues_de("pediatría", "Psiquiatría", 4)
        self.assertEqual(nuevo.servicio_previo.nombre, "Pediatría")
        self.assertEqual(nuevo.proximo_servicio.nombre, "Cirugía")
        self.assertEnlacesCirculares()

    def test_validaciones(self):
        self.cargar_servicios()
        with self.assertRaises(ValueError):
            self.plan.agregar_al_final("urgencias", 4)
        with self.assertRaises(ValueError):
            self.plan.agregar_al_final("  ", 4)
        with self.assertRaises(ValueError):
            self.plan.agregar_al_final("Oftalmología", 0)
        with self.assertRaises(ValueError):
            self.plan.agregar_despues_de("Inexistente", "Oftalmología", 2)
        self.assertEqual(len(self.plan), 4)

    def test_semanas_del_ciclo(self):
        self.cargar_servicios()
        self.assertEqual(self.plan.semanas_del_ciclo(), 24)


class TestRemocion(PruebaPlan):
    def test_retirar_servicio_del_medio(self):
        self.cargar_servicios()
        retirado = self.plan.retirar_servicio("Pediatría")
        self.assertIsNone(retirado.proximo_servicio)
        self.assertEqual(nombres(self.plan.recorrer_hacia_adelante()),
                         ["Urgencias", "Cirugía", "Ginecología"])
        self.assertEnlacesCirculares()

    def test_retirar_ingreso_mueve_la_entrada(self):
        self.cargar_servicios()
        self.plan.retirar_servicio("Urgencias")
        self.assertEqual(self.plan.servicio_de_ingreso.nombre, "Pediatría")
        self.assertEnlacesCirculares()

    def test_retirar_el_ultimo_deja_el_plan_vacio(self):
        self.plan.agregar_al_final("Urgencias", 4)
        self.plan.retirar_servicio("Urgencias")
        self.assertTrue(self.plan.esta_vacio())

    def test_retirar_en_plan_vacio(self):
        with self.assertRaises(PlanVacioError):
            self.plan.retirar_servicio("Urgencias")


class TestResidentes(unittest.TestCase):
    def setUp(self):
        self.coordinacion = CoordinacionDeResidentes()
        for nombre, semanas in SERVICIOS:
            self.coordinacion.plan.agregar_al_final(nombre, semanas)

    def test_registrar_en_ingreso_o_en_servicio_elegido(self):
        laura = self.coordinacion.registrar_residente("Laura")
        mateo = self.coordinacion.registrar_residente("Mateo", "cirugía")
        self.assertEqual(laura.servicio_actual.nombre, "Urgencias")
        self.assertEqual(mateo.servicio_actual.nombre, "Cirugía")

    def test_no_registrar_sin_servicios_ni_repetidos(self):
        with self.assertRaises(PlanVacioError):
            CoordinacionDeResidentes().registrar_residente("Laura")
        self.coordinacion.registrar_residente("Laura")
        with self.assertRaises(ValueError):
            self.coordinacion.registrar_residente("laura")

    def test_rotacion_es_circular_y_cuenta_ciclos(self):
        laura = self.coordinacion.registrar_residente("Laura")
        recorrido = [self.coordinacion.rotar_residente("Laura").servicio_actual.nombre
                     for _ in range(5)]
        self.assertEqual(recorrido, ["Pediatría", "Cirugía", "Ginecología", "Urgencias", "Pediatría"])
        self.assertEqual(laura.ciclos_completados, 1)

    def test_devolver_usa_el_servicio_previo(self):
        laura = self.coordinacion.registrar_residente("Laura")
        self.coordinacion.devolver_residente("Laura")
        self.assertEqual(laura.servicio_actual.nombre, "Ginecología")

    def test_devolver_deshace_un_ciclo_completado(self):
        laura = self.coordinacion.registrar_residente("Laura")
        for _ in range(4):
            laura.rotar()
        self.assertEqual(laura.ciclos_completados, 1)
        laura.devolver()
        self.assertEqual(laura.ciclos_completados, 0)

    def test_rotar_a_todos(self):
        self.coordinacion.registrar_residente("Laura")
        self.coordinacion.registrar_residente("Mateo", "Ginecología")
        self.coordinacion.rotar_a_todos()
        ubicacion = {r.nombre: r.servicio_actual.nombre for r in self.coordinacion.residentes}
        self.assertEqual(ubicacion, {"Laura": "Pediatría", "Mateo": "Urgencias"})

    def test_cerrar_servicio_reubica_residentes(self):
        mateo = self.coordinacion.registrar_residente("Mateo", "Cirugía")
        _, reubicados = self.coordinacion.retirar_servicio("Cirugía")
        self.assertEqual(nombres(reubicados), ["Mateo"])
        self.assertEqual(mateo.servicio_actual.nombre, "Ginecología")
        self.assertEqual(mateo.servicio_de_inicio.nombre, "Ginecología")

    def test_no_cerrar_unico_servicio_con_residentes(self):
        coordinacion = CoordinacionDeResidentes()
        coordinacion.plan.agregar_al_final("Urgencias", 4)
        coordinacion.registrar_residente("Laura")
        with self.assertRaises(ValueError):
            coordinacion.retirar_servicio("Urgencias")

    def test_residentes_por_servicio(self):
        self.coordinacion.registrar_residente("Laura", "Pediatría")
        self.coordinacion.registrar_residente("Mateo", "Pediatría")
        pediatria = self.coordinacion.plan.obtener_servicio("Pediatría")
        self.assertEqual(nombres(self.coordinacion.residentes_en(pediatria)), ["Laura", "Mateo"])

    def test_retirar_residente(self):
        self.coordinacion.registrar_residente("Laura")
        self.coordinacion.retirar_residente("Laura")
        self.assertEqual(self.coordinacion.residentes, [])
        with self.assertRaises(ValueError):
            self.coordinacion.rotar_residente("Laura")


class TestPlanDeEjemplo(unittest.TestCase):
    def test_cargar_plan_de_ejemplo_reemplaza_el_contenido(self):
        from rotacion_hospitalaria.datos_ejemplo import (
            RESIDENTES_DE_EJEMPLO, SERVICIOS_DE_EJEMPLO, cargar_plan_de_ejemplo)

        coordinacion = CoordinacionDeResidentes()
        coordinacion.plan.agregar_al_final("Dermatología", 2)
        coordinacion.registrar_residente("Previo")
        cargar_plan_de_ejemplo(coordinacion)

        self.assertEqual(nombres(coordinacion.plan.recorrer_hacia_adelante()),
                         [nombre for nombre, _ in SERVICIOS_DE_EJEMPLO])
        self.assertEqual(len(coordinacion.residentes), len(RESIDENTES_DE_EJEMPLO))


if __name__ == "__main__":
    unittest.main()
