# TRAZA-RFID

Página de presentación del Trabajo Práctico Integrador de **Introducción a la Ingeniería (UNLZ)**.

**Situación B:** planta automatizada de clasificación y despacho de insumos médicos.
**Alternativa elegida:** sistema mixto con RFID y asistencia humana, con tags que además miden la temperatura (cadena de frío).

## Cómo usarla
- Abrí `index.html` en el navegador (funciona sin servidor).
- `←` `→` / barra espaciadora / clicker: cambiar de pantalla.
- `F`: pantalla completa.
- `#7` al final de la URL abre directo esa pantalla.

## Equipo
Matias Cruz · Lara Pintos · Lautaro Garnica · Mia Politi · Morena Miranda · Juan Ignacio Sánchez

## Plano de la planta
- `plano/traza-rfid-planta.dxf`: plano de 40 × 25 m para abrir y editar en AutoCAD (capas separadas: muros, cámara de frío, estanterías, portales RFID, fast-track, recorridos, cotas, rótulo).
- `plano/generar_plano.py`: genera el DXF y actualiza el plano de la web (`pip install ezdxf`, después `python plano/generar_plano.py`).
