# Local Development & Deployment Guide

Complete guide for running the Recruitment Backend locally and deploying to AWS.

## 🚀 Quick Start (5 minutes)

### 1. Install Prerequisites

```bash
# Check if installed
sam --version          # Should be > 1.60
docker --version       # Should be installed
python3 --version      # Should be 3.11+
pip --version          # Should be > 20

# If not installed:
# macOS:
brew install aws-sam-cli docker python@3.11

# Linux:
sudo apt-get install aws-sam-cli docker python3.11

# Windows:
choco install aws-sam-cli docker python@3.11
```

### 2. Configure AWS Credentials

```bash
# One-time setup
aws configure

# Enter:
# AWS Access Key ID: [your key]
# AWS Secret Access Key: [your secret]
# Default region: us-east-1
# Default output format: json

# Or set environment variables:
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Build & Run Locally

```bash
cd infrastructure

# Build the application
sam build

# Start local API (runs on http://localhost:3000)
sam local start-api

# Output should show:
# 2026-05-18 10:30:00 Mounting LambdaFunction at http://127.0.0.1:3000/v1/campanias/activas [GET]
# 2026-05-18 10:30:00 Mounting LambdaFunction at http://127.0.0.1:3000/v1/puestos/activos [GET]
# ... (all 10 endpoints)
# 2026-05-18 10:30:00 Waiting for connections...
```

### 4. Test API (New Terminal)

```bash
# Test GET endpoint
curl http://localhost:3000/v1/campanias/activas

# Expected response:
# {"campanias": []}
```

---

## 🔨 Local Development Workflow

### Setup Local Environment

```bash
# 1. Clone/navigate to project
cd recruitment-backend/infrastructure

# 2. Create Python virtual environment
python3 -m venv .venv

# 3. Activate environment
# macOS/Linux:
source .venv/bin/activate

# Windows:
.\.venv\Scripts\activate

# 4. Install dependencies
pip install pyodbc pydantic email-validator
pip install pytest pytest-cov pytest-mock
```

### Build & Run Locally

```bash
# Build the SAM application
sam build

# Options:
sam build --use-container     # Use Docker for building (recommended)
sam build --cached            # Cache dependencies
sam build --parallel          # Parallel build

# Start local API server
sam local start-api

# Options:
sam local start-api --port 8000                    # Custom port
sam local start-api --debug                        # Debug mode
sam local start-api --warm-containers EAGER        # Pre-warm containers
sam local start-api --profile dev-profile          # Use specific AWS profile
```

---

## 🧪 Testing Locally

### Using curl

```bash
# GET endpoint - no data needed
curl http://localhost:3000/v1/campanias/activas

# POST endpoint - with JSON data
curl -X POST http://localhost:3000/v1/requerimientos \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "REQ-001",
    "campania_id": 1,
    "puesto_id": 1,
    "cantidad_vacantes": 10,
    "descripcion": "Test requirement"
  }'

# PUT endpoint
curl -X PUT http://localhost:3000/v1/postulaciones/1/requisito \
  -H "Content-Type: application/json" \
  -d '{"apto": true}'
```

### Using Postman

```
1. Open Postman
2. Import collection: infrastructure/postman_collection.json
3. Set variables:
   - base_url: http://localhost:3000
   - api_version: v1
4. Run requests from collection
5. Check responses
```

### Using pytest

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_handlers.py -v

# Run integration tests
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/ -v --cov=lambda_function --cov-report=html

# Run with output
pytest tests/test_handlers.py -v -s

# Run specific test
pytest tests/test_handlers.py::test_get_campanias_activas_success -v
```

### Using Make Commands

```bash
# Build
make build

# Test
make test              # Unit tests
make test-api          # Integration tests
make full-test         # All tests

# Local development
make validate          # Validate template
make logs              # View logs
```

---

## 📊 Complete API Test Suite

### Test All Endpoints (bash script)

```bash
#!/bin/bash

API="http://localhost:3000/v1"

echo "Testing Recruitment Backend API"
echo "================================"

# Test 1: GET /campanias/activas
echo "1. GET /campanias/activas"
curl -s -X GET "$API/campanias/activas" | jq .

# Test 2: GET /puestos/activos
echo -e "\n2. GET /puestos/activos"
curl -s -X GET "$API/puestos/activos" | jq .

# Test 3: GET /requerimientos
echo -e "\n3. GET /requerimientos"
curl -s -X GET "$API/requerimientos" | jq .

# Test 4: POST /requerimientos (validation error - missing fields)
echo -e "\n4. POST /requerimientos (invalid - missing fields)"
curl -s -X POST "$API/requerimientos" \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

# Test 5: POST /requerimientos (valid)
echo -e "\n5. POST /requerimientos (valid)"
REQ_PAYLOAD='{
  "codigo": "REQ-'$(date +%s)'",
  "campania_id": 1,
  "puesto_id": 1,
  "cantidad_vacantes": 5,
  "descripcion": "Test requirement"
}'
RESULT=$(curl -s -X POST "$API/requerimientos" \
  -H "Content-Type: application/json" \
  -d "$REQ_PAYLOAD")
echo $RESULT | jq .

# Test 6: POST /postulaciones (valid)
echo -e "\n6. POST /postulaciones (valid)"
curl -s -X POST "$API/postulaciones" \
  -H "Content-Type: application/json" \
  -d '{
    "requerimiento_id": 1,
    "postulante": {
      "nombre": "Juan",
      "apellido": "Pérez",
      "dni": "12345678",
      "email": "juan@example.com",
      "telefono": "987654321",
      "medio_preferido": "email"
    }
  }' | jq .

# Test 7: GET /requerimientos (with filter)
echo -e "\n7. GET /requerimientos?estado=nueva"
curl -s -X GET "$API/requerimientos?estado=nueva" | jq .

echo -e "\n================================"
echo "Tests completed!"
```

