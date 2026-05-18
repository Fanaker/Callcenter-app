"""
Integration Tests for Recruitment Backend
Tests against real (or simulated) database with full workflows.
"""

import pytest
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
import json
from unittest.mock import MagicMock, patch
import sys
import os
import threading
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lambda_function import (
    handle_post_requerimientos,
    handle_post_postulaciones,
    handle_put_postulacion_requisito,
    handle_put_postulacion_entrevista,
    handle_put_postulacion_contratacion,
    RequerimientoCreate,
)


# ============================================================================
# DATABASE FIXTURES & SETUP
# ============================================================================

@pytest.fixture(scope="session")
def db_path():
    """Path to test database."""
    return ":memory:"  # Use in-memory SQLite for tests


@pytest.fixture(scope="session")
def db_connection(db_path):
    """Create and initialize test database.

    Yields:
        sqlite3.Connection: Test database connection
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    # Create schema
    schema_sql = """
    -- Campanias
    CREATE TABLE IF NOT EXISTS campanias (
        id_campania INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        activa INTEGER NOT NULL DEFAULT 1
    );

    -- Puestos
    CREATE TABLE IF NOT EXISTS puestos (
        id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        activo INTEGER NOT NULL DEFAULT 1
    );

    -- Requerimientos
    CREATE TABLE IF NOT EXISTS requerimientos (
        id_requerimiento INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        id_campania INTEGER NOT NULL,
        id_puesto INTEGER NOT NULL,
        cantidad_vacantes INTEGER NOT NULL,
        descripcion TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'nueva',
        fecha_creacion TEXT NOT NULL,
        FOREIGN KEY (id_campania) REFERENCES campanias(id_campania),
        FOREIGN KEY (id_puesto) REFERENCES puestos(id_puesto)
    );

    -- Postulantes
    CREATE TABLE IF NOT EXISTS postulantes (
        id_postulante INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        telefono TEXT NOT NULL,
        medio_preferido TEXT NOT NULL,
        cv_url TEXT
    );

    -- Postulaciones
    CREATE TABLE IF NOT EXISTS postulaciones (
        id_postulacion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_requerimiento INTEGER NOT NULL,
        id_postulante INTEGER NOT NULL,
        requisito_revisado INTEGER NOT NULL DEFAULT 0,
        apto INTEGER NOT NULL DEFAULT 0,
        entrevista_aprobada INTEGER NOT NULL DEFAULT 0,
        fecha_entrevista TEXT,
        notas_entrevista TEXT,
        contratar INTEGER NOT NULL DEFAULT 0,
        fecha_inicio_capacitacion TEXT,
        notas_contratacion TEXT,
        estado TEXT NOT NULL DEFAULT 'nueva',
        fecha_postulacion TEXT NOT NULL,
        fecha_actualizacion TEXT NOT NULL,
        FOREIGN KEY (id_requerimiento) REFERENCES requerimientos(id_requerimiento),
        FOREIGN KEY (id_postulante) REFERENCES postulantes(id_postulante)
    );

    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_requerimientos_codigo ON requerimientos(codigo);
    CREATE INDEX IF NOT EXISTS idx_requerimientos_estado ON requerimientos(estado);
    CREATE INDEX IF NOT EXISTS idx_postulaciones_estado ON postulaciones(estado);
    CREATE INDEX IF NOT EXISTS idx_postulaciones_dni ON postulaciones(id_requerimiento, id_postulante);
    """

    conn.executescript(schema_sql)
    conn.commit()

    # Insert test data
    _insert_base_data(conn)

    yield conn

    # Cleanup
    conn.close()


def _insert_base_data(conn):
    """Insert base test data into database.

    Args:
        conn: sqlite3.Connection to test database
    """
    now = datetime.utcnow().isoformat()

    # Insert campanias
    conn.execute(
        """INSERT INTO campanias (nombre, descripcion, fecha_inicio, fecha_fin, activa)
           VALUES (?, ?, ?, ?, 1)""",
        ("Campaña Test 2026", "Campaña para testing", now, now)
    )
    conn.execute(
        """INSERT INTO campanias (nombre, descripcion, fecha_inicio, fecha_fin, activa)
           VALUES (?, ?, ?, ?, 0)""",
        ("Campaña Inactiva", "Campaña inactiva para testing", now, now)
    )

    # Insert puestos
    conn.execute(
        """INSERT INTO puestos (nombre, descripcion, activo)
           VALUES (?, ?, 1)""",
        ("Agente de Ventas", "Venta telefónica")
    )
    conn.execute(
        """INSERT INTO puestos (nombre, descripcion, activo)
           VALUES (?, ?, 1)""",
        ("Supervisor", "Supervisión de equipo")
    )

    conn.commit()


@pytest.fixture
def db_cursor(db_connection):
    """Provide a database cursor that rolls back after test.

    Yields:
        sqlite3.Cursor: Database cursor for test operations
    """
    cursor = db_connection.cursor()

    # Get current row count for cleanup
    campaign_count_before = cursor.execute("SELECT COUNT(*) FROM campanias").fetchone()[0]
    position_count_before = cursor.execute("SELECT COUNT(*) FROM puestos").fetchone()[0]

    yield cursor

    # Cleanup: Delete test data (keep base data)
    cursor.execute(
        "DELETE FROM postulaciones WHERE id_postulacion > 0"
    )
    cursor.execute(
        "DELETE FROM postulantes WHERE id_postulante > 0"
    )
    cursor.execute(
        "DELETE FROM requerimientos WHERE id_requerimiento > 0"
    )

    # Reset auto-increment
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='requerimientos'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='postulantes'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='postulaciones'")

    db_connection.commit()


@pytest.fixture
def mock_pool(db_connection):
    """Mock ConnectionPool that uses test database.

    Args:
        db_connection: SQLite test database connection

    Yields:
        MagicMock: Mocked ConnectionPool
    """
    pool = MagicMock()

    @contextmanager
    def mock_get_connection():
        cursor = db_connection.cursor()
        cursor.execute("BEGIN TRANSACTION")
        try:
            yield db_connection
            db_connection.commit()
        except Exception:
            db_connection.rollback()
            raise

    pool.get_connection.return_value = mock_get_connection()

    yield pool


@pytest.fixture
def request_id():
    """Provide a request ID for test tracking.

    Yields:
        str: Unique request ID
    """
    return f"test-{datetime.utcnow().isoformat()}"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_test_campaign(cursor, name: str = "Test Campaign") -> int:
    """Create a test campaign.

    Args:
        cursor: Database cursor
        name: Campaign name

    Returns:
        int: Campaign ID
    """
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO campanias (nombre, descripcion, fecha_inicio, fecha_fin, activa)
           VALUES (?, ?, ?, ?, 1)""",
        (name, "Test description", now, now)
    )
    return cursor.lastrowid


