"""Stage `parquet`: write each SQLite table to Parquet."""

from pathlib import Path

from cwss.to_parquet import sqlite_to_parquet

if __name__ == "__main__":
    sqlite_to_parquet(Path("data/processed/nps_cwss.sqlite3"), Path("data/processed/parquet"))
