.PHONY: help build deploy deploy-dev deploy-staging deploy-prod validate test test-integration clean logs dashboard delete-stack

# Default target
.DEFAULT_GOAL := help

# Variables
ENVIRONMENT ?= prod
PROFILE ?= default
REGION ?= us-east-1
STACK_NAME ?= recruitment-backend-$(ENVIRONMENT)

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Recruitment Backend Infrastructure - Makefile Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Build:$(NC)"
	@echo "  make build                  Build SAM application"
	@echo "  make build-layer            Build ODBC Lambda layer"
	@echo ""
	@echo "$(YELLOW)Deploy:$(NC)"
	@echo "  make deploy [ENVIRONMENT=prod]  Deploy to specific environment"
	@echo "  make deploy-dev             Deploy to development"
	@echo "  make deploy-staging         Deploy to staging"
	@echo "  make deploy-prod            Deploy to production"
	@echo "  make deploy-guided          Deploy with guided prompts"
	@echo ""
	@echo "$(YELLOW)Validation & Testing:$(NC)"
	@echo "  make validate               Validate SAM template"
	@echo "  make test                   Run unit tests"
	@echo "  make test-integration       Run integration tests"
	@echo "  make test-api               Test API endpoints"
	@echo ""
	@echo "$(YELLOW)Monitoring:$(NC)"
	@echo "  make logs [ENVIRONMENT=prod]    Tail Lambda logs"
	@echo "  make dashboard [ENVIRONMENT=prod]  Open CloudWatch dashboard"
	@echo "  make alarms [ENVIRONMENT=prod]  List alarms"
	@echo ""
	@echo "$(YELLOW)Cleanup:$(NC)"
	@echo "  make clean                  Remove build artifacts"
	@echo "  make delete-stack [ENVIRONMENT=prod]  Delete CloudFormation stack"
	@echo ""
	@echo "$(YELLOW)Utilities:$(NC)"
	@echo "  make outputs [ENVIRONMENT=prod]  Show stack outputs"
	@echo "  make status [ENVIRONMENT=prod]   Show stack status"
	@echo ""
	@echo "$(YELLOW)Options:$(NC)"
	@echo "  ENVIRONMENT=dev|staging|prod  (default: prod)"
	@echo "  PROFILE=profile_name           AWS profile (default: default)"
	@echo "  REGION=region_name             AWS region (default: us-east-1)"
	@echo ""

# ============================================================================
# Build Targets
# ============================================================================

build: ## Build SAM application
	@echo "$(BLUE)Building SAM application...$(NC)"
	sam build --use-container --profile $(PROFILE)
	@echo "$(GREEN)✓ Build successful$(NC)"

build-layer: ## Build ODBC Lambda layer
	@echo "$(BLUE)Building ODBC Lambda layer...$(NC)"
	@mkdir -p layers/python/lib/python3.11/site-packages
	@echo "Installing Python dependencies..."
	pip install -t layers/python/lib/python3.11/site-packages \
		pyodbc pydantic email-validator > /dev/null 2>&1
	@echo "Creating ZIP archive..."
	@cd layers && zip -q -r odbc-dependencies.zip . && cd ..
	@echo "$(GREEN)✓ Layer built: layers/odbc-dependencies.zip$(NC)"

# ============================================================================
# Deployment Targets
# ============================================================================

deploy: validate build ## Deploy to specified environment
	@echo "$(BLUE)Deploying to $(ENVIRONMENT) environment...$(NC)"
	sam deploy \
		--config-env $(ENVIRONMENT) \
		--profile $(PROFILE) \
		--no-confirm-changeset
	@echo "$(GREEN)✓ Deployment successful$(NC)"
	@$(MAKE) outputs ENVIRONMENT=$(ENVIRONMENT)

deploy-dev: ## Deploy to development
	@$(MAKE) deploy ENVIRONMENT=dev

deploy-staging: ## Deploy to staging
	@$(MAKE) deploy ENVIRONMENT=staging

deploy-prod: ## Deploy to production
	@$(MAKE) deploy ENVIRONMENT=prod

deploy-guided: validate build ## Deploy with guided prompts
	@echo "$(BLUE)Starting guided deployment...$(NC)"
	sam deploy --guided --profile $(PROFILE) --config-env $(ENVIRONMENT)

# ============================================================================
# Validation & Testing
# ============================================================================

validate: ## Validate SAM template
	@echo "$(BLUE)Validating SAM template...$(NC)"
	sam validate --template infrastructure/template.yaml
	@echo "$(GREEN)✓ Template is valid$(NC)"

test: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	python -m pytest tests/test_handlers.py -v --cov=lambda_function --cov-report=term-missing
	@echo "$(GREEN)✓ Tests completed$(NC)"

test-integration: ## Run integration tests (requires deployed API)
	@echo "$(BLUE)Running API integration tests...$(NC)"
	@API_URL=$$(make outputs ENVIRONMENT=$(ENVIRONMENT) 2>/dev/null | grep "API URL:" | cut -d' ' -f3); \
	if [ -z "$$API_URL" ]; then \
		echo "$(RED)Error: Could not retrieve API URL$(NC)"; \
		exit 1; \
	fi; \
	chmod +x infrastructure/test-api.sh && \
	infrastructure/test-api.sh $$API_URL $(ENVIRONMENT)

test-api: test-integration ## Alias for test-integration

# ============================================================================
# Monitoring Targets
# ============================================================================

