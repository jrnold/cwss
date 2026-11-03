"""Write each SQLite table to zstd Parquet, checking primary keys, and package the result."""

import sqlite3
import tarfile
from pathlib import Path

import duckdb


def quote(name: str) -> str:
    """Quote an identifier for SQL."""
    return '"' + name.replace('"', '""') + '"'


def sqlite_tables(db_path: Path) -> dict[str, list[str]]:
    """Return each table's primary key columns, in key order."""
    conn = sqlite3.connect(db_path)
    try:
        names = conn.execute(
            "select name from sqlite_master where type = 'table' and name not like 'sqlite_%'"
        ).fetchall()
        tables = {}
        for (name,) in names:
            info = conn.execute(f"pragma table_info({quote(name)})").fetchall()
            keyed = sorted((c for c in info if c[5] > 0), key=lambda c: c[5])
            tables[name] = [c[1] for c in keyed]
        return tables
    finally:
        conn.close()


def boolean_columns(db_path: Path, table: str) -> list[str]:
    """Return the columns declared BOOLEAN, since DuckDB reads SQLite's 0/1 as integers."""
    conn = sqlite3.connect(db_path)
    try:
        info = conn.execute(f"pragma table_info({quote(table)})").fetchall()
        return [c[1] for c in info if c[2].upper() == "BOOLEAN"]
    finally:
        conn.close()


def check_key(conn: duckdb.DuckDBPyConnection, relation: str, key: list[str]) -> None:
    """Fail if `key` has missing or duplicate values in `relation`."""
    cols = ", ".join(quote(c) for c in key)
    missing = " or ".join(f"{quote(c)} is null" for c in key)
    bad = conn.execute(
        f"""
        select
            count(*) filter (where {missing}),
            (select count(*) from (
                select {cols} from {relation} group by {cols} having count(*) > 1
            ))
        from {relation}
        """
    ).fetchone()
    if bad != (0, 0):
        raise ValueError(f"{relation}: key {key} has {bad[0]} missing, {bad[1]} duplicated values")


def sqlite_to_parquet(db_path: Path, dst: Path) -> None:
    """Write every table in the SQLite file to `dst/<table>.parquet`."""
    dst.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect()
    conn.execute("install sqlite; load sqlite")
    conn.execute(f"attach '{db_path}' as src (type sqlite, read_only)")
    for table, key in sqlite_tables(db_path).items():
        relation = f"src.main.{quote(table)}"
        if key:
            check_key(conn, relation, key)
        out = dst / f"{table}.parquet"
        casts = ", ".join(
            f"{quote(c)}::boolean as {quote(c)}" for c in boolean_columns(db_path, table)
        )
        select = (
            f"select * replace ({casts}) from {relation}" if casts else f"select * from {relation}"
        )
        conn.execute(f"copy ({select}) to '{out}' (format parquet, compression zstd)")
        print(f"{table}: key {key or 'none'}", flush=True)
    conn.close()


def package_directory(src: Path, tar_path: Path) -> None:
    """Tar `src` with sorted names and fixed metadata, so the same files give the same bytes."""

    def normalized(info: tarfile.TarInfo) -> tarfile.TarInfo:
        info.mtime = 0
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        info.mode = 0o644
        return info

    tar_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, "w", format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(src.iterdir()):
            tar.add(path, arcname=f"{src.name}/{path.name}", filter=normalized)
