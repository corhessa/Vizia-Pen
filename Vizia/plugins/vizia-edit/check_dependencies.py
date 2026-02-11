#!/usr/bin/env python3
"""
Vizia Edit - Bağımlılık Kontrol Scripti
Bu script tüm bağımlılıkları kontrol eder ve kurulum sorunlarını tespit eder.
"""

import sys
import subprocess
import platform

def print_header(text):
    """Başlık yazdırır"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_status(check_name, status, message=""):
    """Durum yazdırır"""
    status_icon = "✓" if status else "✗"
    status_text = "TAMAM" if status else "EKSİK"
    print(f"{status_icon} {check_name:30s} [{status_text}] {message}")

def check_python_version():
    """Python sürümünü kontrol eder"""
    version = sys.version_info
    required = (3, 8)
    
    current = f"{version.major}.{version.minor}.{version.micro}"
    required_str = f"{required[0]}.{required[1]}"
    
    is_ok = version >= required
    print_status("Python Sürümü", is_ok, f"Mevcut: {current}, Gerekli: {required_str}+")
    
    return is_ok

def check_pip():
    """pip kurulumunu kontrol eder"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        is_ok = result.returncode == 0
        version = result.stdout.strip().split()[1] if is_ok else "N/A"
        print_status("pip", is_ok, f"Versiyon: {version}")
        return is_ok
    except Exception as e:
        print_status("pip", False, f"Hata: {str(e)}")
        return False

def check_module(module_name, import_name=None, min_version=None):
    """Python modülünü kontrol eder"""
    if import_name is None:
        import_name = module_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "Bilinmiyor")
        
        # Versiyon kontrolü
        is_ok = True
        version_msg = f"Versiyon: {version}"
        
        if min_version and hasattr(module, "__version__"):
            try:
                from packaging import version as pkg_version
                is_ok = pkg_version.parse(module.__version__) >= pkg_version.parse(min_version)
                if not is_ok:
                    version_msg += f" (Gerekli: {min_version}+)"
            except:
                pass
        
        print_status(module_name, is_ok, version_msg)
        return is_ok
    except ImportError:
        print_status(module_name, False, "Kurulu değil")
        return False
    except Exception as e:
        print_status(module_name, False, f"Hata: {str(e)}")
        return False

def check_system_command(command, package_name=None):
    """Sistem komutunu kontrol eder"""
    if package_name is None:
        package_name = command
    
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        is_ok = result.returncode == 0
        
        if is_ok:
            # İlk satırı al
            version_line = result.stdout.split('\n')[0] if result.stdout else result.stderr.split('\n')[0]
            version_line = version_line[:50]  # Kısalt
            print_status(package_name, True, version_line)
        else:
            print_status(package_name, False, "Kurulu değil veya PATH'te değil")
        
        return is_ok
    except FileNotFoundError:
        print_status(package_name, False, "Kurulu değil")
        return False
    except Exception as e:
        print_status(package_name, False, f"Kontrol edilemedi")
        return False

def print_installation_help(missing_items):
    """Eksik bağımlılıklar için kurulum yardımı gösterir"""
    if not missing_items:
        return
    
    print_header("KURULUM TALİMATLARI")
    
    os_type = platform.system()
    
    if "PyQt5" in missing_items:
        print("\n📦 PyQt5 Kurulumu:")
        print("   pip3 install PyQt5>=5.15.0")
        if os_type == "Linux":
            print("   veya: sudo apt install python3-pyqt5")
    
    if "numpy" in missing_items:
        print("\n📦 numpy Kurulumu:")
        print("   pip3 install numpy>=1.21.0")
    
    if "Pillow" in missing_items:
        print("\n📦 Pillow Kurulumu:")
        print("   pip3 install Pillow>=9.0.0")
    
    if "python-mpv" in missing_items:
        print("\n📦 python-mpv Kurulumu (Opsiyonel):")
        print("   pip3 install python-mpv>=1.0.0")
        print("   Not: mpv olmadan da çalışır (QMediaPlayer fallback)")
    
    if "ffmpeg" in missing_items:
        print("\n🎬 FFmpeg Kurulumu (Gerekli):")
        if os_type == "Linux":
            print("   sudo apt install ffmpeg")
        elif os_type == "Darwin":
            print("   brew install ffmpeg")
        else:
            print("   https://ffmpeg.org/download.html adresinden indirin")
    
    if "mpv" in missing_items:
        print("\n🎥 mpv Kurulumu (Opsiyonel - Önizleme için):")
        if os_type == "Linux":
            print("   sudo apt install mpv libmpv-dev")
        elif os_type == "Darwin":
            print("   brew install mpv")
        else:
            print("   https://mpv.io/installation/ adresinden indirin")
    
    print("\n💡 Tüm Python paketlerini tek seferde kurmak için:")
    print("   pip3 install -r requirements.txt")
    print("\n💡 İzin hatası alırsanız:")
    print("   pip3 install --user -r requirements.txt")
    print("\n💡 Virtual environment kullanmak için:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate  # Linux/macOS")
    print("   pip install -r requirements.txt")

