# Arquitectura del sistema

## 1. Estilo arquitectónico

Se adopta una **arquitectura en capas con separación MVC** (patrón estructural) sobre un
núcleo de dominio rico. La dependencia apunta siempre hacia el dominio: la interfaz y la
persistencia conocen al dominio, nunca al revés (principio de inversión de dependencias, D de SOLID).

```
┌──────────────────────────────────────────────────────────────┐
│  Capa de presentación (Vista + Controlador)                  │
│  Web / Móvil  →  CasoRescateController, DashboardController  │
└───────────────────────────┬──────────────────────────────────┘
                            │ DTOs / comandos
┌───────────────────────────▼──────────────────────────────────┐
│  Capa de aplicación (Servicios de caso de uso)               │
│  RegistrarRescateService · AsignarResponsableService          │
│  CambiarEstadoService                                        │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│  Dominio (Modelo)                                            │
│  CasoRescate · Expediente · Especie · EstadoCaso             │
│  GestorCasos (Singleton) · Observers · ExpedienteFactory     │
└───────────────────────────┬──────────────────────────────────┘
                            │ interfaces de repositorio
┌───────────────────────────▼──────────────────────────────────┐
│  Infraestructura                                             │
│  CasoRescateRepository (JPA/SQL) · NotificacionMail/Push      │
└──────────────────────────────────────────────────────────────┘
```

## 2. Componentes y responsabilidades

| Componente | Responsabilidad | Patrón/principio |
|---|---|---|
| `GestorCasos` | Punto único de coordinación del motor de casos | Singleton |
| `ExpedienteFactory` | Crear el expediente adecuado según la especie | Factory Method |
| `NotificadorRescates` (Subject) | Emitir el evento de nuevo rescate | Observer |
| `VoluntarioObserver`, `VeterinarioObserver` | Reaccionar al evento según disponibilidad y rol | Observer |
| `CasoRescate` | Entidad raíz del agregado; controla transiciones de estado | Dominio rico |
| `CasoRescateController` | Traducir la petición HTTP a comandos de aplicación | MVC / Controller |
| `CasoRescateRepository` | Persistencia; abstracción intercambiable | DIP |

## 3. Máquina de estados del caso

```
   [REPORTADO] ──► [RESCATADO] ──► [EN_TRATAMIENTO] ──► [ADOPCION]
        │               │                 │  ▲              │
        │               │                 │  └── recaída    │
        └───────────────┴─────────────────┴──────────────► [CERRADO]
                                              (fauna silvestre) ──► [LIBERACION]
```

Transiciones válidas:

| Desde | Hacia | Quién |
|---|---|---|
| REPORTADO | RESCATADO, CERRADO | Administrador |
| RESCATADO | EN_TRATAMIENTO, CERRADO | Veterinario |
| EN_TRATAMIENTO | EN_TRATAMIENTO, ADOPCION, LIBERACION, CERRADO | Veterinario |
| ADOPCION | CERRADO | Administrador |

## 4. Integración de la arquitectura con el flujo de versiones

La arquitectura se organiza en módulos alineados con las ramas de Gitflow, de modo que
cada `feature/*` toca un módulo y no genera conflictos con el resto del equipo:

| Rama | Módulo impactado |
|---|---|
| `feature/analisis-requerimientos` | `docs/` |
| `feature/dominio-casos` | Núcleo de dominio y máquina de estados |
| `feature/notificaciones-observer` | `NotificadorRescates` y observers |
| `feature/expedientes-factory` | `ExpedienteFactory` y jerarquía de expedientes |
| `release/1.0` | Congelamiento: solo correcciones, sin nuevas funciones |

Reglas del flujo:

1. Un `feature/*` nace de `develop` y se integra con `merge --no-ff`.
2. Un `release/*` se abre desde `develop`, se valida y se fusiona en `master` y `develop`.
3. Un `hotfix/*` nace de `master` y se fusiona en `master` y `develop`.
4. Cada integración se revisa en un Pull Request con descripción del cambio.
