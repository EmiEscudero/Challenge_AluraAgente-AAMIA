# 🌿 AAMIA — Apoyo al Adulto Mayor IA

Agente RAG en español para consultar una biblioteca documental sobre cuidado de personas adultas mayores: cuidados iniciales y cotidianos, alimentación, actividad física, movilidad, memoria y bienestar general.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![Deploy](https://img.shields.io/badge/Deploy-Streamlit_Cloud-FF4B4B?logo=streamlit&logoColor=white)
![Tests](https://img.shields.io/badge/tests-14_passed-1f7a5c)

🌐 **[Abrir AAMIA en Streamlit Cloud](https://challenge-alura-gente-aamia.streamlit.app/)**

> **Aviso:** AAMIA ofrece información educativa basada en los documentos cargados. No diagnostica, no prescribe y no sustituye una valoración médica. Ante una posible urgencia, indica contactar inmediatamente a los servicios de emergencia locales.

## Demostración

[![Ver la demostración de AAMIA en YouTube](https://i.ytimg.com/vi/m-19G62AS6g/hqdefault.jpg)](https://youtu.be/m-19G62AS6g)

El video muestra una consulta real ejecutada en Docker: AAMIA recibe la pregunta, recupera evidencia de la biblioteca y presenta los documentos y páginas PDF utilizados.

▶️ **[Reproducir la demostración completa en YouTube](https://youtu.be/m-19G62AS6g)**

## Problema y objetivo

Familiares, cuidadores y equipos de apoyo suelen tener que buscar información en manuales extensos y dispersos. AAMIA transforma una colección de PDF en una biblioteca conversacional: recibe una pregunta, recupera los fragmentos más relevantes, construye una respuesta y muestra el documento y la página PDF utilizados.

El objetivo del proyecto es facilitar el acceso a información documental sin ocultar su procedencia ni convertir al agente en sustituto de profesionales de salud.

## Funcionalidades

- Descubrimiento automático de todos los PDF dentro de `docs/`.
- Carga de hasta 5 PDF de 15 MB cada uno para crear una biblioteca BM25 temporal y aislada por sesión.
- Extracción por página, limpieza de texto y fragmentación con solapamiento.
- Recuperación BM25 local con expansión de términos del dominio y reranking por diversidad.
- Respuestas respaldadas por fuentes, título del documento y página PDF.
- Modo local funcional sin API key y generación opcional con OpenAI u OCI Generative AI.
- Rechazo explícito de preguntas fuera del alcance documental.
- Aviso prioritario ante frases que podrían describir una urgencia.
- Protección básica frente a prompt injection proveniente de los documentos.
- Historial de conversación durante la sesión y retroalimentación positiva/negativa.
- Auditoría en JSON Lines con hashes y metadatos; el contenido se excluye por defecto.
- Índice persistente y reconstrucción automática cuando cambian los PDF.
- Docker, Docker Compose, health check, CI y guía de despliegue en OCI.

## Resultado de la ingesta real

La validación local utilizó los 19 PDF de trabajo más la guía abierta incluida en el repositorio. El despliegue creado directamente desde GitHub inicia con la guía abierta y permite que cada visitante cargue sus propios documentos temporalmente.

| Métrica | Resultado |
|---|---:|
| Documentos PDF | 20 (19 locales + 1 guía abierta del proyecto) |
| Páginas revisadas | 3,059 |
| Páginas con texto indexadas | 2,818 |
| Páginas vacías o solo imagen omitidas | 241 |
| Fragmentos consultables | 4,366 |
| Errores de ingesta | 0 |

## Arquitectura

```mermaid
flowchart LR
    A["PDF en docs/ o carga temporal"] --> B["Extracción por página con pypdf"]
    B --> C["Limpieza y chunking con metadatos"]
    C --> D["Índice BM25 persistente"]
    Q["Pregunta en Streamlit"] --> S["Filtro de alcance y urgencias"]
    S --> R["Recuperación + expansión + reranking"]
    D --> R
    R --> G{"Proveedor configurado"}
    G -->|Sin credenciales| E["Respuesta extractiva"]
    G -->|OpenAI| O["Responses API"]
    G -->|OCI| I["OCI Generative AI Responses API"]
    E --> U["Respuesta, fuentes y páginas"]
    O --> U
    I --> U
    U --> L["Auditoría JSONL y feedback"]
```

La recuperación es local y barata: no requiere descargar modelos ni una base vectorial externa. El proveedor generativo recibe únicamente los fragmentos seleccionados y un prompt que exige responder desde el contexto, citar fuentes y reconocer cuando falta información.

## Cómo se procesa una pregunta

1. Al iniciar, `pypdf` extrae el texto de cada página, lo limpia y lo divide en fragmentos con metadatos.
2. Los fragmentos se guardan en un índice BM25 comprimido dentro de `data/index/`.
3. La pregunta pasa por los filtros de alcance y posibles urgencias.
4. BM25 recupera los fragmentos con mayor coincidencia y el reranker selecciona hasta cinco fuentes distintas.
5. El proveedor configurado construye la respuesta y la interfaz muestra sus fuentes y páginas.

Con la configuración predeterminada `LLM_PROVIDER=extractive` no se ejecuta un modelo de lenguaje. El sistema puntúa las oraciones recuperadas por coincidencia con la pregunta y presenta las tres más relevantes. Esto evita API keys y costo por consulta, aunque la redacción es menos natural que la de un LLM.

## Tecnologías

- **Python 3.12**: aplicación y pipeline.
- **pypdf**: extracción de texto y metadatos por página.
- **BM25**: búsqueda local eficiente con índice comprimido.
- **Streamlit**: interfaz web conversacional.
- **OpenAI SDK / Responses API**: adaptador generativo opcional. El modelo económico predeterminado es `gpt-5.6-luna`, configurable por entorno. Consulta la [guía oficial de modelos](https://developers.openai.com/api/docs/guides/latest-model).
- **OCI Generative AI**: proveedor opcional mediante su endpoint compatible con OpenAI.
- **Docker y OCI Compute Ampere A1**: empaquetado y despliegue compatible con la capa Always Free.
- **GitHub Actions + Ruff + unittest**: integración continua y calidad.

## Estructura

```text
.
├── app.py                         # Interfaz Streamlit
├── eldercare_agent/
│   ├── ingestion.py              # Extracción, limpieza y fragmentación
│   ├── retriever.py              # Índice BM25 y reranking
│   ├── uploads.py                # Corpus temporal aislado por sesión
│   ├── llm.py                    # Modos extractivo, OpenAI y OCI
│   ├── service.py                # Orquestación del agente
│   ├── safety.py                 # Alcance, urgencias y aviso médico
│   └── audit.py                  # Trazabilidad y feedback
├── docs/                          # Base documental
├── scripts/                       # Indexación y smoke test
├── tests/                         # Pruebas unitarias
├── deploy/oci/                    # Automatización y guía OCI
├── evidence/                      # Evidencia visual local
├── Dockerfile
└── compose.yaml
```

## Ejecución local

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

### Linux o macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Abre <http://localhost:8501>. En el primer arranque, la aplicación construye `data/index/bm25-index.json.gz`. Con la colección incluida localmente tomó aproximadamente un minuto; los siguientes arranques cargan el índice existente.

Desde la barra lateral también puedes cargar hasta 5 PDF de 15 MB cada uno. La aplicación construye un índice BM25 separado para esa sesión; al volver a la biblioteca pública o finalizar la sesión, elimina los archivos y el índice temporal. Los PDF escaneados sin una capa de texto requieren OCR previo.

También puedes usar la terminal:

```bash
python -m eldercare_agent.cli --stats
python -m eldercare_agent.cli "¿Cómo debe organizarse una sesión de actividad física?"
python scripts/smoke_test.py
```

## Configuración del modelo

El despliegue gratuito descrito en este repositorio usa:

```dotenv
LLM_PROVIDER=extractive
```

Este modo no llama a OpenAI ni a OCI Generative AI. Si se configura un proveedor generativo, BM25 sigue haciendo la recuperación y únicamente los fragmentos seleccionados se envían al modelo:

Para obtener respuestas redactadas y sintetizadas con OpenAI:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=<secreto>
OPENAI_MODEL=gpt-5.6-luna
```

Para ejecutar la generación dentro del ecosistema OCI:

```dotenv
LLM_PROVIDER=oci
OCI_GENAI_API_KEY=<secreto>
OCI_GENAI_REGION=us-chicago-1
OCI_GENAI_PROJECT=ocid1.generativeaiproject...
OCI_GENAI_MODEL=openai.gpt-oss-120b
```

OCI recomienda Responses API para aplicaciones nuevas y permite utilizar el SDK de OpenAI con un endpoint de OCI; consulta su [QuickStart oficial](https://docs.oracle.com/en-us/iaas/Content/generative-ai/get-started-agents.htm).

Nunca publiques `.env`, API keys, tokens de OCIR ni llaves privadas. El repositorio ya los excluye.

## Ejemplos verificados

**Pregunta:** ¿Cómo debe organizarse una sesión de actividad física?

**Respuesta local:** La biblioteca indica que una sesión tiene tres partes: inicial, principal y final o vuelta a la calma. La interfaz cita *Tercera edad: actividad física y salud*, páginas PDF 94 y 95.

**Pregunta:** ¿Qué recomendaciones hay sobre alimentación del adulto mayor?

**Respuesta local:** El agente recupera recomendaciones sobre una alimentación variada, apetecible y nutritiva, respetando las indicaciones médicas o nutricionales, y muestra los manuales y páginas consultados.

**Pregunta:** ¿Cuál es la capital de Francia?

**Respuesta:** “La pregunta parece estar fuera del alcance de esta biblioteca…” No se adjuntan fuentes ni se intenta inventar una respuesta.

## Pruebas y calidad

```bash
ruff check .
python -m unittest discover -s tests -v
```

Validaciones realizadas:

- 14 pruebas unitarias y de integración aprobadas.
- Smoke test sobre alimentación, actividad física, memoria, caídas y una pregunta fuera de alcance.
- Health check local: `/_stcore/health` responde `200 ok`.
- Prueba de interfaz en navegador a 1440 × 1100, incluida la carga de un PDF y una consulta BM25 con fuentes.
- Ingesta completa de los 20 PDF sin errores.

## Docker

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

La imagen corre como usuario sin privilegios, expone el puerto `8501` y tiene health check. Los volúmenes conservan el índice y los logs. El build incorpora los PDF que existan en `docs/`.

## Despliegue

La aplicación está publicada en **[Streamlit Community Cloud](https://challenge-alura-gente-aamia.streamlit.app/)** desde la rama `main`. El despliegue utiliza `app.py`, `requirements.txt` y `.streamlit/config.toml` directamente desde este repositorio.

### Oracle Cloud

La ruta recomendada para mantener costo cero es una VM **OCI Compute VM.Standard.A1.Flex** con 1 OCPU y 6 GB de RAM, Ubuntu y Docker Compose. No requiere OCI Generative AI: deja `LLM_PROVIDER=extractive` para evitar consumo de APIs pagadas. La guía desde la creación de la cuenta hasta la validación pública está en [deploy/oci/README.md](deploy/oci/README.md).

## Seguridad, privacidad y límites

- Las respuestas dependen de la calidad y vigencia de los documentos.
- Las páginas sin texto OCR se omiten; para una colección totalmente escaneada debe agregarse OCR.
- Las cargas están limitadas a 5 PDF de 15 MB cada uno y permanecen en almacenamiento temporal aislado por sesión.
- No deben cargarse expedientes clínicos ni documentos con datos personales o sensibles.
- El modo extractivo es deliberadamente conservador y puede conservar rasgos de redacción del documento.
- Las citas usan el número de página física del PDF, que puede diferir de la numeración impresa.
- La detección de urgencias es preventiva, no un sistema de triaje clínico.
- `LOG_CONTENT=false` evita guardar preguntas y respuestas completas. Actívalo solo con una política de privacidad adecuada.

Consulta [SECURITY.md](SECURITY.md) para reportar vulnerabilidades y revisar las medidas implementadas.

## Evidencia del desarrollo

- [Pantalla inicial local](evidence/local-app.png)
- [Respuesta local con fuentes](evidence/local-answer.png)
- [Detalle local de documentos y páginas](evidence/local-answer-sources.png)

## Licencia

El código se distribuye bajo licencia MIT. La guía de AAMIA incluida en `docs/` se distribuye bajo CC BY 4.0.
