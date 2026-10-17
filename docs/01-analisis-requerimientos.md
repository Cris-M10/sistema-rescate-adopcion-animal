# Análisis del problema

## 1. Actores y sus interacciones

| Actor | Casos de uso principales |
|---|---|
| Ciudadano / Reportante | Reportar rescate, consultar estado del reporte |
| Voluntario / Veterinario | Ver casos asignados, actualizar estado clínico, registrar tratamiento |
| Administrador del Refugio | Gestionar usuarios, asignar responsable, consultar reportes e indicadores |

## 2. Requerimientos funcionales

| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-01 | Crear un caso de rescate con ubicación, descripción y evidencia | Alta |
| RF-02 | Categorizar la especie: perro, gato, fauna silvestre | Alta |
| RF-03 | Asignar un voluntario o veterinario responsable al caso | Alta |
| RF-04 | Gestionar los estados del caso (Rescatado, En Tratamiento, Adopción) | Alta |
| RF-05 | Notificar a los voluntarios disponibles ante un nuevo rescate | Media |
| RF-06 | Registrar el historial de cambios de estado de cada caso | Media |
| RF-07 | Generar expediente clínico diferenciado por especie | Media |
| RF-08 | Consultar indicadores: casos abiertos, tiempo medio de atención | Baja |

## 3. Requerimientos no funcionales

| ID | Requerimiento | Criterio de verificación |
|---|---|---|
| RNF-01 | Escalabilidad | El sistema soporta el crecimiento del número de casos y refugios sin rediseñar el núcleo |
| RNF-02 | Mantenibilidad | Cada módulo es sustituible de forma aislada; cobertura de pruebas del núcleo |
| RNF-03 | Trazabilidad de versiones | Todo cambio queda en una rama `feature/*` y se integra vía Pull Request |
| RNF-04 | Seguridad | Autenticación por rol; el reportante anónimo solo accede a su propio caso |
| RNF-05 | Usabilidad | Registro de un rescate en menos de 2 minutos desde un dispositivo móvil |

## 4. Reglas de negocio

- Un caso no puede pasar a `ADOPCION` sin haber estado en `EN_TRATAMIENTO`.
- Un caso solo puede tener un responsable activo a la vez.
- El cambio de estado genera un evento de dominio que alimenta las notificaciones.
- La fauna silvestre no puede pasar a `ADOPCION`: su estado final es `LIBERACION`.
