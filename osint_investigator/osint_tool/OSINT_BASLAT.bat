@echo off
title OSINT Investigator - Kurulum ve Baslatic
color 0A

echo.
echo  ==========================================
echo    OSINT NAME INVESTIGATOR - v1.0
echo    Hazirlanıyor...
echo  ==========================================
echo.

:: Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo  [!] Python bulunamadi. Yukleniyor...
    echo  [*] winget ile Python yukleniyor...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo  [!] winget basarisiz. Manuel indirme aciliyor...
        start https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
        echo  [!] Python'u yukleyip bu dosyayi tekrar calistir.
        pause
        exit /b 1
    )
    :: PATH yenile
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
)

echo  [✓] Python bulundu.

:: pip güncelle
echo  [*] pip guncelleniyor...
python -m pip install --upgrade pip --quiet

:: Kütüphaneler
echo  [*] Gerekli kutuphaneler yukleniyor...
python -m pip install requests beautifulsoup4 googlesearch-python colorama rich --quiet

echo  [✓] Tum bagimliliklar tamam.
echo.
echo  [*] Program baslatiliyor...
echo.

:: osint_gui.py ile aynı klasörde olduğunu varsay
python "%~dp0osint_gui.py"

if errorlevel 1 (
    echo.
    echo  [!] Program hata ile kapandi. Log:
    python "%~dp0osint_gui.py"
    pause
)
