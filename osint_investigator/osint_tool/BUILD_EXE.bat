@echo off
echo [*] OSINT Investigator - .exe Build Script
echo.

:: Install dependencies
echo [1/3] Bagimliliklar yukleniyor...
pip install -r requirements.txt
pip install pyinstaller

:: Build exe
echo.
echo [2/3] .exe derleniyor...
pyinstaller --onefile --windowed --name "OSINT_Investigator" --icon=NONE osint_gui.py

echo.
echo [3/3] Tamamlandi!
echo Cikti: dist\OSINT_Investigator.exe
pause