def main():
    """Ana fonksiyon"""
    print("\n" + "=" * 70)
    print("  🎬 VİZİA EDİT - BAĞIMLILIK KONTROLÜ")
    print("=" * 70)
    
    print(f"\n📍 Platform: {platform.system()} {platform.release()}")
    print(f"📍 Python: {sys.executable}")
    
    # Sonuçları sakla
    results = {}
    missing_items = []
    
    # Python ve pip kontrolü
    print_header("SİSTEM GEREKSINIMLERI")
    results["Python"] = check_python_version()
    results["pip"] = check_pip()
    
    # Python modülleri
    print_header("PYTHON PAKETLERI")
    results["PyQt5"] = check_module("PyQt5", "PyQt5", "5.15.0")
    results["numpy"] = check_module("numpy", "numpy", "1.21.0")
    results["Pillow"] = check_module("Pillow", "PIL", "9.0.0")
    results["python-mpv"] = check_module("python-mpv", "mpv", "1.0.0")
    
    # Eksik Python paketlerini kaydet
    for module in ["PyQt5", "numpy", "Pillow", "python-mpv"]:
        if not results.get(module, False):
            missing_items.append(module)
    
    # Sistem bağımlılıkları
    print_header("SİSTEM PAKETLERI")
    results["ffmpeg"] = check_system_command("ffmpeg", "FFmpeg")
    results["mpv"] = check_system_command("mpv", "mpv")
    
    if not results.get("ffmpeg", False):
        missing_items.append("ffmpeg")
    if not results.get("mpv", False):
        missing_items.append("mpv")
    
    # Özet
    print_header("ÖZET")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\n✓ Başarılı: {passed}/{total}")
    print(f"✗ Eksik: {failed}/{total}")
    
    # Core bağımlılıkları kontrol et
    core_deps = ["Python", "pip"]
    core_ok = all(results.get(dep, False) for dep in core_deps)
    
    python_deps = ["PyQt5", "numpy", "Pillow"]
    python_ok = all(results.get(dep, False) for dep in python_deps)
    
    if core_ok and python_ok and results.get("ffmpeg", False):
        print("\n✅ KURULUM TAMAMLANDI!")
        print("   Uygulamayı çalıştırmak için: python run.py")
    elif core_ok and python_ok:
        print("\n⚠️  TEMEL KURULUM TAMAM")
        print("   FFmpeg kurulmamış - video işleme çalışmayacak")
        print("   Uygulamayı yine de başlatabilirsiniz: python run.py")
    elif core_ok:
        print("\n❌ KURULUM EKSİK")
        print("   Lütfen eksik Python paketlerini kurun")
        print_installation_help(missing_items)
    else:
        print("\n❌ KURULUM BAŞARISIZ")
        print("   Python veya pip düzgün kurulmamış")
    
    # Opsiyonel uyarı
    if not results.get("mpv", False):
        print("\n💡 İpucu: mpv kurulu değil. Önizleme QMediaPlayer ile çalışacak.")
    
    # Detaylı yardım
    if missing_items:
        print_installation_help(missing_items)
    
    print("\n" + "=" * 70)
    print("📚 Detaylı kurulum kılavuzu için: INSTALL.md dosyasını okuyun")
    print("=" * 70 + "\n")
    
    # Exit code
    sys.exit(0 if (core_ok and python_ok) else 1)

if __name__ == "__main__":
    main()
