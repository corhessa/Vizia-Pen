# 🔧 Vizia Edit - Kurulum Sorunları Çözüm Rehberi

## "Gerekli olan kütüphaneleri kuramıyorum" Sorunu - TAM ÇÖZÜM

Bu dosya özellikle Python kütüphanelerini kurarken sorun yaşayan kullanıcılar için hazırlanmıştır.

---

## 🎯 EN HIZLI ÇÖZÜM

### 1. Otomatik Kurulum Script'ini Çalıştırın

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```
install.bat
```

Script sizin için:
- ✅ Python sürümünü kontrol eder
- ✅ pip'i günceller
- ✅ Paketleri kurar
- ✅ Sistem bağımlılıklarını kontrol eder
- ✅ Sorunları tespit eder ve çözüm önerir

### 2. Manuel Kontrol

Eğer script çalışmazsa:
```bash
python3 check_dependencies.py
```

Bu komut:
- 🔍 Tüm bağımlılıkları kontrol eder
- 📋 Eksikleri listeler
- �� Kurulum talimatları verir

---

## 🚨 YAYGIN HATALAR VE ÇÖZÜMLERI

### HATA 1: "pip: command not found"

**Çözüm:**
```bash
# pip'i Python modülü olarak kullanın
python3 -m pip install -r requirements.txt
```

### HATA 2: "Permission denied" / "sudo ile kurmayın"

**Çözüm 1 - Kullanıcı dizinine kurun (ÖNERİLEN):**
```bash
pip3 install --user -r requirements.txt
```

**Çözüm 2 - Virtual Environment (EN İYİ YÖNTEM):**
```bash
# Virtual environment oluştur
python3 -m venv venv

# Aktif et
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Paketleri kur
pip install -r requirements.txt

# Uygulamayı çalıştır
python run.py
```

### HATA 3: "externally-managed-environment" (Python 3.11+)

Bu hata yeni Linux dağıtımlarında (Ubuntu 23.04+, Debian 12+) görülür.

**ÇÖZÜM - Virtual Environment Kullanın:**
```bash
# 1. Virtual environment oluştur
python3 -m venv venv

# 2. Aktif et
source venv/bin/activate

# 3. Paketleri kur
pip install -r requirements.txt

# 4. Uygulamayı çalıştır
python run.py

# Kapatmak için:
deactivate
```

**NOT:** Her uygulamayı çalıştırmadan önce `source venv/bin/activate` çalıştırın.

### HATA 4: PyQt5 kurulamıyor

**Sebep:** Build araçları veya Qt kütüphaneleri eksik

**Ubuntu/Debian Çözümü:**
```bash
# Sistem paketini kullan (ÖNERİLEN)
sudo apt install python3-pyqt5

# veya build araçlarını kur
sudo apt install build-essential python3-dev qt5-default
pip3 install --user PyQt5
```

**macOS Çözümü:**
```bash
brew install qt5
pip3 install PyQt5
```

**Windows Çözümü:**
```bash
# Visual C++ Build Tools gerekli
# https://visualstudio.microsoft.com/downloads/ adresinden indirin
# veya
pip3 install PyQt5 --only-binary :all:
```

### HATA 5: python-mpv kurulamıyor

**ÖNEMLİ:** python-mpv OPSİYONELDİR! Kurulu olmasa da uygulama çalışır.

**Minimal Kurulum (python-mpv olmadan):**
```bash
pip3 install -r requirements-minimal.txt
```

**Eğer mpv kuruluysa ve python-mpv istiyorsanız:**

Ubuntu/Debian:
```bash
sudo apt install mpv libmpv-dev
pip3 install --user python-mpv
```

macOS:
```bash
brew install mpv
pip3 install python-mpv
```

Windows:
```
python-mpv Windows'ta sorunludur, kullanmayın.
Uygulama QMediaPlayer ile çalışacaktır.
```

### HATA 6: numpy build hatası

**Çözüm 1 - Önceden derlenmiş wheel kullan:**
```bash
pip3 install --user numpy --only-binary :all:
```

**Çözüm 2 - Sistem paketini kullan:**
```bash
# Ubuntu/Debian
sudo apt install python3-numpy
```

### HATA 7: "No matching distribution found"

**Sebep:** Python sürümünüz çok eski veya çok yeni

**Kontrol:**
```bash
python3 --version
```

**Gerekli:** Python 3.8 - 3.12 arası

