# Biblioteca documental

AAMIA descubre recursivamente los archivos `*.pdf` de esta carpeta, conserva el nombre del documento y la página PDF como metadatos, y reconstruye el índice cuando detecta cambios.

El repositorio incluye `AAMIA_guia_abierta_para_el_cuidado.pdf` como base documental inicial.

Para comprobar la colección local:

```bash
python -m eldercare_agent.cli --stats
```
