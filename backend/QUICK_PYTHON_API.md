# Backend rapido en Python

API local para conectar el front Angular con Microsoft SQL Server.

## 1. Preparar entorno

Desde la carpeta `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-quick.txt
```

Si `python` no funciona en Windows, instala Python 3.11+ y marca la opcion "Add python.exe to PATH".

## 2. Configurar SQL Server

Copia `.env.example` a `.env` y ajusta:

```powershell
Copy-Item .env.example .env
notepad .env
```

Ejemplos comunes:

```env
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=CallCenter
DB_TRUSTED_CONNECTION=yes
```

o:

```env
DB_SERVER=localhost
DB_NAME=CallCenter
DB_USER=sa
DB_PASSWORD=tu_password
DB_TRUSTED_CONNECTION=no
```

Necesitas tener instalado el driver ODBC de SQL Server. Si no conecta, cambia `DB_DRIVER` a:

```env
DB_DRIVER=ODBC Driver 18 for SQL Server
```

## 3. Ejecutar

```powershell
uvicorn quick_api:app --reload --host 0.0.0.0 --port 3000
```

Prueba:

```powershell
Invoke-RestMethod http://localhost:3000/api/health
Invoke-RestMethod http://localhost:3000/api/candidatos
```

El front ya apunta a:

```txt
http://localhost:3000/api/candidatos
```

## Endpoints incluidos

- `GET /api/health`
- `GET /api/candidatos`
- `GET /api/candidatos/{id}`
- `POST /api/candidatos`
- `PUT /api/candidatos/{id}`
- `PATCH /api/candidatos/{id}`
- `DELETE /api/candidatos/{id}`

Al iniciar, la API crea automaticamente la tabla `dbo.candidatos_front` si no existe.
