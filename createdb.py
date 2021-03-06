#!/usr/bin/env python3
import argparse
import sqlite3
import os
import fnmatch
import csv
from os import path

from sqlalchemy import (create_engine, Table, Column, MetaData, String, Float,
                        DateTime, Boolean, Integer, PrimaryKeyConstraint)

metadata = MetaData()

def clean_row(row):
    for k, v in row.items():
        if v == '':
            row[k] = None
        elif v == 'False':
            row[k] = 0
        elif v == 'True':
            row[k] = 1

table_Category = Table('Category', metadata,
    Column('PK_ID', Integer() , primary_key = True),
    Column('CATEGORY', String(100)),
    Column('ABBR', String(10)),
    Column('DESCRIPTION', String(200)),
    Column('ISDELETE', Boolean() , nullable = False),
    Column('PUBDATE', DateTime() , nullable = False),
    Column('UPDATEDATE', DateTime()),
    Column('UPDATEBY', String(30)),
    Column('UPDATETYPE', String(15)),
    Column('COMMENTS', String(255)))


table_Cemeteries_Info = Table('Cemeteries_Info', metadata,
    Column('CT_IMAGE', String(28) ),
    Column('CT_GRAVENUMBER', String(5) ),
    Column('CT_LASTNAME', String(20) ),
    Column('CT_FIRSTNAME', String(20) ),
    Column('CT_RANK', String(8) ),
    Column('CT_COMPANY', String(10) ),
    Column('CT_STATE', String(5) ),
    Column('CT_BRANCHOFSERVICE', String(20) ),
    Column('CT_SIDE', String(15) ),
    Column('CT_TYPE', String(15) ),
    Column('CT_DATEOFDEATH', String(20) ),
    Column('CT_BURIALPLACE', String(30) ),
    Column('CT_RESEARCHCOMMENTS', String(100) ),
    Column('CT_PUBLICCOMMENTS', String(100) ),
    Column('CT_ENLISTAGE', String(2) ),
    Column('CT_ENLISTPLACE', String(50) ),
    Column('CT_ENLISTDATE', String(20) ),
    Column('CT_OCCUPATION', String(25) ),
    Column('CT_RESIDENCE', String(50) ),
    Column('CT_UNITNAME', String(70) ),
    Column('CT_REGT', String(40) ),
    Column('CT_ISDELETE', Boolean() , nullable = False),
    Column('CT_PUBDATE', DateTime() , nullable = False),
    Column('CT_UPDATEDATE', DateTime() ),
    Column('CT_UPDATEBY', Integer() ),
    Column('CT_UPDATETYPE', String(15) ),
    Column('CT_COMMENTS', String(255) ),
    Column('CT_ID', Integer() , primary_key = True))

table_Cemeteries_Info_unusedColumns = Table('Cemeteries_Info_unusedColumns', metadata,
    Column('CT_BLOCK', String(5) ),
    Column('CT_STONESHOWS', String(115) ),
    Column('CT_BREMER', String(1) ),
    Column('CT_REGISTER', String(1) ),
    Column('CT_DONE', String(1) ),
    Column('CT_TYPEOFSTONE', String(6) ),
    Column('CT_NOINFO', String(1) ),
    Column('CT_DSG', String(10) ),
    Column('CT_REGISTERSHOWS', String(75) ),
    Column('CT_REGT', String(40) ),
    Column('CT_NBROFBURIALS', Float() ),
    Column('CT_FINI', String(1) ),
    Column('CT_FOLDER', String(1) ),
    Column('CT_ID', Float() , primary_key = True))


table_Company_Std = Table('Company_Std', metadata,
                          Column('Comp_Name_Orig', String(7)),
                          Column('Comp_Name_Std', String(7)),
                          Column('Comp_Isdelete', Boolean()),
                          Column('Comp_PubDate', DateTime()),
                          Column('Comp_UpdateDate', DateTime()),
                          Column('Comp_UpdateBy', Integer()),
                          Column('Comp_UpdateType', String(15)),
                          Column('Comp_Comments', String(255)))

