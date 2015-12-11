#!/bin/bash
DB=data/new/nps_cwss.sqlite3
DIR=data/new/tsv
SQLITE=sqlite3

if [ -e "$DB" ]
then
    echo "Deleting $DB"
    rm $DB
fi

echo "Creating $DB and adding schema"
$SQLITE $DB < schema.sql

tables=$($SQLITE $DB .tables)
for tbl in $tables
do
    echo "Loading table $tbl into $DB"
    $SQLITE $DB <<EOF
.mode tabs
.header on
.import $DIR/${tbl}.tsv $tbl
EOF
done
