# Desplegar AAMIA en OCI sin salir de Always Free

Esta es la ruta más sencilla y predecible para una primera entrega: **una VM OCI Compute Ampere A1 con Ubuntu + Docker Compose**. No necesitas publicar una imagen en un registry ni activar una API de IA pagada.

## 0. Costo y límites que debes respetar

Puedes mantener este despliegue en **$0 USD** si la consola muestra la etiqueta **Always Free-eligible** y no superas los límites. La configuración de esta guía usa:

| Recurso | Configuración de AAMIA | Límite Always Free documentado |
|---|---:|---:|
| VM Ampere A1 | 1 OCPU, 6 GB RAM | 2 OCPU, 12 GB RAM en total |
| Boot volume | 50 GB | 200 GB entre boot y block volumes |
| Región | Home region | Compute Always Free sólo en home region |
| Modelo generativo | Desactivado (`extractive`) | No consume OpenAI ni OCI Generative AI |

Al crear la cuenta, Oracle ofrece además **USD 300 por hasta 30 días** como prueba promocional. No confundas esos créditos temporales con Always Free. La tarjeta normalmente se pide para verificar identidad; puede aparecer una retención pequeña y temporal, pero Oracle indica que no realiza cargos a menos que elijas actualizar la cuenta a modalidad pagada.

Documentación oficial: [OCI Free Tier](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm) y [recursos Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm).

## 1. Crear la cuenta de OCI