table_Contitle = Table('Contitle', metadata,
    Column('STATE', String(3) , primary_key = True),
    Column('SIDE', String(2)),
    Column('TITLE', String(50)),
    Column('ISDELETE', Boolean() , nullable = False),
    Column('PUBDATE', DateTime() , nullable = False),
    Column('UPDATEDATE', DateTime()),
    Column('UPDATEBY', Integer()),
    Column('UPDATETYPE', String(15)),
    Column('COMMENTS', String(255)))

# CREATE TABLE focus (
# 	id Integer() , primary_key = True,
# 	datecreated String(200) ,
# 	coveragetemporal String(500) ,
# 	begindate String(50) ,
# 	enddate String(50) ,
# 	relation String(500) ,
# 	url String(500) ,
# 	mrsid1 String(5) ,
# 	server1 String(150) ,
# 	catalog1 String(150) ,
# 	file1 String(150) ),
# 	folder1 String(150) ),
# 	part1 String(150) ),
# 	sourceproperties1 String(5) ),
# 	format1 String(100) ),
# 	filesize1 String(5) ),
# 	width1 String(10) ),
# 	height1 String(10) ),
# 	bitdepth1 String(10) ),
# 	mrsid2 String(5) ),
# 	server2 String(150) ),
# 	catalog2 String(150) ),
# 	file2 String(150) ),
# 	folder2 String(150) ),
# 	part2 String(150) ),
# 	sourceproperties2 String(5) ),
# 	format2 String(100) ),
# 	filesize2 String(5) ),
# 	width2 String(10) ),
# 	height2 String(10) ),
# 	bitdepth2 String(10) ),
# 	mrsid3 String(5) ),
# 	server3 String(150) ),
# 	catalog3 String(150) ),
# 	file3 String(150) ),
# 	folder3 String(150) ),
# 	part3 String(150) ),
# 	sourceproperties3 String(5) ),
# 	format3 String(100) ),
# 	filesize3 String(5) ),
# 	width3 String(10) ),
# 	height3 String(10) ),
# 	bitdepth3 String(10) ),
# 	mrsid4 String(5) ),
# 	server4 String(150) ),
# 	catalog4 String(150) ),
# 	file4 String(150) ),
# 	folder4 String(150) ),
# 	part4 String(150) ),
# 	sourceproperties4 String(5) ),
# 	format4 String(100) ),
# 	filesize4 String(5) ),
# 	width4 String(10) ),
# 	height4 String(10) ),
# 	bitdepth4 String(10) ),
# 	rights String(200) ),
# 	rightsinfo String(1500) ),
# 	title String(500) ),
# 	contributor1 String(200) ),
# 	affiliation1 String(200) ),
# 	role1 String(200) ),
# 	contributor2 String(200) ),
# 	affiliation2 String(200) ),
# 	role2 String(200) ),
# 	contributor3 String(200) ),
# 	affiliation3 String(200) ),
# 	role3 String(200) ),
# 	publisher String(250) ),
# 	type String(200) ),
# 	formatmedium String(250) ),
# 	source String(400) ),
# 	identifier String(400) ),
# 	description1 String(2500) ),
# 	description2 String(2500) ),
# 	description3 String(2500) ),
# 	description4 String(2500) ),
# 	subject1 String(150) ),
# 	subject2 String(150) ),
# 	subject3 String(150) ),
# 	subject4 String(150) ),
# 	subject5 String(150) ),
# 	subject6 String(150) ),
# 	parkname String(300) ),
# 	parkcode String(10) ),
# 	coveragespatial String(500) ),
# 	north String(50) ),
# 	west String(50) ),
# 	abstract String(8000) ),
# 	descriptionabstract String(8000) ),
# 	relationispartof1 String(250) ),
# 	relationispartof2 String(250) ),
# 	relationispartof3 String(250) ),
# 	relationispartof4 String(250) ),
# 	recordstate String(100) ),
# 	recordowner String(200) ),
# 	recordview String(55) ),
# 	recorduid String(50) ),
# 	recordsetuid String(50) ),
# 	useruid String(50) ),
# 	batcreatedate String(50) ),
# 	batmodifydate String(50) ),
# 	stateuid String(50) ),
# 	tableofcontents String(1000) ),
# 	subjectkeyword String(1500) ),
# 	titlealternative String(500) ),
# 	npsnumber String(250) ),
# 	yyyymmdd String(10) ),
# 	numbertype String(100) ),
# 	djvu String(100) ),
# 	file String(100) ),
# 	folder String(100) ),
# 	format String(100) ),
# 	identifierurl String(200) ),
# 	language String(100) ),
# 	server String(100) ),
# 	catalog String(100) ),
# 	descriptiontableofcontents String(500) 
# )


