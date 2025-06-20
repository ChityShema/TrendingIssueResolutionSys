#!/bin/bash

# Cloud deployment script for Trending Issue Resolver

PROJECT_ID="hacker2025-team-98-dev"
REGION="us-central1"
SERVICE_NAME="trending-resolver"
BUCKET_NAME="trending-resolver-bucket"

echo "🚀 Deploying Trending Issue Resolver to Google Cloud"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable datastore.googleapis.com

# Create storage bucket if it doesn't exist
echo "🪣 Creating storage bucket..."
gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME 2>/dev/null || echo "Bucket already exists"

# Skip Python package build - using Docker instead
echo "📦 Skipping Python package build (using Docker)..."

# Skip Vertex AI deployment for now - focus on Cloud Run
echo "🤖 Skipping Vertex AI deployment (focusing on Cloud Run)..."

# Build and deploy dashboard to Cloud Run
echo "🌐 Building Docker image..."
if ! gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME; then
    echo "❌ Docker build failed. Checking for common issues..."
    echo "Verifying Dockerfile exists..."
    ls -la Dockerfile
    echo "Checking Cloud Build API status..."
    gcloud services list --enabled --filter="name:cloudbuild.googleapis.com"
    exit 1
fi

echo "✅ Docker image built successfully"
echo "🚀 Deploying to Cloud Run..."

if ! gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8501 \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID; then
    echo "❌ Cloud Run deployment failed"
    exit 1
fi

echo "✅ Deployment completed!"
echo "Dashboard URL: https://$SERVICE_NAME-$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' | cut -d'/' -f3)"