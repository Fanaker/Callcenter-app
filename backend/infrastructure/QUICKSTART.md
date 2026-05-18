# ⚡ Quick Start Guide - Recruitment Backend Deployment

Deploy the Recruitment Backend to AWS in 5 minutes!

## 📋 Prerequisites Checklist

```bash
# 1. Check AWS CLI is installed
aws --version

# 2. Check SAM CLI is installed
sam --version

# 3. Check Python 3.11+
python3 --version

# 4. Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, region, and output format

# 5. Have these values ready:
# - RDS endpoint (e.g., rds-xxx.us-east-1.rds.amazonaws.com)
# - Database name (e.g., callcenter)
# - Database user (e.g., admin)
# - Database password
# - VPC ID
# - Private subnet IDs (2)
# - Security group ID
# - Email for alerts
```

## 🚀 5-Minute Deployment

### Step 1: Navigate to Infrastructure Directory

```bash
cd infrastructure
```

### Step 2: Install Dependencies (if needed)

```bash
# Install Python dependencies for layer
pip install pyodbc pydantic email-validator

# If using Makefile
make check-tools
```

### Step 3: Build the Application

```bash
# Option A: Using Makefile (recommended)
make build

# Option B: Using SAM CLI
sam build
```

### Step 4: Deploy to AWS

```bash
# Option A: Guided deployment (recommended for first time)
sam deploy --guided

# Option B: Using Makefile
make deploy-dev          # Deploy to dev
make deploy-staging      # Deploy to staging
make deploy-prod         # Deploy to production

# Option C: Direct SAM deployment
sam deploy \
    --stack-name recruitment-backend-prod \
    --s3-bucket your-s3-bucket \
    --region us-east-1 \
    --capabilities CAPABILITY_NAMED_IAM
```

### Step 5: Get Your API URL

```bash
# Using Makefile
make outputs

# Using AWS CLI
aws cloudformation describe-stacks \
    --stack-name recruitment-backend-prod \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text

# Output will be something like:
# https://abc123def.execute-api.us-east-1.amazonaws.com/prod
```

## ✅ Test Your Deployment

```bash
# Set your API URL (replace with actual URL)
API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"

# Test GET endpoint
curl -X GET "$API_URL/v1/campanias/activas"

# Should return something like:
# {"campanias": []}

# Test POST endpoint
curl -X POST "$API_URL/v1/requerimientos" \
    -H "Content-Type: application/json" \
    -d '{
        "codigo": "TEST-001",
        "campania_id": 1,
        "puesto_id": 1,
        "cantidad_vacantes": 5,
        "descripcion": "Test requirement"
    }'

# Run full integration tests
make test-api
```

## 📊 Monitor Your Deployment

```bash
# View real-time logs
make logs

# View alarms
make alarms

# Open CloudWatch dashboard
make dashboard

# Show stack outputs
make outputs

# Check stack status
make status
```

## 🔄 Make Updates

```bash
# Update Lambda code
# 1. Edit lambda_function.py
# 2. Rebuild and redeploy:

make build
make deploy

# Or in one command:
make quick-deploy
```

## 🧹 Cleanup

```bash
# Remove build artifacts (safe)
make clean

# Delete entire stack (CAREFUL - no undo!)
make delete-stack
```

## 📊 Common Commands Reference

### Build & Deploy
```bash
make validate           # Validate template
make build             # Build SAM app
make deploy            # Deploy to current environment
make quick-deploy      # Clean build and deploy
make deploy-dev        # Deploy to dev
make deploy-staging    # Deploy to staging
make deploy-prod       # Deploy to prod
```

### Testing
```bash
make test              # Run unit tests
make test-api          # Run API integration tests
make full-test         # Run all tests
```

### Monitoring
```bash
make logs              # Stream Lambda logs
make dashboard         # Open CloudWatch dashboard
make alarms            # List CloudWatch alarms
make outputs           # Show stack outputs
make status            # Show stack status
make info              # Show all stack info
```