table_Medal_Ofhonor = Table('Medal_Ofhonor', metadata,
    Column('MD_LASTNAME', String(15) ),
    Column('MD_FIRSTNAME', String(20) ),
    Column('MD_RANKCODE', String(8) ),
    Column('MD_CO', String(1) ),
    Column('MD_UNITNAME', String(50) ),
    Column('MD_CITATIONCITY', String(15) ),
    Column('MD_CITATIONSTATE', String(2) ),
    Column('MD_CITATIONDATE', String(12) ),
    Column('MD_ENTERPL', String(15) ),
    Column('MD_ENTERST', String(9) ),
    Column('MD_BIRTHPL', String(15) ),
    Column('MD_ISSUEDX', String(12) ),
    Column('MD_PAGE', String(3) ),
    Column('MD_CWUNIT', String(12) ),
    Column('MD_RECNUMBER', Float() , primary_key = True),
    Column('MD_CITATION', String(2000) ),
    Column('MD_BIRTHST', String(7) ),
    Column('MD_SIDE', String(1) ),
    Column('MD_BRANCHOFSERVICE', String(30) ),
    Column('MD_MIDDLEINITIAL', String(7) ),
    Column('MD_ISDELETE', Boolean() , nullable = False),
    Column('MD_PUBDATE', DateTime() , nullable = False),
    Column('MD_UPDATEDATE', DateTime() ),
    Column('MD_UPDATEBY', Integer() ),
    Column('MD_UPDATETYPE', String(15) ),
    Column('MD_COMMENTS', String(255) ))

table_Medal_Ofhonor_unusedColumns = Table('Medal_Ofhonor_unusedColumns', metadata,
    Column('MD_RECNUMBER', Float() , primary_key = True),
    Column('MD_X', String(1) ),
    Column('MD_DATE_R', DateTime() ),
    Column('MD_ISSUED', DateTime() ),
    Column('MD_M', String(4) ),
    Column('MD_D', String(3) ),
    Column('MD_Y', String(5) ),
    Column('MD_CITATION1', String(60) ),
    Column('MD_CITATION2', String(60) ),
    Column('MD_CITATION3', String(60) ),
    Column('MD_CITATION4', String(60) ),
    Column('MD_CITATION5', String(60) ),
    Column('MD_CITATION6', String(60) ),
    Column('MD_CITATION7', String(60) ),
    Column('MD_CITATION8', String(60) ),
    Column('MD_RUNNING', Float() ),
    Column('MD_MIDDLEINITIAL', String(7))) 

