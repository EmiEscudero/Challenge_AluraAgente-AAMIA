"""Generate the openly licensed starter guide bundled with AAMIA."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
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
OUTPUT = ROOT / "docs" / "AAMIA_guia_abierta_para_el_cuidado.pdf"

GREEN = colors.HexColor("#185C4A")
GREEN_2 = colors.HexColor("#267A64")
MINT = colors.HexColor("#E9F4EF")
CREAM = colors.HexColor("#FBF8F0")
CORAL = colors.HexColor("#DC6B4D")
INK = colors.HexColor("#19332C")
GRAY = colors.HexColor("#52635D")
LINE = colors.HexColor("#D8E8DF")


def _register_fonts() -> tuple[str, str]:
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("AAMIA-Regular", regular))
        pdfmetrics.registerFont(TTFont("AAMIA-Bold", bold))
        return "AAMIA-Regular", "AAMIA-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = _register_fonts()


def _header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setFillColor(GREEN)
        canvas.rect(0, height - 15 * mm, width, 15 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(FONT_BOLD, 9)
        canvas.drawString(18 * mm, height - 9.5 * mm, "AAMIA  ·  Apoyo al Adulto Mayor IA")
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFillColor(GRAY)
    canvas.setFont(FONT, 8)
    canvas.drawString(18 * mm, 9.5 * mm, "Guía educativa · CC BY 4.0 · Julio 2026")
    canvas.drawRightString(width - 18 * mm, 9.5 * mm, f"{doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="AamiaTitle",
        parent=styles["Title"],
        fontName=FONT_BOLD,
        fontSize=31,
        leading=35,
        textColor=colors.white,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="AamiaSubtitle",
        parent=styles["Normal"],
        fontName=FONT,
        fontSize=14,
        leading=20,
        textColor=colors.white,
    )
)
styles.add(
    ParagraphStyle(
        name="AamiaH1",
        parent=styles["Heading1"],
        fontName=FONT_BOLD,
        fontSize=23,
        leading=28,
        textColor=GREEN,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="AamiaH2",
        parent=styles["Heading2"],
        fontName=FONT_BOLD,
        fontSize=14,
        leading=18,
        textColor=GREEN_2,
        spaceBefore=8,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="AamiaBody",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=10.5,
        leading=15.5,
        textColor=INK,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="AamiaBullet",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=10.2,
        leading=14.5,
        leftIndent=12,
        firstLineIndent=-7,
        bulletIndent=0,
        textColor=INK,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="AamiaSmall",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=8.4,
        leading=11.5,
        textColor=GRAY,
        spaceAfter=4,
    )
)


def p(text: str, style: str = "AamiaBody") -> Paragraph:
    return Paragraph(text, styles[style])


def bullets(items: list[str]) -> list[Paragraph]:
    return [p(f"• {item}", "AamiaBullet") for item in items]


def callout(title: str, body: str, color=GREEN) -> Table:
    content = Paragraph(
        f'<font name="{FONT_BOLD}" color="{color.hexval()}">{title}</font><br/>{body}',
        styles["AamiaBody"],
    )
    table = Table([[content]], colWidths=[168 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CREAM),
                ("BOX", (0, 0), (-1, -1), 1, color),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def section(title: str, intro: str, items: list[str]) -> list:
    return [p(title, "AamiaH2"), p(intro), *bullets(items)]


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=19 * mm,
        title="AAMIA: guía abierta para acompañar el cuidado cotidiano",
        author="Proyecto AAMIA",
        subject="Cuidados generales, alimentación, movilidad y seguridad de personas adultas mayores",
        keywords="adultos mayores, cuidados, alimentación, ejercicio, seguridad, CC BY 4.0",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates(PageTemplate(id="aamia", frames=[frame], onPageEnd=_header_footer))

    story = []

    cover = Table(
        [[p("AAMIA", "AamiaTitle")], [p("Apoyo al Adulto Mayor con Inteligencia Artificial", "AamiaSubtitle")]],
        colWidths=[170 * mm],
        rowHeights=[52 * mm, 38 * mm],
    )
    cover.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN),
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    story.extend(
        [
            Spacer(1, 9 * mm),
            cover,
            Spacer(1, 14 * mm),
            p("Guía abierta para acompañar el cuidado cotidiano", "AamiaH1"),
            p(
                "Una referencia breve para familias y personas cuidadoras sobre observación inicial, "
                "alimentación, movimiento seguro, prevención de caídas y organización del cuidado.",
            ),
            Spacer(1, 7 * mm),
            callout(
                "Uso responsable",
                "Este material es educativo. No diagnostica, no prescribe tratamientos y no sustituye al personal de salud. "
                "Adapta cualquier recomendación a la capacidad, preferencias e indicaciones clínicas de la persona.",
                CORAL,
            ),
            Spacer(1, 9 * mm),
            p("Edición 1.0 · Julio de 2026", "AamiaSmall"),
            p(
                "Licencia Creative Commons Atribución 4.0 Internacional (CC BY 4.0). "
                "Puedes copiar y adaptar esta guía si atribuyes al Proyecto AAMIA e indicas los cambios.",
                "AamiaSmall",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("1. Cuidar comienza por conocer a la persona", "AamiaH1"),
            p(
                "No existe una única forma de envejecer. Un buen plan parte de lo que la persona puede y quiere hacer, "
                "de sus rutinas y de las barreras de su entorno. El objetivo es apoyar sin quitar autonomía. [1]",
            ),
            *section(
                "Antes de ayudar",
                "Habla con calma y pide permiso. Explica cada paso antes de tocar, mover o cambiar la rutina.",
                [
                    "Pregunta cómo prefiere ser llamada y qué actividades desea realizar por sí misma.",
                    "Identifica dificultades de visión, audición, movilidad, memoria, deglución o comunicación.",
                    "Ten a mano contactos de familia, personal de salud y servicios de emergencia locales.",
                    "Registra alergias, diagnósticos y medicamentos exactamente como fueron indicados; no ajustes dosis por cuenta propia.",
                ],
            ),
            *section(
                "Cambios que merecen atención",
                "Compara con el estado habitual, no sólo con una lista genérica.",
                [
                    "Confusión nueva, somnolencia inusual, caída o debilidad repentina.",
                    "Falta de aire, dolor fuerte o persistente, fiebre, vómitos repetidos o sangrado.",
                    "Dificultad nueva para comer o beber, menos orina, boca muy seca o rechazo sostenido de alimentos.",
                    "Cambios marcados en ánimo, conducta, sueño o capacidad para las tareas cotidianas.",
                ],
            ),
            Spacer(1, 5 * mm),
            callout(
                "Posible urgencia",
                "Ante pérdida de conciencia, dificultad intensa para respirar, dolor torácico, sangrado que no cede o signos súbitos "
                "como rostro caído, debilidad de un brazo o habla alterada, contacta de inmediato a los servicios de emergencia locales. "
                "No esperes una respuesta de una aplicación.",
                CORAL,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("2. Rutina de cuidados cotidianos", "AamiaH1"),
            p(
                "Una rutina predecible reduce olvidos y facilita detectar cambios. Debe ser flexible: la energía y las necesidades "
                "pueden variar cada día.",
            ),
            *section(
                "Al comenzar el día",
                "Observa sin invadir y conversa sobre cómo se siente.",
                [
                    "Comprueba orientación, ánimo, dolor, respiración y capacidad para levantarse respecto del día anterior.",
                    "Ofrece tiempo suficiente para aseo, vestido y baño; prepara los objetos en el orden de uso.",
                    "Favorece ropa cómoda y calzado cerrado, firme y antideslizante.",
                    "Revisa que lentes, auxiliares auditivos, bastón o andadera estén limpios, disponibles y en buen estado.",
                ],
            ),
            *section(
                "Durante el día",
                "Combina actividad, descanso, alimentación y contacto social.",
                [
                    "Mantén agua y objetos de uso frecuente al alcance, según las restricciones indicadas por profesionales.",
                    "Propón tareas con propósito: doblar ropa, regar plantas, conversar, escuchar música o caminar acompañado.",
                    "Evita hacer por la persona lo que todavía puede realizar con tiempo o una adaptación sencilla.",
                    "Revisa la piel expuesta a presión o humedad y solicita valoración si aparecen lesiones, dolor o enrojecimiento persistente.",
                ],
            ),
            *section(
                "Al cerrar el día",
                "Un registro corto ayuda a comunicar hechos, no impresiones.",
                [
                    "Anota alimentación, líquidos, actividad, evacuaciones, sueño, caídas, dolor y cambios relevantes.",
                    "Prepara iluminación nocturna y una ruta despejada hacia el baño.",
                    "Comparte novedades con la red de apoyo y consulta cuando un cambio sea nuevo, empeore o preocupe.",
                ],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("3. Alimentación e hidratación", "AamiaH1"),
            p(
                "La OMS resume una alimentación saludable en cuatro principios: adecuación, equilibrio, moderación y diversidad. "
                "La composición exacta debe adaptarse a salud, cultura, disponibilidad, apetito y actividad. [2]",
            ),
            *section(
                "Una base práctica",
                "Busca variedad y alimentos poco procesados, sin imponer un menú rígido.",
                [
                    "Incluye verduras y frutas, cereales integrales o tubérculos, leguminosas y fuentes de proteína apropiadas.",
                    "Prefiere preparaciones sencillas y limita productos con exceso de sodio, azúcares libres y grasas no saludables. [2]",
                    "Respeta preferencias y costumbres; comer acompañado puede mejorar la experiencia.",
                    "Sirve porciones manejables y ofrece más si la persona lo desea.",
                ],
            ),
            *section(
                "Comer con seguridad",
                "La tos, voz húmeda, atragantamiento o dificultad para masticar requieren valoración profesional.",
                [
                    "Procura una postura sentada y estable; evita alimentar a una persona somnolienta o acostada.",
                    "Verifica temperatura, textura, dentadura y utensilios; no modifiques consistencias sin orientación si existe disfagia.",
                    "Da tiempo para masticar y tragar. No apresures ni fuerces.",
                    "Mantén higiene de manos, superficies, alimentos y boca.",
                ],
            ),
            *section(
                "Hidratación",
                "Ofrece líquidos de forma regular si no existe una restricción médica.",
                [
                    "Usa un vaso fácil de sujetar y deja agua visible y accesible.",
                    "Consulta ante rechazo persistente, orina muy escasa, mareo, debilidad o cambios agudos de atención.",
                    "En enfermedad renal, cardiaca u otras condiciones, sigue la cantidad indicada por el equipo tratante.",
                ],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("4. Movimiento, fuerza y equilibrio", "AamiaH1"),
            p(
                "La actividad regular favorece capacidad física y mental. Para personas mayores, la OMS recomienda combinar actividad "
                "aeróbica, fortalecimiento y ejercicios multicomponente de equilibrio y fuerza. [3]",
            ),
            *section(
                "Meta de referencia, no receta",
                "Cuando la salud y la capacidad lo permiten, la referencia poblacional es 150–300 minutos semanales de actividad "
                "aeróbica moderada; además, fuerza al menos dos días y trabajo multicomponente tres o más días. [3]",
                [
                    "Si hoy hay poca actividad, empieza con periodos breves y aumenta de forma gradual.",
                    "Caminar, bailar sentado o de pie, levantarse de una silla y tareas domésticas adaptadas también cuentan.",
                    "Intercala descanso y evita comparar el ritmo con el de otras personas.",
                    "Una persona con caída reciente, dolor, mareo o enfermedad descompensada necesita orientación antes de progresar.",
                ],
            ),
            *section(
                "Sesión sencilla y supervisada",
                "Elige un espacio estable, iluminado y sin obstáculos.",
                [
                    "Inicio: movimientos suaves y respiración cómoda.",
                    "Parte principal: una actividad que permita hablar, aunque con algo de esfuerzo; usa apoyo estable cuando haga falta.",
                    "Final: reduce el ritmo de forma progresiva y observa cómo se siente.",
                    "Suspende y pide ayuda si aparece dolor torácico, falta de aire intensa, desmayo, debilidad súbita o dolor agudo.",
                ],
            ),
            Spacer(1, 4 * mm),
            callout(
                "Dignidad y elección",
                "El movimiento no debe usarse como castigo ni imponerse. Ofrece opciones, escucha el cansancio y celebra la constancia, no el rendimiento.",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("5. Hogar seguro y prevención de caídas", "AamiaH1"),
            p(
                "Las caídas pueden causar lesiones importantes. Revisar el entorno y practicar fuerza y equilibrio reduce riesgos, pero "
                "ninguna medida sustituye una valoración cuando ya hubo caídas o mareos. [4]",
            ),
            *section(
                "Recorrido de seguridad",
                "Haz la revisión caminando por las rutas que la persona usa de día y de noche.",
                [
                    "Retira cables, tapetes sueltos, muebles bajos y objetos de zonas de paso.",
                    "Mejora la iluminación, especialmente en escaleras, entradas y ruta al baño.",
                    "Instala superficies antideslizantes y apoyos firmes donde sean necesarios; una toalla o mueble móvil no es un pasamanos.",
                    "Deja teléfono, agua y artículos frecuentes a una altura accesible, sin necesidad de bancos o escaleras.",
                    "Revisa que el calzado ajuste bien y que bastón o andadera tengan altura y mantenimiento adecuados.",
                ],
            ),
            *section(
                "Si ocurre una caída",
                "Mantén la calma y pregunta por dolor. No levantes de inmediato a la persona si hay dolor intenso, golpe en la cabeza, "
                "deformidad, sangrado, pérdida de conciencia o incapacidad para moverse.",
                [
                    "Contacta a emergencias ante signos graves o si no puedes valorar la situación con seguridad.",
                    "Aunque parezca estar bien, informa al equipo de salud si es una caída nueva o repetida.",
                    "Registra qué ocurrió antes, dónde, calzado, iluminación, síntomas y posibles obstáculos.",
                    "No atribuyas una caída simplemente a la edad: medicamentos, visión, presión arterial, infección o entorno pueden influir.",
                ],
            ),
            Spacer(1, 4 * mm),
            callout(
                "Baño",
                "Es una zona de alto riesgo. Prioriza piso seco, tapete antideslizante, iluminación, barras correctamente fijadas y objetos al alcance. [4]",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("6. Medicamentos, memoria y bienestar", "AamiaH1"),
            *section(
                "Medicamentos sin improvisar",
                "La organización reduce errores, pero cualquier cambio corresponde al equipo tratante.",
                [
                    "Mantén una lista actualizada con nombre, dosis, horario, motivo y profesional que indicó cada producto.",
                    "Incluye medicamentos sin receta, vitaminas, suplementos y productos herbolarios.",
                    "Usa un único sistema de recordatorio y registra la toma; no dupliques una dosis olvidada sin indicación.",
                    "No tritures tabletas ni abras cápsulas sin confirmar que sea seguro.",
                    "Solicita revisión si aparecen mareos, somnolencia, confusión, caídas o dificultad para seguir el esquema.",
                ],
            ),
            *section(
                "Memoria y comunicación",
                "Una rutina clara y un entorno amable suelen ayudar más que corregir repetidamente.",
                [
                    "Da una instrucción a la vez, deja tiempo para responder y reduce ruido de fondo.",
                    "Usa calendarios, etiquetas sencillas y objetos siempre en el mismo lugar.",
                    "Valida la emoción aunque el recuerdo sea impreciso; evita discutir para demostrar quién tiene razón.",
                    "Consulta ante confusión repentina: un cambio agudo no debe asumirse como parte normal del envejecimiento.",
                ],
            ),
            *section(
                "La persona cuidadora también necesita cuidado",
                "El cansancio sostenido afecta a ambas personas.",
                [
                    "Reparte tareas concretas y acuerda relevos antes de llegar al agotamiento.",
                    "Conserva tiempo para dormir, comer, moverte y hablar con alguien de confianza.",
                    "Busca apoyo profesional si hay desesperanza, irritabilidad persistente, aislamiento o sensación de no poder continuar.",
                    "Pedir ayuda es una medida de seguridad, no un fracaso.",
                ],
            ),
            PageBreak(),
        ]
    )

    sources = [
        (
            "[1] Organización Mundial de la Salud. Envejecimiento y salud (2025).",
            "https://www.who.int/es/news-room/fact-sheets/detail/ageing-and-health",
        ),
        (
            "[2] Organización Mundial de la Salud. Alimentación saludable (2026).",
            "https://www.who.int/es/news-room/fact-sheets/detail/healthy-diet",
        ),
        (
            "[3] Organización Mundial de la Salud. Actividad física.",
            "https://www.who.int/news-room/fact-sheets/detail/physical-activity",
        ),
        (
            "[4] MedlinePlus, Biblioteca Nacional de Medicina de EE. UU. Prevención de caídas.",
            "https://medlineplus.gov/spanish/ency/patientinstructions/000052.htm",
        ),
        (
            "[5] INAPAM. Manual de apoyo con el cuidado de personas adultas mayores (2024).",
            "https://www.gob.mx/inapam/documentos/122471",
        ),
    ]
    source_flowables = []
    for label, url in sources:
        source_flowables.append(
            KeepTogether(
                [
                    p(label, "AamiaBody"),
                    Paragraph(f'<link href="{url}" color="#267A64">{url}</link>', styles["AamiaSmall"]),
                    Spacer(1, 2 * mm),
                ]
            )
        )

    story.extend(
        [
            p("7. Plan breve y fuentes", "AamiaH1"),
            p("Completa este plan con la persona adulta mayor y su red de apoyo."),
            Table(
                [
                    [p("Prioridad de esta semana", "AamiaSmall"), ""],
                    [p("Actividad que desea conservar", "AamiaSmall"), ""],
                    [p("Riesgo del hogar que corregiremos", "AamiaSmall"), ""],
                    [p("Persona a quien pediremos apoyo", "AamiaSmall"), ""],
                    [p("Cambio que consultaremos", "AamiaSmall"), ""],
                ],
                colWidths=[60 * mm, 108 * mm],
                rowHeights=[14 * mm] * 5,
                style=TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                        ("BACKGROUND", (0, 0), (0, -1), MINT),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ]
                ),
            ),
            Spacer(1, 7 * mm),
            p("Fuentes de consulta", "AamiaH2"),
            *source_flowables,
            Spacer(1, 4 * mm),
            callout(
                "Licencia abierta",
                "© 2026 Proyecto AAMIA. Esta guía se ofrece bajo CC BY 4.0: "
                '<link href="https://creativecommons.org/licenses/by/4.0/deed.es" color="#185C4A">creativecommons.org/licenses/by/4.0/deed.es</link>. '
                "Atribución sugerida: “Proyecto AAMIA, Guía abierta para acompañar el cuidado cotidiano, versión 1.0”.",
            ),
        ]
    )

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
