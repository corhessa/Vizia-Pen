@echo off
REM Vizia Edit - Otomatik Kurulum Scripti (Windows)

echo ==================================
echo   Vizia Edit - Otomatik Kurulum
echo ==================================
echo.

REM Python kontrolu
echo 1. Python surumu kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi!
    echo Lutfen Python 3.8 veya uzerini kurun: https://python.org
    pause
    exit /b 1
)

python --version
echo [TAMAM] Python bulundu
echo.

REM pip kontrolu
echo 2. pip kontrol ediliyor...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] pip bulunamadi!
    pause
    exit /b 1
)

python -m pip --version
echo [TAMAM] pip bulundu
echo.

REM pip guncelleme
echo 3. pip guncelleniyor...
python -m pip install --upgrade pip
echo.

REM Python paketlerini kurma
echo 4. Python paketleri kuruluyor...
if exist requirements-windows.txt (
    echo Windows icin ozel paketler kuruluyor...
    python -m pip install -r requirements-windows.txt
) else (
    echo Standart paketler kuruluyor...
    python -m pip install -r requirements.txt
)

if %errorlevel% neq 0 (
    echo [HATA] Paket kurulumu basarisiz!
    echo.
    echo Alternatif olarak minimal kurulum deneyin:
    echo   python -m pip install -r requirements-minimal.txt
    pause
    exit /b 1
)

echo [TAMAM] Python paketleri kuruldu
echo.

REM FFmpeg kontrolu
echo 5. FFmpeg kontrol ediliyor...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] FFmpeg bulunamadi!
    echo.
    echo FFmpeg kurmak icin:
    echo   1. https://ffmpeg.org/download.html adresini ziyaret edin
    echo   2. Windows icin derlenmiş versiyonu indirin
    echo   3. ZIP dosyasini cikarin
    echo   4. bin klasorunu PATH'e ekleyin
    echo.
    echo Not: FFmpeg olmadan video isleme calismayacak
) else (
    ffmpeg -version | findstr /i "ffmpeg version"
    echo [TAMAM] FFmpeg bulundu
)
echo.

REM Bagimliliklari kontrol et
echo 6. Bagimliliklar kontrol ediliyor...
python check_dependencies.py
echo.

REM Ozet
echo ==================================
echo   Kurulum Tamamlandi!
echo ==================================
echo.
echo Uygulamayi baslatmak icin:
echo   python run.py
echo.
echo Veya plugin olarak kullanmak icin:
echo   1. vizia-edit klasorunu Vizia/plugins/ dizinine kopyalayin
echo   2. Vizia-Pen'i baslatin
echo.
echo Sorun yasarsaniz:
echo   - python check_dependencies.py
echo   - INSTALL.md dosyasini okuyun
echo.

pause
