# Contributing Guide

Thank you for considering a contribution to this project! The following steps will help you get a development environment running, execute the tests, and submit your changes.

## Development setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/genesis-engine/genesis-engine.git
   cd genesis-engine
   ```
2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```
3. **Install dependencies**
   Install the project in editable mode with the development extras (or install from `requirements.txt`):
   ```bash
   pip install -e ".[dev]"
   # or
   pip install -r requirements.txt
   ```

## Running the tests

The test suite lives in the [`tests/`](tests/) directory and can be executed with `pytest`:
```bash
pytest
```

Before submitting changes, please ensure code style is consistent:
```bash
black .
isort .
```

## Submitting a pull request

1. Fork the repository and create a new branch for your feature or fix.
2. Run the tests and formatters described above.
3. Push your branch and open a pull request against the main repository.
4. Describe the problem and how your changes address it. Include any relevant issue numbers.

We appreciate your help improving this project!
