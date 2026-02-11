#!/bin/bash
# Vizia Edit - Otomatik Kurulum Scripti (Linux/macOS)

set -e  # Hata durumunda dur

echo "=================================="
echo "  Vizia Edit - Otomatik Kurulum"
echo "=================================="
echo

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonksiyonlar
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "ℹ $1"
}

# Python kontrolü
echo "1. Python sürümü kontrol ediliyor..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python bulundu: $PYTHON_VERSION"
else
    print_error "Python 3 bulunamadı!"
    echo "Lütfen Python 3.8 veya üzerini kurun."
    exit 1
fi

# pip kontrolü
echo
echo "2. pip kontrol ediliyor..."
if python3 -m pip --version &> /dev/null; then
    PIP_VERSION=$(python3 -m pip --version | awk '{print $2}')
    print_success "pip bulundu: $PIP_VERSION"
else
    print_error "pip bulunamadı!"
    echo "Lütfen pip kurun: sudo apt install python3-pip"
    exit 1
fi

# pip güncelleme
echo
echo "3. pip güncelleniyor..."
python3 -m pip install --upgrade pip --user || print_warning "pip güncellenemedi, devam ediliyor..."

# Python paketlerini kurma
echo
echo "4. Python paketleri kuruluyor..."

# Platform tespiti
PLATFORM=$(uname -s)
case "$PLATFORM" in
    Linux*)
        print_info "Platform: Linux"
        REQ_FILE="requirements.txt"
        ;;
    Darwin*)
        print_info "Platform: macOS"
        REQ_FILE="requirements-macos.txt"
        ;;
    *)
        print_warning "Bilinmeyen platform: $PLATFORM"
        REQ_FILE="requirements-minimal.txt"
        ;;
esac

# Paketleri kur
if [ -f "$REQ_FILE" ]; then
    print_info "Kurulum dosyası: $REQ_FILE"
    if python3 -m pip install --user -r "$REQ_FILE"; then
        print_success "Python paketleri kuruldu"
    else
        print_error "Paket kurulumu başarısız!"
        echo
        print_info "Alternatif kurulum deneyin:"
        echo "  python3 -m pip install --user -r requirements-minimal.txt"
        exit 1
    fi
else
    print_error "Requirements dosyası bulunamadı: $REQ_FILE"
    exit 1
fi

# FFmpeg kontrolü
echo
echo "5. FFmpeg kontrol ediliyor..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1)
    print_success "FFmpeg bulundu"
else
    print_warning "FFmpeg bulunamadı!"
    echo
    if [ "$PLATFORM" = "Linux" ]; then
        echo "Kurulum için: sudo apt install ffmpeg"
    elif [ "$PLATFORM" = "Darwin" ]; then
        echo "Kurulum için: brew install ffmpeg"
    fi
    echo "Not: FFmpeg olmadan video işleme çalışmayacak"
fi

# mpv kontrolü (opsiyonel)
echo
echo "6. mpv kontrol ediliyor..."
if command -v mpv &> /dev/null; then
    MPV_VERSION=$(mpv --version 2>&1 | head -n1)
    print_success "mpv bulundu"
else
    print_warning "mpv bulunamadı (opsiyonel)"
    echo "   Önizleme QMediaPlayer ile çalışacak"
fi

# Bağımlılık kontrolü
echo
echo "7. Bağımlılıklar kontrol ediliyor..."
if python3 check_dependencies.py > /dev/null 2>&1; then
    print_success "Tüm bağımlılıklar hazır"
else
    print_warning "Bazı bağımlılıklar eksik"
    echo
    echo "Detaylı kontrol için çalıştırın:"
    echo "  python3 check_dependencies.py"
fi

# Özet
echo
echo "=================================="
echo "  Kurulum Tamamlandı!"
echo "=================================="
echo
echo "Uygulamayı başlatmak için:"
echo "  python3 run.py"
echo
echo "Veya plugin olarak kullanmak için:"
echo "  1. vizia-edit klasörünü Vizia/plugins/ dizinine kopyalayın"
echo "  2. Vizia-Pen'i başlatın"
echo
echo "Sorun yaşarsanız:"
echo "  - python3 check_dependencies.py"
echo "  - INSTALL.md dosyasını okuyun"
echo
