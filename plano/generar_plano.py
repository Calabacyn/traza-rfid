"""Genera el plano de planta de TRAZA-RFID.

Una sola definicion (en metros, origen abajo-izquierda) produce:
  - plano/traza-rfid-planta.dxf  -> para abrir y editar en AutoCAD (capas separadas)
  - index.html                   -> inyecta el SVG entre <!--PLANO:INICIO--> y <!--PLANO:FIN-->

Uso:  python plano/generar_plano.py   (requiere: pip install ezdxf)
"""
from pathlib import Path
import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

ROOT = Path(__file__).resolve().parent.parent
W, H = 40.0, 25.0  # nave de 40 x 25 m

# capa: (color ACI, tipo de linea)
LAYERS = {
    "MUROS": (7, "Continuous"),
    "TABIQUES": (7, "Continuous"),
    "CAMARA_FRIO": (5, "Continuous"),
    "PUERTAS": (3, "Continuous"),
    "ESTANTERIAS": (8, "Continuous"),
    "MOBILIARIO": (8, "Continuous"),
    "DEMARCACION": (2, "DASHED"),
    "PORTALES_RFID": (2, "Continuous"),
    "ANTENAS_RFID": (30, "Continuous"),
    "TAGS_POSICION": (6, "Continuous"),
    "LECTOR_ZORRA": (30, "Continuous"),
    "REFERENCIAS": (7, "Continuous"),
    "FAST_TRACK": (1, "Continuous"),
    "RECORRIDO": (4, "DASHED"),
    "RECORRIDO_URGENTE": (1, "DASHED"),
    "CAMIONES": (9, "Continuous"),
    "TEXTOS": (7, "Continuous"),
    "COTAS": (6, "Continuous"),
    "ROTULO": (7, "Continuous"),
}

P = []  # primitivas


def wall(pts, w=0.3, layer="MUROS"):
    P.append(("wall", pts, w, layer))


def line(a, b, layer, cls=""):
    P.append(("line", a, b, layer, cls))


def rect(x0, y0, x1, y1, layer, cls=""):
    P.append(("rect", x0, y0, x1, y1, layer, cls))


def text(x, y, s, h=0.45, layer="TEXTOS", cls="", rot=0):
    P.append(("text", x, y, s, h, layer, cls, rot))


def hatch(pts, layer, cls):
    P.append(("hatch", pts, layer, cls))


def arc(cx, cy, r, a0, a1, layer="PUERTAS"):
    P.append(("arc", cx, cy, r, a0, a1, layer))


def dim(p1, p2, base, angle=0):
    P.append(("dim", p1, p2, base, angle))


def badge(x, y, n):
    P.append(("badge", x, y, n))


def antenna(x, y):
    """Antena RFID fija de techo (lectura continua)."""
    P.append(("antenna", x, y))


def tag(x, y):
    """Tag de posición fijo en una estantería (ubicación exacta)."""
    P.append(("tag", x, y))


def reader(x, y):
    """Lector RFID montado en una zorra eléctrica."""
    P.append(("reader", x, y))


def rack(x0, y0, x1, y1, cls):
    """Módulo de estantería con su tag de posición en el frente."""
    rect(x0, y0, x1, y1, "ESTANTERIAS", cls)
    tag((x0 + x1) / 2, y0 + 0.3)


# ---------------- muros exteriores (con aberturas) ----------------
# izquierda x=0: portones recepcion y 16.5-19.5 / 21-24
wall([(0, 16.5), (0, 0), (40, 0), (40, 1)])
wall([(0, 19.5), (0, 21)])
wall([(0, 24), (0, 25), (36, 25)])
# arriba: puerta de personal 36-37.2 ; derecha: urgencias y 1-3.2, despacho 5-8.5 / 9.5-13
wall([(37.2, 25), (40, 25), (40, 13)])
wall([(40, 3.2), (40, 5)])
wall([(40, 8.5), (40, 9.5)])

# portones (cortina enrollable = linea punteada en la abertura)
for (a, b) in [((0, 16.5), (0, 19.5)), ((0, 21), (0, 24)), ((40, 5), (40, 8.5)), ((40, 9.5), (40, 13)), ((40, 1), (40, 3.2))]:
    line(a, b, "PUERTAS", "door")
arc(37.2, 25, 1.2, 180, 270)
line((37.2, 25), (37.2, 23.8), "PUERTAS")

