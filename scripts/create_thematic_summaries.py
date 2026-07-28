"""Genera los cinco resúmenes PDF seleccionados que utiliza el corpus RAG de AAMIA.

Los PDF originales siguen siendo la evidencia canónica. Los archivos Markdown de
``docs`` solo sirven como contexto editorial: nunca se copian al corpus generado y
la aplicación continúa aceptando exclusivamente cargas de PDF.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS_OUTPUT = ROOT / "docs" / "resumenes"
DELIVERY_OUTPUT = ROOT / "output" / "pdf"

GREEN = colors.HexColor("#185C4A")
GREEN_2 = colors.HexColor("#267A64")
MINT = colors.HexColor("#E9F4EF")
MINT_2 = colors.HexColor("#D6ECE2")
CREAM = colors.HexColor("#FBF8F0")
CORAL = colors.HexColor("#C8543D")
CORAL_LIGHT = colors.HexColor("#F9E8E2")
GOLD = colors.HexColor("#D89A2B")
INK = colors.HexColor("#19332C")
GRAY = colors.HexColor("#52635D")
LIGHT_GRAY = colors.HexColor("#F3F5F4")
LINE = colors.HexColor("#D8E8DF")


def _register_fonts() -> tuple[str, str]:
    candidates = (
        (Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
    )
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("AAMIA-Regular", regular))
            pdfmetrics.registerFont(TTFont("AAMIA-Bold", bold))
            return "AAMIA-Regular", "AAMIA-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = _register_fonts()


def S(title: str, intro: str, bullets: tuple[str, ...], evidence: str) -> dict:
    return {"title": title, "intro": intro, "bullets": bullets, "evidence": evidence}


def R(code: str, title: str, pages: str, source_type: str, note: str = "") -> tuple[str, ...]:
    return code, title, pages, source_type, note


SUMMARIES = (
    {
        "number": 1,
        "slug": "salud_integral_y_seguridad_clinica",
        "title": "Salud integral y seguridad clínica",
        "subtitle": "Valoración, cambios relevantes, medicamentos y coordinación del cuidado",
        "audience": "Familias, personas cuidadoras y equipos de apoyo",
        "keywords": (
            "valoración integral", "fragilidad", "medicamentos", "polifarmacia",
            "señales de alarma", "enfermedad crónica",
        ),
        "principles": (
            "Comparar con el estado habitual es más útil que atribuir cualquier cambio a la edad.",
            "Función, memoria, ánimo, nutrición y red de apoyo forman parte de una misma valoración.",
            "La familia observa y registra; el personal de salud diagnostica, prescribe y modifica tratamientos.",
            "Un cambio súbito exige más atención que una dificultad estable y conocida.",
        ),
        "sections": (
            S(
                "1. Partir de una línea de base personal",
                "Una valoración útil comienza por conocer qué puede y quiere hacer la persona, cómo se comunica y qué apoyos utiliza. La autonomía no se mide solo por diagnósticos.",
                (
                    "Registrar capacidad para comer, bañarse, vestirse, usar el baño, desplazarse y manejar compras, citas, medicamentos o finanzas.",
                    "Observar orientación, memoria, atención, ánimo, sueño, dolor, respiración, apetito, evacuaciones y marcha.",
                    "Identificar lentes, auxiliares auditivos, prótesis, bastón o andadera y comprobar que funcionen.",
                    "Anotar preferencias, rutinas, alergias, diagnósticos, contactos y decisiones anticipadas expresadas.",
                ),
                "Síntesis de [R1, pp. 2 y 7], [R2, pp. 11 y 123-124], [R3, pp. 10-11] y [R4, pp. 19 y 22-25].",
            ),
            S(
                "2. Envejecimiento no significa enfermedad",
                "El envejecimiento modifica la reserva de distintos sistemas, pero no vuelve normal la pérdida rápida de capacidad ni explica por sí solo síntomas nuevos.",
                (
                    "Distinguir cambios graduales de deterioro repentino. Confusión nueva, debilidad súbita, caída reciente o somnolencia inusual requieren valoración.",
                    "La fragilidad puede expresarse como menor fuerza, lentitud, cansancio, pérdida de peso o menor tolerancia al esfuerzo.",
                    "Factores físicos, cognitivos, emocionales, nutricionales y sociales pueden interactuar.",
                    "Evitar estereotipos: edad cronológica o número de enfermedades no determinan por sí solos capacidad y preferencias.",
                ),
                "Reserva fisiológica, sarcopenia y fragilidad se revisan en [R5, pp. 5 y 7] y [R6, pp. 1 y 4].",
            ),
            S(
                "3. Observar, registrar y comunicar",
                "Un registro breve permite detectar tendencias y comunicar hechos concretos al equipo tratante.",
                (
                    "Anotar fecha, hora, qué cambió, actividad previa, duración, síntomas asociados y recuperación.",
                    "Registrar caídas, dosis omitidas, dificultad para tragar, rechazo de alimentos, menos orina, fiebre, dolor o cambios conductuales.",
                    "Preparar preguntas antes de cada consulta y llevar registros y lista de medicamentos.",
                    "Compartir información entre cuidadores para evitar versiones contradictorias o pérdidas de seguimiento.",
                ),
                "Observación del cuidador en [R1, pp. 2-3 y 7], [R2, p. 50] y [R3, pp. 11 y 25].",
            ),
            S(
                "4. Medicamentos sin improvisar",
                "La polifarmacia aumenta complejidad, interacciones y reacciones adversas. La respuesta segura es revisar, no suspender por cuenta propia.",
                (
                    "Mantener una lista única con nombre, dosis, horario, motivo e indicación profesional; incluir productos sin receta y herbolaria.",
                    "Usar un solo sistema de organización. No duplicar una dosis olvidada sin instrucciones específicas.",
                    "No triturar tabletas ni abrir cápsulas sin confirmar que sea seguro.",
                    "Solicitar revisión ante mareo, somnolencia, confusión, estreñimiento, sangrado, caídas o dificultad para cumplir el esquema.",
                ),
                "Recomendaciones convergentes en [R1, p. 7], [R2, p. 50], [R3, p. 25] y [R7, pp. 2 y 5].",
            ),
            S(
                "5. Enfermedades crónicas y transiciones",
                "Cuando existen varias enfermedades, el plan debe coordinar función, prioridades y carga del tratamiento.",
                (
                    "Conservar un resumen de diagnósticos, medicamentos, alergias, contactos y cambios recientes.",
                    "Tras una hospitalización, confirmar por escrito cambios en medicación, alimentación, movilidad, curaciones y seguimiento.",
                    "Prevenir inmovilidad innecesaria durante la recuperación siguiendo las indicaciones del equipo tratante.",
                    "Las decisiones complejas deben considerar beneficios, riesgos, calidad de vida y preferencias expresadas.",
                ),
                "Coordinación de patología crónica en [R8, pp. 1-2]; transiciones y riesgos en [R2, pp. 123-124] y [R9, pp. 4-5].",
            ),
            S(
                "6. Evidencia especializada: límites",
                "Los artículos sobre terapia intensiva, cirugía, estenosis aórtica y demencia avanzada ayudan a reconocer complejidad, pero no deben convertirse en instrucciones domésticas.",
                (
                    "Usar estas fuentes para formular preguntas, no para elegir procedimientos o tratamientos.",
                    "Varios artículos clínicos son de 2012 y pueden no reflejar guías actuales.",
                    "Ante contradicciones, priorizar al equipo tratante y fuentes institucionales recientes aplicables al país y condición.",
                    "Mantener separadas la educación general y la decisión clínica individual.",
                ),
                "Contexto especializado: [R9], [R10], [R11] y [R12]. La epidemiología [R13] no genera recomendaciones individuales.",
            ),
        ),
        "actions": (
            ("Observar", "Cambio leve, estable o aislado sin señales de alarma.", "Registrar y comentar en el seguimiento."),
            ("Consultar pronto", "Deterioro nuevo de memoria, marcha, apetito, ánimo, continencia o capacidad diaria.", "Contactar salud y llevar cronología y medicamentos."),
            ("Atención urgente", "Pérdida de conciencia, dificultad intensa para respirar, dolor torácico, sangrado que no cede, rostro caído, debilidad de un brazo, habla alterada o deterioro rápido.", "Contactar emergencias locales; no esperar a la aplicación."),
        ),
        "references": (
            R("R1", "AAMIA_guia_abierta_para_el_cuidado.pdf", "2-3, 7", "Guía abierta"),
            R("R2", "MANUAL_BASICO_CUIDADO_PERSONAS_ADULTAS_MAYORES_16_JULIO_221021.pdf", "11, 50, 94, 123-124, 147, 160", "Manual institucional"),
            R("R3", "Manual_cuidados-generales.pdf", "10-11, 25, 28-29", "Manual práctico"),
            R("R4", "Envejecer con alegría guía para acompañar y vivir la tercera edad (Montoya Carrasquilla, Jorge).pdf", "19, 22-25", "Libro de consulta"),
            R("R5", "Cambios-fisiol-gicos-asociados-al-envejeci_2012_Revista-M-dica-Cl-nica-Las-C.pdf", "5, 7", "Revisión clínica, 2012"),
            R("R6", "Evaluaci-n-y-cuidado-del-adulto-mayor-fr_2012_Revista-M-dica-Cl-nica-Las-Con.pdf", "1, 4", "Revisión clínica, 2012"),
            R("R7", "Polifarmacia-y-morbilidad-en-adultos-may_2012_Revista-M-dica-Cl-nica-Las-Con.pdf", "2, 5", "Revisión clínica, 2012"),
            R("R8", "La-gesti-n-del-paciente-mayor-con-patolog-a_2012_Revista-M-dica-Cl-nica-Las-.pdf", "1-2", "Artículo clínico, 2012"),
            R("R9", "Evaluaci-n-de-riesgos-quir-rgicos-y-manejo-post-cir_2012_Revista-M-dica-Cl-n.pdf", "1, 4-5", "Revisión clínica, 2012", "Contexto profesional"),
            R("R10", "Consideraciones-Del-Adulto-Mayor-En-UT_2012_Revista-M-dica-Cl-nica-Las-Conde.pdf", "1, 4", "Artículo clínico, 2012", "Contexto profesional"),
            R("R11", "Estenosis-a-rtica--Implante-de-pr-tesis-valvular-a-r_2012_Revista-M-dica-Cl-.pdf", "1", "Revisión clínica, 2012", "Contexto profesional"),
            R("R12", "Toma-de-decisiones-en-pacientes-con-demencia_2012_Revista-M-dica-Cl-nica-Las.pdf", "1, 3-4", "Revisión clínica y ética, 2012"),
            R("R13", "Poblaci-n-de-80-y-m-s-a-os-en-chile--Una-visi-n-preli_2012_Revista-M-dica-Cl.pdf", "1-8", "Artículo epidemiológico, 2012"),
            R("R14", "Manual de cuidado del adulto y el envejeciente II (Holguín Guzmán, Estefany Mayrobi).pdf", "19-41", "Manual académico"),
        ),
        "context": (
            "Transcripción video de YouTube - Cuidado básico del adulto mayor webinar.md (enfoque integral y autonomía; no indexado).",
            "Articulo web- Cuidado de adultos mayores en casa- Una guía integral.md (contexto domiciliario; no indexado).",
        ),
        "excluded": (
            "Editorial_2012_Revista-M-dica-Cl-nica-Las-Condes.pdf: editorial general sin recomendaciones verificables para el cuidado.",
        ),
    },
    {
        "number": 2,
        "slug": "autonomia_cuidados_y_entorno_seguro",
        "title": "Autonomía, cuidados cotidianos y entorno seguro",
        "subtitle": "Rutinas, higiene, piel, sueño, caídas, trato digno y apoyo al cuidador",
        "audience": "Personas mayores, familias y cuidadores domiciliarios",
        "keywords": (
            "autonomía", "actividades diarias", "higiene", "piel",
            "sueño", "caídas", "maltrato", "cuidador",
        ),
        "principles": (
            "Ayudar solo en lo necesario conserva capacidad, identidad y dignidad.",
            "Una rutina predecible debe ser flexible y construirse con la persona.",
            "El entorno puede aumentar o reducir discapacidad; seguridad y autonomía deben diseñarse juntas.",
            "Cuidar bien requiere relevo, capacitación y atención a la salud de quien cuida.",
        ),
        "sections": (
            S(
                "1. Cuidado centrado en la persona",
                "El cuidado cotidiano comienza pidiendo permiso, explicando cada paso y respetando preferencias, tiempos y privacidad.",
                (
                    "Preguntar cómo desea ser llamada, qué actividades quiere conservar y dónde necesita apoyo.",
                    "Ofrecer opciones reales en ropa, horarios, alimentos, actividades y organización del día.",
                    "Evitar infantilizar, apresurar, regañar o hablar como si la persona no estuviera presente.",
                    "Revisar si el apoyo sigue siendo proporcional: demasiada ayuda puede reducir función y autoestima.",
                ),
                "Principios en [R1, pp. 2-3], [R2, p. 11], [R3, pp. 5 y 28] y [R5, p. 16].",
            ),
            S(
                "2. Rutina que permite observar cambios",
                "Combinar autocuidado, alimentación, movimiento, descanso y contacto social facilita el día y revela cambios respecto de lo habitual.",
                (
                    "Al iniciar, observar orientación, ánimo, dolor, respiración y capacidad para levantarse.",
                    "Preparar objetos en orden de uso y dar tiempo suficiente para aseo, vestido y baño.",
                    "Alternar actividad y descanso y mantener al alcance agua y apoyos permitidos.",
                    "Registrar alimentación, líquidos, evacuaciones, actividad, sueño, dolor, caídas y novedades.",
                ),
                "Rutina sintetizada de [R1, p. 3], [R2, pp. 121 y 124] y [R3, pp. 5 y 65].",
            ),
            S(
                "3. Higiene, boca y piel",
                "La higiene protege salud, imagen personal y autoestima. Debe realizarse con privacidad y participación.",
                (
                    "Adaptar baño, manos, boca, cabello, uñas y ropa al grado de independencia.",
                    "Mantener prótesis dentales limpias y revisar ajuste, dolor, heridas, boca seca o dificultad para masticar.",
                    "Observar piel expuesta a presión o humedad. Enrojecimiento persistente, herida, dolor, secreción u olor requieren valoración.",
                    "En movilidad muy limitada, solicitar un plan profesional de posición, superficies de apoyo, nutrición y continencia.",
                ),
                "Higiene y piel: [R2, pp. 26, 128 y 136-137], [R3, pp. 24 y 28], [R5, p. 29] y [R13, p. 25].",
            ),
            S(
                "4. Sueño y descanso",
                "El sueño puede cambiar con la edad, pero insomnio persistente, somnolencia excesiva o pausas respiratorias observadas merecen consulta.",
                (
                    "Mantener horarios regulares, luz diurna, actividad apropiada y una rutina tranquila al final del día.",
                    "Reducir ruido, luz intensa y pantallas; preparar una ruta nocturna iluminada al baño.",
                    "Revisar dolor, necesidad de orinar, ansiedad, estimulantes y posibles efectos de medicamentos.",
                    "No iniciar sedantes o productos para dormir por cuenta propia; pueden aumentar confusión y caídas.",
                ),
                "Apoyo en [R1, p. 3], [R2, p. 121] y [R6, pp. 59-62].",
            ),
            S(
                "5. Hogar seguro y respuesta a caídas",
                "La revisión del entorno sigue las rutas usadas de día y de noche. Después de una caída se valora seguridad antes de mover.",
                (
                    "Retirar cables, tapetes y obstáculos; mejorar iluminación y contraste.",
                    "Instalar apoyos firmes y superficies antideslizantes cuando sean necesarios.",
                    "Revisar calzado, lentes, audición, bastón o andadera; las caídas suelen tener varias causas.",
                    "No levantar de inmediato ante golpe en cabeza, dolor intenso, deformidad, sangrado, pérdida de conciencia o incapacidad para moverse.",
                    "Registrar circunstancias y avisar al equipo de salud si la caída es nueva o repetida.",
                ),
                "Prevención y respuesta en [R1, p. 6], [R2, pp. 94 y 121], [R5, p. 16] y [R6, pp. 65-66].",
            ),
            S(
                "6. Calidad del cuidado y prevención del maltrato",
                "El maltrato puede ser físico, psicológico, sexual, económico, por negligencia o por restricción injustificada.",
                (
                    "Observar lesiones sin explicación, miedo, higiene deficiente, sobremedicación, aislamiento, cambios conductuales o control indebido del dinero.",
                    "Escuchar en privado cuando sea seguro y no confrontar si aumenta el riesgo.",
                    "Ante peligro inmediato, contactar emergencias o servicios locales de protección.",
                    "Capacitación, supervisión, personal suficiente y vías de queja forman parte de la calidad institucional.",
                ),
                "Calidad en [R7, pp. 4 y 8]; dependencia en [R8, pp. 5-6]; maltrato en [R9, pp. 4-6] y [R6, pp. 31-33].",
            ),
            S(
                "7. Cuidar a quien cuida",
                "El agotamiento indica que la carga supera recursos disponibles; no es una falla moral.",
                (
                    "Distribuir tareas, horarios y contactos; acordar relevos antes de una crisis.",
                    "Conservar sueño, alimentación, movimiento, atención médica y vínculos propios.",
                    "Buscar apoyo ante irritabilidad persistente, aislamiento, desesperanza o sensación de no poder continuar.",
                    "Si aparecen ideas de hacerse daño o dañar a la persona cuidada, pedir ayuda urgente y crear distancia segura.",
                ),
                "Sobrecarga y red de apoyo en [R3, pp. 60-65], [R4, p. 14] y [R14, pp. 1, 3 y 5].",
            ),
        ),
        "actions": (
            ("Adaptar", "La actividad es lenta o requiere ayuda parcial.", "Dar tiempo, simplificar pasos y ofrecer apoyos estables."),
            ("Consultar", "Caídas repetidas, insomnio persistente, lesión de piel, pérdida funcional o agotamiento.", "Solicitar valoración con un registro de frecuencia y contexto."),
            ("Proteger", "Lesión grave, pérdida de conciencia, sospecha de abuso o riesgo inmediato.", "Contactar emergencias o protección y no dejar sola a la persona en riesgo."),
        ),
        "references": (
            R("R1", "AAMIA_guia_abierta_para_el_cuidado.pdf", "2-3, 6-7", "Guía abierta"),
            R("R2", "MANUAL_BASICO_CUIDADO_PERSONAS_ADULTAS_MAYORES_16_JULIO_221021.pdf", "11, 26, 94, 121, 124, 128, 136-137, 160", "Manual institucional"),
            R("R3", "Manual_de_Apoyo_con_el_Cuidado_de_PAMS.pdf", "5, 24, 28, 56, 59-65", "Manual institucional"),
            R("R4", "Guía de cuidados básicos interactivo.pdf", "14, 43, 62", "Guía práctica"),
            R("R5", "Manual_cuidados-generales.pdf", "16, 19, 29", "Manual práctico"),
            R("R6", "Cuidado de los adultos mayores (Lesur, Luis).pdf", "31-33, 51, 59-66, 255", "Libro de consulta"),
            R("R7", "Calidad_del_cuidado_del_adulto_mayor_en.pdf", "4, 8", "Artículo de investigación, 2005"),
            R("R8", "Dejar de ser o hacer - significado de dependencia funcional para el adulto mayor.pdf", "5-6", "Artículo cualitativo"),
            R("R9", "Maltrato-en-el-adulto-mayor-institucionalizado--_2012_Revista-M-dica-Cl-nica.pdf", "4-6", "Revisión, 2012"),
            R("R10", "Experiencia-cl-nica-de-la-fundaci-n-villa-de-anci_2012_Revista-M-dica-Cl-nic.pdf", "1-5", "Experiencia institucional, 2012"),
            R("R11", "Espacio-sociosanitario-del-adulto-mayor--miradas_2012_Revista-M-dica-Cl-nica.pdf", "1-5", "Salud pública, 2012"),
            R("R12", "Envejecer con alegría guía para acompañar y vivir la tercera edad (Montoya Carrasquilla, Jorge).pdf", "17, 64, 75", "Libro de consulta"),
            R("R13", "Manual de práctica cuidado del adulto y el envejeciente (Sepúlveda Estévez, Magdalena).pdf", "25", "Manual académico"),
            R("R14", "Hijos-adultos-mayores-al-cuidado-de-sus-padres--_2012_Revista-M-dica-Cl-nica.pdf", "1, 3, 5", "Artículo psicosocial, 2012"),
        ),
        "context": (
            "Articulo web- Cuidado de adultos mayores en casa- Una guía integral.md (adaptación y apoyo domiciliario; no indexado).",
            "Articulo web- Qué cuidados debo brindar a un adulto mayor.md (higiene, entorno y participación; no indexado).",
            "Transcripción video de YouTube - Cuidado básico del adulto mayor webinar.md (autonomía, sueño y roles; no indexado).",
        ),
    },
    {
        "number": 3,
        "slug": "alimentacion_hidratacion_y_salud_digestiva",
        "title": "Alimentación, hidratación y salud digestiva",
        "subtitle": "Nutrición adaptable, seguridad al comer, salud bucal y prevención del estreñimiento",
        "audience": "Personas mayores, familias y cuidadores",
        "keywords": (
            "alimentación", "hidratación", "desnutrición", "disfagia",
            "hipertensión", "estreñimiento", "fecaloma", "salud bucal",
        ),
        "principles": (
            "La alimentación debe ser suficiente, variada, agradable y compatible con la situación clínica y cultural.",
            "Cambios de peso, apetito, deglución o hidratación son datos de salud.",
            "No existe un menú universal para todas las personas mayores.",
            "Restricciones de sal, líquidos, textura o nutrientes deben individualizarse.",
        ),
        "sections": (
            S(
                "1. Una base flexible y apetecible",
                "La meta es combinar adecuación, equilibrio, moderación y diversidad sin convertir la comida en una imposición.",
                (
                    "Incluir verduras y frutas, cereales o tubérculos, leguminosas y fuentes apropiadas de proteína.",
                    "Preferir alimentos poco procesados y adaptar porción, textura, temperatura y presentación.",
                    "Respetar preferencias, cultura, horarios y posibilidades económicas; comer acompañado puede ayudar.",
                    "Considerar diagnósticos, actividad, dentición, apetito y capacidad para comprar o cocinar.",
                ),
                "Síntesis de [R1, p. 4], [R2, pp. 30 y 34-36], [R3, pp. 4-6] y [R4, p. 4].",
            ),
            S(
                "2. Detectar riesgo nutricional",
                "La pérdida de peso involuntaria, menor fuerza o cambios sostenidos de apetito no deben asumirse como inevitables.",
                (
                    "Observar peso, ajuste de ropa, fuerza, número de comidas, proteína, frutas, verduras y líquidos.",
                    "Investigar dolor dental, prótesis, boca seca, deglución, depresión, aislamiento, medicamentos o acceso a alimentos.",
                    "Consultar ante pérdida de peso, debilidad creciente, heridas que no cicatrizan, edema, vómitos o rechazo persistente.",
                    "La evaluación profesional integra historia, peso, función, enfermedades y alimentación; una cifra aislada no basta.",
                ),
                "Riesgo y evaluación en [R3, pp. 4-5], [R4, p. 12] y [R9, p. 21].",
            ),
            S(
                "3. Hidratación individualizada",
                "La sensación de sed puede disminuir y algunas personas necesitan recordatorios, pero otras tienen restricciones médicas.",
                (
                    "Ofrecer líquidos regularmente en cantidades manejables si no existe restricción indicada.",
                    "Usar vasos fáciles de sujetar y dejar agua visible; registrar ingesta cuando haya riesgo.",
                    "Observar boca seca, orina escasa u oscura, mareo, debilidad, somnolencia o confusión nueva.",
                    "En enfermedad renal, cardiaca o hepática, seguir la cantidad indicada por el equipo tratante.",
                ),
                "Hidratación en [R1, p. 4], [R3, p. 5] y [R4, pp. 12 y 19].",
            ),
            S(
                "4. Comer y beber con seguridad",
                "Tos, voz húmeda, atragantamiento, alimento retenido o infecciones respiratorias repetidas pueden sugerir dificultad de deglución.",
                (
                    "Procurar postura sentada y estable; no alimentar a una persona somnolienta o acostada.",
                    "Ofrecer tiempo, porciones pequeñas y un ambiente sin prisas.",
                    "No cambiar consistencias, usar espesantes ni triturar medicamentos sin indicación individual.",
                    "Ante obstrucción completa o incapacidad para respirar, activar emergencias y aplicar solo maniobras con capacitación vigente.",
                ),
                "Seguridad general en [R1, p. 4] y [R7, pp. 47 y 49].",
            ),
            S(
                "5. Hipertensión y sodio",
                "Reducir sodio suele formar parte del manejo, pero la intensidad de la restricción debe ajustarse a cada persona.",
                (
                    "Priorizar alimentos frescos y revisar etiquetas de procesados, embutidos, sopas, salsas y botanas.",
                    "Dar sabor con hierbas y especias compatibles con preferencias y tolerancia.",
                    "No usar sustitutos con potasio sin consultar; pueden ser inadecuados en enfermedad renal o con ciertos fármacos.",
                    "No trasladar cantidades exactas de fuentes antiguas sin confirmación profesional actual.",
                ),
                "Principios revisados en [R2, pp. 14, 34-36 y 40-44].",
            ),
            S(
                "6. Estreñimiento y fecaloma",
                "El estreñimiento puede relacionarse con fibra, líquidos, inactividad, rutina, medicamentos o enfermedades.",
                (
                    "Registrar frecuencia, consistencia, esfuerzo, dolor, evacuación incompleta y cambios del patrón habitual.",
                    "Aumentar fibra gradualmente con líquidos permitidos; mantener movimiento, privacidad y tiempo.",
                    "No iniciar laxantes, enemas o extracción manual sin orientación, sobre todo con dolor o distensión.",
                    "Diarrea líquida inesperada con estreñimiento crónico puede coexistir con retención fecal y requiere valoración.",
                ),
                "Prevención en [R4, p. 12] y [R5, p. 25]; retención en [R6, pp. 1-2] y [R7, pp. 171-174].",
            ),
            S(
                "7. Salud bucal y experiencia de comer",
                "Dolor, pérdida dental, prótesis floja, boca seca o lesiones pueden reducir variedad y cantidad de alimentos.",
                (
                    "Realizar higiene bucal y de prótesis regularmente y con respeto.",
                    "Observar úlceras, sangrado, placas, dolor, olor persistente y cambios para masticar.",
                    "Solicitar atención dental ante prótesis que lastima, lesión persistente o dificultad para alimentarse.",
                    "Adaptar preparaciones sin eliminar grupos de alimentos ni reducir innecesariamente el placer de comer.",
                ),
                "Boca y nutrición en [R2, p. 85], [R4, pp. 4 y 12] y [R8, p. 128].",
            ),
        ),
        "actions": (
            ("Ajustar", "Apetito variable sin pérdida de peso ni dificultad.", "Ofrecer porciones manejables, variedad y registrar preferencias."),
            ("Consultar", "Pérdida de peso, tos al comer, rechazo persistente, estreñimiento nuevo, dolor o deshidratación.", "Solicitar valoración médica, nutricional, dental o de deglución."),
            ("Atención urgente", "Atragantamiento sin poder respirar, pérdida de conciencia, sangre en vómito, sangrado importante, dolor abdominal intenso o deterioro rápido.", "Contactar emergencias locales."),
        ),
        "references": (
            R("R1", "AAMIA_guia_abierta_para_el_cuidado.pdf", "4", "Guía abierta"),
            R("R2", "Guía didáctica alimentación saludable para adultos mayores hipertensos (Instituto Superior Tecnológico American College).pdf", "14, 30, 34-36, 40-44", "Guía didáctica"),
            R("R3", "La nutrición en el adulto mayor - una oportunidad para el cuidado de enfermería.pdf", "4-6", "Revisión de enfermería"),
            R("R4", "Nutricion y Cuidados del Adulto Mayor. Estudio Monografico (vmoya).pdf", "4, 12, 19, 26", "Estudio monográfico"),
            R("R5", "Gastronomía como estrategia para el manejo del estreñimiento en el adulto mayor (Valencia Naranjo, Alejandra & Muñoz Contreras, Angélica María & Cardona Gallo, David).pdf", "25", "Trabajo académico"),
            R("R6", "Caso-cl-nico-radiol-gico-fecaloma---importante-complic_2012_Revista-M-dica-C.pdf", "1-2", "Caso clínico, 2012"),
            R("R7", "Cuidado de los adultos mayores (Lesur, Luis).pdf", "47, 49, 171-174", "Libro de consulta"),
            R("R8", "MANUAL_BASICO_CUIDADO_PERSONAS_ADULTAS_MAYORES_16_JULIO_221021.pdf", "85, 124, 128", "Manual institucional"),
            R("R9", "Manual_cuidados-generales.pdf", "21", "Manual práctico"),
        ),
        "context": (
            "Articulo web- Cuidado de adultos mayores en casa- Una guía integral.md (comidas y apoyo domiciliario; no indexado).",
            "Articulo web- Qué cuidados debo brindar a un adulto mayor.md (alimentación general; no indexado).",
        ),
    },
    {
        "number": 4,
        "slug": "movimiento_movilidad_y_capacidad_funcional",
        "title": "Movimiento, movilidad y capacidad funcional",
        "subtitle": "Actividad adaptable, fuerza, equilibrio, estiramientos y prevención de caídas",
        "audience": "Personas mayores, familias, cuidadores y facilitadores de actividad",
        "keywords": (
            "actividad física", "movilidad", "fuerza", "equilibrio",
            "estiramientos", "yoga en silla", "motricidad", "caídas",
        ),
        "principles": (
            "Moverse con regularidad importa más que alcanzar una cifra perfecta desde el primer día.",
            "El programa se adapta a capacidad, diagnósticos, síntomas, preferencias y entorno.",
            "Fuerza, equilibrio, resistencia, movilidad y coordinación se complementan.",
            "Dolor agudo, falta de aire intensa, desmayo o debilidad súbita obligan a detenerse y pedir ayuda.",
        ),
        "sections": (
            S(
                "1. Movimiento como parte de la autonomía",
                "La actividad puede apoyar función, salud mental, participación y confianza, incluso sentada o con apoyo.",
                (
                    "Integrar caminatas, levantarse de una silla, tareas adaptadas, baile, juegos o ejercicios supervisados.",
                    "Evitar largos periodos de inactividad sin indicación clínica.",
                    "Relacionar el ejercicio con objetivos: llegar al baño, cocinar, salir o conservar una actividad apreciada.",
                    "Celebrar regularidad y participación, no rendimiento ni comparación.",
                ),
                "Beneficios y personalización en [R1, p. 5], [R2, p. 65], [R3, p. 30] y [R8, pp. 46-47].",
            ),
            S(
                "2. Antes de comenzar o progresar",
                "Una persona sedentaria puede iniciar con periodos breves, pero ciertas situaciones requieren valoración previa.",
                (
                    "Consultar ante caída reciente, dolor no explicado, mareo, desmayo, falta de aire inusual o enfermedad descompensada.",
                    "Revisar calzado, espacio, temperatura, iluminación, hidratación permitida y estabilidad del apoyo.",
                    "Elegir una intensidad que permita hablar con algo de esfuerzo y progresar gradualmente.",
                    "Si necesita asistencia, definir quién supervisa y cómo evitar que también caiga el cuidador.",
                ),
                "Seguridad general en [R1, p. 5], [R10, p. 94] y [R11, p. 28].",
            ),
            S(
                "3. Componentes y estructura de sesión",
                "Resistencia, fuerza, equilibrio, coordinación y movilidad apoyan tareas distintas. Una sesión sube y baja intensidad progresivamente.",
                (
                    "Inicio: comprobar cómo se siente, explicar el objetivo y realizar movimientos suaves.",
                    "Parte principal: trabajar uno o varios componentes con pausas y apoyos.",
                    "Vuelta a la calma: reducir ritmo, respirar cómodamente y observar recuperación.",
                    "Registrar actividad, duración, esfuerzo, síntomas y ajustes para la siguiente sesión.",
                ),
                "Las tres partes se describen en [R2, pp. 94-95] y [R3, p. 29].",
            ),
            S(
                "4. Estiramientos con control",
                "Un estiramiento debe sentirse como tensión moderada, no como dolor agudo ni competencia.",
                (
                    "Mantener postura estable, respiración fluida y movimientos lentos; evitar rebotes no planificados.",
                    "No forzar articulaciones o posiciones complejas sin supervisión.",
                    "Osteoporosis, prótesis, cirugía reciente o alteraciones neurológicas requieren indicaciones individuales.",
                    "Detenerse ante dolor punzante, hormigueo nuevo, pérdida de fuerza, mareo o inestabilidad.",
                ),
                "Tipos de estiramiento en [R4, p. 40]; precauciones en [R5, pp. 13-14 y 103].",
            ),
            S(
                "5. Actividad en silla y apoyos",
                "La silla amplía participación, pero debe ser estable y formar parte de una adaptación consciente.",
                (
                    "Usar silla firme, sin ruedas y sobre superficie estable; evitar mobiliario móvil como apoyo.",
                    "Ajustar amplitud, palancas y tiempo; mantener posición segura y respiración cómoda.",
                    "Revisar bandas, bloques y materiales; no improvisar objetos inestables.",
                    "Yoga en silla y ejercicios sentados son opciones, no sustitutos universales de rehabilitación.",
                ),
                "Adaptaciones revisadas en [R6, pp. 7, 17, 34 y 38].",
            ),
            S(
                "6. Equilibrio, coordinación y juegos",
                "Los ejercicios multicomponente pueden mejorar función y reducir riesgo de caída cuando son progresivos y sostenidos.",
                (
                    "Practicar cerca de apoyo estable y con supervisión cuando exista riesgo elevado.",
                    "Progresar una variable a la vez: base, velocidad, dirección, alcance o tarea cognitiva.",
                    "Los juegos integran movimiento, memoria, comunicación y relación social si se adaptan.",
                    "Después de una caída, buscar causas y recuperar confianza con un plan; evitar todo movimiento perpetúa el miedo.",
                ),
                "Equilibrio en [R7, pp. 2 y 5-6]; juegos integrados en [R3, pp. 214 y 312].",
            ),
        ),
        "actions": (
            ("Continuar adaptando", "Esfuerzo moderado, respiración controlada y recuperación esperada.", "Mantener técnica, pausas y progresión gradual."),
            ("Detener y consultar", "Dolor nuevo, mareo recurrente, fatiga desproporcionada, caída o pérdida de capacidad.", "Suspender progresión y solicitar valoración."),
            ("Atención urgente", "Dolor torácico, falta de aire intensa, desmayo, debilidad súbita, habla alterada o caída con lesión grave.", "Activar emergencias locales."),
        ),
        "references": (
            R("R1", "AAMIA_guia_abierta_para_el_cuidado.pdf", "5", "Guía abierta"),
            R("R2", "Tercera edad actividad física y salud (Pont Geis, Pilar).pdf", "65, 94-95", "Libro de actividad física"),
            R("R3", "Juegos de motricidad para la tercera edad (Cancela Carral, José María).pdf", "29-30, 214, 312", "Libro de actividades"),
            R("R4", "Anatomía  estiramientos para la tercera edad (Portal Torices, María José).pdf", "40", "Libro de estiramientos"),
            R("R5", "Ejercicios De Estiramiento Para Mayores De 60 Años Ejercicios Simples Para Recuperar La Flexibilidad, Reducir La Rigidez,… (Michael Smith).pdf", "13-14, 103", "Guía práctica"),
            R("R6", "Yoga en silla para mayores de 60 años Ejercicios sencillos para vivir sin dolor, recuperar el equilibrio, la flexibilidad y la… (Michael Smith  Nathalie Seaton).pdf", "7, 17, 34, 38", "Guía práctica"),
            R("R7", "Ejercicios de equilibrio y coordinación en el adulto mayor con riesgo de caída.pdf", "2, 5-6", "Artículo original, 2021"),
            R("R8", "Estimulación múltiple en adultos mayores estrategias (Arévalo Herrera, Diana M.).pdf", "46-47", "Manual de intervención"),
            R("R9", "Cambios-fisiol-gicos-asociados-al-envejeci_2012_Revista-M-dica-Cl-nica-Las-C.pdf", "7", "Revisión clínica, 2012"),
            R("R10", "MANUAL_BASICO_CUIDADO_PERSONAS_ADULTAS_MAYORES_16_JULIO_221021.pdf", "94, 121", "Manual institucional"),
            R("R11", "Manual_cuidados-generales.pdf", "28", "Manual práctico"),
        ),
        "context": (
            "Transcripción video de YouTube - Cuidado básico del adulto mayor webinar.md (actividad, independencia y fragilidad; no indexado).",
        ),
    },
    {
        "number": 5,
        "slug": "memoria_bienestar_y_relaciones_humanas",
        "title": "Memoria, bienestar y relaciones humanas",
        "subtitle": "Cognición, comunicación, ánimo, vínculos, espiritualidad, dignidad y redes",
        "audience": "Personas mayores, familias, cuidadores y equipos comunitarios",
        "keywords": (
            "memoria", "atención", "estimulación cognitiva", "depresión",
            "comunicación", "familia", "espiritualidad", "dignidad",
        ),
        "principles": (
            "La persona conserva identidad, historia y derechos aunque cambien memoria o función.",
            "La estimulación útil tiene significado, elección y conexión; no es un examen permanente.",
            "Depresión, aislamiento y pérdida funcional se influyen entre sí y son tratables.",
            "La espiritualidad se incorpora solo según creencias y preferencias de la persona.",
        ),
        "sections": (
            S(
                "1. Cambios de memoria: observar el impacto",
                "Un olvido aislado no equivale a demencia. Preocupa más el cambio progresivo que interfiere con tareas o el cambio súbito.",
                (
                    "Observar dificultad nueva para manejar dinero, medicamentos, rutas, conversaciones, cocina o citas.",
                    "Registrar inicio, frecuencia, ejemplos y relación con sueño, dolor, ánimo, infección o medicamentos.",
                    "Consultar ante deterioro progresivo o preocupación de la persona o familia.",
                    "Confusión súbita, somnolencia inusual o fluctuación marcada requieren valoración pronta.",
                ),
                "Diferenciación y planificación en [R1, pp. 2 y 7], [R4, pp. 47 y 92] y el contexto editorial.",
            ),
            S(
                "2. Estimulación cognitiva con propósito",
                "Las actividades se ajustan a intereses y capacidad para evitar frustración.",
                (
                    "Usar conversación sobre historia personal, música, lectura, fotografías, listas, juegos o tareas conocidas.",
                    "Combinar memoria, atención, lenguaje, percepción y movimiento en sesiones breves.",
                    "Reducir distractores, presentar una tarea a la vez y aumentar dificultad solo si sigue siendo positiva.",
                    "Conservar actividades sociales y diarias; practicar no significa corregir cada error.",
                ),
                "Atención y ejercicios en [R2, pp. 16 y 28]; estimulación múltiple en [R3, pp. 39-40 y 47].",
            ),
            S(
                "3. Comunicación respetuosa",
                "La forma de hablar puede reducir ansiedad y facilitar participación.",
                (
                    "Acercarse de frente, presentarse si hace falta, usar frases claras y dar tiempo para responder.",
                    "Ofrecer una instrucción por vez y apoyar con gestos sin usar tono infantil.",
                    "Validar la emoción aunque el recuerdo sea impreciso; evitar discutir solo para demostrar quién tiene razón.",
                    "Revisar audición, visión, dolor, hambre, baño y ambiente antes de llamar oposición a una conducta.",
                ),
                "Comunicación y empatía en [R1, p. 7], [R13, p. 101] y manuales citados en los resúmenes 1 y 2.",
            ),
            S(
                "4. Ánimo, depresión y participación",
                "La depresión no es una consecuencia normal de envejecer y puede verse como irritabilidad, aislamiento, menor interés o pérdida funcional.",
                (
                    "Observar tristeza persistente, ansiedad, cansancio, desesperanza y cambios de sueño o apetito.",
                    "Mantener contacto, movimiento y actividades significativas sin exigir que la persona se anime.",
                    "Solicitar valoración; dolor, medicamentos, enfermedad y pérdidas recientes pueden contribuir.",
                    "Ante ideas de muerte o autolesión, no dejar sola a la persona y buscar ayuda urgente.",
                ),
                "Relación entre depresión y función en [R5, pp. 2, 5 y 7-8]; ánimo en [R4, pp. 40 y 193].",
            ),
            S(
                "5. Propósito, participación y vínculos",
                "Bienestar incluye agencia, relaciones y actividades valiosas dentro de las posibilidades actuales.",
                (
                    "Preguntar qué desea conservar, aprender, enseñar o compartir.",
                    "Favorecer grupos, voluntariado, cultura, contacto intergeneracional y tareas con propósito.",
                    "Hablar de expectativas, tareas, dinero, decisiones médicas y descansos antes de una crisis familiar.",
                    "Reconocer que algunos cuidadores también son mayores y necesitan apoyos propios.",
                ),
                "Participación en [R4, pp. 11 y 31], vínculos en [R7, p. 107] y cuidado intergeneracional en [R8, pp. 1, 3 y 5].",
            ),
            S(
                "6. Espiritualidad sin imposición",
                "La espiritualidad puede relacionarse con sentido, esperanza, conexión, religión o valores no religiosos.",
                (
                    "Preguntar si desea incorporar alguna creencia, práctica, comunidad o persona al cuidado.",
                    "Facilitar privacidad, objetos, música o contacto comunitario cuando lo solicite.",
                    "No interpretar sufrimiento solo como problema espiritual ni sustituir atención clínica.",
                    "Respetar también el deseo de no participar en prácticas religiosas.",
                ),
                "Cuidado espiritual y límites conceptuales en [R6, pp. 5-6].",
            ),
            S(
                "7. Dignidad y decisiones difíciles",
                "La capacidad puede ser específica para cada decisión y no desaparece por edad o diagnóstico.",
                (
                    "Explicar opciones de manera comprensible y apoyar participación máxima.",
                    "Conocer valores, prioridades y voluntades anticipadas antes de una crisis.",
                    "En demencia avanzada, decisiones clínicas requieren evaluación, representación válida y consideración de deseos previos.",
                    "Restricción, institucionalización o manejo de finanzas exige salvaguardas y revisión.",
                ),
                "Dignidad en [R9, p. 6] y decisiones en [R12, pp. 1 y 3-4]; enfoque integral en [R13, p. 128].",
            ),
        ),
        "actions": (
            ("Acompañar", "Olvidos ocasionales sin pérdida de función, tristeza transitoria o necesidad de más tiempo.", "Adaptar ambiente, mantener participación y observar cambios."),
            ("Consultar", "Deterioro progresivo, aislamiento, pérdida de interés, alucinaciones nuevas o dificultad en tareas conocidas.", "Solicitar valoración con ejemplos, cronología y medicamentos."),
            ("Atención urgente", "Confusión súbita, riesgo de autolesión, violencia, incapacidad para estar a salvo o deterioro rápido.", "Permanecer, reducir riesgos y contactar emergencias o crisis."),
        ),
        "references": (
            R("R1", "AAMIA_guia_abierta_para_el_cuidado.pdf", "2, 7", "Guía abierta"),
            R("R2", "Cómo mejorar la memoria y la atención en estudiantes y adultos mayores (Fau, Mauricio Enrique).pdf", "16, 22, 28", "Guía práctica"),
            R("R3", "Estimulación múltiple en adultos mayores estrategias (Arévalo Herrera, Diana M.).pdf", "39-40, 47", "Manual de intervención"),
            R("R4", "Envejecer con alegría guía para acompañar y vivir la tercera edad (Montoya Carrasquilla, Jorge).pdf", "11, 31, 40, 47, 92, 102-105, 183, 193", "Libro de consulta"),
            R("R5", "Comprendiendo el impacto de los síntomas depresivos en la funcionalidad de las personas mayores.pdf", "2, 5, 7-8", "Revisión clínica, 2017"),
            R("R6", "13-cuidado_espiritual.pdf", "5-6", "Artículo de reflexión, 2020"),
            R("R7", "Salud, familias y vínculos en el mundo de los adultos mayores (Elsa López  López, Elsa).pdf", "107", "Libro académico"),
            R("R8", "Hijos-adultos-mayores-al-cuidado-de-sus-padres--_2012_Revista-M-dica-Cl-nica.pdf", "1, 3, 5", "Artículo psicosocial, 2012"),
            R("R9", "Reflexiones-sobre-calidad-de-vida--dignidad-y-_2012_Revista-M-dica-Cl-nica-L.pdf", "6", "Revisión ética, 2012"),
            R("R10", "El-viejo-y-su-tiempo--Hacia-una--tica-de-la-r_2012_Revista-M-dica-Cl-nica-La.pdf", "1-5", "Ensayo ético, 2012"),
            R("R11", "Una-visi-n-optimista-del-envejecimient_2012_Revista-M-dica-Cl-nica-Las-Conde.pdf", "1-2", "Ensayo, 2012"),
            R("R12", "Toma-de-decisiones-en-pacientes-con-demencia_2012_Revista-M-dica-Cl-nica-Las.pdf", "1, 3-4", "Revisión clínica y ética, 2012"),
            R("R13", "Viviendo la tercera edad un modelo integral de consejería para el buen envejecimiento (Montilla R., Esteban).pdf", "101, 128", "Libro de consejería"),
            R("R14", "Notas--Hombres-en-peligro-_2012_Revista-M-dica-Cl-nica-Las-Condes.pdf", "1-2", "Nota demográfica, 2012", "Contexto de género"),
        ),
        "context": (
            "Articulo web- Cuidado de adultos mayores en casa- Una guía integral.md (compañía, red y agotamiento; no indexado).",
            "Articulo web- Qué cuidados debo brindar a un adulto mayor.md (participación social; no indexado).",
            "Transcripción video de YouTube - Cuidado básico del adulto mayor webinar.md (memoria, autonomía, roles y enfoque integral; no indexado).",
        ),
        "excluded": (
            "Mujer-anciana-de-Arles--Vincent-van-gogh--19_2012_Revista-M-dica-Cl-nica-Las.pdf: comentario de portada sin evidencia para recomendaciones.",
        ),
    },
)


def _make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverKicker", fontName=FONT_BOLD, fontSize=10, leading=13,
        textColor=MINT_2, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="CoverTitle", fontName=FONT_BOLD, fontSize=28, leading=32,
        textColor=colors.white, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle", fontName=FONT, fontSize=13, leading=18,
        textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="H1", fontName=FONT_BOLD, fontSize=21, leading=25,
        textColor=GREEN, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="H2", fontName=FONT_BOLD, fontSize=13.5, leading=17,
        textColor=GREEN_2, spaceBefore=7, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="Body", fontName=FONT, fontSize=9.6, leading=14,
        textColor=INK, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="AamiaBullet", fontName=FONT, fontSize=9.4, leading=13.6,
        textColor=INK, leftIndent=12, bulletIndent=1, spaceAfter=4.5,
    ))
    styles.add(ParagraphStyle(
        name="Evidence", fontName=FONT, fontSize=8.2, leading=11.5,
        textColor=GRAY, leftIndent=7, spaceBefore=3, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Small", fontName=FONT, fontSize=7.2, leading=9.2,
        textColor=GRAY, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="SmallBold", fontName=FONT_BOLD, fontSize=7.2, leading=9.2,
        textColor=GREEN, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="CenterSmall", fontName=FONT, fontSize=7.8, leading=10.5,
        textColor=GRAY, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="TableHead", fontName=FONT_BOLD, fontSize=8, leading=10,
        textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="TableBody", fontName=FONT, fontSize=7.6, leading=10.2,
        textColor=INK,
    ))
    return styles


STYLES = _make_styles()


def P(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(escape(text), STYLES[style])


def bullet(text: str) -> Paragraph:
    return Paragraph(escape(text), STYLES["AamiaBullet"], bulletText="•")


def callout(title: str, body: str, color=GREEN, background=CREAM) -> Table:
    table = Table([[[P(title, "SmallBold"), P(body)]]], colWidths=[166 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.9, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def header_footer(summary: dict):
    def draw(canvas, doc) -> None:
        canvas.saveState()
        width, height = A4
        if doc.page > 1:
            canvas.setFillColor(GREEN)
            canvas.rect(0, height - 14 * mm, width, 14 * mm, fill=1, stroke=0)
            canvas.setFillColor(colors.white)
            canvas.setFont(FONT_BOLD, 8.3)
            canvas.drawString(18 * mm, height - 9 * mm, f"AAMIA · Resumen temático {summary['number']}")
            canvas.setFont(FONT, 7.4)
            canvas.drawRightString(width - 18 * mm, height - 9 * mm, summary["title"])
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
        canvas.setFillColor(GRAY)
        canvas.setFont(FONT, 7.3)
        canvas.drawString(18 * mm, 9.4 * mm, "Síntesis educativa · Fuentes y páginas al final · Julio 2026")
        canvas.drawRightString(width - 18 * mm, 9.4 * mm, str(doc.page))
        canvas.restoreState()
    return draw


def cover(summary: dict) -> list:
    cover_box = Table([[([
        P(f"AAMIA · RESUMEN TEMÁTICO {summary['number']} DE 5", "CoverKicker"),
        P(summary["title"], "CoverTitle"),
        P(summary["subtitle"], "CoverSubtitle"),
    ])]], colWidths=[170 * mm], rowHeights=[105 * mm])
    cover_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
    ]))
    chips = Table(
        [[P(word, "CenterSmall") for word in summary["keywords"][:3]]],
        colWidths=[55 * mm] * 3,
    )
    chips.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MINT),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [
        Spacer(1, 6 * mm), cover_box, Spacer(1, 9 * mm), chips, Spacer(1, 7 * mm),
        P(f"Audiencia: {summary['audience']}", "Small"),
        callout(
            "Uso responsable",
            "Este documento organiza y resume una biblioteca local. No diagnostica, no prescribe y no sustituye una valoración profesional. Las fuentes originales son la evidencia canónica; las referencias usan la página física del PDF.",
            CORAL, CORAL_LIGHT,
        ),
        Spacer(1, 6 * mm), P("Edición 1.0 · Julio de 2026 · Proyecto AAMIA", "Small"),
        PageBreak(),
    ]


def intro_page(summary: dict) -> list:
    rows = [[P("Campo", "TableHead"), P("Valor", "TableHead")],
        [P("Tema principal", "TableBody"), P(summary["title"], "TableBody")],
        [P("Temas de recuperación", "TableBody"), P(", ".join(summary["keywords"]), "TableBody")],
        [P("Tipo de fuente", "TableBody"), P("Resumen secundario; remite a evidencia original", "TableBody")],
        [P("Riesgo clínico", "TableBody"), P("Mixto: educativo con señales de consulta y urgencia", "TableBody")],
        [P("Contexto Markdown", "TableBody"), P("Usado para redactar; no es documento indexado", "TableBody")],
    ]
    table = Table(rows, colWidths=[43 * mm, 123 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("BACKGROUND", (0, 1), (0, -1), MINT),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [
        P("Cómo usar este resumen", "H1"),
        P("Está diseñado para recuperación aumentada: cada apartado concentra una intención de búsqueda y conserva referencias legibles. Para decisiones importantes se consulta la fuente original y al equipo profesional."),
        table, Spacer(1, 6 * mm), P("Principios de síntesis", "H2"),
        *[bullet(item) for item in summary["principles"]], Spacer(1, 3 * mm),
        callout(
            "Jerarquía de uso",
            "1) localizar el tema; 2) recuperar los fragmentos originales; 3) responder indicando documento y página; 4) reconocer cuando la biblioteca no basta.",
        ),
        PageBreak(),
    ]


def section_pages(summary: dict) -> list:
    story: list = []
    for index, section in enumerate(summary["sections"]):
        block = [P(section["title"], "H2"), P(section["intro"])]
        block.extend(bullet(item) for item in section["bullets"])
        block.append(P(section["evidence"], "Evidence"))
        story.append(KeepTogether(block))
        if index in {2, 5} and index < len(summary["sections"]) - 1:
            story.append(PageBreak())
    story.append(PageBreak())
    return story


def action_page(summary: dict) -> list:
    rows = [[P("Nivel", "TableHead"), P("Situación", "TableHead"), P("Acción", "TableHead")]]
    rows.extend([[P(a, "TableBody"), P(b, "TableBody"), P(c, "TableBody")] for a, b, c in summary["actions"]])
    table = Table(rows, colWidths=[33 * mm, 67 * mm, 66 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GRAY),
        ("BACKGROUND", (0, 2), (-1, 2), CREAM),
        ("BACKGROUND", (0, 3), (-1, 3), CORAL_LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return [
        P("Orientación por nivel de acción", "H1"),
        P("Esta tabla no es un sistema de triaje. Resume una respuesta conservadora a cambios comunes y señales de peligro."),
        table, Spacer(1, 7 * mm),
        callout(
            "Regla de seguridad",
            "Cuando el cambio es súbito, intenso, empeora rápido o la persona no puede mantenerse a salvo, se prioriza ayuda humana inmediata sobre la consulta al RAG.",
            CORAL, CORAL_LIGHT,
        ),
        Spacer(1, 8 * mm), P("Qué debe conservar una respuesta de AAMIA", "H2"),
        bullet("Diferenciar educación general de indicaciones personalizadas."),
        bullet("Mostrar fuentes originales y páginas que sostienen la respuesta."),
        bullet("Declarar incertidumbre, antigüedad o desacuerdo entre fuentes."),
        bullet("No transformar procedimientos clínicos en instrucciones domésticas."),
        bullet("Recordar que autonomía, preferencias y contexto importan."),
        PageBreak(),
    ]


def reference_pages(summary: dict) -> list:
    story: list = [
        P("Fuentes utilizadas", "H1"),
        P("Las páginas son páginas físicas del PDF. Las referencias documentan conceptos centrales; no implican adoptar toda afirmación de la fuente."),
        callout(
            "Criterio editorial",
            "Se priorizaron recomendaciones convergentes, prudentes y aplicables. Las fuentes antiguas o especializadas se conservaron como contexto cuando requerían corroboración actual.",
            GOLD, CREAM,
        ),
        Spacer(1, 5 * mm),
    ]
    for code, title, pages, source_type, note in summary["references"]:
        detail = f"Páginas PDF: {pages}. Tipo: {source_type}."
        if note:
            detail += f" Nota: {note}."
        story.append(KeepTogether([
            P(f"[{code}] {title}", "SmallBold"), P(detail, "Small"), Spacer(1, 0.5 * mm),
        ]))
    if summary.get("context"):
        story.extend([
            Spacer(1, 4 * mm), P("Contexto editorial no indexado", "H2"),
            P("Estos Markdown ayudaron a contrastar lenguaje y necesidades domésticas. No se incorporan al índice ni a la carga pública.", "Small"),
            *[bullet(item) for item in summary["context"]],
        ])
    if summary.get("excluded"):
        story.extend([
            Spacer(1, 3 * mm), P("Archivos revisados y no usados como evidencia", "H2"),
            *[bullet(item) for item in summary["excluded"]],
        ])
    return story


def build_summary(summary: dict) -> Path:
    CORPUS_OUTPUT.mkdir(parents=True, exist_ok=True)
    DELIVERY_OUTPUT.mkdir(parents=True, exist_ok=True)
    filename = f"{summary['number']:02d}_{summary['slug']}.pdf"
    target = CORPUS_OUTPUT / filename
    doc = BaseDocTemplate(
        str(target), pagesize=A4,
        leftMargin=22 * mm, rightMargin=22 * mm, topMargin=20 * mm, bottomMargin=19 * mm,
        title=f"AAMIA - {summary['title']}", author="Proyecto AAMIA",
        subject=summary["subtitle"], keywords=", ".join(summary["keywords"]),
        creator="Proyecto AAMIA - síntesis temática para RAG",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates(PageTemplate(
        id="aamia-summary", frames=[frame], onPageEnd=header_footer(summary),
    ))
    story = [
        *cover(summary), *intro_page(summary), *section_pages(summary),
        *action_page(summary), *reference_pages(summary),
    ]
    doc.build(story)
    shutil.copy2(target, DELIVERY_OUTPUT / filename)
    return target


def main() -> int:
    for summary in SUMMARIES:
        print(build_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
