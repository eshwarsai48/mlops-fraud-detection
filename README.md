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
Swagger UI → http://localhost:8000/docs
Healthcheck → http://localhost:8000/healthcheck
4. Dockerize the API
5. Provision infrastructure with Terraform
6. Deploy container to AKS using Helm
7. Monitor with Prometheus & Azure Monitor
8. Automate deployment with GitHub Actions

---
