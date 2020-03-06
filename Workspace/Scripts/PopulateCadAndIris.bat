@ECHO OFF
SET PSQL_BIN_DIR=%~dp0\Platforms\PostgreSQL\11.5.1\pgsql\bin
cd %PSQL_BIN_DIR%
"%PSQL_BIN_DIR%\psql" -U postgres -d iris -f "Z:\TeTRES\Cad_Iris_Sql_DataParser\initial_database_setup\irisCreate.sql"
"%PSQL_BIN_DIR%\psql" -U postgres -d cad -f "Z:\TeTRES\Cad_Iris_Sql_DataParser\initial_database_setup\cadCreate.sql"
cmd /k