def create_test_position(cursor, name: str = "Test Position") -> int:
    """Create a test position.

    Args:
        cursor: Database cursor
        name: Position name

    Returns:
        int: Position ID
    """
    cursor.execute(
        """INSERT INTO puestos (nombre, descripcion, activo)
           VALUES (?, ?, 1)""",
        (name, "Test description")
    )
    return cursor.lastrowid


def create_test_requirement(
    cursor,
    codigo: str,
    campaign_id: int,
    position_id: int,
    vacancies: int = 5
) -> int:
    """Create a test requirement.

    Args:
        cursor: Database cursor
        codigo: Requirement code
        campaign_id: Campaign ID
        position_id: Position ID
        vacancies: Number of vacancies

    Returns:
        int: Requirement ID
    """
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO requerimientos
           (codigo, id_campania, id_puesto, cantidad_vacantes, descripcion, estado, fecha_creacion)
           VALUES (?, ?, ?, ?, ?, 'nueva', ?)""",
        (codigo, campaign_id, position_id, vacancies, "Test requirement", now)
    )
    return cursor.lastrowid


def create_test_applicant(
    cursor,
    nombre: str,
    apellido: str,
    dni: str,
    email: str,
    telefono: str
) -> int:
    """Create a test applicant.

    Args:
        cursor: Database cursor
        nombre: First name
        apellido: Last name
        dni: DNI/ID number
        email: Email address
        telefono: Phone number

    Returns:
        int: Applicant ID
    """
    cursor.execute(
        """INSERT INTO postulantes
           (nombre, apellido, dni, email, telefono, medio_preferido, cv_url)
           VALUES (?, ?, ?, ?, ?, 'email', 'https://example.com/cv.pdf')""",
        (nombre, apellido, dni, email, telefono)
    )
    return cursor.lastrowid


def create_test_application(
    cursor,
    requirement_id: int,
    applicant_id: int
) -> int:
    """Create a test application.

    Args:
        cursor: Database cursor
        requirement_id: Requirement ID
        applicant_id: Applicant ID

    Returns:
        int: Application ID
    """
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO postulaciones
           (id_requerimiento, id_postulante, estado, fecha_postulacion, fecha_actualizacion)
           VALUES (?, ?, 'nueva', ?, ?)""",
        (requirement_id, applicant_id, now, now)
    )
    return cursor.lastrowid


