"""
Pytest test suite for lambda_function.py
Tests all endpoints with happy path, validation, and error scenarios.
"""

import pytest
import json
from unittest.mock import MagicMock, Mock, patch, call
from datetime import datetime
from pydantic import ValidationError
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lambda_function import (
    handle_get_campanias_activas,
    handle_get_puestos_activos,
    handle_get_requerimientos,
    handle_post_requerimientos,
    handle_get_requerimiento_by_codigo,
    handle_get_requerimiento_postulaciones,
    handle_post_postulaciones,
    handle_put_postulacion_requisito,
    handle_put_postulacion_entrevista,
    handle_put_postulacion_contratacion,
    lambda_handler,
    check_foreign_key,
    check_duplicate,
    convert_types,
    Postulante,
    RequerimientoCreate,
    PostulacionCreate,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_cursor():
    """Mock pyodbc cursor."""
    cursor = MagicMock()
    cursor.description = [
        ("id_campania",),
        ("nombre",),
        ("descripcion",),
        ("fecha_inicio",),
        ("fecha_fin",),
    ]
    return cursor


@pytest.fixture
def mock_connection(mock_cursor):
    """Mock pyodbc connection."""
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    conn.begin = MagicMock()
    conn.commit = MagicMock()
    conn.rollback = MagicMock()
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    return conn


@pytest.fixture
def mock_pool(mock_connection):
    """Mock ConnectionPool."""
    pool = MagicMock()
    pool.get_connection.return_value.__enter__ = MagicMock(return_value=mock_connection)
    pool.get_connection.return_value.__exit__ = MagicMock(return_value=False)
    return pool


@pytest.fixture
def sample_campanias():
    """Sample campanias data."""
    return [
        (1, "Campaña Verano 2026", "Contratación estival", "2026-01-01T00:00:00", "2026-03-31T00:00:00"),
        (2, "Campaña Invierno 2026", "Contratación invernal", "2026-06-01T00:00:00", "2026-08-31T00:00:00"),
    ]


@pytest.fixture
def sample_puestos():
    """Sample puestos data."""
    return [
        (1, "Agente de Ventas", "Venta telefónica"),
        (2, "Supervisor", "Supervisión de equipo"),
    ]


@pytest.fixture
def sample_requerimientos():
    """Sample requerimientos data."""
    return [
        (
            1,
            "REQ-001",
            1,
            1,
            10,
            "Requerimiento de agentes de ventas",
            "nueva",
            "2026-05-01T10:00:00",
        ),
        (
            2,
            "REQ-002",
            1,
            2,
            5,
            "Requerimiento de supervisores",
            "nueva",
            "2026-05-02T10:00:00",
        ),
    ]


@pytest.fixture
def sample_postulacion():
    """Sample postulacion data."""
    return {
        "id_postulacion": 1,
        "id_requerimiento": 1,
        "id_postulante": 1,
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "juan@example.com",
        "requisito_revisado": False,
        "apto": False,
        "entrevista_aprobada": False,
        "fecha_entrevista": None,
        "contratar": False,
        "estado": "nueva",
        "fecha_postulacion": "2026-05-18T10:00:00",
    }


@pytest.fixture
def request_id():
    """Sample request ID."""
    return "test-req-123"


# ============================================================================
# GET /campanias/activas TESTS
# ============================================================================

def test_get_campanias_activas_success(mock_pool, sample_campanias, request_id):
    """Test GET /campanias/activas - happy path returns list."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id_campania",), ("nombre",), ("descripcion",), ("fecha_inicio",), ("fecha_fin",)]
    mock_cursor.fetchall.return_value = sample_campanias
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_campanias_activas(mock_pool, request_id)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "campanias" in body
    assert len(body["campanias"]) == 2
    assert body["campanias"][0]["nombre"] == "Campaña Verano 2026"


def test_get_campanias_activas_empty(mock_pool, request_id):
    """Test GET /campanias/activas - no active campaigns returns empty list."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id_campania",), ("nombre",), ("descripcion",), ("fecha_inicio",), ("fecha_fin",)]
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_campanias_activas(mock_pool, request_id)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["campanias"] == []


