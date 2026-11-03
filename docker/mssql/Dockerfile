# SQL Server for Linux. The sqlite stage runs this once to read the NPS backup, which only SQL
# Server can restore, then deletes the container. The image is amd64 only, so on Apple Silicon it
# needs Docker Desktop's Rosetta emulation.
FROM --platform=linux/amd64 mcr.microsoft.com/mssql/server:2022-CU27-GDR1-ubuntu-22.04

ENV ACCEPT_EULA=Y
ENV MSSQL_PID=Developer
