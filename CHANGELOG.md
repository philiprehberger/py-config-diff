# Changelog

## 0.3.0 (2026-05-26)

- `include` and `exclude` now accept compiled `re.Pattern` objects alongside glob strings — useful for redacting secret keys by regex (e.g., `re.compile(r".*_token$")`)
- Add package-card image to README

## 0.2.0 (2026-04-29)

- Add `unified_diff(left, right, *, context, left_label, right_label)` for traditional `diff -u` style output
- Extend tests to cover `unified_diff` on flat, nested, and identical dicts
- Clean up malformed CHANGELOG history (collapsed `0.1.5` entries split out)

## 0.1.6 (2026-03-25)

- Convert API section to table format

## 0.1.5 (2026-03-22)

- Add pytest and mypy tool configuration to pyproject.toml
- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility
- Add GitHub issue templates, dependabot config, and PR template

## 0.1.4 (2026-03-15)

- Add Development section to README

## 0.1.1 (2026-03-12)

- Add project URLs to pyproject.toml

## 0.1.0 (2026-03-10)

- Initial release
