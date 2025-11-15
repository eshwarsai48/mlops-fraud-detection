# 🌐 User Request Flow (Fraud API)

This document explains how a user request flows through the Fraud Detection platform —
from the moment a client hits the public API endpoint to the final JSON response.

---

## 📘 User Flow Diagram

![User Flow](user-flow.png)

The diagram illustrates the following sequence:

1. A user or external client sends a request to the **fraud API endpoint**  
2. The request reaches the **Ingress Controller**  
3. The Ingress forwards traffic to the internal **fraud-api Service**  
4. Kubernetes routes the request to one of the running **fraud-api Pods**  
5. The pod processes the request and returns a **JSON response** back through the same path

---

## 🔁 Flow Breakdown

### **1. User / Client**
The caller can be:
- A web frontend
- A mobile app
- A merchant backend
- A batch risk engine

They send an HTTPS request to:

