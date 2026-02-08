import os

# 1. Dosya Yollarını Bul
current_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(current_dir, "Assets", "Web")
js_path = os.path.join(web_dir, "galacean.js")
html_path = os.path.join(web_dir, "vizia_editor.html")

print(f"Calisma Klasoru: {web_dir}")

# 2. Galacean.js'yi Oku
try:
    with open(js_path, "r", encoding="utf-8") as f:
        js_code = f.read()
    print(f"BASARILI: Galacean JS Okundu ({len(js_code)} karakter).")
except FileNotFoundError:
    print("HATA: galacean.js dosyasi bulunamadi! Lutfen ismini kontrol et.")
    exit()

# 3. HTML Şablonu (İçine JS Gömeceğiz)
# Not: HTML içindeki kodlarda emojiler sorun yaratmaz, sadece terminal çıktısı yaratır.
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vizia Studio Pro (Embedded)</title>
    <style>
        * {{ box-sizing: border-box; user-select: none; }}
        body {{ margin: 0; overflow: hidden; background-color: #1c1c1e; color: #e5e5e5; font-family: 'Segoe UI', sans-serif; height: 100vh; font-size: 12px; }}
        #loader {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #1c1c1e; z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
        .spinner {{ width: 40px; height: 40px; border: 4px solid #333; border-top: 4px solid #0a84ff; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 15px; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        canvas {{ width: 100%; height: 100%; display: block; outline: none; }}
    </style>

    <script>
    {js_code}
    </script>

</head>
<body>
    <div id="loader">
        <div class="spinner"></div>
        <div id="status">Vizia Engine Yukleniyor...</div>
    </div>
    
    <canvas id="canvas"></canvas>

    <script>
        // --- VIZIA BASLATMA KODU ---
        window.onload = function() {{
            if (typeof GALACEAN === 'undefined') {{
                alert("KRITIK HATA: JS Kodu Yuklenemedi!");
                return;
            }}
            initEngine();
        }};

        async function initEngine() {{
            try {{
                const engine = await GALACEAN.WebGLEngine.create({{ canvas: "canvas" }});
                engine.canvas.resizeByClientSize();
                const scene = engine.sceneManager.activeScene;
                const root = scene.createRootEntity("Root");
                scene.background.solidColor.set(0.15, 0.15, 0.15, 1);

                // Isik
                const light = root.createChild("Light");
                light.addComponent(GALACEAN.DirectLight);
                light.transform.setPosition(5, 10, 5);
                light.transform.lookAt(new GALACEAN.Vector3(0, 0, 0));

                // Kamera
                const camera = root.createChild("Camera");
                camera.addComponent(GALACEAN.Camera);
                camera.transform.setPosition(0, 2, 5);
                camera.transform.lookAt(new GALACEAN.Vector3(0, 0, 0));
                
                // Basit Kamera Kontrolu
                class Orbiter extends GALACEAN.Script {{
                    onAwake() {{
                        this.angle = 0;
                        this.r = 5;
                    }}
                    onUpdate() {{
                        this.angle += 0.5;
                        const rad = GALACEAN.MathUtil.degreeToRadian(this.angle);
                        this.entity.transform.setPosition(Math.sin(rad) * this.r, 2, Math.cos(rad) * this.r);
                        this.entity.transform.lookAt(new GALACEAN.Vector3(0,0,0));
                    }}
                }}
                camera.addComponent(Orbiter);

                // Kup
                const cube = root.createChild("Cube");
                const r = cube.addComponent(GALACEAN.MeshRenderer);
                r.mesh = GALACEAN.PrimitiveMesh.createCuboid(engine, 1, 1, 1);
                r.setMaterial(new GALACEAN.BlinnPhongMaterial(engine));

                engine.run();
                
                // Loader'i kapat
                setTimeout(() => {{
                    document.getElementById('loader').style.display = 'none';
                }}, 500);
                
                console.log("MOTOR CALISIYOR!");
            }} catch (e) {{
                alert("Motor Hatasi: " + e.message);
            }}
        }}
    </script>
</body>
</html>
"""

# 4. Dosyayı Kaydet
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print("ISLEM TAMAM! Galacean.js kodlari vizia_editor.html icine gomuldu.")
print("Simdi main.py dosyasini calistir.")