def test_get_campanias_activas_db_error(mock_pool, request_id):
    """Test GET /campanias/activas - database error returns 500."""
    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = Exception("DB connection error")

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_campanias_activas(mock_pool, request_id)

    assert result["statusCode"] == 500
    body = json.loads(result["body"])
    assert "error" in body
    assert body["error"] == "Error interno del servidor"


# ============================================================================
# GET /puestos/activos TESTS
# ============================================================================

def test_get_puestos_activos_success(mock_pool, sample_puestos, request_id):
    """Test GET /puestos/activos - happy path returns list."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id_puesto",), ("nombre",), ("descripcion",)]
    mock_cursor.fetchall.return_value = sample_puestos
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_puestos_activos(mock_pool, request_id)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "puestos" in body
    assert len(body["puestos"]) == 2


def test_get_puestos_activos_empty(mock_pool, request_id):
    """Test GET /puestos/activos - no puestos returns empty list."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id_puesto",), ("nombre",), ("descripcion",)]
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_puestos_activos(mock_pool, request_id)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["puestos"] == []


# ============================================================================
# GET /requerimientos TESTS
# ============================================================================

def test_get_requerimientos_all(mock_pool, sample_requerimientos, request_id):
    """Test GET /requerimientos - returns all requirements."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ("id_requerimiento",), ("codigo",), ("id_campania",), ("id_puesto",),
        ("cantidad_vacantes",), ("descripcion",), ("estado",), ("fecha_creacion",)
    ]
    mock_cursor.fetchall.return_value = sample_requerimientos
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_requerimientos(mock_pool, {}, request_id)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "requerimientos" in body
    assert len(body["requerimientos"]) == 2


def test_get_requerimientos_filter_by_estado(mock_pool, request_id):
    """Test GET /requerimientos - filters by estado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ("id_requerimiento",), ("codigo",), ("id_campania",), ("id_puesto",),
        ("cantidad_vacantes",), ("descripcion",), ("estado",), ("fecha_creacion",)
    ]
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_requerimientos(mock_pool, {"estado": "nueva"}, request_id)

    assert result["statusCode"] == 200
    mock_conn.cursor.return_value.execute.assert_called_once()


def test_get_requerimientos_invalid_campania_id(mock_pool, request_id):
    """Test GET /requerimientos - invalid campaniaId returns 400."""
    result = handle_get_requerimientos(mock_pool, {"campaniaId": "invalid"}, request_id)

    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "error" in body


# ============================================================================
# POST /requerimientos TESTS
# ============================================================================

