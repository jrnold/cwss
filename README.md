# Civil War Sailors and Soldiers Database

Data from the National Park Service's [Civil War Soldiers and Sailors Database](http://www.nps.gov/civilwar/soldiers-and-sailors-database.htm), received by request from the [National Park Service](http://www.nps.gov/aboutus/contactus.htm) and code to (1) dump the tables to tsv and

# Other scripts

To load the tables in the `.tsv` files into a SQLite database run
```console
$ python createdb.py data sqlite:///path/to/dbname.sqlite
```

The original CWSS database was a MS SQL database backup file. To make it easier to work with the data I dumped it to tab-separated files.
The file `mssql_to_tsv.py` is the script that was used to create the `.tsv` files distributed with this data.
It should not be necessary to run it, but it distributed for reproducibility or to make it easier to migrate the database to another engine.
```console
$ python3 mssql_to_tsv.py ENGINE DST
```
Where `ENGINE` is a valid database engine specification in [SQLAlchemy](http://docs.sqlalchemy.org/en/latest/dialects/mssql.html#module-sqlalchemy.dialects.mssql.pyodbc). `DST` is the directory in which to dump the tables. It will be created if it does not already exist.
This requires [SQLAlchemy](http://www.sqlalchemy.org/).
