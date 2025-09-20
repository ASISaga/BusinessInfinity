# Business Infinity Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying Business Infinity in various environments, from development to enterprise production deployments. The platform leverages Azure cloud services for scalable, reliable operations.

## Prerequisites

### System Requirements
- **Azure Subscription** with sufficient credits/budget
- **Azure CLI** version 2.40.0 or later
- **PowerShell** 7.0 or later
- **Node.js** 18.0 or later
- **Python** 3.9 or later
- **Git** for source code management

### Required Permissions
- **Azure Subscription Contributor** role
- **Azure Active Directory** application registration permissions
- **Azure OpenAI** service access
- **Key Vault** management permissions

### Service Quotas
Ensure your Azure subscription has sufficient quotas for:
- **Azure Functions**: Premium or Dedicated plan
- **Azure OpenAI**: Model deployment capacity
- **Azure Storage**: General Purpose v2 accounts
- **Azure App Service**: Standard or Premium plans

## Environment Setup

### 1. Clone Repository

```powershell
# Clone the main repository
git clone https://github.com/ASISaga/RealmOfAgents.git
cd RealmOfAgents\BusinessInfinity

# Initialize submodules if needed
git submodule update --init --recursive
```

### 2. Azure CLI Setup

```powershell
# Login to Azure
az login

# Set default subscription
az account set --subscription "Your-Subscription-ID"

# Install required extensions
az extension add --name application-insights
az extension add --name cognitiveservices
```

### 3. Environment Configuration

Create environment-specific configuration files:

```powershell
# Create environment configuration
copy .env.template .env.dev
copy .env.template .env.staging  
copy .env.template .env.prod
```

Edit each environment file with appropriate values:

```bash
# .env.dev example
ENVIRONMENT_NAME=dev
AZURE_LOCATION=eastus
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
RESOURCE_GROUP=rg-business-infinity-dev
```

## Development Deployment

### 1. Local Development Setup

```powershell
# Install Python dependencies
cd server
pip install .

# Install Node.js dependencies for frontend
cd ..\businessinfinity.asisaga.com
npm install

# Start local development servers
cd ..\server
python main.py

# In another terminal, start frontend
cd businessinfinity.asisaga.com
npm run dev
```

### 2. Azure Development Environment

```powershell
# Create resource group
az group create --name rg-business-infinity-dev --location eastus

# Deploy infrastructure
az deployment group create `
  --resource-group rg-business-infinity-dev `
  --template-file infra\main.bicep `
  --parameters environmentName=dev `
  --parameters location=eastus `
  --parameters @dev-parameters.json
```

## Staging Deployment

### 1. Infrastructure Deployment

```powershell
# Create staging resource group
az group create --name rg-business-infinity-staging --location eastus

# Deploy staging infrastructure
az deployment group create `
  --resource-group rg-business-infinity-staging `
  --template-file infra\main.bicep `
  --parameters environmentName=staging `
  --parameters location=eastus `
  --parameters @staging-parameters.json
```

### 2. Application Deployment

```powershell
# Build and deploy Function Apps
cd azure-functions

# Deploy summarization pipeline
func azure functionapp publish func-bi-summarization-staging --python

# Deploy fine-tuning pipeline  
func azure functionapp publish func-bi-finetuning-staging --python

# Deploy operations agents
func azure functionapp publish func-bi-operations-staging --python
```

### 3. Configuration Management

```powershell
# Update application settings
az functionapp config appsettings set `
  --name func-bi-operations-staging `
  --resource-group rg-business-infinity-staging `
  --settings @staging-appsettings.json
```

## Production Deployment

### 1. Production Infrastructure

```powershell
# Create production resource group
az group create --name rg-business-infinity-prod --location eastus

# Deploy production infrastructure with high availability
az deployment group create `
  --resource-group rg-business-infinity-prod `
  --template-file infra\main.bicep `
  --parameters environmentName=prod `
  --parameters location=eastus `
  --parameters enableHighAvailability=true `
  --parameters @prod-parameters.json
