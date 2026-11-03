"""Restore the NPS SQL Server backup into a throwaway Docker container."""

import secrets
import shutil
import subprocess
import tempfile
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pymssql
import sqlalchemy as sa

BACKUP_NAME = "nps_cwss-20121031.bak"
DATABASE = "nps_cwss"
DATA_DIR = "/var/opt/mssql/data"
READY_TIMEOUT_SECONDS = 300


def _docker(*args: str) -> str:
    done = subprocess.run(["docker", *args], check=True, capture_output=True, text=True)
    return done.stdout.strip()


def extract_backup(zip_path: Path, dst: Path) -> None:
    """Extract the backup somewhere the SQL Server user in the container can read it.

    This calls `unzip` because the NPS zip uses Deflate64, which Python's `zipfile` can't read.
    """
    subprocess.run(["unzip", "-q", "-o", str(zip_path), BACKUP_NAME, "-d", str(dst)], check=True)
    dst.chmod(0o755)
    (dst / BACKUP_NAME).chmod(0o644)


def _connect(port: int, password: str) -> pymssql.Connection:
    """Connect once the server accepts logins, which takes a while under emulation."""
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    while True:
        try:
            return pymssql.connect(
                server="127.0.0.1", port=port, user="sa", password=password, autocommit=True
            )
        except pymssql.OperationalError:
            if time.monotonic() > deadline:
                raise
            time.sleep(5)


def restore_statement(backup: str, files: list[tuple[str, str]]) -> str:
    """Build the RESTORE command, moving each (logical name, type) file into the data directory."""
    moves = ", ".join(
        f"MOVE '{name}' TO '{DATA_DIR}/{DATABASE}_{i}.{'ldf' if kind == 'L' else 'mdf'}'"
        for i, (name, kind) in enumerate(files)
    )
    return f"RESTORE DATABASE [{DATABASE}] FROM DISK = '{backup}' WITH {moves}"


def _restore(conn: pymssql.Connection, backup: str) -> None:
    cursor = conn.cursor()
    cursor.execute(f"RESTORE FILELISTONLY FROM DISK = '{backup}'")
    files = [(row[0], row[2]) for row in cursor.fetchall()]
    cursor.execute(restore_statement(backup, files))
    # RESTORE reports progress as result sets, and it stops early unless they are read.
    while cursor.nextset():
        pass


@contextmanager
def restored_database(zip_path: Path, dockerfile: Path) -> Iterator[sa.Engine]:
    """Yield an engine for the restored database, removing the container afterwards."""
    image = "cwss-mssql:build"
    container = f"cwss-mssql-{uuid.uuid4().hex[:8]}"
    # SQL Server requires a complex password. It only guards a local, short-lived container.
    password = f"Cw1!{secrets.token_hex(16)}"
    _docker("build", "--quiet", "-t", image, str(dockerfile.parent))
    workdir = Path(tempfile.mkdtemp(prefix="cwss-bak-"))
    try:
        extract_backup(zip_path, workdir)
        _docker(
            "run",
            "--detach",
            "--name",
            container,
            "--env",
            f"MSSQL_SA_PASSWORD={password}",
            "--publish",
            "127.0.0.1::1433",
            "--volume",
            f"{workdir}:/backup:ro",
            image,
        )
        port = int(_docker("port", container, "1433/tcp").rsplit(":", 1)[1])
        conn = _connect(port, password)
        _restore(conn, f"/backup/{BACKUP_NAME}")
        conn.close()
        url = sa.URL.create(
            "mssql+pymssql",
            username="sa",
            password=password,
            host="127.0.0.1",
            port=port,
            database=DATABASE,
        )
        engine = sa.create_engine(url)
        try:
            yield engine
        finally:
            engine.dispose()
    finally:
        subprocess.run(["docker", "rm", "--force", container], check=False, capture_output=True)
        shutil.rmtree(workdir, ignore_errors=True)