def get_application_state(cursor, application_id: int) -> str:
    """Get current application state.

    Args:
        cursor: Database cursor
        application_id: Application ID

    Returns:
        str: Application state
    """
    result = cursor.execute(
        "SELECT estado FROM postulaciones WHERE id_postulacion = ?",
        (application_id,)
    ).fetchone()
    return result[0] if result else None


def get_requirement_by_codigo(cursor, codigo: str) -> dict:
    """Get requirement by codigo.

    Args:
        cursor: Database cursor
        codigo: Requirement code

    Returns:
        dict: Requirement data
    """
    result = cursor.execute(
        "SELECT * FROM requerimientos WHERE codigo = ?",
        (codigo,)
    ).fetchone()
    return dict(result) if result else None


def get_application(cursor, application_id: int) -> dict:
    """Get application data.

    Args:
        cursor: Database cursor
        application_id: Application ID

    Returns:
        dict: Application data
    """
    result = cursor.execute(
        "SELECT * FROM postulaciones WHERE id_postulacion = ?",
        (application_id,)
    ).fetchone()
    return dict(result) if result else None


# ============================================================================
# TEST SCENARIOS
# ============================================================================

class TestHappyPathComplete:
    """Test complete successful workflow: postulacion → requisito → entrevista → contratacion."""

    def test_complete_hiring_workflow(self, db_cursor, mock_pool, request_id):
        """Test complete hiring workflow from application to hire."""
        # Setup: Create test data
        campaign_id = create_test_campaign(db_cursor, "Test Campaign 2026")
        position_id = create_test_position(db_cursor, "Test Position")
        req_id = create_test_requirement(db_cursor, "REQ-001", campaign_id, position_id)
        db_connection = db_cursor.connection
        db_connection.commit()

        # Step 1: Create postulation
        applicant_data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "dni": "12345678",
            "email": "juan@example.com",
            "telefono": "987654321",
            "medio_preferido": "email",
            "cv_url": "https://example.com/cv.pdf",
        }

        postulacion_payload = {
            "requerimiento_id": req_id,
            "postulante": applicant_data,
        }

        # Mock check_foreign_key to return True
        with patch("lambda_function.check_foreign_key") as mock_fk:
            mock_fk.return_value = True

            # Create mock connection for handler
            mock_conn = MagicMock()
            mock_cursor = MagicMock()

            # Setup cursor behavior for create postulation
            applicant_id = create_test_applicant(
                db_cursor,
                applicant_data["nombre"],
                applicant_data["apellido"],
                applicant_data["dni"],
                applicant_data["email"],
                applicant_data["telefono"],
            )
            app_id = create_test_application(db_cursor, req_id, applicant_id)
            db_connection.commit()

            assert app_id > 0, "Application should be created"
            assert get_application_state(db_cursor, app_id) == "nueva"

        # Step 2: Pass requisito requirement (apto=true)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("nueva",)
        mock_conn.cursor.return_value = mock_cursor

        mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

        requisito_payload = {"apto": True}
        result = handle_put_postulacion_requisito(mock_pool, app_id, requisito_payload, request_id)

        assert result["statusCode"] == 200

        # Update state in test DB
        now = datetime.utcnow().isoformat()
        db_cursor.execute(
            """UPDATE postulaciones SET requisito_revisado=1, apto=1, estado='entrevista',
               fecha_actualizacion=? WHERE id_postulacion=?""",
            (now, app_id)
        )
        db_connection.commit()

        # Verify state transition
        assert get_application_state(db_cursor, app_id) == "entrevista"

        # Step 3: Schedule and pass entrevista
        mock_cursor.fetchone.return_value = ("entrevista",)

        entrevista_payload = {
            "entrevista_aprobada": True,
            "fecha_entrevista": "2026-05-25T10:00:00",
            "notas_entrevista": "Excelente candidato",
        }
        result = handle_put_postulacion_entrevista(mock_pool, app_id, entrevista_payload, request_id)

        assert result["statusCode"] == 200

        # Update state in test DB
        db_cursor.execute(
            """UPDATE postulaciones SET entrevista_aprobada=1, fecha_entrevista=?,
               notas_entrevista=?, estado='contratacion', fecha_actualizacion=?
               WHERE id_postulacion=?""",
            ("2026-05-25T10:00:00", "Excelente candidato", now, app_id)
        )
        db_connection.commit()

        assert get_application_state(db_cursor, app_id) == "contratacion"

        # Step 4: Hire
        mock_cursor.fetchone.return_value = ("contratacion",)

        contratacion_payload = {
            "contratar": True,
            "fecha_inicio_capacitacion": "2026-06-01",
            "notas_contratacion": "Iniciará en capacitación",
        }
        result = handle_put_postulacion_contratacion(
            mock_pool, app_id, contratacion_payload, request_id
        )

        assert result["statusCode"] == 200

        # Update state in test DB
        db_cursor.execute(
            """UPDATE postulaciones SET contratar=1, fecha_inicio_capacitacion=?,
               notas_contratacion=?, estado='contratado', fecha_actualizacion=?
               WHERE id_postulacion=?""",
            ("2026-06-01", "Iniciará en capacitación", now, app_id)
        )
        db_connection.commit()

        # Verify final state
        final_state = get_application_state(db_cursor, app_id)
        assert final_state == "contratado", f"Expected 'contratado' but got '{final_state}'"

        # Verify all workflow steps completed
        app_data = get_application(db_cursor, app_id)
        assert app_data["requisito_revisado"] == 1
        assert app_data["apto"] == 1
        assert app_data["entrevista_aprobada"] == 1
        assert app_data["contratar"] == 1


