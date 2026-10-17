#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el informe de la Actividad #1 (DSI - U1) en formato ODT."""

import os, re, sys, json, zipfile, struct
from xml.sax.saxutils import escape

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "diagrams", "png")
OUT = os.path.join(BASE, "Informe_DSI_U1_Rescate_Animal.odt")
PAGES_JSON = os.path.join(BASE, ".pages.json")

page_map = json.load(open(PAGES_JSON)) if os.path.exists(PAGES_JSON) else {}

# ---------------------------------------------------------------- imágenes
def img_size(name):
    with open(os.path.join(IMG, name), "rb") as f:
        head = f.read(33)
    w, h = struct.unpack(">II", head[16:24])
    return w, h

def fig_height(name, width_cm):
    w, h = img_size(name)
    return round(width_cm * h / w, 2)

# ---------------------------------------------------------------- helpers XML
def rich(t):
    t = escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r'<text:span text:style-name="TxtBold">\1</text:span>', t)
    t = re.sub(r"__(.+?)__", r'<text:span text:style-name="TxtItalic">\1</text:span>', t)
    return t

body = []
fig_n = [0]

def P(t="", style="Cuerpo"):
    body.append(f'<text:p text:style-name="{style}">{rich(t)}</text:p>')

def RAW(xml):
    body.append(xml)

def H1(t):
    body.append(f'<text:p text:style-name="H1">{rich(t)}</text:p>')

def H2(t):
    body.append(f'<text:p text:style-name="H2">{rich(t)}</text:p>')

def BULLETS(items):
    out = ['<text:list text:style-name="LVinetas">']
    for it in items:
        out.append(f'<text:list-item><text:p text:style-name="CuerpoLista">{rich(it)}</text:p></text:list-item>')
    out.append('</text:list>')
    body.append("".join(out))

def TABLE(headers, rows, widths):
    total = 15.9
    rel = [round(w / sum(widths) * total, 2) for w in widths]
    x = ['<table:table table:style-name="TablaBase">']
    for i, r in enumerate(rel):
        x.append(f'<table:table-column table:style-name="Col{i}" table:default-cell-style-name="CeldaNormal"/>')
    x.append('<table:table-row>')
    for h in headers:
        x.append(f'<table:table-cell table:style-name="CeldaEncabezado" office:value-type="string"><text:p text:style-name="TextoEncabezado">{rich(h)}</text:p></table:table-cell>')
    x.append('</table:table-row>')
    for row in rows:
        x.append('<table:table-row>')
        for c in row:
            x.append(f'<table:table-cell table:style-name="CeldaNormal" office:value-type="string"><text:p text:style-name="TextoCell">{rich(c)}</text:p></table:table-cell>')
        x.append('</table:table-row>')
    x.append('</table:table>')
    # columnas deben ir en automatic-styles -> se registran aparte
    for i, w in enumerate(rel):
        COLS.append(f'<style:style style:name="Col{i}" style:family="table-column"><style:table-column-properties style:column-width="{w}cm"/></style:style>')
    body.append("".join(x))
    body.append('<text:p text:style-name="EspacioTabla"></text:p>')

COLS = []
COLS.append('<style:style style:name="ColFigura" style:family="table-column"><style:table-column-properties style:column-width="15.9cm"/></style:style>')

def FIG(name, width_cm, titulo, note=""):
    fig_n[0] += 1
    n = fig_n[0]
    h = fig_height(name, width_cm)
    # La figura inicia en página nueva para que nunca se separe de su pie.
    body.append(
        f'<text:p text:style-name="FigPagina"><draw:frame draw:style-name="Marco" draw:name="Figura{n}" '
        f'text:anchor-type="as-char" svg:width="{width_cm}cm" svg:height="{h}cm">'
        f'<draw:image xlink:href="Pictures/{name}" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>'
        f'</draw:frame></text:p>')
    body.append(f'<text:p text:style-name="EtiquetaFigura">Figura {n}</text:p>')
    body.append(f'<text:p text:style-name="TituloFigura">{escape(titulo)}</text:p>')
    if note:
        P(note, "NotaFigura")

def FIGCAP(n_label, title, landscape=False, before=False, after=True):
    pass

# ---------------------------------------------------------------- portada
body.append('<text:p text:style-name="PortadaInicio">UNIVERSIDAD TÉCNICA DE MANABÍ</text:p>')
P("Facultad de Ciencias Informáticas", "PortadaCentro")
P("Carrera de Tecnologías de la Información en Línea", "PortadaCentro")
P("", "PortadaEspacio")
P("Asignatura: **Desarrollo de Sistemas Informáticos**", "PortadaCentro")
P("Unidad 1: Desarrollo de software. Introducción y paradigmas de diseño", "PortadaCentro")
P("", "PortadaEspacio")
P("Estudio de caso: diseño de la arquitectura lógica de un Sistema de Control de Rescate y Adopción Animal", "PortadaTitulo")
P("Actividad # 1 — Componente de aprendizaje asistido por el docente", "PortadaSubtitulo")
P("", "PortadaEspacio")
P("**Autor:** Cristopher Montoya", "PortadaCentro")
P("**Docente:** Ing. Jorge Arun Zambrano Cedeño, Mg.", "PortadaCentro")
P("**Periodo académico:** septiembre 2026 – enero 2027", "PortadaCentro")
P("**Fecha de entrega:** 17 de octubre de 2026", "PortadaCentro")
P("", "PortadaEspacio")
P("Repositorio: github.com/Cris-M10/sistema-rescate-adopcion-animal", "PortadaCentro")

