#!/bin/bash

################################################################################
# Recruitment Backend API - Integration Test Script
# Tests all endpoints after deployment
# Usage: ./test-api.sh <API_URL> [environment]
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL=${1:-}
ENVIRONMENT=${2:-prod}
TEST_RESULTS=0
TEST_PASSED=0
TEST_FAILED=0

# Default headers
HEADERS=(
    "-H" "Content-Type: application/json"
    "-H" "Accept: application/json"
)

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}   $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_code=$4
    local test_name=$5

    echo ""
    echo -e "${YELLOW}Testing:${NC} $test_name"
    echo -e "  Method: $method"
    echo -e "  URL: $API_URL$endpoint"

    # Make request
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" "${HEADERS[@]}")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            "${HEADERS[@]}" \
            -d "$data")
    fi

    # Extract status code and body
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    echo -e "  Status: $http_code (expected: $expected_code)"

    # Check result
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "  ${GREEN}✓ PASS${NC}"
        ((TEST_PASSED++))
    else
        echo -e "  ${RED}✗ FAIL${NC}"
        echo -e "  Response: $body"
        ((TEST_FAILED++))
    fi

    ((TEST_RESULTS++))
}

# Validate input
if [ -z "$API_URL" ]; then
    echo -e "${RED}Error: API_URL not provided${NC}"
    echo "Usage: $0 <API_URL> [environment]"
    echo "Example: $0 https://abc123.execute-api.us-east-1.amazonaws.com/prod prod"
    exit 1
fi

# Remove trailing slash from API_URL
API_URL="${API_URL%/}"

print_header "Recruitment Backend API Tests"
echo ""
echo -e "API URL: ${GREEN}$API_URL${NC}"
echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
echo ""

# =============================================================================
# GET /v1/campanias/activas
# =============================================================================

print_header "GET /v1/campanias/activas"

test_endpoint "GET" "/v1/campanias/activas" "" "200" \
    "Get active campaigns - should return 200"

# =============================================================================
# GET /v1/puestos/activos
# =============================================================================

print_header "GET /v1/puestos/activos"

test_endpoint "GET" "/v1/puestos/activos" "" "200" \
    "Get active positions - should return 200"

# =============================================================================
# GET /v1/requerimientos
# =============================================================================

print_header "GET /v1/requerimientos"

test_endpoint "GET" "/v1/requerimientos" "" "200" \
    "Get all requirements - should return 200"

test_endpoint "GET" "/v1/requerimientos?estado=nueva" "" "200" \
    "Get requirements filtered by state - should return 200"

# =============================================================================
# POST /v1/requerimientos
# =============================================================================

print_header "POST /v1/requerimientos"

# Valid requirement
REQ_PAYLOAD='{
    "codigo": "TEST-'$(date +%s%N | md5sum | head -c 8)'",
    "campania_id": 1,
    "puesto_id": 1,
    "cantidad_vacantes": 5,
    "descripcion": "Test requirement for integration testing"
}'

test_endpoint "POST" "/v1/requerimientos" "$REQ_PAYLOAD" "201" \
    "Create requirement - should return 201"

# Missing required field
INVALID_REQ_PAYLOAD='{
    "campania_id": 1,
    "puesto_id": 1
}'

test_endpoint "POST" "/v1/requerimientos" "$INVALID_REQ_PAYLOAD" "422" \
    "Create requirement with missing fields - should return 422"

# Invalid cantidad_vacantes
INVALID_CANTIDAD='{
    "codigo": "TEST-002",
    "campania_id": 1,
    "puesto_id": 1,
    "cantidad_vacantes": 0,
    "descripcion": "Test"
}'

test_endpoint "POST" "/v1/requerimientos" "$INVALID_CANTIDAD" "422" \
    "Create requirement with invalid cantidad - should return 422"

# =============================================================================
# GET /v1/requerimientos/{codigo}
# =============================================================================

print_header "GET /v1/requerimientos/{codigo}"

# Get first requirement (we don't know the codigo, but test the pattern)
test_endpoint "GET" "/v1/requerimientos/REQ-001" "" "200" \
    "Get requirement by codigo (REQ-001) - may return 200 or 404"

