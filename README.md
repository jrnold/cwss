# Civil War Soldiers and Sailors Database

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23905004.svg)](https://doi.org/10.5281/zenodo.23905004)

Data from the National Park Service's (NPS) [Civil War Soldiers and Sailors System](https://www.nps.gov/civilwar/soldiers-and-sailors-database.htm), and the code that turns its SQL Server backup into SQLite and Parquet files you can use without SQL Server.

## Get the data

The data are archived on Zenodo at [doi:10.5281/zenodo.23905004](https://doi.org/10.5281/zenodo.23905004):

| File | Size | Contents |
|---|---|---|
| `CWSS.zip` | 819 MB | The NPS file, unchanged: the SQL Server backup plus the original XML and CSV files |
| `nps_cwss.sqlite3` | 2.2 GB | All 30 tables as a SQLite database |
| `cwss-parquet.tar` | 148 MB | All 30 tables as zstd Parquet files, one per table |

For analysis, use the Parquet files. For example, with [DuckDB](https://duckdb.org/):

```sql
select PER_SIDE, count(*)
from 'parquet/Soldiers_Personz.parquet'
group by PER_SIDE;
```

Collaborators with access to the project's DVC remote can run `dvc pull` instead.

## How the files are built

The source is <https://www.nps.gov/featurecontent/foia/CWSS.zip>, tracked with `dvc import-url`. Only SQL Server can read the backup inside it, so the build restores it in a temporary container. The pipeline is defined in `dvc.yaml`:

```text
data/raw/nps/CWSS.zip
  └ sqlite   → data/processed/nps_cwss.sqlite3
      └ parquet  → data/processed/parquet/<table>.parquet
          └ package  → data/processed/cwss-parquet.tar
```

| Stage | Entry point | Logic | What it does |
|---|---|---|---|
| `runtime-lock` | `uv export` | | Writes `requirements.lock`, so adding a dev tool doesn't rerun the data stages |
| `sqlite` | `scripts/build_sqlite.py` | `src/cwss/restore.py`, `src/cwss/to_sqlite.py` | Extracts the backup, starts SQL Server from `docker/mssql/Dockerfile`, restores the backup, copies each table to SQLite, and removes the container. It fails if any table's row count differs from the source. |
| `parquet` | `scripts/build_parquet.py` | `src/cwss/to_parquet.py` | Writes each table to zstd Parquet, and fails if a primary key has missing or duplicate values |
| `package` | `scripts/package.py` | `src/cwss/to_parquet.py` | Tars the Parquet files with fixed metadata, so the same input gives the same bytes |

`src/cwss/zenodo.py` (`cwss-zenodo-upload`) uploads the three files to the Zenodo draft. It isn't a pipeline stage. Publishing needs its own `--publish` flag, because a published version can't be changed.

To rebuild, you need [uv](https://docs.astral.sh/uv/), Docker, `unzip` and network access. The `sqlite` stage pulls the SQL Server image, and the `parquet` stage downloads DuckDB's SQLite extension.

```console
$ uv sync
$ uv run dvc repro
```

The `sqlite` stage takes about 7 minutes on an Apple Silicon Mac. The SQL Server image is amd64 only, so on Apple Silicon turn on Rosetta in Docker Desktop's settings. To run the tests, which don't need Docker, use `uv run pytest`.

## Tables

The NPS zip has no data dictionary, so these descriptions are inferred from table names, column names and values. Check them against the data before relying on them. The DDL in `docs/` shows the SQL Server definitions, and `docs/unitcodes.yaml` is a lookup of unit codes copied from the NPS website.

| Table | Rows | Columns | Primary key | Description |
|---|---|---|---|---|
| `Category` | 41 | 10 | `PK_ID` | Lookup of category codes and descriptions. |
| `Cemeteries_Info` | 5,672 | 28 | `CT_ID` | Cemetery and headstone records: image, grave number, name, rank and unit. |
| `Cemeteries_Info_unusedColumns` | 5,670 | 14 | none declared | Columns split off from `Cemeteries_Info`, which the NPS table name marks as unused. |
| `Company_Std` | 3,078 | 8 | none declared | Original company names mapped to standardized ones. |
| `Contitle` | 16 | 9 | `STATE` | Headings for Confederate state troops. |
| `MEMORIAL` | 236,518 | 20 | none declared | Another version of the memorial records, with original names and unit codes. |
| `Medal_Ofhonor` | 1,210 | 26 | `MD_RECNUMBER` | Medal of Honor recipients and citations. |
| `Medal_Ofhonor_unusedColumns` | 1,210 | 17 | none declared | Columns split off from `Medal_Ofhonor`, which the NPS table name marks as unused. |
| `Prisoners_Andersonville` | 42,344 | 26 | `PRA_PKEY` | Prisoners at Andersonville. |
| `Prisoners_Andersonville_unusedColumns` | 42,340 | 10 | none declared | Columns split off from `Prisoners_Andersonville`, which the NPS table name marks as unused. |
| `Prisoners_FtCode` | 61 | 9 | `CODE`, `Ft_DESCRIPTION` | Codes used in `Prisoners_FtMcHenry`. |
| `Prisoners_FtMcHenry` | 5,184 | 20 | `PRM_ID` | Prisoners at Fort McHenry. |
| `Rankz` | 752 | 8 | `RANK_CODE` | Rank codes and names. |
| `Regiments_Unitz` | 7,002 | 20 | `REG_UNIT_CODE` | Units: code, side, state, type and history. |
| `Regiments_Unitz_Ext` | 6,997 | 12 | `REG_UNIT_CODE` | More unit details, such as where and when a unit was organized. |
| `SAILORS_CONTISLANDS` | 70 | 3 | none declared | Birthplaces outside the states, for sailors. |
| `Sailors_Enlistinfo` | 17,858 | 12 | `SAL_ENLISTID` | Sailor enlistments: date, place, rating and term. |
| `Sailors_Musterinfo` | 77,884 | 10 | `SAL_PKID` | Sailor musters: date and vessel. |
| `Sailors_Personinfo` | 17,858 | 18 | `SAL_INFOID` | Sailor records: name, birthplace, age, occupation and description. |
| `Sailors_Shipinfo` | 605 | 8 | `SAL_PKID` | Vessels. |
| `SoldiersCountPerState` | 50 | 4 | `StateAbbr` | Count of Union and Confederate soldiers by state. |
| `Soldiers_Filmz` | 1,731 | 8 | `FILM_NBR` | Microfilm numbers and rolls of the source records. |
| `Soldiers_Memorial` | 236,519 | 17 | `MEM_NBR_ORIG` | Records for the African American Civil War Memorial, with plaque IDs. Links to `Soldiers_Personz` through `MEM_PK`. |
| `Soldiers_Memorial_backup` | 236,518 | 10 | `MEM_NBR_ORIG` | Earlier copy of `Soldiers_Memorial`, with fewer columns. |
| `Soldiers_Personz` | 6,270,642 | 24 | `PER_PK` | Soldier records: name, side, unit, company and rank in and out. The main table. |
| `Soldiers_notez` | 2,616,137 | 16 | `PER_NBR_ORIG` | Notes on soldier records. Links to `Soldiers_Personz` through `PER_PK`. |
| `StateCountryName` | 165 | 12 | `STATECOUNTRY_ABBR` | State and country abbreviations and names. |
| `State_Name` | 49 | 8 | `STATE_ABBR` | State abbreviations and names. |
| `Unititle` | 48 | 9 | `STATE` | Headings for Union state troops. |
| `focus` | 245,787 | 117 | none declared | Metadata for images in the NPS Focus digital collection, such as headstone photographs. |

The database's empty `sysdiagrams` table, which SQL Server uses internally, isn't copied.

### Things to know

- **Types:** SQL Server `uniqueidentifier` values are stored as uppercase text with hyphens, such as `00000183-DC7A-DF11-BF36-B8AC6F5D926A`, to match the `varchar` columns that refer to them. `bit` columns are booleans (0/1 in SQLite). `numeric` columns are floats, because SQLite has no exact decimal type.
- **Placeholder dates:** some date columns hold `1753-01-01`, the earliest date a SQL Server `datetime` allows. Treat it as missing.
- **Padding:** fixed-width codes can have trailing spaces, such as `'CS        '`. Trim them before joining.
- **Keys:** tables marked "none declared" have no primary key in the source database, so the build doesn't check their keys.
- **Unmatched links:** not every link resolves. 1 of 236,519 `Soldiers_Memorial` rows and 559 of 2,616,137 `Soldiers_notez` rows have no match in `Soldiers_Personz`.

## Schemas

These come from the built SQLite database. The types are SQLite's, and the Parquet files use the matching DuckDB types.

<details>
<summary><code>Category</code> (10 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `PK_ID` | INTEGER | no | yes |
| `CATEGORY` | VARCHAR(100) | yes |  |
| `ABBR` | VARCHAR(10) | yes |  |
| `DESCRIPTION` | VARCHAR(200) | yes |  |
| `ISDELETE` | BOOLEAN | no |  |
| `PUBDATE` | DATETIME | no |  |
| `UPDATEDATE` | DATETIME | yes |  |
| `UPDATEBY` | VARCHAR(30) | yes |  |
| `UPDATETYPE` | VARCHAR(15) | yes |  |
| `COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Cemeteries_Info</code> (28 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `CT_IMAGE` | VARCHAR(28) | yes |  |
| `CT_GRAVENUMBER` | VARCHAR(5) | yes |  |
| `CT_LASTNAME` | VARCHAR(20) | yes |  |
| `CT_FIRSTNAME` | VARCHAR(20) | yes |  |
| `CT_RANK` | VARCHAR(8) | yes |  |
| `CT_COMPANY` | VARCHAR(10) | yes |  |
| `CT_STATE` | VARCHAR(5) | yes |  |
| `CT_BRANCHOFSERVICE` | VARCHAR(20) | yes |  |
| `CT_SIDE` | VARCHAR(15) | yes |  |
| `CT_TYPE` | VARCHAR(15) | yes |  |
| `CT_DATEOFDEATH` | VARCHAR(20) | yes |  |
| `CT_BURIALPLACE` | VARCHAR(30) | yes |  |
| `CT_RESEARCHCOMMENTS` | VARCHAR(100) | yes |  |
| `CT_PUBLICCOMMENTS` | VARCHAR(100) | yes |  |
| `CT_ENLISTAGE` | VARCHAR(2) | yes |  |
| `CT_ENLISTPLACE` | VARCHAR(50) | yes |  |
| `CT_ENLISTDATE` | VARCHAR(20) | yes |  |
| `CT_OCCUPATION` | VARCHAR(25) | yes |  |
| `CT_RESIDENCE` | VARCHAR(50) | yes |  |
| `CT_UNITNAME` | VARCHAR(70) | yes |  |
| `CT_REGT` | VARCHAR(40) | yes |  |
| `CT_ISDELETE` | BOOLEAN | no |  |
| `CT_PUBDATE` | DATETIME | no |  |
| `CT_UPDATEDATE` | DATETIME | yes |  |
| `CT_UPDATEBY` | INTEGER | yes |  |
| `CT_UPDATETYPE` | VARCHAR(15) | yes |  |
| `CT_COMMENTS` | VARCHAR(255) | yes |  |
| `CT_ID` | INTEGER | no | yes |

</details>

<details>
<summary><code>Cemeteries_Info_unusedColumns</code> (14 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `CT_BLOCK` | VARCHAR(5) | yes |  |
| `CT_STONESHOWS` | VARCHAR(115) | yes |  |
| `CT_BREMER` | VARCHAR(1) | yes |  |
| `CT_REGISTER` | VARCHAR(1) | yes |  |
| `CT_DONE` | VARCHAR(1) | yes |  |
| `CT_TYPEOFSTONE` | VARCHAR(6) | yes |  |
| `CT_NOINFO` | VARCHAR(1) | yes |  |
| `CT_DSG` | VARCHAR(10) | yes |  |
| `CT_REGISTERSHOWS` | VARCHAR(75) | yes |  |
| `CT_REGT` | VARCHAR(40) | yes |  |
| `CT_NBROFBURIALS` | FLOAT | yes |  |
| `CT_FINI` | VARCHAR(1) | yes |  |
| `CT_FOLDER` | VARCHAR(1) | yes |  |
| `CT_ID` | FLOAT | yes |  |

</details>

<details>
<summary><code>Company_Std</code> (8 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `Comp_Name_Orig` | VARCHAR(7) | yes |  |
| `Comp_Name_Std` | VARCHAR(7) | no |  |
| `Comp_Isdelete` | BOOLEAN | no |  |
| `Comp_PubDate` | DATETIME | no |  |
| `Comp_UpdateDate` | DATETIME | yes |  |
| `Comp_UpdateBy` | INTEGER | yes |  |
| `Comp_UpdateType` | VARCHAR(15) | yes |  |
| `Comp_Comments` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Contitle</code> (9 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `STATE` | VARCHAR(3) | no | yes |
| `SIDE` | VARCHAR(2) | yes |  |
| `TITLE` | VARCHAR(50) | yes |  |
| `ISDELETE` | BOOLEAN | no |  |
| `PUBDATE` | DATETIME | no |  |
| `UPDATEDATE` | DATETIME | yes |  |
| `UPDATEBY` | INTEGER | yes |  |
| `UPDATETYPE` | VARCHAR(15) | yes |  |
| `COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>MEMORIAL</code> (20 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `MEM_NBR` | FLOAT | yes |  |
| `MEM_GIV_NAME_ORIG` | VARCHAR(50) | yes |  |
| `MEM_SUR_NAME_ORIG` | VARCHAR(30) | yes |  |
| `MEM_UNIT_CODE` | VARCHAR(12) | yes |  |
| `MEM_AKA_NAME_ORIG` | VARCHAR(50) | yes |  |
| `MEM_NAME_DUP` | VARCHAR(3) | yes |  |
| `MEM_NAME_DUP_PTR` | FLOAT | yes |  |
| `MEM_NAME_SEP_CHAR` | VARCHAR(1) | yes |  |
| `MEM_AKA_SUR_NAME` | VARCHAR(50) | yes |  |
| `MEM_AKA_GIV_NAME` | VARCHAR(50) | yes |  |
| `MEM_GIV_NAME_FULL` | VARCHAR(50) | yes |  |
| `MEM_AKA_GIV_FULL` | VARCHAR(50) | yes |  |
| `MEM_PLAQUE_ID` | VARCHAR(5) | yes |  |
| `MEM_NBR_ORIG` | FLOAT | yes |  |
| `MEM_ISDELETE` | BOOLEAN | no |  |
| `MEM_PUBDATE` | DATETIME | no |  |
| `MEM_UPDATEDATE` | DATETIME | yes |  |
| `MEM_UPDATEBY` | INTEGER | yes |  |
| `MEM_UPDATETYPE` | VARCHAR(15) | yes |  |
| `MEM_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Medal_Ofhonor</code> (26 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `MD_LASTNAME` | VARCHAR(15) | yes |  |
| `MD_FIRSTNAME` | VARCHAR(20) | yes |  |
| `MD_RANKCODE` | VARCHAR(8) | yes |  |
| `MD_CO` | VARCHAR(1) | yes |  |
| `MD_UNITNAME` | VARCHAR(50) | yes |  |
| `MD_CITATIONCITY` | VARCHAR(15) | yes |  |
| `MD_CITATIONSTATE` | VARCHAR(2) | yes |  |
| `MD_CITATIONDATE` | VARCHAR(12) | yes |  |
| `MD_ENTERPL` | VARCHAR(15) | yes |  |
| `MD_ENTERST` | VARCHAR(9) | yes |  |
| `MD_BIRTHPL` | VARCHAR(15) | yes |  |
| `MD_ISSUEDX` | VARCHAR(12) | yes |  |
| `MD_PAGE` | VARCHAR(3) | yes |  |
| `MD_CWUNIT` | VARCHAR(12) | yes |  |
| `MD_RECNUMBER` | FLOAT | no | yes |
| `MD_CITATION` | VARCHAR(2000) | yes |  |
| `MD_BIRTHST` | VARCHAR(7) | yes |  |
| `MD_SIDE` | VARCHAR(1) | yes |  |
| `MD_BRANCHOFSERVICE` | VARCHAR(30) | yes |  |
| `MD_MIDDLEINITIAL` | VARCHAR(7) | yes |  |
| `MD_ISDELETE` | BOOLEAN | no |  |
| `MD_PUBDATE` | DATETIME | no |  |
| `MD_UPDATEDATE` | DATETIME | yes |  |
| `MD_UPDATEBY` | INTEGER | yes |  |
| `MD_UPDATETYPE` | VARCHAR(15) | yes |  |
| `MD_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Medal_Ofhonor_unusedColumns</code> (17 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `MD_RECNUMBER` | FLOAT | yes |  |
| `MD_X` | VARCHAR(1) | yes |  |
| `MD_DATE_R` | DATETIME | yes |  |
| `MD_ISSUED` | DATETIME | yes |  |
| `MD_M` | VARCHAR(4) | yes |  |
| `MD_D` | VARCHAR(3) | yes |  |
| `MD_Y` | VARCHAR(5) | yes |  |
| `MD_CITATION1` | VARCHAR(60) | yes |  |
| `MD_CITATION2` | VARCHAR(60) | yes |  |
| `MD_CITATION3` | VARCHAR(60) | yes |  |
| `MD_CITATION4` | VARCHAR(60) | yes |  |
| `MD_CITATION5` | VARCHAR(60) | yes |  |
| `MD_CITATION6` | VARCHAR(60) | yes |  |
| `MD_CITATION7` | VARCHAR(60) | yes |  |
| `MD_CITATION8` | VARCHAR(60) | yes |  |
| `MD_RUNNING` | FLOAT | yes |  |
| `MD_MIDDLEINITIAL` | VARCHAR(7) | yes |  |

</details>

<details>
<summary><code>Prisoners_Andersonville</code> (26 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `PRA_LASTNAME` | VARCHAR(15) | yes |  |
| `PRA_FIRSTNAME` | VARCHAR(13) | yes |  |
| `PRA_STATE` | VARCHAR(3) | yes |  |
| `PRA_REGIMENT` | VARCHAR(3) | yes |  |
| `PRA_RANK` | VARCHAR(10) | yes |  |
| `PRA_COMPANY` | VARCHAR(1) | yes |  |
| `PRA_FUNCTION` | VARCHAR(15) | yes |  |
| `PRA_CODE` | VARCHAR(5) | yes |  |
| `PRA_REMARKS` | VARCHAR(255) | yes |  |
| `PRA_ALTNAME1` | VARCHAR(13) | yes |  |
| `PRA_ALTNAME2` | VARCHAR(13) | yes |  |
| `PRA_ALTNAME3` | VARCHAR(13) | yes |  |
| `PRA_ALTNAME4` | VARCHAR(13) | yes |  |
| `PRA_UNITNAME` | VARCHAR(35) | yes |  |
| `PRA_STATENAME` | VARCHAR(20) | yes |  |
| `PRA_SIDE` | VARCHAR(1) | yes |  |
| `PRA_CAPTURE` | VARCHAR(20) | yes |  |
| `PRA_DCAP` | DATETIME | yes |  |
| `PRA_TYPEDESCRIPTION` | VARCHAR(120) | yes |  |
| `PRA_ISDELETE` | BOOLEAN | no |  |
| `PRA_PUBDATE` | DATETIME | no |  |
| `PRA_UPDATEDATE` | DATETIME | yes |  |
| `PRA_UPDATEBY` | INTEGER | yes |  |
| `PRA_UPDATETYPE` | VARCHAR(15) | yes |  |
| `PRA_COMMENTS` | VARCHAR(255) | yes |  |
| `PRA_PKEY` | INTEGER | no | yes |

</details>

<details>
<summary><code>Prisoners_Andersonville_unusedColumns</code> (10 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `PRA_PKEY` | FLOAT | yes |  |
| `PRA_GRAVE` | VARCHAR(5) | yes |  |
| `PRA_DCAUSE` | VARCHAR(18) | yes |  |
| `PRA_DDATE` | DATETIME | yes |  |
| `PRA_REF` | VARCHAR(75) | yes |  |
| `PRA_CAPTURE` | VARCHAR(20) | yes |  |
| `PRA_DCAP` | DATETIME | yes |  |
| `PRA_PG` | FLOAT | yes |  |
| `PRA_MORE` | VARCHAR(3) | yes |  |
| `PRA_TOTAL` | FLOAT | yes |  |

</details>

<details>
<summary><code>Prisoners_FtCode</code> (9 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `CODE` | VARCHAR(10) | no | yes |
| `DISPOSITION` | VARCHAR(25) | yes |  |
| `Ft_DESCRIPTION` | VARCHAR(10) | no | yes |
| `FT_ISDELETE` | BOOLEAN | no |  |
| `FT_PUBDATE` | DATETIME | no |  |
| `FT_UPDATEDATE` | DATETIME | yes |  |
| `FT_UPDATEBY` | INTEGER | yes |  |
| `FT_UPDATETYPE` | VARCHAR(15) | yes |  |
| `FT_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Prisoners_FtMcHenry</code> (20 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `PRM_TYPE` | VARCHAR(2) | yes |  |
| `PRM_NAME` | VARCHAR(20) | yes |  |
| `PRM_REGISTRATIONDATE` | DATETIME | yes |  |
| `PRM_RESIDENCE` | VARCHAR(15) | yes |  |
| `PRM_DATEDISP` | DATETIME | yes |  |
| `PRM_DISP` | VARCHAR(4) | yes |  |
| `PRM_HOSPITAL` | VARCHAR(2) | yes |  |
| `PRM_FTRANK` | VARCHAR(2) | yes |  |
| `PRM_NOTES` | VARCHAR(30) | yes |  |
| `PRM_LASTNAME` | VARCHAR(50) | yes |  |
| `PRM_FIRSTNAME` | VARCHAR(50) | yes |  |
| `PRM_RECNUMBER` | FLOAT | yes |  |
| `PRM_ID` | INTEGER | no | yes |
| `PRM_TYPEDESCRIPTION` | VARCHAR(50) | yes |  |
| `PRM_ISDELETE` | BOOLEAN | no |  |
| `PRM_PUBDATE` | DATETIME | no |  |
| `PRM_UPDATEDATE` | DATETIME | yes |  |
| `PRM_UPDATEBY` | INTEGER | yes |  |
| `PRM_UPDATETYPE` | VARCHAR(15) | yes |  |
| `PRM_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Rankz</code> (8 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `RANK_CODE` | VARCHAR(4) | no | yes |
| `RANK_NAME` | VARCHAR(54) | yes |  |
| `RANK_ISDELETE` | BOOLEAN | no |  |
| `RANK_PUBDATE` | DATETIME | no |  |
| `RANK_UPDATEDATE` | DATETIME | yes |  |
| `RANK_UPDATETYPE` | VARCHAR(15) | yes |  |
| `RANK_COMMENTS` | VARCHAR(255) | yes |  |
| `RANK_UPDATEBY` | INTEGER | yes |  |

</details>

<details>
<summary><code>Regiments_Unitz</code> (20 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `REG_UNIT_CODE` | VARCHAR(12) | no | yes |
| `REG_SIDE` | VARCHAR(1) | no |  |
| `REG_STATE` | VARCHAR(2) | no |  |
| `REG_ORDINAL` | VARCHAR(4) | no |  |
| `REG_ARM` | VARCHAR(1) | yes |  |
| `REG_TYPE` | VARCHAR(1) | yes |  |
| `REG_SPECIAL` | VARCHAR(1) | yes |  |
| `REG_DUPLICATE` | VARCHAR(1) | yes |  |
| `REG_ETHNIC` | VARCHAR(1) | yes |  |
| `REG_HISTORY` | TEXT | yes |  |
| `REG_UNIT_NAME` | VARCHAR(110) | yes |  |
| `REG_NOTES` | VARCHAR(200) | yes |  |
| `REG_FUNCTION` | VARCHAR(2) | yes |  |
| `REG_LONGHISTORY` | TEXT | yes |  |
| `REG_ISDELETE` | BOOLEAN | no |  |
| `REG_PUBDATE` | DATETIME | no |  |
| `REG_UPDATEDATE` | DATETIME | yes |  |
| `REG_UPDATEBY` | INTEGER | yes |  |
| `REG_COMMENTS` | VARCHAR(255) | yes |  |
| `REG_UPDATETYPE` | VARCHAR(15) | yes |  |

</details>

<details>
<summary><code>Regiments_Unitz_Ext</code> (12 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `REG_UNIT_CODE` | VARCHAR(12) | no | yes |
| `REG_DUPLICATE` | VARCHAR(1) | yes |  |
| `REG_ORG_CITY` | VARCHAR(25) | yes |  |
| `REG_ORG_COUNTY` | VARCHAR(25) | yes |  |
| `REG_ORG_STATE` | VARCHAR(2) | yes |  |
| `REG_ORG_DATE` | DATETIME | yes |  |
| `REG_EISDELETE` | BOOLEAN | no |  |
| `REG_EPUBDATE` | DATETIME | no |  |
| `REG_EUPDATEDATE` | DATETIME | yes |  |
| `REG_EUPDATEBY` | INTEGER | yes |  |
| `REG_EUPDATETYPE` | VARCHAR(15) | yes |  |
| `REG_ECOMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>SAILORS_CONTISLANDS</code> (3 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `PKID` | VARCHAR(255) | yes |  |
| `CONTISLANDNAMES` | VARCHAR(255) | yes |  |
| `COUNTRYABBR` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Sailors_Enlistinfo</code> (12 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `SAL_ENLISTID` | VARCHAR(7) | no | yes |
| `SAL_DATEENLIST` | DATETIME | yes |  |
| `SAL_RATING` | VARCHAR(24) | yes |  |
| `SAL_PLACENLIST` | VARCHAR(30) | yes |  |
| `SAL_REENLIST` | VARCHAR(50) | yes |  |
| `SAL_TERMENLIST` | VARCHAR(5) | yes |  |
| `SAL_EISDELETE` | BOOLEAN | no |  |
| `SAL_EPUBDATE` | DATETIME | no |  |
| `SAL_EUPDATEDATE` | DATETIME | yes |  |
| `SAL_EUPDATEBY` | INTEGER | yes |  |
| `SAL_EUPDATETYPE` | VARCHAR(15) | yes |  |
| `SAL_ECOMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Sailors_Musterinfo</code> (10 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `SAL_DATEMUSTER` | DATETIME | yes |  |
| `SAL_MUSTERID` | VARCHAR(7) | yes |  |
| `SAL_VESSEL` | VARCHAR(20) | yes |  |
| `SAL_PKID` | INTEGER | no | yes |
| `SAL_MISDELETE` | BOOLEAN | no |  |
| `SAL_MPUBDATE` | DATETIME | no |  |
| `SAL_MUPDATEDATE` | DATETIME | yes |  |
| `SAL_MUPDATEBY` | INTEGER | yes |  |
| `SAL_MUPDATETYPE` | VARCHAR(15) | yes |  |
| `SAL_MCOMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Sailors_Personinfo</code> (18 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `SAL_INFOID` | VARCHAR(7) | no | yes |
| `SAL_LASTNAME` | VARCHAR(15) | yes |  |
| `SAL_FIRSTNAME` | VARCHAR(20) | yes |  |
| `SAL_MIDDLENAME` | VARCHAR(10) | yes |  |
| `SAL_CITYOFBIRTH` | VARCHAR(20) | yes |  |
| `SAL_STATEOFBIRTH` | VARCHAR(18) | yes |  |
| `SAL_AGE` | VARCHAR(22) | yes |  |
| `SAL_OCCUPATION` | VARCHAR(30) | yes |  |
| `SAL_COMPLEXION` | VARCHAR(15) | yes |  |
| `SAL_HEIGHTFEET` | VARCHAR(22) | yes |  |
| `SAL_HEIGHTINCH` | VARCHAR(22) | yes |  |
| `SAL_COUNTRYOFBIRTH` | VARCHAR(18) | yes |  |
| `SAL_ISDELETE` | BOOLEAN | no |  |
| `SAL_PUBDATE` | DATETIME | no |  |
| `SAL_UPDATEDATE` | DATETIME | yes |  |
| `SAL_UPDATEBY` | INTEGER | yes |  |
| `SAL_UPDATETYPE` | VARCHAR(15) | yes |  |
| `SAL_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Sailors_Shipinfo</code> (8 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `SAl_VESSEL` | VARCHAR(20) | yes |  |
| `SAL_PKID` | INTEGER | no | yes |
| `SAL_SISDELETE` | BOOLEAN | no |  |
| `SAL_SPUBDATE` | DATETIME | no |  |
| `SAL_SUPDATE` | DATETIME | yes |  |
| `SAL_SUPDATEBY` | INTEGER | yes |  |
| `SAL_SUPDATETYPE` | VARCHAR(15) | yes |  |
| `SAL_SCOMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>SoldiersCountPerState</code> (4 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `StateAbbr` | VARCHAR(3) | no | yes |
| `UnionCount` | INTEGER | yes |  |
| `ConfederateCount` | INTEGER | yes |  |
| `TotalCount` | INTEGER | yes |  |

</details>

<details>
<summary><code>Soldiers_Filmz</code> (8 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `FILM_NBR` | VARCHAR(7) | no | yes |
| `FILM_ROLL` | VARCHAR(15) | yes |  |
| `FILM_ISDELETE` | BOOLEAN | no |  |
| `FILM_PUBDATE` | DATETIME | no |  |
| `FILM_UPDATEDATE` | DATETIME | yes |  |
| `FILM_UPDATEBY` | INTEGER | yes |  |
| `FILM_UPDATETYPE` | VARCHAR(15) | yes |  |
| `FILM_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Soldiers_Memorial</code> (17 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `MEM_NBR_ORIG` | FLOAT | no | yes |
| `MEM_NAME_DUP` | VARCHAR(3) | yes |  |
| `MEM_NAME_DUP_PTR` | FLOAT | yes |  |
| `MEM_NAME_SEP_CHAR` | VARCHAR(1) | yes |  |
| `MEM_AKA_SUR_NAME` | VARCHAR(50) | yes |  |
| `MEM_AKA_GIV_NAME` | VARCHAR(50) | yes |  |
| `MEM_GIV_NAME_FULL` | VARCHAR(50) | yes |  |
| `MEM_AKA_GIV_FULL` | VARCHAR(50) | yes |  |
| `MEM_PLAQUE_ID` | VARCHAR(5) | yes |  |
| `MEM_PK` | VARCHAR(50) | yes |  |
| `MEM_SUR_NAME_ORIG` | VARCHAR(30) | yes |  |
| `MEM_ISDELETE` | BOOLEAN | no |  |
| `MEM_PUBDATE` | DATETIME | no |  |
| `MEM_UPDATEDATE` | DATETIME | yes |  |
| `MEM_UPDATEBY` | INTEGER | yes |  |
| `MEM_UPDATETYPE` | VARCHAR(15) | yes |  |
| `MEM_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Soldiers_Memorial_backup</code> (10 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `MEM_NBR_ORIG` | FLOAT | no | yes |
| `MEM_NAME_DUP` | VARCHAR(3) | yes |  |
| `MEM_NAME_DUP_PTR` | FLOAT | yes |  |
| `MEM_NAME_SEP_CHAR` | VARCHAR(1) | yes |  |
| `MEM_AKA_SUR_NAME` | VARCHAR(50) | yes |  |
| `MEM_AKA_GIV_NAME` | VARCHAR(50) | yes |  |
| `MEM_GIV_NAME_FULL` | VARCHAR(50) | yes |  |
| `MEM_AKA_GIV_FULL` | VARCHAR(50) | yes |  |
| `MEM_PLAQUE_ID` | VARCHAR(5) | yes |  |
| `MEM_PK` | VARCHAR(50) | yes |  |

</details>

<details>
<summary><code>Soldiers_Personz</code> (24 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `PER_FIRST_NAME` | VARCHAR(50) | yes |  |
| `PER_LAST_NAME` | VARCHAR(40) | yes |  |
| `PER_SIDE` | VARCHAR(1) | yes |  |
| `PER_UNIT_ORIG` | VARCHAR(340) | yes |  |
| `PER_UNIT_CODE` | VARCHAR(12) | yes |  |
| `PER_COMPANY` | VARCHAR(3) | yes |  |
| `PER_RANK_IN_ORIG` | VARCHAR(60) | yes |  |
| `PER_RANK_IN_CODE` | VARCHAR(4) | yes |  |
| `PER_RANK_OUT_ORIG` | VARCHAR(60) | yes |  |
| `PER_RANK_OUT_CODE` | VARCHAR(4) | yes |  |
| `PER_AKA_NAME_ORIG` | VARCHAR(140) | yes |  |
| `PER_BAT_NBR` | VARCHAR(8) | yes |  |
| `PER_FILM_NBR` | VARCHAR(7) | yes |  |
| `PER_NBR_ORIG` | FLOAT | no |  |
| `PER_STATE` | VARCHAR(2) | yes |  |
| `PER_FUNCTION` | VARCHAR(2) | yes |  |
| `PER_UNIT_NUMBER` | VARCHAR(4) | yes |  |
| `PER_PK` | VARCHAR(36) | no | yes |
| `PER_ISDELETE` | BOOLEAN | no |  |
| `PER_PUBDATE` | DATETIME | no |  |
| `PER_UPDATEDATE` | DATETIME | yes |  |
| `PER_UPDATEBY` | INTEGER | yes |  |
| `PER_UPDATETYPE` | VARCHAR(15) | yes |  |
| `PER_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Soldiers_notez</code> (16 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `PER_NBR_ORIG` | FLOAT | no | yes |
| `PER_NOTES` | VARCHAR | yes |  |
| `PER_NAMENOTE` | VARCHAR | yes |  |
| `PER_COMPANYNOTE` | VARCHAR | yes |  |
| `PER_UNITNOTE` | VARCHAR | yes |  |
| `PER_SIDENOTE` | VARCHAR | yes |  |
| `PER_RANKINNOTE` | VARCHAR | yes |  |
| `PER_RANKOUTNOTE` | VARCHAR | yes |  |
| `PER_AKANOTE` | VARCHAR | yes |  |
| `PER_PK` | VARCHAR(50) | yes |  |
| `PER_NISDELETE` | BOOLEAN | no |  |
| `PER_NPUBDATE` | DATETIME | no |  |
| `PER_NUPDATEDATE` | DATETIME | yes |  |
| `PER_NUPDATEBY` | INTEGER | yes |  |
| `PER_NUPDATETYPE` | VARCHAR(15) | yes |  |
| `PER_NCOMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>StateCountryName</code> (12 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `State_Country` | VARCHAR(25) | yes |  |
| `STATECOUNTRY_ABBR` | VARCHAR(5) | no | yes |
| `COLUMN_ABBR` | VARCHAR(70) | yes |  |
| `COLUMN_ABBRDESCRIPTION` | VARCHAR(150) | yes |  |
| `PK_ID` | INTEGER | no |  |
| `NAME` | VARCHAR(50) | yes |  |
| `SC_ISDELETE` | BOOLEAN | no |  |
| `SC_PUBDATE` | DATETIME | no |  |
| `SC_UPDATEDATE` | DATETIME | yes |  |
| `SC_UPDATEBY` | INTEGER | yes |  |
| `SC_UPDATETYPE` | VARCHAR(15) | yes |  |
| `SC_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>State_Name</code> (8 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `STATE_ABBR` | VARCHAR(10) | no | yes |
| `STATE_NAME` | VARCHAR(150) | yes |  |
| `STATE_ISDELETE` | BOOLEAN | no |  |
| `STATE_PUBDATE` | DATETIME | no |  |
| `STATE_UPDATEDATE` | DATETIME | yes |  |
| `STATE_UPDATEBY` | INTEGER | yes |  |
| `STATE_UPDATETYPE` | VARCHAR(15) | yes |  |
| `STATE_COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>Unititle</code> (9 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `STATE` | VARCHAR(3) | no | yes |
| `SIDE` | VARCHAR(2) | yes |  |
| `TITLE` | VARCHAR(50) | yes |  |
| `ISDELETE` | BOOLEAN | no |  |
| `PUBDATE` | DATETIME | no |  |
| `UPDATEDATE` | DATETIME | yes |  |
| `UPDATEBY` | INTEGER | yes |  |
| `UPDATETYPE` | VARCHAR(15) | yes |  |
| `COMMENTS` | VARCHAR(255) | yes |  |

</details>

<details>
<summary><code>focus</code> (117 columns)</summary>

| Column | Type | Nullable | Key |
|---|---|---|---|
| `id` | INTEGER | no |  |
| `datecreated` | VARCHAR(200) | yes |  |
| `coveragetemporal` | VARCHAR(500) | yes |  |
| `begindate` | VARCHAR(50) | yes |  |
| `enddate` | VARCHAR(50) | yes |  |
| `relation` | VARCHAR(500) | yes |  |
| `url` | VARCHAR(500) | yes |  |
| `mrsid1` | VARCHAR(5) | yes |  |
| `server1` | VARCHAR(150) | yes |  |
| `catalog1` | VARCHAR(150) | yes |  |
| `file1` | VARCHAR(150) | yes |  |
| `folder1` | VARCHAR(150) | yes |  |
| `part1` | VARCHAR(150) | yes |  |
| `sourceproperties1` | VARCHAR(5) | yes |  |
| `format1` | VARCHAR(100) | yes |  |
| `filesize1` | VARCHAR(5) | yes |  |
| `width1` | VARCHAR(10) | yes |  |
| `height1` | VARCHAR(10) | yes |  |
| `bitdepth1` | VARCHAR(10) | yes |  |
| `mrsid2` | VARCHAR(5) | yes |  |
| `server2` | VARCHAR(150) | yes |  |
| `catalog2` | VARCHAR(150) | yes |  |
| `file2` | VARCHAR(150) | yes |  |
| `folder2` | VARCHAR(150) | yes |  |
| `part2` | VARCHAR(150) | yes |  |
| `sourceproperties2` | VARCHAR(5) | yes |  |
| `format2` | VARCHAR(100) | yes |  |
| `filesize2` | VARCHAR(5) | yes |  |
| `width2` | VARCHAR(10) | yes |  |
| `height2` | VARCHAR(10) | yes |  |
| `bitdepth2` | VARCHAR(10) | yes |  |
| `mrsid3` | VARCHAR(5) | yes |  |
| `server3` | VARCHAR(150) | yes |  |
| `catalog3` | VARCHAR(150) | yes |  |
| `file3` | VARCHAR(150) | yes |  |
| `folder3` | VARCHAR(150) | yes |  |
| `part3` | VARCHAR(150) | yes |  |
| `sourceproperties3` | VARCHAR(5) | yes |  |
| `format3` | VARCHAR(100) | yes |  |
| `filesize3` | VARCHAR(5) | yes |  |
| `width3` | VARCHAR(10) | yes |  |
| `height3` | VARCHAR(10) | yes |  |
| `bitdepth3` | VARCHAR(10) | yes |  |
| `mrsid4` | VARCHAR(5) | yes |  |
| `server4` | VARCHAR(150) | yes |  |
| `catalog4` | VARCHAR(150) | yes |  |
| `file4` | VARCHAR(150) | yes |  |
| `folder4` | VARCHAR(150) | yes |  |
| `part4` | VARCHAR(150) | yes |  |
| `sourceproperties4` | VARCHAR(5) | yes |  |
| `format4` | VARCHAR(100) | yes |  |
| `filesize4` | VARCHAR(5) | yes |  |
| `width4` | VARCHAR(10) | yes |  |
| `height4` | VARCHAR(10) | yes |  |
| `bitdepth4` | VARCHAR(10) | yes |  |
| `rights` | VARCHAR(200) | yes |  |
| `rightsinfo` | VARCHAR(1500) | yes |  |
| `title` | VARCHAR(500) | yes |  |
| `contributor1` | VARCHAR(200) | yes |  |
| `affiliation1` | VARCHAR(200) | yes |  |
| `role1` | VARCHAR(200) | yes |  |
| `contributor2` | VARCHAR(200) | yes |  |
| `affiliation2` | VARCHAR(200) | yes |  |
| `role2` | VARCHAR(200) | yes |  |
| `contributor3` | VARCHAR(200) | yes |  |
| `affiliation3` | VARCHAR(200) | yes |  |
| `role3` | VARCHAR(200) | yes |  |
| `publisher` | VARCHAR(250) | yes |  |
| `type` | VARCHAR(200) | yes |  |
| `formatmedium` | VARCHAR(250) | yes |  |
| `source` | VARCHAR(400) | yes |  |
| `identifier` | VARCHAR(400) | yes |  |
| `description1` | VARCHAR(2500) | yes |  |
| `description2` | VARCHAR(2500) | yes |  |
| `description3` | VARCHAR(2500) | yes |  |
| `description4` | VARCHAR(2500) | yes |  |
| `subject1` | VARCHAR(150) | yes |  |
| `subject2` | VARCHAR(150) | yes |  |
| `subject3` | VARCHAR(150) | yes |  |
| `subject4` | VARCHAR(150) | yes |  |
| `subject5` | VARCHAR(150) | yes |  |
| `subject6` | VARCHAR(150) | yes |  |
| `parkname` | VARCHAR(300) | yes |  |
| `parkcode` | VARCHAR(10) | yes |  |
| `coveragespatial` | VARCHAR(500) | yes |  |
| `north` | VARCHAR(50) | yes |  |
| `west` | VARCHAR(50) | yes |  |
| `abstract` | VARCHAR(8000) | yes |  |
| `descriptionabstract` | VARCHAR(8000) | yes |  |
| `relationispartof1` | VARCHAR(250) | yes |  |
| `relationispartof2` | VARCHAR(250) | yes |  |
| `relationispartof3` | VARCHAR(250) | yes |  |
| `relationispartof4` | VARCHAR(250) | yes |  |
| `recordstate` | VARCHAR(100) | yes |  |
| `recordowner` | VARCHAR(200) | yes |  |
| `recordview` | VARCHAR(55) | yes |  |
| `recorduid` | VARCHAR(50) | yes |  |
| `recordsetuid` | VARCHAR(50) | yes |  |
| `useruid` | VARCHAR(50) | yes |  |
| `batcreatedate` | VARCHAR(50) | yes |  |
| `batmodifydate` | VARCHAR(50) | yes |  |
| `stateuid` | VARCHAR(50) | yes |  |
| `tableofcontents` | VARCHAR(1000) | yes |  |
| `subjectkeyword` | VARCHAR(1500) | yes |  |
| `titlealternative` | VARCHAR(500) | yes |  |
| `npsnumber` | VARCHAR(250) | yes |  |
| `yyyymmdd` | VARCHAR(10) | yes |  |
| `numbertype` | VARCHAR(100) | yes |  |
| `djvu` | VARCHAR(100) | yes |  |
| `file` | VARCHAR(100) | yes |  |
| `folder` | VARCHAR(100) | yes |  |
| `format` | VARCHAR(100) | yes |  |
| `identifierurl` | VARCHAR(200) | yes |  |
| `language` | VARCHAR(100) | yes |  |
| `server` | VARCHAR(100) | yes |  |
| `catalog` | VARCHAR(100) | yes |  |
| `descriptiontableofcontents` | VARCHAR(500) | yes |  |

</details>