# ---------------------------------------------------------------- índice
TOC = [
    (1, "1. Introducción"),
    (1, "2. Objetivos"),
    (1, "3. Análisis del problema"),
    (2, "3.1. Actores del sistema"),
    (2, "3.2. Requerimientos funcionales"),
    (2, "3.3. Requerimientos no funcionales"),
    (2, "3.4. Reglas de negocio"),
    (1, "4. Diseño del sistema"),
    (2, "4.1. Arquitectura general"),
    (2, "4.2. Diagrama de casos de uso"),
    (2, "4.3. Diagrama de clases"),
    (2, "4.4. Principios SOLID aplicados"),
    (2, "4.5. Máquina de estados del caso"),
    (1, "5. Patrones de diseño aplicados"),
    (2, "5.1. Singleton: GestorCasos"),
    (2, "5.2. Factory Method: ExpedienteFactory"),
    (2, "5.3. Observer: NotificadorRescates"),
    (2, "5.4. Modelo-Vista-Controlador (MVC)"),
    (2, "5.5. Interacción entre los patrones"),
    (1, "6. Flujo de trabajo con Gitflow"),
    (2, "6.1. Justificación del modelo"),
    (2, "6.2. Estructura de ramas"),
    (2, "6.3. Evidencia del historial"),
    (1, "7. Conclusiones"),
    (1, "8. Referencias"),
    (1, "Anexo A. Repositorio del proyecto"),
]

H1("Índice")
for lvl, txt in TOC:
    st = "Indice1" if lvl == 1 else "Indice2"
    pg = page_map.get(txt, "")
    body.append(f'<text:p text:style-name="{st}">{rich(txt)}<text:tab/>{pg}</text:p>')

# ---------------------------------------------------------------- 1
H1("1. Introducción")
P("El presente informe documenta el diseño de la arquitectura lógica de un Sistema de Control de Rescate y Adopción Animal, elaborado como Actividad # 1 de la Unidad 1 de la asignatura Desarrollo de Sistemas Informáticos. La problemática abordada es la gestión de casos en un refugio animal: el ingreso de animales rescatados —perros, gatos y fauna silvestre—, la asignación de voluntarios o veterinarios responsables y el seguimiento de los estados del proceso hasta el cierre del caso.")
P("El diseño se apoya en tres pilares. Primero, un análisis de requerimientos que identifica a los actores, las funciones esperadas y los atributos de calidad que debe cumplir la solución. Segundo, un modelo de diseño expresado en UML mediante diagramas de casos de uso, de clases y de secuencia, en los que se evidencia la relación entre los objetos bajo los principios SOLID. Tercero, la aplicación justificada de patrones de diseño de software, que permiten que la solución sea escalable, reutilizable y mantenible en el tiempo.")
P("Adicionalmente, el proyecto se gestiona en un repositorio público de GitHub bajo el modelo Gitflow. Cada avance se desarrolla en una rama __feature/__ y se integra a la rama __develop__ mediante fusiones explícitas, de modo que el historial de commits constituye por sí mismo la evidencia del flujo de trabajo profesional aplicado y de la trazabilidad de versiones exigida en la consigna.")

# ---------------------------------------------------------------- 2
H1("2. Objetivos")
P("**Objetivo general**")
P("Diseñar la arquitectura lógica de un sistema de gestión de rescate y adopción animal, aplicando patrones de diseño de software y el modelo de trabajo colaborativo Gitflow, como base para una solución escalable, reutilizable y mantenible.")
P("**Objetivos específicos**")
BULLETS([
    "Identificar los actores, los requerimientos funcionales y los requerimientos no funcionales del sistema.",
    "Elaborar los diagramas de casos de uso, de clases y de secuencia que representen el diseño propuesto.",
    "Aplicar y justificar al menos tres patrones de diseño de software, explicando el problema concreto que cada uno resuelve.",
    "Configurar un repositorio en GitHub con la estructura de ramas de Gitflow y documentar su historial como evidencia del flujo de trabajo.",
])

# ---------------------------------------------------------------- 3
H1("3. Análisis del problema")
P("Un refugio animal recibe reportes de animales en riesgo provenientes de ciudadanos, instituciones y patrullas de rescate. Cada reporte debe convertirse en un caso con un responsable asignado, un expediente clínico propio de la especie y un estado que refleje el avance del proceso. Cuando esta gestión se realiza de forma manual —mensajes de texto, hojas de cálculo y cuadernos— se producen casos duplicados, pérdida de trazabilidad, notificaciones tardías a los voluntarios y ausencia de indicadores para la toma de decisiones. El sistema debe resolver esos problemas mediante un modelo de dominio claro y una arquitectura que permita crecer en número de casos, de refugios y de usuarios sin rediseñar el núcleo.")

H2("3.1. Actores del sistema")
P("Se identifican tres actores con responsabilidades diferenciadas sobre los casos de rescate:")
TABLE(["Actor", "Responsabilidad dentro del sistema"],
      [["Ciudadano / Reportante", "Registra el reporte de un animal en riesgo, adjunta ubicación y evidencia, y consulta el estado de su reporte."],
       ["Voluntario / Veterinario", "Consulta los casos asignados, atiende el rescate, registra el tratamiento y actualiza el estado clínico del caso."],
       ["Administrador del Refugio", "Gestiona usuarios y roles, asigna responsables, valida transiciones de estado y consulta indicadores de gestión."]],
      [26, 74])

H2("3.2. Requerimientos funcionales")
TABLE(["ID", "Requerimiento", "Prioridad"],
      [["RF-01", "Crear un caso de rescate con ubicación, descripción y evidencia fotográfica.", "Alta"],
       ["RF-02", "Categorizar la especie del animal: perro, gato o fauna silvestre.", "Alta"],
       ["RF-03", "Asignar un voluntario o veterinario responsable al caso.", "Alta"],
       ["RF-04", "Gestionar los estados del caso: Rescatado, En tratamiento, Adopción, Liberación y Cerrado.", "Alta"],
       ["RF-05", "Notificar automáticamente a los voluntarios disponibles cuando ingresa un nuevo rescate.", "Media"],
       ["RF-06", "Registrar el historial de cambios de estado de cada caso para efectos de auditoría.", "Media"],
       ["RF-07", "Generar un expediente clínico diferenciado según la especie del animal.", "Media"],
       ["RF-08", "Consultar indicadores: casos abiertos, tiempo medio de atención y adopciones del periodo.", "Baja"]],
      [8, 72, 20])