test_endpoint "GET" "/v1/requerimientos/NONEXISTENT" "" "404" \
    "Get nonexistent requirement - should return 404"

# =============================================================================
# POST /v1/postulaciones
# =============================================================================

print_header "POST /v1/postulaciones"

# Valid postulation
POSTULACION_PAYLOAD='{
    "requerimiento_id": 1,
    "postulante": {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "'$(shuf -i 10000000-99999999 -n 1)'",
        "email": "test-'$(date +%s%N)'@example.com",
        "telefono": "9'$(shuf -i 10000000-99999999 -n 1)'",
        "medio_preferido": "email",
        "cv_url": "https://example.com/cv.pdf"
    }
}'

test_endpoint "POST" "/v1/postulaciones" "$POSTULACION_PAYLOAD" "201" \
    "Create postulation - should return 201"

# Invalid DNI
INVALID_DNI_PAYLOAD='{
    "requerimiento_id": 1,
    "postulante": {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "123",
        "email": "test@example.com",
        "telefono": "987654321",
        "medio_preferido": "email"
    }
}'

test_endpoint "POST" "/v1/postulaciones" "$INVALID_DNI_PAYLOAD" "422" \
    "Create postulation with invalid DNI - should return 422"

# Invalid phone
INVALID_PHONE_PAYLOAD='{
    "requerimiento_id": 1,
    "postulante": {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "test@example.com",
        "telefono": "812345678",
        "medio_preferido": "email"
    }
}'

test_endpoint "POST" "/v1/postulaciones" "$INVALID_PHONE_PAYLOAD" "422" \
    "Create postulation with invalid phone - should return 422"

# Invalid email
INVALID_EMAIL_PAYLOAD='{
    "requerimiento_id": 1,
    "postulante": {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "not-an-email",
        "telefono": "987654321",
        "medio_preferido": "email"
    }
}'

test_endpoint "POST" "/v1/postulaciones" "$INVALID_EMAIL_PAYLOAD" "422" \
    "Create postulation with invalid email - should return 422"

# =============================================================================
# PUT /v1/postulaciones/{idPostulacion}/requisito
# =============================================================================

print_header "PUT /v1/postulaciones/{idPostulacion}/requisito"

REQUISITO_PAYLOAD='{"apto": true}'

test_endpoint "PUT" "/v1/postulaciones/1/requisito" "$REQUISITO_PAYLOAD" "200" \
    "Update postulation requisito (may fail if postulation doesn't exist)"

test_endpoint "PUT" "/v1/postulaciones/999999/requisito" "$REQUISITO_PAYLOAD" "404" \
    "Update nonexistent postulation - should return 404"

# =============================================================================
# PUT /v1/postulaciones/{idPostulacion}/entrevista
# =============================================================================

print_header "PUT /v1/postulaciones/{idPostulacion}/entrevista"

ENTREVISTA_PAYLOAD='{
    "entrevista_aprobada": true,
    "fecha_entrevista": "2026-05-25T10:00:00",
    "notas_entrevista": "Excelente candidato"
}'

test_endpoint "PUT" "/v1/postulaciones/1/entrevista" "$ENTREVISTA_PAYLOAD" "200" \
    "Update postulation entrevista (may fail if state is wrong)"

# =============================================================================
# PUT /v1/postulaciones/{idPostulacion}/contratacion
# =============================================================================

print_header "PUT /v1/postulaciones/{idPostulacion}/contratacion"

CONTRATACION_PAYLOAD='{
    "contratar": true,
    "fecha_inicio_capacitacion": "2026-06-01",
    "notas_contratacion": "Iniciará en capacitación"
}'

test_endpoint "PUT" "/v1/postulaciones/1/contratacion" "$CONTRATACION_PAYLOAD" "200" \
    "Update postulation contratacion (may fail if state is wrong)"

# =============================================================================
# Test Results Summary
# =============================================================================

print_header "Test Results Summary"

echo ""
echo -e "Total Tests: ${YELLOW}$TEST_RESULTS${NC}"
echo -e "Passed: ${GREEN}$TEST_PASSED${NC}"
echo -e "Failed: ${RED}$TEST_FAILED${NC}"
echo ""

if [ $TEST_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    exit 1
fi
