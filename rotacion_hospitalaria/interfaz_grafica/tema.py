"""Colores y tipografía de la interfaz gráfica (estilo clínico, sobrio)."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

# ---------------------------------------------------------------- paleta
FONDO = "#EEF2F4"          # gris frío de pasillo hospitalario
SUPERFICIE = "#FFFFFF"
BORDE = "#D5DDE2"
TINTA = "#1D2B34"          # texto principal (pizarra)
TINTA_SUAVE = "#5C6E79"    # texto secundario
QUIROFANO = "#0D6E63"      # verde de uniforme quirúrgico: sentido de rotación
QUIROFANO_CLARO = "#E1F0EC"
QUIROFANO_OSCURO = "#095249"
INGRESO = "#B45309"        # ámbar: marca el servicio de ingreso
INGRESO_CLARO = "#FDF0E1"
PREVIO = "#94A3AD"         # enlaces hacia el servicio previo
ALERTA = "#B42318"
ALERTA_CLARO = "#FDECEA"
EXITO_CLARO = "#E6F3EE"

# Colores para las fichas de los residentes (uno por residente).
FICHAS = ["#0D6E63", "#3E5BA9", "#8A4FB0", "#B45309", "#1F7A99", "#A63D5A", "#5B7F2A", "#6B5B4B"]


def elegir_familia(raiz: tk.Misc) -> str:
    """Usa Segoe UI en Windows y una alternativa limpia en otros sistemas."""
    disponibles = set(tkfont.families(raiz))
    for familia in ("Segoe UI", "Inter", "Helvetica Neue", "DejaVu Sans"):
        if familia in disponibles:
            return familia
    return "TkDefaultFont"


class Fuentes:
    """Escala tipográfica de la aplicación."""

    def __init__(self, raiz: tk.Misc) -> None:
        familia = elegir_familia(raiz)
        self.titulo = tkfont.Font(raiz, family=familia, size=15, weight="bold")
        self.subtitulo = tkfont.Font(raiz, family=familia, size=11, weight="bold")
        self.cuerpo = tkfont.Font(raiz, family=familia, size=10)
        self.cuerpo_fuerte = tkfont.Font(raiz, family=familia, size=10, weight="bold")
        self.pequena = tkfont.Font(raiz, family=familia, size=9)
        self.cifra = tkfont.Font(raiz, family=familia, size=18, weight="bold")


def aplicar_estilos(raiz: tk.Tk, fuentes: Fuentes) -> None:
    """Configura los widgets ttk con la paleta de la aplicación."""
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    raiz.configure(background=FONDO)
    raiz.option_add("*TCombobox*Listbox.font", fuentes.cuerpo)
    raiz.option_add("*TCombobox*Listbox.selectBackground", QUIROFANO)

    estilo.configure(".", font=fuentes.cuerpo, background=FONDO, foreground=TINTA)
    estilo.configure("Fondo.TFrame", background=FONDO)
    estilo.configure("Panel.TFrame", background=SUPERFICIE)
    estilo.configure("Panel.TLabel", background=SUPERFICIE, foreground=TINTA)
    estilo.configure("Suave.TLabel", background=SUPERFICIE, foreground=TINTA_SUAVE,
                     font=fuentes.pequena)
    estilo.configure("Seccion.TLabel", background=SUPERFICIE, foreground=TINTA,
                     font=fuentes.subtitulo)
    estilo.configure("Panel.TRadiobutton", background=SUPERFICIE, foreground=TINTA)
    estilo.map("Panel.TRadiobutton", background=[("active", SUPERFICIE)])

    estilo.configure("TEntry", fieldbackground=SUPERFICIE, bordercolor=BORDE,
                     lightcolor=BORDE, darkcolor=BORDE, padding=6)
    estilo.map("TEntry", bordercolor=[("focus", QUIROFANO)], lightcolor=[("focus", QUIROFANO)])
    estilo.configure("TCombobox", fieldbackground=SUPERFICIE, bordercolor=BORDE,
                     lightcolor=BORDE, darkcolor=BORDE, padding=5, arrowsize=14)
    estilo.map("TCombobox", fieldbackground=[("readonly", SUPERFICIE)],
               selectbackground=[("readonly", SUPERFICIE)],
               selectforeground=[("readonly", TINTA)],
               foreground=[("disabled", "#A9B6BD")],
               bordercolor=[("focus", QUIROFANO)])
    estilo.configure("TSpinbox", fieldbackground=SUPERFICIE, bordercolor=BORDE,
                     lightcolor=BORDE, darkcolor=BORDE, padding=5, arrowsize=12)

    # Botones: principal (verde), secundario (contorno) y de riesgo (rojo).
    estilo.configure("Principal.TButton", background=QUIROFANO, foreground="#FFFFFF",
                     bordercolor=QUIROFANO, lightcolor=QUIROFANO, darkcolor=QUIROFANO,
                     font=fuentes.cuerpo_fuerte, padding=(14, 7), focuscolor=QUIROFANO)
    estilo.map("Principal.TButton",
               background=[("disabled", "#9DBFB8"), ("pressed", QUIROFANO_OSCURO),
                           ("active", QUIROFANO_OSCURO)],
               bordercolor=[("disabled", "#9DBFB8"), ("active", QUIROFANO_OSCURO)])
    estilo.configure("Secundario.TButton", background=SUPERFICIE, foreground=TINTA,
                     bordercolor=BORDE, lightcolor=SUPERFICIE, darkcolor=SUPERFICIE,
                     padding=(12, 7), focuscolor=SUPERFICIE)
    estilo.map("Secundario.TButton",
               background=[("pressed", QUIROFANO_CLARO), ("active", QUIROFANO_CLARO)],
               bordercolor=[("active", QUIROFANO)],
               foreground=[("disabled", "#A9B6BD")])
    estilo.configure("Riesgo.TButton", background=SUPERFICIE, foreground=ALERTA,
                     bordercolor="#E9B8B3", lightcolor=SUPERFICIE, darkcolor=SUPERFICIE,
                     padding=(12, 7), focuscolor=SUPERFICIE)
    estilo.map("Riesgo.TButton",
               background=[("pressed", ALERTA_CLARO), ("active", ALERTA_CLARO)],
               foreground=[("disabled", "#D9A6A0")])

    estilo.configure("Treeview", background=SUPERFICIE, fieldbackground=SUPERFICIE,
                     foreground=TINTA, rowheight=30, bordercolor=BORDE, borderwidth=0,
                     font=fuentes.cuerpo)
    estilo.configure("Treeview.Heading", background=FONDO, foreground=TINTA_SUAVE,
                     font=fuentes.pequena, relief="flat", padding=(6, 6), bordercolor=BORDE)
    estilo.map("Treeview", background=[("selected", QUIROFANO_CLARO)],
               foreground=[("selected", TINTA)])
    estilo.map("Treeview.Heading", background=[("active", FONDO)])
    estilo.configure("Vertical.TScrollbar", background=FONDO, troughcolor=SUPERFICIE,
                     bordercolor=SUPERFICIE, arrowcolor=TINTA_SUAVE, lightcolor=FONDO,
                     darkcolor=FONDO)
