# Recruitment Management System - Infrastructure Setup

Complete SAM (Serverless Application Model) infrastructure for the Recruitment Backend.

## 📋 Prerequisites

### Required Tools
```bash
# Install AWS CLI v2
https://aws.amazon.com/cli/

# Install SAM CLI
pip install aws-sam-cli

# Install Python 3.11
python --version  # Must be 3.11+

# Verify SAM installation
sam --version
```

### AWS Requirements
1. AWS Account with appropriate IAM permissions
2. S3 Bucket for CloudFormation artifacts
3. RDS SQL Server instance (already created)
4. VPC with at least 2 private subnets
5. Security group allowing Lambda to RDS communication
6. SNS topic for alarm notifications (optional - template will create one)

## 🔧 Pre-Deployment Setup

### 1. Create S3 Bucket for SAM Artifacts

```bash
aws s3 mb s3://lambda-layers-${AWS_ACCOUNT_ID}-${AWS_REGION} \
    --region ${AWS_REGION}

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket lambda-layers-${AWS_ACCOUNT_ID}-${AWS_REGION} \
    --versioning-configuration Status=Enabled
```

### 2. Build ODBC Lambda Layer

Create the ODBC dependencies layer:

```bash
# Create layer structure
mkdir -p layers/python/lib/python3.11/site-packages

# Install dependencies
pip install -t layers/python/lib/python3.11/site-packages \
    pyodbc pydantic email-validator

# Create zip
cd layers
zip -r odbc-dependencies.zip .
cd ..

# Upload to S3
aws s3 cp layers/odbc-dependencies.zip \
    s3://lambda-layers-${AWS_ACCOUNT_ID}-${AWS_REGION}/layers/
```

### 3. Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Or use AWS_PROFILE environment variable
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1
```

### 4. Gather Required Information

Before deploying, collect:

- **RDS Endpoint**: e.g., `rds-instance.cxyz.us-east-1.rds.amazonaws.com`
- **Database Name**: e.g., `callcenter`
- **Database User**: e.g., `admin`
- **Database Password**: Your RDS master password
- **VPC ID**: Your VPC ID
- **Private Subnet 1**: First private subnet ID
- **Private Subnet 2**: Second private subnet ID
- **Security Group ID**: Lambda security group ID
- **Alert Email**: Email for CloudWatch alarms

## 🚀 Deployment

### Option 1: Guided Deployment (Recommended)

```bash
cd infrastructure

# Build the function
sam build

# Deploy with guided prompts
sam deploy --guided --profile your-profile

# Follow prompts:
# - Stack Name: recruitment-backend-prod
# - Region: us-east-1
# - DbHost: your-rds-endpoint
# - DbName: callcenter
# - DbUser: admin
# - DbPassword: *** (will be hidden)
# - VPC settings (select from dropdowns)
# - AlertEmail: your-email@example.com
# - ✓ Allow SAM CLI changes
```

### Option 2: Using samconfig.toml

```bash
cd infrastructure

# Edit samconfig.toml with your S3 bucket
sed -i 's/{{ YOUR_S3_BUCKET }}/your-actual-bucket/g' samconfig.toml

# Build
sam build

# Deploy to production
sam deploy --config-env prod

# Or deploy to dev
sam deploy --config-env dev

# Or deploy to staging
sam deploy --config-env staging
```

### Option 3: Manual Deployment

```bash
cd infrastructure

sam build

sam deploy \
    --stack-name recruitment-backend-prod \
    --s3-bucket your-s3-bucket \
    --region us-east-1 \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        DbHost=rds-endpoint.amazonaws.com \
        DbName=callcenter \
        DbUser=admin \
        DbPassword=your-password \
        VpcId=vpc-xxxxx \
        PrivateSubnet1=subnet-xxxxx \
        PrivateSubnet2=subnet-xxxxx \
        LambdaSecurityGroup=sg-xxxxx \
        CorsOrigin=https://yourdomain.com \
        ApiStageName=prod \
        AlertEmail=alerts@example.com
```

## 📊 Post-Deployment

### 1. Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
    --stack-name recruitment-backend-prod \
    --region us-east-1

# List Lambda functions
aws lambda list-functions --region us-east-1

# List API Gateway APIs
aws apigateway get-rest-apis --region us-east-1
```

### 2. Get API Endpoint

```bash
# Retrieve API URL from CloudFormation outputs
aws cloudformation describe-stacks \
    --stack-name recruitment-backend-prod \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --region us-east-1 \
    --output text

# Example output: https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

### 3. Test API Endpoints

```bash
# Set your API URL
API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"

# Test GET /v1/campanias/activas
curl -X GET "${API_URL}/v1/campanias/activas"

# Test POST /v1/requerimientos
curl -X POST "${API_URL}/v1/requerimientos" \
    -H "Content-Type: application/json" \
    -d '{
        "codigo": "REQ-001",
        "campania_id": 1,
        "puesto_id": 1,
        "cantidad_vacantes": 10,
        "descripcion": "Test requirement"
    }'
```

### 4. Monitor Alarms

```bash
# View CloudWatch alarms
aws cloudwatch describe-alarms \
    --region us-east-1 \
    --query 'MetricAlarms[*].[AlarmName,StateValue]' \
    --output table

# View CloudWatch logs
aws logs tail /aws/lambda/recruitment-backend-prod \
    --follow \
    --region us-east-1
```

### 5. Access Monitoring Dashboard

```bash
# Open in browser (requires AWS console access)
# https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=recruitment-backend-prod
```

## 🔄 Updates & Maintenance

### Update Lambda Code

```bash
cd infrastructure

