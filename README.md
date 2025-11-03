# RealDiag-Software

Real Time Diagnostic Assistant Software - A comprehensive system diagnostic tool for monitoring and analyzing system health, network connectivity, and performance metrics.

## Quick Start

### Option 1: Docker Compose (Full Stack - Web + API)
Run the complete web application with backend API:
```bash
docker compose up --build
```
Access:
- API → http://localhost:8000/health
- Web → http://localhost:3000/diagnostic

### Option 2: Command-Line Tool (Standalone Python)
Run diagnostics from the command line:
```bash
pip install -r requirements.txt
python main.py --all
```

## Features

- **System Diagnostics**: Monitor CPU, memory, and disk usage with configurable thresholds
- **Network Diagnostics**: Check network connectivity, interface information, and network statistics
- **Performance Monitoring**: Track system uptime, process information, and load averages
- **Real-time Analysis**: Get instant insights into your system's health
- **Report Generation**: Save diagnostic reports in JSON format for later analysis
- **Color-coded Output**: Easy-to-read, color-coded console output
- **Flexible CLI**: Command-line interface with multiple options for targeted diagnostics
- **Web Interface**: Modern web-based diagnostic interface (via Docker)
- **REST API**: Backend API for diagnostic services (via Docker)

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Docker and Docker Compose (for web application)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/bevroy/RealDiag-Software.git
cd RealDiag-Software
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage - CLI Tool

### Basic Usage

Run all diagnostics:
```bash
python main.py --all
```

### Specific Diagnostics

Run system diagnostics only:
```bash
python main.py --system
```

Run network diagnostics only:
```bash
python main.py --network
```

Run performance diagnostics only:
```bash
python main.py --performance
```

### Combining Options

Run system and network diagnostics:
```bash
python main.py --system --network
```

### Saving Reports

Save diagnostic results to a JSON file:
```bash
python main.py --all --save
```

Run diagnostics quietly (no console output) and save results:
```bash
python main.py --all --save --quiet
```

### Help and Version

Display help information:
```bash
python main.py --help
```

Display version information:
```bash
python main.py --version
```

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--system` | `-s` | Run system diagnostics (CPU, memory, disk) |
| `--network` | `-n` | Run network diagnostics (connectivity, interfaces, stats) |
| `--performance` | `-p` | Run performance diagnostics (uptime, processes, load) |
| `--all` | `-a` | Run all available diagnostics |
| `--save` | | Save diagnostic report to JSON file |
| `--quiet` | `-q` | Suppress console output |
| `--version` | `-v` | Show version information |
| `--help` | `-h` | Show help message |

## Configuration

The application can be configured by editing the `config.py` file. Available settings include:

- **Thresholds**: CPU, memory, and disk warning thresholds
- **Network Settings**: Default test host and timeout values
- **Report Settings**: Report directory and log file locations
- **Check Interval**: Frequency of diagnostic checks

## Output Examples

### System Diagnostics
Shows CPU usage, memory utilization, and disk space with status indicators:
- ✓ **OK**: Metrics within normal thresholds
- ⚠ **WARNING**: Metrics exceeding configured thresholds

### Network Diagnostics
Displays:
- Connectivity status to test hosts
- Network interface information
- Network I/O statistics (bytes sent/received, packets, errors)

### Performance Diagnostics
Provides:
- System uptime information
- Total running processes
- Top 5 processes by CPU usage
- Load averages (on supported platforms)

## Report Files

Diagnostic reports are saved in the `reports/` directory with the following naming convention:
```
{diagnostic_type}_report_{timestamp}.json
```

Example: `full_report_20241103_162530.json`

## Dependencies

- **psutil**: Cross-platform library for system and process utilities
- **colorama**: Cross-platform colored terminal text

See `requirements.txt` for specific versions.

## Architecture

```
RealDiag-Software/
├── main.py                 # Main entry point and CLI interface
├── config.py               # Configuration settings
├── diagnostics/            # Diagnostic modules
│   ├── __init__.py        # Module initialization
│   ├── system.py          # System diagnostics
│   ├── network.py         # Network diagnostics
│   └── performance.py     # Performance monitoring
├── tests/                  # Test suite
│   ├── test_system.py     # System module tests
│   ├── test_network.py    # Network module tests
│   └── test_performance.py # Performance module tests
├── backend/                # Backend API (Docker)
├── frontend/               # Web interface (Docker)
├── docker-compose.yml      # Docker compose configuration
├── requirements.txt        # Python dependencies
└── README.md              # Documentation
```

## Testing

Run the test suite:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.

## Version

Current version: 1.0.0

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/bevroy/RealDiag-Software).
