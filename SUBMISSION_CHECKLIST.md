# Checklist de entrega

## Código y GitHub

- [x] Aplicación funcional en local.
- [x] Ingesta de PDF, recuperación, fuentes y fallback.
- [x] README, arquitectura, ejecución y ejemplos.
- [x] Pruebas, lint, Dockerfile y CI.
- [x] Conectar esta carpeta con el repositorio público de GitHub.
- [x] Crear el commit inicial y hacer `push` a `main`.
- [x] Confirmar que [GitHub Actions #2](https://github.com/EmiEscudero/Challenge_AluraAgente-AAMIA/actions/runs/30292940897) termine en verde, incluida la construcción Docker.
- [x] Verificar que ningún secreto o PDF aportado sin permiso de redistribución esté publicado.

## Oracle Cloud

- [ ] Crear una VM Compute `VM.Standard.A1.Flex` Always Free (1 OCPU, 6 GB).
- [ ] Clonar el repositorio y ejecutar `deploy/oci/bootstrap.sh`.
- [ ] Abrir TCP 8501 en el NSG únicamente para la demostración.
- [ ] Confirmar `/_stcore/health` = `ok` desde la URL pública.
- [ ] Probar alimentación, ejercicio y pregunta fuera de alcance.
- [ ] Guardar `evidence/oci-running.png` y `evidence/oci-app.png`.
- [ ] Sustituir `PENDIENTE_URL_OCI` en `README.md`.

## Alura

- [ ] Abrir el repositorio en una ventana privada y confirmar que sea público.
- [ ] Revisar código, README y evidencias desde GitHub.
- [ ] Enviar la URL correcta del repositorio.
- [ ] Descargar el badge antes de finalizar el envío.
