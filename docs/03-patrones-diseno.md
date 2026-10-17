# Patrones de diseño aplicados

Se aplican **cuatro** patrones (el mínimo exigido es tres). Cada uno responde a un
problema concreto del Sistema de Control de Rescate y Adopción Animal.

## 1. Singleton — `GestorCasos`

**Categoría:** creacional.
**Problema:** el motor de gestión de casos y la conexión a datos no pueden duplicarse:
dos instancias producirían expedientes inconsistentes, notificaciones repetidas y
un consumo innecesario de conexiones.

**Solución:** una única instancia de acceso controlado, con constructor privado y un
método estático `getInstance()` sincronizado (doble verificación) para soportar concurrencia.

```java
public final class GestorCasos {
    private static volatile GestorCasos instancia;
    private final Map<String, CasoRescate> casos = new ConcurrentHashMap<>();

    private GestorCasos() {
        if (instancia != null) throw new IllegalStateException("Usa getInstance()");
    }

    public static GestorCasos getInstance() {
        if (instancia == null) {
            synchronized (GestorCasos.class) {
                if (instancia == null) instancia = new GestorCasos();
            }
        }
        return instancia;
    }

    public void registrar(CasoRescate caso) {
        casos.put(caso.id(), caso);
        NotificadorRescates.getInstance().notificarNuevoRescate(caso);
    }
}
```

**Por qué no una clase estática:** el Singleton mantiene estado, permite inyectar dependencias
(el repositorio) y puede sustituirse por un doble de prueba, algo imposible con miembros estáticos.

## 2. Factory Method — `ExpedienteFactory`

**Categoría:** creacional.
**Problema:** cada especie requiere un expediente distinto (vacunas y esterilización en perros y
gatos, valoración de fauna y liberación en silvestres). Instanciar con `new` condicionales dispersa
la lógica de creación y viola el principio Abierto/Cerrado.

**Solución:** el controlador pide un expediente a la fábrica y recibe la abstracción
`Expediente`; la lógica de qué clase concreta construir queda en un solo lugar.

```java
public interface Expediente { String resumenClinico(); }

public class ExpedientePerro   implements Expediente { /* vacunas, esterilización */ }
public class ExpedienteGato    implements Expediente { }
public class ExpedienteFaunaSilvestre implements Expediente { }

public final class ExpedienteFactory {
    public static Expediente crear(Especie especie) {
        return switch (especie) {
            case PERRO  -> new ExpedientePerro();
            case GATO   -> new ExpedienteGato();
            case FAUNA_SILVESTRE -> new ExpedienteFaunaSilvestre();
        };
    }
}
```

**Beneficio:** agregar una nueva especie solo implica crear su clase y añadir una rama en la
fábrica; ningún otro módulo cambia.

## 3. Observer — `NotificadorRescates`

**Categoría:** de comportamiento.
**Problema:** al ingresar un rescate hay que avisar a voluntarios y veterinarios, pero los canales
(push, correo, SMS) y los criterios de disponibilidad cambian con frecuencia. Un acoplamiento
directo obligaría a modificar el núcleo cada vez que se agrega un canal.

**Solución:** el núcleo publica un evento y los interesados se suscriben. Es la base de la
programación reactiva que menciona la guía.

```java
public interface ObservadorRescate {
    void alNuevoRescate(CasoRescate caso);
}

public class NotificadorRescates {                 // Subject
    private static final NotificadorRescates INSTANCIA = new NotificadorRescates();
    private final List<ObservadorRescate> observadores = new CopyOnWriteArrayList<>();

    public static NotificadorRescates getInstance() { return INSTANCIA; }
    public void suscribir(ObservadorRescate o)   { observadores.add(o); }
    public void desuscribir(ObservadorRescate o) { observadores.remove(o); }

    public void notificarNuevoRescate(CasoRescate caso) {
        observadores.stream()
                    .filter(o -> o.disponiblePara(caso))
                    .forEach(o -> o.alNuevoRescate(caso));
    }
}
```

**Beneficio:** añadir un canal de WhatsApp o de SMS es crear un nuevo observador sin tocar
`GestorCasos`; cumple Abierto/Cerrado y responsabilidad única.

## 4. MVC — patrón estructural de organización

**Categoría:** estructural / arquitectónico.
**Problema:** mezclar la lógica de negocio con la interfaz impide reutilizar el núcleo para web y
móvil, y hace que un cambio visual rompa reglas del negocio.

**Solución:** separación en tres responsabilidades:

| Elemento | Clase | Responsabilidad |
|---|---|---|
| Modelo | `CasoRescate`, `GestorCasos`, repositorios | Estado, reglas y transiciones válidas |
| Vista | `CasoRescateView`, plantillas HTML | Presentación, sin reglas de negocio |
| Controlador | `CasoRescateController` | Recibe la petición, invoca el caso de uso y elige la vista |

```java
public class CasoRescateController {
    public Respuesta postRescate(SolicitudRescate s) {
        CasoRescate caso = GestorCasos.getInstance()
            .crearCaso(s.reportante(), s.especie(), s.ubicacion());
        return new CasoRescateView(caso).render();   // la vista no conoce reglas
    }
}
```

## 5. Relación entre patrones

```
 Ciudadano ──► Controller (MVC) ──► GestorCasos (Singleton)
                                          │
                                          ├─► ExpedienteFactory (Factory Method) ──► Expediente{Perro|Gato|Fauna}
                                          └─► NotificadorRescates (Observer) ──► Voluntario / Veterinario
```

El controlador no conoce la fábrica ni los observers: solo conversa con el Singleton, que actúa
como fachada del dominio. Esto mantiene bajo el acoplamiento y hace que cada patrón sea
sustituible de forma independiente.

## 6. Tabla resumen de justificación

| Patrón | Dónde se aplica | Problema del sistema que resuelve | Beneficio medible |
|---|---|---|---|
| Singleton | `GestorCasos` | Duplicidad de instancias y de conexiones | Estado único y consistente de los casos |
| Factory Method | `ExpedienteFactory` | Creación condicional por especie | Nuevas especies sin modificar el resto |
| Observer | `NotificadorRescates` | Notificaciones acopladas al núcleo | Nuevos canales sin tocar el dominio |
| MVC | Controladores y vistas | Mezcla de negocio y presentación | Reutilización del núcleo en web y móvil |
