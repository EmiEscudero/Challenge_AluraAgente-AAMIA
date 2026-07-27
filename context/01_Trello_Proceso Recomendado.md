## Trello - Proceso recomendado

### 0. Crea tu repositorio de Proyectos en GitHub
Git y GitHub son herramientas muy útiles para cualquier desarrollador, por lo que debes acostumbrarte a trabajar con ellas.

En este desafío queremos proponerte que el primer paso sea la creación de este repositorio en GitHub. Aunque todavía no hayas desarrollado nada de código, lo importante es que tengas al menos una carpeta específica para tu proyecto y que puedas ir actualizándolo gradualmente.

### 1. Colecta y organización de documentos
La recolección y organización de los documentos es el punto de partida de todo el proyecto: antes de procesar, indexar o buscar cualquier cosa, es necesario saber exactamente qué documentos existen, dónde están y quién es responsable de ellos.

Es una etapa más organizacional que técnica, pero que determina la calidad de todo lo que viene después.

1. Mapeo de las fuentes
El primer paso es descubrir dónde están hoy los documentos relevantes, ya que en una empresa suelen estar dispersos en:

Carpetas compartidas (Google Drive, SharePoint, OneDrive)

Sistemas internos (sistema de Recursos Humanos)

Repositorios de código (para documentación técnica)

Correos electrónicos archivados

Incluso carpetas locales en computadoras de personas clave.

Este mapeo generalmente requiere hablar con cada área (RH, Financiero, Jurídico, etc.) para entender dónde guardan sus documentos oficiales.

2. Definición de categorías
Los documentos se organizan en las categorías de negocio que tengan sentido para la empresa —como las sugeridas al inicio del proyecto (RH, Financiero, Operacional, Legal, etc.).

Esta categorización no es solo cosmética: se convierte en un metadato que se utilizará después para filtrar búsquedas y para definir a los responsables de mantener actualizado ese conjunto de documentos.

3. Curaduría de calidad
No todo documento encontrado debe ingresar a la base. En esta fase es importante filtrar:

Versiones desactualizadas o borradores (manteniendo solo la versión oficial vigente de una política, por ejemplo);

Documentos duplicados o redundantes;

Contenido irrelevante para preguntas de los colaboradores (como anotaciones personales o archivos de prueba).

4. Definición de responsables (ownership)
Cada categoría de documentos debe tener un responsable dentro de la empresa —generalmente alguien de la propia área (RH se encarga de los documentos de RH, el área Jurídica se encarga de contratos y compliance).

Esta persona es quien aprueba lo que entra a la base y a quien se le debe avisar cuando el contenido necesite una actualización.

5. Acceso y permisos
Como se definió en el proyecto, el agente está abierto a todos los colaboradores, por lo que aquí el enfoque no es restringir quién puede preguntar, sino garantizar que el agente tenga acceso de lectura a los lugares correctos (carpetas, sistemas) para buscar y actualizar los documentos automáticamente, sin depender del envío manual de archivos.

6. Proceso de ingesta inicial
Por último, se define cómo llegarán esos documentos al pipeline de procesamiento (etapa 2):

Vía conexión directa con la fuente (por ejemplo, la API de Google Drive o SharePoint);

Carga (upload) manual inicial para comenzar el proyecto;

O una combinación de ambas opciones mientras se construye la integración automática.

Por qué esta etapa importa tanto
Si esta base se estructura de forma deficiente —con documentos desactualizados, mal categorizados o sin un responsable definido— todo el resto del pipeline (procesamiento, indexación, búsqueda, generación de respuesta) heredará ese problema.

Es el principio de "garbage in, garbage out" (si entra basura, sale basura): la IA solo puede ser tan confiable como los documentos de los que se alimenta.

### 2. Proceso y extracción de contenido
El procesamiento y extracción de contenido es la fase responsable de transformar los documentos originales —en sus variados formatos— en texto limpio y estructurado, listo para ser convertido en embeddings en la siguiente etapa. Funciona más o menos así:

1. Extracción por formato
Cada tipo de archivo exige un enfoque diferente:

PDF: extracción de texto directo cuando el PDF es nativo (generado digitalmente); cuando es un documento escaneado (imagen), es necesario utilizar OCR (reconocimiento óptico de caracteres) para convertir la imagen en texto.

Word: extracción del texto corrido, preservando la estructura como títulos y párrafos, ya que esto ayuda a mantener el sentido al dividir el contenido posteriormente.

Excel: conversión de las tablas en texto estructurado (por ejemplo, línea por línea, con encabezados de columna repetidos), ya que las planillas tienen una lógica diferente a la del texto corrido.