# ---------------- camara de frio 8-18 x 15-25 ----------------
rect(8, 15, 18, 25, "CAMARA_FRIO", "cold")
wall([(12, 15), (8, 15), (8, 25)], 0.25, "CAMARA_FRIO")
wall([(14.5, 15), (18, 15), (18, 25)], 0.25, "CAMARA_FRIO")
line((12, 15), (14.5, 15), "PUERTAS", "door")
for x0 in (8.6, 11.6, 14.6):
    rack(x0, 23.7, x0 + 2.8, 24.75, "rack-cold")
    rack(x0, 19.0, x0 + 2.8, 21.4, "rack-cold")
text(13, 22.55, "CÁMARA DE FRÍO 2–8 °C", 0.4)
# portal en la puerta de la cámara y antenas fijas de techo (lectura continua + temperatura)
P.append(("portal", 12, 15, 14.5, 15, "PORTAL C"))
for (x, y) in [(10.4, 17.4), (16.1, 17.4), (8.75, 22.55), (17.25, 22.55)]:
    antenna(x, y)

# ---------------- estanterias alta densidad 20.5-31.5 x 15.3-24.85 ----------------
for (y0, y1) in [(15.5, 16.7), (19.0, 21.4), (23.7, 24.85)]:
    for x0 in (20.5, 23.3, 26.1, 28.9):
        rack(x0, y0, x0 + 2.7, y1, "rack")
text(26, 18.0, "ALTA DENSIDAD", 0.5)
text(26, 22.55, "STOCK GENERAL", 0.38, cls="muted")

# ---------------- anden de recepcion + portal entrada ----------------
rect(0.4, 15.5, 5.0, 24.6, "DEMARCACION", "dock")
text(2.7, 15.9, "ANDÉN RECEPCIÓN", 0.36)
P.append(("portal", 5.7, 16.4, 5.7, 20.8, "PORTAL E"))

# ---------------- pasillo principal y=12-15 ----------------
line((0.4, 13.5), (33.3, 13.5), "DEMARCACION", "axis")
text(27.5, 14.1, "PASILLO PRINCIPAL", 0.36, cls="muted")

# ---------------- vestuario 0-7 x 0-4 / cuarentena 0-7 x 4-12 ----------------
wall([(0, 4), (5.6, 4)], 0.15, "TABIQUES")
wall([(6.6, 4), (7, 4), (7, 7.5)], 0.15, "TABIQUES")
wall([(7, 9), (7, 12), (0, 12)], 0.15, "TABIQUES")
arc(7, 9, 1.5, 180, 270)
arc(5.6, 4, 1.0, 270, 360)
text(4.2, 2, "VESTUARIO / BAÑOS", 0.36, cls="muted")
text(3.5, 8.6, "CONTROL Y", 0.42)
text(3.5, 7.9, "CUARENTENA", 0.42)
rect(1.0, 4.8, 3.2, 6.2, "MOBILIARIO", "table")
rect(1.0, 10.2, 6.2, 11.4, "MOBILIARIO", "table")

# ---------------- clasificacion 8.5-17.5 x 4.5-11 ----------------
rect(8.5, 4.5, 17.5, 11, "DEMARCACION", "zone")
rect(9.5, 8.6, 16.5, 9.6, "MOBILIARIO", "table")
rect(9.5, 5.8, 12.4, 6.8, "MOBILIARIO", "cold-bin")
rect(13.6, 5.8, 16.5, 6.8, "MOBILIARIO", "table")
text(10.95, 6.05, "FRÍO", 0.34)
text(15.05, 6.05, "SECO", 0.34)
text(14.6, 10.2, "CLASIFICACIÓN", 0.42)

# ---------------- preparacion de pedidos 20.5-31.5 x 4.5-11 ----------------
rect(20.5, 4.5, 31.5, 11, "DEMARCACION", "zone")
for x0 in (21.3, 24.0, 26.7, 29.4):
    rect(x0, 7.0, x0 + 1.6, 8.4, "MOBILIARIO", "table")
text(26, 5.3, "PREPARACIÓN DE PEDIDOS", 0.42)

# ---------------- fast-track: conector x 18-20 y carril y 1-3.2 ----------------
ft = [(18, 3.2), (18, 12), (20, 12), (20, 3.2), (40, 3.2), (40, 1), (18, 1)]
hatch(ft, "FAST_TRACK", "fast")
text(30, 1.6, "CARRIL FAST-TRACK · URGENCIAS", 0.48, cls="fast-txt")

