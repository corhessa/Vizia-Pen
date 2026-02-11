// Vizia/core/cpp_engine/recorder.cpp

#include "recorder.h"
#include <iostream>

extern "C" {
    __declspec(dllexport) CapContext* init_engine(int w, int h) {
        // Parametre kontrolü
        if (w <= 0 || h <= 0) return nullptr;

        CapContext* ctx = new (std::nothrow) CapContext();
        if (!ctx) return nullptr;

        ctx->width = w;
        ctx->height = h;
        ctx->bufferSize = (size_t)w * h * 4; // BGRA = 4 byte per pixel

        // 1. Ekran DC'sini al
        ctx->hScreen = GetDC(NULL);
        if (!ctx->hScreen) {
            delete ctx;
            return nullptr;
        }

        // 2. Bellekte uyumlu bir DC oluştur
        ctx->hDC = CreateCompatibleDC(ctx->hScreen);
        if (!ctx->hDC) {
            ReleaseDC(NULL, ctx->hScreen);
            delete ctx;
            return nullptr;
        }

        // 3. Bitmap bilgilerini hazırla (BGRA formatı)
        BITMAPINFO bmi = { 0 };
        bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        bmi.bmiHeader.biWidth = w;
        bmi.bmiHeader.biHeight = -h; // Negatif: Top-down görüntü (OpenCV uyumlu)
        bmi.bmiHeader.biPlanes = 1;
        bmi.bmiHeader.biBitCount = 32;
        bmi.bmiHeader.biCompression = BI_RGB;

        // 4. DIB Section oluştur (Doğrudan bellek erişimi sağlar)
        ctx->hBmp = CreateDIBSection(ctx->hDC, &bmi, DIB_RGB_COLORS, &ctx->pBits, NULL, 0);
        if (!ctx->hBmp || !ctx->pBits) {
            DeleteDC(ctx->hDC);
            ReleaseDC(NULL, ctx->hScreen);
            delete ctx;
            return nullptr;
        }

        // 5. Bitmap'i DC'ye seç
        SelectObject(ctx->hDC, ctx->hBmp);

        return ctx;
    }

    __declspec(dllexport) bool grab_frame(CapContext* ctx, unsigned char* buffer, size_t bufferSize) {
        // Güvenlik kontrolleri (Buffer Overrun önleme)
        if (!ctx || !buffer || !ctx->pBits || bufferSize < ctx->bufferSize) {
            return false;
        }

        // BitBlt ile ekranı belleğe kopyala
        // SRCCOPY | CAPTUREBLT: Katmanlı (yarı saydam) pencereleri de dahil eder.
        BOOL success = BitBlt(
            ctx->hDC, 0, 0, ctx->width, ctx->height, 
            ctx->hScreen, 0, 0, 
            SRCCOPY | CAPTUREBLT
        );

        if (success) {
            // Veriyi Python'dan gelen tampon belleğe (buffer) güvenli kopyala
            memcpy(buffer, ctx->pBits, ctx->bufferSize);
            return true;
        }

        return false;
    }

    __declspec(dllexport) void release_engine(CapContext* ctx) {
        if (!ctx) return;

        // GDI Kaynaklarını doğru sırayla temizle (Memory Leak önleme)
        if (ctx->hBmp) DeleteObject(ctx->hBmp);
        if (ctx->hDC) DeleteDC(ctx->hDC);
        if (ctx->hScreen) ReleaseDC(NULL, ctx->hScreen);

        delete ctx;
    }
}