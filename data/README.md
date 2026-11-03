# Data

## Sources

One row per directory in `data/raw/`. Add the row in the commit that adds the data.

| Directory | Source | Retrieved | Version | License | How to fetch |
|---|---|---|---|---|---|
| `raw/SOURCE` | URL or person | YYYY-MM-DD | Release, revision, or none | Terms of use | Script or manual steps |

## Tables

One row per table in `data/processed/`.

| Table | One row per | Key | Stage | Notes |
|---|---|---|---|---|
| `processed/TABLE.parquet` | Unit of observation | Column or columns | Stage in `dvc.yaml` | |
