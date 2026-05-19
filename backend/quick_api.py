import os
from datetime import datetime
from typing import Any

import pypyodbc as pyodbc
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

app = FastAPI(title="Callcenter Quick API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def connection_string() -> str:
    driver = env("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = env("DB_SERVER", r"localhost\SQLEXPRESS")
    database = env("DB_NAME", "CallCenter")

    if env("DB_TRUSTED_CONNECTION", "no").lower() in ("yes", "true", "1"):
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={env('DB_USER', 'sa')};"
        f"PWD={env('DB_PASSWORD')};"
        "TrustServerCertificate=yes;"
    )


def get_conn() -> pyodbc.Connection:
    return pyodbc.connect(connection_string(), autocommit=False, timeout=8)


def table_exists(table_name: str) -> bool:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?
            """,
            (table_name,),
        )
        return cursor.fetchone() is not None


def fetch_all(cursor: pyodbc.Cursor) -> list[dict[str, Any]]:
    columns = [column[0] for column in cursor.description]
    result = []
    for row in cursor.fetchall():
        item = {}
        for key, value in zip(columns, row):
            item[key] = value.isoformat() if hasattr(value, "isoformat") else value
        result.append(item)
    return result


def normalize_requerimiento(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "codigo": row.get("codigo"),
        "campaniaId": row.get("campaniaid"),
        "campaign": row.get("campaign"),
        "puestoId": row.get("puestoid"),
        "puesto": row.get("puesto"),
        "comentarios": row.get("comentarios") or "",
        "cantidad": row.get("cantidad"),
        "diasCapacitacion": row.get("diascapacitacion"),
        "fechaIngreso": row.get("fechaingreso"),
        "fechaInicioCapacitacion": row.get("fechainiciocapacitacion"),
        "fechaFinCapacitacion": row.get("fechafincapacitacion"),
        "estado": row.get("estado"),
        "testCount": row.get("testcount"),
        "aprobacionPromedio": float(row.get("aprobacionpromedio") or 0),
        "applyPath": row.get("applypath"),
        "candidatos": [],
    }


def ensure_table() -> None:
    sql = """
    IF OBJECT_ID('dbo.candidatos_front', 'U') IS NULL
    BEGIN
        CREATE TABLE dbo.candidatos_front (
            id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
            dni VARCHAR(20) NULL,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            email VARCHAR(150) NULL,
            correo VARCHAR(150) NULL,
            telefono VARCHAR(30) NULL,
            puesto VARCHAR(120) NULL,
            medioPreferido VARCHAR(30) NULL,
            cvUrl VARCHAR(500) NULL,
            fechaPostulacion DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
            apto VARCHAR(10) NULL,
            entrevista VARCHAR(10) NULL,
            observaciones VARCHAR(1000) NULL,
            fechaEntrevista DATETIME2(0) NULL,
            evaluador VARCHAR(120) NULL,
            estado VARCHAR(30) NOT NULL DEFAULT 'pendiente'
        );
    END
    """
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()


def ensure_requerimientos_table() -> None:
    if table_exists("requerimientos"):
        return

    sql = """
    CREATE TABLE dbo.requerimientos (
        id_requerimiento INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        codigo VARCHAR(30) NOT NULL UNIQUE,
        campania_id INT NOT NULL DEFAULT 0,
        campaign VARCHAR(120) NOT NULL DEFAULT '',
        puesto_id INT NOT NULL DEFAULT 0,
        puesto VARCHAR(120) NOT NULL DEFAULT '',
        comentarios VARCHAR(500) NULL,
        cantidad INT NOT NULL DEFAULT 1,
        dias_capacitacion INT NOT NULL DEFAULT 1,
        fecha_ingreso DATE NULL,
        fecha_inicio_capacitacion DATE NULL,
        fecha_fin_capacitacion DATE NULL,
        estado VARCHAR(20) NOT NULL DEFAULT 'ABIERTO',
        test_count INT NOT NULL DEFAULT 1,
        aprobacion_promedio DECIMAL(5,2) NOT NULL DEFAULT 10,
        created_at DATETIME2(0) NOT NULL DEFAULT SYSDATETIME()
    )
    """
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()


class Candidato(BaseModel):
    dni: str | None = None
    nombre: str
    apellido: str
    email: str | None = None
    correo: str | None = None
    telefono: str | None = None
    puesto: str | None = None
    medioPreferido: str | None = "whatsapp"
    cvUrl: str | None = None
    fechaPostulacion: datetime | None = None
    apto: str | None = None
    entrevista: str | None = None
    observaciones: str | None = None
    fechaEntrevista: datetime | None = None
    evaluador: str | None = None
    estado: str | None = "pendiente"


class CandidatoPatch(BaseModel):
    dni: str | None = None
    nombre: str | None = None
    apellido: str | None = None
    email: str | None = None
    correo: str | None = None
    telefono: str | None = None
    puesto: str | None = None
    medioPreferido: str | None = None
    cvUrl: str | None = None
    fechaPostulacion: datetime | None = None
    apto: str | None = None
    entrevista: str | None = None
    observaciones: str | None = None
    fechaEntrevista: datetime | None = None
    evaluador: str | None = None
    estado: str | None = None


class RequerimientoCreate(BaseModel):
    campaniaId: int
    puestoId: int
    comentarios: str | None = ""
    cantidad: int
    diasCapacitacion: int
    fechaIngreso: str
    fechaInicioCapacitacion: str
    fechaFinCapacitacion: str
    estado: str | None = "ABIERTO"


def ensure_campanias_table() -> None:
    if not table_exists("campanias"):
        sql = """
        CREATE TABLE dbo.campanias (
            id_campania INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL UNIQUE,
            estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVA',
            created_at DATETIME2(0) NOT NULL DEFAULT SYSDATETIME()
        )
        """
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dbo.campanias")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO dbo.campanias (nombre, estado) VALUES (?, ?)",
                [
                    ("Renovacion Proactiva", "ACTIVA"),
                    ("Laboratorio", "ACTIVA"),
                    ("Upselling", "ACTIVA"),
                    ("Portabilidad BM", "ACTIVA"),
                    ("Campania Fin de Ano", "INACTIVA"),
                ],
            )
            conn.commit()


def ensure_puestos_table() -> None:
    if not table_exists("puestos"):
        sql = """
        CREATE TABLE dbo.puestos (
            id_puesto INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL UNIQUE,
            estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
            created_at DATETIME2(0) NOT NULL DEFAULT SYSDATETIME()
        )
        """
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dbo.puestos")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO dbo.puestos (nombre, estado) VALUES (?, ?)",
                [
                    ("Asesor de ventas", "ACTIVO"),
                    ("Asesor de atencion al cliente", "ACTIVO"),
                    ("Back Office", "ACTIVO"),
                    ("Coordinador de formacion", "INACTIVO"),
                ],
            )
            conn.commit()


@app.on_event("startup")
def startup() -> None:
    try:
        ensure_table()
        ensure_campanias_table()
        ensure_puestos_table()
        ensure_requerimientos_table()
    except Exception as exc:
        print(f"No se pudo inicializar SQL Server: {exc}")


@app.get("/api/health")
def health() -> dict[str, str]:
    try:
        with get_conn() as conn:
            conn.cursor().execute("SELECT 1")
        return {"status": "ok", "database": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"SQL Server no disponible: {exc}")


@app.get("/api/candidatos")
def listar_candidatos() -> list[dict[str, Any]]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, dni, nombre, apellido, email, correo, telefono, puesto,
                   medioPreferido, cvUrl, fechaPostulacion, apto, entrevista,
                   observaciones, fechaEntrevista, evaluador, estado
            FROM dbo.candidatos_front
            ORDER BY id DESC
            """
        )
        return fetch_all(cursor)


