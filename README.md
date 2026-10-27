# Prompts RCI · Diplomado en IA y Protección de Datos

Material del módulo 3 del Diplomado en IA y Protección de Datos de Northern
International University (Ecuador): prompt engineering en el derecho,
herramientas avanzadas y GPTs personalizados. Aplica la metodología
**Rol · Contexto · Instrucción** de Next Leap, con la identidad visual del
diplomado.

**Publicado en:** https://next-leap-s-a-s.github.io/prompts-rci-niu/

## Qué contiene

- **Módulo** (`index.html`). Ruta de la clase, biblioteca de 54 prompts con rol,
  contexto e instrucción (6 de datos personales con la LOPDP), herramientas
  avanzadas, 16 asistentes listos para copiar, tareas con su criterio, test de
  autoevaluación y lecturas con la tarea final.
- **Laboratorio** (`laboratorio.html`). Editor Rol, Contexto, Instrucción con
  medidor de 10 criterios y detector de datos personales (cédula, RUC, número de
  causa), versiones del prompt, matriz de nueve pruebas en tres modelos e
  informe en Markdown. El trabajo se guarda en el navegador de quien lo usa.

## Cómo está construido

Dos archivos HTML autocontenidos, sin peticiones externas. Se editan en `src/` y
se generan con `python3 src/build.py`. El texto visible pasa una revisión de
redacción en el propio build.

Los ejemplos usan datos ficticios.
