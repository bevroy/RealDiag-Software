# Quick Start Guide - RealDiag-Software

## Installation

### Option 1: Using Installation Script (Recommended)

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
install.bat
```

### Option 2: Manual Installation

```bash
pip install -r requirements.txt
```

### Option 3: Install from Package

```bash
pip install dist/realdiag_software-1.0.0-py3-none-any.whl
```

## Running the Application

### Command-Line Tool

Run all diagnostics:
```bash
python main.py --all
```

Run specific diagnostics:
```bash
python main.py --system        # System diagnostics only
python main.py --network       # Network diagnostics only
python main.py --performance   # Performance diagnostics only
```

Save results to file:
```bash
python main.py --all --save
```

### Docker Deployment (Full Stack)

Start all services:
```bash
docker compose up --build
```

Access the application:
- Web Interface: http://localhost:3000/diagnostic
- API Backend: http://localhost:8000/health

Stop services:
```bash
docker compose down
```

## Quick Test

Verify installation:
```bash
python main.py --version
python main.py --help
python -m unittest discover -s tests -v
```

## Common Commands

| Command | Description |
|---------|-------------|
| `python main.py --all` | Run all diagnostics |
| `python main.py --system` | System diagnostics only |
| `python main.py --network` | Network diagnostics only |
| `python main.py --performance` | Performance diagnostics only |
| `python main.py --all --save` | Save results to JSON |
| `python main.py --all --quiet` | Run without console output |
| `make test` | Run test suite |
| `make clean` | Clean build artifacts |

## Getting Help

```bash
python main.py --help
```

For more details, see [README.md](README.md)

## Local prebuilt frontend (developer convenience)

If your local environment is constrained and the Next.js production build OOMs during
`docker compose up --build`, you can prebuild the frontend and use a prebuilt image
for faster, more-robust local testing.

1. Build frontend locally:

```bash
cd frontend
npm ci && npm run build
cd -
```

2. Build the helper image that copies the built files (no `npm run build` inside the image):

```bash
docker build -f Dockerfile.prebuilt -t realdiag-frontend:prebuilt .
```

3. Start the stack using a compose override that forces the `web` service to use the prebuilt image:

```bash
cat > docker-compose.local.yml <<'YML'
version: "3.9"
services:
	web:
		image: realdiag-frontend:prebuilt
		build: null
YML

docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
```

This mirrors the CI-friendly approach implemented in `.github/workflows/frontend-prebuild.yml`.

## Publishing images to GitHub Container Registry (GHCR)

If you want CI to publish the prebuilt frontend image to GHCR, create a Personal Access
Token (PAT) with the `write:packages` scope (and `read:packages` if needed) and add it as
a repository secret named `GHCR_TOKEN`.

Steps to create the PAT:

1. Visit https://github.com/settings/tokens/new
2. Give it a descriptive name (e.g. "GHCR publish token")
3. Under "Select scopes", check `write:packages` (optionally `read:packages`)
4. Create the token and copy the value (you won't be able to see it again)

Add it to your repository:

1. Go to your repository on GitHub -> Settings -> Secrets -> Actions -> New repository secret
2. Name: `GHCR_TOKEN`
3. Value: the PAT you copied

With that secret present, the CI workflow `.github/workflows/frontend-prebuild.yml` will push
the built frontend image to GHCR and post the pushed image digest to the PR (or create a
release if running on `main`).
