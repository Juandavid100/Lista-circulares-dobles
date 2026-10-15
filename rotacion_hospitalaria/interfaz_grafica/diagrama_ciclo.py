"""Dibujo del plan de rotación como un anillo de servicios.

Cada servicio es una tarjeta ubicada sobre un círculo. Por fuera del anillo
van las flechas hacia el próximo servicio (sentido de la rotación) y por
dentro las flechas hacia el servicio previo: así se ven los dos enlaces de la
lista circular doble.
"""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Callable

from ..coordinacion import CoordinacionDeResidentes
from ..residente import Residente
from ..servicio import ServicioHospitalario
from . import tema


def rectangulo_redondeado(lienzo: tk.Canvas, x1, y1, x2, y2, radio=10, **opciones) -> int:
    """Tk no tiene rectángulos redondeados: se dibuja un polígono suavizado."""
    r = min(radio, (x2 - x1) / 2, (y2 - y1) / 2)
    puntos = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return lienzo.create_polygon(puntos, smooth=True, **opciones)


def iniciales(nombre: str) -> str:
    partes = nombre.split()
    if len(partes) >= 2:
        return (partes[0][0] + partes[1][0]).upper()
    return nombre[:2].upper()


class DiagramaDelCiclo(tk.Canvas):
    """Lienzo que muestra el plan de rotación y la ubicación de los residentes."""

    def __init__(
        self,
        padre: tk.Misc,
        coordinacion: CoordinacionDeResidentes,
        fuentes: tema.Fuentes,
        color_de_residente: Callable[[Residente], str],
        al_elegir_servicio: Callable[[ServicioHospitalario], None],
    ) -> None:
        super().__init__(padre, background=tema.SUPERFICIE, highlightthickness=0, borderwidth=0)
        self.coordinacion = coordinacion
        self.fuentes = fuentes
        self.color_de_residente = color_de_residente
        self.al_elegir_servicio = al_elegir_servicio
        self.servicio_elegido: ServicioHospitalario | None = None
        self.residente_elegido: Residente | None = None
        self._servicios_dibujados: dict[str, ServicioHospitalario] = {}
        self.bind("<Configure>", lambda _evento: self.dibujar())

    # ---------------------------------------------------------------- público
    def dibujar(self) -> None:
        self.delete("all")
        self._servicios_dibujados.clear()
        ancho, alto = self.winfo_width(), self.winfo_height()
        if ancho < 50 or alto < 50:
            return

        plan = self.coordinacion.plan
        if plan.esta_vacio():
            self._dibujar_estado_vacio(ancho, alto)
            return

        servicios = list(plan.recorrer_hacia_adelante())
        cantidad = len(servicios)
        cx, cy = ancho / 2, (alto - 30) / 2 + 4
        alto_tarjeta = 60

        # Los servicios se ubican sobre un óvalo que aprovecha todo el lienzo.
        # Las tarjetas se encogen cuando hay muchos servicios para no montarse.
        ancho_tarjeta = 164.0
        for _ in range(2):
            radio_x = max(80, (ancho - ancho_tarjeta) / 2 - 22)
            radio_y = max(70, (alto - 30 - alto_tarjeta) / 2 - 44)
            if cantidad > 1:
                cuerda = 2 * min(radio_x, radio_y * 1.4) * math.sin(math.pi / cantidad)
                ancho_tarjeta = max(104, min(164, cuerda * 0.62))

        if cantidad == 1:
            # Un solo servicio: va al centro y sus dos enlaces apuntan a sí mismo.
            posiciones = [(cx, cy - 24)]
            self._dibujar_bucle_unico(posiciones[0], ancho_tarjeta, alto_tarjeta)
        else:
            posiciones = [
                (cx + radio_x * math.cos(self._angulo(i, cantidad)),
                 cy + radio_y * math.sin(self._angulo(i, cantidad)))
                for i in range(cantidad)
            ]
            self._dibujar_centro(cx, cy, cantidad)
            self._dibujar_enlaces(servicios, posiciones, cx, cy, ancho_tarjeta, alto_tarjeta)
        for indice, (servicio, (x, y)) in enumerate(zip(servicios, posiciones)):
            self._dibujar_tarjeta(indice, servicio, x, y, ancho_tarjeta, alto_tarjeta)
        self._dibujar_leyenda(alto)

    # ------------------------------------------------------------- geometría
    @staticmethod
    def _angulo(indice: int, cantidad: int) -> float:
        # El servicio de ingreso arriba y la rotación en sentido horario.
        return -math.pi / 2 + 2 * math.pi * indice / cantidad

    @staticmethod
    def _hasta_el_borde(semi_ancho, arriba, abajo, dx, dy) -> float:
        """Distancia desde el centro de una tarjeta hasta su borde en la dirección (dx, dy).

        El borde de abajo es más profundo porque ahí van las fichas de los residentes.
        """
        limites = []
        if abs(dx) > 1e-9:
            limites.append(semi_ancho / abs(dx))
        if dy > 1e-9:
            limites.append(abajo / dy)
        elif dy < -1e-9:
            limites.append(arriba / -dy)
        return min(limites)

    def _trazo_entre(self, origen, destino, cx, cy, ancho, alto, desplazamiento, curva):
        """Puntos de una flecha curva que va del borde de una tarjeta al de otra.

        `desplazamiento` > 0 la corre hacia afuera del anillo; < 0, hacia adentro.
        """
        (xa, ya), (xb, yb) = origen, destino
        largo = math.hypot(xb - xa, yb - ya) or 1.0
        dx, dy = (xb - xa) / largo, (yb - ya) / largo
        # Normal que apunta hacia afuera del anillo.
        nx, ny = -dy, dx
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        if nx * (mx - cx) + ny * (my - cy) < 0:
            nx, ny = -nx, -ny
        arriba, abajo = alto / 2 + 20, alto / 2 + 34
        salida = self._hasta_el_borde(ancho / 2 + 8, arriba, abajo, dx, dy)
        llegada = self._hasta_el_borde(ancho / 2 + 8, arriba, abajo, -dx, -dy)
        x1, y1 = xa + dx * salida, ya + dy * salida
        x2, y2 = xb - dx * llegada, yb - dy * llegada
        recorrido = math.hypot(x2 - x1, y2 - y1)
        if recorrido < 18 or (x2 - x1) * dx + (y2 - y1) * dy <= 0:
            return None
        empuje = desplazamiento + math.copysign(curva * recorrido, desplazamiento)
        return [x1 + nx * desplazamiento, y1 + ny * desplazamiento,
                mx + nx * empuje, my + ny * empuje,
                x2 + nx * desplazamiento, y2 + ny * desplazamiento]

    # ---------------------------------------------------------------- partes
    def _dibujar_estado_vacio(self, ancho, alto) -> None:
        cx, cy = ancho / 2, alto / 2
        radio = min(ancho, alto) * 0.28
        self.create_oval(cx - radio, cy - radio, cx + radio, cy + radio,
                         outline=tema.BORDE, width=2, dash=(6, 6))
        self.create_text(cx, cy - 12, text="El plan de rotación está vacío",
                         font=self.fuentes.subtitulo, fill=tema.TINTA)
        self.create_text(cx, cy + 14, width=radio * 1.7, justify="center",
                         text="Agrega el primer servicio en el panel izquierdo "
                              "o carga el plan de ejemplo.",
                         font=self.fuentes.cuerpo, fill=tema.TINTA_SUAVE)

    def _dibujar_centro(self, cx, cy, cantidad) -> None:
        semanas = self.coordinacion.plan.semanas_del_ciclo()
        self.create_text(cx, cy - 16, text=f"{semanas} semanas",
                         font=self.fuentes.cifra, fill=tema.TINTA)
        self.create_text(cx, cy + 10, text="por ciclo completo",
                         font=self.fuentes.cuerpo, fill=tema.TINTA_SUAVE)
        texto = "1 servicio" if cantidad == 1 else f"{cantidad} servicios"
        self.create_text(cx, cy + 30, text=texto, font=self.fuentes.pequena,
                         fill=tema.TINTA_SUAVE)

    def _dibujar_enlaces(self, servicios, posiciones, cx, cy, ancho, alto) -> None:
        cantidad = len(servicios)
        servicio_destacado = (self.residente_elegido.servicio_actual
                              if self.residente_elegido else self.servicio_elegido)
        separacion = 9 if cantidad > 2 else 16

        for indice, servicio in enumerate(servicios):
            siguiente = servicios[(indice + 1) % cantidad]
            origen, destino = posiciones[indice], posiciones[(indice + 1) % cantidad]

            # Enlace al próximo servicio: por fuera, en el sentido de la rotación.
            trazo = self._trazo_entre(origen, destino, cx, cy, ancho, alto, separacion, 0.10)
            if trazo:
                destacado = servicio is servicio_destacado
                self.create_line(
                    trazo, smooth=True, arrow=tk.LAST, arrowshape=(12, 14, 5),
                    width=3.4 if destacado else 2.2, capstyle=tk.ROUND,
                    fill=tema.QUIROFANO if destacado or servicio_destacado is None
                    else "#93C4BA")

            # Enlace al servicio previo: por dentro, en sentido contrario.
            trazo = self._trazo_entre(destino, origen, cx, cy, ancho, alto, -separacion, 0.04)
            if trazo:
                destacado = siguiente is servicio_destacado
                self.create_line(
                    trazo, smooth=True, arrow=tk.LAST, arrowshape=(10, 12, 4),
                    width=2.4 if destacado else 1.4,
                    fill="#5C6E79" if destacado else tema.PREVIO,
                    dash=() if destacado else (5, 4))

    def _dibujar_bucle_unico(self, posicion, ancho_tarjeta, alto_tarjeta) -> None:
        # Con un solo servicio, sus dos enlaces apuntan a sí mismo.
        x, y = posicion
        for radio_x, radio_y, horario, color, grosor, trazos in (
            (ancho_tarjeta / 2 + 64, alto_tarjeta / 2 + 58, True, tema.QUIROFANO, 2.2, ()),
            (ancho_tarjeta / 2 + 44, alto_tarjeta / 2 + 42, False, tema.PREVIO, 1.4, (5, 4)),
        ):
            puntos: list[float] = []
            for paso in range(41):
                fraccion = paso / 40
                angulo = math.radians(-60 + 300 * fraccion) if horario \
                    else math.radians(240 - 300 * fraccion)
                puntos += [x + radio_x * math.cos(angulo), y + radio_y * math.sin(angulo)]
            self.create_line(puntos, smooth=True, arrow=tk.LAST, arrowshape=(11, 13, 5),
                             fill=color, width=grosor, dash=trazos)
        semanas = self.coordinacion.plan.semanas_del_ciclo()
        self.create_text(x, y + alto_tarjeta / 2 + 92, font=self.fuentes.cuerpo,
                         fill=tema.TINTA_SUAVE, justify="center",
                         text=f"Ciclo de {semanas} semanas.\nCon un solo servicio, "
                              "el próximo y el previo son el mismo servicio.")

    def _dibujar_tarjeta(self, indice, servicio, x, y, ancho, alto) -> None:
        etiqueta = f"servicio:{indice}"
        self._servicios_dibujados[etiqueta] = servicio
        es_ingreso = servicio is self.coordinacion.plan.servicio_de_ingreso
        elegido = servicio is self.servicio_elegido
        del_residente = (self.residente_elegido is not None
                         and servicio is self.residente_elegido.servicio_actual)

        x1, y1, x2, y2 = x - ancho / 2, y - alto / 2, x + ancho / 2, y + alto / 2
        # Sombra suave para despegar la tarjeta del fondo.
        rectangulo_redondeado(self, x1 + 1, y1 + 3, x2 + 1, y2 + 3, 12,
                              fill="#E3E9EC", outline="", tags=etiqueta)
        borde = tema.QUIROFANO if (elegido or del_residente) else tema.BORDE
        relleno = tema.QUIROFANO_CLARO if del_residente else tema.SUPERFICIE
        rectangulo_redondeado(self, x1, y1, x2, y2, 12, fill=relleno, outline=borde,
                              width=2.5 if (elegido or del_residente) else 1.2, tags=etiqueta)
        if es_ingreso:
            rectangulo_redondeado(self, x1, y1, x1 + 6, y2, 3, fill=tema.INGRESO,
                                  outline="", tags=etiqueta)
            self.create_text(x, y1 - 11, text="Ingreso", font=self.fuentes.pequena,
                             fill=tema.INGRESO, tags=etiqueta)

        lineas = self._partir_nombre(servicio.nombre, ancho - 22, self.fuentes.cuerpo_fuerte)
        self.create_text(x, y - 8 if len(lineas) == 1 else y - 11, text="\n".join(lineas),
                         font=self.fuentes.cuerpo_fuerte, fill=tema.TINTA,
                         justify="center", tags=etiqueta)
        residentes = self.coordinacion.residentes_en(servicio)
        detalle = "1 semana" if servicio.semanas == 1 else f"{servicio.semanas} semanas"
        self.create_text(x, y2 - 12 if len(lineas) > 1 else y + 12, text=detalle, font=self.fuentes.pequena,
                         fill=tema.TINTA_SUAVE, tags=etiqueta)
        self._dibujar_fichas(residentes, x, y2 + 16, etiqueta)

        self.tag_bind(etiqueta, "<Button-1>",
                      lambda _evento, s=servicio: self.al_elegir_servicio(s))
        self.tag_bind(etiqueta, "<Enter>", lambda _evento: self.configure(cursor="hand2"))
        self.tag_bind(etiqueta, "<Leave>", lambda _evento: self.configure(cursor=""))

    def _dibujar_fichas(self, residentes, x, y, etiqueta) -> None:
        if not residentes:
            return
        visibles = residentes[:4]
        diametro, espacio = 24, 4
        total = len(visibles) + (1 if len(residentes) > 4 else 0)
        inicio = x - (total * diametro + (total - 1) * espacio) / 2 + diametro / 2
        for posicion, residente in enumerate(visibles):
            fx = inicio + posicion * (diametro + espacio)
            elegido = residente is self.residente_elegido
            self.create_oval(fx - diametro / 2, y - diametro / 2, fx + diametro / 2,
                             y + diametro / 2, fill=self.color_de_residente(residente),
                             outline=tema.TINTA if elegido else tema.SUPERFICIE,
                             width=2.5 if elegido else 2, tags=etiqueta)
            self.create_text(fx, y, text=iniciales(residente.nombre), fill="#FFFFFF",
                             font=self.fuentes.pequena, tags=etiqueta)
        if len(residentes) > 4:
            fx = inicio + 4 * (diametro + espacio)
            self.create_oval(fx - diametro / 2, y - diametro / 2, fx + diametro / 2,
                             y + diametro / 2, fill=tema.FONDO, outline=tema.BORDE, tags=etiqueta)
            self.create_text(fx, y, text=f"+{len(residentes) - 4}", fill=tema.TINTA_SUAVE,
                             font=self.fuentes.pequena, tags=etiqueta)

    def _dibujar_leyenda(self, alto) -> None:
        x, y = 18, alto - 22
        self.create_line(x, y, x + 26, y, fill=tema.QUIROFANO, width=2, arrow=tk.LAST,
                         arrowshape=(8, 10, 4))
        self.create_text(x + 34, y, text="Próximo servicio", anchor="w",
                         font=self.fuentes.pequena, fill=tema.TINTA_SUAVE)
        x += 150
        self.create_line(x + 26, y, x, y, fill=tema.PREVIO, width=1.4, dash=(5, 4),
                         arrow=tk.LAST, arrowshape=(8, 10, 4))
        self.create_text(x + 34, y, text="Servicio previo", anchor="w",
                         font=self.fuentes.pequena, fill=tema.TINTA_SUAVE)
        x += 140
        self.create_rectangle(x, y - 6, x + 5, y + 6, fill=tema.INGRESO, outline="")
        self.create_text(x + 13, y, text="Servicio de ingreso", anchor="w",
                         font=self.fuentes.pequena, fill=tema.TINTA_SUAVE)

    @classmethod
    def _partir_nombre(cls, nombre, ancho_max, fuente) -> list[str]:
        """Parte el nombre en máximo dos líneas para que quepa en la tarjeta."""
        if fuente.measure(nombre) <= ancho_max:
            return [nombre]
        palabras = nombre.split()
        primera = ""
        while palabras and fuente.measure((primera + " " + palabras[0]).strip()) <= ancho_max:
            primera = (primera + " " + palabras.pop(0)).strip()
        if not primera:
            return [cls._recortar(nombre, ancho_max, fuente)]
        return [primera, cls._recortar(" ".join(palabras), ancho_max, fuente)]

    @staticmethod
    def _recortar(texto, ancho_max, fuente) -> str:
        if fuente.measure(texto) <= ancho_max:
            return texto
        while texto and fuente.measure(texto + "…") > ancho_max:
            texto = texto[:-1]
        return texto + "…"