H2("3.3. Requerimientos no funcionales")
TABLE(["ID", "Requerimiento", "Criterio de verificación"],
      [["RNF-01", "Escalabilidad", "El sistema admite el crecimiento del número de casos y de refugios sin rediseñar el núcleo de dominio."],
       ["RNF-02", "Mantenibilidad", "Cada módulo es sustituible de forma aislada y el núcleo cuenta con pruebas automatizadas."],
       ["RNF-03", "Trazabilidad de versiones", "Todo cambio queda registrado en una rama __feature/__ y se integra mediante una fusión explícita y revisable."],
       ["RNF-04", "Seguridad", "Autenticación basada en roles; el reportante anónimo solo accede a su propio reporte."],
       ["RNF-05", "Usabilidad", "El registro de un rescate se completa en menos de dos minutos desde un dispositivo móvil."]],
      [10, 26, 64])

H2("3.4. Reglas de negocio")
BULLETS([
    "Un caso no puede pasar a **Adopción** sin haber estado previamente en **En tratamiento**.",
    "Un caso solo puede tener un responsable activo a la vez; la reasignación deja registro en el historial.",
    "Todo cambio de estado genera un evento de dominio que alimenta el sistema de notificaciones.",
    "La fauna silvestre no puede pasar a **Adopción**: su estado final es **Liberación**.",
    "El cierre de un caso es irreversible y exige un motivo registrado por el administrador.",
])

# ---------------------------------------------------------------- 4
H1("4. Diseño del sistema")
P("El diseño se organiza en cuatro capas con dependencias dirigidas siempre hacia el dominio: presentación, aplicación, dominio e infraestructura. La interfaz y la persistencia conocen al dominio, pero el dominio no conoce a ninguna de ellas, lo que materializa el principio de inversión de dependencias y permite sustituir la base de datos o el canal de notificación sin tocar las reglas de negocio.")

H2("4.1. Arquitectura general")
P("La capa de **presentación** implementa el patrón Modelo-Vista-Controlador: el controlador recibe la petición, la traduce en un comando de aplicación y selecciona la vista que se devolverá al usuario, sin contener reglas de negocio. La capa de **aplicación** agrupa los casos de uso (registrar rescate, asignar responsable, cambiar estado, notificar); cada servicio orquesta el dominio y la persistencia. La capa de **dominio** concentra las entidades, los objetos de valor y los patrones de diseño: el motor de casos, la fábrica de expedientes y el notificador de eventos. Finalmente, la capa de **infraestructura** implementa los repositorios y los servicios externos de correo y notificaciones push.")
P("El flujo de versiones acompaña esta estructura: cada capa evoluciona en ramas __feature/__ independientes, de modo que las fusiones hacia __develop__ rara vez producen conflictos y la rama __release/__ congela el alcance de la entrega.")
FIG("05-arquitectura.png", 15.2, "Arquitectura general en capas y su integración con el flujo de versiones")

H2("4.2. Diagrama de casos de uso")
P("El diagrama de casos de uso representa las interacciones de los tres actores con la plataforma. El ciudadano registra el reporte —caso de uso que incluye la categorización de la especie— y consulta el estado de su caso. El voluntario o veterinario consulta los casos asignados, registra el tratamiento y actualiza el estado, lo que a su vez incluye el envío de notificaciones. El administrador asigna responsables, gestiona usuarios y roles y consulta los indicadores de gestión.")
FIG("01-casos-uso.png", 14.4, "Diagrama de casos de uso del sistema")

H2("4.3. Diagrama de clases")
P("El modelo de clases se organiza alrededor de la entidad raíz __CasoRescate__, que contiene la especie, el estado, la ubicación, el responsable asignado y el expediente clínico. El expediente se modela como una interfaz con tres implementaciones —perro, gato y fauna silvestre—, creadas siempre a través de la fábrica, nunca mediante instanciación directa. El motor de casos, las notificaciones y el acceso a datos se resuelven con los patrones que se describen en el capítulo 5.")
P("Las relaciones respetan los principios de responsabilidad única e inversión de dependencias: la entidad no conoce la base de datos, el controlador no conoce la fábrica y los observadores no conocen el motor de casos, sino únicamente el evento de nuevo rescate.")
FIG("02a-clases-dominio.png", 15.2, "Diagrama de clases UML: modelo de dominio y patrones creacionales")
FIG("02b-clases-mvc.png", 14.8, "Diagrama de clases UML: capa MVC y patrón Observer")

H2("4.4. Principios SOLID aplicados")
TABLE(["Principio", "Aplicación en el diseño"],
      [["S — Responsabilidad única", "__CasoRescate__ gestiona su estado; __NotificadorRescates__ notifica; __CasoRescateRepository__ persiste. Ninguna clase acumula dos motivos de cambio."],
       ["O — Abierto/cerrado", "Agregar una especie implica crear un nuevo expediente y una rama en la fábrica; no se modifica el motor de casos ni el controlador."],
       ["L — Sustitución de Liskov", "Cualquier implementación de __Expediente__ puede usarse donde se espera la interfaz, incluida la de fauna silvestre con sus reglas propias."],
       ["I — Segregación de interfaces", "La interfaz __Expediente__ expone solo lo que el caso necesita; los observadores implementan únicamente la operación de notificación."],
       ["D — Inversión de dependencias", "El dominio depende de la abstracción __CasoRescateRepository__, no de una implementación concreta de base de datos."]],
      [28, 72])

