# Biblioteca documental

Coloca en esta carpeta los PDF autorizados que utilizará AAMIA. La aplicación descubre todos los archivos `*.pdf` de manera recursiva, conserva el nombre del documento y la página PDF como metadatos, y reconstruye el índice cuando detecta cambios.

Antes de compartir cualquier documento, consulta [COPYRIGHT_AUDIT.md](COPYRIGHT_AUDIT.md). Que un PDF pueda descargarse de Internet no significa que tenga una licencia abierta para volver a publicarlo.

Los PDF entregados originalmente no se publican automáticamente porque algunos parecen ser libros protegidos por derechos de autor. Solo debes subir a un repositorio público aquellos documentos cuya licencia permita redistribución. El `Dockerfile` sí incorpora los PDF presentes localmente al construir una imagen, por lo que puedes desplegar una biblioteca que estés autorizado a usar sin exponer los archivos en GitHub.

Para comprobar la colección local:

```bash
python -m eldercare_agent.cli --stats
```
