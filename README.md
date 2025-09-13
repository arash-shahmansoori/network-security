### Network Security Projects For Phising Data

Setup github secrets:
AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

AWS_REGION = us-east-1

AWS_ECR_LOGIN_URI = 788614365622.dkr.ecr.us-east-1.amazonaws.com/networkssecurity
ECR_REPOSITORY_NAME = networkssecurity


Docker Setup In EC2 commands to be Executed
#optinal

sudo apt-get update -y

sudo apt-get upgrade

#required

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker

### Run locally (uv)

- Prerequisites: Python 3.10+ and `uv` installed.

```bash
# Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Provide environment variables (create a .env at project root)
echo "MONGODB_URL_KEY=YOUR_MONGODB_CONNECTION_STRING" > .env

# Run the API (http://localhost:8000)
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

- Dev helpers:
  - Lint: `uv run ruff check .`
  - Fix: `uv run ruff check . --fix`
  - Format: `uv run ruff format .`

### Run with Docker

```bash
# Build image
docker build -t networksecurity:latest .

# Option A: pass env file
echo "MONGODB_URL_KEY=YOUR_MONGODB_CONNECTION_STRING" > .env
docker run --rm -p 8000:8000 --env-file .env networksecurity:latest

# Option B: pass env inline
docker run --rm -p 8000:8000 -e MONGODB_URL_KEY="YOUR_MONGODB_CONNECTION_STRING" networksecurity:latest
```

### MLflow tracking

- The training code logs to an MLflow file store under the project at:

  - `/Users/arashshahmansoori/Desktop/all projects/e2e/network_security/mlruns`

- The experiment name is set to `network security`.

- Launch the UI against this store:

```bash
mlflow ui \
  --backend-store-uri file:/Users/arashshahmansoori/Desktop/all\ projects/e2e/network_security/mlruns \
  --host 127.0.0.1 --port 5000
```

- Alternatively, run a tracking server with the same backend and artifact root:

```bash
mlflow server \
  --backend-store-uri file:/Users/arashshahmansoori/Desktop/all\ projects/e2e/network_security/mlruns \
  --default-artifact-root file:/Users/arashshahmansoori/Desktop/all\ projects/e2e/network_security/mlruns \
  --host 127.0.0.1 --port 5000
```