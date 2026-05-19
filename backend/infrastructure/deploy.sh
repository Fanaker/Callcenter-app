#!/bin/bash

################################################################################
# Recruitment Backend - SAM Deployment Script
# Automates build and deployment of infrastructure
# Usage: ./deploy.sh [dev|staging|prod] [--guided] [--no-confirm]
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-prod}
GUIDED=false
NO_CONFIRM=false
PROFILE="default"

# Parse arguments
for arg in "$@"; do
    case $arg in
        dev|staging|prod)
            ENVIRONMENT=$arg
            ;;
        --guided)
            GUIDED=true
            ;;
        --no-confirm)
            NO_CONFIRM=true
            ;;
        --profile)
            PROFILE=$2
            shift 2
            ;;
        --help)
            echo "Usage: ./deploy.sh [dev|staging|prod] [OPTIONS]"
            echo ""
            echo "Arguments:"
            echo "  dev|staging|prod    Environment to deploy (default: prod)"
            echo ""
            echo "Options:"
            echo "  --guided            Run with guided prompts"
            echo "  --no-confirm        Skip changeset confirmation"
            echo "  --profile PROFILE   AWS profile to use (default: default)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg"
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}❌ Invalid environment: $ENVIRONMENT${NC}"
    echo "Must be: dev, staging, or prod"
    exit 1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Recruitment Backend SAM Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
echo -e "Profile: ${GREEN}$PROFILE${NC}"
echo -e "Guided Mode: ${GREEN}${GUIDED:-false}${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    echo "  https://aws.amazon.com/cli/"
    exit 1
fi
echo -e "${GREEN}✓${NC} AWS CLI found: $(aws --version)"

# Check SAM CLI
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI not found. Please install it first.${NC}"
    echo "  pip install aws-sam-cli"
    exit 1
fi
echo -e "${GREEN}✓${NC} SAM CLI found: $(sam --version)"

# Check Python
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}❌ Python 3.11 not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3.11 found: $(python3.11 --version)"

# Verify AWS credentials
echo ""
echo -e "${YELLOW}🔐 Verifying AWS credentials...${NC}"
if ! aws sts get-caller-identity --profile "$PROFILE" &> /dev/null; then
    echo -e "${RED}❌ Failed to authenticate with AWS profile: $PROFILE${NC}"
    echo "   Run: aws configure --profile $PROFILE"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --profile "$PROFILE" --query Account --output text)
REGION=$(aws configure get region --profile "$PROFILE" || echo "us-east-1")

echo -e "${GREEN}✓${NC} AWS Account: $ACCOUNT_ID"
echo -e "${GREEN}✓${NC} AWS Region: $REGION"

# Verify S3 bucket
echo ""
echo -e "${YELLOW}📦 Verifying S3 bucket...${NC}"
S3_BUCKET="lambda-layers-${ACCOUNT_ID}-${REGION}"

if aws s3 ls "s3://$S3_BUCKET" --profile "$PROFILE" &> /dev/null; then
    echo -e "${GREEN}✓${NC} S3 bucket exists: $S3_BUCKET"
else
    echo -e "${YELLOW}⚠${NC} S3 bucket not found: $S3_BUCKET"
    read -p "Create bucket? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Creating S3 bucket...${NC}"
        aws s3 mb "s3://$S3_BUCKET" --region "$REGION" --profile "$PROFILE"
        echo -e "${GREEN}✓${NC} Bucket created"
    else
        echo -e "${RED}❌ Cannot proceed without S3 bucket${NC}"
        exit 1
    fi
fi

# Verify ODBC layer
echo ""
echo -e "${YELLOW}🔧 Checking ODBC layer...${NC}"
if aws s3 ls "s3://$S3_BUCKET/layers/odbc-dependencies.zip" --profile "$PROFILE" &> /dev/null; then
    echo -e "${GREEN}✓${NC} ODBC layer found in S3"
