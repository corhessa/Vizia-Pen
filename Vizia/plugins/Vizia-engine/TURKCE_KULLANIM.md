# Vizia Studio Pro - Türkçe Kullanım Kılavuzu

## Hoş Geldiniz! 🎨

Vizia Studio Pro, güçlü bir 3D editör ve geliştirme ortamıdır. Bu kılavuz ile editörü hızlıca kullanmaya başlayabilirsiniz.

## Hızlı Başlangıç

### Kurulum

```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Editörü başlatın
python main.py
```

### İlk Adımlar

1. **Editör açıldığında** 1200x800 boyutunda bir pencere görürsünüz
2. **Tam ekran için** F11 tuşuna basın
3. **Konsol panelinde** hoş geldin mesajlarını okuyun

## Arayüz Açıklaması

### 📋 HİYERARŞİ (Sol Panel)
**Ne İşe Yarar:** Sahnenizdeki tüm nesneleri ağaç yapısında gösterir.

**Nasıl Kullanılır:**
- **Sağ tıklayın** → Nesne eklemek için menü açılır
  - ➕ Küp Ekle
  - ➕ Küre Ekle
  - 💡 Işık Ekle
  - 📷 Kamera Ekle
- **Nesneye tıklayın** → Seçili nesne mavi renkte görünür
- **Seçili nesne** → Özellikler panelinde düzenlenebilir

### 🎬 3D GÖRÜNÜM (Merkez)
**Ne İşe Yarar:** 3D sahnenizi gerçek zamanlı olarak görüntüler.

**Kamera Kontrolleri:**
- **Döndür:** Alt + Sol Fare
- **Kaydır:** Orta Fare Tuşu
- **Yakınlaştır:** Fare Tekerleği

**Izgara ve Grid:** Varsayılan olarak görünür

### 🔍 ÖZELLİKLER (Sağ Panel)
**Ne İşe Yarar:** Seçili nesnenin özelliklerini gösterir ve düzenler.

**Düzenleyebilecekleriniz:**
- **Konum** (Position) - X, Y, Z eksenleri
- **Döndürme** (Rotation) - Açı değerleri
- **Ölçek** (Scale) - Büyüklük ayarları
- **Materyal** - Renk, metallik, pürüzlülük

### 🛠️ ARAÇ ÇUBUĞU (Üst)

#### Oynatma Kontrolleri
- **▶ Çalıştır** - Sahneyi çalıştırır
- **⏸ Duraklat** - Sahneyi durdurur
- **⏹ Durdur** - Sahneyi tamamen durdurur

#### Dönüşüm Araçları
- **🔄 Taşı (W)** - Nesneyi taşıma modu
- **🔃 Döndür (E)** - Nesneyi döndürme modu
- **📏 Ölçekle (R)** - Nesneyi ölçeklendirme modu

#### Diğer
- **💾 Kaydet (Ctrl+S)** - Sahneyi kaydet

### 📄 KONSOL (Alt Panel)
**Ne İşe Yarar:** Sistem mesajlarını gösterir.

**Mesaj Türleri:**
- **📝 Bilgi** - Normal mesajlar (mavi)
- **⚠️ Uyarı** - Uyarı mesajları (sarı)
- **❌ Hata** - Hata mesajları (kırmızı)

**Kontroller:**
- **🗑️ Temizle** - Tüm mesajları siler
- **Filtre Butonları** - Mesaj türlerini göster/gizle

### 💻 TERMİNAL (Alt Panel)
**Ne İşe Yarar:** TypeScript/JavaScript kodu yazıp çalıştırabilirsiniz.

**Özellikler:**
- Monaco Editor ile kod yazma
- Syntax highlighting
- Otomatik tamamlama
- Sahne API'sine erişim

**Örnek Kod:**
```javascript
// Küp ekle
app.scene.addCube('BenimKübüm', [0, 1, 0]);

// Küre ekle
app.scene.addSphere('BenimKürem', [2, 1, 0]);

// Sahneyi kaydet
app.saveScene();
```

### 📦 VARLIKLAR (Alt Panel)
**Ne İşe Yarar:** Proje dosyalarınızı yönetir.

**Klasörler:**
- 📁 Sahneler
- 📁 Modeller
- 📁 Dokular
- 📁 Materyaller

## Kısayol Tuşları ⌨️

### Genel
- **F11** - Tam ekran aç/kapat
- **Ctrl+S** - Sahneyi kaydet
- **Ctrl+Z** - Geri al
- **Ctrl+Y** - Yinele

### Araçlar
- **W** - Taşıma aracı
- **E** - Döndürme aracı
- **R** - Ölçeklendirme aracı