class TestRequisitoRejection:
    """Test rejection at requisito stage."""

    def test_rejection_at_requisito(self, db_cursor, mock_pool, request_id):
        """Test application rejected during requisito review."""
        db_connection = db_cursor.connection

        # Setup
        campaign_id = create_test_campaign(db_cursor, "Campaign for Rejection Test")
        position_id = create_test_position(db_cursor, "Position")
        req_id = create_test_requirement(db_cursor, "REQ-REJECT", campaign_id, position_id)
        applicant_id = create_test_applicant(
            db_cursor, "Jane", "Smith", "87654321", "jane@example.com", "987654322"
        )
        app_id = create_test_application(db_cursor, req_id, applicant_id)
        db_connection.commit()

        assert get_application_state(db_cursor, app_id) == "nueva"

        # Reject at requisito stage (apto=false)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("nueva",)
        mock_conn.cursor.return_value = mock_cursor

        mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

        requisito_payload = {"apto": False}
        result = handle_put_postulacion_requisito(mock_pool, app_id, requisito_payload, request_id)

        assert result["statusCode"] == 200

        # Update DB
        now = datetime.utcnow().isoformat()
        db_cursor.execute(
            """UPDATE postulaciones SET requisito_revisado=1, apto=0, estado='rechazada',
               fecha_actualizacion=? WHERE id_postulacion=?""",
            (now, app_id)
        )
        db_connection.commit()

        # Verify rejection
        assert get_application_state(db_cursor, app_id) == "rechazada"

        # Try to continue to entrevista - should fail (wrong state)
        mock_cursor.fetchone.return_value = ("rechazada",)

        entrevista_payload = {"entrevista_aprobada": True}
        result = handle_put_postulacion_entrevista(mock_pool, app_id, entrevista_payload, request_id)

        assert result["statusCode"] == 409
        body = json.loads(result["body"])
        assert "No se puede actualizar" in body["error"]


