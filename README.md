# Civil War Sailors and Soldiers Database

Data from the National Park Service's [Civil War Soldiers and Sailors Database](http://www.nps.gov/civilwar/soldiers-and-sailors-database.htm), received by request from the [National Park Service](http://www.nps.gov/aboutus/contactus.htm) and code to (1) dump the tables to tsv and

# Download files

The original files from the CWSS is stored on AWS due to their size. 

- `data/orig/battle.xml`: Battles
- `data/orig/battleunitlink.xml`: Links military units to battles
- `data/orig/units.xml`: Units 
- `data/orig/NPS_BattlefieldParks.csv`: List of parks and the battles associated with those parks.
- `data/orig/nps_cwss-20121031.bak` The MS SQLServer database backup with the CWSS database.
- `data/new/tsv/*.tsv` tsv files of the tables in the database
- `data/nps_cwss-20121013.sqlite3` Database as a SQLite database

# Scripts

To download the data
```console
$ download.sh
```

To dump the MS SQL database to tab-separated value (tsv) files:
```console
$ python3 mssql_to_tsv.py ENGINE DST
```
Where `ENGINE` is a valid database engine specification in [SQLAlchemy](http://docs.sqlalchemy.org/en/latest/dialects/mssql.html#module-sqlalchemy.dialects.mssql.pyodbc). `DST` is the directory in which to dump the tables. It will be created if it does not already exist.
This requires `SQLalchemy`.

Create a new SQLite database from those `tsv` files
```console
$ createdb.sh        
```

