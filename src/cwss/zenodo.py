"""Upload the CWSS files to a Zenodo draft, and optionally publish it.

Uploading only changes the draft. Publishing is a separate flag because it can't be undone:
Zenodo doesn't allow the files of a published version to change.

    uv run --env-file .env cwss-zenodo-upload
    uv run --env-file .env cwss-zenodo-upload --publish
"""

import argparse
import datetime
import hashlib
import json
import os
import urllib.request
from pathlib import Path
from typing import Any

DEPOSITION = 23905004
API = "https://zenodo.org/api/deposit/depositions"
FILES = [
    Path("data/raw/nps/CWSS.zip"),
    Path("data/processed/nps_cwss.sqlite3"),
    Path("data/processed/cwss-parquet.tar"),
]
SOURCE_URL = "https://www.nps.gov/featurecontent/foia/CWSS.zip"
SITE_URL = "https://www.nps.gov/civilwar/soldiers-and-sailors-database.htm"
REPO_URL = "https://github.com/jrnold/cwss"

DESCRIPTION = f"""\
<p>Data from the National Park Service's <a href="{SITE_URL}">Civil War Soldiers and Sailors \
System (CWSS)</a>, with versions of its database that don't need SQL Server.</p>
<p><b>Original data</b></p>
<ul>
<li><code>CWSS.zip</code>: the file published by the National Park Service at \
<a href="{SOURCE_URL}">{SOURCE_URL}</a> (last modified 2021-08-20), unchanged. It holds the SQL \
Server backup <code>nps_cwss-20121031.bak</code> and the original XML and CSV files.</li>
</ul>
<p><b>Derived data</b></p>
<ul>
<li><code>nps_cwss.sqlite3</code>: the 30 tables of the database as a SQLite file.</li>
<li><code>cwss-parquet.tar</code>: the same tables as zstd Parquet files, one per table.</li>
</ul>
<p>The derived files were made by restoring the backup in SQL Server and copying each table. The \
code and table documentation are in <a href="{REPO_URL}">{REPO_URL}</a>.</p>
"""


def metadata(publication_date: datetime.date) -> dict[str, Any]:
    """Return the record's metadata."""
    return {
        "title": "Civil War Soldiers and Sailors Database (NPS CWSS): original and derived data",
        "upload_type": "dataset",
        "publication_date": publication_date.isoformat(),
        "description": DESCRIPTION,
        "access_right": "open",
        "license": "other-pd",
        "creators": [{"name": "Arnold, Jeffrey B."}],
        "keywords": [
            "American Civil War",
            "United States",
            "soldiers",
            "sailors",
            "National Park Service",
            "CWSS",
        ],
        "related_identifiers": [
            {"identifier": REPO_URL, "relation": "isSupplementedBy", "scheme": "url"},
            {"identifier": SOURCE_URL, "relation": "isDerivedFrom", "scheme": "url"},
            {"identifier": SITE_URL, "relation": "isDerivedFrom", "scheme": "url"},
        ],
    }


def md5(path: Path, chunk: int = 1 << 20) -> str:
    """Return the file's md5, the checksum Zenodo reports."""
    digest = hashlib.md5()  # noqa: S324
    with path.open("rb") as f:
        while block := f.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def request(
    url: str,
    token: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Send a JSON request and return the JSON response."""
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method)  # noqa: S310
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as response:  # noqa: S310
        return json.load(response)


def upload_file(bucket: str, path: Path, token: str) -> dict[str, Any]:
    """Stream one file to the draft's bucket, replacing any file of that name."""
    with path.open("rb") as f:
        req = urllib.request.Request(f"{bucket}/{path.name}", data=f, method="PUT")  # noqa: S310
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Length", str(path.stat().st_size))
        req.add_header("Content-Type", "application/octet-stream")
        with urllib.request.urlopen(req, timeout=3600) as response:  # noqa: S310
            return json.load(response)


def check_checksum(path: Path, reported: str) -> None:
    """Fail unless Zenodo's checksum, such as `md5:abc`, matches the local file."""
    expected = md5(path)
    if reported.removeprefix("md5:") != expected:
        raise RuntimeError(f"{path.name}: Zenodo reports {reported}, local md5 is {expected}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deposition", type=int, default=DEPOSITION, help="Zenodo draft id")
    parser.add_argument("--publish", action="store_true", help="publish the draft as it stands")
    args = parser.parse_args()
    token = os.environ["ZENODO_API_KEY"]
    url = f"{API}/{args.deposition}"

    if args.publish:
        done = request(f"{url}/actions/publish", token, method="POST")
        print(f"published {done['doi']}: {done['links']['record_html']}")
        return

    draft = request(url, token)
    for path in FILES:
        print(f"uploading {path} ({path.stat().st_size} bytes)", flush=True)
        uploaded = upload_file(draft["links"]["bucket"], path, token)
        check_checksum(path, uploaded["checksum"])
    request(url, token, method="PUT", payload={"metadata": metadata(datetime.date.today())})
    print(f"draft updated, not published: {draft['links']['html']}")


if __name__ == "__main__":
    main()
