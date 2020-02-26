@ECHO OFF
REM The script sets environment variables helpful for PostgreSQL
REM This script should be inside the root of the PostgreSQL folder (save folder as "bin")
REM On the first run it will initialize PostgreSQL and create the databases.
REM @command hides command ECHOing. only use for @ECHO off


REM ////////////////////// VARIABLES ///////////////////////////////
SET redText=[91m
SET greenText=[92m
SET yellowText=[93m
SET magentaText=[95m
SET cyanText=[96m
SET whiteText=[97m
SET resetText=[0m



SET PGHOME=D:\Portable-PyTICAS\postgresql\App\PgSQL
SET PGDATA=D:\Portable-PyTICAS\postgresql\Data\data

SET PATH="%PGHOME%\bin";%PATH%
SET PGUSER=postgres
SET PGPORT=5432


REM ////////////////////// MAIN ///////////////////////////////
CLS

REM Start PostgreSQL
REM ECHO %greenText%Starting PostgreSQL...%resetText%
REM "%PGHOME%\bin\pg_ctl" -D "%PGDATA%" start


REM Connect to the running database
ECHO %greenText%Connecting to the database...%resetText%
"%PGHOME%\bin\psql" -U %PGUSER% -p %PGPORT%

REM When the user enters "\q" at the PostgreSQL command line, shutdown PostgreSQL
REM ECHO %greenText%Shutting down PostgreSQL...%resetText%
REM "%PGHOME%\bin\pg_ctl" -D "%PGDATA%" stop

REM ECHO %greenText%Done%cyanText%
REM pause
pause >nul
ECHO %resetText%


