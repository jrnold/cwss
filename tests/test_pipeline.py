"""Tests that need no Docker or SQL Server: type mapping, copying, key checks and packaging."""

import hashlib
import sqlite3
import stat
import uuid
import zipfile

import duckdb
import pytest
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

from cwss import zenodo
from cwss.restore import BACKUP_NAME, extract_backup, restore_statement
from cwss.to_parquet import check_key, package_directory, sqlite_tables, sqlite_to_parquet
from cwss.to_sqlite import copy_database, generic_type, normalize_value
from cwss.zenodo import check_checksum


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (mssql.BIT(), sa.Boolean),
        (mssql.DATETIME(), sa.DateTime),
        (mssql.REAL(), sa.Float),
        (mssql.NUMERIC(18, 0), sa.Float),
        (mssql.INTEGER(), sa.Integer),
        (mssql.TEXT(), sa.Text),
    ],
)
def test_generic_type_maps_mssql_types(source, expected):
    assert isinstance(generic_type(source), expected)


def test_generic_type_drops_collation():
    converted = generic_type(mssql.VARCHAR(10, collation="SQL_Latin1_General_CP1_CI_AS"))
    assert converted.collation is None
    assert converted.length == 10


def test_guid_keeps_sql_server_text_form():
    assert generic_type(mssql.UNIQUEIDENTIFIER()).length == 36
    guid = uuid.UUID("c6acf485-c8ab-e011-8262-a4badb3b8d0e")
    assert normalize_value(guid) == "C6ACF485-C8AB-E011-8262-A4BADB3B8D0E"
    assert normalize_value("not a guid") == "not a guid"


def test_generic_type_compiles_on_sqlite():
    from sqlalchemy.dialects import sqlite

    for source in (mssql.BIT(), mssql.NVARCHAR(5), mssql.NTEXT(), mssql.UNIQUEIDENTIFIER()):
        assert generic_type(source).compile(dialect=sqlite.dialect())


def test_restore_statement_moves_data_and_log_files():
    statement = restore_statement("/backup/x.bak", [("cwss", "D"), ("cwss_log", "L")])
    assert "MOVE 'cwss' TO '/var/opt/mssql/data/nps_cwss_0.mdf'" in statement
    assert "MOVE 'cwss_log' TO '/var/opt/mssql/data/nps_cwss_1.ldf'" in statement


def test_extract_backup_is_readable_by_the_container_user(tmp_path):
    archive = tmp_path / "CWSS.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(BACKUP_NAME, b"backup")
        zf.writestr("other.xml", b"other")
    dst = tmp_path / "bak"
    dst.mkdir(mode=0o700)
    extract_backup(archive, dst)
    assert (dst / BACKUP_NAME).read_bytes() == b"backup"
    assert not (dst / "other.xml").exists()
    assert stat.S_IMODE((dst / BACKUP_NAME).stat().st_mode) == 0o644
    assert stat.S_IMODE(dst.stat().st_mode) == 0o755


@pytest.fixture
def source_engine(tmp_path):
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'source.db'}")
    with engine.begin() as conn:
        conn.exec_driver_sql("create table people (id integer primary key, name text, age integer)")
        conn.exec_driver_sql("insert into people values (1, 'A', 0), (2, '', null)")
        conn.exec_driver_sql("create table sysdiagrams (id integer primary key)")
    return engine


def test_copy_keeps_zero_empty_string_and_null(source_engine, tmp_path):
    db = tmp_path / "out.sqlite3"
    assert copy_database(source_engine, db) == {"people": 2}
    rows = sqlite3.connect(db).execute("select id, name, age from people order by id").fetchall()
    assert rows == [(1, "A", 0), (2, "", None)]


def test_copy_skips_internal_tables(source_engine, tmp_path):
    db = tmp_path / "out.sqlite3"
    copy_database(source_engine, db)
    assert set(sqlite_tables(db)) == {"people"}


def test_sqlite_to_parquet_keeps_rows_and_key(source_engine, tmp_path):
    db = tmp_path / "out.sqlite3"
    copy_database(source_engine, db)
    assert sqlite_tables(db) == {"people": ["id"]}
    dst = tmp_path / "parquet"
    sqlite_to_parquet(db, dst)
    path = dst / "people.parquet"
    rows = duckdb.sql(f"select id, name, age from '{path}' order by id").fetchall()
    assert rows == [(1, "A", 0), (2, "", None)]
    codecs = duckdb.sql(f"select distinct compression from parquet_metadata('{path}')").fetchall()
    assert codecs == [("ZSTD",)]


def test_sqlite_to_parquet_writes_real_booleans(tmp_path):
    db = tmp_path / "flags.sqlite3"
    conn = sqlite3.connect(db)
    conn.execute("create table flags (id integer primary key, deleted boolean)")
    conn.execute("insert into flags values (1, 0), (2, 1), (3, null)")
    conn.commit()
    conn.close()
    dst = tmp_path / "parquet"
    sqlite_to_parquet(db, dst)
    path = dst / "flags.parquet"
    assert duckdb.sql(f"select distinct typeof(deleted) from '{path}'").fetchall() == [("BOOLEAN",)]
    rows = duckdb.sql(f"select deleted from '{path}' order by id").fetchall()
    assert rows == [(False,), (True,), (None,)]


@pytest.mark.parametrize(
    ("values", "problem"),
    [("(1), (1)", "1 duplicated"), ("(1), (null)", "1 missing")],
)
def test_check_key_rejects_bad_keys(values, problem):
    conn = duckdb.connect()
    conn.execute(f"create table t as select * from (values {values}) v(id)")
    with pytest.raises(ValueError, match=problem):
        check_key(conn, "t", ["id"])


def test_check_key_accepts_unique_keys():
    conn = duckdb.connect()
    conn.execute("create table t as select * from (values (1), (2)) v(id)")
    check_key(conn, "t", ["id"])


def test_package_is_reproducible(tmp_path):
    src = tmp_path / "parquet"
    src.mkdir()
    (src / "b.parquet").write_bytes(b"b")
    (src / "a.parquet").write_bytes(b"a")
    first = tmp_path / "first.tar"
    package_directory(src, first)
    (src / "a.parquet").touch()
    second = tmp_path / "second.tar"
    package_directory(src, second)
    digest = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (first, second)]
    assert digest[0] == digest[1]


def test_zenodo_checksum_rejects_a_mismatch(tmp_path):
    path = tmp_path / "file.bin"
    path.write_bytes(b"data")
    check_checksum(path, f"md5:{hashlib.md5(b'data').hexdigest()}")  # noqa: S324
    with pytest.raises(RuntimeError, match="local md5"):
        check_checksum(path, "md5:00000000000000000000000000000000")


def test_zenodo_upload_never_publishes_without_the_flag(monkeypatch):
    urls = []

    def fake_request(url, token, method="GET", payload=None):
        urls.append(url)
        return {"links": {"bucket": "https://bucket", "html": "https://draft"}}

    monkeypatch.setattr(zenodo, "request", fake_request)
    monkeypatch.setattr(zenodo, "FILES", [])
    monkeypatch.setattr("sys.argv", ["cwss-zenodo-upload"])
    monkeypatch.setenv("ZENODO_API_KEY", "token")
    zenodo.main()
    assert urls
    assert not any("publish" in url for url in urls)