table_Memorial = Table('Memorial', metadata,
    Column('MEM_NBR', Float() ),
    Column('MEM_GIV_NAME_ORIG', String(50) ),
    Column('MEM_SUR_NAME_ORIG', String(30) ),
    Column('MEM_UNIT_CODE', String(12) ),
    Column('MEM_AKA_NAME_ORIG', String(50) ),
    Column('MEM_NAME_DUP', String(3) ),
    Column('MEM_NAME_DUP_PTR', Float() ),
    Column('MEM_NAME_SEP_CHAR', String(1) ),
    Column('MEM_AKA_SUR_NAME', String(50) ),
    Column('MEM_AKA_GIV_NAME', String(50) ),
    Column('MEM_GIV_NAME_FULL', String(50) ),
    Column('MEM_AKA_GIV_FULL', String(50) ),
    Column('MEM_PLAQUE_ID', String(5) ),
    Column('MEM_NBR_ORIG', Float() ),
    Column('MEM_ISDELETE', Boolean() , nullable = False),
    Column('MEM_PUBDATE', DateTime() , nullable = False),
    Column('MEM_UPDATEDATE', DateTime() ),
    Column('MEM_UPDATEBY', Integer() ),
    Column('MEM_UPDATETYPE', String(15) ),
    Column('MEM_COMMENTS', String(255)))


table_Prisoners_Andersonville = Table('Prisoners_Andersonville', metadata,
                                      Column('PRA_LASTNAME', String(15) ),
                                      Column('PRA_FIRSTNAME', String(13) ),
                                      Column('PRA_STATE', String(3) ),
                                      Column('PRA_REGIMENT', String(3) ),
                                      Column('PRA_RANK', String(10) ),
                                      Column('PRA_COMPANY', String(1) ),
                                      Column('PRA_FUNCTION', String(15) ),
                                      Column('PRA_CODE', String(5) ),
                                      Column('PRA_REMARKS', String(255) ),
                                      Column('PRA_ALTNAME1', String(13) ),
                                      Column('PRA_ALTNAME2', String(13) ),
                                      Column('PRA_ALTNAME3', String(13) ),
                                      Column('PRA_ALTNAME4', String(13) ),
                                      Column('PRA_UNITNAME', String(35) ),
                                      Column('PRA_STATENAME', String(20) ),
                                      Column('PRA_SIDE', String(1) ),
                                      Column('PRA_CAPTURE', String(20) ),
                                      Column('PRA_DCAP', DateTime() ),
                                      Column('PRA_TYPEDESCRIPTION', String(120) ),
                                      Column('PRA_ISDELETE', Boolean() , nullable = False),
                                      Column('PRA_PUBDATE', DateTime() , nullable = False),
                                      Column('PRA_UPDATEDATE', DateTime() ),
                                      Column('PRA_UPDATEBY', Integer() ),
                                      Column('PRA_UPDATETYPE', String(15) ),
                                      Column('PRA_COMMENTS', String(255) ),
                                      Column('PRA_PKEY', Integer() , primary_key = True))

table_Prisoners_Andersonville_unusedColumns = Table('Prisoners_Andersonville_unusedColumns', metadata, 
    Column('PRA_PKEY', Integer(), primary_key = True),
    Column('PRA_GRAVE', String(5) ),
    Column('PRA_DCAUSE', String(18) ),
    Column('PRA_DDATE', DateTime() ),
    Column('PRA_REF', String(75) ),
    Column('PRA_CAPTURE', String(20) ),
    Column('PRA_DCAP', DateTime() ),
    Column('PRA_PG', Float() ),
    Column('PRA_MORE', String(3) ),
    Column('PRA_TOTAL', Float()))

table_Prisoners_FtCode = Table('Prisoners_FtCode', metadata,
                               Column('CODE', String(10) , nullable = False),
                               Column('DISPOSITION', String(25) ),
                               Column('FT_DESCRIPTION', String(10) , nullable = False),
                               Column('FT_ISDELETE', Boolean() , nullable = False),
                               Column('FT_PUBDATE', DateTime() , nullable = False),
                               Column('FT_UPDATEDATE', DateTime() ),
                               Column('FT_UPDATEBY', Integer() ),
                               Column('FT_UPDATETYPE', String(15) ),
                               Column('FT_COMMENTS', String(255) ),
                               PrimaryKeyConstraint('CODE', 'FT_DESCRIPTION'))


table_Prisoners_FtMcHenry = Table('Prisoners_FtMcHenry', metadata,
    Column('PRM_TYPE', String(2) ),
    Column('PRM_NAME', String(20) ),
    Column('PRM_REGISTRATIONDATE', DateTime() ),
    Column('PRM_RESIDENCE', String(15) ),
    Column('PRM_DATEDISP', DateTime() ),
    Column('PRM_DISP', String(4) ),
    Column('PRM_HOSPITAL', String(2) ),
    Column('PRM_FTRANK', String(2) ),
    Column('PRM_NOTES', String(30) ),
    Column('PRM_LASTNAME', String(50) ),
    Column('PRM_FIRSTNAME', String(50) ),
    Column('PRM_RECNUMBER', Float() ),
    Column('PRM_ID', Integer() , primary_key = True),
    Column('PRM_TYPEDESCRIPTION', String(50) ),
    Column('PRM_ISDELETE', Boolean() , nullable = False),
    Column('PRM_PUBDATE', DateTime() , nullable = False),
    Column('PRM_UPDATEDATE', DateTime() ),
    Column('PRM_UPDATEBY', Integer() ),
    Column('PRM_UPDATETYPE', String(15) ),
    Column('PRM_COMMENTS', String(255) ))

table_Rankz = Table('Rankz', metadata,
    Column('RANK_CODE', String(4) , nullable = False),
    Column('RANK_NAME', String(54)),
    Column('RANK_ISDELETE', Boolean() , nullable = False),
    Column('RANK_PUBDATE', DateTime() , nullable = False),
    Column('RANK_UPDATEDATE', DateTime()),
    Column('RANK_UPDATETYPE', String(15)),
    Column('RANK_COMMENTS', String(255)),
    Column('RANK_UPDATEBY', Integer()))

table_Regiments_Unitz = Table('Regiments_Unitz', metadata,
    Column('REG_UNIT_CODE', String(12) , primary_key = True , nullable = False),
    Column('REG_SIDE', String(1) , nullable = False),
    Column('REG_STATE', String(2) , nullable = False),
    Column('REG_ORDINAL', String(4) , nullable = False),
    Column('REG_ARM', String(1)),
    Column('REG_TYPE', String(1)),
    Column('REG_SPECIAL', String(1)),
    Column('REG_DUPLICATE', String(1)),
    Column('REG_ETHNIC', String(1)),
    Column('REG_HISTORY', String()),
    Column('REG_UNIT_NAME', String(110)),
    Column('REG_NOTES', String(200)),
    Column('REG_FUNCTION', String(2)),
    Column('REG_LONGHISTORY', String()),
    Column('REG_ISDELETE', Boolean() , nullable = False),
    Column('REG_PUBDATE', DateTime() , nullable = False),
    Column('REG_UPDATEDATE', DateTime()),
    Column('REG_UPDATEBY', Integer()),
    Column('REG_COMMENTS', String(255)),
    Column('REG_UPDATETYPE', String(15)))

table_Regiments_Unitz_Ext = Table('Regiments_Unitz_Ext', metadata,
    Column('REG_UNIT_CODE', String(12) , primary_key = True),
    Column('REG_DUPLICATE', String(1) ),
    Column('REG_ORG_CITY', String(25) ),
    Column('REG_ORG_COUNTY', String(25) ),
    Column('REG_ORG_STATE', String(2) ),
    Column('REG_ORG_DATE', DateTime() ),
    Column('REG_EISDELETE', Boolean() , nullable = False),
    Column('REG_EPUBDATE', DateTime() , nullable = False),
    Column('REG_EUPDATEDATE', DateTime() ),
    Column('REG_EUPDATEBY', Integer() ),
    Column('REG_EUPDATETYPE', String(15) ),
    Column('REG_ECOMMENTS', String(255) ))

