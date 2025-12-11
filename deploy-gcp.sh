#!/bin/bash
# GCP Cloud Run Deployment Script for Lex Fund Formation App
# Prerequisites: gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="us-central1"
BACKEND_SERVICE="lex-api"
FRONTEND_SERVICE="lex-frontend"

echo "🚀 Deploying Lex to GCP Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

# Build and deploy backend
echo ""
echo "🔧 Building and deploying backend..."
cd server
gcloud builds submit --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE --project=$PROJECT_ID
gcloud run deploy $BACKEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --project=$PROJECT_ID

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
echo "✅ Backend deployed: $BACKEND_URL"

# Build and deploy frontend with backend URL
echo ""
echo "🎨 Building and deploying frontend..."
cd ../client
gcloud builds submit \
    --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
    --project=$PROJECT_ID \
    --build-arg VITE_API_URL=$BACKEND_URL

gcloud run deploy $FRONTEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --project=$PROJECT_ID

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --project=$PROJECT_ID --format='value(status.url)')

echo ""
echo "🎉 Deployment complete!"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend:  $BACKEND_URL"
echo ""
echo "Share $FRONTEND_URL with your friend!"
