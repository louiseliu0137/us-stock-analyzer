#!/bin/bash

# Google Cloud One-Click Deployment Script
# 美股分析工具 Google Cloud 一键部署脚本

set -e

echo "=========================================="
echo "🚀 US Stock Analyzer - Google Cloud Deployment"
echo "=========================================="
echo ""

# 检查gcloud是否安装
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Step 1: 获取项目ID
echo "📋 Step 1: Project Configuration"
echo "=================================="
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project set. Run 'gcloud init' first"
    exit 1
fi
echo "✓ Project ID: $PROJECT_ID"
echo ""

# Step 2: 启用必要的API
echo "📋 Step 2: Enabling Required APIs"
echo "=================================="
echo "Enabling Cloud Functions API..."
gcloud services enable cloudfunctions.googleapis.com

echo "Enabling Cloud Scheduler API..."
gcloud services enable cloudscheduler.googleapis.com

echo "Enabling Cloud Logging API..."
gcloud services enable logging.googleapis.com

echo "Enabling Cloud Build API..."
gcloud services enable cloudbuild.googleapis.com

echo "✓ All APIs enabled"
echo ""

# Step 3: 获取Cloud Function URL
echo "📋 Step 3: Deploying Cloud Function"
echo "=================================="
echo "Deploying analyze_market function..."

REGION="us-central1"

# 部署Cloud Function
gcloud functions deploy analyze_market \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point analyze_market \
  --source . \
  --set-env-vars GMAIL_ADDRESS="louise.sinorich@gmail.com",GMAIL_PASSWORD="fyyxoupgygiescye",RECIPIENT_EMAIL="liuchujun137@icloud.com" \
  --timeout=540 \
  --memory=512MB \
  --region=$REGION

FUNCTION_URL="https://${REGION}-${PROJECT_ID}.cloudfunctions.net/analyze_market"
echo "✓ Cloud Function deployed"
echo "  URL: $FUNCTION_URL"
echo ""

# Step 4: 创建Scheduler任务
echo "📋 Step 4: Creating Cloud Scheduler Jobs"
echo "=================================="

# 检查任务是否已存在，如果存在则删除
echo "Checking for existing scheduler jobs..."
if gcloud scheduler jobs describe premarket-analysis --location=$REGION &>/dev/null; then
    echo "Deleting existing premarket-analysis job..."
    gcloud scheduler jobs delete premarket-analysis --location=$REGION --quiet
fi

if gcloud scheduler jobs describe postmarket-analysis --location=$REGION &>/dev/null; then
    echo "Deleting existing postmarket-analysis job..."
    gcloud scheduler jobs delete postmarket-analysis --location=$REGION --quiet
fi

# 创建盘前分析任务
echo "Creating premarket-analysis job..."
gcloud scheduler jobs create http premarket-analysis \
  --schedule="0 21 * * 1-5" \
  --timezone="Asia/Shanghai" \
  --uri="${FUNCTION_URL}?type=premarket" \
  --http-method=GET \
  --location=$REGION

echo "✓ Premarket analysis job created"
echo "  Schedule: 北京时间每个交易日 21:00"
echo ""

# 创建收盘分析任务
echo "Creating postmarket-analysis job..."
gcloud scheduler jobs create http postmarket-analysis \
  --schedule="30 5 * * 1-5" \
  --timezone="Asia/Shanghai" \
  --uri="${FUNCTION_URL}?type=postmarket" \
  --http-method=GET \
  --location=$REGION

echo "✓ Postmarket analysis job created"
echo "  Schedule: 北京时间每个交易日 05:30"
echo ""

# Step 5: 测试部署
echo "📋 Step 5: Testing Deployment"
echo "=================================="
echo "Testing Cloud Function..."

# 等待3秒让函数完全部署
sleep 3

RESPONSE=$(curl -s -X GET "${FUNCTION_URL}?type=postmarket")
echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "success"; then
    echo "✓ Cloud Function test passed!"
else
    echo "⚠️ Warning: Function response might indicate an issue"
fi
echo ""

# Step 6: 完成
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📊 Deployment Summary:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Function URL: $FUNCTION_URL"
echo ""
echo "📅 Scheduled Tasks:"
echo "  1. Premarket Analysis: 北京时间 21:00 (Mon-Fri)"
echo "  2. Postmarket Analysis: 北京时间 05:30 (Mon-Fri)"
echo ""
echo "📧 Email Configuration:"
echo "  From: louise.sinorich@gmail.com"
echo "  To: liuchujun137@icloud.com"
echo ""
echo "🔍 Next Steps:"
echo "  1. Check your iCloud mailbox for test email"
echo "  2. View logs: gcloud functions logs read analyze_market --limit=50"
echo "  3. Manual trigger: gcloud scheduler jobs run premarket-analysis --location=$REGION"
echo ""
echo "📞 Useful Commands:"
echo "  - View logs: gcloud functions logs read analyze_market --follow"
echo "  - List jobs: gcloud scheduler jobs list --location=$REGION"
echo "  - Pause job: gcloud scheduler jobs pause premarket-analysis --location=$REGION"
echo "  - Resume job: gcloud scheduler jobs resume premarket-analysis --location=$REGION"
echo "  - Delete job: gcloud scheduler jobs delete premarket-analysis --location=$REGION"
echo ""