H2("4.5. Máquina de estados del caso")
FIG("06-estados.png", 15.0, "Máquina de estados del caso de rescate")
P("El ciclo de vida del caso se modela como una máquina de estados finita. Un caso nace en estado **Reportado**, pasa a **Rescatado** cuando el voluntario confirma la atención y luego a **En tratamiento** al iniciarse la valoración veterinaria. Desde allí puede avanzar a **Adopción** (perros y gatos) o a **Liberación** (fauna silvestre), y en ambos casos cierra en **Cerrado**. Las transiciones inválidas, como adoptar un caso que nunca estuvo en tratamiento, son rechazadas por la propia entidad y no por la interfaz, lo que garantiza la integridad de la regla de negocio en cualquier canal de acceso.")

# ---------------------------------------------------------------- 5
H1("5. Patrones de diseño aplicados")
P("Se aplican cuatro patrones de diseño —uno más que el mínimo exigido—, seleccionados porque cada uno responde a un problema concreto y recurrente del sistema de rescate. Para cada patrón se describe el problema, la solución adoptada, el lugar del diseño donde se materializa y la razón técnica de su elección.")

H2("5.1. Singleton: GestorCasos")
P("**Problema.** El motor de gestión de casos coordina la creación de casos, la asignación de responsables y la publicación de eventos. Si existieran dos instancias del motor —por ejemplo, una por cada petición web—, se producirían expedientes inconsistentes, notificaciones duplicadas y un consumo innecesario de conexiones a la base de datos.")
P("**Solución.** Se define __GestorCasos__ con constructor privado y un único punto de acceso, __getInstance()__, implementado con bloqueo de doble verificación para soportar el acceso concurrente de varios usuarios sin degradar el rendimiento.")
P("**Justificación.** Se prefiere el Singleton a una clase con miembros estáticos porque el motor mantiene estado (el mapa de casos activos) y depende de un repositorio inyectable: eso permite sustituir la persistencia en pruebas y auditar el estado en un único punto. El patrón se aplica exclusivamente al motor y al notificador; no se usa para objetos de dominio como __CasoRescate__, que deben poder instanciarse múltiples veces.")

H2("5.2. Factory Method: ExpedienteFactory")
P("**Problema.** Cada especie requiere un expediente distinto: perros y gatos necesitan control de vacunas y esterilización, mientras que la fauna silvestre exige valoración de rehabilitación y un protocolo de liberación. Si el controlador creara los expedientes con estructuras condicionales, la lógica de creación quedaría dispersa y cada nueva especie obligaría a modificar varias clases.")
P("**Solución.** Se define la interfaz __Expediente__ con sus tres implementaciones y una fábrica, __ExpedienteFactory__, que recibe la especie y devuelve la implementación adecuada. El resto del sistema trabaja siempre contra la abstracción.")
P("**Justificación.** El patrón concentra en un solo punto la decisión de qué clase concreta construir y cumple el principio abierto/cerrado: incorporar una nueva especie —por ejemplo, aves— implica crear su expediente y añadir una rama en la fábrica, sin modificar el motor de casos, el controlador ni las vistas.")

H2("5.3. Observer: NotificadorRescates")
P("**Problema.** Cuando ingresa un rescate hay que avisar a los voluntarios disponibles, a los veterinarios de turno y, en ciertos casos, al administrador. Los canales —notificación push, correo electrónico, mensajería— y los criterios de disponibilidad cambian con frecuencia; un acoplamiento directo obligaría a modificar el núcleo del sistema cada vez que se agrega un canal o un criterio.")
P("**Solución.** __NotificadorRescates__ actúa como sujeto: mantiene una lista de observadores suscritos y, al publicarse el evento de nuevo rescate, notifica únicamente a aquellos cuyo método de disponibilidad devuelve verdadero. Voluntarios y veterinarios se registran como observadores concretos.")
P("**Justificación.** El patrón desacopla al emisor del evento de sus receptores y constituye la base de la programación reactiva: añadir un canal de mensajería se reduce a crear un nuevo observador y suscribirlo, sin tocar el motor de casos. Además, permite suspender temporalmente a un voluntario sin modificar su lógica de negocio.")
P("La Figura 6 muestra la secuencia completa de registro de un rescate, donde se aprecia la colaboración de los tres patrones creacionales y de comportamiento en una sola operación.")
FIG("03-secuencia-registro.png", 15.2, "Secuencia de registro de un rescate y notificación a los observadores")

H2("5.4. Modelo-Vista-Controlador (MVC)")
P("**Problema.** Mezclar la lógica de negocio con la interfaz impide reutilizar el núcleo para la web y para la aplicación móvil, y provoca que un cambio visual pueda romper una regla del negocio.")
P("**Solución.** El **modelo** lo constituyen las entidades de dominio y el motor de casos; la **vista** se limita a presentar la información del caso; el **controlador** recibe la petición, invoca el caso de uso correspondiente y selecciona la vista.")
P("**Justificación.** La separación permite que el mismo núcleo atienda a la interfaz web y a la móvil, facilita las pruebas del modelo sin interfaz y distribuye el trabajo por capas, lo que se refleja en la organización de las ramas del repositorio.")

H2("5.5. Interacción entre los patrones")
FIG("04-secuencia-estado.png", 15.2, "Secuencia de cambio de estado con validación de la transición")
P("Los patrones no actúan de forma aislada: el controlador (MVC) solicita al motor de casos (Singleton) la creación de un caso; el motor delega en la fábrica (Factory Method) la construcción del expediente según la especie y, una vez persistido el caso, publica el evento que el notificador (Observer) distribuye entre los voluntarios y veterinarios suscritos. La Figura 7 representa esa colaboración mediante el cambio de estado de un caso, con validación de la transición y notificación del resultado.")

