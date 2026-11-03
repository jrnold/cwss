# cwss

## Data (DVC)

This project follows the data baseline; read it with `git -C ~/jrnold-projects show origin/main:data-baseline/README.md`. Its
project type is empirical. This directory is its own DVC project, so run `dvc` from here.

- Default remote: `gs://jrnold-dvc/cwss`. On an auth error, ask the user to run
  `! gcloud auth application-default login`.
- After changing data: `dvc repro` or `dvc add`, `dvc push`, `git commit`, `git push`.
- Never run `dvc gc`, and never `git add` a DVC-tracked path.

Exceptions to the baseline, one line each, in the form `Exception to P1: reason`. `data-audit` reads
these lines and reports the rule as accepted. 
Exception to F3: `data/processed/nps_cwss.sqlite3` is SQLite because it's a distribution copy of the database. Every table is also in `data/processed/parquet/`.

## Build

- The `sqlite` stage needs Docker running and `unzip`. It restores the NPS backup in a throwaway SQL Server container.
- Don't publish to Zenodo without the user's explicit confirmation, because a published version can't be changed.
