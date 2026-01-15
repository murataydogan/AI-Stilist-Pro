# 👔 AI Stilist Pro (Yapay Zeka Gardırop Asistanı)

> **"Bilgisayarlı görü, renk teorisi ve yapay zeka algoritmalarını birleştirerek kişisel stil danışmanınız olan akıllı masaüstü uygulaması."**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-0078D6?style=for-the-badge&logo=windows)
![AI](https://img.shields.io/badge/AI-OpenCV_%26_KMeans-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Beta_v1.0-green?style=for-the-badge)

## 🌟 Proje Hakkında
**AI Stilist Pro**, klasik gardırop uygulamalarının ötesine geçerek, kıyafetlerinizi matematiksel ve estetik kurallara göre analiz eden bir "Karar Destek Sistemi"dir.

Kullanıcı "Ne giysem?" diye düşündüğünde; sistem o günkü hava durumunu, gidilecek mekanı (Spor/Ofis/Düğün) ve renk teorisi (Color Theory) kurallarını işleyerek en uygun kombini puanlar ve önerir. Ayrıca sesli komutlarla ("Jarvis Modu") yönetilebilir.

## 🚀 Öne Çıkan Özellikler

### 🧠 1. Yapay Zeka Analizi (Computer Vision)
* Yüklenen kıyafet fotoğraflarının arka planını otomatik temizler (`rembg`).
* `K-Means` kümeleme algoritması ile kıyafetin baskın rengini milimetrik olarak tespit eder.
* Kıyafet türünü (Üst/Alt/Ayakkabı) görüntü oranlarına göre otomatik sınıflandırır.

### 🎨 2. Akıllı Puanlama Algoritması
Sadece rastgele eşleştirme yapmaz. Her kombine 0-100 arası bir **"Uyum Puanı"** verir ve nedenini açıklar:
* **Renk Uyumu:** Monokrom, Analog, Tam Zıt (Complementary) kurallarını uygular.
* **Sandviç Kuralı:** Ayakkabı ve üst giyim arasındaki renk dengesini kontrol eder.
* **Hava Durumu:** Yağmurlu havada beyaz pantolonu, kapalı havada aşırı canlı renkleri engeller.

### 🎙️ 3. Sesli Asistan & IoT
* **Sesli Komut:** "Bana spor kombin yap" veya "Hava nasıl?" komutlarıyla klavyesiz yönetim.
* **Mobil Bağlantı:** Aynı Wi-Fi ağındaki telefondan QR kod ile anında bilgisayara fotoğraf aktarımı (Flask Sunucusu).

### 📈 4. Öğrenen Sistem (Reinforcement Learning Lite)
* Kullanıcının "Beğendim" 👍 veya "Beğenmedim" 👎 tepkilerini hafızaya alır.
* Kullanıcının zevklerini öğrenerek zamanla daha kişiselleştirilmiş öneriler sunar.

## 🛠️ Kurulum

Projeyi kendi bilgisayarınızda çalıştırmak için:

1. **Repoyu Klonlayın:**
   ```bash
   git clone [https://github.com/murataydogan/AI-Stilist-Pro.git](https://github.com/murataydogan/AI-Stilist-Pro.git)
   cd AI-Stilist-Pro
   
2. Gerekli Kütüphaneleri Yükleyin:
Bash
pip install -r requirements.txt

3. Uygulamayı Başlatın:
Bash
python arayuz.py

📂 Dosya Yapısı

arayuz.py: Uygulamanın ana ekranı, modern arayüz ve sesli asistan kodları.

gardiropv2.py: Projenin "Beyni". AI analizleri, puanlama motoru ve veritabanı yönetimi.

telefon_baglantisi.py: Telefondan bilgisayara resim aktaran yerel sunucu.

requirements.txt: Proje bağımlılıkları.

📄 Lisans
Bu proje MIT Lisansı ile açık kaynak olarak sunulmuştur.

Geliştirici: Murat Aydoğan
