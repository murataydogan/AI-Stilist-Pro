import os
import socket
import threading
import qrcode
from flask import Flask, request, render_template_string
from PIL import Image
import io  # <--- YENİ EKLENDİ: Format dönüşümü için gerekli

# Yüklenen dosyaların geleceği klasör
YUKLEME_KLASORU = "gelen_fotograflar"
if not os.path.exists(YUKLEME_KLASORU):
    os.makedirs(YUKLEME_KLASORU)

HTML_SAYFASI = """
<!doctype html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial_scale=1.0">
    <title>Gardırop Yükleme</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #f0f0f0; }
        .btn { background-color: #2CC985; color: white; padding: 20px 40px; font-size: 20px; border: none; border-radius: 10px; cursor: pointer; width: 100%; margin-top: 20px;}
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>📸 Kıyafet Yükle</h1>
    <p>Bilgisayara göndermek için aşağıdan fotoğraf seç:</p>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="image/*" style="font-size: 18px;">
        <br><br>
        <input type="submit" value="GÖNDER 🚀" class="btn">
    </form>
</body>
</html>
"""

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = YUKLEME_KLASORU
son_yuklenen_dosya = None


@app.route('/', methods=['GET', 'POST'])
def yukleme_sayfasi():
    global son_yuklenen_dosya
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Dosya seçilmedi!'
        file = request.files['file']
        if file.filename == '':
            return 'Dosya yok!'
        if file:
            dosya_yolu = os.path.join(app.config['UPLOAD_FOLDER'], "son_gelen.jpg")
            file.save(dosya_yolu)
            son_yuklenen_dosya = dosya_yolu
            return """<h1 style='color:green; text-align:center; margin-top:50px;'>✅ YÜKLENDİ!</h1>
                      <p style='text-align:center;'>Bilgisayar ekranına bakabilirsin.</p>"""
    return render_template_string(HTML_SAYFASI)


def yerel_ip_bul():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def sunucuyu_baslat():
    try:
        # Arka planda sessizce çalışsın
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except:
        pass


def qr_kod_olustur():
    ip = yerel_ip_bul()
    url = f"http://{ip}:5000"

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    # QR kodunu oluşturuyoruz (Bu özel bir formatta geliyor)
    qr_ozel_format = qr.make_image(fill_color="black", back_color="white")

    # --- DÜZELTME BURADA ---
    # CustomTkinter'ın anlayacağı standart PIL formatına çeviriyoruz
    byte_stream = io.BytesIO()
    qr_ozel_format.save(byte_stream, format="PNG")  # Hafızaya kaydet
    byte_stream.seek(0)  # Başa sar
    img_pil = Image.open(byte_stream)  # Standart resim olarak aç

    return img_pil, url


threading.Thread(target=sunucuyu_baslat, daemon=True).start()