table_SAILORS_CONTISLANDS = Table('SAILORS_CONTISLANDS', metadata,
    Column('PKID', String(255)),
    Column('CONTISLANDNAMES', String(255)),
    Column('COUNTRYABBR', String(255)))

table_Sailors_Enlistinfo = Table('Sailors_Enlistinfo', metadata,
    Column('SAL_ENLISTID', String(7) , primary_key = True),
    Column('SAL_DATEENLIST', DateTime() ),
    Column('SAL_RATING', String(24) ),
    Column('SAL_PLACENLIST', String(30) ),
    Column('SAL_REENLIST', String(50) ),
    Column('SAL_TERMENLIST', String(5) ),
    Column('SAL_EISDELETE', Boolean() , nullable = False),
    Column('SAL_EPUBDATE', DateTime() , nullable = False),
    Column('SAL_EUPDATEDATE', DateTime() ),
    Column('SAL_EUPDATEBY', Integer() ),
    Column('SAL_EUPDATETYPE', String(15) ),
    Column('SAL_ECOMMENTS', String(255) ))

table_Sailors_Musterinfo = Table('Sailors_Musterinfo', metadata,
    Column('SAL_DATEMUSTER', DateTime() ),
    Column('SAL_MUSTERID', String(7) ),
    Column('SAL_VESSEL', String(20) ),
    Column('SAL_PKID', Integer() , primary_key = True),
    Column('SAL_MISDELETE', Boolean() , nullable = False),
    Column('SAL_MPUBDATE', DateTime() , nullable = False),
    Column('SAL_MUPDATEDATE', DateTime() ),
    Column('SAL_MUPDATEBY', Integer() ),
    Column('SAL_MUPDATETYPE', String(15) ),
    Column('SAL_MCOMMENTS', String(255) ))

table_Sailors_Personinfo = Table('Sailors_Personinfo', metadata,
    Column('SAL_INFOID', String(7) , primary_key = True),
    Column('SAL_LASTNAME', String(15) ),
    Column('SAL_FIRSTNAME', String(20) ),
    Column('SAL_MIDDLENAME', String(10) ),
    Column('SAL_CITYOFBIRTH', String(20) ),
    Column('SAL_STATEOFBIRTH', String(18) ),
    Column('SAL_AGE', String(22) ),
    Column('SAL_OCCUPATION', String(30) ),
    Column('SAL_COMPLEXION', String(15) ),
    Column('SAL_HEIGHTFEET', String(22) ),
    Column('SAL_HEIGHTINCH', String(22) ),
    Column('SAL_COUNTRYOFBIRTH', String(18) ),
    Column('SAL_ISDELETE', Boolean() , nullable = False),
    Column('SAL_PUBDATE', DateTime() , nullable = False),
    Column('SAL_UPDATEDATE', DateTime() ),
    Column('SAL_UPDATEBY', Integer() ),
    Column('SAL_UPDATETYPE', String(15) ),
    Column('SAL_COMMENTS', String(255)))

table_Sailors_Shipinfo = Table('Sailors_Shipinfo', metadata,
    Column('SAL_VESSEL', String(20) ),
    Column('SAL_PKID', Integer() , primary_key = True),
    Column('SAL_SISDELETE', Boolean() , nullable = False),
    Column('SAL_SPUBDATE', DateTime() , nullable = False),
    Column('SAL_SUPDATE', DateTime() ),
    Column('SAL_SUPDATEBY', Integer() ),
    Column('SAL_SUPDATETYPE', String(15) ),
    Column('SAL_SCOMMENTS', String(255) ))

table_SoldiersCountPerState = Table('SoldiersCountPerState', metadata,
    Column('StateAbbr', String(3) , primary_key = True),
    Column('UnionCount', Integer() ),
    Column('ConfederateCount', Integer() ),
    Column('TotalCount', Integer() ))