1. Abre [signup.oraclecloud.com](https://signup.oraclecloud.com).
2. Selecciona México, escribe tu nombre y correo, completa el CAPTCHA y verifica el mensaje que recibas.
3. Crea la contraseña y el nombre de la cuenta cloud.
4. Elige con cuidado la **Home Region**. No se puede cambiar después. Para México aparecen:
   - **Mexico Central (Queretaro):** `mx-queretaro-1`.
   - **Mexico Northeast (Monterrey):** `mx-monterrey-1`.
5. Usa la región más conveniente para ti. La capacidad A1 gratuita puede agotarse temporalmente en cualquiera de ellas.
6. Ingresa domicilio y teléfono.
7. Agrega una tarjeta de crédito o débito Visa/Mastercard que no requiera PIN. Las tarjetas prepagadas pueden rechazarse.
8. Acepta los términos e inicia la prueba gratuita. **No pulses “Upgrade”** si quieres mantener una cuenta sólo gratuita.

La guía oficial de registro está en [Sign Up for the Free Oracle Cloud Promotion](https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/signingup_topic-Sign_Up_for_Free_Oracle_Cloud_Promotion.htm).

## 2. Crear la VM gratuita

1. Entra a la consola de OCI y confirma arriba a la derecha que estás en tu **Home Region**.
2. Abre el menú ☰ y entra a **Compute > Instances**.
3. Pulsa **Create instance**.
4. Nombre: `aamia`.
5. En **Image and shape**, pulsa **Edit**:
   - Imagen: **Canonical Ubuntu 24.04** o la versión Ubuntu marcada como Always Free elegible.
   - Shape: **Ampere** > `VM.Standard.A1.Flex`.
   - OCPU: `1`.
   - Memory: `6 GB`.
6. En **Networking**:
   - Si es tu primera VM, permite crear una VCN y subred nuevas.
   - Selecciona una **public subnet**.
   - Activa **Assign a public IPv4 address**.
7. En **Add SSH keys**, elige **Generate a key pair for me** y descarga la llave privada. Guárdala; OCI no vuelve a mostrarla.
8. Deja el boot volume en `50 GB` y no agregues volúmenes de pago.
9. Revisa que la forma muestre **Always Free-eligible** y pulsa **Create**.
10. Espera a que el estado sea **Running** y copia la **Public IPv4 address**.

Si aparece `Out of host capacity`, no significa que hiciste algo mal. Oracle recomienda intentar otro availability domain cuando exista o volver a intentar más tarde. Las regiones mexicanas tienen un solo availability domain, así que normalmente toca reintentar.

## 3. Abrir el puerto 8501 en OCI

1. Desde los detalles de la instancia, abre la **Primary VNIC**.
2. Abre la **Subnet** y luego su **Security List**. Si elegiste un NSG al crear la VM, abre ese NSG.
3. Pulsa **Add Ingress Rules** y crea:
   - Source CIDR: `0.0.0.0/0` para la demostración pública.
   - IP Protocol: `TCP`.
   - Destination Port Range: `8501`.
   - Description: `AAMIA Streamlit`.
4. Conserva también la regla SSH del puerto `22`.

Para una prueba de challenge, `0.0.0.0/0` permite que el jurado abra la app. En un uso real, agrega HTTPS y limita el origen.

## 4. Conectarte desde Windows PowerShell

Abre PowerShell en la carpeta donde descargaste la llave. Sustituye el nombre del archivo y la IP:

```powershell
ssh -i .\ssh-key-aamia.key ubuntu@<IP_PUBLICA>
```

La primera vez escribe `yes`. Si Windows indica que la llave tiene permisos demasiado abiertos, ejecuta:

```powershell
icacls .\ssh-key-aamia.key /inheritance:r
icacls .\ssh-key-aamia.key /grant:r "$($env:USERNAME):(R)"
```

No compartas ni subas la llave privada al repositorio.

## 5. Clonar y arrancar AAMIA

Ya dentro de la VM, ejecuta cada bloque:

```bash
sudo apt-get update
sudo apt-get install -y git
git clone https://github.com/EmiEscudero/Challenge_AluraAgente-AAMIA.git
cd Challenge_AluraAgente-AAMIA
cp .env.example .env
```

La configuración incluida ya usa `LLM_PROVIDER=extractive`: funciona sin API key y sin consumo de un modelo pagado. Después instala Docker y arranca el servicio:

```bash
chmod +x deploy/oci/bootstrap.sh
./deploy/oci/bootstrap.sh
```

El primer build puede tardar varios minutos. El primer arranque construye el índice documental.

## 6. Permitir el puerto en Ubuntu

En la misma sesión SSH:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 8501/tcp
sudo ufw --force enable
```

Después valida localmente:

```bash
curl http://127.0.0.1:8501/_stcore/health
sudo docker compose ps
```

El health check debe responder `ok` y el contenedor debe aparecer `healthy` después del periodo de inicio.

## 7. Abrir la aplicación

En tu navegador visita:

```text
http://<IP_PUBLICA>:8501
```

Prueba estas preguntas:

- `¿Qué aspectos debo observar al comenzar el cuidado diario?`
- `¿Cómo puedo hacer más seguro el hogar?`
- `¿Qué recomienda la guía sobre actividad física?`
- `¿Cuál es la capital de Francia?` — debe rechazarla por estar fuera de alcance.

## 8. Actualizar después de un cambio en GitHub

```bash
cd ~/Challenge_AluraAgente-AAMIA
git pull --ff-only
sudo docker compose up --detach --build
sudo docker compose ps
```

Para ver errores:

```bash
sudo docker compose logs --tail=200 aamia
```

Para reiniciar:

```bash
sudo docker compose restart aamia
```

## 9. Mantenerte en la capa gratuita

- Confirma la etiqueta **Always Free-eligible** antes de crear cualquier recurso.
- Mantén como máximo **2 OCPU y 12 GB de RAM A1 en total**; esta guía usa la mitad.
- Mantén los volúmenes de boot y block dentro de **200 GB** y en la home region.
- No actives OCI Generative AI para esta entrega si tu prioridad es costo cero. El modo extractivo ya cumple el flujo RAG.
- No crees servicios “por probar” durante el trial: si no son Always Free, dejarán de existir al terminar los créditos o pueden costar si actualizas la cuenta.
- Las instancias Always Free consideradas inactivas durante siete días pueden ser reclamadas por Oracle. La [documentación de Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) explica los umbrales actuales.
- En **Governance & Administration > Limits, Quotas and Usage** puedes revisar el consumo de la tenancy.

## 10. Evidencias para la entrega

Guarda al menos:

1. Captura de **Compute Instance Details** con `aamia`, estado `Running`, shape A1 y la IP pública.
2. Captura de AAMIA abierta desde la IP pública.
3. Captura de una respuesta con sus fuentes y páginas.
4. Captura de `docker compose ps` mostrando `healthy`.
5. URL pública escrita en el README sustituyendo `PENDIENTE_URL_OCI`.

## Solución rápida de problemas

| Problema | Revisión |
|---|---|
| No conecta por SSH | IP pública, regla TCP 22, usuario `ubuntu` y llave correcta |
| Navegador no abre 8501 | Regla OCI 8501 + `sudo ufw status` + `docker compose ps` |
| Contenedor reinicia | `sudo docker compose logs --tail=200 aamia` |
| App dice que no hay PDF | Confirma que `docs/AAMIA_guia_abierta_para_el_cuidado.pdf` existe después del clone |
| `Out of host capacity` | Reintenta más tarde; no cambies a una shape pagada por accidente |

Guía oficial de instancias Compute: [Launching an instance](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm).
