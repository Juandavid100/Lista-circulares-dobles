# 🏥 Rotación de Residentes Médicos — Lista Circular Doblemente Enlazada

Taller de **Estructuras de Datos**. Universidad Cooperativa de Colombia, sede Pasto.

Caso de estudio implementado en **Python**, con una **interfaz por consola** para manipular la estructura.

---

## 1. Caso de estudio

### El problema
En un hospital universitario, los **residentes médicos** no se quedan en un solo servicio. Rotan por un ciclo fijo de servicios (Urgencias, Pediatría, Cirugía, Ginecología…), cada uno con su duración en semanas. Cuando terminan el último servicio, **vuelven a empezar** el ciclo.

La coordinación académica necesita un sistema que atienda estas situaciones:

| Situación real | Qué debe hacer el sistema |
|---|---|
| Un residente termina su periodo en un servicio | Pasarlo al **próximo servicio** del plan |
| Termina el último servicio del ciclo | Volver al **primer servicio** sin interrupción |
| Un residente debe **repetir** el servicio anterior (evaluación pendiente, incapacidad, novedad) | Devolverlo al **servicio previo** sin recorrer todo el plan |
| El hospital abre un servicio nuevo, por ejemplo Psiquiatría | **Insertarlo** entre dos servicios existentes |
| Un servicio se cierra temporalmente (remodelación, falta de docentes) | **Retirarlo** y reubicar a sus residentes en el próximo |
| Fin de periodo académico | **Rotar a todos** los residentes al mismo tiempo |
| Consultar a un residente | Saber de qué servicio **viene**, en cuál **está** y hacia cuál **va** |

### ¿Por qué una lista circular doblemente enlazada?
Cada característica de la estructura responde a una necesidad real del plan:

- **Circular**, porque el plan de rotación es un ciclo. Después del último servicio sigue el primero, sin recalcular posiciones ni usar `% n`.
- **Doblemente enlazada**, porque cada servicio conoce su **próximo** y su **previo**. Devolver a un residente al servicio anterior o mostrar de dónde viene cuesta O(1).
- **Enlazada en lugar de un arreglo**, porque abrir o cerrar un servicio solo reconecta a sus dos vecinos. Además, los residentes guardan una **referencia directa** a su servicio, así que no se pierden ni hay que actualizar índices cuando el plan cambia.

Con una lista simple, devolver a un residente obligaría a recorrer todo el ciclo para encontrar el servicio anterior. Con un arreglo, cada apertura o cierre desplazaría las posiciones y desactualizaría la ubicación de los residentes.

---

## 2. Marco teórico

### ¿Qué es una lista circular doblemente enlazada?
Es una estructura lineal y dinámica formada por elementos enlazados, donde cada elemento guarda:

1. **El dato**: aquí el nombre del servicio y su duración en semanas.
2. **Un enlace al siguiente elemento**: aquí `proximo_servicio`.
3. **Un enlace al elemento anterior**: aquí `servicio_previo`.

Es **circular** porque el último elemento se enlaza con el primero y el primero con el último. Mientras haya elementos, **ningún enlace queda en `None`**.

```
      servicio_de_ingreso
            │
            ▼
      ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌─────────────┐
 ┌───►│ Urgencias │ ⇄── │ Pediatría │ ⇄── │  Cirugía  │ ⇄── │ Ginecología │────┐
 │    │  4 sem    │     │  6 sem    │     │  8 sem    │     │   6 sem     │    │
 │    └───────────┘     └───────────┘     └───────────┘     └─────────────┘    │
 │          ▲                                                                  │
 │          └───────────── proximo_servicio de Ginecología ────────────────────┘
 └────────────────────── servicio_previo de Urgencias ─────────────────────────
```

Los residentes **no** son elementos de la lista. Cada uno guarda una referencia al servicio donde está:

```
   Laura ──► Pediatría          Mateo ──► Cirugía
```

**Caso especial: un solo servicio.** Sus dos enlaces apuntan **a sí mismo**, nunca a `None`:

```
      ┌───────────┐
 ┌───►│ Urgencias │───┐    proximo_servicio = Urgencias
 └────│           │◄──┘    servicio_previo  = Urgencias
      └───────────┘
```

### Correspondencia entre la teoría y el código

| Concepto teórico | Nombre en este proyecto |
|---|---|
| Nodo | `ServicioHospitalario` |
| Lista circular doble | `PlanDeRotacion` |
| Puntero al siguiente | `proximo_servicio` |
| Puntero al anterior | `servicio_previo` |
| Referencia de entrada (cabeza) | `servicio_de_ingreso` |
| Tamaño | `cantidad_servicios` |
| Recorrido hacia adelante / atrás | `recorrer_hacia_adelante` / `recorrer_hacia_atras` |

### Operaciones y complejidad

