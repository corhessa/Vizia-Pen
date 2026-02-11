# Vizia Edit - Detaylı Kurulum Kılavuzu

Bu kılavuz, Vizia Edit'i kurarken karşılaşabileceğiniz sorunları ve çözümlerini içerir.

## 🚀 Hızlı Kurulum

### Adım 1: Python Sürümünü Kontrol Edin

```bash
python3 --version
```

**Gereksinim:** Python 3.8 veya üzeri (Python 3.9+ önerilir)

Python yüklü değilse:
- **Ubuntu/Debian:** `sudo apt install python3 python3-pip`
- **macOS:** `brew install python3`
- **Windows:** [python.org](https://python.org) adresinden indirin

### Adım 2: pip'i Güncelleyin

```bash
pip3 install --upgrade pip
```

veya

```bash
python3 -m pip install --upgrade pip
```

### Adım 3: Python Kütüphanelerini Kurun

**Basit Kurulum:**
```bash
pip3 install -r requirements.txt
```

**Eğer Hata Alırsanız, Tek Tek Kurun:**
```bash
pip3 install PyQt5>=5.15.0
pip3 install numpy>=1.21.0
pip3 install Pillow>=9.0.0
pip3 install python-mpv>=1.0.0
```

### Adım 4: Sistem Bağımlılıklarını Kurun

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg mpv libmpv-dev python3-dev build-essential
```

#### macOS (Homebrew)

```bash
brew install ffmpeg mpv
```

#### Windows

1. **FFmpeg:** [ffmpeg.org/download.html](https://ffmpeg.org/download.html) adresinden indirin
   - ZIP dosyasını çıkarın
   - `bin` klasörünü PATH'e ekleyin
   - Terminal'de `ffmpeg -version` ile test edin

2. **mpv (opsiyonel):** [mpv.io/installation](https://mpv.io/installation/) adresinden indirin

## ❌ Yaygın Hatalar ve Çözümleri

### Hata 1: "pip: command not found"

**Çözüm:**
```bash
# Python 3 ile pip kullanın
python3 -m pip install -r requirements.txt
```

### Hata 2: "Permission denied" / İzin hatası

**Çözüm:**
```bash
# Kullanıcı dizinine kurun (sudo kullanmayın)
pip3 install --user -r requirements.txt
```

### Hata 3: PyQt5 kurulamıyor

**Sebep:** Sistem paketleri eksik olabilir.

**Ubuntu/Debian Çözümü:**
```bash
sudo apt install python3-pyqt5 python3-pyqt5.qtsvg python3-pyqt5.qtmultimedia
# veya
sudo apt install build-essential python3-dev qt5-default
pip3 install PyQt5
```

**macOS Çözümü:**
```bash
brew install qt5
pip3 install PyQt5
```

**Windows Çözümü:**
- Visual C++ Build Tools kurulu olmalı
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) indirin
- Veya önceden derlenmiş wheel kullanın:
```bash
pip3 install PyQt5 --only-binary :all:
```

### Hata 4: python-mpv kurulamıyor

**Not:** mpv opsiyoneldir, kurulmazsa uygulama QMediaPlayer kullanır.

**Çözüm (mpv gerekiyorsa):**

Ubuntu/Debian:
```bash
sudo apt install mpv libmpv-dev
pip3 install python-mpv
```

macOS:
```bash
brew install mpv
pip3 install python-mpv
```

Windows:
- mpv'yi kurun ve PATH'e ekleyin
- Veya mpv olmadan çalıştırın (fallback modu)

### Hata 5: "externally-managed-environment" hatası (Python 3.11+)

**Sebep:** Bazı Linux dağıtımlarında sistem Python'unu korumak için pip kısıtlanmıştır.

**Çözüm 1 - Virtual Environment (Önerilen):**
```bash
# Virtual environment oluştur
python3 -m venv venv

# Aktif et
source venv/bin/activate  # Linux/macOS
# veya
venv\Scripts\activate     # Windows

# Paketleri kur
pip install -r requirements.txt

# Uygulamayı çalıştır
python run.py
```

**Çözüm 2 - Kullanıcı dizinine kur:**
```bash
pip3 install --user -r requirements.txt
```

**Çözüm 3 - pipx kullan:**
```bash
sudo apt install pipx
pipx install -r requirements.txt
```

### Hata 6: numpy build hatası

**Çözüm:**
```bash
# Ubuntu/Debian
sudo apt install python3-numpy
pip3 install numpy

# veya önceden derlenmiş wheel kullan
pip3 install numpy --only-binary :all:
```

### Hata 7: "No matching distribution found"

**Sebep:** Python sürümünüz çok eski veya çok yeni olabilir.

**Çözüm:**
```bash
# Python sürümünü kontrol edin
python3 --version

# Python 3.8-3.12 arası kullanın
# Farklı Python versiyonu kurun veya pyenv kullanın
```

## 🔍 Kurulumu Test Etme

Kurulumun başarılı olup olmadığını kontrol etmek için:

```bash
python3 check_dependencies.py
```

Bu script tüm bağımlılıkları kontrol eder ve eksikleri bildirir.

## 📦 Minimal Kurulum (Sadece Core)

GUI olmadan sadece core engine'i test etmek için:

```bash
# Sadece numpy gerekli
pip3 install numpy

# Core engine'i test et
python3 -c "from src.core.timeline import Timeline; print('✓ Core çalışıyor')"
```

## 🐳 Docker ile Kurulum (Alternatif)

Eğer kurulum sorunları devam ederse Docker kullanabilirsiniz:

```bash
# Dockerfile oluştur (örnek)
docker build -t vizia-edit .
docker run -it vizia-edit python run.py
```

## 🆘 Hâlâ Sorun mu Yaşıyorsunuz?

1. **Hata mesajını kaydedin:**
   ```bash
   pip3 install -r requirements.txt 2>&1 | tee install_log.txt
   ```

2. **Sistem bilgilerinizi toplayın:**
   ```bash
   python3 --version
   pip3 --version
   uname -a  # Linux/macOS
   ```

3. **GitHub Issues'da rapor edin:**
   - Hata mesajının tamamını paylaşın
   - İşletim sisteminizi belirtin
   - Python sürümünüzü belirtin

## ✅ Kurulum Sonrası

Kurulum başarılı olduysa:

```bash
# Standalone modda çalıştırın
python run.py

# Veya plugin olarak kullanın
# vizia-edit klasörünü Vizia/plugins/ dizinine kopyalayın
```

## 🔗 Yararlı Linkler

- [Python Kurulum Kılavuzu](https://www.python.org/downloads/)
- [pip Kullanım Kılavuzu](https://pip.pypa.io/en/stable/user_guide/)
- [PyQt5 Dokümantasyonu](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [FFmpeg Kurulum](https://ffmpeg.org/download.html)
- [Virtual Environment Rehberi](https://docs.python.org/3/tutorial/venv.html)

---

**Not:** Vizia Edit, performans için FFmpeg ve mpv kullanır. Bunlar kurulu değilse bazı özellikler çalışmayacaktır, ancak uygulama yine de açılır.
