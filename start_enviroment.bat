@echo off
title your_camera_name 
REM Configuration - modify these variables as needed
REM To see version conda in anaconda prompt = echo %CONDA_PREFIX%
set CONDA_PATH="C:\ProgramData\anaconda3\Scripts\activate.bat" 
set PROJECT_DRIVE=D:
set ENVIRONMENT="your_enviroment_name"
set PROJECT_FOLDER="folder_name"
REM set SCRIPT_NAME=your_script.py

REM Navigate to project directory and activate environment
call %CONDA_PATH%
%PROJECT_DRIVE%
cd %PROJECT_FOLDER%
call conda activate %ENVIRONMENT%

REM python %SCRIPT_NAME%
REM Show current location and open interactive command prompt
echo Anaconda environment activated in %cd%
echo Current conda environment: %ENVIRONMENT%
cmd /k
