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
