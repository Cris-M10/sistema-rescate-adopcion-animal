# Flujo de trabajo con Gitflow

## 1. Justificación del modelo

El proyecto es individual, pero el modelo Gitflow se usa igual porque el resultado que se evalúa
es la **capacidad de trabajar con un flujo profesional**, no el tamaño del equipo. Gitflow aporta:

| Beneficio | Cómo se materializa en este repositorio |
|---|---|
| Aislamiento del trabajo en curso | Cada requerimiento se desarrolla en su propia rama `feature/*` |
| Estabilidad de lo entregado | `master` solo recibe código validado mediante una rama `release/*` |
| Integración ordenada | `develop` concentra los avances y se integra con `merge --no-ff` |
| Trazabilidad | Cada fusión conserva un commit de merge con mensaje descriptivo |
| Corrección urgente sin romper el avance | `hotfix/*` sale de `master` y vuelve a `master` y `develop` |

## 2. Ramas del repositorio

| Rama | Origen | Destino | Contenido |
|---|---|---|---|
| `master` | — | — | Única rama con entregables estables (`v1.0`) |
| `develop` | `master` | `release/*` | Integración de todas las funcionalidades terminadas |
| `feature/documentacion-arquitectura` | `develop` | `develop` | Análisis, arquitectura y patrones |
| `feature/diagramas-uml` | `develop` | `develop` | Casos de uso, clases y secuencia |
| `feature/implementacion-patrones` | `develop` | `develop` | Código de referencia de los patrones |
| `release/1.0` | `develop` | `master` y `develop` | Versión final para la entrega |

## 3. Flujo aplicado paso a paso

```bash
# 1. Rama de trabajo a partir de develop
git checkout develop
git checkout -b feature/diagramas-uml

# 2. Commits atómicos con mensajes convencionales
git add diagrams/
git commit -m "feat(diagramas): casos de uso y diagrama de clases con SOLID"

# 3. Integración con merge --no-ff para conservar la rama en el historial
git checkout develop
git merge --no-ff feature/diagramas-uml

# 4. Preparación y cierre de la versión
git checkout -b release/1.0 develop
git checkout master
git merge --no-ff release/1.0
git tag -a v1.0 -m "Entrega Unidad 1 - Diseno de arquitectura"
```

## 4. Convención de mensajes de commit

Formato `tipo(alcance): descripción en imperativo`.

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad o documento |
| `fix` | Corrección de un error |
| `docs` | Cambios solo en documentación |
| `refactor` | Reestructuración sin cambio de comportamiento |
| `chore` | Configuración, dependencias, estructura |

## 5. Evidencia del historial

El historial del repositorio evidencia el flujo aplicado:

```bash
git log --oneline --graph --all --decorate
```

Salida esperada: cada `feature/*` aparece como una rama paralela que se cierra con un commit de
merge en `develop`, y `master` conserva la versión estable etiquetada como `v1.0`.

Para el documento de entrega se incluyen capturas de:

1. La lista de ramas (`git branch -a`).
2. El grafo del historial (`git log --oneline --graph --all`).
3. La vista *Network* del repositorio en GitHub.
4. El Pull Request que integra una rama `feature/*` en `develop`.
