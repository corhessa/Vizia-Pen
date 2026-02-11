import os
import subprocess
import sys

def compile_dll():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(current_dir, "recorder.cpp")
    build_dir = os.path.join(current_dir, "build")
    dll_path = os.path.join(build_dir, "recorder.dll")
    
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
        
    print(f"[Vizia Builder] C++ Derleniyor... Hedef: {dll_path}")

    # 1. Yontem: Microsoft Visual Studio (cl.exe)
    try:
        # Once basit kontrol
        if subprocess.call("where cl", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            # Komut: cl /LD /O2 /Fe:"dll_path" "src" user32.lib gdi32.lib
            cmd = f"cl /LD /O2 /Fe:\"{dll_path}\" \"{src}\" user32.lib gdi32.lib"
            subprocess.check_call(cmd, shell=True)
            print("[Vizia Builder] MSVC (Microsoft) ile basariyla derlendi!")
            return dll_path
    except:
        pass

    # 2. Yontem: MinGW (g++)
    try:
        if subprocess.call("where g++", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            cmd = f"g++ -shared -o \"{dll_path}\" \"{src}\" -O3 -lgdi32 -luser32"
            subprocess.check_call(cmd, shell=True)
            print("[Vizia Builder] G++ (MinGW) ile basariyla derlendi!")
            return dll_path
    except:
        pass
        
    print("[Vizia Builder] HATA: Derleyici (cl veya g++) bulunamadi.")
    print("[Vizia Builder] Ipucu: Visual Studio Build Tools kurulumu veya Path ayari eksik.")
    return None

if __name__ == "__main__":
    compile_dll()