PowerPoint: extracción del texto de cada diapositiva (slide), generalmente junto con las notas del orador, que suelen contener contexto adicional importante.

Markdown, CSV, JSON, HTML: formatos que ya son estructurados o semiestructurados y que requieren principalmente eliminar marcas técnicas (etiquetas HTML, sintaxis Markdown) manteniendo el contenido legible, o convertir la estructura de datos (JSON, CSV) en frases o tablas comprensibles.

2. Limpieza del texto
Eliminación de ruidos que no aportan significado: encabezados y pies de página repetidos, numeración de páginas, caracteres especiales de formato, espacios duplicados o fragmentos corrompidos de la extracción (común en PDFs mal formateados).

3. Chunking (división en fragmentos)
El texto extraído se divide en partes más pequeñas (chunks), ya que los documentos completos suelen ser demasiado grandes para caber en el contexto de búsqueda y del LLM. Algunas estrategias comunes son:

División por tamaño fijo (por ejemplo, de 500 a 1000 caracteres), con una pequeña superposición (overlap) entre fragmentos para no cortar una idea por la mitad;

División por estructura lógica del documento (por sección, por párrafo, por diapositiva), lo que tiende a preservar mejor el sentido completo de cada fragmento.

4. Atribución de metadatos
Cada fragmento recibe información que se utilizará después para el filtrado y la citación de fuentes: categoría del documento (RH, Financiero, etc.), nombre del archivo original, fecha de creación o última actualización, autor o responsable, y la ubicación exacta dentro del documento (página, sección o diapositiva).

Por qué esta etapa es crítica
La calidad de la extracción y del chunking es crítica: los errores en esta etapa perjudican la búsqueda y pueden generar respuestas incompletas o incorrectas, incluso si el resto del pipeline está bien construido.

### 3. Indexación
La indexación vectorial es el proceso de transformar el texto extraído de los documentos en representaciones numéricas que capturan su significado, y organizarlas de forma que puedan ser buscadas rápidamente por similitud semántica. Es lo que hace posible, en la etapa 4, encontrar fragmentos relevantes incluso cuando la pregunta del colaborador no utiliza exactamente las mismas palabras del documento.

Qué es un embedding
Un embedding es un vector de números (generalmente de algunas cientos o miles de dimensiones) generado por un modelo de lenguaje entrenado específicamente para eso.

Los textos con significados parecidos generan vectores numéricamente próximos en el espacio vectorial, incluso si usan palabras diferentes. Por ejemplo, "política de reembolso de gastos" y "cómo solicitar el resarcimiento de costos" tienden a generar vectores cercanos porque tratan sobre el mismo tema.

Cómo funciona en este proyecto, paso a paso:
 

Entrada: Cada fragmento (chunk) de texto generado en la etapa 2 (ya limpio y con sus metadados asociados) se envía a un modelo de embedding.

Generación del vector: El modelo devuelve un vector numérico que representa ese fragmento. Este mismo modelo se debe utilizar de forma consistente tanto para los documentos como para las preguntas de los colaboradores, ya que los vectores generados por modelos diferentes no son comparables entre sí.

Almacenamiento: El vector se guarda en una base de datos vectorial junto con una referencia al texto original y a los metadados (categoría, nombre del archivo, fecha, autor). Considerando los formatos y contextos de la empresa, las opciones comunes incluyen Pinecone, Weaviate, Qdrant, Chroma o pgvector (extensión de PostgreSQL).

Indexación para una búsqueda eficiente: La base de datos vectorial organiza estos vectores en una estructura de índice (como HNSW — Hierarchical Navigable Small World) que permite encontrar los vectores más cercanos a una consulta sin necesidad de compararlos uno por uno con todos los vectores almacenados, lo cual sería inviable a medida que la base de documentos crece.

Indexación paralela de metadados: Además de la búsqueda vectorial, los metadados se indexan de forma tradicional (como en cualquier base de datos), lo que permite aplicar filtros —por ejemplo, restringir la búsqueda a documentos de la categoría "Financiero" creados en los últimos 12 meses, incluso antes de calcular la similitud semántica.

Por qué importa esto
La indexación vectorial unifica documentos de diferentes formatos y categorías en un espacio de búsqueda común, permitiendo que una sola pregunta realice la búsqueda en toda la base, mientras que los metadados garantizan la posibilidad de restringir esa búsqueda a un contexto específico cuando sea necesario.