```

### 2. Security Configuration

```powershell
# Configure Key Vault access policies
az keyvault set-policy `
  --name kv-business-infinity-prod `
  --object-id <function-app-principal-id> `
  --secret-permissions get list

# Configure network security
az functionapp config access-restriction add `
  --name func-bi-operations-prod `
  --resource-group rg-business-infinity-prod `
  --rule-name "AllowVNet" `
  --priority 100 `
  --vnet-name vnet-business-infinity `
  --subnet-name subnet-functions
```

### 3. SSL/TLS Configuration

```powershell
# Configure custom domain and SSL
az functionapp config hostname add `
  --webapp-name func-bi-operations-prod `
  --resource-group rg-business-infinity-prod `
  --hostname api.businessinfinity.asisaga.com

# Bind SSL certificate
az functionapp config ssl bind `
  --certificate-thumbprint <cert-thumbprint> `
  --ssl-type SNI `
  --name func-bi-operations-prod `
  --resource-group rg-business-infinity-prod
```

## Multi-Region Deployment

### 1. Primary Region Setup

```powershell
# Deploy to primary region (East US)
az deployment group create `
  --resource-group rg-business-infinity-prod-eastus `
  --template-file infra\main.bicep `
  --parameters environmentName=prod `
  --parameters location=eastus `
  --parameters isPrimaryRegion=true
```

### 2. Secondary Region Setup

```powershell
# Deploy to secondary region (West US)
az deployment group create `
  --resource-group rg-business-infinity-prod-westus `
  --template-file infra\main.bicep `
  --parameters environmentName=prod `
  --parameters location=westus `
  --parameters isPrimaryRegion=false `
  --parameters primaryRegionResourceGroup=rg-business-infinity-prod-eastus
```

### 3. Global Load Balancer

```powershell
# Create Traffic Manager profile
az network traffic-manager profile create `
  --name tm-business-infinity `
  --resource-group rg-business-infinity-global `
  --routing-method Priority `
  --unique-dns-name business-infinity-global

# Add endpoints
az network traffic-manager endpoint create `
  --name eastus-endpoint `
  --profile-name tm-business-infinity `
  --resource-group rg-business-infinity-global `
  --type azureEndpoints `
  --target-resource-id <eastus-function-app-id> `
  --priority 1
```

## Database Migration

### 1. Schema Deployment

```powershell
# Deploy database schema
sqlcmd -S "sql-business-infinity-prod.database.windows.net" `
       -d "BusinessInfinityDB" `
       -U "admin-user" `
       -P "secure-password" `
       -i "database\schema.sql"
```

### 2. Data Migration

```powershell
# Run data migration scripts
python scripts\migrate-data.py `
  --source-env staging `
  --target-env production `
  --verify-only false
```

## Monitoring and Logging Setup

### 1. Application Insights Configuration

```powershell
# Configure Application Insights
az monitor app-insights component create `
  --app business-infinity-insights `
  --location eastus `
  --resource-group rg-business-infinity-prod `
  --application-type web
```

### 2. Log Analytics Workspace

```powershell
# Create Log Analytics workspace
az monitor log-analytics workspace create `
  --resource-group rg-business-infinity-prod `
  --workspace-name law-business-infinity `
  --location eastus
```

### 3. Alerts and Notifications

```powershell
# Create alert rules
az monitor metrics alert create `
  --name "High Error Rate" `
  --resource-group rg-business-infinity-prod `
  --scopes <function-app-resource-id> `
  --condition "avg exceptions/requests > 0.05" `
  --action <action-group-id>
```

## CI/CD Pipeline Setup

### 1. Azure DevOps Pipeline

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
    - main
    - develop

variables:
  - group: business-infinity-variables

stages:
- stage: Build
  jobs:
  - job: BuildAndTest
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.9'
    - script: |
  pip install .
        python -m pytest tests/
      displayName: 'Install dependencies and run tests'

- stage: Deploy
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToProduction
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureFunctionApp@1
            inputs:
              azureSubscription: '$(azureSubscription)'
              appType: 'functionAppLinux'
              appName: '$(functionAppName)'
              package: '$(Pipeline.Workspace)/drop/function-app.zip'
```