### Nesne İşlemleri
- **Delete** - Seçili nesneyi sil
- **F** - Seçili nesneye odaklan
- **Ctrl+D** - Nesneyi kopyala

## İş Akışı Önerileri

### Yeni Sahne Oluşturma

1. **Editörü Açın**
   ```bash
   python main.py
   ```

2. **Tam Ekran Yapın**
   - F11 tuşuna basın
   - Daha geniş çalışma alanı elde edin

3. **İlk Nesneyi Ekleyin**
   - Hiyerarşi panelinde sağ tıklayın
   - "➕ Küp Ekle" seçin

4. **Nesneyi Düzenleyin**
   - Hiyerarşide nesneye tıklayın
   - Özellikler panelinde konum/ölçek ayarlayın

5. **Daha Fazla Nesne Ekleyin**
   - Sağ tıklayıp menüden seçin
   - Terminal ile kod yazarak ekleyin

6. **Sahneyi Kaydedin**
   - Ctrl+S tuşlarına basın
   - Veya 💾 Kaydet butonuna tıklayın

### Terminal ile Toplu İşlem

Terminal kullanarak birden fazla nesne ekleyebilirsiniz:

```javascript
// 5 küp oluştur
for (let i = 0; i < 5; i++) {
    app.scene.addCube(`Küp_${i}`, [i * 2, 1, 0]);
}

// Daire şeklinde küreler
const radius = 5;
const count = 8;
for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2;
    const x = Math.cos(angle) * radius;
    const z = Math.sin(angle) * radius;
    app.scene.addSphere(`Küre_${i}`, [x, 1, z]);
}
```

## Sorun Giderme

### Siyah Ekran Görüyorum
**Çözüm:** 
- İnternet bağlantınızı kontrol edin (Galacean CDN'den yükleniyor)
- Konsol paneline bakın, hata mesajları var mı kontrol edin
- WebGL desteğinizi kontrol edin

### PyQtWebEngine Bulunamadı
**Çözüm:**
```bash
pip install PyQtWebEngine==5.15.7
```

### Pencere Çok Küçük
**Çözüm:**
- F11 ile tam ekran yapın
- Veya pencere kenarlıklarından manuel olarak büyütün

### Türkçe Karakterler Hatalı
**Çözüm:**
- Dosyaların UTF-8 kodlamasında olduğundan emin olun
- Tarayıcı ayarlarınızı kontrol edin

## İpuçları 💡

### Performans
- Çok fazla nesne eklerseniz FPS düşebilir
- 100'den fazla nesne için optimize edin

### Navigasyon
- Alt tuşu ile kamera kontrolü yapın
- Fare tekerleği ile yakınlaştırma çok hızlı

### Organizasyon
- Nesnelere anlamlı isimler verin
- Hiyerarşide parent-child ilişkisi kullanın

### Kaydetme
- Sık sık Ctrl+S ile kaydedin
- LocalStorage'da saklanır
- Export işlevi için terminal kullanın

## Sık Sorulan Sorular

### Q: Tam ekrandan nasıl çıkarım?
**A:** F11 tuşuna tekrar basın veya Esc tuşu.

### Q: Sahnem nerede kaydediliyor?
**A:** Tarayıcının LocalStorage'ında. Export için terminal kullanın.

### Q: İnternet olmadan çalışır mı?
**A:** Hayır, Galacean Engine CDN'den yükleniyor. İnternet gerekli.

### Q: Kendi 3D modellerimi ekleyebilir miyim?
**A:** Şu anda sadece temel şekiller (küp, küre). Gelecek versiyonlarda OBJ/FBX desteği gelecek.

### Q: Terminal'de hangi komutları kullanabilirim?
**A:** 
- `app.scene` - Sahne yönetimi
- `app.saveScene()` - Sahneyi kaydet
- Galacean Engine API'sine tam erişim var

## Destek ve İletişim

### Sorun Bildirme
- GitHub Issues: https://github.com/corhessa/Vizia-engine/issues

### Dokümantasyon
- README.md - İngilizce dokümantasyon
- QUICKSTART.md - Hızlı başlangıç rehberi
- ARCHITECTURE.md - Teknik detaylar

## Güncelleme Notları

### Versiyon 1.0 (Mevcut)
- ✅ Tamamen Türkçe arayüz
- ✅ Sistem pencere çubuğu
- ✅ F11 tam ekran desteği
- ✅ 1200x800 varsayılan boyut
- ✅ Gelişmiş buton tasarımı
- ✅ Panel başlıkları vurgulandı
- ✅ Hoş geldin mesajları
- ✅ Türkçe hata mesajları

---

**Vizia Studio Pro** - Türk geliştiriciler için optimize edilmiş 3D editör 🇹🇷

İyi çalışmalar! 🎨✨