def test_post_requerimientos_success(mock_pool, request_id):
    """Test POST /requerimientos - happy path creates requirement."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # First call: check foreign key campania
    # Second call: check foreign key puesto
    # Third call: check duplicate codigo
    # Fourth call: insert requerimiento
    mock_cursor.fetchone.side_effect = [Mock(), Mock(), None, None]
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    # Mock check_foreign_key and check_duplicate
    with patch("lambda_function.check_foreign_key") as mock_fk:
        with patch("lambda_function.check_duplicate") as mock_dup:
            mock_fk.return_value = True
            mock_dup.return_value = False

            payload = {
                "codigo": "req-001",
                "campania_id": 1,
                "puesto_id": 1,
                "cantidad_vacantes": 10,
                "descripcion": "Test requirement",
            }

            result = handle_post_requerimientos(mock_pool, payload, request_id)

    assert result["statusCode"] == 201
    body = json.loads(result["body"])
    assert "mensaje" in body
    assert body["codigo"] == "REQ-001"  # Should be uppercase


def test_post_requerimientos_validation_missing_codigo(mock_pool, request_id):
    """Test POST /requerimientos - missing codigo returns 422."""
    payload = {
        "campania_id": 1,
        "puesto_id": 1,
        "cantidad_vacantes": 10,
        "descripcion": "Test",
    }

    result = handle_post_requerimientos(mock_pool, payload, request_id)

    assert result["statusCode"] == 422
    body = json.loads(result["body"])
    assert "error" in body


def test_post_requerimientos_validation_invalid_cantidad(mock_pool, request_id):
    """Test POST /requerimientos - invalid cantidad_vacantes returns 422."""
    payload = {
        "codigo": "REQ-001",
        "campania_id": 1,
        "puesto_id": 1,
        "cantidad_vacantes": 2000,  # Exceeds max
        "descripcion": "Test",
    }

    result = handle_post_requerimientos(mock_pool, payload, request_id)

    assert result["statusCode"] == 422


def test_post_requerimientos_duplicate_codigo(mock_pool, request_id):
    """Test POST /requerimientos - duplicate codigo returns 409."""
    with patch("lambda_function.check_foreign_key") as mock_fk:
        with patch("lambda_function.check_duplicate") as mock_dup:
            mock_fk.return_value = True
            mock_dup.return_value = True  # Duplicate exists

            payload = {
                "codigo": "REQ-001",
                "campania_id": 1,
                "puesto_id": 1,
                "cantidad_vacantes": 10,
                "descripcion": "Test",
            }

            result = handle_post_requerimientos(mock_pool, payload, request_id)

    assert result["statusCode"] == 409
    body = json.loads(result["body"])
    assert "ya existe" in body["error"].lower()


def test_post_requerimientos_foreign_key_campania_not_found(mock_pool, request_id):
    """Test POST /requerimientos - campania not found returns 404."""
    with patch("lambda_function.check_foreign_key") as mock_fk:
        with patch("lambda_function.check_duplicate") as mock_dup:
            mock_fk.return_value = False  # Campania not found
            mock_dup.return_value = False

            payload = {
                "codigo": "REQ-001",
                "campania_id": 999,
                "puesto_id": 1,
                "cantidad_vacantes": 10,
                "descripcion": "Test",
            }

            result = handle_post_requerimientos(mock_pool, payload, request_id)

    assert result["statusCode"] == 404
    body = json.loads(result["body"])
    assert "Campaña" in body["error"]


def test_post_requerimientos_foreign_key_puesto_not_found(mock_pool, request_id):
    """Test POST /requerimientos - puesto not found returns 404."""
    with patch("lambda_function.check_foreign_key") as mock_fk:
        with patch("lambda_function.check_duplicate") as mock_dup:
            # First call succeeds (campania), second fails (puesto)
            mock_fk.side_effect = [True, False]
            mock_dup.return_value = False

            payload = {
                "codigo": "REQ-001",
                "campania_id": 1,
                "puesto_id": 999,
                "cantidad_vacantes": 10,
                "descripcion": "Test",
            }

            result = handle_post_requerimientos(mock_pool, payload, request_id)

    assert result["statusCode"] == 404
    body = json.loads(result["body"])
    assert "Puesto" in body["error"]


# ============================================================================
# GET /requerimientos/{codigo} TESTS
# ============================================================================

def test_get_requerimiento_by_codigo_success(mock_pool, sample_requerimientos, request_id):
    """Test GET /requerimientos/{codigo} - returns requirement."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [
        ("id_requerimiento",), ("codigo",), ("id_campania",), ("id_puesto",),
        ("cantidad_vacantes",), ("descripcion",), ("estado",), ("fecha_creacion",)
    ]
    mock_cursor.fetchone.return_value = sample_requerimientos[0]
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_requerimiento_by_codigo(mock_pool, "REQ-001", request_id)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "requerimiento" in body
    assert body["requerimiento"]["codigo"] == "REQ-001"


def test_get_requerimiento_by_codigo_not_found(mock_pool, request_id):
    """Test GET /requerimientos/{codigo} - not found returns 404."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id_requerimiento",)]
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_requerimiento_by_codigo(mock_pool, "INVALID", request_id)

    assert result["statusCode"] == 404


# ============================================================================
# GET /requerimientos/{codigo}/postulaciones TESTS
# ============================================================================

def test_get_requerimiento_postulaciones_success(mock_pool, sample_postulacion, request_id):
    """Test GET /requerimientos/{codigo}/postulaciones - returns postulaciones."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # First execute: get requerimiento_id
    mock_cursor.fetchone.side_effect = [(1,), (sample_postulacion,)]
    mock_cursor.description = [
        ("id_postulacion",), ("id_requerimiento",), ("id_postulante",),
        ("nombre",), ("apellido",), ("dni",), ("email",),
        ("requisito_revisado",), ("apto",), ("entrevista_aprobada",),
        ("fecha_entrevista",), ("contratar",), ("estado",), ("fecha_postulacion",)
    ]

    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = handle_get_requerimiento_postulaciones(mock_pool, "REQ-001", request_id)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "postulaciones" in body


