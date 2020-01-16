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

SET PGHOME=%~dp0\Platforms\PostgreSQL\11.5.1\pgsql
SET PGDATA=%PGHOME%\data
SET PGLOCALEDIR=%PGHOME%\share\locale
SET PATH="%PGHOME%\bin";%PATH%
SET PGDATABASE=postgres
SET PGUSER=postgres
SET PGPORT=5432

SET PYHOME=%~dp0\Libraries\Python\3.7.4

SET true=1
SET false=0


REM ////////////////////// MAIN ///////////////////////////////
CLS
ECHO %whiteText%This script will start and connect to the PostgreSQL database.
ECHO It will automatically set up the PostgreSQL database if needed.
ECHO Type %cyanText%"\q"%whiteText% to quit the PostgreSQL terminal and automatically shutdown the database.%resetText%
ECHO %resetText%

REM "isFirstRun" will be set to %true% or %false%
CALL :checkIsFirstRun isFirstRun

REM Pass the value of "isFirstRun" to the function
CALL :initPostgreSQL %isFirstRun%

REM Start PostgreSQL
ECHO %greenText%Starting PostgreSQL...%resetText%
"%PGHOME%\bin\pg_ctl" -D "%PGHOME%/data" -l %PGHOME%\logfile start

REM Pass the value of "isFirstRun" to the function
CALL :createDatabases %isFirstRun%

REM Start the python server
REM START cmd /k "@echo %greenText%Starting python server...%resetText% && @%PYHOME%\python.exe %~dp0\Server\server.py"

REM Connect to the running database
ECHO %greenText%Connecting to the database...%resetText%
"%PGHOME%\bin\psql" -U %PGUSER% -p %PGPORT%

REM When the user enters "\q" at the PostgreSQL command line, shutdown PostgreSQL
ECHO %greenText%Shutting down PostgreSQL...%resetText%
"%PGHOME%\bin\pg_ctl" -D "%PGHOME%/data" stop

ECHO %greenText%Done%cyanText%
REM pause
pause >nul
ECHO %resetText%




REM ////////////////////// FUNCTIONS ///////////////////////////////
REM Function to check if data folder exists.
REM If not then this is the first run of this script.
: checkIsFirstRun
IF exist %PGDATA% (^
REM ECHO %magentaText%Previous initialization detected%resetText%
SET %~1=%false%
)^
ELSE (^
REM ECHO %magentaText%First run detected%resetText%
SET %~1=%true%
)
EXIT /B 0


REM Function to initialize PostgreSQL if first run.
: initPostgreSQL
IF %~1 EQU %true% (^
ECHO %magentaText%First run detected, initializing PostgreSQL%resetText%
"%PGHOME%\bin\initdb" -U postgres -A trust
)^
ELSE (^
ECHO %magentaText%PostgreSQL previously initialized, skipping%resetText%
)
EXIT /B 0


REM Function to create the databases: "tetres" "cad" and "iris_incident"
REM   if the data folder does not exist.
: createDatabases
IF %~1 EQU %true% (^
ECHO %magentaText%First run detected, creating databases%resetText%
"%PGHOME%\bin\createdb" tetres
"%PGHOME%\bin\createdb" cad
"%PGHOME%\bin\createdb" incident
)^
ELSE (^
ECHO %magentaText%Databases previously created, skipping%resetText%
)
EXIT /B 0






