@app.get("/api/campanias")
def listar_campanias() -> list[dict[str, Any]]:
    ensure_campanias_table()

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_campania AS id, nombre, estado
            FROM dbo.campanias
            WHERE estado = 'ACTIVA'
            ORDER BY nombre
            """
        )
        return fetch_all(cursor)


@app.get("/api/puestos")
def listar_puestos() -> list[dict[str, Any]]:
    ensure_puestos_table()

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_puesto AS id, nombre, estado
            FROM dbo.puestos
            WHERE estado = 'ACTIVO'
            ORDER BY nombre
            """
        )
        return fetch_all(cursor)


@app.get("/api/requerimientos")
def listar_requerimientos() -> list[dict[str, Any]]:
    ensure_requerimientos_table()

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                codigo,
                campania_id AS campaniaId,
                campaign,
                puesto_id AS puestoId,
                puesto,
                ISNULL(comentarios, '') AS comentarios,
                cantidad,
                dias_capacitacion AS diasCapacitacion,
                CONVERT(VARCHAR(10), fecha_ingreso, 23) AS fechaIngreso,
                CONVERT(VARCHAR(10), fecha_inicio_capacitacion, 23) AS fechaInicioCapacitacion,
                CONVERT(VARCHAR(10), fecha_fin_capacitacion, 23) AS fechaFinCapacitacion,
                estado,
                test_count AS testCount,
                aprobacion_promedio AS aprobacionPromedio,
                '/postular/' + codigo AS applyPath
            FROM dbo.requerimientos
            ORDER BY created_at DESC, id_requerimiento DESC
            """
        )
        requerimientos = fetch_all(cursor)

    return [normalize_requerimiento(rq) for rq in requerimientos]


@app.post("/api/requerimientos", status_code=201)
def crear_requerimiento(requerimiento: RequerimientoCreate) -> dict[str, Any]:
    ensure_campanias_table()
    ensure_puestos_table()
    ensure_requerimientos_table()

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nombre FROM dbo.campanias WHERE id_campania = ? AND estado = 'ACTIVA'",
            (requerimiento.campaniaId,),
        )
        campania = cursor.fetchone()
        if not campania:
            raise HTTPException(status_code=404, detail="Campania no encontrada")

        cursor.execute(
            "SELECT nombre FROM dbo.puestos WHERE id_puesto = ? AND estado = 'ACTIVO'",
            (requerimiento.puestoId,),
        )
        puesto = cursor.fetchone()
        if not puesto:
            raise HTTPException(status_code=404, detail="Puesto no encontrado")

        cursor.execute("SELECT ISNULL(MAX(id_requerimiento), 0) + 1 FROM dbo.requerimientos")
        next_id = cursor.fetchone()[0]
        codigo = f"RQ{int(next_id):03d}"

        cursor.execute(
            """
            INSERT INTO dbo.requerimientos (
                codigo, campania_id, campaign, puesto_id, puesto, comentarios,
                cantidad, dias_capacitacion, fecha_ingreso,
                fecha_inicio_capacitacion, fecha_fin_capacitacion, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                codigo,
                requerimiento.campaniaId,
                campania[0],
                requerimiento.puestoId,
                puesto[0],
                requerimiento.comentarios or "",
                requerimiento.cantidad,
                requerimiento.diasCapacitacion,
                requerimiento.fechaIngreso,
                requerimiento.fechaInicioCapacitacion,
                requerimiento.fechaFinCapacitacion,
                requerimiento.estado or "ABIERTO",
            ),
        )
        conn.commit()

    return obtener_requerimiento_por_codigo(codigo)


