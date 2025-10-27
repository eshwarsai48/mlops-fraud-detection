pipeline {
  agent any

  environment {
    ACR_NAME = "mlopsdevacr2025"
    IMAGE_NAME = "fraud-api"
    IMAGE_TAG = "latest"
    REGISTRY = "${ACR_NAME}.azurecr.io"
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

    stage('Build Docker image') {
      steps {
        script {
          echo "Building Docker image..."
          sh "docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
        }
      }
    }

    stage('Login to ACR') {
      steps {
        script {
          withCredentials([usernamePassword(credentialsId: 'acr-creds',
                                            usernameVariable: 'ACR_USER',
                                            passwordVariable: 'ACR_PASS')]) {
            sh 'echo $ACR_PASS | docker login ${REGISTRY} -u $ACR_USER --password-stdin'
          }
        }
      }
    }

    stage('Push image to ACR') {
      steps {
        echo "Pushing image ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        sh "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
      }
    }

    stage('Deploy to AKS via Helm') {
      steps {
        script {
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
