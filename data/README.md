# Data

## Sources

One row per directory in `data/raw/`. Add the row in the commit that adds the data.

| Directory | Source | Retrieved | Version | License | How to fetch |
|---|---|---|---|---|---|
| `raw/nps` | [National Park Service FOIA reading room](https://www.nps.gov/aboutus/foia/foia-frd.htm): <https://www.nps.gov/featurecontent/foia/CWSS.zip> | 2026-11-02 | Last modified 2021-08-20, ETag `5b76eff9ee95d71:0`; backup dated 2012-10-31 | US government work; recorded on Zenodo as public domain (`other-pd`) | `dvc import-url`; refresh with `dvc update data/raw/nps/CWSS.zip.dvc` |

## Tables

One row per table in `data/processed/`. See the README for what each table holds and its schema.

| Table | One row per | Key | Stage | Notes |
|---|---|---|---|---|
| `processed/nps_cwss.sqlite3` | Database with 30 tables | Per table, as in the rows below | `sqlite` | Distribution copy of the database |
| `processed/cwss-parquet.tar` | Tar of `processed/parquet/` | | `package` | Distribution copy for Zenodo |
| `processed/parquet/Category.parquet` | One row of `Category` | `PK_ID` | `parquet` | 41 rows |
| `processed/parquet/Cemeteries_Info.parquet` | One row of `Cemeteries_Info` | `CT_ID` | `parquet` | 5,672 rows |
| `processed/parquet/Cemeteries_Info_unusedColumns.parquet` | One row of `Cemeteries_Info_unusedColumns` | none declared | `parquet` | 5,670 rows |
| `processed/parquet/Company_Std.parquet` | One row of `Company_Std` | none declared | `parquet` | 3,078 rows |
| `processed/parquet/Contitle.parquet` | One row of `Contitle` | `STATE` | `parquet` | 16 rows |
| `processed/parquet/MEMORIAL.parquet` | One row of `MEMORIAL` | none declared | `parquet` | 236,518 rows |
| `processed/parquet/Medal_Ofhonor.parquet` | One row of `Medal_Ofhonor` | `MD_RECNUMBER` | `parquet` | 1,210 rows |
| `processed/parquet/Medal_Ofhonor_unusedColumns.parquet` | One row of `Medal_Ofhonor_unusedColumns` | none declared | `parquet` | 1,210 rows |
| `processed/parquet/Prisoners_Andersonville.parquet` | One row of `Prisoners_Andersonville` | `PRA_PKEY` | `parquet` | 42,344 rows |
| `processed/parquet/Prisoners_Andersonville_unusedColumns.parquet` | One row of `Prisoners_Andersonville_unusedColumns` | none declared | `parquet` | 42,340 rows |
| `processed/parquet/Prisoners_FtCode.parquet` | One row of `Prisoners_FtCode` | `CODE`, `Ft_DESCRIPTION` | `parquet` | 61 rows |
| `processed/parquet/Prisoners_FtMcHenry.parquet` | One row of `Prisoners_FtMcHenry` | `PRM_ID` | `parquet` | 5,184 rows |
| `processed/parquet/Rankz.parquet` | One row of `Rankz` | `RANK_CODE` | `parquet` | 752 rows |
| `processed/parquet/Regiments_Unitz.parquet` | One row of `Regiments_Unitz` | `REG_UNIT_CODE` | `parquet` | 7,002 rows |
| `processed/parquet/Regiments_Unitz_Ext.parquet` | One row of `Regiments_Unitz_Ext` | `REG_UNIT_CODE` | `parquet` | 6,997 rows |
| `processed/parquet/SAILORS_CONTISLANDS.parquet` | One row of `SAILORS_CONTISLANDS` | none declared | `parquet` | 70 rows |
| `processed/parquet/Sailors_Enlistinfo.parquet` | One row of `Sailors_Enlistinfo` | `SAL_ENLISTID` | `parquet` | 17,858 rows |
| `processed/parquet/Sailors_Musterinfo.parquet` | One row of `Sailors_Musterinfo` | `SAL_PKID` | `parquet` | 77,884 rows |
| `processed/parquet/Sailors_Personinfo.parquet` | One row of `Sailors_Personinfo` | `SAL_INFOID` | `parquet` | 17,858 rows |
| `processed/parquet/Sailors_Shipinfo.parquet` | One row of `Sailors_Shipinfo` | `SAL_PKID` | `parquet` | 605 rows |
| `processed/parquet/SoldiersCountPerState.parquet` | One row of `SoldiersCountPerState` | `StateAbbr` | `parquet` | 50 rows |
| `processed/parquet/Soldiers_Filmz.parquet` | One row of `Soldiers_Filmz` | `FILM_NBR` | `parquet` | 1,731 rows |
| `processed/parquet/Soldiers_Memorial.parquet` | One row of `Soldiers_Memorial` | `MEM_NBR_ORIG` | `parquet` | 236,519 rows |
| `processed/parquet/Soldiers_Memorial_backup.parquet` | One row of `Soldiers_Memorial_backup` | `MEM_NBR_ORIG` | `parquet` | 236,518 rows |
| `processed/parquet/Soldiers_Personz.parquet` | One row of `Soldiers_Personz` | `PER_PK` | `parquet` | 6,270,642 rows |
| `processed/parquet/Soldiers_notez.parquet` | One row of `Soldiers_notez` | `PER_NBR_ORIG` | `parquet` | 2,616,137 rows |
| `processed/parquet/StateCountryName.parquet` | One row of `StateCountryName` | `STATECOUNTRY_ABBR` | `parquet` | 165 rows |
| `processed/parquet/State_Name.parquet` | One row of `State_Name` | `STATE_ABBR` | `parquet` | 49 rows |
| `processed/parquet/Unititle.parquet` | One row of `Unititle` | `STATE` | `parquet` | 48 rows |
| `processed/parquet/focus.parquet` | One row of `focus` | none declared | `parquet` | 245,787 rows |