def obtener_requerimiento_por_codigo(codigo: str) -> dict[str, Any]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                codigo,
                campania_id AS campaniaId,
                campaign,
                puesto_id AS puestoId,
                puesto,
                ISNULL(comentarios, '') AS comentarios,
                cantidad,
                dias_capacitacion AS diasCapacitacion,
                CONVERT(VARCHAR(10), fecha_ingreso, 23) AS fechaIngreso,
                CONVERT(VARCHAR(10), fecha_inicio_capacitacion, 23) AS fechaInicioCapacitacion,
                CONVERT(VARCHAR(10), fecha_fin_capacitacion, 23) AS fechaFinCapacitacion,
                estado,
                test_count AS testCount,
                aprobacion_promedio AS aprobacionPromedio,
                '/postular/' + codigo AS applyPath
            FROM dbo.requerimientos
            WHERE codigo = ?
            """,
            (codigo,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

        return normalize_requerimiento(dict_from_row(cursor, row))


@app.get("/api/candidatos/{candidato_id}")
def obtener_candidato(candidato_id: int) -> dict[str, Any]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, dni, nombre, apellido, email, correo, telefono, puesto,
                   medioPreferido, cvUrl, fechaPostulacion, apto, entrevista,
                   observaciones, fechaEntrevista, evaluador, estado
            FROM dbo.candidatos_front
            WHERE id = ?
            """,
            (candidato_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Candidato no encontrado")
        return dict_from_row(cursor, row)


@app.post("/api/candidatos", status_code=201)
def crear_candidato(candidato: Candidato) -> dict[str, Any]:
    fecha_postulacion = candidato.fechaPostulacion or datetime.now()
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO dbo.candidatos_front (
                dni, nombre, apellido, email, correo, telefono, puesto,
                medioPreferido, cvUrl, fechaPostulacion, apto, entrevista,
                observaciones, fechaEntrevista, evaluador, estado
            )
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidato.dni,
                candidato.nombre,
                candidato.apellido,
                candidato.email or candidato.correo,
                candidato.correo or candidato.email,
                candidato.telefono,
                candidato.puesto,
                candidato.medioPreferido,
                candidato.cvUrl,
                fecha_postulacion,
                candidato.apto,
                candidato.entrevista,
                candidato.observaciones,
                candidato.fechaEntrevista,
                candidato.evaluador,
                candidato.estado or "pendiente",
            ),
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
    return obtener_candidato(new_id)


