@echo off
SET PGHOME=D:\Portable-PyTICAS\postgresql\App\PgSQL
SET PGDATA=D:\Portable-PyTICAS\postgresql\Data\data

SET PATH="%PGHOME%\bin";%PATH%

"%PGHOME%\bin\pg_dump" -U postgres tetres > Z:\\dump.sql

pause >nul

