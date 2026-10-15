"""Punto de entrada: ejecuta `python main.py` para abrir la coordinación de residentes."""

from rotacion_hospitalaria.interfaz_consola import InterfazConsola


def main() -> None:
    try:
        InterfazConsola().iniciar()
    except (KeyboardInterrupt, EOFError):
        print("\nSesión cerrada.")


if __name__ == "__main__":
    main()