# Make changes to ../lambda_function.py

# Build
sam build

# Deploy (without guided prompts)
sam deploy --no-confirm-changeset

# Or with specific environment
sam deploy --config-env prod
```

### Update Infrastructure

```bash
# Edit template.yaml

sam build
sam deploy --no-confirm-changeset
```

### View Changeset Before Deploy

```bash
sam deploy --no-execute-changeset

# Review in CloudFormation console, then:
# Menu → Stacks → Select your stack → Change Sets → Execute
```

## 📝 Environment-Specific Deployments

### Development (Dev)

```bash
sam deploy --config-env dev \
    --parameter-overrides CorsOrigin="*"
```

### Staging

```bash
sam deploy --config-env staging \
    --parameter-overrides CorsOrigin="https://staging.yourdomain.com"
```

### Production

```bash
sam deploy --config-env prod \
    --parameter-overrides CorsOrigin="https://yourdomain.com"
```

## 🗑️ Cleanup

### Delete Stack (Careful!)

```bash
# This will delete ALL resources including Lambda, API Gateway, etc.
aws cloudformation delete-stack \
    --stack-name recruitment-backend-prod \
    --region us-east-1

# Verify deletion
aws cloudformation describe-stacks \
    --stack-name recruitment-backend-prod \
    --region us-east-1
```

### Remove Local Build Artifacts

```bash
rm -rf .aws-sam/
rm -rf .aws-sam-build/
```

## 🐛 Troubleshooting

### Deployment Fails: "S3 bucket not found"

```bash
# Create and verify S3 bucket
aws s3 ls | grep lambda-layers
aws s3 mb s3://lambda-layers-${AWS_ACCOUNT_ID}-${AWS_REGION} --region ${AWS_REGION}
```

### Lambda Can't Connect to RDS

```bash
# Check security group rules
aws ec2 describe-security-groups \
    --group-ids sg-xxxxx \
    --region us-east-1

# RDS SG should allow inbound on port 1433 from Lambda SG
# Add rule if missing:
aws ec2 authorize-security-group-ingress \
    --group-id sg-rds-id \
    --protocol tcp \
    --port 1433 \
    --source-security-group-id sg-lambda-id
```

### ODBC Layer Not Found

```bash
# Verify layer in S3
aws s3 ls s3://lambda-layers-${AWS_ACCOUNT_ID}-${AWS_REGION}/layers/

# If missing, rebuild and upload:
cd infrastructure
mkdir -p layers/python/lib/python3.11/site-packages
pip install -t layers/python/lib/python3.11/site-packages pyodbc pydantic
cd layers && zip -r odbc-dependencies.zip . && cd ..
aws s3 cp layers/odbc-dependencies.zip s3://lambda-layers-${AWS_ACCOUNT_ID}-${AWS_REGION}/layers/
```

### Alarms Not Triggering

```bash
# Verify SNS topic subscription
aws sns list-subscriptions-by-topic \
    --topic-arn arn:aws:sns:us-east-1:ACCOUNT:recruitment-backend-alarms-prod

# Check alarm state
aws cloudwatch describe-alarms \
    --alarm-names recruitment-lambda-errors-prod \
    --region us-east-1
```

## 📊 CloudWatch Monitoring

### Available Metrics

- **Lambda**: Invocations, Errors, Duration (avg, p99), Throttles
- **API Gateway**: Count, 4xx/5xx Errors, Latency (avg, p99)
- **Custom Logs**: Structured JSON logs with requestId correlation

### Create Custom Dashboards

```bash
# Dashboard is auto-created by template
# View at: https://console.aws.amazon.com/cloudwatch/

# Customize via CLI:
aws cloudwatch put-dashboard \
    --dashboard-name custom-recruitment-dashboard \
    --dashboard-body file://dashboard.json
```

## 🔐 Security Best Practices

### Secrets Management

```bash
# Rotate database password
aws secretsmanager rotate-secret \
    --secret-id recruitment-backend/database/prod
```

### IAM Least Privilege

The template creates minimal IAM permissions:
- Lambda: VPC access + Secrets Manager read + CloudWatch Logs
- API Gateway: Lambda invoke only
- No S3, DynamoDB, or other service access

### Enable X-Ray Tracing

```bash
# View service map (auto-enabled in template)
# https://console.aws.amazon.com/xray/home?region=us-east-1#/service-map
```

## 📈 Scaling

### Lambda Concurrent Executions

```bash
# Configured in template: 100 reserved concurrent executions

# Adjust if needed:
aws lambda put-function-concurrency \
    --function-name recruitment-backend-prod \
    --reserved-concurrent-executions 200
```

### API Gateway Throttling

```bash
# Current: 10 req/s, 100 burst (configured in template)

# Adjust via AWS Console:
# API Gateway → Stage → Throttling & Caching
```

## 📞 Support

### View Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/recruitment-backend-prod --follow

# Specific time range
aws logs filter-log-events \
    --log-group-name /aws/lambda/recruitment-backend-prod \
    --start-time $(($(date +%s)*1000 - 3600000)) \
    --query 'events[*].[timestamp,message]'
```

### Lambda Insights

```bash
# Enable Lambda Insights for detailed monitoring
# Configured in template - view in CloudWatch Logs Insights
```

## 📚 Additional Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [CloudFormation User Guide](https://docs.aws.amazon.com/cloudformation/)

---

**Last Updated**: May 2026  
**Template Version**: 1.0  
**SAM Specification**: 2010-09-12
