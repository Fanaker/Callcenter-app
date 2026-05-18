"""
AWS Lambda Handler for Recruitment Management System
Production-ready with connection pooling, Pydantic validation, structured logging,
and explicit transaction management.
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import pyodbc
from pydantic import BaseModel, validator, ValidationError, EmailStr, Field
import re
import traceback
import uuid

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def log_structured(
    level: str,
    message: str,
    request_id: str,
    **extras
) -> None:
    """Emit structured JSON log line."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "requestId": request_id,
        **extras
    }
    print(json.dumps(log_entry))


# ============================================================================
# CONNECTION POOLING
# ============================================================================

class ConnectionPool:
    """Thread-safe connection pool for ODBC connections."""

    def __init__(self, max_size: int = 5):
        """Initialize connection pool.

        Args:
            max_size: Maximum number of connections to keep in pool
        """
        self.max_size = max_size
        self.available: List[pyodbc.Connection] = []
        self.in_use: set = set()

    def _create_connection(self) -> pyodbc.Connection:
        """Create new database connection."""
        conn_str = (
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={os.getenv('DB_HOST')};"
            f"Database={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASS')};"
            f"TrustServerCertificate=yes"
        )
        return pyodbc.connect(conn_str, autocommit=False)

    def _validate_connection(self, conn: pyodbc.Connection) -> bool:
        """Validate connection before returning from pool."""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            return False

    @contextmanager
    def get_connection(self):
        """Get connection from pool or create new one.

        Yields:
            pyodbc.Connection: Database connection

        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                ...
        """
        conn = None
        try:
            # Try to get from available pool
            if self.available:
                conn = self.available.pop()
                if not self._validate_connection(conn):
                    conn = self._create_connection()
            else:
                conn = self._create_connection()

            self.in_use.add(id(conn))
            yield conn

        finally:
            if conn:
                self.in_use.discard(id(conn))
                if len(self.available) < self.max_size:
                    try:
                        conn.rollback()
                        self.available.append(conn)
                    except Exception:
                        try:
                            conn.close()
                        except Exception:
                            pass
                else:
                    try:
                        conn.close()
                    except Exception:
                        pass

    def close_all(self) -> None:
        """Close all connections in pool."""
        for conn in self.available:
            try:
                conn.close()
            except Exception:
                pass
        self.available.clear()


# Global pool instance
_pool = ConnectionPool(max_size=5)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Postulante(BaseModel):
    """Postulante data model."""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    dni: str
    email: EmailStr
    telefono: str
    medio_preferido: str
    cv_url: Optional[str] = None

    @validator("nombre", "apellido", pre=True)
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("dni")
    def validate_dni(cls, v: str) -> str:
        if not re.match(r"^\d{8}$", v):
            raise ValueError("DNI debe contener exactamente 8 dígitos")
        return v

    @validator("telefono")
    def validate_telefono(cls, v: str) -> str:
        if not re.match(r"^9\d{8}$", v):
            raise ValueError("Teléfono debe comenzar con 9 y tener 9 dígitos")
        return v

    @validator("medio_preferido")
    def validate_medio_preferido(cls, v: str) -> str:
        if v not in ("email", "whatsapp", "llamada"):
            raise ValueError("Medio preferido debe ser: email, whatsapp o llamada")
        return v.lower()


class RequerimientoCreate(BaseModel):
    """Requerimiento creation model."""
    codigo: str = Field(..., min_length=3, max_length=50)
    campania_id: int = Field(..., gt=0)
    puesto_id: int = Field(..., gt=0)
    cantidad_vacantes: int = Field(..., ge=1, le=1000)
    descripcion: str = Field(..., max_length=1000)

    @validator("codigo", pre=True)
    def uppercase_codigo(cls, v):
        if not isinstance(v, str):
            raise ValueError("Código debe ser string")
        return v.strip().upper()

    @validator("descripcion", pre=True)
    def strip_descripcion(cls, v):
        return v.strip() if isinstance(v, str) else v