# ---------------- portal salida + anden despacho ----------------
P.append(("portal", 33.6, 6.2, 33.6, 10.2, "PORTAL S"))
rect(34.6, 4.0, 39.6, 14.0, "DEMARCACION", "dock")
text(37.1, 13.4, "ANDÉN DESPACHO", 0.36)

# ---------------- sala de control 33.5-40 x 19-25 ----------------
wall([(33.5, 25), (33.5, 19), (35, 19)], 0.15, "TABIQUES")
wall([(36.4, 19), (40, 19)], 0.15, "TABIQUES")
arc(35, 19, 1.4, 0, 90)
rect(34.3, 23.2, 39.2, 24.3, "MOBILIARIO", "table")
text(37.0, 22.2, "SALA DE CONTROL", 0.4)
text(37.0, 21.4, "SUPERVISIÓN", 0.36, cls="muted")

# ---------------- carga de zorras 33.6-39.6 x 15.3-18.5 ----------------
rect(33.6, 15.3, 39.6, 18.5, "DEMARCACION", "zone")
for x0 in (34.0, 35.9, 37.8):
    rect(x0, 15.7, x0 + 1.5, 17.2, "MOBILIARIO", "pjack")
    reader(x0 + 0.75, 16.45)
text(37.2, 17.75, "CARGA ZORRAS", 0.36)

# ---------------- camiones ----------------
for yc in (18.0,):
    rect(-10.6, yc - 1.25, -0.4, yc + 1.25, "CAMIONES", "truck")
    rect(-12.6, yc - 1.15, -10.8, yc + 1.15, "CAMIONES", "cab")
text(-5.5, 18.0, "CAMIÓN REFRIGERADO", 0.4)

# ---------------- recorridos ----------------
ROUTE = [(-2.5, 18), (2.5, 18), (5.7, 18.6), (6.6, 16.6), (6.6, 13.5), (11, 13.5), (11, 9.1),
         (11, 13.5), (13.25, 13.5), (13.25, 17.8), (13.25, 13.5), (26, 13.5), (26, 9.4),
         (31.8, 9.4), (31.8, 8.2), (33.6, 8.2), (37, 8.2), (41, 6.75)]
URGENT = [(13.25, 17.8), (13.25, 13.5), (19, 13.5), (19, 2.6), (41.5, 2.6)]
P.append(("route", ROUTE, "RECORRIDO", "route"))
P.append(("route", URGENT, "RECORRIDO_URGENTE", "route-urg"))

# ---------------- numeracion de zonas (coincide con la leyenda de la web) ----------------
for (x, y, n) in [(2.7, 23.6, 1), (6.6, 21.6, 2), (3.5, 10.8, 3), (9.2, 10.3, 4), (9.0, 16.0, 5),
                  (21.3, 18.0, 6), (21.3, 10.3, 7), (19.0, 4.2, 8), (32.6, 11.0, 9), (35.3, 4.9, 10),
                  (34.2, 20.0, 11), (34.2, 17.75, 12), (1.0, 2.0, 13)]:
    badge(x, y, n)

# ---------------- referencias RFID (espacio libre a la izquierda de la nave) ----------------
LEG_X, LEG_Y = -12.4, 12.6
LEGEND = [("portal", "Portal RFID"),
          ("antenna", "Antena fija de techo"),
          ("tag", "Tag de posición"),
          ("reader", "Lector en zorra")]
P.append(("legend", LEG_X, LEG_Y, LEGEND))

# ---------------- cotas ----------------
dim((0, 0), (40, 0), (0, -1.6))
dim((40, 0), (40, 25), (41.6, 0), 90)
dim((8, 25), (18, 25), (8, 26.2))
dim((31.6, 12), (31.6, 15), (32.3, 12), 90)
dim((31.9, 16.7), (31.9, 19.0), (32.6, 16.7), 90)
dim((21, 1), (21, 3.2), (21.6, 1), 90)


