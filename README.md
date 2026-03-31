# philiprehberger-config-diff

[![Tests](https://github.com/philiprehberger/py-config-diff/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-config-diff/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-config-diff.svg)](https://pypi.org/project/philiprehberger-config-diff/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-config-diff)](https://github.com/philiprehberger/py-config-diff/commits/main)

Compare configuration files across environments.

## Installation

```bash
pip install philiprehberger-config-diff
```

## Usage

```python
from philiprehberger_config_diff import diff_files, diff_dicts

# Compare files (JSON, TOML, INI, .env)
report = diff_files("config.dev.json", "config.prod.json")

for change in report.changes:
    print(change)  # "+ db.name = 'proddb'" / "~ port: 3000 -> 8080"

print(report.summary())
# "Added: 3, Removed: 1, Modified: 5"

# Filter by key patterns
report = diff_files("dev.env", "prod.env", include=["DB_*"])

# Compare dicts directly
report = diff_dicts(dev_config, prod_config)
```

## API

- `diff_files(left, right, include=None, exclude=None)` — Compare config files
- `diff_dicts(left, right, include=None, exclude=None)` — Compare dicts
- `report.changes` — List of `Change` objects
- `report.added` / `report.removed` / `report.modified` — Filtered changes
- `report.summary()` — Change count summary

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-config-diff)

🐛 [Report issues](https://github.com/philiprehberger/py-config-diff/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-config-diff/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
