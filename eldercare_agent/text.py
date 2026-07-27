from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Iterable
from itertools import pairwise

SPANISH_STOPWORDS = {
    "a", "al", "algo", "algun", "alguna", "algunas", "alguno", "algunos", "ante",
    "como", "con", "contra", "cual", "cuando", "de", "del", "desde", "donde", "dos",
    "el", "ella", "ellas", "ellos", "en", "entre", "era", "es", "esa", "ese", "eso",
    "esta", "este", "esto", "fue", "ha", "hay", "la", "las", "le", "les", "lo", "los",
    "mas", "me", "mi", "muy", "no", "nos", "o", "para", "pero", "por", "porque", "que",
    "se", "ser", "si", "sin", "sobre", "son", "su", "sus", "tambien", "te", "tiene",
    "todo", "un", "una", "uno", "unos", "y", "ya", "debe", "deben", "deber",
    "puede", "pueden", "puedo", "podria", "podrian", "hacer", "ayuda", "ayudan",
}

DOMAIN_EXPANSIONS: dict[str, tuple[str, ...]] = {
    "alimentacion": ("nutricion", "dieta", "comida", "alimentos"),
    "alimentar": ("nutricion", "dieta", "comida"),
    "comer": ("alimentacion", "nutricion", "dieta"),
    "ejercicio": ("actividad", "fisica", "movimiento", "movilidad", "entrenamiento"),
    "estirar": ("estiramiento", "flexibilidad", "movilidad"),
    "caida": ("caidas", "equilibrio", "prevencion", "riesgo"),
    "memoria": ("cognitiva", "cognicion", "atencion", "estimulacion"),
    "cuidador": ("cuidado", "cuidados", "dependencia", "apoyo"),
    "hipertension": ("hipertenso", "presion", "arterial"),
    "estrenimiento": ("fibra", "evacuacion", "intestinal"),
    "higiene": ("aseo", "bano", "piel", "limpieza"),
    "adulto": ("mayor", "anciano", "envejecimiento"),
}


def strip_accents(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\u00ad", "")
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize(text: str, expand: bool = False) -> list[str]:
    normalized = strip_accents(text.lower())
    words = re.findall(r"[a-z0-9]{2,}", normalized)
    tokens = [word for word in words if word not in SPANISH_STOPWORDS]
    if expand:
        expanded = list(tokens)
        for token in tokens:
            expanded.extend(DOMAIN_EXPANSIONS.get(token, ()))
        tokens = expanded
    bigrams = [f"{left}_{right}" for left, right in pairwise(tokens)]
    return tokens + bigrams


def sentence_split(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡])", compact) if part.strip()]


def stable_hash(*parts: str, length: int = 16) -> str:
    payload = "\x1f".join(parts).encode("utf-8", errors="replace")
    return hashlib.sha256(payload).hexdigest()[:length]


def compact_excerpt(text: str, limit: int = 360) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    if len(value) <= limit:
        return value
    clipped = value[:limit].rsplit(" ", 1)[0]
    return f"{clipped}…"


def unique_preserving_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