@app.put("/api/candidatos/{candidato_id}")
def reemplazar_candidato(candidato_id: int, candidato: Candidato) -> dict[str, Any]:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM dbo.candidatos_front WHERE id = ?", (candidato_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Candidato no encontrado")

        cursor.execute(
            """
            UPDATE dbo.candidatos_front
            SET dni = ?, nombre = ?, apellido = ?, email = ?, correo = ?,
                telefono = ?, puesto = ?, medioPreferido = ?, cvUrl = ?,
                fechaPostulacion = ?, apto = ?, entrevista = ?, observaciones = ?,
                fechaEntrevista = ?, evaluador = ?, estado = ?
            WHERE id = ?
            """,
            (
                candidato.dni,
                candidato.nombre,
                candidato.apellido,
                candidato.email or candidato.correo,
                candidato.correo or candidato.email,
                candidato.telefono,
                candidato.puesto,
                candidato.medioPreferido,
                candidato.cvUrl,
                candidato.fechaPostulacion or datetime.now(),
                candidato.apto,
                candidato.entrevista,
                candidato.observaciones,
                candidato.fechaEntrevista,
                candidato.evaluador,
                candidato.estado or "pendiente",
                candidato_id,
            ),
        )
        conn.commit()
    return obtener_candidato(candidato_id)


@app.patch("/api/candidatos/{candidato_id}")
def actualizar_candidato(candidato_id: int, cambios: CandidatoPatch) -> dict[str, Any]:
    data = cambios.model_dump(exclude_unset=True)
    if not data:
        return obtener_candidato(candidato_id)

    allowed = set(CandidatoPatch.model_fields.keys())
    fields = [field for field in data if field in allowed]
    values = [data[field] for field in fields]
    set_clause = ", ".join(f"{field} = ?" for field in fields)

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM dbo.candidatos_front WHERE id = ?", (candidato_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Candidato no encontrado")
        cursor.execute(
            f"UPDATE dbo.candidatos_front SET {set_clause} WHERE id = ?",
            (*values, candidato_id),
        )
        conn.commit()
    return obtener_candidato(candidato_id)


@app.delete("/api/candidatos/{candidato_id}", status_code=204)
def eliminar_candidato(candidato_id: int) -> None:
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dbo.candidatos_front WHERE id = ?", (candidato_id,))
        conn.commit()


def dict_from_row(cursor: pyodbc.Cursor, row: pyodbc.Row) -> dict[str, Any]:
    columns = [column[0] for column in cursor.description]
    data = {}
    for key, value in zip(columns, row):
        data[key] = value.isoformat() if hasattr(value, "isoformat") else value
    return data
