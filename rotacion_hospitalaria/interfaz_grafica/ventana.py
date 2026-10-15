"""Ventana principal de la coordinación de residentes."""

from __future__ import annotations

import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from ..coordinacion import CoordinacionDeResidentes
from ..datos_ejemplo import cargar_plan_de_ejemplo
from ..residente import Residente
from ..servicio import ServicioHospitalario
from . import tema
from .diagrama_ciclo import DiagramaDelCiclo

OPCION_INGRESO = "Servicio de ingreso"
UBICACION_FINAL, UBICACION_INGRESO, UBICACION_DESPUES = "final", "ingreso", "despues"


class VentanaPrincipal:
    """Arma la ventana y traduce cada acción del usuario en operaciones del plan."""

    def __init__(self, raiz: tk.Tk, coordinacion: CoordinacionDeResidentes | None = None) -> None:
        self.raiz = raiz
        self.coordinacion = coordinacion if coordinacion is not None else CoordinacionDeResidentes()
        self.plan = self.coordinacion.plan
        self.fuentes = tema.Fuentes(raiz)
        tema.aplicar_estilos(raiz, self.fuentes)

        self.servicio_elegido: ServicioHospitalario | None = None
        self.residente_elegido: Residente | None = None
        self._colores: dict[str, str] = {}
        self._aviso_pendiente: str | None = None

        raiz.title("Rotación de residentes")
        raiz.minsize(1120, 640)
        self._construir()
        self.refrescar()
        self.registrar_en_bitacora("Sesión iniciada. Agrega servicios o carga el plan de ejemplo.")

    # =================================================================== armado
    def _construir(self) -> None:
        self.raiz.columnconfigure(0, weight=1)
        self.raiz.rowconfigure(2, weight=1)
        self._construir_encabezado()

        cuerpo = ttk.Frame(self.raiz, style="Fondo.TFrame", padding=(14, 12, 14, 14))
        cuerpo.grid(row=2, column=0, sticky="nsew")
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        izquierda = self._panel(cuerpo, relleno=14)
        izquierda.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        self._construir_panel_servicios(izquierda)

        centro = self._panel(cuerpo, relleno=0)
        centro.grid(row=0, column=1, sticky="nsew")
        self.diagrama = DiagramaDelCiclo(centro, self.coordinacion, self.fuentes,
                                         self.color_de, self.elegir_servicio)
        self.diagrama.pack(fill="both", expand=True, padx=2, pady=2)
        self._construir_aviso(centro)

        derecha = self._panel(cuerpo)
        derecha.grid(row=0, column=2, sticky="nse", padx=(12, 0))
        self._construir_panel_residentes(derecha)

    def _panel(self, padre: tk.Misc, relleno: int = 16) -> tk.Frame:
        marco = tk.Frame(padre, background=tema.SUPERFICIE, highlightbackground=tema.BORDE,
                         highlightthickness=1, padx=relleno, pady=relleno)
        return marco

    def _construir_encabezado(self) -> None:
        encabezado = tk.Frame(self.raiz, background=tema.SUPERFICIE, padx=20, pady=9,
                              highlightbackground=tema.BORDE, highlightthickness=1)
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.columnconfigure(1, weight=1)

        titulos = ttk.Frame(encabezado, style="Panel.TFrame")
        titulos.grid(row=0, column=0, sticky="w")
        ttk.Label(titulos, text="Rotación de residentes", style="Panel.TLabel",
                  font=self.fuentes.titulo).pack(anchor="w")
        ttk.Label(titulos, text="Coordinación académica del hospital universitario",
                  style="Suave.TLabel").pack(anchor="w")

        cifras = ttk.Frame(encabezado, style="Panel.TFrame")
        cifras.grid(row=0, column=2, sticky="e", padx=(0, 24))
        self.cifra_servicios = self._cifra(cifras, "servicios")
        self.cifra_residentes = self._cifra(cifras, "residentes")
        self.cifra_semanas = self._cifra(cifras, "semanas por ciclo")

        acciones = ttk.Frame(encabezado, style="Panel.TFrame")
        acciones.grid(row=0, column=3, sticky="e")
        ttk.Button(acciones, text="Cargar plan de ejemplo", style="Secundario.TButton",
                   command=self.cargar_ejemplo).pack(side="left", padx=(0, 8))
        self.boton_periodo = ttk.Button(acciones, text="Cerrar periodo y rotar a todos",
                                        style="Principal.TButton", command=self.cerrar_periodo)
        self.boton_periodo.pack(side="left")

    def _cifra(self, padre: tk.Misc, texto: str) -> tk.StringVar:
        valor = tk.StringVar(value="0")
        bloque = ttk.Frame(padre, style="Panel.TFrame")
        bloque.pack(side="left", padx=(18, 0))
        ttk.Label(bloque, textvariable=valor, style="Panel.TLabel",
                  font=self.fuentes.cifra).pack(anchor="e")
        ttk.Label(bloque, text=texto, style="Suave.TLabel").pack(anchor="e")
        return valor

    def _construir_aviso(self, contenedor: tk.Misc) -> None:
        self.aviso = tk.Label(contenedor, padx=16, pady=7, font=self.fuentes.cuerpo,
                              wraplength=520, justify="left")

    # ---------------------------------------------------------- panel izquierdo
    def _construir_panel_servicios(self, panel: tk.Frame) -> None:
        panel.configure(width=290)
        ttk.Label(panel, text="Agregar servicio", style="Seccion.TLabel").pack(anchor="w")

        self.nombre_servicio = tk.StringVar()
        self._campo(panel, "Nombre del servicio")
        entrada = ttk.Entry(panel, textvariable=self.nombre_servicio, width=30)
        entrada.pack(fill="x")
        entrada.bind("<Return>", lambda _e: self.agregar_servicio())

        self.semanas_servicio = tk.StringVar(value="4")
        fila = ttk.Frame(panel, style="Panel.TFrame")
        fila.pack(fill="x", pady=(8, 0))
        ttk.Label(fila, text="Duración en semanas", style="Suave.TLabel").pack(side="left")
        ttk.Spinbox(fila, from_=1, to=52, textvariable=self.semanas_servicio,
                    width=6).pack(side="right")

        self._campo(panel, "Ubicación en el ciclo")
        self.ubicacion = tk.StringVar(value=UBICACION_FINAL)
        for texto, valor in (("Al final del ciclo", UBICACION_FINAL),
                             ("Como servicio de ingreso", UBICACION_INGRESO),
                             ("Después de otro servicio", UBICACION_DESPUES)):
            ttk.Radiobutton(panel, text=texto, value=valor, variable=self.ubicacion,
                            style="Panel.TRadiobutton",
                            command=self._actualizar_ubicacion).pack(anchor="w")
        self.servicio_de_referencia = tk.StringVar()
        self.combo_referencia = ttk.Combobox(panel, textvariable=self.servicio_de_referencia,
                                             state="disabled")
        self.combo_referencia.pack(fill="x", pady=(4, 0), padx=(22, 0))

        ttk.Button(panel, text="Agregar servicio", style="Principal.TButton",
                   command=self.agregar_servicio).pack(fill="x", pady=(10, 0))

        self._divisor(panel)
        ttk.Label(panel, text="Servicio seleccionado", style="Seccion.TLabel").pack(anchor="w")
        self.detalle_servicio = ttk.Label(panel, style="Suave.TLabel", justify="left",
                                          wraplength=230)
        self.detalle_servicio.pack(anchor="w", pady=(4, 6), fill="x")
        self.boton_cerrar_servicio = ttk.Button(panel, text="Cerrar servicio",
                                                style="Riesgo.TButton",
                                                command=self.cerrar_servicio)
        self.boton_cerrar_servicio.pack(fill="x")

        self._divisor(panel)
        ttk.Label(panel, text="Registrar residente", style="Seccion.TLabel").pack(anchor="w")
        self.nombre_residente = tk.StringVar()
        self._campo(panel, "Nombre completo")
        entrada = ttk.Entry(panel, textvariable=self.nombre_residente)
        entrada.pack(fill="x")
        entrada.bind("<Return>", lambda _e: self.registrar_residente())
        self.servicio_inicial = tk.StringVar(value=OPCION_INGRESO)
        self._campo(panel, "Empieza en")
        self.combo_inicial = ttk.Combobox(panel, textvariable=self.servicio_inicial,
                                          state="readonly")
        self.combo_inicial.pack(fill="x")
        ttk.Button(panel, text="Registrar residente", style="Principal.TButton",
                   command=self.registrar_residente).pack(fill="x", pady=(10, 0))

    def _campo(self, padre: tk.Misc, texto: str) -> None:
        ttk.Label(padre, text=texto, style="Suave.TLabel").pack(anchor="w", pady=(7, 2))

    def _divisor(self, padre: tk.Misc) -> None:
        tk.Frame(padre, height=1, background=tema.BORDE).pack(fill="x", pady=9)

    # ----------------------------------------------------------- panel derecho
    def _construir_panel_residentes(self, panel: tk.Frame) -> None:
        cabecera = ttk.Frame(panel, style="Panel.TFrame")
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="Residentes", style="Seccion.TLabel").pack(side="left")
        self.conteo_residentes = ttk.Label(cabecera, style="Suave.TLabel")
        self.conteo_residentes.pack(side="right")

        marco_tabla = ttk.Frame(panel, style="Panel.TFrame")
        marco_tabla.pack(fill="both", expand=True, pady=(10, 0))
        columnas = ("nombre", "servicio", "proximo", "ciclos")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings",
                                  selectmode="browse", height=7)
        for columna, titulo, ancho, alineacion in (
            ("nombre", "Residente", 130, "w"),
            ("servicio", "Está en", 135, "w"),
            ("proximo", "Va hacia", 120, "w"),
            ("ciclos", "Ciclos", 58, "center"),
        ):
            self.tabla.heading(columna, text=titulo, anchor=alineacion)
            self.tabla.column(columna, width=ancho, minwidth=40, anchor=alineacion,
                              stretch=columna != "ciclos")
        barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._al_elegir_fila)

        self.ficha = tk.Frame(panel, background=tema.FONDO, padx=12, pady=8)
        self.ficha.pack(fill="x", pady=(10, 8))
        self.ficha_titulo = ttk.Label(self.ficha, background=tema.FONDO,
                                      font=self.fuentes.cuerpo_fuerte)
        self.ficha_titulo.pack(anchor="w")
        self.ficha_recorrido = ttk.Label(self.ficha, background=tema.FONDO,
                                         foreground=tema.TINTA_SUAVE, justify="left",
                                         wraplength=400)
        self.ficha_recorrido.pack(anchor="w", pady=(4, 0))

        botones = ttk.Frame(panel, style="Panel.TFrame")
        botones.pack(fill="x")
        botones.columnconfigure((0, 1), weight=1, uniform="botones")
        self.boton_devolver = ttk.Button(botones, text="Devolver al previo",
                                         style="Secundario.TButton",
                                         command=self.devolver_residente)
        self.boton_devolver.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.boton_rotar = ttk.Button(botones, text="Rotar al próximo",
                                      style="Principal.TButton", command=self.rotar_residente)
        self.boton_rotar.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self.boton_retirar = ttk.Button(botones, text="Retirar residente",
                                        style="Riesgo.TButton", command=self.retirar_residente)
        self.boton_retirar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        self._divisor(panel)
        ttk.Label(panel, text="Bitácora de movimientos", style="Seccion.TLabel").pack(anchor="w")
        self.bitacora = tk.Text(panel, height=5, width=46, wrap="word", relief="flat",
                                background=tema.SUPERFICIE, foreground=tema.TINTA,
                                font=self.fuentes.pequena, padx=0, pady=6,
                                highlightthickness=0, cursor="arrow")
        self.bitacora.pack(fill="both")
        self.bitacora.tag_configure("hora", foreground=tema.TINTA_SUAVE)
        self.bitacora.configure(state="disabled")

    # ================================================================ refresco
    def refrescar(self) -> None:
        """Vuelve a pintar toda la ventana a partir del estado del plan."""
        nombres = [s.nombre for s in self.plan.recorrer_hacia_adelante()]
        residentes = self.coordinacion.residentes

        # Si lo elegido ya no existe, se suelta la selección.
        if self.servicio_elegido is not None and self.servicio_elegido.nombre not in nombres:
            self.servicio_elegido = None
        if self.residente_elegido is not None and self.residente_elegido not in residentes:
            self.residente_elegido = None

        self.cifra_servicios.set(str(len(self.plan)))
        self.cifra_residentes.set(str(len(residentes)))
        self.cifra_semanas.set(str(self.plan.semanas_del_ciclo()))

        self.combo_referencia.configure(values=nombres)
        if self.servicio_de_referencia.get() not in nombres:
            self.servicio_de_referencia.set(nombres[-1] if nombres else "")
        self.combo_inicial.configure(values=[OPCION_INGRESO, *nombres])
        if self.servicio_inicial.get() not in (OPCION_INGRESO, *nombres):
            self.servicio_inicial.set(OPCION_INGRESO)

        self._refrescar_tabla(residentes)
        self._refrescar_servicio_elegido()
        self._refrescar_ficha()
        self.boton_periodo.state(["!disabled"] if residentes else ["disabled"])

        self.diagrama.servicio_elegido = self.servicio_elegido
        self.diagrama.residente_elegido = self.residente_elegido
        self.diagrama.dibujar()

    def _refrescar_tabla(self, residentes: list[Residente]) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for residente in residentes:
            actual = residente.servicio_actual
            self.tabla.insert("", "end", iid=self._clave(residente), values=(
                residente.nombre, actual.nombre, actual.proximo_servicio.nombre,
                residente.ciclos_completados))
        if self.residente_elegido is not None:
            clave = self._clave(self.residente_elegido)
            self.tabla.selection_set(clave)
            self.tabla.see(clave)
        cantidad = len(residentes)
        self.conteo_residentes.configure(
            text="Sin residentes" if cantidad == 0
            else ("1 residente" if cantidad == 1 else f"{cantidad} residentes"))

    def _refrescar_servicio_elegido(self) -> None:
        servicio = self.servicio_elegido
        if servicio is None:
            self.detalle_servicio.configure(
                text="Elige un servicio en el diagrama.")
            self.boton_cerrar_servicio.state(["disabled"])
            return
        cantidad = len(self.coordinacion.residentes_en(servicio))
        ocupacion = ("sin residentes" if cantidad == 0
                     else "1 residente" if cantidad == 1 else f"{cantidad} residentes")
        self.detalle_servicio.configure(text=(
            f"{servicio.nombre}, {servicio.semanas} semanas, {ocupacion}.\n"
            f"Viene de {servicio.servicio_previo.nombre} y "
            f"rota hacia {servicio.proximo_servicio.nombre}."))
        self.boton_cerrar_servicio.state(["!disabled"])

    def _refrescar_ficha(self) -> None:
        residente = self.residente_elegido
        botones = (self.boton_devolver, self.boton_rotar, self.boton_retirar)
        if residente is None:
            self.ficha_titulo.configure(text="Ningún residente seleccionado")
            self.ficha_recorrido.configure(
                text="Elige un residente en la tabla para rotarlo o devolverlo.")
            for boton in botones:
                boton.state(["disabled"])
            return
        actual = residente.servicio_actual
        self.ficha_titulo.configure(text=residente.nombre)
        self.ficha_recorrido.configure(text=(
            f"Viene de {actual.servicio_previo.nombre}\n"
            f"Está en {actual.nombre} ({actual.semanas} semanas)\n"
            f"Va hacia {actual.proximo_servicio.nombre}"))
        for boton in botones:
            boton.state(["!disabled"])

    # ================================================================= acciones
    def agregar_servicio(self) -> None:
        def accion():
            nombre = self.nombre_servicio.get()
            semanas = self._leer_semanas()
            ubicacion = self.ubicacion.get()
            if ubicacion == UBICACION_INGRESO:
                servicio = self.plan.agregar_como_ingreso(nombre, semanas)
                detalle = "como nuevo servicio de ingreso"
            elif ubicacion == UBICACION_DESPUES and not self.plan.esta_vacio():
                referencia = self.servicio_de_referencia.get()
                if not referencia:
                    raise ValueError("Elige después de qué servicio va el nuevo servicio.")
                servicio = self.plan.agregar_despues_de(referencia, nombre, semanas)
                detalle = (f"entre {servicio.servicio_previo.nombre} "
                           f"y {servicio.proximo_servicio.nombre}")
            else:
                servicio = self.plan.agregar_al_final(nombre, semanas)
                detalle = "al final del ciclo"
            self.nombre_servicio.set("")
            self.servicio_elegido = servicio
            self.registrar_en_bitacora(f"Se agregó {servicio.nombre} {detalle}.")
        self._ejecutar(accion)

    def cerrar_servicio(self) -> None:
        servicio = self.servicio_elegido
        if servicio is None:
            return
        afectados = self.coordinacion.residentes_en(servicio)
        pregunta = f"¿Cerrar {servicio.nombre} y sacarlo del plan de rotación?"
        if afectados:
            pregunta += (f"\n\n{len(afectados)} residente(s) pasarán a "
                         f"{servicio.proximo_servicio.nombre}.")
        if not messagebox.askyesno("Cerrar servicio", pregunta, icon="warning", parent=self.raiz):
            return

        def accion():
            retirado, reubicados = self.coordinacion.retirar_servicio(servicio.nombre)
            self.servicio_elegido = None
            self.registrar_en_bitacora(f"Se cerró {retirado.nombre}.")
            for residente in reubicados:
                self.registrar_en_bitacora(
                    f"{residente.nombre} pasa a {residente.servicio_actual.nombre}.")
        self._ejecutar(accion)

    def registrar_residente(self) -> None:
        def accion():
            inicial = self.servicio_inicial.get()
            residente = self.coordinacion.registrar_residente(
                self.nombre_residente.get(), None if inicial == OPCION_INGRESO else inicial)
            self.nombre_residente.set("")
            self.residente_elegido = residente
            self.registrar_en_bitacora(
                f"{residente.nombre} empieza en {residente.servicio_actual.nombre}.")
        self._ejecutar(accion)

    def rotar_residente(self) -> None:
        residente = self.residente_elegido
        if residente is None:
            return

        def accion():
            origen = residente.servicio_actual.nombre
            residente.rotar()
            self.registrar_en_bitacora(
                f"{residente.nombre} rotó de {origen} a {residente.servicio_actual.nombre}.")
            self._anunciar_ciclo(residente)
        self._ejecutar(accion)

    def devolver_residente(self) -> None:
        residente = self.residente_elegido
        if residente is None:
            return

        def accion():
            origen = residente.servicio_actual.nombre
            residente.devolver()
            self.registrar_en_bitacora(
                f"{residente.nombre} regresó de {origen} a {residente.servicio_actual.nombre}.")
        self._ejecutar(accion)

    def retirar_residente(self) -> None:
        residente = self.residente_elegido
        if residente is None:
            return
        if not messagebox.askyesno("Retirar residente",
                                   f"¿Retirar a {residente.nombre} de la rotación?",
                                   icon="warning", parent=self.raiz):
            return

        def accion():
            self.coordinacion.retirar_residente(residente.nombre)
            self.residente_elegido = None
            self.registrar_en_bitacora(f"{residente.nombre} salió de la rotación.")
        self._ejecutar(accion)

    def cerrar_periodo(self) -> None:
        def accion():
            cantidad = self.coordinacion.rotar_a_todos()
            texto = "1 residente rotó" if cantidad == 1 else f"{cantidad} residentes rotaron"
            self.registrar_en_bitacora(f"Cierre de periodo: {texto} a su próximo servicio.")
            for residente in self.coordinacion.residentes:
                self._anunciar_ciclo(residente)
            self.mostrar_aviso(f"Periodo cerrado. {texto} a su próximo servicio.", exito=True)
        self._ejecutar(accion)

    def cargar_ejemplo(self) -> None:
        if not self.plan.esta_vacio() and not messagebox.askyesno(
                "Cargar plan de ejemplo",
                "Se reemplazarán los servicios y residentes actuales. ¿Continuar?",
                parent=self.raiz):
            return

        def accion():
            cargar_plan_de_ejemplo(self.coordinacion)
            self.servicio_elegido = None
            self.residente_elegido = None
            self.registrar_en_bitacora("Se cargó el plan de ejemplo con 6 servicios y 6 residentes.")
        self._ejecutar(accion)

    def elegir_servicio(self, servicio: ServicioHospitalario) -> None:
        self.servicio_elegido = None if servicio is self.servicio_elegido else servicio
        if self.servicio_elegido is not None:
            self.servicio_de_referencia.set(servicio.nombre)
        self.refrescar()

    # =============================================================== auxiliares
    def _ejecutar(self, accion) -> None:
        """Corre una acción, muestra el error si lo hay y refresca la ventana."""
        try:
            accion()
        except ValueError as error:
            self.mostrar_aviso(str(error))
        self.refrescar()

    def _leer_semanas(self) -> int:
        try:
            semanas = int(self.semanas_servicio.get().strip())
        except ValueError:
            raise ValueError("La duración debe ser un número entero de semanas.") from None
        if not 1 <= semanas <= 52:
            raise ValueError("La duración debe estar entre 1 y 52 semanas.")
        return semanas

    def _actualizar_ubicacion(self) -> None:
        despues = self.ubicacion.get() == UBICACION_DESPUES
        self.combo_referencia.configure(state="readonly" if despues else "disabled")

    def _al_elegir_fila(self, _evento=None) -> None:
        seleccion = self.tabla.selection()
        residente = None
        if seleccion:
            for candidato in self.coordinacion.residentes:
                if self._clave(candidato) == seleccion[0]:
                    residente = candidato
        if residente is not self.residente_elegido:
            self.residente_elegido = residente
            self._refrescar_ficha()
            self.diagrama.residente_elegido = residente
            self.diagrama.dibujar()

    def _anunciar_ciclo(self, residente: Residente) -> None:
        if residente.servicio_actual is residente.servicio_de_inicio:
            self.registrar_en_bitacora(
                f"{residente.nombre} completó el ciclo {residente.ciclos_completados}.")

    @staticmethod
    def _clave(residente: Residente) -> str:
        return residente.nombre.lower()

    def color_de(self, residente: Residente) -> str:
        clave = self._clave(residente)
        if clave not in self._colores:
            self._colores[clave] = tema.FICHAS[len(self._colores) % len(tema.FICHAS)]
        return self._colores[clave]

    def registrar_en_bitacora(self, mensaje: str) -> None:
        self.bitacora.configure(state="normal")
        self.bitacora.insert("1.0", f"{mensaje}\n")
        self.bitacora.insert("1.0", f"{datetime.now():%H:%M}  ", "hora")
        self.bitacora.configure(state="disabled")

    def mostrar_aviso(self, mensaje: str, exito: bool = False) -> None:
        self.aviso.configure(
            text=mensaje,
            background=tema.EXITO_CLARO if exito else tema.ALERTA_CLARO,
            foreground=tema.QUIROFANO_OSCURO if exito else tema.ALERTA)
        self.aviso.place(relx=0.5, rely=1.0, y=-44, anchor="s")
        self.aviso.lift()
        if self._aviso_pendiente is not None:
            self.raiz.after_cancel(self._aviso_pendiente)
        self._aviso_pendiente = self.raiz.after(5000, self._ocultar_aviso)

    def _ocultar_aviso(self) -> None:
        self._aviso_pendiente = None
        self.aviso.place_forget()


def iniciar() -> None:
    """Abre la ventana. En Windows activa el escalado nítido de pantallas HD."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass
    raiz = tk.Tk()
    VentanaPrincipal(raiz)
    if sys.platform == "win32":
        raiz.state("zoomed")
    else:
        raiz.geometry("1366x800")
    raiz.mainloop()
