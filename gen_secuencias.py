#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera diagramas de secuencia UML compactos en SVG (legibles a 15.5 cm de ancho)."""

import html
import os

FONT = "DejaVu Sans, Arial, sans-serif"
FS = 13.0          # tamaño de fuente base
COLW = 148.0       # ancho de columna
MARGIN = 26.0
ROW = 34.0         # separación vertical entre mensajes
BOXH = 46.0
TOP = 74.0         # espacio para cabeceras


def text_w(s, fs=FS):
    return len(s) * fs * 0.55


class Seq:
    def __init__(self, participants, title=""):
        self.participants = participants
        self.msgs = []
        self.title = title

    def msg(self, a, b, label, ret=False, self_call=False):
        self.msgs.append((a, b, label, ret, self_call))

    def render(self):
        w = MARGIN * 2 + COLW * (len(self.participants) - 1) + 130
        h = TOP + ROW * (len(self.msgs) + 1) + 24
        cx = {(p[0] if isinstance(p, tuple) else p): MARGIN + 65 + COLW * i
              for i, p in enumerate(self.participants)}
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
               f'viewBox="0 0 {w:.0f} {h:.0f}" font-family="{FONT}">']
        out.append('<defs><marker id="ar" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">'
                   '<path d="M0,0 L9,3.5 L0,7 z" fill="#202124"/></marker>'
                   '<marker id="aro" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">'
                   '<path d="M0,0 L9,3.5 L0,7 z" fill="#202124" fill-opacity="0"/></marker></defs>')
        out.append(f'<rect width="{w:.0f}" height="{h:.0f}" fill="#ffffff"/>')

        # cabeceras y líneas de vida
        for p in self.participants:
            name, sub = (p if isinstance(p, tuple) else (p, ""))
            x = cx[name]
            out.append(f'<rect x="{x-62:.1f}" y="14" width="124" height="{BOXH}" rx="5" '
                       f'fill="#E8F0FE" stroke="#1A73E8" stroke-width="1.3"/>')
            ty = 32 if sub else 14 + BOXH / 2 + 4.5
            out.append(f'<text x="{x:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="{FS}" '
                       f'fill="#0B2545">{html.escape(name)}</text>')
            if sub:
                out.append(f'<text x="{x:.1f}" y="{ty+13:.1f}" text-anchor="middle" font-size="{FS-3.5}" '
                           f'fill="#5F6368">{html.escape(sub)}</text>')
            out.append(f'<line x1="{x:.1f}" y1="{14+BOXH}" x2="{x:.1f}" y2="{h-14:.1f}" '
                       f'stroke="#9AA0A6" stroke-width="1" stroke-dasharray="5,4"/>')

        y = TOP
        for i, (a, b, label, ret, self_call) in enumerate(self.msgs, start=1):
            xa, xb = cx[a], cx[b]
            dash = ' stroke-dasharray="6,4"' if ret else ''
            if self_call:
                x2 = xa + 26
                out.append(f'<path d="M{xa:.1f},{y} H{x2:.1f} V{y+13:.1f} H{xa+3:.1f}" fill="none" '
                           f'stroke="#202124" stroke-width="1.2"{dash} marker-end="url(#ar)"/>')
                out.append(f'<text x="{x2+8:.1f}" y="{y+9:.1f}" font-size="{FS-1}" fill="#202124">'
                           f'{html.escape(label)}</text>')
            else:
                sign = 1 if xb > xa else -1
                out.append(f'<line x1="{xa + 3*sign:.1f}" y1="{y}" x2="{xb - 3*sign:.1f}" y2="{y}" '
                           f'stroke="#202124" stroke-width="1.2"{dash} marker-end="url(#ar)"/>')
                mx = (xa + xb) / 2
                out.append(f'<text x="{mx:.1f}" y="{y-7:.1f}" text-anchor="middle" font-size="{FS-1}" '
                           f'fill="#202124">{html.escape(label)}</text>')
            # número de orden
            out.append(f'<text x="6" y="{y-7:.1f}" font-size="{FS-3}" fill="#80868b">{i}</text>')
            y += ROW

        out.append('</svg>')
        return "\n".join(out), w, h


def build_registro():
    s = Seq([("Ciudadano", "actor"), ("Controller", "MVC"), ("GestorCasos", "Singleton"),
             ("Factory", "Factory Method"), ("Notificador", "Observer")])
    s.msg("Ciudadano", "Controller", "reportar()")
    s.msg("Controller", "GestorCasos", "getInstance()")
    s.msg("GestorCasos", "Controller", "instancia única", ret=True)
    s.msg("Controller", "GestorCasos", "crearCaso()")
    s.msg("GestorCasos", "Factory", "crear(especie)")
    s.msg("Factory", "GestorCasos", "Expediente", ret=True)
    s.msg("GestorCasos", "GestorCasos", "guardar(caso)", self_call=True)
    s.msg("GestorCasos", "Notificador", "notificar()")
    s.msg("Notificador", "Ciudadano", "push al observador", ret=True)
    s.msg("GestorCasos", "Controller", "CasoRescate", ret=True)
    s.msg("Controller", "Ciudadano", "confirmación", ret=True)
    return s.render()


def build_estado():
    s = Seq([("Voluntario", "actor"), ("Controller", "MVC"), ("GestorCasos", "Singleton"),
             ("CasoRescate", "entidad"), ("Notificador", "Observer")])
    s.msg("Voluntario", "Controller", "putEstado()")
    s.msg("Controller", "GestorCasos", "buscar(id)")
    s.msg("GestorCasos", "Controller", "CasoRescate", ret=True)
    s.msg("Controller", "CasoRescate", "validar()")
    s.msg("CasoRescate", "Controller", "válida / no válida", ret=True)
    s.msg("Controller", "CasoRescate", "cambiarEstado()")
    s.msg("CasoRescate", "CasoRescate", "historial", self_call=True)
    s.msg("CasoRescate", "Notificador", "publicar()")
    s.msg("Notificador", "Voluntario", "auditoría", ret=True)
    s.msg("Controller", "Voluntario", "confirmación", ret=True)
    return s.render()


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    for name, fn in [("03-secuencia-registro", build_registro), ("04-secuencia-estado", build_estado)]:
        svg, w, h = fn()
        p = os.path.join(base, "diagrams", name + ".svg")
        open(p, "w").write(svg)
        print(p, int(w), "x", int(h))