# =====================================================================
def write_dxf(path):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = units.M
    doc.header["$LTSCALE"] = 0.6
    for name, (color, lt) in LAYERS.items():
        doc.layers.add(name, color=color, linetype=lt)
    msp = doc.modelspace()

    def txt(s, x, y, h, layer, rot=0, align=TextEntityAlignment.MIDDLE_CENTER):
        t = msp.add_text(s, height=h, rotation=rot, dxfattribs={"layer": layer, "style": "OpenSans"})
        t.set_placement((x, y), align=align)

    def solid(ps, layer, color):
        hh = msp.add_hatch(color=color, dxfattribs={"layer": layer})
        hh.paths.add_polyline_path(ps, is_closed=True)
        msp.add_lwpolyline(ps, close=True, dxfattribs={"layer": layer})

    def sym_portal(x, y, layer="PORTALES_RFID"):
        sq = [(x - .25, y - .25), (x + .25, y - .25), (x + .25, y + .25), (x - .25, y + .25)]
        solid(sq, layer, 2)

    def sym_antenna(x, y, layer="ANTENAS_RFID"):
        msp.add_circle((x, y), 0.38, dxfattribs={"layer": layer})
        hh = msp.add_hatch(color=30, dxfattribs={"layer": layer})
        hh.paths.add_edge_path().add_arc((x, y), 0.14, 0, 360)

    def sym_tag(x, y, layer="TAGS_POSICION"):
        solid([(x - .17, y - .17), (x + .17, y - .17), (x + .17, y + .17), (x - .17, y + .17)], layer, 6)

    def sym_reader(x, y, layer="LECTOR_ZORRA"):
        solid([(x - .3, y - .22), (x + .3, y - .22), (x, y + .3)], layer, 30)

    for p in P:
        k = p[0]
        if k == "wall":
            msp.add_lwpolyline(p[1], dxfattribs={"layer": p[3], "const_width": p[2]})
        elif k == "line":
            msp.add_line(p[1], p[2], dxfattribs={"layer": p[3]})
        elif k == "rect":
            _, x0, y0, x1, y1, layer, _ = p
            msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": layer})
        elif k == "text":
            _, x, y, s, h, layer, _, rot = p
            txt(s, x, y, h, layer, rot)
        elif k == "hatch":
            hh = msp.add_hatch(color=1, dxfattribs={"layer": p[2]})
            hh.set_pattern_fill("ANSI31", scale=0.6)
            hh.paths.add_polyline_path(p[1], is_closed=True)
            msp.add_lwpolyline(p[1], close=True, dxfattribs={"layer": p[2]})
        elif k == "arc":
            _, cx, cy, r, a0, a1, layer = p
            msp.add_arc((cx, cy), r, a0, a1, dxfattribs={"layer": layer})
        elif k == "portal":
            _, x0, y0, x1, y1, lbl = p
            for (x, y) in ((x0, y0), (x1, y1)):
                sym_portal(x, y)
            msp.add_line((x0, y0), (x1, y1), dxfattribs={"layer": "PORTALES_RFID", "linetype": "DASHED"})
            if y0 == y1:  # portal horizontal (puerta de la cámara)
                txt(lbl, (x0 + x1) / 2, y0 - 0.75, 0.34, "PORTALES_RFID")
            else:
                txt(lbl, x0 - 0.9 if x0 > 30 else x0 + 1.0, (y0 + y1) / 2, 0.34, "PORTALES_RFID", 90)
        elif k == "antenna":
            sym_antenna(p[1], p[2])
        elif k == "tag":
            sym_tag(p[1], p[2])
        elif k == "reader":
            sym_reader(p[1], p[2])
        elif k == "legend":
            _, lx, ly, items = p
            txt("REFERENCIAS RFID", lx, ly, 0.42, "REFERENCIAS", align=TextEntityAlignment.MIDDLE_LEFT)
            draw = {"portal": lambda x, y: sym_portal(x, y, "REFERENCIAS"),
                    "antenna": lambda x, y: sym_antenna(x, y, "REFERENCIAS"),
                    "tag": lambda x, y: sym_tag(x, y, "REFERENCIAS"),
                    "reader": lambda x, y: sym_reader(x, y, "REFERENCIAS")}
            for i, (kind, label) in enumerate(items):
                y = ly - 1.1 * (i + 1)
                draw[kind](lx + 0.4, y)
                txt(label, lx + 1.1, y, 0.34, "REFERENCIAS", align=TextEntityAlignment.MIDDLE_LEFT)
        elif k == "route":
            msp.add_lwpolyline(p[1], dxfattribs={"layer": p[2]})
        elif k == "badge":
            _, x, y, n = p
            msp.add_circle((x, y), 0.42, dxfattribs={"layer": "TEXTOS"})
            txt(str(n), x, y, 0.4, "TEXTOS")
        elif k == "dim":
            _, p1, p2, base, angle = p
            d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, dimstyle="EZDXF",
                                   override={"dimlfac": 1, "dimzin": 0, "dimtxt": 0.4, "dimasz": 0.25, "dimexe": 0.15, "dimexo": 0.15,
                                             "dimdec": 2, "dimtad": 1, "dimgap": 0.08},
                                   dxfattribs={"layer": "COTAS"})
            d.render()

    # rotulo
    rx, ry = 16, -8.5
    msp.add_lwpolyline([(rx, ry), (40, ry), (40, ry + 4.6), (rx, ry + 4.6)], close=True, dxfattribs={"layer": "ROTULO"})
    msp.add_line((rx, ry + 2.3), (40, ry + 2.3), dxfattribs={"layer": "ROTULO"})
    msp.add_line((33, ry), (33, ry + 2.3), dxfattribs={"layer": "ROTULO"})
    for (s, x, y, h) in [("TRAZA-RFID · PLANTA DE CLASIFICACIÓN Y DESPACHO", 28, ry + 3.45, 0.55),
                         ("UNLZ · Introducción a la Ingeniería · TP Integrador", 24.5, ry + 1.15, 0.4),
                         ("Medidas en m · Esc. 1:200", 36.5, ry + 1.15, 0.4)]:
        txt(s, x, y, h, "ROTULO")
    doc.saveas(path)


