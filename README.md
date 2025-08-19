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
2. Wrap it in a FastAPI application
3. Dockerize the API
4. Provision infrastructure with Terraform
5. Deploy container to AKS using Helm
6. Monitor with Prometheus & Azure Monitor
7. Automate deployment with GitHub Actions

---
