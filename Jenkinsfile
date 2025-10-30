pipeline {
  agent any

  environment {
    ACR_NAME   = "mlopsdevacr2025"
    IMAGE_NAME = "fraud-api"
    IMAGE_TAG  = "latest"
    REGISTRY   = "${ACR_NAME}.azurecr.io"
    CHART_PATH = "helm/fraud-api"
    RELEASE_NAME = "fraud-api"
    NAMESPACE = "default"
  }

  stages {
    stage('Checkout') {
      steps {
        echo "Pulling latest code from GitHub..."
        git branch: 'main', url: 'https://github.com/eshwarsai48/mlops-fraud-detection.git'
      }
    }

    stage('Build and Push Image with Kaniko') {
      agent { label 'kaniko' }
      steps {
        echo "Building and pushing Docker image with Kaniko..."
        sh """
          /kaniko/executor \
            --context ${WORKSPACE} \
            --dockerfile ${WORKSPACE}/Dockerfile \
            --destination ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
            --skip-tls-verify \
            --insecure
        """
      }
    }

    stage('Deploy to AKS via Helm') {
      agent any
      steps {
        echo "Deploying new image to AKS..."
        sh """
          helm upgrade --install ${RELEASE_NAME} ${CHART_PATH} \
            --namespace ${NAMESPACE} \
            --set image.repository=${REGISTRY}/${IMAGE_NAME} \
            --set image.tag=${IMAGE_TAG} \
            --set image.pullPolicy=Always
        """
      }
    }
  }

  post {
    success {
      echo "✅ Build and deployment successful!"
    }
    failure {
      echo "❌ Build or deployment failed. Check logs above."
    }
  }
}