table_Soldiers_Filmz = Table('Soldiers_Filmz', metadata,
    Column('FILM_NBR', String(7) , primary_key = True),
    Column('FILM_ROLL', String(15) ),
    Column('FILM_ISDELETE', Boolean() , nullable = False),
    Column('FILM_PUBDATE', DateTime() , nullable = False),
    Column('FILM_UPDATEDATE', DateTime() ),
    Column('FILM_UPDATEBY', Integer() ),
    Column('FILM_UPDATETYPE', String(15) ),
    Column('FILM_COMMENTS', String(255) ))

table_Soldiers_Memorial = Table('Soldiers_Memorial', metadata,
    Column('MEM_NBR_ORIG', Float() , primary_key = True),
    Column('MEM_NAME_DUP', String(3) ),
    Column('MEM_NAME_DUP_PTR', Float() ),
    Column('MEM_NAME_SEP_CHAR', String(1) ),
    Column('MEM_AKA_SUR_NAME', String(50) ),
    Column('MEM_AKA_GIV_NAME', String(50) ),
    Column('MEM_GIV_NAME_FULL', String(50) ),
    Column('MEM_AKA_GIV_FULL', String(50) ),
    Column('MEM_PLAQUE_ID', String(5) ),
    Column('MEM_PK', String(50) ),
    Column('MEM_SUR_NAME_ORIG', String(30) ),
    Column('MEM_ISDELETE', Boolean() , nullable = False),
    Column('MEM_PUBDATE', DateTime() , nullable = False),
    Column('MEM_UPDATEDATE', DateTime() ),
    Column('MEM_UPDATEBY', Integer() ),
    Column('MEM_UPDATETYPE', String(15) ),
    Column('MEM_COMMENTS', String(255) ))

table_Soldiers_Memorial_backup = Table('table_Soldiers_Memorial_backup', metadata,
    Column('MEM_NBR_ORIG', Float() , primary_key = True),
    Column('MEM_NAME_DUP', String(3) ),
    Column('MEM_NAME_DUP_PTR', Float() ),
    Column('MEM_NAME_SEP_CHAR', String(1) ),
    Column('MEM_AKA_SUR_NAME', String(50) ),
    Column('MEM_AKA_GIV_NAME', String(50) ),
    Column('MEM_GIV_NAME_FULL', String(50) ),
    Column('MEM_AKA_GIV_FULL', String(50) ),
    Column('MEM_PLAQUE_ID', String(5) ),
    Column('MEM_PK', String(50)))


table_Soldiers_notez = Table('Soldiers_notez', metadata,
    Column('PER_NBR_ORIG', Float() , primary_key = True),
    Column('PER_NOTES', String() ),
    Column('PER_NAMENOTE', String() ),
    Column('PER_COMPANYNOTE', String() ),
    Column('PER_UNITNOTE', String() ),
    Column('PER_SIDENOTE', String() ),
    Column('PER_RANKINNOTE', String() ),
    Column('PER_RANKOUTNOTE', String() ),
    Column('PER_AKANOTE', String() ),
    Column('PER_PK', String(50) ),
    Column('PER_NISDELETE', Boolean() , nullable = False),
    Column('PER_NPUBDATE', DateTime() , nullable = False),
    Column('PER_NUPDATEDATE', DateTime() ),
    Column('PER_NUPDATEBY', Integer() ),
    Column('PER_NUPDATETYPE', String(15) ),
    Column('PER_NCOMMENTS', String(255) ))