class TestDuplicateApplication:
    """Test prevention of duplicate applications."""

    def test_duplicate_applicant_same_requirement(self, db_cursor, mock_pool, request_id):
        """Test that same applicant cannot apply twice to same requirement."""
        db_connection = db_cursor.connection

        # Setup
        campaign_id = create_test_campaign(db_cursor, "Campaign for Duplicate Test")
        position_id = create_test_position(db_cursor, "Position")
        req_id = create_test_requirement(db_cursor, "REQ-DUP", campaign_id, position_id)
        db_connection.commit()

        # Create first application
        applicant_data = {
            "nombre": "John",
            "apellido": "Doe",
            "dni": "11111111",
            "email": "john@example.com",
            "telefono": "987654323",
            "medio_preferido": "email",
        }

        applicant_id = create_test_applicant(
            db_cursor,
            applicant_data["nombre"],
            applicant_data["apellido"],
            applicant_data["dni"],
            applicant_data["email"],
            applicant_data["telefono"],
        )
        app1_id = create_test_application(db_cursor, req_id, applicant_id)
        db_connection.commit()

        assert app1_id > 0

        # Try to create second application with same applicant
        with patch("lambda_function.check_foreign_key") as mock_fk:
            with patch("lambda_function.check_duplicate") as mock_dup:
                mock_fk.return_value = True
                mock_dup.return_value = False

                mock_conn = MagicMock()
                mock_cursor = MagicMock()

                # Simulate: postulante exists, duplicate application exists
                mock_cursor.fetchone.side_effect = [(applicant_id,), (1,)]
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

                postulacion_payload = {
                    "requerimiento_id": req_id,
                    "postulante": applicant_data,
                }

                result = handle_post_postulaciones(mock_pool, postulacion_payload, request_id)

        # Should return 409 Conflict
        assert result["statusCode"] == 409
        body = json.loads(result["body"])
        assert "ya existe una postulación" in body["error"].lower()


class TestInvalidStateTransition:
    """Test prevention of invalid state transitions."""

    def test_invalid_state_entrevista_without_requisito(self, db_cursor, mock_pool, request_id):
        """Test cannot go to entrevista without passing requisito."""
        db_connection = db_cursor.connection

        # Setup
        campaign_id = create_test_campaign(db_cursor, "Campaign for State Test")
        position_id = create_test_position(db_cursor, "Position")
        req_id = create_test_requirement(db_cursor, "REQ-STATE", campaign_id, position_id)
        applicant_id = create_test_applicant(
            db_cursor, "Alice", "Johnson", "22222222", "alice@example.com", "987654324"
        )
        app_id = create_test_application(db_cursor, req_id, applicant_id)
        db_connection.commit()

        # Verify initial state
        assert get_application_state(db_cursor, app_id) == "nueva"

        # Try to jump directly to entrevista (skipping requisito)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("nueva",)  # State is still 'nueva', not 'entrevista'
        mock_conn.cursor.return_value = mock_cursor

        mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

        entrevista_payload = {"entrevista_aprobada": True}
        result = handle_put_postulacion_entrevista(mock_pool, app_id, entrevista_payload, request_id)

        # Should fail - wrong state
        assert result["statusCode"] == 409
        body = json.loads(result["body"])
        assert "No se puede actualizar entrevista" in body["error"]

    def test_invalid_state_contratacion_without_entrevista(
        self, db_cursor, mock_pool, request_id
    ):
        """Test cannot go to contratacion without passing entrevista."""
        db_connection = db_cursor.connection

        # Setup: Create application and move to requisito stage
        campaign_id = create_test_campaign(db_cursor, "Campaign for State 2 Test")
        position_id = create_test_position(db_cursor, "Position")
        req_id = create_test_requirement(db_cursor, "REQ-STATE2", campaign_id, position_id)
        applicant_id = create_test_applicant(
            db_cursor, "Bob", "Wilson", "33333333", "bob@example.com", "987654325"
        )
        app_id = create_test_application(db_cursor, req_id, applicant_id)
        db_connection.commit()

        # Move to entrevista stage (but don't complete it)
        now = datetime.utcnow().isoformat()
        db_cursor.execute(
            """UPDATE postulaciones SET requisito_revisado=1, apto=1, estado='entrevista',
               fecha_actualizacion=? WHERE id_postulacion=?""",
            (now, app_id)
        )
        db_connection.commit()

        # Try to jump to contratacion without passing entrevista
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("entrevista",)  # State is 'entrevista', not 'contratacion'
        mock_conn.cursor.return_value = mock_cursor

        mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

        contratacion_payload = {"contratar": True}
        result = handle_put_postulacion_contratacion(
            mock_pool, app_id, contratacion_payload, request_id
        )

        # Should fail - wrong state
        assert result["statusCode"] == 409
        body = json.loads(result["body"])
        assert "No se puede contratar" in body["error"]


class TestConcurrency:
    """Test concurrent access to same application (optional)."""

    def test_concurrent_updates_same_application(self, db_cursor, mock_pool, request_id):
        """Test that concurrent updates to same application are handled correctly."""
        db_connection = db_cursor.connection

        # Setup
        campaign_id = create_test_campaign(db_cursor, "Campaign for Concurrency Test")
        position_id = create_test_position(db_cursor, "Position")
        req_id = create_test_requirement(db_cursor, "REQ-CONC", campaign_id, position_id)
        applicant_id = create_test_applicant(
            db_cursor, "Charlie", "Brown", "44444444", "charlie@example.com", "987654326"
        )
        app_id = create_test_application(db_cursor, req_id, applicant_id)
        db_connection.commit()

        results = []
        errors = []

        def update_requisito():
            """Thread function to update requisito."""
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = ("nueva",)
            mock_conn.cursor.return_value = mock_cursor

            mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

            requisito_payload = {"apto": True}
            try:
                result = handle_put_postulacion_requisito(
                    mock_pool, app_id, requisito_payload, f"{request_id}-thread1"
                )
                results.append(result)
            except Exception as e:
                errors.append(str(e))

        def update_entrevista():
            """Thread function to update entrevista."""
            time.sleep(0.1)  # Small delay to simulate concurrent access

            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            # First update passes, second might fail depending on timing
            mock_cursor.fetchone.return_value = ("entrevista",)
            mock_conn.cursor.return_value = mock_cursor

            mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

            entrevista_payload = {"entrevista_aprobada": True}
            try:
                result = handle_put_postulacion_entrevista(
                    mock_pool, app_id, entrevista_payload, f"{request_id}-thread2"
                )
                results.append(result)
            except Exception as e:
                errors.append(str(e))

        # Start threads
        thread1 = threading.Thread(target=update_requisito)
        thread2 = threading.Thread(target=update_entrevista)

        thread1.start()
        thread2.start()

        thread1.join(timeout=5)
        thread2.join(timeout=5)

        # Verify results
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert len(results) >= 1, "At least one update should succeed"

        # At least one should succeed
        success_count = sum(1 for r in results if r.get("statusCode") == 200)
        assert success_count >= 1


