@ECHO OFF
SET PYTHON=%~dp0\Platforms\Python\3.7.4\python.exe
SET SERVER=%~dp0\Server\src\server.py

%PYTHON% %SERVER%

cmd /k