### Cleanup
```bash
make clean             # Remove build artifacts
make delete-stack      # Delete CloudFormation stack
```

## 🎯 Environment Variables

Create `.env` file from example:

```bash
cp .env.example .env
# Edit .env with your values
```

Required variables:
- `DB_HOST`: RDS endpoint
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASS`: Database password
- `VPC_ID`: VPC ID
- `PRIVATE_SUBNET_1`: Subnet ID
- `PRIVATE_SUBNET_2`: Subnet ID
- `LAMBDA_SECURITY_GROUP`: Security group ID
- `ALERT_EMAIL`: Email for alerts

## 🔐 Security Notes

### Database Credentials
- Stored securely in AWS Secrets Manager
- Never logged or exposed
- Can be rotated automatically

### API Security
- CORS configured (customize for production)
- X-Ray tracing enabled
- CloudWatch logs with JSON structure
- Request ID tracking for debugging

### Network Security
- Lambda runs in private subnets
- Security group restricts access to RDS only
- No direct internet access

## 🐛 Troubleshooting

### AWS Credentials Error
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

### S3 Bucket Not Found
```bash
# Create S3 bucket for SAM artifacts
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1

aws s3 mb s3://lambda-layers-${ACCOUNT_ID}-${REGION} \
    --region ${REGION}
```

### Lambda Can't Connect to RDS
```bash
# Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Add inbound rule if missing (replace sg-ids)
aws ec2 authorize-security-group-ingress \
    --group-id sg-rds-id \
    --protocol tcp \
    --port 1433 \
    --source-security-group-id sg-lambda-id
```

### ODBC Layer Error
```bash
# Rebuild and upload ODBC layer
make build-layer

# Then deploy
make deploy
```

## 📚 Next Steps

1. **Setup Database**: Ensure RDS SQL Server is created with proper schema
2. **Test Endpoints**: Use Postman or curl to test all endpoints
3. **Monitor Logs**: Check CloudWatch logs for any errors
4. **Setup Alarms**: Verify SNS topic subscription for alerts
5. **Scale Up**: Adjust Lambda memory, timeout, and concurrent executions as needed

## 📈 Performance Tips

### Improve Cold Start Time
```bash
# Increase Lambda memory (uses more CPU)
# Edit template.yaml -> MemorySize: 1024

# Use provisioned concurrency
# Edit template.yaml -> ReservedConcurrentExecutions: 50
```

### Improve Database Performance
```bash
# Check RDS CPU and connections
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name CPUUtilization \
    --dimensions Name=DBInstanceIdentifier,Value=your-db-instance \
    --statistics Average \
    --start-time 2026-05-18T00:00:00Z \
    --end-time 2026-05-19T00:00:00Z \
    --period 3600
```

## 📝 Documentation

- [Full README](README.md) - Detailed setup and configuration
- [Template Documentation](template.yaml) - Infrastructure as Code details
- [API Documentation](../API.md) - Endpoint specifications
- [Test Documentation](../tests/) - Test suite details

## 🆘 Need Help?

### View Logs
```bash
make logs

# Or specific time range
aws logs filter-log-events \
    --log-group-name /aws/lambda/recruitment-backend-prod \
    --start-time $(($(date +%s)*1000 - 3600000))
```

### Check Recent Changes
```bash
aws cloudformation describe-stack-events \
    --stack-name recruitment-backend-prod \
    --query 'StackEvents[:5]'
```

### Validate Template
```bash
make validate

# Or
sam validate --template template.yaml
```

## ✨ That's It!

Your Recruitment Backend is now deployed on AWS Lambda with:
- ✅ REST API via API Gateway
- ✅ Lambda function with VPC access to RDS
- ✅ CloudWatch monitoring and alarms
- ✅ JSON structured logging
- ✅ X-Ray tracing
- ✅ Auto-scaling capabilities

**Time to celebrate! 🎉**

---

**For detailed documentation**, see [README.md](README.md)  
**For support**, check logs with `make logs` or `make dashboard`
