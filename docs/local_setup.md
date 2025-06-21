
# Local setup
## Install uv
Please follow instructions [here](https://docs.astral.sh/uv/getting-started/installation/)

## Setup virtual environment
```bash
uv venv
```

Install dependencies
```bash
uv pip install -r pyproject.toml
```

## Run the server (development)
```bash
fastapi dev app/api.py
```

## Add new packages
```bash
uv add <package-name>
```

## Linting and formatting
Recommended editor: Visual Studio Code
1. Install [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## Debugging
Add the below configuration to `.vscode/launch.json`
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI CLI",
            "type": "debugpy",
            "request": "launch",
            "module": "fastapi",
            "args": [
                "run",
                "app/api.py",
                "--port", "8000",
                "--reload"
            ],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/.venv/bin/python"
            },
            "justMyCode": true
        }
    ]
}
```