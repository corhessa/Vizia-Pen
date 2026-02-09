#include <windows.h>
#include <iostream>

struct CapContext {
    HDC hScreen;
    HDC hDC;
    HBITMAP hBmp;
    void* pBits;
    int width;
    int height;
};

extern "C" {
    __declspec(dllexport) CapContext* init_engine(int w, int h) {
        CapContext* ctx = new CapContext();
        ctx->width = w;
        ctx->height = h;

        // Ekran DC'sini al
        ctx->hScreen = GetDC(NULL); 
        ctx->hDC = CreateCompatibleDC(ctx->hScreen);

        // RGB Bitmap oluştur (4 Kanal - BGRA)
        BITMAPINFO bmi = {0};
        bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        bmi.bmiHeader.biWidth = w;
        bmi.bmiHeader.biHeight = -h; // Eksi değer görüntüyü düz (top-down) yapar
        bmi.bmiHeader.biPlanes = 1;
        bmi.bmiHeader.biBitCount = 32; // Her piksel 4 byte (B, G, R, Alpha)
        bmi.bmiHeader.biCompression = BI_RGB;

        ctx->hBmp = CreateDIBSection(ctx->hDC, &bmi, DIB_RGB_COLORS, &ctx->pBits, NULL, 0);
        SelectObject(ctx->hDC, ctx->hBmp);

        return ctx;
    }

    __declspec(dllexport) bool grab_frame(CapContext* ctx, unsigned char* buffer) {
        if (!ctx) return false;

        // BitBlt ile ekranı kopyala (SRCCOPY | CAPTUREBLT)
        // CAPTUREBLT: Yarı saydam pencereleri de alır
        BitBlt(ctx->hDC, 0, 0, ctx->width, ctx->height, ctx->hScreen, 0, 0, SRCCOPY | 0x40000000);

        // Veriyi Python buffer'ına kopyala
        memcpy(buffer, ctx->pBits, ctx->width * ctx->height * 4);
        
        return true;
    }

    __declspec(dllexport) void release_engine(CapContext* ctx) {
        if (!ctx) return;
        ReleaseDC(NULL, ctx->hScreen);
        DeleteDC(ctx->hDC);
        DeleteObject(ctx->hBmp);
        delete ctx;
    }
}