# ---------------------------------------------------------------- 6
H1("6. Flujo de trabajo con Gitflow")
P("El proyecto se aloja en un repositorio público de GitHub y se gestiona con el modelo Gitflow. Aunque la actividad es individual, el modelo se aplica íntegramente porque lo que se evalúa es la capacidad de trabajar con un flujo profesional y no el tamaño del equipo.")

H2("6.1. Justificación del modelo")
BULLETS([
    "**Aislamiento del trabajo en curso:** cada requerimiento se desarrolla en su propia rama __feature/__, de modo que un avance incompleto nunca afecta la versión estable.",
    "**Estabilidad de lo entregado:** la rama __master__ solo recibe código validado a través de una rama __release/__, lo que garantiza que la versión etiquetada corresponda a un estado verificable.",
    "**Integración ordenada y trazable:** las fusiones se realizan con __--no-ff__, conservando en el historial el commit de merge que evidencia la integración de cada funcionalidad.",
    "**Corrección urgente sin frenar el avance:** una rama __hotfix/__ permite corregir un error sobre __master__ y devolver el cambio a __develop__ sin bloquear el desarrollo en curso.",
])

H2("6.2. Estructura de ramas")
TABLE(["Rama", "Origen", "Destino", "Contenido"],
      [["__master__", "—", "—", "Versión estable y entregable, etiquetada como __v1.0__."],
       ["__develop__", "__master__", "__release/__", "Integración continua de todas las funcionalidades terminadas."],
       ["__feature/documentacion-arquitectura__", "__develop__", "__develop__", "Análisis de requerimientos, arquitectura y justificación de patrones."],
       ["__feature/gitflow-doc__", "__develop__", "__develop__", "Documentación del modelo de trabajo y convención de commits."],
       ["__feature/diagramas-uml__", "__develop__", "__develop__", "Diagramas de casos de uso, clases, secuencia y máquina de estados."],
       ["__release/1.0__", "__develop__", "__master__ y __develop__", "Congelamiento del alcance, validación y cierre de la entrega."]],
      [30, 15, 20, 35])

H2("6.3. Evidencia del historial")
P("El historial de ramas y commits constituye la evidencia del flujo aplicado. La Figura 8 presenta el resultado de los comandos __git branch -a__ y __git log --oneline --graph --all --decorate__ ejecutados sobre el repositorio local; en el grafo se observa cómo cada rama __feature/__ aparece como una línea paralela que se cierra con un commit de merge sobre __develop__.")
FIG("07-historial-git.png", 15.2, "Ramas y grafo del historial del repositorio local")
P("Los mensajes de commit siguen la convención __tipo(alcance): descripción en imperativo__, con los tipos __feat__, __docs__, __fix__, __refactor__ y __chore__. Esta convención permite reconstruir la intención de cada cambio sin necesidad de abrir el código y facilita la generación automática de notas de versión.")
P("La Figura 9 complementa la evidencia con la vista del repositorio remoto: arriba, la lista de ramas activas, con __master__ como rama por defecto y __develop__ por delante en los commits de integración; abajo, el historial de commits publicado en GitHub, donde se distinguen los mensajes convencionales y los commits de fusión.")
FIG("08-09-github.png", 15.0, "Ramas e historial de commits publicados en GitHub")

# ---------------------------------------------------------------- 7
H1("7. Conclusiones")
BULLETS([
    "El análisis de requerimientos permitió identificar tres actores con responsabilidades claramente diferenciadas y ocho requerimientos funcionales, de los cuales los tres primeros concentran el mayor valor para el refugio: registrar el rescate, categorizar la especie y asignar un responsable.",
    "La arquitectura en capas con MVC como patrón estructural permite que el mismo núcleo de dominio atienda a la interfaz web y a la móvil, y que la persistencia pueda sustituirse sin afectar las reglas de negocio, lo que responde directamente a los requerimientos de escalabilidad y mantenibilidad.",
    "Los cuatro patrones aplicados resuelven problemas concretos y verificables: el Singleton garantiza un estado único de los casos, la fábrica aísla la creación de expedientes por especie, el Observer desacopla las notificaciones del núcleo y MVC separa la presentación de la lógica de negocio. Cada uno podría sustituirse de forma independiente sin reescribir el sistema.",
    "El uso de Gitflow, evidenciado en el grafo de ramas y en el historial de commits del repositorio, demuestra que el diseño no solo se documenta sino que se construye de forma trazable, condición indispensable para el trabajo profesional en equipos de desarrollo.",
])

# ---------------------------------------------------------------- 8
H1("8. Referencias")
REFS = [
    "Chacon, S., & Straub, B. (2014). __Pro Git__ (2.ª ed.). Apress. https://git-scm.com/book/es/v2",
    "Fowler, M. (2003). __UML distilled: A brief guide to the standard object modeling language__ (3.ª ed.). Addison-Wesley.",
    "Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). __Design patterns: Elements of reusable object-oriented software__. Addison-Wesley.",
    "GitHub. (2026). __GitHub flow y gestión de ramas__. https://docs.github.com/es/get-started/using-github/github-flow",
    "Object Management Group. (2017). __OMG Unified Modeling Language (OMG UML), versión 2.5.1__. https://www.omg.org/spec/UML/2.5.1",
    "Pressman, R. S., & Maxim, B. R. (2020). __Ingeniería del software: un enfoque práctico__ (9.ª ed.). McGraw-Hill.",
    "Sommerville, I. (2016). __Ingeniería de software__ (10.ª ed.). Pearson Educación.",
]
for r in REFS:
    body.append(f'<text:p text:style-name="Referencia">{rich(r)}</text:p>')