# =====================================================================
def svg_sym(kind, x, y):
    """Símbolo RFID en coordenadas SVG (y ya invertida)."""
    if kind == "portal":
        return f'<rect class="pl-post" x="{x - .3}" y="{y - .3}" width=".6" height=".6"/>'
    if kind == "antenna":
        return f'<g class="pl-ant"><circle cx="{x}" cy="{y}" r=".38"/><circle class="c" cx="{x}" cy="{y}" r=".14"/></g>'
    if kind == "tag":
        return f'<rect class="pl-tagp" x="{x - .17:.2f}" y="{y - .17:.2f}" width=".34" height=".34"/>'
    return f'<polygon class="pl-reader" points="{x - .3:.2f},{y + .22:.2f} {x + .3:.2f},{y + .22:.2f} {x:.2f},{y - .3:.2f}"/>'


def write_svg():
    def Y(y):
        return round(H - y, 3)

    def pts(ps):
        return " ".join(f"{x},{Y(y)}" for x, y in ps)

    o = []
    for p in P:
        k = p[0]
        if k == "wall":
            o.append(f'<polyline class="pl-wall" style="stroke-width:{p[2]}" points="{pts(p[1])}"/>')
        elif k == "line":
            o.append(f'<line class="pl-{p[4] or "ln"}" x1="{p[1][0]}" y1="{Y(p[1][1])}" x2="{p[2][0]}" y2="{Y(p[2][1])}"/>')
        elif k == "rect":
            _, x0, y0, x1, y1, layer, cls = p
            o.append(f'<rect class="pl-{cls}" x="{x0}" y="{Y(y1)}" width="{round(x1 - x0, 3)}" height="{round(y1 - y0, 3)}"/>')
        elif k == "text":
            _, x, y, s, h, layer, cls, rot = p
            o.append(f'<text class="pl-t {("pl-" + cls) if cls else ""}" x="{x}" y="{Y(y)}" font-size="{round(h * 1.3, 3)}">{s}</text>')
        elif k == "hatch":
            o.append(f'<polygon class="pl-{p[3]}" points="{pts(p[1])}"/>')
        elif k == "arc":
            _, cx, cy, r, a0, a1, layer = p
            import math
            sx, sy = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
            ex, ey = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
            o.append(f'<path class="pl-swing" d="M{cx},{Y(cy)} L{sx:.3f},{Y(sy)} A{r},{r} 0 0 0 {ex:.3f},{Y(ey)}"/>')
        elif k == "portal":
            _, x0, y0, x1, y1, lbl = p
            o.append(f'<line class="pl-beam" x1="{x0}" y1="{Y(y0)}" x2="{x1}" y2="{Y(y1)}"/>')
            for (x, y) in ((x0, y0), (x1, y1)):
                o.append(f'<rect class="pl-post" x="{x - .3}" y="{Y(y) - .3}" width=".6" height=".6"/>')
            cx, cy = (x0 + x1) / 2, Y((y0 + y1) / 2)
            o.append(f'<g class="pl-scan"><circle cx="{cx}" cy="{cy}" r="1.2"/><circle cx="{cx}" cy="{cy}" r="1.2" style="animation-delay:.8s"/></g>')
        elif k in ("antenna", "tag", "reader"):
            o.append(svg_sym(k, p[1], Y(p[2])))
        elif k == "legend":
            _, lx, ly, items = p
            o.append(f'<g class="pl-legend"><text class="pl-lt pl-ltitle" x="{lx}" y="{Y(ly)}">REFERENCIAS RFID</text>')
            for i, (kind, label) in enumerate(items):
                yy = Y(ly - 1.1 * (i + 1))
                o.append(svg_sym(kind, lx + 0.4, yy) + f'<text class="pl-lt" x="{lx + 1.1}" y="{yy}">{label}</text>')
            o.append('</g>')
        elif k == "route":
            o.append(f'<polyline id="{p[3]}" class="pl-{p[3]}" points="{pts(p[1])}"/>')
        elif k == "badge":
            _, x, y, n = p
            o.append(f'<g class="pl-badge"><rect x="{x - .45}" y="{Y(y) - .45}" width=".9" height=".9"/><text x="{x}" y="{Y(y)}">{n}</text></g>')
        elif k == "dim":
            _, p1, p2, base, angle = p
            if angle == 0:
                yb = Y(base[1]); a, b = p1[0], p2[0]
                o.append(f'<g class="pl-dim"><line x1="{a}" y1="{yb}" x2="{b}" y2="{yb}"/>'
                         f'<line x1="{a}" y1="{yb - .3}" x2="{a}" y2="{yb + .3}"/><line x1="{b}" y1="{yb - .3}" x2="{b}" y2="{yb + .3}"/>'
                         f'<text x="{(a + b) / 2}" y="{yb - .25}">{abs(b - a):.2f}</text></g>')
            else:
                xb = base[0]; a, b = Y(p1[1]), Y(p2[1])
                o.append(f'<g class="pl-dim"><line x1="{xb}" y1="{a}" x2="{xb}" y2="{b}"/>'
                         f'<line x1="{xb - .3}" y1="{a}" x2="{xb + .3}" y2="{a}"/><line x1="{xb - .3}" y1="{b}" x2="{xb + .3}" y2="{b}"/>'
                         f'<text transform="translate({xb + .35} {(a + b) / 2}) rotate(-90)">{abs(b - a):.2f}</text></g>')

    route_d = "M" + " L".join(f"{x},{Y(y)}" for x, y in ROUTE)
    urg_d = "M" + " L".join(f"{x},{Y(y)}" for x, y in URGENT)
    # escala grafica
    o.append('<g class="pl-scale"><rect x="-12.6" y="27.0" width="5" height=".35"/><rect x="-7.6" y="27.0" width="5" height=".35" class="w"/>'
             '<text x="-12.6" y="26.7">0</text><text x="-7.6" y="26.7">5</text><text x="-2.6" y="26.7">10 m</text></g>')
    # bultos animados
    o.append(f'<g class="pl-pkg"><rect x="-.45" y="-.35" width=".9" height=".7"/>'
             f'<animateMotion dur="18s" repeatCount="indefinite" path="{route_d}"/></g>')
    o.append(f'<g class="pl-pkg urg"><rect x="-.45" y="-.35" width=".9" height=".7"/>'
             f'<animateMotion dur="9s" begin="3s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="0;.35;.85;1" calcMode="linear" path="{urg_d}"/></g>')
    return "\n".join(o)


SVG_HEAD = '<svg id="planta" viewBox="-13.2 -2 56.6 30.2" xmlns="http://www.w3.org/2000/svg" aria-label="Plano de planta TRAZA-RFID, nave de 40 por 25 metros">'

if __name__ == "__main__":
    out = ROOT / "plano"
    write_dxf(out / "traza-rfid-planta.dxf")
    body = write_svg()
    svg = SVG_HEAD + "\n" + body + "\n</svg>"
    idx = ROOT / "index.html"
    html = idx.read_text(encoding="utf8")
    a, b = "<!--PLANO:INICIO-->", "<!--PLANO:FIN-->"
    if a in html:
        i, j = html.index(a) + len(a), html.index(b)
        html = html[:i] + "\n" + svg + "\n" + html[j:]
        idx.write_text(html, encoding="utf8")
    print("ok:", out / "traza-rfid-planta.dxf")
