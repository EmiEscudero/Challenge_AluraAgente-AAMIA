# Biblioteca documental

AAMIA descubre recursivamente los archivos `*.pdf` de esta carpeta, conserva el nombre del documento y la página PDF como metadatos, y reconstruye el índice cuando detecta cambios.

El repositorio incluye `AAMIA_guia_abierta_para_el_cuidado.pdf` como base documental inicial.

## Resúmenes temáticos

La carpeta `resumenes/` contiene cinco síntesis preparadas para la recuperación aumentada:

1. **Salud integral y seguridad clínica.** Valoración inicial, cambios fisiológicos, fragilidad,
   enfermedades crónicas, señales de alarma, medicamentos, polifarmacia, hospitalización y
   cuidados perioperatorios.
2. **Autonomía, cuidados cotidianos y entorno seguro.** Higiene, sueño, actividades diarias,
   cuidado domiciliario, dependencia funcional, prevención y atención de caídas, calidad del
   cuidado, institucionalización y prevención del maltrato.
3. **Alimentación, hidratación y salud digestiva.** Nutrición general, alimentación para
   hipertensión, hidratación, estreñimiento, fecaloma, deglución, higiene alimentaria y cuidados
   de enfermería relacionados.
4. **Movimiento, movilidad y capacidad funcional.** Actividad física, estiramientos, fuerza,
   equilibrio, coordinación, motricidad, yoga en silla, adaptaciones y mantenimiento de la
   independencia.
5. **Memoria, bienestar y relaciones humanas.** Memoria, atención, estimulación cognitiva,
   depresión, comunicación, familia, cuidadores, espiritualidad, dignidad, envejecimiento positivo
   y decisiones éticas en demencia.

Cada resumen conserva referencias al archivo y a la página física del PDF original. Los resúmenes
ayudan a localizar el tema; las fuentes originales siguen siendo la evidencia canónica cuando están
disponibles en la colección local. La ingesta omite sus dos páginas iniciales de portada y metadatos
para que las respuestas recuperen contenido sustantivo.

Los archivos Markdown recopilados en `docs/` se usan únicamente como contexto editorial para crear
las síntesis. AAMIA no los descubre, no los indexa y la carga pública continúa aceptando solo PDF.

Para regenerar los cinco documentos:

```bash
python scripts/create_thematic_summaries.py
```

Para comprobar la colección local:

```bash
python -m eldercare_agent.cli --stats
```