### 2. GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Business Infinity

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install .
    - name: Run tests
      run: |
        python -m pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    - name: Deploy to Azure Functions
      uses: azure/functions-action@v1
      with:
        app-name: 'func-business-infinity-prod'
        package: './azure-functions'
```

## Backup and Disaster Recovery

### 1. Automated Backups

```powershell
# Configure automated backups
az backup vault create `
  --name vault-business-infinity `
  --resource-group rg-business-infinity-prod `
  --location eastus

# Configure database backup
az sql db export `
  --name BusinessInfinityDB `
  --server sql-business-infinity-prod `
  --resource-group rg-business-infinity-prod `
  --storage-key-type StorageAccessKey `
  --storage-key <storage-key> `
  --storage-uri "https://storage.blob.core.windows.net/backups/db-backup.bacpac"
```

### 2. Disaster Recovery Plan

```powershell
# Create disaster recovery runbook
az automation runbook create `
  --name "DisasterRecoveryPlan" `
  --resource-group rg-business-infinity-prod `
  --automation-account-name auto-business-infinity `
  --type PowerShell
```

## Performance Optimization

### 1. Function App Scaling

```powershell
# Configure auto-scaling
az functionapp plan update `
  --name plan-business-infinity-prod `
  --resource-group rg-business-infinity-prod `
  --max-burst 100 `
  --sku EP2
```

### 2. CDN Configuration

```powershell
# Create CDN profile and endpoint
az cdn profile create `
  --name cdn-business-infinity `
  --resource-group rg-business-infinity-prod `
  --sku Standard_Microsoft

az cdn endpoint create `
  --name business-infinity-api `
  --profile-name cdn-business-infinity `
  --resource-group rg-business-infinity-prod `
  --origin api.businessinfinity.asisaga.com
```

## Security Hardening

### 1. Network Security

```powershell
# Create virtual network
az network vnet create `
  --name vnet-business-infinity `
  --resource-group rg-business-infinity-prod `
  --subnet-name subnet-functions `
  --address-prefix 10.0.0.0/16 `
  --subnet-prefix 10.0.1.0/24
```

### 2. Identity and Access Management

```powershell
# Create managed identity
az identity create `
  --name id-business-infinity `
  --resource-group rg-business-infinity-prod

# Assign roles
az role assignment create `
  --assignee <managed-identity-principal-id> `
  --role "Key Vault Secrets User" `
  --scope <key-vault-resource-id>
```

## Troubleshooting

### Common Deployment Issues

1. **Insufficient Permissions**
   ```powershell
   # Check current permissions
   az role assignment list --assignee <your-user-id>
   ```

2. **Resource Quota Exceeded**
   ```powershell
   # Check current usage
   az vm list-usage --location eastus
   ```

3. **Function App Deployment Failures**
   ```powershell
   # Check deployment logs
   az functionapp log download --name <function-app-name> --resource-group <rg-name>
   ```

### Log Analysis

```powershell
# Query Application Insights
az monitor app-insights query `
  --app business-infinity-insights `
  --analytics-query "requests | where timestamp > ago(1h) | summarize count() by resultCode"
```

## Post-Deployment Verification

### 1. Health Checks

```powershell
# Verify Function Apps are running
az functionapp show --name func-bi-operations-prod --resource-group rg-business-infinity-prod --query "state"

# Test API endpoints
Invoke-RestMethod -Uri "https://api.businessinfinity.asisaga.com/health" -Method GET
```

### 2. Performance Testing

```powershell
# Run load tests
az load test create `
  --name "bi-load-test" `
  --resource-group rg-business-infinity-prod `
  --test-plan-file "tests/load-test-plan.jmx"
```

## Maintenance Procedures

### 1. Regular Updates

```powershell
# Update Function App runtime
az functionapp config set `
  --name func-bi-operations-prod `
  --resource-group rg-business-infinity-prod `
  --python-version "3.10"
```

### 2. Security Patches

```powershell
# Update Key Vault certificates
az keyvault certificate import `
  --vault-name kv-business-infinity-prod `
  --name ssl-certificate `
  --file certificate.pfx
```

This deployment guide ensures a robust, secure, and scalable deployment of Business Infinity across all environments.
