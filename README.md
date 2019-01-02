# philiprehberger-config-diff

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

## License

MIT