else
    echo -e "${YELLOW}⚠${NC} ODBC layer not found in S3${NC}"
    read -p "Build and upload ODBC layer? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Building ODBC layer...${NC}"

        # Clean previous build
        rm -rf layers/
        mkdir -p layers/python/lib/python3.11/site-packages

        # Install dependencies
        echo "Installing dependencies..."
        pip install -t layers/python/lib/python3.11/site-packages pyodbc pydantic email-validator > /dev/null 2>&1

        # Create zip
        cd layers
        zip -r odbc-dependencies.zip . > /dev/null 2>&1
        cd ..

        # Upload to S3
        echo "Uploading to S3..."
        aws s3 cp layers/odbc-dependencies.zip "s3://$S3_BUCKET/layers/" --profile "$PROFILE"

        echo -e "${GREEN}✓${NC} ODBC layer uploaded"

        # Cleanup
        rm -rf layers/
    else
        echo -e "${RED}❌ Cannot proceed without ODBC layer${NC}"
        exit 1
    fi
fi

# Build SAM application
echo ""
echo -e "${YELLOW}🔨 Building SAM application...${NC}"
if sam build --profile "$PROFILE"; then
    echo -e "${GREEN}✓${NC} Build successful"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

# Deploy SAM application
echo ""
echo -e "${YELLOW}🚀 Deploying to $ENVIRONMENT environment...${NC}"

if [ "$GUIDED" = true ]; then
    # Guided deployment
    sam deploy \
        --guided \
        --profile "$PROFILE" \
        --config-env "$ENVIRONMENT" \
        --tags Environment="$ENVIRONMENT" Application="RecruitmentBackend"
else
    # Non-interactive deployment
    if [ "$NO_CONFIRM" = true ]; then
        sam deploy \
            --profile "$PROFILE" \
            --config-env "$ENVIRONMENT" \
            --no-confirm-changeset \
            --tags Environment="$ENVIRONMENT" Application="RecruitmentBackend"
    else
        sam deploy \
            --profile "$PROFILE" \
            --config-env "$ENVIRONMENT" \
            --tags Environment="$ENVIRONMENT" Application="RecruitmentBackend"
    fi
fi

# Get outputs
echo ""
echo -e "${YELLOW}📊 Retrieving stack outputs...${NC}"

STACK_NAME="recruitment-backend-${ENVIRONMENT}"

API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --profile "$PROFILE" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

LAMBDA_ARN=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --profile "$PROFILE" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionArn`].OutputValue' \
    --output text)

LOG_GROUP=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --profile "$PROFILE" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudWatchLogGroup`].OutputValue' \
    --output text)

# Display results
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Deployment successful!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📍 Stack Information:${NC}"
echo -e "  Stack Name: ${GREEN}$STACK_NAME${NC}"
echo -e "  Region: ${GREEN}$REGION${NC}"
echo -e "  Account: ${GREEN}$ACCOUNT_ID${NC}"
echo ""
echo -e "${YELLOW}🔗 Endpoints & Resources:${NC}"
echo -e "  API URL: ${GREEN}$API_URL${NC}"
echo -e "  Lambda ARN: ${GREEN}$LAMBDA_ARN${NC}"
echo -e "  Logs: ${GREEN}$LOG_GROUP${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "  1. Test the API:"
echo -e "     ${GREEN}curl -X GET \"$API_URL/v1/campanias/activas\"${NC}"
echo ""
echo "  2. View Lambda logs:"
echo -e "     ${GREEN}aws logs tail $LOG_GROUP --follow --profile $PROFILE${NC}"
echo ""
echo "  3. View monitoring dashboard:"
echo -e "     ${GREEN}https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:name=recruitment-backend-${ENVIRONMENT}${NC}"
echo ""
echo "  4. Check API Gateway:"
echo -e "     ${GREEN}https://console.aws.amazon.com/apigateway/main/apis?region=$REGION${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