# ============================================================================
# POST /postulaciones TESTS
# ============================================================================

def test_post_postulaciones_success_new_postulante(mock_pool, request_id):
    """Test POST /postulaciones - creates postulacion with new postulante."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Mocks for: check FK, check postulante exists, insert postulante, check duplicate
    mock_cursor.fetchone.side_effect = [None, None, 1]  # postulante doesn't exist, then gets id
    mock_cursor.execute.return_value = mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    with patch("lambda_function.check_foreign_key") as mock_fk:
        mock_fk.return_value = True

        payload = {
            "requerimiento_id": 1,
            "postulante": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "dni": "12345678",
                "email": "juan@example.com",
                "telefono": "987654321",
                "medio_preferido": "email",
                "cv_url": "https://example.com/cv.pdf",
            },
        }

        result = handle_post_postulaciones(mock_pool, payload, request_id)

    assert result["statusCode"] == 201
    body = json.loads(result["body"])
    assert "mensaje" in body


def test_post_postulaciones_validation_invalid_dni(mock_pool, request_id):
    """Test POST /postulaciones - invalid DNI returns 422."""
    payload = {
        "requerimiento_id": 1,
        "postulante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "dni": "1234567",  # Invalid: only 7 digits
            "email": "juan@example.com",
            "telefono": "987654321",
            "medio_preferido": "email",
        },
    }

    result = handle_post_postulaciones(mock_pool, payload, request_id)

    assert result["statusCode"] == 422


def test_post_postulaciones_validation_invalid_telefono(mock_pool, request_id):
    """Test POST /postulaciones - invalid telefono returns 422."""
    payload = {
        "requerimiento_id": 1,
        "postulante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "dni": "12345678",
            "email": "juan@example.com",
            "telefono": "812345678",  # Invalid: doesn't start with 9
            "medio_preferido": "email",
        },
    }

    result = handle_post_postulaciones(mock_pool, payload, request_id)

    assert result["statusCode"] == 422


def test_post_postulaciones_validation_invalid_email(mock_pool, request_id):
    """Test POST /postulaciones - invalid email returns 422."""
    payload = {
        "requerimiento_id": 1,
        "postulante": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "dni": "12345678",
            "email": "not-an-email",
            "telefono": "987654321",
            "medio_preferido": "email",
        },
    }

    result = handle_post_postulaciones(mock_pool, payload, request_id)

    assert result["statusCode"] == 422


def test_post_postulaciones_duplicate_application(mock_pool, request_id):
    """Test POST /postulaciones - duplicate active application returns 409."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Check FK succeeds, postulante exists, check duplicate succeeds
    mock_cursor.fetchone.side_effect = [(1,), (1,)]  # postulante exists, duplicate exists
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    with patch("lambda_function.check_foreign_key") as mock_fk:
        mock_fk.return_value = True

        payload = {
            "requerimiento_id": 1,
            "postulante": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "dni": "12345678",
                "email": "juan@example.com",
                "telefono": "987654321",
                "medio_preferido": "email",
            },
        }

        result = handle_post_postulaciones(mock_pool, payload, request_id)

    assert result["statusCode"] == 409
    body = json.loads(result["body"])
    assert "ya existe una postulación" in body["error"].lower()


# ============================================================================
# PUT /postulaciones/{id}/requisito TESTS
# ============================================================================

