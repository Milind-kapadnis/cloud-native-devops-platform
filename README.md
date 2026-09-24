# Cloud Native DevOps Platform

A production-style DevOps project: a containerized FastAPI service taken through CI/CD, Kubernetes, monitoring and infrastructure as code (Terraform for AWS EKS).

## Architecture

~~~mermaid
flowchart LR
  Dev[Developer] -->|git push| GH[GitHub]
  GH --> CI[GitHub Actions CI - tests, build, Trivy scan]
  CI -->|image tagged with commit SHA| GHCR[(GHCR)]
  CI --> CD[CD on self-hosted runner]
  CD -->|kubectl apply| K8S
  subgraph K8S["Kubernetes - Minikube or EKS"]
    ING[Ingress] --> SVC[Service] --> APP[FastAPI Deployment + HPA]
    APP --> PG[(PostgreSQL + PVC)]
  end
  PROM[Prometheus] --> AM[Alertmanager]
  PROM --> GRAF[Grafana]
  PROM -.->|scrapes| K8S
  TF[Terraform] --> AWS[AWS VPC + EKS]
~~~

## Tech stack

| Layer | Tools |
|---|---|
| Application | Python, FastAPI, SQLAlchemy, Pydantic v2 |
| Database | PostgreSQL |
| Auth | JWT (python-jose), bcrypt password hashing |
| Containers | Docker, Docker Compose |
| Orchestration | Kubernetes (Minikube locally, AWS EKS in the cloud) |
| IaC | Terraform (VPC, EKS, node group) |
| CI/CD | GitHub Actions (self-hosted runner for the local cluster) |
| Security | Trivy image scanning, Kubernetes Secrets, NetworkPolicy |
| Monitoring | Prometheus, Grafana, Alertmanager (kube-prometheus-stack) |

## API

- `POST /register`, `POST /login` (returns a JWT), `GET /me`
- `GET /users/`, `GET/PUT/DELETE /users/{id}`: protected, and a user can only modify their own account
- `GET /health`: used for liveness and readiness probes
- Errors: 401 invalid credentials, 403 modifying another user, 404 unknown user, 400 duplicate username or email

## Run locally with Docker Compose

Secrets are read from a `.env` file that is never committed. Compose waits for the Postgres healthcheck before starting the API.

~~~bash
cp .env.example .env   # then set POSTGRES_PASSWORD and JWT_SECRET_KEY (e.g. openssl rand -hex 32)
docker compose up -d --build
~~~

The API is on http://localhost:8000 and the docs on http://localhost:8000/docs.

## Run on Kubernetes (Minikube)

Secrets are not stored in Git. Create them in the cluster first:

~~~bash
kubectl create secret generic app-secrets --from-literal=JWT_SECRET_KEY="$(openssl rand -hex 32)"
PGPASS=$(openssl rand -hex 16)
kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_USER=admin \
  --from-literal=POSTGRES_PASSWORD="$PGPASS" \
  --from-literal=POSTGRES_DB=devops_db \
  --from-literal=DATABASE_URL="postgresql://admin:${PGPASS}@postgres:5432/devops_db"
~~~

Apply the manifests in this order (Postgres must be ready before the API starts):

~~~bash
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/postgres.yaml
kubectl rollout status deployment/postgres
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml   # requires: minikube addons enable ingress
~~~

Check it:

~~~bash
kubectl port-forward service/cloud-native-devops-service 8000:8000
curl http://localhost:8000/health   # {"status":"healthy"}
~~~

`k8s/examples/postgres-secret.example.yaml` shows the shape of the Postgres secret with placeholder values. The real `k8s/postgres-secret.yaml` is git-ignored.

## Monitoring

Prometheus, Grafana and Alertmanager run in the `monitoring` namespace via the kube-prometheus-stack Helm chart, with trimmed resource limits (`monitoring/values.yaml`) so it fits on a small Minikube.

~~~bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
kubectl create namespace monitoring
kubectl create secret generic grafana-admin -n monitoring \
  --from-literal=admin-user=admin --from-literal=admin-password="$(openssl rand -hex 12)"
helm install monitoring prometheus-community/kube-prometheus-stack --version 91.5.1 \
  -n monitoring -f monitoring/values.yaml
kubectl apply -f monitoring/application-alerts.yaml
kubectl apply -f monitoring/dashboards/dashboard-configmap.yaml
~~~

- Alert rules (`monitoring/application-alerts.yaml`): deployment down, pods not ready, high CPU, frequent restarts. The firing and recovery cycle was tested by scaling the deployment to zero.
- The Grafana dashboard is code: `monitoring/dashboards/cloud-native-devops.json`, loaded through a labelled ConfigMap.
- Alertmanager has no notification receiver yet: alerts show up in Alertmanager but are not sent anywhere.

## CI/CD

- CI (`.github/workflows/ci.yml`): on every push it runs the tests against a Postgres service, builds the Docker image, scans it with Trivy (pinned to a commit SHA), and pushes it to GHCR tagged `latest` and with the commit SHA.
- CD (`.github/workflows/cd.yml`): runs after a successful CI run on `main`, on a self-hosted runner next to the local Minikube. It checks the cluster and secrets exist, applies the manifests in dependency order (waiting for Postgres), sets the deployment to the image of that exact commit SHA, waits for the rollout and checks `/health`. Only one deploy runs at a time.

## Security

- No secrets in Git: `JWT_SECRET_KEY` and `DATABASE_URL` have no fallback defaults, so the app refuses to start without them. Locally they come from `.env`, in Kubernetes from Secrets.
- Passwords are hashed with bcrypt, JWTs expire after 30 minutes, and users can only update or delete their own account.
- The container runs as a non-root user, and Python dependencies are pinned.
- Postgres has readiness and liveness probes, resource limits and a `Recreate` rollout strategy so two pods never share the volume.

## AWS EKS with Terraform

~~~bash
cd terraform
terraform init
terraform plan
terraform apply     # prints a ready-to-run `aws eks update-kubeconfig` command
terraform destroy   # tear everything down to stop AWS charges
~~~

Region, profile, cluster name, Kubernetes version and node instance type are variables (`terraform/variables.tf`). `terraform/backend.tf.example` shows S3 remote state with locking; it is not active until you create the bucket. The code passes `terraform validate`, but it has not been applied end to end (the cluster is kept off to avoid AWS cost). On EKS you still need to install the EBS CSI driver (for the Postgres volume), metrics-server (for the HPA) and ingress-nginx.

## Known limitations

- NetworkPolicy manifests are included, but Minikube's default network plugin does not enforce them (a pod without the app label could still reach Postgres). Enforcement needs a CNI such as Calico.
- Alertmanager has no notification receiver, and the app has no `/metrics` endpoint yet.
- The app does not reconnect to a restarted database on its own, so one request can fail after a Postgres restart. A JWT stays valid after its account is deleted.
- The `HighCPU` alert rule was adjusted for Minikube's metric labels and should be re-checked on EKS.

## Project structure

~~~
app/                FastAPI application
tests/              pytest suite (auth, CRUD, error codes)
k8s/                Kubernetes manifests (+ examples/ for the secret shape)
monitoring/         kube-prometheus-stack values, alert rules, Grafana dashboard
terraform/          AWS VPC and EKS (variables, outputs, remote state example)
.github/workflows/  CI and CD pipelines
Dockerfile, docker-compose.yml, .env.example
~~~

## Author

Milind Kapadnis
