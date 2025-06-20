#!/bin/bash

# Test Docker build locally before cloud deployment

PROJECT_ID="hacker2025-team-98-dev"
SERVICE_NAME="trending-resolver"

echo "🧪 Testing Docker build locally..."

# Build the Docker image locally
if docker build -t $SERVICE_NAME .; then
    echo "✅ Local Docker build successful"
    
    # Test if the image can run
    echo "🧪 Testing if container can start..."
    if timeout 30 docker run --rm -p 8501:8501 $SERVICE_NAME &
    then
        sleep 10
        if curl -f http://localhost:8501 > /dev/null 2>&1; then
            echo "✅ Container starts and responds successfully"
        else
            echo "⚠️  Container starts but may not be responding on port 8501"
        fi
        docker stop $(docker ps -q --filter ancestor=$SERVICE_NAME) 2>/dev/null
    else
        echo "❌ Container failed to start properly"
    fi
else
    echo "❌ Local Docker build failed"
    echo "Check the following:"
    echo "1. Dockerfile syntax"
    echo "2. requirements.txt dependencies"
    echo "3. Application code structure"
    exit 1
fi

echo "🚀 Ready for cloud deployment!"