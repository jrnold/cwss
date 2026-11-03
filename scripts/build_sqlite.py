"""Stage `sqlite`: restore the NPS backup in Docker and copy it to SQLite."""

from pathlib import Path

from cwss.restore import restored_database
from cwss.to_sqlite import copy_database

ZIP = Path("data/raw/nps/CWSS.zip")
DOCKERFILE = Path("docker/mssql/Dockerfile")
DB = Path("data/processed/nps_cwss.sqlite3")

if __name__ == "__main__":
    with restored_database(ZIP, DOCKERFILE) as engine:
        copy_database(engine, DB)
