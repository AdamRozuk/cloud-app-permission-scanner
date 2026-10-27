# cloud-app-permission-scanner

## Installation

### From source (local)

```bash
git clone https://github.com/syndaez/cloud-app-permission-scanner.git
cd cloud-app-permission-scanner
pip install .
```

### Development mode

If you're making changes to the source code, install in editable mode so your changes take effect immediately without reinstalling:

```bash
pip install -e .
```

### From GitHub (directly)

```bash
pip install git+https://github.com/syndaez/cloud-app-permission-scanner.git
```

### Verify installation

```bash
cloud-app-permission-scanner --help
```

## Development

Install the package with its development tools, then run the checks that CI runs:

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check .
mypy
pytest
```

The end-to-end tests compile the Java samples in `tests/fixtures/java` with
`javac`, so they need a JDK on `PATH`. Without one they are skipped.