table_Soldiers_Personz = Table('Soldiers_Personz', metadata,
    Column('PER_FIRST_NAME', String(50) ),
    Column('PER_LAST_NAME', String(40) ),
    Column('PER_SIDE', String(1) ),
    Column('PER_UNIT_ORIG', String(340) ),
    Column('PER_UNIT_CODE', String(12) ),
    Column('PER_COMPANY', String(3) ),
    Column('PER_RANK_IN_ORIG', String(60) ),
    Column('PER_RANK_IN_CODE', String(4) ),
    Column('PER_RANK_OUT_ORIG', String(60) ),
    Column('PER_RANK_OUT_CODE', String(4) ),
    Column('PER_AKA_NAME_ORIG', String(140) ),
    Column('PER_BAT_NBR', String(8) ),
    Column('PER_FILM_NBR', String(7) ),
    Column('PER_NBR_ORIG', Float() , nullable = False),
    Column('PER_STATE', String(2) ),
    Column('PER_FUNCTION', String(2) ),
    Column('PER_UNIT_NUMBER', String(4) ),
    Column('PER_PK', String(32), primary_key = True),
    Column('PER_ISDELETE', Boolean() , nullable = False),
    Column('PER_PUBDATE', DateTime() , nullable = False),
    Column('PER_UPDATEDATE', DateTime() ),
    Column('PER_UPDATEBY', Integer() ),
    Column('PER_UPDATETYPE', String(15) ),
    Column('PER_COMMENTS', String(255) ))

table_StateCountryName = Table('StateCountryName', metadata,
    Column('State_Country', String(25) ),
    Column('STATECOUNTRY_ABBR', String(5) , primary_key = True),
    Column('COLUMN_ABBR', String(70) ),
    Column('COLUMN_ABBRDESCRIPTION', String(150) ),
    Column('PK_ID', Integer(), nullable = False),
    Column('NAME', String(50) ),
    Column('SC_ISDELETE', Boolean() , nullable = False),
    Column('SC_PUBDATE', DateTime() , nullable = False),
    Column('SC_UPDATEDATE', DateTime() ),
    Column('SC_UPDATEBY', Integer() ),
    Column('SC_UPDATETYPE', String(15) ),
    Column('SC_COMMENTS', String(255)))

table_State_Name = Table('State_Name', metadata,
    Column('STATE_ABBR', String(10) , primary_key = True , nullable = False),
    Column('STATE_NAME', String(150) ),
    Column('STATE_ISDELETE', Boolean() , nullable = False),
    Column('STATE_PUBDATE', DateTime() , nullable = False),
    Column('STATE_UPDATEDATE', DateTime()),
    Column('STATE_UPDATEBY', Integer()),
    Column('STATE_UPDATETYPE', String(15)),
    Column('STATE_COMMENTS', String(255)))

table_Unititle = Table('Unititle', metadata,
    Column('STATE', String(3) , primary_key = True),
    Column('SIDE', String(2)),
    Column('TITLE', String(50)),
    Column('ISDELETE', Boolean() , nullable = False),
    Column('PUBDATE', DateTime() , nullable = False),
    Column('UPDATEDATE', DateTime()),
    Column('UPDATEBY', Integer()),
    Column('UPDATETYPE', String(15)),
    Column('COMMENTS', String(255)))


# def mssql_to_sqlite(args):
#     mssql_engine = create_engine("mssql+pyodbc://nps_cwss")
#     meta = MetaData()
#     meta.reflect(bind = mssql_engine)
#     sqlite_engine = create_engine("sqlite://:memory:")

def tsv_to_sqlite(filename, table):
    ins = metadata.tables[table].insert()
    con = metadata.bind.connect()
    print("Loading %s into table %s" % (filename, table))
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, delimiter = '\t')
        for row in reader:
            clean_row(row)
            con.execute(ins, **row)

def tsv_to_sqlite_multi(src, db):
    engine = create_engine(db)
    metadata.bind = engine
    metadata.drop_all()
    metadata.create_all()
    for filename in os.listdir(src):
        if fnmatch.fnmatch(filename, "*.tsv"):
            fname = path.join(src, filename)
            table = path.splitext(filename)[0]
            tsv_to_sqlite(fname, table)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', metavar = 'SRC', help = 'directory with input tsv files')    
    parser.add_argument('db', metavar = 'DB', help = 'SQLite database')
    args = parser.parse_args()
    tsv_to_sqlite_multi(args.SRC, args.DB)

if __name__ == '__main__':
    main()