logs: ## Tail Lambda logs
	@echo "$(BLUE)Tailing Lambda logs for $(ENVIRONMENT)...$(NC)"
	@LOG_GROUP=$$(aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--profile $(PROFILE) \
		--region $(REGION) \
		--query 'Stacks[0].Outputs[?OutputKey==\`CloudWatchLogGroup\`].OutputValue' \
		--output text); \
	aws logs tail $$LOG_GROUP --follow --profile $(PROFILE) --region $(REGION)

dashboard: ## Open CloudWatch dashboard in browser
	@echo "$(BLUE)Opening CloudWatch dashboard...$(NC)"
	@REGION=$$(aws configure get region --profile $(PROFILE) || echo "us-east-1"); \
	open "https://console.aws.amazon.com/cloudwatch/home?region=$$REGION#dashboards:name=recruitment-backend-$(ENVIRONMENT)" || \
	xdg-open "https://console.aws.amazon.com/cloudwatch/home?region=$$REGION#dashboards:name=recruitment-backend-$(ENVIRONMENT)" || \
	echo "Visit: https://console.aws.amazon.com/cloudwatch/home?region=$$REGION#dashboards:name=recruitment-backend-$(ENVIRONMENT)"

alarms: ## List CloudWatch alarms
	@echo "$(BLUE)CloudWatch Alarms for $(ENVIRONMENT):$(NC)"
	@aws cloudwatch describe-alarms \
		--region $(REGION) \
		--profile $(PROFILE) \
		--query "MetricAlarms[?contains(AlarmName, '$(ENVIRONMENT)')].{Name:AlarmName,State:StateValue,Threshold:Threshold}" \
		--output table

# ============================================================================
# Cleanup Targets
# ============================================================================

clean: ## Remove build artifacts
	@echo "$(BLUE)Cleaning up build artifacts...$(NC)"
	rm -rf .aws-sam/
	rm -rf build/
	rm -rf layers/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

delete-stack: ## Delete CloudFormation stack (CAREFUL!)
	@echo "$(YELLOW)WARNING: This will delete the entire stack for $(ENVIRONMENT)$(NC)"
	@echo "Stack: $(STACK_NAME)"
	@read -p "Are you sure? (yes/no): " CONFIRM; \
	if [ "$$CONFIRM" = "yes" ]; then \
		echo "$(BLUE)Deleting stack...$(NC)"; \
		aws cloudformation delete-stack \
			--stack-name $(STACK_NAME) \
			--profile $(PROFILE) \
			--region $(REGION); \
		echo "$(GREEN)✓ Stack deletion initiated$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

# ============================================================================
# Utility Targets
# ============================================================================

outputs: ## Display stack outputs
	@echo "$(BLUE)Stack Outputs for $(STACK_NAME):$(NC)"
	@echo ""
	@aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--profile $(PROFILE) \
		--region $(REGION) \
		--query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' \
		--output table || echo "$(RED)Stack not found$(NC)"

status: ## Display stack status
	@echo "$(BLUE)Stack Status for $(STACK_NAME):$(NC)"
	@aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME) \
		--profile $(PROFILE) \
		--region $(REGION) \
		--query 'Stacks[0].{StackStatus:StackStatus,CreationTime:CreationTime,LastUpdatedTime:LastUpdatedTime}' \
		--output table || echo "$(RED)Stack not found$(NC)"

info: outputs status ## Display stack information and status

# ============================================================================
# Development Targets
# ============================================================================

.PHONY: format lint docs

format: ## Format Python code
	@echo "$(BLUE)Formatting Python code...$(NC)"
	black lambda_function.py tests/
	@echo "$(GREEN)✓ Formatting complete$(NC)"

lint: ## Lint Python code
	@echo "$(BLUE)Linting Python code...$(NC)"
	python -m pylint lambda_function.py --disable=all --enable=E,F
	@echo "$(GREEN)✓ Linting complete$(NC)"

# ============================================================================
# Quick Deploy Targets
# ============================================================================

.PHONY: quick-deploy quick-dev quick-staging quick-prod

quick-deploy: clean validate build deploy ## Quick deploy to specified environment
	@echo "$(GREEN)✓ Quick deploy complete$(NC)"

quick-dev: ## Quick deploy to dev
	@$(MAKE) quick-deploy ENVIRONMENT=dev

quick-staging: ## Quick deploy to staging
	@$(MAKE) quick-deploy ENVIRONMENT=staging

quick-prod: ## Quick deploy to prod
	@$(MAKE) quick-deploy ENVIRONMENT=prod

# ============================================================================
# Comprehensive Targets
# =============================================================================

.PHONY: full-test full-deploy

full-test: test test-integration ## Run all tests
	@echo "$(GREEN)✓ All tests passed$(NC)"

full-deploy: clean build deploy test-integration ## Build, deploy, and test
	@echo "$(GREEN)✓ Full deployment complete$(NC)"

# ============================================================================
# Default Help
# ============================================================================

.PHONY: version check-tools

version: ## Show versions of tools
	@echo "$(BLUE)Tool Versions:$(NC)"
	@echo "  AWS CLI: $$(aws --version)"
	@echo "  SAM CLI: $$(sam --version)"
	@echo "  Python: $$(python3 --version)"

check-tools: ## Check if required tools are installed
	@echo "$(BLUE)Checking required tools...$(NC)"
	@command -v aws >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) AWS CLI" || echo "$(RED)✗$(NC) AWS CLI not found"
	@command -v sam >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) SAM CLI" || echo "$(RED)✗$(NC) SAM CLI not found"
	@command -v python3 >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) Python 3" || echo "$(RED)✗$(NC) Python 3 not found"
	@command -v pip >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) pip" || echo "$(RED)✗$(NC) pip not found"

all: check-tools validate test build ## Run all checks and build
	@echo "$(GREEN)✓ All checks passed and build successful$(NC)"