### 4. Camada de recuperación (RAG)
La capa de recuperación es el corazón del RAG: es la que decide qué fragmentos de documentos se le entregarán al LLM para generar la respuesta. Funciona en algunas fases:

1. Transformación de la pregunta en embedding
Cuando el colaborador hace una pregunta, su texto pasa por el mismo modelo de embedding utilizado en la indexación de los documentos, generando un vector numérico que representa el significado semántico de la consulta.

2. Búsqueda semántica en la base de datos vectorial
Este vector se compara con los vectores de todos los fragmentos de documentos ya indexados, utilizando una métrica de similitud (generalmente similitud de coseno o distancia euclidiana).

La base de datos vectorial devuelve los $N$ fragmentos más cercanos semánticamente —no necesariamente los que contienen las mismas palabras, sino los que tratan sobre el mismo tema. Esto es lo que permite que una pregunta como "¿cuántos días de vacaciones tengo?" encuentre un fragmento que habla de la "política de licencia remunerada", incluso sin usar la palabra "vacaciones".

3. Filtrado por metadados
Antes o después de la búsqueda semántica, es común aplicar filtros utilizando los metadados definidos en la etapa 2 —por ejemplo, restringir la búsqueda únicamente a documentos de la categoría "RH" o a los más recientes, descartando versiones antiguas de una política ya revisada.

4. Reclasificación (Reranking)
La búsqueda vectorial inicial suele devolver un número mayor de candidatos (por ejemplo, los 20 fragmentos más cercanos) para luego pasarlos por un segundo modelo, más preciso pero más lento, llamado reranker.

Este modelo reevalúa cada candidato considerando la pregunta completa y reordena los resultados por relevancia real, reteniendo solo los más útiles (por ejemplo, los 3 a 5 mejores).

5. Ensamblaje del contexto
Los fragmentos finales seleccionados se organizan en un bloque de texto, junto con sus metadados de origen (documento, sección, fecha), formando el contexto que se insertará en el prompt enviado al LLM en la etapa de generación de respuesta.

Por qué importa la reclasificación (reranking)
La búsqueda vectorial pura es rápida pero puede traer resultados ligeramente fuera del objetivo, ya que mide la similitud general del significado.

El reranker corrige esto analizando la relación más detallada entre la pregunta y el fragmento, mejorando considerablemente la precisión final —es un equilibrio entre velocidad (búsqueda vectorial amplia) y calidad (reclasificación sobre un conjunto reducido).

### 5. Producción y validación de respuestas
El LLM recibe la pregunta más el contexto recuperado y genera una respuesta basada en los documentos, siempre indicando la fuente (nombre del archivo, sección o página). Cuando el contenido necesario no se encuentra, el agente debe informarlo claramente en lugar de inventar una respuesta.

1. Generación de la respuesta
Después de que la etapa de recuperación encuentra los fragmentos de documentos más relevantes para la pregunta, estos fragmentos se insertan en un prompt junto con la pregunta original y se envían al LLM.

El prompt generalmente instruye al modelo a responder únicamente con base en el contexto proporcionado, sin utilizar conocimiento externo, y a indicar claramente de qué documento se extrajo cada información.

2. Citación de la fuente
Para que la respuesta sea rastreable y verificable, el agente adjunta los metadados de origen: nombre del archivo, sección, página o fecha de actualización.

Esto permite que el colaborador confirme la información en el documento original, lo cual es especialmente importante en áreas sensibles como Legal, Financiero o RH.

3. Validación y control de alucinación
Para reducir el riesgo de que el modelo invente información, algunas técnicas comunes son:

Restringir al modelo a responder solo con base en el contexto recuperado, instruyéndolo a admitir cuando no lo sepa;

Comparar la respuesta generada con los fragmentos originales (verificación de consistencia), rechazando o regenerando respuestas que no tengan un respaldo claro en el contexto;

Definir un umbral de confianza en la búsqueda semántica: si ningún fragmento recuperado tiene la relevancia suficiente, el agente no intenta generar una respuesta.

4. Fallback (alternativa) cuando no hay respuesta
Cuando los documentos disponibles no cubren la pregunta, el agente debe informar esto explícitamente ("no encontré esta información en los documentos disponibles") en lugar de arriesgarse a dar una respuesta incorrecta, y puede sugerir ponerse en contacto con el área responsable (RH, Jurídico, etc.) o indicar que ese tipo de pregunta está fuera del alcance de la base de conocimiento.

Nota: Aquí debes revisar si los contactos de las áreas se encuentran en el banco de información conocido por el agente.

