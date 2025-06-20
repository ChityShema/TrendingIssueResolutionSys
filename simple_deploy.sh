#!/bin/bash

# Simplified Cloud Run deployment script

PROJECT_ID="hacker2025-team-98-dev"
REGION="us-central1"
SERVICE_NAME="trending-resolver"

echo "🚀 Simple Cloud Run Deployment"
echo "Project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📡 Enabling Cloud Run and Cloud Build APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Build and deploy in one step
echo "🌐 Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8501 \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
    echo "🌐 Service URL: $SERVICE_URL"
else
    echo "❌ Deployment failed"
    exit 1
fi