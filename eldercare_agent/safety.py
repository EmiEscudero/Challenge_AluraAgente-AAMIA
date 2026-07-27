from __future__ import annotations

import re

from .text import strip_accents

EMERGENCY_TERMS = (
    "no respira", "dificultad para respirar", "dolor de pecho", "inconsciente",
    "no responde", "sangrado abundante", "convulsion", "cara caida",
    "debilidad de un lado", "habla arrastrada", "intento de suicidio",
    "quiere morir", "sobredosis", "caida con golpe en la cabeza",
)

EMERGENCY_NOTICE = (
    "Esto podría describir una urgencia. Llama ahora al número local de emergencias y "
    "sigue las instrucciones del personal sanitario. No retrases la atención por esperar "
    "una respuesta de este asistente."
)


def emergency_notice(query: str) -> str | None:
    normalized = strip_accents(query.lower())
    if any(term in normalized for term in EMERGENCY_TERMS):
        return EMERGENCY_NOTICE
    return None


MEDICAL_DISCLAIMER = (
    "Información educativa basada en los documentos de la biblioteca. No sustituye una "
    "valoración médica ni debe usarse para diagnosticar, prescribir o cambiar tratamientos."
)


DOMAIN_TERMS = {
    "adulto", "adultos", "mayor", "mayores", "anciano", "ancianos", "vejez",
    "envejecimiento", "cuidador", "cuidadora", "cuidado", "cuidados", "dependencia",
    "alimentacion", "alimentar", "comer", "comida", "dieta", "nutricion", "alimento",
    "alimentos", "agua", "hidratacion", "desayuno", "almuerzo", "cena", "fibra",
    "ejercicio", "actividad", "fisica", "movilidad", "estiramiento", "yoga", "caminar",
    "equilibrio", "flexibilidad", "fuerza", "caida", "caidas", "levantarse", "transferencia",
    "memoria", "atencion", "cognitivo", "cognitiva", "estimulacion", "soledad", "animo",
    "higiene", "aseo", "bano", "piel", "ulcera", "postura", "sueno", "descanso",
    "salud", "dolor", "hipertension", "presion", "estrenimiento", "incontinencia",
    "medicamento", "medicamentos", "primeros", "auxilios", "emergencia", "urgencia",
}


def is_domain_query(query: str) -> bool:
    normalized = strip_accents(query.lower())
    words = set(re.findall(r"[a-z0-9]+", normalized))
    return bool(words & DOMAIN_TERMS) or emergency_notice(query) is not None
