"""Copy every table of a database into SQLite, keeping column types, NULLs and primary keys."""

import uuid
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# SQL Server's internal table for database diagrams. It's empty and holds no CWSS data.
SKIP_TABLES = {"sysdiagrams"}
BATCH_ROWS = 50_000


def generic_type(column_type: sa.types.TypeEngine) -> sa.types.TypeEngine:
    """Translate a SQL Server column type to one that SQLite can store."""
    if isinstance(column_type, mssql.BIT):
        return sa.Boolean()
    if isinstance(column_type, mssql.UNIQUEIDENTIFIER):
        # Keep the text form, because other tables store these ids in varchar columns.
        return sa.String(36)
    if isinstance(column_type, sa.Numeric):
        # SQLite has no exact decimal type. Declaring REAL says so instead of hiding it.
        return sa.Float()
    generic = column_type.as_generic()
    if isinstance(generic, sa.String):
        # A SQL Server collation means nothing to SQLite and would fail on CREATE TABLE.
        generic.collation = None
    return generic


def normalize_value(value: Any) -> Any:
    """Write a GUID the way SQL Server shows it: uppercase, with hyphens."""
    return str(value).upper() if isinstance(value, uuid.UUID) else value


def copy_table(source: sa.Engine, destination: sa.Engine, table: sa.Table) -> int:
    """Create `table` in `destination`, copy its rows, and return how many were copied."""
    target = sa.Table(
        table.name,
        sa.MetaData(),
        *(
            sa.Column(c.name, generic_type(c.type), primary_key=c.primary_key, nullable=c.nullable)
            for c in table.columns
        ),
    )
    target.create(destination)
    insert = target.insert()
    copied = 0
    with source.connect() as src, destination.begin() as dst:
        rows = src.execution_options(stream_results=True).execute(table.select())
        for batch in rows.partitions(BATCH_ROWS):
            dst.execute(
                insert, [{k: normalize_value(v) for k, v in row._mapping.items()} for row in batch]
            )
            copied += len(batch)
    return copied


def copy_database(source: sa.Engine, db_path: Path) -> dict[str, int]:
    """Copy all tables to a new SQLite file, failing if any row count differs from the source."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.unlink(missing_ok=True)
    metadata = sa.MetaData()
    metadata.reflect(bind=source)
    destination = sa.create_engine(f"sqlite:///{db_path}")
    counts = {}
    for table in metadata.sorted_tables:
        if table.name in SKIP_TABLES:
            continue
        copied = copy_table(source, destination, table)
        with source.connect() as conn:
            expected = conn.execute(sa.select(sa.func.count()).select_from(table)).scalar_one()
        if copied != expected:
            raise RuntimeError(f"{table.name}: copied {copied} rows, source has {expected}")
        print(f"{table.name}: {copied} rows", flush=True)
        counts[table.name] = copied
    destination.dispose()
    return counts