# ---------------------------------------------------------------- anexo
H1("Anexo A. Repositorio del proyecto")
P("El diseño completo, los diagramas en formato editable y la documentación de análisis se encuentran publicados en el repositorio:")
P("**https://github.com/Cris-M10/sistema-rescate-adopcion-animal**", "CuerpoCentrado")
P("Estructura del repositorio:")
RAW('<text:p text:style-name="Codigo">sistema-rescate-adopcion-animal/\n├── README.md\n├── docs/\n│   ├── 01-analisis-requerimientos.md\n│   ├── 02-arquitectura.md\n│   ├── 03-patrones-diseno.md\n│   └── 04-gitflow.md\n├── diagrams/\n│   ├── 01-casos-uso.mmd\n│   ├── 02-clases.mmd\n│   ├── 03-secuencia-registro.mmd\n│   ├── 04-secuencia-estado.mmd\n│   ├── 05-arquitectura.html\n│   ├── 06-estados.mmd\n│   └── png/  (figuras del informe)\n└── .gitignore</text:p>')

# ================================================================ XML
def style_para(name, extra_props="", text_props="", parent="Standard", master=None):
    mp = f' style:master-page-name="{master}"' if master else ""
    return (f'<style:style style:name="{name}" style:family="paragraph" style:parent-style-name="{parent}"{mp}>'
            f'<style:paragraph-properties {extra_props}/>'
            f'<style:text-properties {text_props}/></style:style>')

autostyles = []
A = autostyles.append

A(style_para("PortadaInicio",
             'fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.2cm" fo:line-height="130%"',
             'fo:font-size="18pt" fo:font-weight="bold"', master="FirstPage"))
A(style_para("PortadaCentro",
             'fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.15cm" fo:line-height="130%"',
             'fo:font-size="12pt"'))
A(style_para("PortadaTitulo",
             'fo:text-align="center" fo:margin-top="0.6cm" fo:margin-bottom="0.3cm" fo:line-height="140%"',
             'fo:font-size="16pt" fo:font-weight="bold"'))
A(style_para("PortadaSubtitulo",
             'fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.3cm" fo:line-height="130%"',
             'fo:font-size="12pt" fo:font-style="italic"'))
A(style_para("PortadaEspacio",
             'fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.9cm"',
             'fo:font-size="12pt"'))
A(style_para("H1",
             'fo:break-before="page" fo:margin-top="0cm" fo:margin-bottom="0.5cm" fo:line-height="150%" '
             'fo:keep-with-next="always" fo:text-align="left"',
             'fo:font-size="14pt" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"'))
A(style_para("H2",
             'fo:margin-top="0.45cm" fo:margin-bottom="0.2cm" fo:line-height="150%" '
             'fo:keep-with-next="always" fo:text-align="left"',
             'fo:font-size="12.5pt" fo:font-weight="bold"'))
A(style_para("Cuerpo",
             'fo:text-align="justify" fo:margin-top="0cm" fo:margin-bottom="0.3cm" fo:line-height="150%" '
             'fo:text-indent="0cm" style:justify-single-word="false"',
             'fo:font-size="12pt"'))
A(style_para("CuerpoCentrado",
             'fo:text-align="center" fo:margin-top="0.2cm" fo:margin-bottom="0.4cm" fo:line-height="150%"',
             'fo:font-size="12pt"'))
A(style_para("CuerpoLista",
             'fo:text-align="justify" fo:margin-top="0cm" fo:margin-bottom="0.15cm" fo:line-height="150%"',
             'fo:font-size="12pt"'))
A(style_para("EspacioTabla", 'fo:margin-top="0cm" fo:margin-bottom="0.15cm" fo:line-height="100%"', 'fo:font-size="6pt"'))
A(style_para("FigPagina",
             'fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.1cm" fo:line-height="100%" '
             'fo:break-before="page"',
             'fo:font-size="12pt"'))
A(style_para("FigPort",
             'fo:text-align="center" fo:margin-top="0.3cm" fo:margin-bottom="0.1cm" fo:line-height="100%" '
             'fo:keep-with-next="always"',
             'fo:font-size="12pt"'))
A(style_para("FigLand",
             'fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.1cm" fo:line-height="100%" '
             'fo:break-before="page"',
             'fo:font-size="12pt"', master="Landscape"))
A(style_para("FigLandImg",
             'fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.1cm" fo:line-height="100%"',
             'fo:font-size="12pt"', master="Landscape"))
A(style_para("BloqueFigura",
             'fo:text-align="center" fo:margin-top="0.35cm" fo:margin-bottom="0.55cm" fo:line-height="130%"',
             'fo:font-size="12pt"'))
A('<style:style style:name="TxtEtiquetaFig" style:family="text"><style:text-properties fo:font-size="10.5pt" fo:font-weight="bold"/></style:style>')
A('<style:style style:name="TxtTituloFig" style:family="text"><style:text-properties fo:font-size="11pt" fo:font-style="italic"/></style:style>')
A(style_para("TituloFigura",
             'fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.55cm" fo:line-height="130%"',
             'fo:font-size="11pt" fo:font-style="italic"'))
A(style_para("EtiquetaFigura",
             'fo:text-align="center" fo:margin-top="0.15cm" fo:margin-bottom="0.05cm" fo:line-height="130%" '
             'fo:keep-with-next="always"',
             'fo:font-size="10.5pt" fo:font-weight="bold"'))
A(style_para("EtiquetaFiguraLand",
             'fo:text-align="center" fo:margin-top="0.05cm" fo:margin-bottom="0.3cm" fo:line-height="130%"',
             'fo:font-size="10pt" fo:font-weight="bold"'))
# tras una figura horizontal, volver a página vertical
A(style_para("FigLandBack",
             'fo:break-before="page" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:line-height="100%"',
             'fo:font-size="1pt"', master="Standard"))