---

## 🐛 Debugging Locally

### Enable Debug Mode

```bash
# Start with debug output
sam local start-api --debug

# Output shows all Lambda invocations, logs, etc.
```

### View Lambda Logs

```bash
# In another terminal, tail logs
tail -f .aws-sam/logs/lambda.log

# Or use CloudWatch Logs Insights locally:
sam logs -n RecruitmentBackendFunction --stack-name SAM_STACK
```

### Common Issues & Solutions

#### Issue 1: Port Already in Use

```bash
# Error: Address already in use

# Solution: Kill process on port 3000
# macOS/Linux:
lsof -ti:3000 | xargs kill -9

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port:
sam local start-api --port 8000
```

#### Issue 2: Docker Not Running

```bash
# Error: Cannot connect to Docker daemon

# Solution: Start Docker
# macOS:
open /Applications/Docker.app

# Linux:
sudo systemctl start docker

# Windows:
# Click Docker Desktop icon
```

#### Issue 3: Dependencies Not Found

```bash
# Error: ModuleNotFoundError: No module named 'pyodbc'

# Solution: Install dependencies
pip install pyodbc pydantic email-validator

# Or rebuild with dependencies:
sam build --use-container
```

#### Issue 4: Lambda Container Issues

```bash
# Error: Lambda container failed to start

# Solution: Clear SAM cache
rm -rf .aws-sam/
sam build --use-container

# Or increase Docker resources:
# Docker Desktop → Preferences → Resources → Increase Memory/CPU
```

---

## 🚀 Deploy to AWS

### Step 1: Initial Guided Deployment

```bash
cd infrastructure

sam deploy --guided

# Follow prompts:
# ✓ Stack Name: recruitment-backend-prod
# ✓ AWS Region: us-east-1
# ✓ Parameter DbHost: your-rds-endpoint.amazonaws.com
# ✓ Parameter DbName: callcenter
# ✓ Parameter DbUser: admin
# ✓ Parameter DbPassword: *** (hidden)
# ✓ Parameter VpcId: vpc-xxxxx
# ✓ Parameter PrivateSubnet1: subnet-xxxxx
# ✓ Parameter PrivateSubnet2: subnet-xxxxx
# ✓ Parameter LambdaSecurityGroup: sg-xxxxx
# ✓ Parameter CorsOrigin: https://yourdomain.com
# ✓ Parameter AlertEmail: alerts@example.com
# ✓ Confirm changeset: Y
# ✓ Allow SAM to create IAM roles: Y

# Output shows:
# CloudFormation events...
# Stack created successfully
# API endpoint: https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

### Step 2: Subsequent Deployments

```bash
# After first deployment, use config file
sam deploy

# Or specify environment
sam deploy --config-env prod      # Production
sam deploy --config-env staging   # Staging
sam deploy --config-env dev       # Development

# Or deploy with no confirmation
sam deploy --no-confirm-changeset
```

### Step 3: Verify Deployment

```bash
# Get API endpoint
aws cloudformation describe-stacks \
  --stack-name recruitment-backend-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text

# Test API (replace with actual URL)
curl https://abc123.execute-api.us-east-1.amazonaws.com/prod/v1/campanias/activas

# View logs
aws logs tail /aws/lambda/recruitment-backend-prod --follow

# Check alarms
aws cloudwatch describe-alarms --region us-east-1 | grep recruitment
```

### Step 4: Monitor Deployment

```bash
# View CloudWatch logs
make logs ENVIRONMENT=prod

# View alarms
make alarms ENVIRONMENT=prod

# Open dashboard
make dashboard ENVIRONMENT=prod

# Check stack events
aws cloudformation describe-stack-events \
  --stack-name recruitment-backend-prod
