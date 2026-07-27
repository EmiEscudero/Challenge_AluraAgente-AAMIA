# Seguridad

## Datos y alcance

AAMIA es una herramienta educativa, no un dispositivo médico. No debe recibir expedientes clínicos, identificadores personales ni secretos. La persona responsable del despliegue debe revisar las licencias y la sensibilidad de cada PDF.

## Medidas implementadas

- Secretos cargados desde variables de entorno y excluidos de Git y Docker.
- Contenedor ejecutado con usuario sin privilegios.
- Respuestas restringidas al contexto recuperado.
- Los documentos se delimitan como contenido no confiable para reducir prompt injection.
- Preguntas fuera de alcance se rechazan sin enviar contexto al proveedor.
- Registro de hashes y metadatos por defecto (`LOG_CONTENT=false`).
- Límite de 2,000 caracteres por pregunta y contexto máximo enviado al modelo.
- Health check y dependencias acotadas por versión mayor.

## Producción

- Termina TLS en un OCI Load Balancer o proxy inverso.
- Limita el puerto 8501 a los orígenes necesarios.
- Guarda secretos en OCI Vault o en variables protegidas del servicio.
- Usa IAM/Resource Principal cuando el entorno lo permita.
- Revisa y actualiza dependencias regularmente.
- No habilites logs de contenido sin consentimiento, retención definida y controles de acceso.

## Reporte de vulnerabilidades

No publiques credenciales ni datos sensibles en un issue. Contacta de forma privada a la persona propietaria del repositorio con una descripción, impacto y pasos mínimos de reproducción.