| Operación | Método | Complejidad |
|---|---|---|
| Insertar al final | `agregar_al_final` | O(1)* |
| Insertar al inicio | `agregar_como_ingreso` | O(1)* |
| Insertar después de un elemento | `agregar_despues_de` | O(n) por la búsqueda, O(1) al enlazar |
| Eliminar | `retirar_servicio` | O(n) por la búsqueda, O(1) al reconectar |
| Buscar | `buscar_servicio` | O(n) |
| Recorrer hacia adelante | `recorrer_hacia_adelante` | O(n) |
| Recorrer hacia atrás | `recorrer_hacia_atras` | O(n) |
| Rotar un residente | `Residente.rotar` | O(1) |
| Devolver un residente | `Residente.devolver` | O(1) |
| Duración del ciclo | `semanas_del_ciclo` | O(n) |

\* La inserción revisa que el servicio no esté repetido, lo que cuesta O(n). El enlace en sí es O(1).

### Inserción al final
El nuevo servicio queda entre el último (`servicio_de_ingreso.servicio_previo`) y el de ingreso:

```python
ultimo = servicio_de_ingreso.servicio_previo
nuevo.servicio_previo  = ultimo
nuevo.proximo_servicio = servicio_de_ingreso
ultimo.proximo_servicio = nuevo
servicio_de_ingreso.servicio_previo = nuevo
```

### Inserción al inicio
Se inserta igual que al final y después se mueve la referencia de entrada. En una lista circular, el "inicio" es solo el punto desde donde se empieza a mirar:

```python
nuevo = agregar_al_final(...)
servicio_de_ingreso = nuevo
```

### Eliminación
Se reconectan los dos vecinos entre sí. Si el servicio eliminado era el de ingreso, la entrada pasa al próximo:

```python
servicio.servicio_previo.proximo_servicio = servicio.proximo_servicio
servicio.proximo_servicio.servicio_previo = servicio.servicio_previo
```

### Recorrido sin ciclo infinito
Como no hay `None` que marque el final, el recorrido **se detiene al volver al servicio de partida**:

```python
actual = servicio_de_ingreso
while True:
    visitar(actual)
    actual = actual.proximo_servicio
    if actual is servicio_de_ingreso:
        break
```

### Ventajas
- **Recorrido bidireccional**: el plan se puede ver en orden de rotación o al revés.
- **Recorrido continuo**: desde cualquier servicio se llega a todos los demás.
- **No hay que calcular el primero ni el último**: el último siempre es `servicio_de_ingreso.servicio_previo`.
- **Insertar o eliminar no desplaza elementos**: solo se reconectan enlaces.
- **Rotar y devolver cuestan O(1)**.

### Desventajas
- **Implementación más compleja**: cada inserción o eliminación actualiza cuatro enlaces en lugar de dos.
- **Más uso de memoria**: cada elemento guarda dos referencias.
- **Riesgo de ciclos infinitos** si un recorrido no controla el punto de parada.
- **Sin acceso por índice**: llegar al servicio número k cuesta O(k).
- **Control estricto**: un enlace mal actualizado rompe el ciclo completo.

---

## 3. Ejecución

Requiere **Python 3.10 o superior**. No usa librerías externas.

```bash
python main.py
```

### Menú

```
╔═══════════════════════════════════════════════╗
║      ROTACIÓN DE RESIDENTES — HOSPITAL        ║
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
╚═══════════════════════════════════════════════╝
```

### Ejemplo de uso

```
  ✓ Medicina Interna es ahora el servicio de ingreso.
  ✓ Ginecología quedó entre Pediatría y Cirugía.

  Servicios: 5   |   Ciclo completo: 32 semanas
  Orden de rotación: Medicina Interna (8 sem) → Urgencias (4 sem) → Pediatría (6 sem)
                     → Ginecología (6 sem) → Cirugía (8 sem) → (vuelve a empezar)
  En sentido inverso: Medicina Interna ← Cirugía ← Ginecología ← Pediatría ← Urgencias ← …

  ✓ Fin de periodo. Nueva ubicación:
    Laura           → Urgencias
    Mateo           → Medicina Interna

  Mateo
    Viene de:  Cirugía
    Está en:   Medicina Interna (8 semanas)
    Va hacia:  Urgencias

  ↩ Mateo regresó a Cirugía.
```

### Pruebas

```bash
python -m unittest -v
```

Las 21 pruebas verifican, después de cada operación, que **todos los enlaces son recíprocos** (`s.proximo_servicio.servicio_previo is s`) y que el plan sigue siendo circular. También prueban los casos límite: plan vacío, un solo servicio, cierre del servicio de ingreso y reubicación de residentes.

---

## 4. Estructura del proyecto

```
├── main.py                        # Punto de entrada
├── rotacion_hospitalaria/
│   ├── servicio.py                # ServicioHospitalario: el elemento de la lista
│   ├── plan.py                    # PlanDeRotacion: la lista circular doble
│   ├── residente.py               # Residente: se mueve dentro del plan
│   ├── coordinacion.py            # CoordinacionDeResidentes: une plan y residentes
│   └── interfaz_consola.py        # Menú interactivo
└── tests/
    └── test_rotacion.py           # Pruebas unitarias
```

El código separa la **estructura de datos** (`plan.py`), la **lógica del negocio** (`residente.py`, `coordinacion.py`) y la **interfaz** (`interfaz_consola.py`). Así, el mismo plan podría usarse más adelante con una interfaz gráfica o web sin cambiar la lógica.