```

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] All tests pass locally: `pytest tests/ -v`
- [ ] No linting errors: `pylint lambda_function.py`
- [ ] Code formatted: `black lambda_function.py`
- [ ] Template validates: `sam validate`
- [ ] AWS credentials configured: `aws sts get-caller-identity`
- [ ] RDS database created and accessible
- [ ] VPC/subnets/security groups configured
- [ ] S3 bucket for SAM artifacts exists
- [ ] Email address for alarms is correct

### During Deployment

- [ ] No errors in CloudFormation events
- [ ] Lambda function created successfully
- [ ] API Gateway endpoints created
- [ ] IAM roles created with correct permissions
- [ ] Secrets Manager secret created with DB credentials
- [ ] CloudWatch alarms created
- [ ] X-Ray tracing enabled

### Post-Deployment

- [ ] API endpoint responds to requests
- [ ] Logs appear in CloudWatch
- [ ] Alarms subscribed to SNS topic
- [ ] Database connection working
- [ ] All 10 endpoints tested
- [ ] Performance acceptable

---

## 🔄 Local Development Loop

### Typical Workflow

```
1. Start local API
   $ sam local start-api

2. In another terminal:
   $ curl http://localhost:3000/v1/campanias/activas
   
3. Edit code (lambda_function.py)

4. Rebuild (Ctrl+C to stop, then):
   $ sam build
   $ sam local start-api

5. Test changes
   $ curl http://localhost:3000/v1/campanias/activas

6. Run unit tests
   $ pytest tests/ -v

7. Commit changes
   $ git add .
   $ git commit -m "Add feature..."

8. Deploy to AWS
   $ sam deploy
```

### Using File Watcher for Auto-Rebuild

```bash
# Install watchmedo (on macOS/Linux)
pip install watchdog

# Auto-rebuild on file changes
watchmedo shell-command \
  --patterns="*.py" \
  --recursive \
  --command='sam build' \
  .
```

---

## 🎯 Common Development Tasks

### Add New Endpoint

```bash
# 1. Add handler function to lambda_function.py
def handle_new_endpoint(pool, request_id):
    # Implementation
    pass

# 2. Add route to lambda_handler
elif method == "GET" and path == "/new-endpoint":
    return handle_new_endpoint(pool, request_id)

# 3. Rebuild and test
sam build
sam local start-api
curl http://localhost:3000/v1/new-endpoint

# 4. Add unit tests to tests/test_handlers.py
def test_new_endpoint_success():
    # Test implementation
    pass

# 5. Run tests
pytest tests/test_handlers.py::test_new_endpoint_success -v

# 6. Deploy
sam deploy
```

### Add New Database Query

```bash
# 1. Test query in SQL Server Management Studio or locally
SELECT * FROM campanias WHERE activa = 1

# 2. Add to lambda_function.py
with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM campanias WHERE activa = 1")
    rows = cursor.fetchall()

# 3. Test locally
sam build && sam local start-api

# 4. Check performance with CloudWatch logs
```

### Update Dependencies

```bash
# 1. Add to requirements.txt
pip install new-package

# 2. Update lambda layer
sam build --use-container

# 3. Test locally
sam local start-api

# 4. Deploy
sam deploy
```

---

## 📈 Performance Testing Locally

### Load Test with Apache Bench

```bash
# Install ab (ApacheBench)
# macOS: brew install httpd
# Linux: sudo apt-get install apache2-utils

# Start local API
sam local start-api

# Run load test (1000 requests, 10 concurrent)
ab -n 1000 -c 10 http://localhost:3000/v1/campanias/activas

# Output shows:
# Requests per second: [value]
# Time per request: [value]ms
# Failed requests: [count]
```

### Memory/CPU Profiling

```bash
# Install memory_profiler
pip install memory-profiler

# Add to lambda_function.py
from memory_profiler import profile

@profile
def handle_get_campanias_activas(pool, request_id):
    # Function body
    pass

# Run locally and monitor
sam local start-api
```

---

## 🔐 Security Notes

### Local Development

```
⚠️ IMPORTANT:
- Never commit .env files with passwords
- Use environment variables instead
- For local testing, use a test RDS instance
- Don't expose credentials in logs
- Use AWS IAM roles, not access keys (when possible)
```

### Secrets in Local Development

```bash
# Create .env.local (NOT COMMITTED)
DB_PASS=test-password-only-for-local-dev

# Load in your shell
source .env.local

# Or use AWS Secrets Manager locally:
aws secretsmanager get-secret-value --secret-id test-secret
```

---

## 📚 Useful References

- [SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [SAM Local Testing](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-testing.html)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway Testing](https://docs.aws.amazon.com/apigateway/latest/developerguide/test-invoke-api-gateway.html)

---

## ✅ Verification Checklist

### Local Development Works

- [ ] `sam build` completes without errors
- [ ] `sam local start-api` starts successfully
- [ ] `curl http://localhost:3000/v1/campanias/activas` returns 200
- [ ] All 10 endpoints are mounted
- [ ] `pytest tests/ -v` passes all tests
- [ ] Debug mode shows logs properly

### AWS Deployment Works

- [ ] `sam deploy --guided` completes successfully
- [ ] CloudFormation stack created
- [ ] Lambda function deployed
- [ ] API Gateway endpoints working
- [ ] `curl https://api-endpoint/v1/campanias/activas` returns 200
- [ ] CloudWatch logs appearing
- [ ] Alarms configured and subscribed

---

**Status**: Ready for Development & Production  
**Last Updated**: May 2026  
**Version**: 1.0