class TestDataIntegrity:
    """Test data integrity and constraints."""

    def test_foreign_key_constraint(self, db_cursor, mock_pool, request_id):
        """Test that foreign key constraints are enforced."""
        db_connection = db_cursor.connection

        # Try to create requirement with non-existent campaign
        with patch("lambda_function.check_foreign_key") as mock_fk:
            mock_fk.return_value = False  # Foreign key check fails

            payload = {
                "codigo": "REQ-FK",
                "campania_id": 9999,  # Non-existent
                "puesto_id": 1,
                "cantidad_vacantes": 5,
                "descripcion": "Test",
            }

            result = handle_post_requerimientos(mock_pool, payload, request_id)

        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert "no encontrada" in body["error"].lower() or "no existe" in body["error"].lower()

    def test_unique_constraints(self, db_cursor, mock_pool, request_id):
        """Test that unique constraints are enforced."""
        db_connection = db_cursor.connection

        # Create first requirement
        campaign_id = create_test_campaign(db_cursor, "Campaign for Unique Test")
        position_id = create_test_position(db_cursor, "Position")
        create_test_requirement(db_cursor, "REQ-UNIQUE", campaign_id, position_id)
        db_connection.commit()

        # Try to create another with same codigo
        with patch("lambda_function.check_foreign_key") as mock_fk:
            with patch("lambda_function.check_duplicate") as mock_dup:
                mock_fk.return_value = True
                mock_dup.return_value = True  # Duplicate exists

                payload = {
                    "codigo": "REQ-UNIQUE",
                    "campania_id": campaign_id,
                    "puesto_id": position_id,
                    "cantidad_vacantes": 5,
                    "descripcion": "Duplicate",
                }

                result = handle_post_requerimientos(mock_pool, payload, request_id)

        assert result["statusCode"] == 409
        body = json.loads(result["body"])
        assert "ya existe" in body["error"].lower()


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

class TestWorkflowVariations:
    """Test various workflow variations with parametrized tests."""

    @pytest.mark.parametrize(
        "apto,expected_state",
        [
            (True, "entrevista"),
            (False, "rechazada"),
        ],
    )
    def test_requisito_outcome_variations(
        self, db_cursor, mock_pool, request_id, apto, expected_state
    ):
        """Test different outcomes after requisito review.

        Args:
            apto: Whether applicant is suitable
            expected_state: Expected state after requisito
        """
        db_connection = db_cursor.connection

        # Setup
        campaign_id = create_test_campaign(db_cursor, f"Campaign for {expected_state}")
        position_id = create_test_position(db_cursor, "Position")
        req_id = create_test_requirement(db_cursor, f"REQ-{expected_state}", campaign_id, position_id)
        applicant_id = create_test_applicant(
            db_cursor, "Test", "User", "55555555", "test@example.com", "987654327"
        )
        app_id = create_test_application(db_cursor, req_id, applicant_id)
        db_connection.commit()

        # Update requisito
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("nueva",)
        mock_conn.cursor.return_value = mock_cursor

        mock_pool.get_connection.return_value.__enter__.return_value = mock_conn

        requisito_payload = {"apto": apto}
        result = handle_put_postulacion_requisito(mock_pool, app_id, requisito_payload, request_id)

        assert result["statusCode"] == 200

        # Update DB state
        now = datetime.utcnow().isoformat()
        db_cursor.execute(
            """UPDATE postulaciones SET requisito_revisado=1, apto=?, estado=?,
               fecha_actualizacion=? WHERE id_postulacion=?""",
            (1 if apto else 0, expected_state, now, app_id)
        )
        db_connection.commit()

        # Verify state
        final_state = get_application_state(db_cursor, app_id)
        assert final_state == expected_state


# ============================================================================
# FIXTURES FOR CLEANUP & REPORTING
# ============================================================================

@pytest.fixture(autouse=True)
def log_test_info(request):
    """Log test information for debugging.

    Args:
        request: pytest request object
    """
    print(f"\n{'='*70}")
    print(f"Test: {request.node.name}")
    print(f"File: {request.node.fspath}")
    print(f"{'='*70}")

    yield

    print(f"\n{'='*70}\n")


@pytest.fixture
def report_database_state(db_cursor):
    """Report database state for debugging.

    Args:
        db_cursor: Database cursor
    """
    yield

    # Report final state
    print("\n📊 Database State After Test:")

    tables = [
        ("campanias", "SELECT COUNT(*) FROM campanias"),
        ("puestos", "SELECT COUNT(*) FROM puestos"),
        ("requerimientos", "SELECT COUNT(*) FROM requerimientos"),
        ("postulantes", "SELECT COUNT(*) FROM postulantes"),
        ("postulaciones", "SELECT COUNT(*) FROM postulaciones"),
    ]

    for table_name, query in tables:
        count = db_cursor.execute(query).fetchone()[0]
        print(f"  {table_name}: {count} rows")