def test_put_postulacion_requisito_apto_true(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/requisito - apto=true moves to entrevista."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("nueva",)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {"apto": True}
    result = handle_put_postulacion_requisito(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "mensaje" in body


def test_put_postulacion_requisito_apto_false(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/requisito - apto=false moves to rechazada."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("nueva",)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {"apto": False}
    result = handle_put_postulacion_requisito(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 200


def test_put_postulacion_requisito_not_found(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/requisito - not found returns 404."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {"apto": True}
    result = handle_put_postulacion_requisito(mock_pool, 999, payload, request_id)

    assert result["statusCode"] == 404


def test_put_postulacion_requisito_invalid_state(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/requisito - wrong state returns 409."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("entrevista",)  # Wrong state
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {"apto": True}
    result = handle_put_postulacion_requisito(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 409
    body = json.loads(result["body"])
    assert "No se puede actualizar" in body["error"]


# ============================================================================
# PUT /postulaciones/{id}/entrevista TESTS
# ============================================================================

def test_put_postulacion_entrevista_approved(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/entrevista - approved moves to contratacion."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("entrevista",)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {
        "entrevista_aprobada": True,
        "fecha_entrevista": "2026-05-20T10:00:00",
        "notas_entrevista": "Candidato muy potencial",
    }
    result = handle_put_postulacion_entrevista(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 200


def test_put_postulacion_entrevista_rejected(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/entrevista - rejected moves to rechazada."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("entrevista",)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {
        "entrevista_aprobada": False,
        "notas_entrevista": "No cumple requisitos",
    }
    result = handle_put_postulacion_entrevista(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 200


def test_put_postulacion_entrevista_invalid_state(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/entrevista - wrong state returns 409."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("nueva",)  # Wrong state
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {
        "entrevista_aprobada": True,
    }
    result = handle_put_postulacion_entrevista(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 409


# ============================================================================
# PUT /postulaciones/{id}/contratacion TESTS
# ============================================================================

def test_put_postulacion_contratacion_hire(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/contratacion - contratar=true moves to contratada."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("contratacion",)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {
        "contratar": True,
        "fecha_inicio_capacitacion": "2026-06-01",
        "notas_contratacion": "Inicio inmediato",
    }
    result = handle_put_postulacion_contratacion(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 200


def test_put_postulacion_contratacion_reject(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/contratacion - contratar=false moves to rechazada."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("contratacion",)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {
        "contratar": False,
        "notas_contratacion": "Cambio de decisión",
    }
    result = handle_put_postulacion_contratacion(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 200


def test_put_postulacion_contratacion_invalid_state(mock_pool, request_id):
    """Test PUT /postulaciones/{id}/contratacion - wrong state returns 409."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("entrevista",)  # Wrong state
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    payload = {"contratar": True}
    result = handle_put_postulacion_contratacion(mock_pool, 1, payload, request_id)

    assert result["statusCode"] == 409


# ============================================================================
# LAMBDA HANDLER ROUTER TESTS
# ============================================================================

def test_lambda_handler_get_campanias_activas(mock_pool, request_id):
    """Test lambda_handler routes GET /campanias/activas correctly."""
    event = {
        "httpMethod": "GET",
        "path": "/campanias/activas",
        "queryStringParameters": None,
        "body": None,
        "requestContext": {"requestId": request_id},
    }

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id_campania",), ("nombre",), ("descripcion",), ("fecha_inicio",), ("fecha_fin",)]
    mock_cursor.fetchall.return_value = [(1, "Test", "", "", "")]
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    with patch("lambda_function._pool", mock_pool):
        result = lambda_handler(event, None)

    assert result["statusCode"] == 200


def test_lambda_handler_endpoint_not_found():
    """Test lambda_handler returns 404 for unknown endpoint."""
    event = {
        "httpMethod": "GET",
        "path": "/unknown/endpoint",
        "queryStringParameters": None,
        "body": None,
    }

    with patch("lambda_function._pool"):
        result = lambda_handler(event, None)

    assert result["statusCode"] == 404
    body = json.loads(result["body"])
    assert "no encontrado" in body["error"].lower()


def test_lambda_handler_unhandled_exception():
    """Test lambda_handler returns 500 on unhandled exception."""
    event = {
        "httpMethod": "GET",
        "path": "/campanias/activas",
        "queryStringParameters": None,
        "body": None,
    }

    mock_pool = MagicMock()
    mock_pool.get_connection.side_effect = Exception("Unexpected error")

    with patch("lambda_function._pool", mock_pool):
        result = lambda_handler(event, None)

    assert result["statusCode"] == 500


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================

def test_convert_types_datetime():
    """Test convert_types converts datetime to ISO format."""
    dt = datetime(2026, 5, 18, 10, 30, 0)
    row = (1, "test", dt)
    cols = ["id", "name", "fecha"]

    result = convert_types(row, cols)

    assert result["fecha"] == "2026-05-18T10:30:00"


def test_convert_types_none():
    """Test convert_types handles None values."""
    row = (1, "test", None)
    cols = ["id", "name", "optional"]

    result = convert_types(row, cols)

    assert result["optional"] is None


def test_check_foreign_key_exists(mock_pool):
    """Test check_foreign_key returns True when FK exists."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = check_foreign_key(mock_pool, "campanias", "id_campania", 1, "test")

    assert result is True


def test_check_foreign_key_not_exists(mock_pool):
    """Test check_foreign_key returns False when FK doesn't exist."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = check_foreign_key(mock_pool, "campanias", "id_campania", 999, "test")

    assert result is False


def test_check_duplicate_exists(mock_pool):
    """Test check_duplicate returns True when duplicate exists."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = check_duplicate(mock_pool, "requerimientos", "codigo", "REQ-001", "test")

    assert result is True


def test_check_duplicate_not_exists(mock_pool):
    """Test check_duplicate returns False when duplicate doesn't exist."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    result = check_duplicate(mock_pool, "requerimientos", "codigo", "NEW-CODE", "test")

    assert result is False


# ============================================================================
# PYDANTIC MODEL TESTS
# ============================================================================

def test_postulante_valid():
    """Test Postulante model with valid data."""
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "juan@example.com",
        "telefono": "987654321",
        "medio_preferido": "email",
        "cv_url": "https://example.com/cv.pdf",
    }

    postulante = Postulante(**data)

    assert postulante.nombre == "Juan"
    assert postulante.dni == "12345678"
    assert postulante.telefono == "987654321"


def test_postulante_invalid_dni():
    """Test Postulante rejects invalid DNI."""
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "1234567",  # Only 7 digits
        "email": "juan@example.com",
        "telefono": "987654321",
        "medio_preferido": "email",
    }

    with pytest.raises(ValidationError):
        Postulante(**data)


def test_postulante_invalid_telefono():
    """Test Postulante rejects invalid telefono."""
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "juan@example.com",
        "telefono": "887654321",  # Doesn't start with 9
        "medio_preferido": "email",
    }

    with pytest.raises(ValidationError):
        Postulante(**data)


def test_requerimiento_create_uppercase_codigo():
    """Test RequerimientoCreate converts codigo to uppercase."""
    data = {
        "codigo": "req-001",
        "campania_id": 1,
        "puesto_id": 1,
        "cantidad_vacantes": 10,
        "descripcion": "Test requirement",
    }

    req = RequerimientoCreate(**data)

    assert req.codigo == "REQ-001"


def test_requerimiento_create_invalid_cantidad():
    """Test RequerimientoCreate rejects invalid cantidad_vacantes."""
    data = {
        "codigo": "REQ-001",
        "campania_id": 1,
        "puesto_id": 1,
        "cantidad_vacantes": 0,  # Below minimum
        "descripcion": "Test",
    }

    with pytest.raises(ValidationError):
        RequerimientoCreate(**data)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_postulacion_workflow(mock_pool, request_id):
    """Test complete workflow: create postulacion -> requisito -> entrevista -> contratacion."""
    # This is a simplified integration test demonstrating state transitions

    # Step 1: Create postulacion
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [None, None, 1, None]
    mock_conn.cursor.return_value = mock_cursor
    mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

    with patch("lambda_function.check_foreign_key") as mock_fk:
        mock_fk.return_value = True

        payload = {
            "requerimiento_id": 1,
            "postulante": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "dni": "12345678",
                "email": "juan@example.com",
                "telefono": "987654321",
                "medio_preferido": "email",
            },
        }

        result = handle_post_postulaciones(mock_pool, payload, request_id)

    assert result["statusCode"] == 201

    # Step 2: Update requisito
    mock_cursor.fetchone.return_value = ("nueva",)
    result = handle_put_postulacion_requisito(mock_pool, 1, {"apto": True}, request_id)
    assert result["statusCode"] == 200

    # Step 3: Update entrevista
    mock_cursor.fetchone.return_value = ("entrevista",)
    result = handle_put_postulacion_entrevista(
        mock_pool,
        1,
        {"entrevista_aprobada": True, "fecha_entrevista": "2026-05-20T10:00:00"},
        request_id
    )
    assert result["statusCode"] == 200

    # Step 4: Update contratacion
    mock_cursor.fetchone.return_value = ("contratacion",)
    result = handle_put_postulacion_contratacion(
        mock_pool,
        1,
        {"contratar": True, "fecha_inicio_capacitacion": "2026-06-01"},
        request_id
    )
    assert result["statusCode"] == 200
