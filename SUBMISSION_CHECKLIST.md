# Checklist de entrega

## Código y GitHub

- [x] Aplicación funcional en local.
- [x] Ingesta de PDF, recuperación, fuentes y fallback.
- [x] README, arquitectura, ejecución y ejemplos.
- [x] Pruebas, lint, Docker y CI.
- [ ] Conectar esta carpeta con el repositorio público de GitHub.
- [ ] Crear el commit final y hacer `push`.
- [ ] Confirmar que GitHub Actions termine en verde.
- [ ] Verificar que ningún secreto o PDF sin permiso de redistribución esté publicado.

## Oracle Cloud

- [ ] Crear repositorio en OCIR.
- [ ] Construir y publicar la imagen con `deploy/oci/prepare-image.ps1`.
- [ ] Crear una OCI Container Instance o una VM Compute.
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
