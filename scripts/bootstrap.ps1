param(
    [string]$PythonExecutable = ""
)

$ErrorActionPreference = "Stop"

if ($PythonExecutable) {
    & $PythonExecutable -m venv .venv
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -3.12 -m venv .venv
} else {
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ($version -notin @("3.11", "3.12")) {
        throw "Python 3.11 or 3.12 is required; pass -PythonExecutable with its full path."
    }
    python -m venv .venv
}
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/doctor.py
python -m pytest
