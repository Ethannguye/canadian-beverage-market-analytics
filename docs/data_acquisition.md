# Data acquisition runbook

## Requirements
- Python 3.10+ and packages from requirements.txt
- Free local disk space (some full-table ZIPs can be hundreds of MB)
- Internet access for official Statistics Canada source endpoints
- MySQL 8+ for the optional database-loading phase

## Phase A: Verify one small source first
```bash
python etl/download_statcan.py --tables 32100054
python etl/prepare_statcan.py --tables 32100054
python -m unittest discover -s tests -v
```
Inspect `data/processed/32100054_profile.json` for categories and coverage. Check the source's metadata CSV in `data/raw/32100054/`.

## Phase B: Explore larger sources one by one
```bash
python etl/download_statcan.py --tables 20100080
python etl/prepare_statcan.py --tables 20100080
# Repeat for other approved PIDs. Do NOT download all giant tables at once.
```
The default filter is regex-based discovery, not official series code approval. To inspect all source categories:
```bash
python etl/prepare_statcan.py --tables 32100054 --all-categories
```
This overwrites the processed candidate CSV, so save reviewed profiles before changing filtering.

## Provenance
The downloader stores `data/raw/manifest.json` with URL, date, SHA-256 and file names. Raw and processed data are .gitignored to prevent huge commits.

## HS partner trade
The CIMT app provides HS-level commodity and partner analysis but is *not* identical to the industry trade table. The HS workstream is not automated yet. Export a consistent 2020–2025 source file with HS codes 2009, 2201 and 2202, import/export flow, partner country, value, currency and (if present) quantity and quantity unit. Keep original files unchanged and document query settings.

## Review gate
The staging exporter labels beverage categories as **unreviewed candidates**. Verify exact code definitions in source metadata and approve specific series in MySQL before materializing production fact tables.

## Data size notes
- WDS CSV export is entire table by PID, not a beverage-only API query.
- Large downloads require a deliberate `--max-mb` choice.
- A large downloaded ZIP does not imply a complete project; check missing values and source coverage.
