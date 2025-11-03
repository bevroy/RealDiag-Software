# Deployment Guide - RealDiag-Software

This guide covers different deployment scenarios for RealDiag-Software.

## Table of Contents
1. [Standalone CLI Deployment](#standalone-cli-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment](#cloud-deployment)

---

## Standalone CLI Deployment

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bevroy/RealDiag-Software.git
   cd RealDiag-Software
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run diagnostics:**
   ```bash
   python main.py --all
   ```

### System-wide Installation

Install as a Python package:
```bash
pip install dist/realdiag_software-1.0.0-py3-none-any.whl
```

Then run from anywhere:
```bash
realdiag --all
```

---

## Docker Deployment

### Development Mode

1. **Start services:**
   ```bash
   docker compose up --build
   ```

2. **Access the application:**
   - Web UI: http://localhost:3000/diagnostic
   - API: http://localhost:8000/health

3. **Stop services:**
   ```bash
   docker compose down
   ```

### Production Mode

1. **Build images:**
   ```bash
   docker compose build
   ```

2. **Run in detached mode:**
   ```bash
   docker compose up -d
   ```

3. **View logs:**
   ```bash
   docker compose logs -f
   ```

4. **Monitor services:**
   ```bash
   docker compose ps
   ```

---

## Production Deployment

### Prerequisites
- Python 3.7+
- Virtual environment (recommended)
- Reverse proxy (nginx/Apache) for web deployment
- SSL certificate for HTTPS

### Steps

1. **Create virtual environment:**
   ```bash
   python3 -m venv /opt/realdiag/venv
   source /opt/realdiag/venv/bin/activate
   ```

2. **Install application:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure systemd service (Linux):**
   ```ini
   # /etc/systemd/system/realdiag.service
   [Unit]
   Description=RealDiag Diagnostic Service
   After=network.target

   [Service]
   Type=simple
   User=realdiag
   WorkingDirectory=/opt/realdiag
   Environment="PATH=/opt/realdiag/venv/bin"
   ExecStart=/opt/realdiag/venv/bin/python main.py --all --save --quiet
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable and start service:**
   ```bash
   sudo systemctl enable realdiag
   sudo systemctl start realdiag
   ```

### Nginx Configuration (for Web UI)

```nginx
server {
    listen 80;
    server_name diagnostics.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Cloud Deployment

### AWS EC2

1. **Launch EC2 instance** (Amazon Linux 2 or Ubuntu)

2. **Install Docker:**
   ```bash
   sudo yum install docker -y  # Amazon Linux
   # or
   sudo apt-get install docker.io -y  # Ubuntu
   ```

3. **Clone and deploy:**
   ```bash
   git clone https://github.com/bevroy/RealDiag-Software.git
   cd RealDiag-Software
   docker compose up -d
   ```

4. **Configure security group** to allow ports 3000 and 8000

### Azure Container Instances

1. **Build and push images to ACR:**
   ```bash
   az acr build --registry myregistry --image realdiag-backend:v1 -f backend/Dockerfile .
   az acr build --registry myregistry --image realdiag-frontend:v1 -f frontend/Dockerfile .
   ```

2. **Deploy container group:**
   ```bash
   az container create --resource-group mygroup \
     --name realdiag --image myregistry.azurecr.io/realdiag-backend:v1 \
     --ports 8000 --dns-name-label realdiag-api
   ```

### Google Cloud Run

1. **Build and push:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/realdiag-backend
   ```

2. **Deploy:**
   ```bash
   gcloud run deploy realdiag-backend \
     --image gcr.io/PROJECT_ID/realdiag-backend \
     --platform managed --allow-unauthenticated
   ```

---

## Environment Variables

Configure the application using environment variables:

```bash
# Backend API
export API_PORT=8000
export API_HOST=0.0.0.0

# Frontend
export NEXT_PUBLIC_API_BASE=http://localhost:8000

# Diagnostic settings
export DIAGNOSTIC_INTERVAL=300
export LOG_LEVEL=INFO
```

---

## Monitoring and Maintenance

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check diagnostic status
python main.py --system
```

### Log Management

```bash
# View Docker logs
docker compose logs -f

# View systemd logs
journalctl -u realdiag -f
```

### Backup

Important files to backup:
- Configuration: `config.py`
- Reports: `reports/`
- Custom decision trees: `backend/trees/`

---

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change ports in docker-compose.yml
   ports:
     - "8001:8000"  # Use different port
   ```

2. **Permission denied:**
   ```bash
   sudo chown -R $USER:$USER .
   ```

3. **Module not found:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Security Considerations

1. **Use HTTPS** in production
2. **Restrict API access** with authentication
3. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
4. **Use environment variables** for sensitive configuration
5. **Enable firewall rules** to restrict access

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/bevroy/RealDiag-Software/issues
- Documentation: [README.md](README.md)
