"""Dump every table of the CWSS SQL Server database to tab-separated files.

This needs a running SQL Server with the 2012-10-31 backup restored, so it is a frozen stage in
`dvc.yaml`. The tsv files that came out of it are distributed on Zenodo.
"""

import argparse
import csv
import re
from pathlib import Path

import sqlalchemy as sa


def clean_el(x):
    """Return `x` as text, with tabs removed so they can't break the tsv format."""
    return re.sub("\t", "", str(x)) if x else ""


def dump_table(conn, table, filename):
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([c.name for c in table.columns])
        for row in conn.execute(table.select()):
            writer.writerow([clean_el(x) for x in row])


def dump_all(engine, dst):
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    metadata = sa.MetaData()
    metadata.reflect(bind=engine)
    with engine.connect() as conn:
        for table in metadata.sorted_tables:
            out = dst / f"{table.name}.tsv"
            print(f"dumping {table.name} to {out}")
            dump_table(conn, table, out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", help="SQLAlchemy URL, e.g. mssql+pyodbc://nps_cwss")
    parser.add_argument("dst", help="output directory (created if needed)")
    args = parser.parse_args()
    dump_all(sa.create_engine(args.engine), args.dst)


if __name__ == "__main__":
    main()
