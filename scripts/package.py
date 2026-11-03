"""Stage `package`: tar the Parquet tables for Zenodo."""

from pathlib import Path

from cwss.to_parquet import package_directory

if __name__ == "__main__":
    package_directory(Path("data/processed/parquet"), Path("data/processed/cwss-parquet.tar"))
