from __future__ import annotations

import html
import uuid

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import streamlit as st

from eldercare_agent.audit import write_feedback
from eldercare_agent.config import Settings
from eldercare_agent.models import AgentResponse, DocumentChunk, SearchResult
from eldercare_agent.safety import MEDICAL_DISCLAIMER
from eldercare_agent.service import ElderCareAgent
from eldercare_agent.text import compact_excerpt

st.set_page_config(
    page_title="AAMIA | Apoyo al Adulto Mayor IA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    :root {
        --care-green: #185c4a;
        --care-green-soft: #e9f4ef;
        --care-cream: #fbf8f0;
        --care-coral: #dc6b4d;
        --care-ink: #19332c;
    }
    .stApp { background: linear-gradient(180deg, #fbf8f0 0%, #ffffff 26%); }
    [data-testid="stSidebar"] { background: #f0f6f2; border-right: 1px solid #d8e8df; }
    .hero {
        padding: 1.35rem 1.5rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #185c4a 0%, #267a64 100%);
        color: white;
        box-shadow: 0 12px 30px rgba(24, 92, 74, .16);
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; font-size: 2rem; color: white; }
    .hero p { margin: .45rem 0 0; opacity: .92; font-size: 1rem; }
    .notice {
        padding: .85rem 1rem;
        border-left: 4px solid #dc6b4d;
        background: #fff4ed;
        border-radius: 8px;
        color: #633023;
        margin: .5rem 0 1.2rem;
    }
    .source-card {
        background: #f8fbf9;
        border: 1px solid #dce9e2;
        border-radius: 10px;
        padding: .8rem .9rem;
        margin-bottom: .55rem;
    }
    .source-meta { color: #185c4a; font-weight: 650; font-size: .92rem; }
    .source-text { color: #42534d; font-size: .9rem; margin-top: .35rem; }
    .status-chip {
        display: inline-block;
        padding: .2rem .55rem;
        border-radius: 999px;
        background: #dff1e8;
        color: #185c4a;
        font-size: .78rem;
        font-weight: 650;
    }
    [data-testid="stChatMessage"] { border-radius: 14px; }
    div.stButton > button { border-radius: 10px; }
</style>
""",
    unsafe_allow_html=True,
)


def _restore_result(data: dict) -> SearchResult:
    return SearchResult(
        chunk=DocumentChunk.from_dict(data["chunk"]),
        score=data["score"],
        rank=data["rank"],
    )


def _response_to_dict(response: AgentResponse) -> dict:
    return {
        "answer": response.answer,
        "sources": [
            {"chunk": result.chunk.to_dict(), "score": result.score, "rank": result.rank}
            for result in response.sources
        ],
        "provider": response.provider,
        "latency_ms": response.latency_ms,
        "confidence": response.confidence,
        "emergency_notice": response.emergency_notice,
        "fallback_used": response.fallback_used,
        "error": response.error,
    }


@st.cache_resource(show_spinner=False)
def load_agent() -> tuple[ElderCareAgent, bool]:
    return ElderCareAgent.create(Settings.from_env())


def render_sources(message_id: str, source_data: list[dict]) -> None:
    if not source_data:
        return
    with st.expander(f"Ver {len(source_data)} fuentes consultadas", expanded=False):
        for item in source_data:
            result = _restore_result(item)
            title = html.escape(result.chunk.title or result.chunk.source)
            excerpt = html.escape(compact_excerpt(result.chunk.text))
            st.markdown(
                f"""
<div class="source-card">
  <div class="source-meta">Fuente {result.rank} · {title} · página PDF {result.chunk.page}</div>
  <div class="source-text">{excerpt}</div>
</div>
""",
                unsafe_allow_html=True,
            )
    feedback_key = f"feedback_{message_id}"
    if feedback_key not in st.session_state:
        left, right, _spacer = st.columns([1, 1, 7])
        if left.button("👍 Útil", key=f"up_{message_id}", use_container_width=True):
            write_feedback(settings.logs_dir, st.session_state.session_id, message_id, "positive")
            st.session_state[feedback_key] = "positive"
            st.rerun()
        if right.button("👎 Mejorar", key=f"down_{message_id}", use_container_width=True):
            write_feedback(settings.logs_dir, st.session_state.session_id, message_id, "negative")
            st.session_state[feedback_key] = "negative"
            st.rerun()
    else:
        st.caption("Gracias por tu retroalimentación.")


settings = Settings.from_env()
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
<div class="hero">
  <h1>🌿 AAMIA</h1>
  <p>Apoyo al Adulto Mayor con Inteligencia Artificial para un cuidado digno, activo y acompañado.</p>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown(f'<div class="notice">⚕️ {MEDICAL_DISCLAIMER}</div>', unsafe_allow_html=True)

try:
    with st.spinner("Preparando la biblioteca documental…"):
        agent, rebuilt = load_agent()
except Exception as exc:  # noqa: BLE001 - present a friendly startup error in the UI
    st.error(f"No fue posible iniciar el agente: {exc}")
    st.info("Verifica que exista al menos un PDF en `docs/` y revisa la configuración del archivo `.env`.")
    st.stop()

with st.sidebar:
    st.title("Biblioteca")
    stats = agent.stats
    first, second = st.columns(2)
    first.metric("PDF", stats["documents"])
    second.metric("Páginas", stats["pages"])
    st.metric("Fragmentos consultables", stats["chunks"])
    provider_label = {
        "extractive": "Local · sin API",
        "openai": f"OpenAI · {settings.openai_model}",
        "oci": f"OCI GenAI · {settings.oci_genai_model}",
    }.get(settings.llm_provider, settings.llm_provider)
    st.markdown(f'<span class="status-chip">{html.escape(provider_label)}</span>', unsafe_allow_html=True)
    if rebuilt:
        st.success("Índice documental actualizado.")
    if stats["errors"]:
        st.warning(f"La ingesta terminó con {stats['errors']} avisos no críticos.")
    st.divider()
    if st.button("🔄 Reconstruir índice", use_container_width=True):
        with st.spinner("Leyendo nuevamente los PDF…"):
            ElderCareAgent.create(settings, force_rebuild=True)
            load_agent.clear()
        st.success("Índice reconstruido.")
        st.rerun()
    if st.button("🧹 Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    st.divider()
    st.caption("Privacidad: por defecto los logs guardan hashes y metadatos, no el texto de las conversaciones.")

st.subheader("¿Qué te gustaría consultar?")
suggestions = [
    "¿Cómo puedo prevenir caídas en casa?",
    "¿Qué aspectos debe considerar una alimentación saludable?",
    "¿Cómo debe organizarse una sesión de actividad física?",
    "¿Qué actividades ayudan a estimular la memoria?",
]
columns = st.columns(2)
pending_question: str | None = None
for index, suggestion in enumerate(suggestions):
    if columns[index % 2].button(suggestion, key=f"suggestion_{index}", use_container_width=True):
        pending_question = suggestion

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if message.get("emergency_notice"):
                st.error(message["emergency_notice"])
            meta = (
                f"Confianza documental: **{message.get('confidence', 'baja')}** · "
                f"Modo: **{message.get('provider', 'local')}** · "
                f"{message.get('latency_ms', 0)} ms"
            )
            st.caption(meta)
            if message.get("fallback_used"):
                st.warning("El proveedor configurado no respondió; se utilizó el modo local como respaldo.")
            render_sources(message["id"], message.get("sources", []))

typed_question = st.chat_input("Pregunta sobre cuidados, alimentación, ejercicio o bienestar…", max_chars=2_000)
question = pending_question or typed_question
if question:
    user_message = {"id": str(uuid.uuid4()), "role": "user", "content": question}
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando la biblioteca…"):
            response = agent.ask(question, session_id=st.session_state.session_id)
        if response.emergency_notice:
            st.error(response.emergency_notice)
        st.markdown(response.answer)
        st.caption(
            f"Confianza documental: **{response.confidence}** · "
            f"Modo: **{response.provider}** · {response.latency_ms} ms"
        )
        if response.fallback_used:
            st.warning("El proveedor configurado no respondió; se utilizó el modo local como respaldo.")
        assistant_message = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": response.answer,
            **_response_to_dict(response),
        }
        st.session_state.messages.append(assistant_message)
        render_sources(assistant_message["id"], assistant_message["sources"])