A(style_para("NotaFigura",
             'fo:text-align="left" fo:margin-top="0.1cm" fo:margin-bottom="0.5cm" fo:line-height="130%"',
             'fo:font-size="10pt"'))
TABSTOP = ('<style:tab-stops><style:tab-stop style:position="15.9cm" style:type="right" '
           'style:leader-char="." style:leader-style="dotted"/></style:tab-stops>')
A('<style:style style:name="Indice1" style:family="paragraph" style:parent-style-name="Standard">'
  '<style:paragraph-properties fo:text-align="left" fo:margin-top="0.25cm" fo:margin-bottom="0.1cm" '
  'fo:line-height="140%">' + TABSTOP + '</style:paragraph-properties>'
  '<style:text-properties fo:font-size="12pt" fo:font-weight="bold"/></style:style>')
A('<style:style style:name="Indice2" style:family="paragraph" style:parent-style-name="Standard">'
  '<style:paragraph-properties fo:text-align="left" fo:margin-top="0.05cm" fo:margin-bottom="0.05cm" '
  'fo:line-height="140%" fo:margin-left="0.7cm">' + TABSTOP + '</style:paragraph-properties>'
  '<style:text-properties fo:font-size="12pt"/></style:style>')
A(style_para("Referencia",
             'fo:text-align="justify" fo:margin-top="0cm" fo:margin-bottom="0.3cm" fo:line-height="150%" '
             'fo:margin-left="1.25cm" fo:text-indent="-1.25cm"',
             'fo:font-size="12pt"'))
A(style_para("Codigo",
             'fo:text-align="left" fo:margin-top="0.2cm" fo:margin-bottom="0.3cm" fo:line-height="130%" '
             'fo:background-color="#F1F3F4" fo:padding="0.3cm" fo:border="0.5pt solid #D0D7DE"',
             'style:font-name="Courier New" fo:font-size="10pt"'))
A('<style:style style:name="TxtBold" style:family="text"><style:text-properties fo:font-weight="bold"/></style:style>')
A('<style:style style:name="TxtItalic" style:family="text"><style:text-properties fo:font-style="italic"/></style:style>')
A('<style:style style:name="Marco" style:family="graphic"><style:graphic-properties style:run-through="foreground" style:wrap="none" style:vertical-pos="top" style:vertical-rel="baseline" style:horizontal-pos="center" style:horizontal-rel="paragraph"/></style:style>')
A('<style:style style:name="TablaFigura" style:family="table" style:default-outline-level="">'
  '<style:table-properties style:width="15.9cm" table:align="center" fo:margin-top="0.2cm" fo:margin-bottom="0.2cm"/>'
  '</style:style>')
A('<style:style style:name="FilaFigura" style:family="table-row">'
  '<style:table-row-properties fo:keep-together="always"/></style:style>')
A('<style:style style:name="CeldaFigura" style:family="table-cell">'
  '<style:table-cell-properties fo:padding="0cm" fo:border="none" fo:vertical-align="top"/>'
  '</style:style>')
A('<style:style style:name="TablaBase" style:family="table" style:default-outline-level="">'
  '<style:table-properties style:width="15.9cm" table:align="center" fo:margin-top="0.15cm" fo:margin-bottom="0.15cm"/></style:style>')
A('<style:style style:name="CeldaEncabezado" style:family="table-cell">'
  '<style:table-cell-properties fo:background-color="#DCE6F2" fo:padding="0.14cm" fo:border="0.5pt solid #8FA3BF" '
  'fo:vertical-align="middle"/></style:style>')
A('<style:style style:name="CeldaNormal" style:family="table-cell">'
  '<style:table-cell-properties fo:padding="0.14cm" fo:border="0.5pt solid #8FA3BF" fo:vertical-align="top"/></style:style>')
A(style_para("TextoEncabezado",
             'fo:text-align="left" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:line-height="120%"',
             'fo:font-size="10pt" fo:font-weight="bold"'))
A(style_para("TextoCell",
             'fo:text-align="left" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:line-height="120%"',
             'fo:font-size="10pt"'))
A('<text:list-style style:name="LVinetas">'
  '<text:list-level-style-bullet text:level="1" text:bullet-char="•">'
  '<style:list-level-properties text:space-before="0.6cm" text:min-label-width="0.45cm"/>'
  '<style:text-properties fo:font-size="12pt"/></text:list-level-style-bullet></text:list-style>')

# ---------------------------------------------------------------- ensamblar
# Los estilos de párrafo, texto, gráfico y listas deben ser estilos CON NOMBRE en
# styles.xml para que LibreOffice aplique los cambios de página (style:master-page-name).
NAMED, AUTON = [], []
for st in autostyles:
    if ('style:name="Celda' in st) or ('style:name="Tabla' in st) or ('style:name="Col' in st):
        AUTON.append(st)
    else:
        NAMED.append(st)

CONTENT_STYLES = "\n".join(COLS + AUTON)
NAMED_STYLES = "\n".join(NAMED)

def landscape_back():
    """Inserta un párrafo invisible que devuelve el documento a página vertical."""
    return '<text:p text:style-name="FigLandBack"></text:p>'

# insertar retorno a vertical después de cada figura horizontal
final = []
for blk in body:
    final.append(blk)
    if 'EtiquetaFiguraLand' in blk:
        final.append(landscape_back())

content = f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  office:version="1.2" office:mimetype="application/vnd.oasis.opendocument.text">
 <office:font-face-decls>
  <style:font-face style:name="Times New Roman" svg:font-family="'Times New Roman'" style:font-family-generic="roman" style:font-pitch="variable"/>
  <style:font-face style:name="Courier New" svg:font-family="'Courier New'" style:font-family-generic="modern" style:font-pitch="fixed"/>
 </office:font-face-decls>
 <office:automatic-styles>
{CONTENT_STYLES}
 </office:automatic-styles>
 <office:body>
  <office:text>
{chr(10).join(final)}
  </office:text>
 </office:body>
