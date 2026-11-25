@echo off
REM Run on Windows with Python 3.10+ (64-bit) installed, with internet access.
REM Result: WajeehaTranscribe_Package\  (copy this whole folder anywhere)
REM     WajeehaTranscribe.exe
REM     models\whistle.cact
REM     engine\*.dll

python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt || goto :fail

if exist WajeehaTranscribe_Package rmdir /s /q WajeehaTranscribe_Package
mkdir WajeehaTranscribe_Package

echo.
echo === Downloading model + engine into the package ===
python app.py --prepare WajeehaTranscribe_Package || goto :fail

echo.
echo === Building exe ===
REM Use the logo files if they exist and are not empty
set ICONARGS=
if exist WT.ico for %%F in (WT.ico) do if %%~zF GTR 0 set ICONARGS=--icon WT.ico --add-data "WT.ico;."
if exist WT.png for %%F in (WT.png) do if %%~zF GTR 0 set ICONARGS=%ICONARGS% --add-data "WT.png;."
if not defined ICONARGS echo WARNING: WT.ico / WT.png missing or empty - building without a logo.

pyinstaller --noconfirm --onefile --windowed --name WajeehaTranscribe %ICONARGS% ^
  --collect-all needle --collect-all soxr --collect-all sounddevice ^
  --collect-data _sounddevice_data ^
  app.py || goto :fail

copy /y dist\WajeehaTranscribe.exe WajeehaTranscribe_Package\ >nul

echo.
echo === Files in package ===
dir /s /b WajeehaTranscribe_Package
echo.
echo Done. Copy the whole folder WajeehaTranscribe_Package to any Windows PC.
echo Keep the "models" and "engine" folders next to the exe.
pause
exit /b 0

:fail
echo.
echo BUILD FAILED. Copy the error above and send it to me.
pause
exit /b 1