class PostulacionCreate(BaseModel):
    """Postulación creation model."""
    requerimiento_id: int = Field(..., gt=0)
    postulante: Postulante


class RequisitoUpdate(BaseModel):
    """Requisito update model."""
    apto: bool


class EntrevistaUpdate(BaseModel):
    """Entrevista update model."""
    entrevista_aprobada: bool
    fecha_entrevista: Optional[str] = None
    notas_entrevista: Optional[str] = Field(None, max_length=1000)

    @validator("notas_entrevista", pre=True)
    def strip_notas(cls, v):
        return v.strip() if isinstance(v, str) else v


class ContratacionUpdate(BaseModel):
    """Contratación update model."""
    contratar: bool
    fecha_inicio_capacitacion: Optional[str] = None
    notas_contratacion: Optional[str] = Field(None, max_length=1000)

    @validator("notas_contratacion", pre=True)
    def strip_notas(cls, v):
        return v.strip() if isinstance(v, str) else v


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def make_response(
    status_code: int,
    body: Dict[str, Any],
    request_id: str
) -> Dict[str, Any]:
    """Create Lambda response object.

    Args:
        status_code: HTTP status code
        body: Response body dict
        request_id: Request ID for correlation

    Returns:
        Lambda response dict
    """
    cors_origin = os.getenv("CORS_ORIGIN", "*")
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": cors_origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body, default=str),
    }


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse request body from Lambda event.

    Args:
        event: Lambda event object

    Returns:
        Parsed body dict or empty dict
    """
    body = event.get("body", "{}")
    if isinstance(body, str):
        return json.loads(body) if body else {}
    return body


def convert_types(row: tuple, columns: List[str]) -> Dict[str, Any]:
    """Convert database row types for JSON serialization.

    Args:
        row: Database row tuple
        columns: Column names

    Returns:
        Dict with converted types
    """
    result = {}
    for col, val in zip(columns, row):
        if val is None:
            result[col] = None
        elif isinstance(val, bool):
            result[col] = val
        elif hasattr(val, "isoformat"):
            result[col] = val.isoformat()
        elif isinstance(val, int):
            result[col] = val
        else:
            result[col] = str(val)
    return result


def check_foreign_key(
    pool: ConnectionPool,
    table: str,
    id_col: str,
    id_val: int,
    request_id: str
) -> bool:
    """Check if foreign key exists.

    Args:
        pool: Connection pool
        table: Table name
        id_col: ID column name
        id_val: ID value to check
        request_id: Request ID for logging

    Returns:
        True if exists, False otherwise
    """
    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {table} WHERE {id_col} = ?",
                (id_val,)
            )
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
    except Exception as e:
        log_structured("ERROR", f"Error checking FK {table}.{id_col}", request_id, error=str(e))
        return False


def check_duplicate(
    pool: ConnectionPool,
    table: str,
    col: str,
    val: Any,
    request_id: str
) -> bool:
    """Check if value exists in table.

    Args:
        pool: Connection pool
        table: Table name
        col: Column name
        val: Value to check
        request_id: Request ID for logging

    Returns:
        True if exists, False otherwise
    """
    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT 1 FROM {table} WHERE {col} = ?", (val,))
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
    except Exception as e:
        log_structured("ERROR", f"Error checking duplicate {table}.{col}", request_id, error=str(e))
        return False


# ============================================================================
# HANDLERS
# ============================================================================

def handle_get_campanias_activas(
    pool: ConnectionPool,
    request_id: str
) -> Dict[str, Any]:
    """GET /campanias/activas - Get active campaigns."""
    log_structured("INFO", "GET /campanias/activas - inicio", request_id)

    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_campania, nombre, descripcion, fecha_inicio, fecha_fin "
                "FROM campanias WHERE activa = 1 ORDER BY fecha_inicio DESC"
            )
            cols = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            campanias = [convert_types(row, cols) for row in rows]
            log_structured("INFO", "GET /campanias/activas - exito", request_id, count=len(campanias))
            return make_response(200, {"campanias": campanias}, request_id)

    except Exception as e:
        log_structured(
            "ERROR",
            "GET /campanias/activas - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_get_puestos_activos(
    pool: ConnectionPool,
    request_id: str
) -> Dict[str, Any]:
    """GET /puestos/activos - Get active positions."""
    log_structured("INFO", "GET /puestos/activos - inicio", request_id)

    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_puesto, nombre, descripcion FROM puestos WHERE activo = 1 ORDER BY nombre"
            )
            cols = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            puestos = [convert_types(row, cols) for row in rows]
            log_structured("INFO", "GET /puestos/activos - exito", request_id, count=len(puestos))
            return make_response(200, {"puestos": puestos}, request_id)

    except Exception as e:
        log_structured(
            "ERROR",
            "GET /puestos/activos - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_get_requerimientos(
    pool: ConnectionPool,
    query_params: Dict[str, Any],
    request_id: str
) -> Dict[str, Any]:
    """GET /requerimientos - Get requirements with optional filters."""
    log_structured("INFO", "GET /requerimientos - inicio", request_id, filters=query_params)

    try:
        estado = query_params.get("estado")
        campania_id = query_params.get("campaniaId")

        query = (
            "SELECT id_requerimiento, codigo, id_campania, id_puesto, cantidad_vacantes, "
            "descripcion, estado, fecha_creacion FROM requerimientos WHERE 1=1"
        )
        params = []

        if estado:
            query += " AND estado = ?"
            params.append(estado)
        if campania_id:
            try:
                cid = int(campania_id)
                query += " AND id_campania = ?"
                params.append(cid)
            except ValueError:
                return make_response(400, {"error": "campaniaId debe ser numérico"}, request_id)

        query += " ORDER BY fecha_creacion DESC"

        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            cols = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            requerimientos = [convert_types(row, cols) for row in rows]
            log_structured("INFO", "GET /requerimientos - exito", request_id, count=len(requerimientos))
            return make_response(200, {"requerimientos": requerimientos}, request_id)

    except Exception as e:
        log_structured(
            "ERROR",
            "GET /requerimientos - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_post_requerimientos(
    pool: ConnectionPool,
    body: Dict[str, Any],
    request_id: str
) -> Dict[str, Any]:
    """POST /requerimientos - Create new requirement."""
    log_structured("INFO", "POST /requerimientos - inicio", request_id, payload=body)

    try:
        req = RequerimientoCreate(**body)
    except ValidationError as e:
        details = {field: [str(err) for err in errors] for field, errors in e.errors()}
        log_structured("WARN", "POST /requerimientos - validacion fallida", request_id, details=str(details))
        return make_response(422, {"error": "Datos inválidos", "details": details}, request_id)

    # Check foreign keys
    if not check_foreign_key(pool, "campanias", "id_campania", req.campania_id, request_id):
        return make_response(404, {"error": "Campaña no encontrada"}, request_id)

    if not check_foreign_key(pool, "puestos", "id_puesto", req.puesto_id, request_id):
        return make_response(404, {"error": "Puesto no encontrado"}, request_id)

    # Check duplicate codigo
    if check_duplicate(pool, "requerimientos", "codigo", req.codigo, request_id):
        log_structured("WARN", "POST /requerimientos - codigo duplicado", request_id, codigo=req.codigo)
        return make_response(409, {"error": "Código de requerimiento ya existe"}, request_id)

    try:
        with pool.get_connection() as conn:
            conn.begin()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO requerimientos (codigo, id_campania, id_puesto, cantidad_vacantes, "
                    "descripcion, estado, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        req.codigo,
                        req.campania_id,
                        req.puesto_id,
                        req.cantidad_vacantes,
                        req.descripcion,
                        "nueva",
                        datetime.utcnow().isoformat()
                    )
                )
                conn.commit()
                cursor.close()

                log_structured("INFO", "POST /requerimientos - exito", request_id, codigo=req.codigo)
                return make_response(201, {"mensaje": "Requerimiento creado exitosamente", "codigo": req.codigo}, request_id)

            except Exception as e:
                conn.rollback()
                raise e

    except Exception as e:
        log_structured(
            "ERROR",
            "POST /requerimientos - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_get_requerimiento_by_codigo(
    pool: ConnectionPool,
    codigo: str,
    request_id: str
) -> Dict[str, Any]:
    """GET /requerimientos/{codigo} - Get requirement by codigo."""
    log_structured("INFO", "GET /requerimientos/{codigo} - inicio", request_id, codigo=codigo)

    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_requerimiento, codigo, id_campania, id_puesto, cantidad_vacantes, "
                "descripcion, estado, fecha_creacion FROM requerimientos WHERE codigo = ?",
                (codigo,)
            )
            row = cursor.fetchone()
            cursor.close()

            if not row:
                return make_response(404, {"error": "Requerimiento no encontrado"}, request_id)

            cols = [desc[0] for desc in cursor.description]
            requerimiento = convert_types(row, cols)

            log_structured("INFO", "GET /requerimientos/{codigo} - exito", request_id, codigo=codigo)
            return make_response(200, {"requerimiento": requerimiento}, request_id)

    except Exception as e:
        log_structured(
            "ERROR",
            "GET /requerimientos/{codigo} - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_get_requerimiento_postulaciones(
    pool: ConnectionPool,
    codigo: str,
    request_id: str
) -> Dict[str, Any]:
    """GET /requerimientos/{codigo}/postulaciones - Get postulaciones for requirement."""
    log_structured("INFO", "GET /requerimientos/{codigo}/postulaciones - inicio", request_id, codigo=codigo)

    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()

            # Get requerimiento_id
            cursor.execute(
                "SELECT id_requerimiento FROM requerimientos WHERE codigo = ?",
                (codigo,)
            )
            req_row = cursor.fetchone()
            if not req_row:
                return make_response(404, {"error": "Requerimiento no encontrado"}, request_id)

            req_id = req_row[0]

            # Get postulaciones
            cursor.execute(
                "SELECT p.id_postulacion, p.id_requerimiento, p.id_postulante, "
                "po.nombre, po.apellido, po.dni, po.email, p.requisito_revisado, p.apto, "
                "p.entrevista_aprobada, p.fecha_entrevista, p.contratar, p.estado, p.fecha_postulacion "
                "FROM postulaciones p "
                "JOIN postulantes po ON p.id_postulante = po.id_postulante "
                "WHERE p.id_requerimiento = ? "
                "ORDER BY p.fecha_postulacion DESC",
                (req_id,)
            )

            cols = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            postulaciones = [convert_types(row, cols) for row in rows]

            log_structured("INFO", "GET /requerimientos/{codigo}/postulaciones - exito", request_id, codigo=codigo, count=len(postulaciones))
            return make_response(200, {"postulaciones": postulaciones}, request_id)

    except Exception as e:
        log_structured(
            "ERROR",
            "GET /requerimientos/{codigo}/postulaciones - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_post_postulaciones(
    pool: ConnectionPool,
    body: Dict[str, Any],
    request_id: str
) -> Dict[str, Any]:
    """POST /postulaciones - Create new application."""
    log_structured("INFO", "POST /postulaciones - inicio", request_id)

    try:
        postulacion = PostulacionCreate(**body)
    except ValidationError as e:
        details = {field: [str(err) for err in errors] for field, errors in e.errors()}
        log_structured("WARN", "POST /postulaciones - validacion fallida", request_id, details=str(details))
        return make_response(422, {"error": "Datos inválidos", "details": details}, request_id)

    # Check if requerimiento exists
    if not check_foreign_key(pool, "requerimientos", "id_requerimiento", postulacion.requerimiento_id, request_id):
        return make_response(404, {"error": "Requerimiento no encontrado"}, request_id)

    try:
        with pool.get_connection() as conn:
            conn.begin()
            try:
                cursor = conn.cursor()

                # Check for duplicate active application
                cursor.execute(
                    "SELECT 1 FROM postulantes WHERE dni = ?",
                    (postulacion.postulante.dni,)
                )
                postulante_row = cursor.fetchone()

                if postulante_row:
                    postulante_id = cursor.execute(
                        "SELECT id_postulante FROM postulantes WHERE dni = ?",
                        (postulacion.postulante.dni,)
                    ).fetchone()[0]
                else:
                    # Insert new postulante
                    cursor.execute(
                        "INSERT INTO postulantes (nombre, apellido, dni, email, telefono, medio_preferido, cv_url) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            postulacion.postulante.nombre,
                            postulacion.postulante.apellido,
                            postulacion.postulante.dni,
                            postulacion.postulante.email,
                            postulacion.postulante.telefono,
                            postulacion.postulante.medio_preferido,
                            postulacion.postulante.cv_url,
                        )
                    )
                    cursor.execute("SELECT @@IDENTITY")
                    postulante_id = int(cursor.fetchone()[0])

                # Check duplicate application in same requirement
                cursor.execute(
                    "SELECT 1 FROM postulaciones WHERE id_requerimiento = ? AND id_postulante = ? AND estado IN ('nueva', 'entrevista', 'contratacion')",
                    (postulacion.requerimiento_id, postulante_id)
                )
                if cursor.fetchone():
                    conn.rollback()
                    log_structured("WARN", "POST /postulaciones - aplicacion duplicada", request_id, dni=postulacion.postulante.dni)
                    return make_response(409, {"error": "Ya existe una postulación activa para este requerimiento"}, request_id)

                # Insert postulacion
                cursor.execute(
                    "INSERT INTO postulaciones (id_requerimiento, id_postulante, requisito_revisado, apto, "
                    "entrevista_aprobada, fecha_entrevista, notas_entrevista, contratar, "
                    "fecha_inicio_capacitacion, notas_contratacion, estado, fecha_postulacion, fecha_actualizacion) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        postulacion.requerimiento_id,
                        postulante_id,
                        False,
                        False,
                        False,
                        None,
                        None,
                        False,
                        None,
                        None,
                        "nueva",
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat(),
                    )
                )

                conn.commit()
                cursor.close()

                log_structured("INFO", "POST /postulaciones - exito", request_id, dni=postulacion.postulante.dni)
                return make_response(201, {"mensaje": "Postulación creada exitosamente"}, request_id)

            except Exception as e:
                conn.rollback()
                raise e

    except Exception as e:
        log_structured(
            "ERROR",
            "POST /postulaciones - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_put_postulacion_requisito(
    pool: ConnectionPool,
    postulacion_id: int,
    body: Dict[str, Any],
    request_id: str
) -> Dict[str, Any]:
    """PUT /postulaciones/{id}/requisito - Update requisito review."""
    log_structured("INFO", "PUT /postulaciones/{id}/requisito - inicio", request_id, postulacion_id=postulacion_id)

    try:
        update = RequisitoUpdate(**body)
    except ValidationError as e:
        details = {field: [str(err) for err in errors] for field, errors in e.errors()}
        return make_response(422, {"error": "Datos inválidos", "details": details}, request_id)

    try:
        with pool.get_connection() as conn:
            conn.begin()
            try:
                cursor = conn.cursor()

                # Check state
                cursor.execute(
                    "SELECT estado FROM postulaciones WHERE id_postulacion = ?",
                    (postulacion_id,)
                )
                state_row = cursor.fetchone()

                if not state_row:
                    conn.rollback()
                    return make_response(404, {"error": "Postulación no encontrada"}, request_id)

                if state_row[0] != "nueva":
                    conn.rollback()
                    return make_response(
                        409,
                        {"error": f"No se puede actualizar requisito en estado '{state_row[0]}'"},
                        request_id
                    )

                # Update
                cursor.execute(
                    "UPDATE postulaciones SET requisito_revisado = ?, apto = ?, estado = ?, fecha_actualizacion = ? "
                    "WHERE id_postulacion = ?",
                    (
                        True,
                        update.apto,
                        "entrevista" if update.apto else "rechazada",
                        datetime.utcnow().isoformat(),
                        postulacion_id
                    )
                )

                conn.commit()
                cursor.close()

                log_structured("INFO", "PUT /postulaciones/{id}/requisito - exito", request_id, postulacion_id=postulacion_id)
                return make_response(200, {"mensaje": "Postulación actualizada"}, request_id)

            except Exception as e:
                conn.rollback()
                raise e

    except Exception as e:
        log_structured(
            "ERROR",
            "PUT /postulaciones/{id}/requisito - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_put_postulacion_entrevista(
    pool: ConnectionPool,
    postulacion_id: int,
    body: Dict[str, Any],
    request_id: str
) -> Dict[str, Any]:
    """PUT /postulaciones/{id}/entrevista - Update interview."""
    log_structured("INFO", "PUT /postulaciones/{id}/entrevista - inicio", request_id, postulacion_id=postulacion_id)

    try:
        update = EntrevistaUpdate(**body)
    except ValidationError as e:
        details = {field: [str(err) for err in errors] for field, errors in e.errors()}
        return make_response(422, {"error": "Datos inválidos", "details": details}, request_id)

    try:
        with pool.get_connection() as conn:
            conn.begin()
            try:
                cursor = conn.cursor()

                # Check state
                cursor.execute(
                    "SELECT estado FROM postulaciones WHERE id_postulacion = ?",
                    (postulacion_id,)
                )
                state_row = cursor.fetchone()

                if not state_row:
                    conn.rollback()
                    return make_response(404, {"error": "Postulación no encontrada"}, request_id)

                if state_row[0] != "entrevista":
                    conn.rollback()
                    return make_response(
                        409,
                        {"error": f"No se puede actualizar entrevista en estado '{state_row[0]}'"},
                        request_id
                    )

                # Update
                cursor.execute(
                    "UPDATE postulaciones SET entrevista_aprobada = ?, fecha_entrevista = ?, "
                    "notas_entrevista = ?, estado = ?, fecha_actualizacion = ? "
                    "WHERE id_postulacion = ?",
                    (
                        update.entrevista_aprobada,
                        update.fecha_entrevista,
                        update.notas_entrevista,
                        "contratacion" if update.entrevista_aprobada else "rechazada",
                        datetime.utcnow().isoformat(),
                        postulacion_id
                    )
                )

                conn.commit()
                cursor.close()

                log_structured("INFO", "PUT /postulaciones/{id}/entrevista - exito", request_id, postulacion_id=postulacion_id)
                return make_response(200, {"mensaje": "Postulación actualizada"}, request_id)

            except Exception as e:
                conn.rollback()
                raise e

    except Exception as e:
        log_structured(
            "ERROR",
            "PUT /postulaciones/{id}/entrevista - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


def handle_put_postulacion_contratacion(
    pool: ConnectionPool,
    postulacion_id: int,
    body: Dict[str, Any],
    request_id: str
) -> Dict[str, Any]:
    """PUT /postulaciones/{id}/contratacion - Update hiring."""
    log_structured("INFO", "PUT /postulaciones/{id}/contratacion - inicio", request_id, postulacion_id=postulacion_id)

    try:
        update = ContratacionUpdate(**body)
    except ValidationError as e:
        details = {field: [str(err) for err in errors] for field, errors in e.errors()}
        return make_response(422, {"error": "Datos inválidos", "details": details}, request_id)

    try:
        with pool.get_connection() as conn:
            conn.begin()
            try:
                cursor = conn.cursor()

                # Check state
                cursor.execute(
                    "SELECT estado FROM postulaciones WHERE id_postulacion = ?",
                    (postulacion_id,)
                )
                state_row = cursor.fetchone()

                if not state_row:
                    conn.rollback()
                    return make_response(404, {"error": "Postulación no encontrada"}, request_id)

                if state_row[0] != "contratacion":
                    conn.rollback()
                    return make_response(
                        409,
                        {"error": f"No se puede contratar en estado '{state_row[0]}'"},
                        request_id
                    )

                # Update
                cursor.execute(
                    "UPDATE postulaciones SET contratar = ?, fecha_inicio_capacitacion = ?, "
                    "notas_contratacion = ?, estado = ?, fecha_actualizacion = ? "
                    "WHERE id_postulacion = ?",
                    (
                        update.contratar,
                        update.fecha_inicio_capacitacion,
                        update.notas_contratacion,
                        "contratado" if update.contratar else "rechazada",
                        datetime.utcnow().isoformat(),
                        postulacion_id
                    )
                )

                conn.commit()
                cursor.close()

                log_structured("INFO", "PUT /postulaciones/{id}/contratacion - exito", request_id, postulacion_id=postulacion_id)
                return make_response(200, {"mensaje": "Postulación actualizada"}, request_id)

            except Exception as e:
                conn.rollback()
                raise e

    except Exception as e:
        log_structured(
            "ERROR",
            "PUT /postulaciones/{id}/contratacion - error",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)


# ============================================================================
# LAMBDA HANDLER & ROUTER
# ============================================================================

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler - routes requests to appropriate handlers.

    Args:
        event: Lambda event object
        context: Lambda context object

    Returns:
        Lambda response dict
    """
    request_id = str(uuid.uuid4())
    method = event.get("httpMethod", "")
    path = event.get("path", "")
    query_params = event.get("queryStringParameters") or {}
    body = parse_body(event)

    log_structured(
        "INFO",
        f"{method} {path} - recibido",
        request_id,
        method=method,
        path=path,
        query_params=query_params
    )

    try:
        # GET /campanias/activas
        if method == "GET" and path == "/campanias/activas":
            return handle_get_campanias_activas(_pool, request_id)

        # GET /puestos/activos
        elif method == "GET" and path == "/puestos/activos":
            return handle_get_puestos_activos(_pool, request_id)

        # GET /requerimientos
        elif method == "GET" and path == "/requerimientos":
            return handle_get_requerimientos(_pool, query_params, request_id)

        # POST /requerimientos
        elif method == "POST" and path == "/requerimientos":
            return handle_post_requerimientos(_pool, body, request_id)

        # GET /requerimientos/{codigo}
        elif method == "GET" and path.startswith("/requerimientos/") and path.count("/") == 2:
            codigo = path.split("/")[-1]
            return handle_get_requerimiento_by_codigo(_pool, codigo, request_id)

        # GET /requerimientos/{codigo}/postulaciones
        elif method == "GET" and path.endswith("/postulaciones"):
            codigo = path.split("/")[-2]
            return handle_get_requerimiento_postulaciones(_pool, codigo, request_id)

        # POST /postulaciones
        elif method == "POST" and path == "/postulaciones":
            return handle_post_postulaciones(_pool, body, request_id)

        # PUT /postulaciones/{id}/requisito
        elif method == "PUT" and path.endswith("/requisito"):
            postulacion_id = int(path.split("/")[-2])
            return handle_put_postulacion_requisito(_pool, postulacion_id, body, request_id)

        # PUT /postulaciones/{id}/entrevista
        elif method == "PUT" and path.endswith("/entrevista"):
            postulacion_id = int(path.split("/")[-2])
            return handle_put_postulacion_entrevista(_pool, postulacion_id, body, request_id)

        # PUT /postulaciones/{id}/contratacion
        elif method == "PUT" and path.endswith("/contratacion"):
            postulacion_id = int(path.split("/")[-2])
            return handle_put_postulacion_contratacion(_pool, postulacion_id, body, request_id)

        # 404
        else:
            log_structured("WARN", "Endpoint no encontrado", request_id, method=method, path=path)
            return make_response(404, {"error": "Endpoint no encontrado"}, request_id)

    except Exception as e:
        log_structured(
            "ERROR",
            "Error no capturado en router",
            request_id,
            error=str(e),
            traceback=traceback.format_exc()
        )
        return make_response(500, {"error": "Error interno del servidor"}, request_id)

    finally:
        log_structured("INFO", f"{method} {path} - finalizado", request_id)