5. Formato final
Por último, la respuesta se estructura de forma clara para el colaborador, incluyendo normalmente un resumen directo seguido de las referencias a los documentos utilizados, lo cual puede variar según el canal (chat, correo electrónico, integración con Teams/Slack).


### 6. Implantación, interfaz y manutención
El agente necesita una interfaz accesible (por ejemplo, un chat web o integración con Slack o Teams).

Nota: Vale la pena recalcar que la interfaz no necesita tener un diseño ni un front-end profesional; este no es el enfoque del proyecto. Enfócate en una interfaz simple pero funcional, con eso es suficiente.

Construcción de la interfaz
La elección del canal depende de dónde trabajen ya los colaboradores en su día a día:

Chat web dedicado: Una página interna simple, que generalmente es la opción más rápida de implementar, con un campo de pregunta, historial de conversación y visualización de las fuentes citadas.

Integración con herramientas de comunicación: Un bot dentro de Microsoft Teams o Slack, que es la opción más natural cuando la empresa ya utiliza estas plataformas para el trabajo diario, evitando que el colaborador tenga que abrir un sistema adicional.

Plugin en sistemas existentes: Incorporar al agente como un widget dentro de la intranet corporativa o el portal de RH que ya exista.

Independientemente del canal, algunos elementos de la interfaz son importantes:

Indicación clara de que se está conversando con un agente de IA (no con una persona);

Visualización de las fuentes/documentos utilizados en cada respuesta;

Un botón de retroalimentación (feedback positivo/negativo) en cada respuesta;

Un historial de conversación para dar continuidad al contexto dentro de una sesión.

Mantenimiento continuo
Aquí entran los procesos que mantienen al agente relevante y confiable después del lanzamiento:

Pipeline de actualización de documentos: Siempre que un documento sea creado, modificado o eliminado en las fuentes originales, este pipeline debe detectar el cambio, reprocesar el archivo y actualizar el índice vectorial de forma automática (o mediante una rutina periódica, ya sea diaria o semanal).

Curaduría de contenido: Un responsable de cada categoría (RH, Financiero, etc.) debe revisar periódicamente si los documentos indexados siguen siendo la versión oficial, evitando, por ejemplo, que el agente responda con base en una política antigua.

Monitoreo de calidad: Hacer un seguimiento de métricas como la tasa de preguntas sin respuesta, la retroalimentación negativa de los colaboradores y el tiempo de respuesta, utilizando esta información para identificar vacíos en la base de documentos.

Ciclo de mejora: Las preguntas recurrentes que no tengan una buena respuesta pueden indicar la necesidad de añadir un nuevo documento a la base, y las respuestas mal evaluadas pueden señalar ajustes necesarios en el prompt o en la lógica de recuperación.

Actualización del modelo: Evaluar periódicamente si una nueva versión del LLM aporta mejoras en la calidad, realizando siempre pruebas antes de sustituir el modelo en producción.

Este ciclo de mantenimiento es lo que garantiza que el agente siga siendo confiable a medida que la empresa crece y los documentos cambian, en lugar de convertirse en un sistema desactualizado poco tiempo después de su lanzamiento.

Tenemos un articulo sobre Streamlit que puede ayudarte si escoges esa herramienta para mostrar la interfaz de tu proyecto: Streamlit: comparte tu aplicación de datos sin dolores de cabeza | Alura Cursos Online

### 7. Deploy en la nube - OCI
Con el agente validado localmente en los pasos anteriores, esta etapa cubre la publicación del sistema en Oracle Cloud Infrastructure, haciéndolo accesible para todos los colaboradores de forma estable y escalable. En este caso, se presentan sugerencias de configuraciones y servicios de OCI:

Contenerización: Empaquetar la aplicación (API del agente, lógica de RAG, dependencias) en una imagen de Docker, almacenada en OCI Container Registry (OCIR).

Compute: Optar entre OCI Compute (instancias de VM simples), Container Instances (ejecución de contenedores sin gestionar la VM) o OKE (Oracle Kubernetes Engine), para la orquestación con escalamiento automático según el volumen de preguntas.

Almacenamiento de documentos: Los archivos originales (PDF, Word, Excel, etc.) se guardan en OCI Object Storage, con control de acceso mediante políticas de IAM de OCI.

Base de datos vectorial: Puede hospedarse en Oracle Autonomous Database (que soporta búsqueda vectorial nativa) o en una solución vectorial dedicada que corra sobre Compute/OKE, manteniendo los embeddings sincronizados con los documentos de Object Storage.

Secretos y credenciales: Las llaves de API (del LLM, por ejemplo) y las cadenas de conexión se guardan en OCI Vault, de modo que nunca queden expuestas en variables de entorno abiertas.

