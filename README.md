# MLOps Fraud Detection Project

## Overview
This project is an **end-to-end MLOps pipeline** for a Fraud Detection machine learning model. 
It covers the entire lifecycle from **model training** to **deployment on Azure Kubernetes Service (AKS)**, 
including **monitoring with Prometheus & Azure Monitor** and **CI/CD with GitHub Actions**.

## Tech Stack
- **ML**: Python, scikit-learn, pandas, joblib
- **API**: FastAPI, Uvicorn
- **Containerization**: Docker
- **Infrastructure as Code**: Terraform
- **Configuration Management**: Ansible
- **Orchestration**: Kubernetes (AKS)
- **Deployment Management**: Helm
- **Monitoring**: Prometheus, Grafana, Azure Monitor
- **CI/CD**: GitHub Actions

## High-Level Flow
1. Train a fraud detection ML model
2. Serve it via a FastAPI inference service
4. Dockerize the API
Swagger UI → http://localhost:8000/docs
Healthcheck → http://localhost:8000/healthcheck
ReDoc → http://localhost:8000/
6. Provision infrastructure with Terraform
7. Deploy container to AKS using Helm
8. Monitor with Prometheus & Azure Monitor
9. Automate deployment with GitHub Actions
# 🧠 Fraud Detection MLOps Platform

Welcome to the **Fraud Detection MLOps Platform**, a production-ready cloud-native system that includes:

* **Azure Kubernetes Service (AKS)** for scalable deployment
* **Helm** for Kubernetes release management
* **Azure Container Registry (ACR)** for container storage
* **Jenkins / GitHub Actions** for CI/CD
* **Docker Buildx** for multi-architecture image builds
* **FastAPI** for real-time fraud prediction
* **Prometheus & Grafana** for monitoring and observability

This project follows a documentation structure inspired by top engineering organizations such as **Stripe**, **Airbnb**, **Coinbase**, and **Shopify**.

---

## 🏗️ System Architecture

A deep dive into the internal architecture: CI/CD, deployments, networking, pods, and observability.

👉 **[docs/architecture/mlops-system-architecture.md](docs/architecture/mlops-system-architecture.md)**

This includes:

* CI/CD pipeline flow
* Docker image creation using Buildx
* ACR storage and image retrieval
* Helm chart deployment
* AKS pods, services, ingress
* Prometheus + Grafana monitoring loop

---

## 🌐 User Request Flow

Shows how an external client interacts with the Fraud API—ideal for product teams and external consumers.

👉 **[docs/api/user-flow.md](docs/api/user-flow.md)**

This includes:

* `/predict` endpoint request lifecycle
* Ingress routing
* Service → Pod balancing
* Response path back to the user

---

## 📁 Project Structure

Below is the accurate structure extracted directly from the GitHub repository:

```
mlops-fraud-detection/
├── .github/                     # GitHub Actions workflows (CI/CD)
│
├── Infra/
│   └── terraform/               # Terraform IaC for AKS, ACR, Networking
│
├── Jenkins/                     # Jenkins pipeline files, Kaniko integration
│
├── K8S/                         # Raw Kubernetes manifests (legacy / deprecated)
│
├── ML/                          # ML models, preprocessing, training artifacts
│
├── app/                         # FastAPI application source code
│
├── docs/
│   ├── architecture/            # System architecture documentation
│   │   ├── mlops-system-architecture.md
│   │   ├── mlops-system-architecture.png
│   │   └── mlops-system-architecture.drawio
│   │
│   └── api/                     # User request flow documentation
│       ├── user-flow.md
│       ├── user-flow.png
│       └── user-flow.drawio
│
├── helm/                        # Helm chart for fraud-api deployment
│
├── Dockerfile                   # Container build definition
├── Jenkinsfile                  # CI/CD pipeline for Jenkins
├── gunicorn_conf.py             # Gunicorn configuration for FastAPI
├── ingress-controller-svc.yaml  # Ingress controller configuration (manual apply)
├── jenkins-pvc-backup.yaml      # Jenkins PVC backup configuration
├── requirements.txt             # Python package dependencies
├── environment.yml              # Conda environment definition
├── .dockerignore
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

1. Clone the repository
2. Build and push your Docker image using Buildx
3. Deploy using Helm
4. Monitor using Grafana dashboards

---

## 📊 Monitoring & Observability

* **Prometheus** scrapes metrics from the FastAPI `/metrics` endpoint
* **Grafana** visualizes dashboards & alerts

---

## 🤝 Contributing

Contributions are welcome! Please open a PR to propose improvements.

---

## 📄 License

MIT License