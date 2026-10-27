#!/usr/bin/env python3
"""Ensambla index.html a partir de src/.

- template.html        : marcado, estilos y logica (UTF-8, legible)
- prompts-*.js         : biblioteca RCI, un archivo por area
- asistentes.js        : asistentes de ejemplo
- assets/*.woff2, .png : tipografias y logo, se incrustan en base64

El resultado es un unico archivo ASCII puro. Uso:  python3 src/build.py
"""
import base64, pathlib, re, sys

SRC = pathlib.Path(__file__).resolve().parent
OUT = SRC.parent / "index.html"
AREAS = ["datos", "civil", "comercial", "laboral", "penal", "administrativo", "constitucional"]
BANNED = ["—", "–", "!", "¡", "no solo", "no sólo", "sino también",
          "sin embargo", "por lo tanto", "en ese sentido", "por ende", "cabe destacar",
          "cabe resaltar", "es importante destacar", "en el mundo actual",
          "cada vez más", "hoy más que nunca", "en la era de"]


def b64(p):
    return base64.b64encode(p.read_bytes()).decode("ascii")


def font_css():
    faces = [("IBM Plex Mono", 400, "ibmplexmono-400.woff2"), ("IBM Plex Mono", 500, "ibmplexmono-500.woff2"),
             ("Inter", 400, "inter-400.woff2"), ("Inter", 500, "inter-500.woff2"), ("Inter", 600, "inter-600.woff2")]
    return "\n".join(
        "@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;"
        "src:url(data:font/woff2;base64,%s) format('woff2');}" % (f, w, b64(SRC / "assets" / fn))
        for f, w, fn in faces)


def esc_html(s):
    return "".join(c if ord(c) < 128 else "&#%d;" % ord(c) for c in s)


def esc_js(s):
    out = []
    for c in s:
        o = ord(c)
        if o < 128:
            out.append(c)
        elif o <= 0xFFFF:
            out.append("\\u%04x" % o)
        else:
            o -= 0x10000
            out.append("\\u%04x\\u%04x" % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)))
    return "".join(out)


def asciify(html):
    out, pos = [], 0
    for m in re.finditer(r"<script\b[^>]*>.*?</script>", html, flags=re.S):
        out.append(esc_html(html[pos:m.start()]))
        out.append(esc_js(m.group(0)))
        pos = m.end()
    out.append(esc_html(html[pos:]))
    return "".join(out)


def check_prose(tpl):
    """Revisa el texto visible y las cadenas de interfaz de la plantilla."""
    problems = []
    body = re.sub(r"<style\b.*?</style>", " ", tpl, flags=re.S)
    scripts = re.findall(r"<script\b.*?</script>", body, flags=re.S)
    body = re.sub(r"<script\b.*?</script>|<!--.*?-->|<!doctype[^>]*>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"&[a-zA-Z]+;|&#\d+;|\{\{[A-Z_]+\}\}", " ", text)
    low = text.lower()
    for bad in BANNED:
        if bad in low:
            i = low.index(bad)
            problems.append("texto: %r cerca de %r" % (bad, text[max(0, i - 40):i + 40].strip()))
    if ";" in text:
        i = text.index(";")
        problems.append("texto: punto y coma cerca de %r" % text[max(0, i - 40):i + 40].strip())
    for s in scripts:
        for lit in re.findall(r'"((?:[^"\\\n]|\\.)*)"', s):
            if not re.search(r"[a-záéíóú]{4,} [a-záéíóú]{3,}", lit.lower()):
                continue
            for bad in BANNED:
                if bad == "!" and ("!=" in lit or lit.startswith("!")):
                    continue
                if bad in lit.lower():
                    problems.append("script: %r en %r" % (bad, lit[:70]))
    return problems


def main():
    tpl = (SRC / "template.html").read_text(encoding="utf-8")
    lab = (SRC / "lab.html").read_text(encoding="utf-8")
    problems = check_prose(tpl) + ["lab: " + p for p in check_prose(lab)]
    if problems:
        print("revision de redaccion:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    prompts = "\n\n".join((SRC / ("prompts-%s.js" % a)).read_text(encoding="utf-8").strip() for a in AREAS)
    asistentes = (SRC / "asistentes.js").read_text(encoding="utf-8").strip()
    i = tpl.index("/* Identidad visual")
    theme = tpl[i:tpl.index("</style>", i)]
    logo = "data:image/png;base64," + b64(SRC / "assets" / "nextleap-mark.png")
    blanco = "data:image/png;base64," + b64(SRC / "assets" / "niu-blanco.png")
    dorado = "data:image/png;base64," + b64(SRC / "assets" / "niu-dorado.png")
    html = (tpl.replace("{{FONT_CSS}}", font_css())
               .replace("{{LOGO_PNG}}", logo)
               .replace("{{NIU_BLANCO}}", blanco)
               .replace("{{NIU_DORADO}}", dorado)
               .replace("{{PROMPTS}}", prompts)
               .replace("{{ASISTENTES_DATOS}}", (SRC / "asistentes-datos.js").read_text(encoding="utf-8").strip().rstrip(","))
               .replace("{{ASISTENTES}}", asistentes))
    labhtml = (lab.replace("{{FONT_CSS}}", font_css())
                  .replace("{{THEME_CSS}}", theme)
                  .replace("{{LOGO_PNG}}", logo)
                  .replace("{{NIU_BLANCO}}", blanco))
    for nombre, h in (("index.html", html), ("laboratorio.html", labhtml)):
        left = re.findall(r"\{\{[A-Z_]+\}\}", h)
        if left:
            sys.exit("placeholders sin resolver en %s: %s" % (nombre, left))
        h = asciify(h)
        assert all(ord(c) < 128 for c in h)
        out = SRC.parent / nombre
        out.write_text(h, encoding="ascii")
        print("ok: %s (%s bytes)" % (out, format(out.stat().st_size, ",")))


if __name__ == "__main__":
    main()
