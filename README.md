# Sistema de Control de Rescate y Adopción Animal

Diseño de la arquitectura lógica de un sistema para la gestión de casos en un refugio animal.
Trabajo de la **Unidad 1 — Desarrollo de software: Introducción y Paradigmas de diseño**
(Desarrollo de Sistemas Informáticos — UTM, Periodo Septiembre 2026 / Enero 2027).

## Alcance

El sistema permite:

- Reportar el ingreso de animales rescatados (perros, gatos, fauna silvestre).
- Asignar un voluntario o veterinario responsable a cada caso.
- Gestionar el ciclo de vida del caso: `RESCATADO → EN_TRATAMIENTO → ADOPCION` (con `EN_TRATAMIENTO` reversible y cierre por `EGRESO`).
- Notificar automáticamente a los voluntarios disponibles cuando se registra un nuevo rescate.

## Actores

| Actor | Responsabilidad |
|---|---|
| Ciudadano / Reportante | Registra el reporte de un animal en riesgo |
| Voluntario / Veterinario | Atiende el caso, actualiza el estado clínico |
| Administrador del Refugio | Asigna responsables, audita y consulta indicadores |

## Estructura del repositorio

```
docs/        Documentación de análisis, arquitectura y patrones
diagrams/    Diagramas de casos de uso, clases y secuencia
src/         Código de referencia de los patrones implementados
```

## Flujo de trabajo (Gitflow)

| Rama | Propósito |
|---|---|
| `master` | Versiones estables y entregables |
| `develop` | Integración continua de los avances |
| `feature/*` | Desarrollo de cada requerimiento |
| `release/*` | Preparación de una entrega |
| `hotfix/*` | Correcciones urgentes sobre `master` |

Cada `feature/*` se integra a `develop` mediante `merge --no-ff` para conservar la
trazabilidad del avance en el historial.

## Patrones de diseño aplicados

| Patrón | Categoría | Problema que resuelve |
|---|---|---|
| Singleton | Creacional | Instancia única del motor de gestión de casos y del acceso a datos |
| Factory Method | Creacional | Creación polimórfica de expedientes según la especie del animal |
| Observer | Comportamiento | Notificación automática a voluntarios al ingresar un rescate |
| MVC | Estructural | Separación entre modelo de negocio, vista y controlador |