</office:document-content>
'''

styles = f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  office:version="1.2">
 <office:font-face-decls>
  <style:font-face style:name="Times New Roman" svg:font-family="'Times New Roman'" style:font-family-generic="roman" style:font-pitch="variable"/>
  <style:font-face style:name="Courier New" svg:font-family="'Courier New'" style:font-family-generic="modern" style:font-pitch="fixed"/>
 </office:font-face-decls>
 <office:styles>
  <style:default-style style:family="paragraph">
   <style:paragraph-properties fo:orphans="2" fo:widows="2" fo:hyphenation-ladder-count="no-limit"/>
   <style:text-properties style:font-name="Times New Roman" fo:font-size="12pt" fo:language="es" fo:country="EC" style:font-name-asian="Times New Roman" style:font-size-asian="12pt"/>
  </style:default-style>
  <style:style style:name="Standard" style:family="paragraph" style:class="text"/>
  <style:style style:name="Text_20_body" style:display-name="Text body" style:family="paragraph"
               style:parent-style-name="Standard" style:class="text">
   <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0.3cm" fo:line-height="150%" fo:text-align="justify"/>
   <style:text-properties style:font-name="Times New Roman" fo:font-size="12pt"/>
  </style:style>
{NAMED_STYLES}
 </office:styles>
 <office:automatic-styles>
  <style:page-layout style:name="PLPortrait">
   <style:page-layout-properties fo:page-width="21.001cm" fo:page-height="29.7cm" style:print-orientation="portrait"
     fo:margin-top="2.54cm" fo:margin-bottom="2.54cm" fo:margin-left="2.54cm" fo:margin-right="2.54cm"/>
   <style:footer-style><style:header-footer-properties fo:min-height="0.8cm" fo:margin-top="0.6cm"/></style:footer-style>
  </style:page-layout>
  <style:page-layout style:name="PLLandscape">
   <style:page-layout-properties fo:page-width="29.7cm" fo:page-height="21.001cm" style:print-orientation="landscape"
     fo:margin-top="2.0cm" fo:margin-bottom="2.0cm" fo:margin-left="2.0cm" fo:margin-right="2.0cm"/>
   <style:footer-style><style:header-footer-properties fo:min-height="0.8cm" fo:margin-top="0.5cm"/></style:footer-style>
  </style:page-layout>
  <style:style style:name="PieDePagina" style:family="paragraph">
   <style:paragraph-properties fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0cm"/>
   <style:text-properties style:font-name="Times New Roman" fo:font-size="10pt"/>
  </style:style>
 </office:automatic-styles>
 <office:master-styles>
  <style:master-page style:name="Standard" style:page-layout-name="PLPortrait">
   <style:footer>
    <text:p text:style-name="PieDePagina"><text:page-number text:select-page="current">1</text:page-number></text:p>
   </style:footer>
  </style:master-page>
  <style:master-page style:name="FirstPage" style:page-layout-name="PLPortrait"/>
  <style:master-page style:name="Landscape" style:page-layout-name="PLLandscape">
   <style:footer>
    <text:p text:style-name="PieDePagina"><text:page-number text:select-page="current">1</text:page-number></text:p>
   </style:footer>
  </style:master-page>
 </office:master-styles>
</office:document-styles>
'''

meta = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
  office:version="1.2">
 <office:meta>
  <dc:title>Informe Actividad 1 - Sistema de Control de Rescate y Adopción Animal</dc:title>
  <dc:creator>Cristopher Montoya</dc:creator>
  <meta:generator>Hermes</meta:generator>
 </office:meta>
</office:document-meta>
'''

settings = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-settings xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0" office:version="1.2">
 <office:settings>
  <config:config-item-set config:name="ooo:view-settings">
   <config:config-item config:name="ViewAreaTop" config:type="long">0</config:config-item>
   <config:config-item config:name="ViewAreaLeft" config:type="long">0</config:config-item>
  </config:config-item-set>
 </office:settings>
</office:document-settings>
'''

pics = sorted(f for f in os.listdir(IMG) if f.endswith(".png"))
manifest = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">',
            ' <manifest:file-entry manifest:full-path="/" manifest:version="1.2" manifest:media-type="application/vnd.oasis.opendocument.text"/>',
            ' <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>',
            ' <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>',
            ' <manifest:file-entry manifest:full-path="meta.xml" manifest:media-type="text/xml"/>',
            ' <manifest:file-entry manifest:full-path="settings.xml" manifest:media-type="text/xml"/>']
for p in pics:
    manifest.append(f' <manifest:file-entry manifest:full-path="Pictures/{p}" manifest:media-type="image/png"/>')
manifest.append('</manifest:manifest>')
manifest = "\n".join(manifest)

with zipfile.ZipFile(OUT, "w") as z:
    z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.oasis.opendocument.text", zipfile.ZIP_STORED)
    z.writestr("content.xml", content, zipfile.ZIP_DEFLATED)
    z.writestr("styles.xml", styles, zipfile.ZIP_DEFLATED)
    z.writestr("meta.xml", meta, zipfile.ZIP_DEFLATED)
    z.writestr("settings.xml", settings, zipfile.ZIP_DEFLATED)
    z.writestr("META-INF/manifest.xml", manifest, zipfile.ZIP_DEFLATED)
    for p in pics:
        with open(os.path.join(IMG, p), "rb") as f:
            z.writestr(f"Pictures/{p}", f.read(), zipfile.ZIP_STORED)

print("OK:", OUT, os.path.getsize(OUT) // 1024, "KB")
print("figuras:", fig_n[0])
