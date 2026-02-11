// Vizia/plugins/vizia-recorder/cpp_engine/recorder.h

#ifndef RECORDER_H
#define RECORDER_H

#include <windows.h>

// Context yapısı: Ekran yakalama için gerekli Windows kaynaklarını tutar.
struct CapContext {
    HDC hScreen;      // Tüm ekranın DC'si
    HDC hDC;          // Bellekteki uyumlu DC
    HBITMAP hBmp;     // Görüntünün tutulduğu bitmap
    void* pBits;      // Görüntü verisinin ham (raw) adresi
    int width;
    int height;
    size_t bufferSize; // Beklenen tampon boyutu (Güvenlik kontrolü için)
};

// C++ adlandırma karmaşasını (mangling) önlemek için extern "C" kullanılır.
extern "C" {
    // Motoru başlatır ve kaynakları hazırlar.
    __declspec(dllexport) CapContext* init_engine(int w, int h);

    // Bir kare yakalar ve verilen buffer'a güvenli bir şekilde kopyalar.
    __declspec(dllexport) bool grab_frame(CapContext* ctx, unsigned char* buffer, size_t bufferSize);

    // Kaynakları serbest bırakır ve belleği temizler.
    __declspec(dllexport) void release_engine(CapContext* ctx);
}

#endif // RECORDER_H