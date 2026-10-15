"""Interfaz de usuario por consola para manipular el plan de rotación."""

from __future__ import annotations

from .coordinacion import CoordinacionDeResidentes

MENU = """
╔═══════════════════════════════════════════════╗
║      ROTACIÓN DE RESIDENTES — HOSPITAL        ║
║     (lista circular doblemente enlazada)      ║
╠═══════════════════════════════════════════════╣
║  PLAN DE ROTACIÓN                             ║
║   1. Agregar servicio al final del ciclo      ║
║   2. Agregar servicio como ingreso            ║
║   3. Agregar servicio después de otro         ║
║   4. Cerrar servicio                          ║
║   5. Ver plan en ambos sentidos               ║
║  RESIDENTES                                   ║
║   6. Registrar residente                      ║
║   7. Rotar residente al próximo servicio      ║
║   8. Devolver residente al servicio previo    ║
║   9. Fin de periodo: rotar a todos            ║
║  10. Consultar residente                      ║
║  11. Retirar residente                        ║
║  12. Ver residentes por servicio              ║
║   0. Salir                                    ║
╚═══════════════════════════════════════════════╝"""


class InterfazConsola:
    """Menú interactivo que traduce las opciones del usuario en operaciones."""

    def __init__(self, coordinacion: CoordinacionDeResidentes | None = None) -> None:
        self.coordinacion = coordinacion if coordinacion is not None else CoordinacionDeResidentes()
        self.plan = self.coordinacion.plan
        self.acciones = {
            "1": self.agregar_al_final,
            "2": self.agregar_como_ingreso,
            "3": self.agregar_despues_de,
            "4": self.cerrar_servicio,
            "5": self.ver_plan,
            "6": self.registrar_residente,
            "7": self.rotar_residente,
            "8": self.devolver_residente,
            "9": self.rotar_a_todos,
            "10": self.consultar_residente,
            "11": self.retirar_residente,
            "12": self.ver_residentes_por_servicio,
        }

    # ------------------------------------------------------------ ciclo principal
    def iniciar(self) -> None:
        print("\nBienvenido a la coordinación de residentes.")
        print("Arma el plan de rotación con los servicios del hospital y registra a los residentes.")
        while True:
            print(MENU)
            opcion = input("Elige una opción: ").strip()
            if opcion == "0":
                print("Sesión cerrada. ¡Buen turno!")
                return
            accion = self.acciones.get(opcion)
            if accion is None:
                print("  ✗ Opción no válida. Escribe un número del menú.")
                continue
            try:
                accion()
            except ValueError as error:
                print(f"  ✗ {error}")

    # ----------------------------------------------------------- plan de rotación
    def agregar_al_final(self) -> None:
        servicio = self.plan.agregar_al_final(pedir_texto("Nombre del servicio: "),
                                               pedir_entero_positivo("Duración (semanas): "))
        print(f"  ✓ {servicio.nombre} quedó como último servicio del ciclo.")

    def agregar_como_ingreso(self) -> None:
        servicio = self.plan.agregar_como_ingreso(pedir_texto("Nombre del servicio: "),
                                                  pedir_entero_positivo("Duración (semanas): "))
        print(f"  ✓ {servicio.nombre} es ahora el servicio de ingreso.")

    def agregar_despues_de(self) -> None:
        referencia = pedir_texto("¿Después de qué servicio va? ")
        self.plan.obtener_servicio(referencia)  # valida antes de pedir más datos
        servicio = self.plan.agregar_despues_de(referencia, pedir_texto("Nombre del nuevo servicio: "),
                                                pedir_entero_positivo("Duración (semanas): "))
        print(f"  ✓ {servicio.nombre} quedó entre {servicio.servicio_previo.nombre} "
              f"y {servicio.proximo_servicio.nombre}.")

    def cerrar_servicio(self) -> None:
        servicio, reubicados = self.coordinacion.retirar_servicio(pedir_texto("Servicio a cerrar: "))
        print(f"  ✓ {servicio.nombre} salió del plan de rotación.")
        for residente in reubicados:
            print(f"    → {residente.nombre} pasa a {residente.servicio_actual.nombre}.")

    def ver_plan(self) -> None:
        if self._avisar_si_plan_vacio():
            return
        adelante = [f"{s.nombre} ({s.semanas} sem)" for s in self.plan.recorrer_hacia_adelante()]
        atras = [s.nombre for s in self.plan.recorrer_hacia_atras()]
        print(f"\n  Servicios: {len(self.plan)}   |   Ciclo completo: "
              f"{self.plan.semanas_del_ciclo()} semanas")
        print("  Orden de rotación: " + " → ".join(adelante) + " → (vuelve a empezar)")
        print("  En sentido inverso: " + " ← ".join(atras) + " ← …")
        print(f"  Servicio de ingreso: {self.plan.servicio_de_ingreso.nombre}")

    # ----------------------------------------------------------------- residentes
    def registrar_residente(self) -> None:
        if self._avisar_si_plan_vacio():
            print("  Primero agrega al menos un servicio al plan.")
            return
        nombre = pedir_texto("Nombre del residente: ")
        inicial = input("Servicio inicial (Enter = servicio de ingreso): ").strip() or None
        residente = self.coordinacion.registrar_residente(nombre, inicial)
        print(f"  ✓ {residente.nombre} empieza en {residente.servicio_actual.nombre}.")

    def rotar_residente(self) -> None:
        residente = self.coordinacion.rotar_residente(pedir_texto("Nombre del residente: "))
        print(f"  ✓ {residente.nombre} rotó a {residente.servicio_actual.nombre}.")
        self._anunciar_ciclo(residente)

    def devolver_residente(self) -> None:
        residente = self.coordinacion.devolver_residente(pedir_texto("Nombre del residente: "))
        print(f"  ↩ {residente.nombre} regresó a {residente.servicio_actual.nombre}.")

    def rotar_a_todos(self) -> None:
        if not self.coordinacion.residentes:
            print("  (No hay residentes registrados)")
            return
        self.coordinacion.rotar_a_todos()
        print("  ✓ Fin de periodo. Nueva ubicación:")
        for residente in self.coordinacion.residentes:
            print(f"    {residente.nombre:<15} → {residente.servicio_actual.nombre}")
            self._anunciar_ciclo(residente)

    def consultar_residente(self) -> None:
        residente = self.coordinacion.obtener_residente(pedir_texto("Nombre del residente: "))
        actual = residente.servicio_actual
        print(f"\n  {residente.nombre}")
        print(f"    Viene de:  {actual.servicio_previo.nombre}")
        print(f"    Está en:   {actual.nombre} ({actual.semanas} semanas)")
        print(f"    Va hacia:  {actual.proximo_servicio.nombre}")
        print(f"    Ciclos completados: {residente.ciclos_completados}")

    def retirar_residente(self) -> None:
        residente = self.coordinacion.retirar_residente(pedir_texto("Nombre del residente: "))
        print(f"  ✓ {residente.nombre} salió de la rotación.")

    def ver_residentes_por_servicio(self) -> None:
        if self._avisar_si_plan_vacio():
            return
        print()
        for servicio in self.plan.recorrer_hacia_adelante():
            nombres = [r.nombre for r in self.coordinacion.residentes_en(servicio)]
            print(f"  {servicio.nombre:<20} {', '.join(nombres) if nombres else '—'}")

    # ----------------------------------------------------------------- auxiliares
    def _anunciar_ciclo(self, residente) -> None:
        if residente.servicio_actual is residente.servicio_de_inicio:
            print(f"    ★ {residente.nombre} completó el ciclo número "
                  f"{residente.ciclos_completados}.")

    def _avisar_si_plan_vacio(self) -> bool:
        if self.plan.esta_vacio():
            print("\n  (El plan de rotación está vacío)")
            return True
        return False


def pedir_texto(mensaje: str) -> str:
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("  ✗ No puede quedar vacío.")


def pedir_entero_positivo(mensaje: str) -> int:
    while True:
        try:
            numero = int(input(mensaje).strip())
            if numero > 0:
                return numero
        except ValueError:
            pass
        print("  ✗ Escribe un número entero mayor que 0.")