Red y seguridad: Configuración de una Virtual Cloud Network (VCN) con subredes públicas/privadas, un Load Balancer (balanceador de carga) para distribuir las peticiones y Network Security Groups para controlar el tráfico permitido.

CI/CD: Pipeline (OCI DevOps o GitHub Actions) que compila la imagen, ejecuta pruebas y realiza el despliegue automático con cada actualización del código o de los documentos indexados.

¿Qué es el Deploy (Despliegue)?
En este contexto, es el proceso de poner el agente de IA en funcionamiento en un entorno real y accesible, en lugar de mantenerlo corriendo únicamente en la máquina del desarrollador (localmente) durante las pruebas.

Nota: Recuerda que no es obligatorio utilizar ninguna tecnología o servicio mencionado aquí. Sin embargo, es obligatorio usar al menos un servicio del ecosistema de OCI en este proceso de despliegue.

### 8. Registrar ejecución del proyecto
El registro de ejecución documenta lo que hace el agente en producción (o en pruebas), lo que permite la auditoría, la depuración y la mejora continua.

Recuerda que es necesario ejecutarlo en la nube y agregar cualquier archivo multimedia, ya sea foto o video, como registro de esta ejecución.

La forma de hacer esto cambia según el entorno:

Ejecución local
Cuando el agente corre en la máquina del desarrollador o en un servidor interno sin orquestación en la nube, el registro tiende a ser simple y directo:

Logs: Se graban en archivos locales, generalmente en formato JSON Lines, y contienen la pregunta, el contexto recuperado, la respuesta generada, la marca de tiempo (timestamp) y el tiempo de respuesta.

Gestionador de versiones: Uso de Git para el código y herramientas como DVC (Data Version Control) para rastrear las versiones de los documentos indexados y de los embeddings generados.

(Opcional) Monitoreo: Se puede realizar con un panel (dashboard) simple, leído directamente desde los archivos de log, sin necesidad de infraestructura adicional.

Ventajas: Bajo costo, control total sobre los datos, ideal para prototipos y POCs (Pruebas de Concepto). Limitaciones: No escala automáticamente, no cuenta con alta disponibilidad y la responsabilidad de los respaldos (backups) y la seguridad es manual.

Ejecución en la nube
Cuando el agente se despliega en un proveedor de nube o en una plataforma gestionada, el registro se vuelve más robusto y centralizado:

Logs: Centralizados en servicios como CloudWatch, Azure Monitor o Google Cloud Logging, lo que permite la búsqueda, retención configurable y alertas automáticas.

Gestionador de versiones: Registros de las versiones de los modelos, prompts, índices vectoriales y parámetros de cada ejecución, lo que posibilita comparar el rendimiento entre versiones.

(Opcional) Monitoreo: Paneles de observabilidad que acompañan métricas como la latencia, tasa de errores, costo por petición y uso de tokens, con alertas automáticas en caso de anomalías.

Ventajas: Escalabilidad automática, alta disponibilidad, integración nativa con pipelines de CI/CD y respaldos gestionados por el proveedor. Limitaciones: Costo recurrente, mayor complejidad de configuración y necesidad de gobernanza sobre datos sensibles que se transmiten externamente.

Nota: Ninguna tecnología o herramienta mencionada aquí é obligatoria, queda a tu criterio utilizarlas. La única obligación es registrar la ejecución en la nube.

En ambos casos, el objetivo final es el mismo: garantizar la trazabilidad (quién preguntó qué, qué documento se utilizó, qué respuesta se dio) y contar con datos suficientes para auditar decisiones y mejorar el agente con el tiempo.

## 9. Haz tu README
Uno de los pasos más importantes al participar en un proceso de selección es resolver un desafío propuesto por la empresa y, por lo general, esto debe estar descrito en el README.

¿Andas corto de tiempo? No te preocupes, aquí te ayudo con la traducción: ¿Y qué es el README? Es un archivo con extensión .md y es un documento que contiene la descripción del proyecto.

Ahora que estamos en la recta final del proyecto, vamos a comenzar a desarrollar archivos README para nuestros últimos desafíos.

Aquí tienes un artículo con los pasos para crear un README increíble:

[Cómo escribir un README increíble en tu Github | Alura Cursos Online](https://www.aluracursos.com/blog/como-escribir-un-readme-increible-en-tu-github)

## 10. Finalizar Curso

¡Ahora que tu proyecto está listo, no olvides enviar el enlace de tu repositorio de GitHub en el curso del desafío y descargar tu certificado!