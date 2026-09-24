# device_systems

API REST académica para administrar **usuarios**, construida con FastAPI, Pydantic v2 y SQLAlchemy 2. Los datos se guardan en SQLite y sobreviven a los reinicios. No incluye frontend, inicio de sesión ni recursos de dispositivos.

## Requisitos previos

- Python 3.11 o superior, con `pip` y soporte para entornos virtuales.
- Git, para clonar el repositorio.
- Una terminal y un navegador web.
- Conexión a Internet para descargar las dependencias durante la instalación.

SQLite viene incluido con Python: no necesitas instalar ni configurar un servidor de base de datos. La revisión local se verificó con Python 3.14.

## Paso a paso para ejecutar el proyecto

### 1. Clonar el repositorio y entrar en la carpeta

```bash
git clone https://github.com/Santiago-Moreno-Ortiz/device_systems.git
cd device_systems
```

Si ya lo clonaste, entra en la carpeta existente. Ejecuta los siguientes pasos desde esa carpeta, donde están `requirements.txt` y el directorio `app`.

### 2. Comprobar la versión de Python

En Linux o macOS:

```bash
python3 --version
```

En Windows PowerShell:

```powershell
python --version
```

La versión mostrada debe ser 3.11 o superior. Si Windows solo reconoce el comando `py`, úsalo en lugar de `python` para crear el entorno del siguiente paso.

### 3. Crear y activar un entorno virtual

El entorno virtual mantiene las dependencias del proyecto separadas de las de otros programas.

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Normalmente aparecerá `(.venv)` al comienzo de la línea de la terminal. Mantén esta terminal abierta para los siguientes pasos.

Si PowerShell bloquea la activación, puedes continuar sin cambiar sus políticas: reemplaza `python` por `.\.venv\Scripts\python.exe` en los comandos siguientes. En Linux/macOS, la alternativa sin activar es `.venv/bin/python`.

### 4. Instalar las dependencias

Con el entorno activado, en cualquiera de los sistemas:

```bash
python -m pip install -r requirements.txt
```

Espera a que la instalación termine sin errores. Este paso instala FastAPI, Uvicorn, Pydantic, SQLAlchemy y las demás dependencias.

### 5. Crear el archivo de configuración

En la primera instalación, copia el archivo de ejemplo.

**Linux / macOS:**

```bash
cp .env.example .env
```

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

Si ya tienes un archivo `.env`, conserva su contenido y omite la copia. Para probar localmente puedes utilizar los valores incluidos:

```dotenv
DATABASE_URL=sqlite:///./device_systems.db
API_KEY=device_systems_key
API_VERSION=3.0.0
```

`API_KEY` es la clave que se solicitará al eliminar usuarios. El valor incluido es de demostración.

### 6. Iniciar el servidor

```bash
python -m uvicorn app.main:app --reload
```

Cuando el arranque termine, verás un mensaje similar a:

```text
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Deja la terminal abierta mientras uses la API. La opción `--reload` reinicia el servidor cuando modificas el código y se utiliza durante el desarrollo.

Al arrancar se crea automáticamente `device_systems.db` y la tabla `users` si no existen. Una base nueva comienza sin usuarios; los datos que guardes permanecen después de detener el servidor.

### 7. Abrir la aplicación en el navegador

| Dirección | Para qué sirve |
|---|---|
| http://127.0.0.1:8000/ | Comprobar que la API responde |
| http://127.0.0.1:8000/docs | Probar las operaciones mediante Swagger UI |
| http://127.0.0.1:8000/redoc | Consultar la documentación de la API |
| http://127.0.0.1:8000/openapi.json | Consultar la especificación OpenAPI en JSON |

En la dirección raíz deberías recibir:

```json
{
  "app": "device_systems",
  "version": "3.0.0",
  "status": "ok",
  "database": "sqlite + sqlalchemy",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

La versión y el motor pueden variar si modificaste la configuración. La aplicación ofrece una API; Swagger es la interfaz disponible para probarla desde el navegador.

### 8. Crear y consultar tu primer usuario

1. Abre http://127.0.0.1:8000/docs.
2. Despliega **POST /users** y pulsa **Try it out**.
3. Reemplaza el cuerpo de la petición por este ejemplo:

```json
{
  "name": "Santiago Moreno",
  "email": "santiago@example.com",
  "role": "user",
  "is_active": true
}
```

4. Pulsa **Execute**. Una respuesta **201** confirma la creación.
5. Anota el `id` devuelto. Si repites la petición con el mismo correo, recibirás un error por duplicidad.
6. Abre **GET /users**, pulsa **Try it out** y después **Execute** para ver los usuarios guardados.
7. Para consultar uno en particular, usa **GET /users/{user_id}** e introduce su `id`.

Para editar un usuario, utiliza **PUT** con los cuatro campos o **PATCH** con los campos que quieras cambiar. Para eliminarlo, utiliza **DELETE**, introduce su `id` y completa `X-API-Key` con el valor de tu `.env` (por defecto, `device_systems_key`).

### 9. Detener el servidor y volver a ejecutarlo

Presiona `Ctrl+C` en la terminal donde está ejecutándose Uvicorn.

En una nueva sesión, entra en la carpeta del proyecto, activa el entorno y arranca el servidor. No necesitas recrear el entorno, copiar `.env` ni reinstalar las dependencias cada vez.

**Linux / macOS:**

```bash
cd device_systems
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

**Windows PowerShell:**

```powershell
cd device_systems
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Estos ejemplos suponen que estás en la carpeta que contiene el repositorio. Si ya estás dentro de `device_systems`, omite `cd device_systems`. Para salir del entorno virtual después de detener el servidor, ejecuta `deactivate`.

## Solución de problemas frecuentes

| Problema | Qué hacer |
|---|---|
| `python` o `python3` no se reconoce | Comprueba que Python esté instalado y disponible en el PATH. En Windows también puedes comprobar `py --version`. |
| No se puede crear el entorno virtual | Comprueba que tu instalación de Python incluya `venv`; algunas distribuciones Linux lo distribuyen como un paquete separado. |
| PowerShell bloquea `Activate.ps1` | Ejecuta directamente `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`; para instalar dependencias, usa ese mismo ejecutable con `-m pip install -r requirements.txt`. |
| `No module named uvicorn` | Activa el entorno correcto y ejecuta `python -m pip install -r requirements.txt`. |
| No se encuentra `requirements.txt` o el módulo `app` | Sitúate en la raíz del repositorio antes de ejecutar los comandos. |
| El puerto 8000 está ocupado | Usa `python -m uvicorn app.main:app --reload --port 8001` y abre http://127.0.0.1:8001/docs. |
| El navegador no conecta | Comprueba que Uvicorn siga ejecutándose sin errores y que la URL use el mismo puerto. |
| DELETE devuelve 401 | Comprueba que `X-API-Key` coincida con `API_KEY`; reinicia el servidor si cambiaste `.env`. |
| POST devuelve 400 por correo duplicado | Usa otro correo o consulta el usuario que ya creaste. |
| Una petición devuelve 422 | Revisa `detail` en la respuesta: indica los campos que no cumplen la validación. |

La ruta SQLite predeterminada es relativa al directorio de trabajo. Ejecuta siempre desde la raíz del repositorio para utilizar la misma base de datos. No borres `device_systems.db` si quieres conservar los usuarios.

## Configuración

El archivo `.env` se carga al importar la aplicación; las variables ya definidas en el entorno tienen prioridad.

| Variable | Valor predeterminado | Uso |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./device_systems.db` | Conexión SQLAlchemy |
| `API_KEY` | `device_systems_key` | Cabecera `X-API-Key` para DELETE; clave de demostración |
| `API_VERSION` | `3.0.0` | Versión en OpenAPI, raíz y cabecera HTTP |

Reinicia el servidor después de cambiar la configuración. `.env` y las bases SQLite están excluidos de Git. Otros motores requieren instalar su controlador y validar la compatibilidad; las pruebas incluidas usan SQLite.

## Arquitectura

```text
app/
  main.py                         Aplicación, ciclo de vida, middleware y errores
  database/database.py            Engine, Base, sesiones y get_db
  models/user_model.py            Tabla SQLAlchemy y restricciones
  schemas/user_schema.py          Entradas, validaciones y respuestas Pydantic
  dependencies/user_dependencies.py  Filtros, búsqueda por ID y API key
  routes/user_routes.py           Rutas HTTP
  services/user_service.py        Consultas, CRUD, commit y rollback
tests/test_api.py                  Pruebas automáticas con bases temporales
pruebas/                          Capturas históricas
requirements.txt                  Dependencias de ejecución
requirements-dev.txt              Dependencias para pruebas
```

Flujo de una petición: ruta → dependencias y validación → servicio → sesión SQLAlchemy → SQLite → modelo de respuesta. FastAPI comparte la dependencia `get_db` dentro de cada petición; la sesión se cierra al finalizar. Las escrituras se confirman con `commit`; los errores capturados de persistencia ejecutan `rollback`.

Las tablas se crean en el ciclo de vida de FastAPI. Importar `app.main` no crea la base. `create_all` crea tablas faltantes, pero **no migra tablas existentes** cuando cambia el modelo.

## Modelo de usuario

| Campo | Reglas |
|---|---|
| `id` | Entero generado por la base de datos |
| `name` | Entre 3 y 80 caracteres después de quitar espacios exteriores |
| `email` | Correo válido y único; se guarda en minúsculas |
| `role` | `admin`, `support` o `user`; POST usa `user` por defecto |
| `is_active` | Booleano; POST usa `true` por defecto |
| `internal_notes` | Campo interno, excluido de las respuestas públicas |

La base también exige campos no nulos, correo único, longitudes válidas y roles permitidos. El formato del correo se valida en Pydantic. `UserPublic` determina qué datos salen de la API.

Los roles son datos del usuario: **no conceden permisos**. Pydantic aplica sus conversiones habituales; no se ha activado validación estricta de booleanos. Los campos desconocidos se ignoran.

## Operaciones disponibles

| Método | Ruta | Función | Éxito |
|---|---|---|---|
| GET | `/` | Información de la API | 200 |
| GET | `/users` | Lista con filtros opcionales `role` e `is_active` | 200 |
| GET | `/users/{user_id}` | Consulta por ID | 200 |
| POST | `/users` | Crea usuario | 201 |
| PUT | `/users/{user_id}` | Reemplaza los cuatro campos editables | 200 |
| PATCH | `/users/{user_id}` | Modifica campos enviados | 200 |
| DELETE | `/users/{user_id}` | Elimina; exige `X-API-Key` | 200 |

PUT exige `name`, `email`, `role` e `is_active`. PATCH permite omitir campos, pero rechaza `null` con 422 y un objeto vacío con 400. El listado devuelve `{"total": 0, "items": []}` cuando no hay resultados. `total` cuenta los resultados filtrados; no hay paginación.

Errores: **400** por duplicados, restricciones de BD o PATCH vacío; **401** por API key ausente/incorrecta; **404** por usuario inexistente; **422** por validación; **500** por errores internos. Los errores controlados usan `{"detail": "mensaje"}`; la validación de FastAPI devuelve una lista en `detail`. Los detalles internos de errores 500 se registran en el servidor y no se exponen al cliente.

Las respuestas procesadas por el middleware incluyen `X-App-Name` y `X-API-Version`. La ruta `/` informa sobre la aplicación, pero no realiza una consulta de salud a la base.

## Ejemplo de uso

Los siguientes comandos usan la sintaxis de Bash (Linux/macOS). Con el servidor activo, ejecútalos en otra terminal. En Windows puedes realizar las mismas operaciones desde Swagger siguiendo el paso 8:

```bash
curl http://127.0.0.1:8000/

curl -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Ana Perez","email":"ana@example.com","role":"user","is_active":true}'

curl 'http://127.0.0.1:8000/users?role=user&is_active=true'
```

Usa el `id` devuelto al crear el usuario; los siguientes ejemplos suponen `1`:

```bash
curl http://127.0.0.1:8000/users/1

curl -X PUT http://127.0.0.1:8000/users/1 \
  -H 'Content-Type: application/json' \
  -d '{"name":"Ana Maria","email":"ana@example.com","role":"support","is_active":true}'

curl -X PATCH http://127.0.0.1:8000/users/1 \
  -H 'Content-Type: application/json' \
  -d '{"is_active":false}'

curl -X DELETE http://127.0.0.1:8000/users/1 \
  -H 'X-API-Key: device_systems_key'
```

Si cambiaste `API_KEY`, usa tu valor. En Swagger abre una operación, pulsa **Try it out**, completa el cuerpo o los parámetros y pulsa **Execute**. DELETE muestra el parámetro de cabecera `X-API-Key`.

## Pruebas automáticas

Desde la raíz del repositorio y con el entorno virtual activado, instala las dependencias de desarrollo y ejecuta las pruebas. No necesitas mantener Uvicorn abierto para este paso:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Las pruebas cubren CRUD, filtros, correos duplicados, nombres inválidos, PATCH nulo/vacío, PUT incompleto, IDs inexistentes, autorización de DELETE, metadatos y errores de base de datos. Usan archivos SQLite temporales independientes y no modifican la base local. `pruebas/` contiene capturas de versiones anteriores; no sustituye estas pruebas.

## Alcance y límites

Es una base académica funcional, no un sistema de usuarios listo para producción. Las consultas, creación y actualizaciones son públicas, y DELETE usa una clave compartida de demostración. No hay autenticación individual, contraseñas, autorización por rol, paginación, migraciones, registro de auditoría completo ni despliegue configurado. `internal_notes` es un texto fijo, no un historial. No hay frontend, contenedores ni licencia declarada en el repositorio.

Antes de un uso real habría que definir los permisos, proteger los endpoints y los datos personales, implementar migraciones y establecer copias de seguridad. Conserva la base existente al actualizar: borrarla elimina todos sus usuarios.

Consulta [ANALISIS.md](ANALISIS.md) para los hallazgos y cambios de esta revisión.
