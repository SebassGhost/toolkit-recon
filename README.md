# Toolkit-Recon

Modular reconnaissance and OSINT toolkit for educational pentesting workflows.

## Legal Notice

Use this project only on assets you own or where you have explicit authorization.
The authors are not responsible for misuse.

## Features

- Modular architecture (`domain`, `subdomain`, `endpoint`, `tech` modules)
- CLI commands for focused scans and full recon runs
- Profile-based behavior: `passive`, `balanced`, `aggressive`
- JSON output per module plus consolidated `recon.json`
- Cross-platform launchers (`.ps1`, `.bat`, `.sh`)

## Installation

```bash
git clone https://github.com/SebassGhost/toolkit-recon
cd toolkit-recon
pip install -r requirements.txt
```

## Usage

Run as a Python module from the project root:

```bash
python -m toolkit_recon.main subdomain example.com
python -m toolkit_recon.main endpoints example.com
python -m toolkit_recon.main tech example.com
python -m toolkit_recon.main recon-all example.com --profile balanced
```

## Output

Results are stored under:

```text
output/<target>/
```

Main files:

- `output/<target>/subdomains.json`
- `output/<target>/endpoints.json`
- `output/<target>/tech_fingerprint.json`
- `output/<target>/recon.json`

## Profiles

- `passive`: minimal probing, lower concurrency
- `balanced`: default profile for daily use
- `aggressive`: larger path set and higher concurrency

## Development

Install test dependencies and run tests:

```bash
pip install -r tests/requirements.txt
pytest
```

## License

MIT. See `LICENSE`.
