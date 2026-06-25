# Contributing to RealDiag-Software

Thank you for your interest in contributing to RealDiag-Software! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant logs or error messages

### Suggesting Enhancements

We welcome suggestions for new features or improvements! Please create an issue with:
- A clear description of the enhancement
- Why this enhancement would be useful
- Any implementation ideas you might have

### Medical Content Updates

For updates to diagnostic rules, clinical guidelines, or medical content:
- **See [MEDICAL_UPDATE_PROCESS.md](MEDICAL_UPDATE_PROCESS.md)** for the complete medical content update workflow
- All medical updates require clinical review by a qualified healthcare professional
- Include source guideline references and evidence levels
- Follow the structured update process for safety and accuracy

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests to ensure everything works (`python -m unittest discover -s tests`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guidelines for Python code
- Add docstrings to functions and classes
- Write tests for new features
- Keep commits focused and atomic
- Write clear commit messages

### Testing

Before submitting a PR, make sure all tests pass:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Code Review Process

1. All submissions require review
2. We may suggest changes or improvements
3. Once approved, your PR will be merged

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/your-username/RealDiag-Software.git
cd RealDiag-Software
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests to verify setup:
```bash
python -m unittest discover -s tests
```

## Project Structure

```
RealDiag-Software/
├── diagnostics/      # Diagnostic modules
├── tests/           # Test suite
├── backend/         # Backend API
├── frontend/        # Web interface
├── main.py          # CLI entry point
└── config.py        # Configuration
```

## Medical Content Guidelines

### Clinical Review Requirements
All medical content updates must:
1. Include source references (published guidelines, peer-reviewed literature)
2. Specify evidence level (A/B/C based on strength of evidence)
3. Be reviewed by a qualified healthcare professional
4. Include version numbers and last_updated dates
5. Document the clinical reviewer's credentials in the PR

### Validation
Run the medical rules validator before submitting:
```bash
cd backend
python scripts/validate_rules.py --all
```

This checks for:
- Required metadata fields
- YAML syntax errors
- Missing citations
- Outdated rules (>1 year old)
- Data consistency

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

For medical content questions, see [MEDICAL_UPDATE_PROCESS.md](MEDICAL_UPDATE_PROCESS.md).

Thank you for contributing!
