# Cloud Native DevOps Platform

A production-style DevOps project demonstrating a full CI/CD and cloud-native deployment pipeline — from a containerized FastAPI application through to Kubernetes and AWS EKS.

## What this project demonstrates

- Building and containerizing a Python REST API
- Automated testing, security scanning, and image publishing via CI/CD
- Deploying to Kubernetes (locally via Minikube, and to AWS via EKS)
- Managing cloud infrastructure as code with Terraform
- Monitoring and alerting with Prometheus and Grafana

## Tech stack

| Layer          | Tools                                  |
|----------------|-----------------------------------------|
| Application    | Python, FastAPI, SQLAlchemy             |
| Database       | PostgreSQL                              |
| Auth           | JWT (python-jose), bcrypt password hashing |
| Containers     | Docker, Docker Compose                  |
| Orchestration  | Kubernetes (Minikube for local, AWS EKS for cloud) |
| IaC            | Terraform (VPC, EKS cluster, node groups) |
| CI/CD          | GitHub Actions                          |
| Security       | Trivy (container image vulnerability scanning) |
| Monitoring     | Prometheus, Grafana, Alertmanager       |

## Features

- User registration and login with JWT-based authentication
- Password hashing with bcrypt
- Protected CRUD endpoints for user management
- Health check endpoint (/health) for Kubernetes probes

## Running locally with Docker Compose

docker-compose up --build

The API will be available at http://localhost:8000, with interactive docs at http://localhost:8000/docs.

### Try it out

1. Register a user via POST /register
2. Log in via POST /login to receive a JWT access token
3. Click Authorize in the Swagger UI and paste the token
4. Call protected endpoints like GET /me or GET /users/

## Running on Kubernetes (Minikube)

minikube start
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

Check status:

kubectl get pods
kubectl get svc
kubectl get ingress

## Deploying infrastructure to AWS with Terraform

cd terraform
terraform init
terraform plan
terraform apply

This provisions a VPC and an EKS cluster in AWS. After the cluster is up, install the required EKS add-ons before deploying workloads:

aws eks create-addon --cluster-name <cluster-name> --addon-name vpc-cni --region <region>
aws eks create-addon --cluster-name <cluster-name> --addon-name kube-proxy --region <region>
aws eks create-addon --cluster-name <cluster-name> --addon-name coredns --region <region>

To tear down and avoid ongoing AWS charges:

terraform destroy

## CI/CD Pipeline

- CI (.github/workflows/ci.yml): runs on every push — installs dependencies, runs tests, builds the Docker image, scans it with Trivy, and pushes it to GitHub Container Registry (GHCR).
- CD (.github/workflows/cd.yml): triggers after a successful CI run and deploys the latest image to Kubernetes.

## Monitoring

Prometheus alert rules (monitoring/application-alerts.yaml) watch for:
- Pod availability (deployment down)
- Pods not ready
- High CPU usage
- Frequent pod restarts

## Project structure

app/ - FastAPI application code
k8s/ - Kubernetes manifests
terraform/ - AWS infrastructure as code
monitoring/ - Prometheus alert rules
tests/ - Application tests
.github/workflows/ - CI/CD pipelines

## Author

Milind Kapadnis