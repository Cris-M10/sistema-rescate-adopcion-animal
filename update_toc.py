import json, re, subprocess, os

BASE = "/home/crism10/UTM/DSI-U1-RescateAnimal"
PDF = "/tmp/render/Informe_DSI_U1_Rescate_Animal.pdf"

headings = [
    "1. Introducción", "2. Objetivos", "3. Análisis del problema",
    "3.1. Actores del sistema", "3.2. Requerimientos funcionales",
    "3.3. Requerimientos no funcionales", "3.4. Reglas de negocio",
    "4. Diseño del sistema", "4.1. Arquitectura general",
    "4.2. Diagrama de casos de uso", "4.3. Diagrama de clases",
    "4.4. Principios SOLID aplicados", "4.5. Máquina de estados del caso",
    "5. Patrones de diseño aplicados", "5.1. Singleton: GestorCasos",
    "5.2. Factory Method: ExpedienteFactory", "5.3. Observer: NotificadorRescates",
    "5.4. Modelo-Vista-Controlador (MVC)", "5.5. Interacción entre los patrones",
    "6. Flujo de trabajo con Gitflow", "6.1. Justificación del modelo",
    "6.2. Estructura de ramas", "6.3. Evidencia del historial",
    "7. Conclusiones", "8. Referencias", "Anexo A. Repositorio del proyecto",
]

txt = subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True, text=True).stdout
pages = txt.split("\f")

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

mapping = {}
for h in headings:
    target = norm(h)
    for i, page in enumerate(pages, start=1):
        if i <= 2:      # la portada y el índice no cuentan como ubicación real
            continue
        for line in page.split("\n"):
            if norm(line) == target:
                mapping[h] = i
                break
        if h in mapping:
            break
    if h not in mapping:
        print("NO ENCONTRADO:", h)

json.dump(mapping, open(os.path.join(BASE, ".pages.json"), "w"), ensure_ascii=False, indent=1)
for k, v in mapping.items():
    print(f"{v:>3}  {k}")
