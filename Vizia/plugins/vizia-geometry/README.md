# Vizia Geometri Stüdyosu

Vizia Pen için modern, etkileşimli geometri eklentisi.

## Özellikler

- **Canvas tabanlı şekiller** – Şekiller ayrı pencere yerine doğrudan canvas overlay üzerinde çizilir
- **Sürüklenebilir araç paneli** – Paneli istediğiniz yere taşıyın (☰ tutamak)
- **Şekil önizlemeli butonlar** – Her buton şeklin ikonunu gösterir
- **Sürükle-bırak ekleme** – Şekil butonlarını sürükleyip canvas'a bırakarak şekil ekleyin
- **Sürükleyerek şekil çizimi** – Canvas üzerinde basılı tutup sürüklerken gerçek şekil önizlemesi
- **360° döndürme** – Şekilleri slider veya turuncu döndürme tutamağıyla döndürün
- **Dolgu aç/kapat** – Şekillerin içini dolu veya boş yapın
- **Kenarlık kalınlığı** – İnce, Orta, Kalın seçenekleri
- **Ok (Arrow) şekli** – Akış diyagramları ve işaretleme için ok şekli
- **Not kutusu** – İçine metin yazılabilen köşe kıvrımlı not kağıdı
- **Vizia tarzı renk seçici** – HSV slider'lı modern renk paleti (Windows dialog yerine)
- **Kayıtlı özel renkler** – Özel renkler JSON dosyasına kaydedilir
- **Kalem uyumluluğu** – Panel `WindowDoesNotAcceptFocus` ile kalem modunu bozmaz
- **Geri al (Undo)** – ↩ butonu ile son işlemi geri alın
- **Tümünü temizle** – Tüm şekilleri tek tuşla silin
- **Sağ tık menüsü** – Tek şekil silme, öne/arkaya taşıma
- **Gelişmiş tutamaklar** – Yuvarlak köşe + kenar orta tutamakları + döndürme tutamağı
- **Masaüstü modu** – debug.py tüm masaüstünü kaplar
- **Zengin şekil çeşitliliği** – Dikdörtgen, Daire, Üçgen, Yıldız, Ok, Not Kutusu, Izgara, Çizgi

## Dosya Yapısı

| Dosya | Açıklama |
|-------|----------|
| `shapes.py` | `CanvasShape` – döndürme, dolgu, ok, not kutusu destekli şekil modeli |
| `toolbox.py` | `ShapeCanvasOverlay` – şeffaf şekil katmanı, `GeometryToolbox` – iki satırlı araç çubuğu, `ViziaColorPicker` – modern renk seçici |
| `plugin.py` | `ViziaPlugin` – eklenti giriş noktası |
| `debug.py` | Masaüstü overlay modu ile bağımsız test |

## Test

```bash
python debug.py
```
