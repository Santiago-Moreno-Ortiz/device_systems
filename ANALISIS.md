# Análisis del repositorio

## Qué implementa

Backend REST académico centrado en `users`. Utiliza FastAPI para HTTP y documentación, Uvicorn como servidor, Pydantic para validar entradas y respuestas, SQLAlchemy como ORM y SQLite para almacenamiento persistente. No gestiona dispositivos a pesar del nombre del repositorio.

La separación entre rutas, dependencias, servicios, esquemas y modelo facilita modificar cada responsabilidad. Las consultas usan SQLAlchemy, el correo se normaliza antes de guardar y las escrituras controlan errores con rollback. Las respuestas excluyen `internal_notes`.

## Hallazgos corregidos

| Hallazgo | Efecto anterior | Corrección |
|---|---|---|
| Restos de conflictos de Git en README y `.gitignore` | Documentación mezclada con una versión que usaba memoria y referencias a archivos inexistentes | Guía única que describe el código actual y limpieza de `.gitignore` |
| Dependencias repetidas | Dos bloques de requisitos para las mismas bibliotecas | Un único rango por dependencia y archivo separado para herramientas de pruebas |
| Nombre validado antes de quitar espacios | `" a "` o `"   "` llegaban a la BD y fallaban como restricción, en lugar de validación HTTP | Tipo compartido que elimina espacios exteriores antes de validar longitud en POST, PUT y PATCH |
| PATCH aceptaba `null` | Respondía 200 aunque no modificara el campo | Rechazo con 422; los campos omitidos siguen permitidos |
| Versiones inconsistentes | Raíz configurable, OpenAPI fijo en 3.0.0 y cabecera fija en 3.0 | OpenAPI y cabecera usan la versión configurada al inicio |
| Creación de tablas al importar | Importar el módulo podía crear archivos y acceder a la BD | Inicialización en el ciclo de vida de FastAPI |
| Clave vacía configurable | Una cabecera vacía podía autorizar DELETE si `API_KEY` estaba vacía | Rechazo de claves vacías y comparación mediante `secrets.compare_digest` |
| Metadatos de ejemplo | Contacto ficticio y raíz que siempre decía SQLite | Retirada del contacto y motor informado desde SQLAlchemy |
| Ausencia de pruebas ejecutables | Solo existían capturas históricas | Pruebas HTTP con SQLite temporal, sin modificar datos locales |

## Comportamiento conservado

- POST aplica rol `user` y estado activo por defecto.
- PUT requiere los cuatro campos editables; PATCH modifica solo los enviados.
- Correos duplicados devuelven 400; no se cambió a 409 para conservar el contrato.
- DELETE requiere `X-API-Key`; el resto de las operaciones sigue siendo público.
- El listado incluye `total` e `items` y filtros combinables por rol/estado.
- La clave predeterminada sigue siendo académica y aparece en `.env.example`.

## Limitaciones pendientes de una ampliación de alcance

1. **Identidad y permisos:** no hay login ni autorización por rol. Cualquiera con acceso HTTP puede leer, crear o modificar usuarios, incluido su campo `role`. La clave de DELETE es compartida.
2. **Escalabilidad:** el listado carga todos los resultados, sin paginación. SQLite es el único motor verificado. La búsqueda de correo utiliza `lower(email)`, que podría requerir un índice funcional para volúmenes mayores.
3. **Migraciones:** `create_all` no actualiza tablas existentes. Los cambios futuros de esquema necesitan migraciones, por ejemplo con Alembic.
4. **Validación:** Pydantic permite coerción de booleanos y omite campos desconocidos. El correo se valida en la API, pero inserciones SQL externas pueden saltarse esa validación o la normalización a minúsculas.
5. **Operación:** no hay despliegue, copias de seguridad, CI ni comprobación activa de salud de la BD. Los requisitos usan rangos y no un archivo de versiones bloqueadas.
6. **Auditoría:** no hay fechas de creación/actualización ni historial; `internal_notes` es un texto estático.
7. **Interfaz y dispositivos:** no existe frontend ni modelo de dispositivos. Swagger permite usar la API manualmente.
8. **Licencia:** no se encontró un archivo de licencia.

Estas limitaciones se documentan sin convertir el ejercicio en un sistema diferente. La guía de instalación, los endpoints y ejemplos completos están en [README.md](README.md).

## Verificación realizada

- Python 3.14.7; FastAPI 0.141.1, Pydantic 2.13.5 y SQLAlchemy 2.0.54.
- `python -m pytest -q`: **26 pruebas aprobadas**.
- `python -m pip check`: sin dependencias incompatibles.
- Prueba HTTP con Uvicorn y SQLite temporal: arranque, POST, reinicio, consulta del usuario persistido, Swagger y `API_VERSION` personalizada correctos. Los servidores de prueba se detuvieron al terminar.
- `git diff --check`: sin errores de formato.
- Starlette emitió una advertencia de deprecación del uso de `httpx` en su cliente de pruebas; no impidió la ejecución. El cliente de pruebas conserva compatibilidad con el rango de FastAPI declarado.

Las pruebas asíncronas y la comprobación HTTP necesitaron ejecutarse fuera del sandbox de esta sesión, que bloquea sockets. No es un requisito especial de la aplicación al ejecutarla normalmente en una terminal local.