**Çözüm:**
- Python 3.9 veya 3.10 kurmanız önerilir
- veya pyenv kullanın: https://github.com/pyenv/pyenv

---

## 💡 PLATFORM-ÖZEL KURULUMLAR

### Windows

```bash
# Windows için optimize edilmiş paketler
pip install -r requirements-windows.txt

# FFmpeg kurulumu:
# 1. https://ffmpeg.org/download.html adresine gidin
# 2. Windows build indirin
# 3. ZIP'i çıkarın
# 4. bin/ klasörünü PATH'e ekleyin
```

### macOS

```bash
# macOS için optimize edilmiş paketler
pip3 install -r requirements-macos.txt

# Sistem bağımlılıkları
brew install ffmpeg mpv
```

### Linux (Ubuntu/Debian)

```bash
# Tam kurulum
pip3 install --user -r requirements.txt

# Sistem bağımlılıkları
sudo apt update
sudo apt install ffmpeg mpv libmpv-dev python3-dev build-essential
```

---

## 🔍 ADIM ADIM KURULUM (HER ŞEY BAŞARISIZ OLURSA)

### 1. Python Kontrolü
```bash
python3 --version
# Çıktı: Python 3.x.x (3.8 veya üzeri olmalı)
```

### 2. pip Kontrolü
```bash
python3 -m pip --version
# Çıktı: pip x.x.x ...
```

### 3. pip Güncelleme
```bash
python3 -m pip install --upgrade pip --user
```

### 4. Virtual Environment (ÖNERİLEN)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# veya
venv\Scripts\activate     # Windows
```

### 5. Minimal Paketleri Kur (Sadece Gerekli Olanlar)
```bash
pip install PyQt5>=5.15.0
pip install numpy>=1.21.0
pip install Pillow>=9.0.0
```

### 6. Kontrol
```bash
python3 check_dependencies.py
```

### 7. Çalıştır
```bash
python3 run.py
```

---

## 📦 ALTERNATİF REQUIREMENTS DOSYALARI

Projenin kök dizininde farklı requirements dosyaları var:

| Dosya | Açıklama | Kullanım |
|-------|----------|----------|
| `requirements.txt` | Tam kurulum (Linux için) | `pip3 install -r requirements.txt` |
| `requirements-minimal.txt` | Sadece temel paketler (mpv yok) | `pip3 install -r requirements-minimal.txt` |
| `requirements-windows.txt` | Windows için optimize | `pip3 install -r requirements-windows.txt` |
| `requirements-macos.txt` | macOS için optimize | `pip3 install -r requirements-macos.txt` |

**Öneri:** Sorun yaşıyorsanız önce `requirements-minimal.txt` deneyin.

---

## 🆘 HÂLÂ KURULUM YAPAMADINIZ MI?

### 1. Kurulum Logunu Kaydedin
```bash
pip3 install -r requirements.txt 2>&1 | tee kurulum_log.txt
```

### 2. Sistem Bilgilerini Toplayın
```bash
python3 --version > sistem_bilgi.txt
pip3 --version >> sistem_bilgi.txt
uname -a >> sistem_bilgi.txt  # Linux/macOS
```

### 3. GitHub Issues'da Rapor Edin
- Repository: https://github.com/corhessa/vizia-edit/issues
- `kurulum_log.txt` dosyasını paylaşın
- `sistem_bilgi.txt` dosyasını paylaşın
- İşletim sisteminizi belirtin
- Hangi adımda hata aldığınızı yazın

---

## ✅ BAŞARILI KURULUM SONRASI

Kurulum başarılı olduysa:

```bash
# Bağımlılıkları kontrol et
python3 check_dependencies.py

# Uygulamayı başlat
python3 run.py
```

**NOT:** FFmpeg kurulu değilse uygulama açılır ama video işleme çalışmaz.

---

## 📚 EK KAYNAKLAR

- 📖 **INSTALL.md** - Detaylı kurulum kılavuzu (tüm hatalar ve çözümler)
- 🚀 **QUICKSTART.md** - Hızlı başlangıç kılavuzu
- 🧪 **TESTING.md** - Test ve kullanım kılavuzu
- 📘 **README.md** - Genel proje bilgisi

---

## 💬 İLETİŞİM

- GitHub: https://github.com/corhessa/vizia-edit
- Issues: https://github.com/corhessa/vizia-edit/issues

---

**🎬 Vizia Edit - Kurulum artık çok daha kolay!**
