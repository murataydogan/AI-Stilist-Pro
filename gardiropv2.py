import cv2
import numpy as np
from sklearn.cluster import KMeans
import json
import os
import random
import requests
import math
import colorsys

try:
    from rembg import remove

    REMBG_AKTIF = True
except ImportError:
    REMBG_AKTIF = False


class AkilliGardirop:
    def __init__(self):
        self.db_adi = "dolabim.json"
        self.tercih_adi = "tercihler.json"
        self.takvim_adi = "takvim.json"

        self.renk_katalogu = {
            "Siyah": (20, 20, 20), "Beyaz": (250, 250, 250), "Gri": (128, 128, 128),
            "Kırmızı": (220, 20, 60), "Mavi": (30, 144, 255), "Yeşil": (34, 139, 34),
            "Lacivert": (0, 0, 128), "Kahverengi": (139, 69, 19), "Bej": (245, 245, 220),
            "Bordo": (128, 0, 0), "Sarı": (255, 215, 0), "Turuncu": (255, 140, 0),
            "Mor": (128, 0, 128), "Pembe": (255, 105, 180), "Haki": (240, 230, 140)
        }

        self.dolap = self.yukle(self.db_adi)
        self.tercihler = self.yukle(self.tercih_adi)
        self.takvim = self.yukle(self.takvim_adi)
        if not self.tercihler: self.tercihler = {"begenilenler": [], "yasaklananlar": []}

    def yukle(self, dosya):
        if os.path.exists(dosya):
            try:
                return json.load(open(dosya, "r", encoding="utf-8"))
            except:
                return [] if dosya == self.db_adi else {}
        return [] if dosya == self.db_adi else {}

    def kaydet(self, veri, dosya):
        json.dump(veri, open(dosya, "w", encoding="utf-8"), indent=4, ensure_ascii=False)

    # --- YENİLENMİŞ PUANLAMA MOTORU ---
    def hesapla_uyum_puani(self, ust, alt, ayak, hava):
        # Başlangıçta biraz rastgelelik ekle ki hepsi birebir aynı olmasın (Canlılık)
        puan = 60 + random.randint(-3, 3)
        notlar = []

        r_ust = ust['renk']
        r_alt = alt['renk']
        r_ayak = ayak['renk']

        # 1. Renk Analizi (İsim kullanarak yorum yap)
        if r_ust == r_alt:
            puan += 15
            notlar.append(f"{r_ust} Monokrom (Tek renk) bütünlüğü")
        elif r_ust in ["Siyah", "Beyaz"] or r_alt in ["Siyah", "Beyaz"]:
            puan += 20
            notlar.append(f"{r_ust} ve {r_alt} ile klasik kontrast")
        else:
            # Renk çarkı analizi
            uyum, ek_puan = self.renk_carki_analiz(r_ust, r_alt)
            puan += ek_puan
            if ek_puan > 0: notlar.append(uyum)

        # 2. Ayakkabı Detayı
        if r_ayak == r_ust:
            puan += 10
            notlar.append(f"Ayakkabı ve Üst ({r_ayak}) uyumu harika")
        elif r_ayak in ["Beyaz", "Siyah"]:
            puan += 5
            notlar.append("Nötr ayakkabı kurtarıcıdır")

        # 3. Hava Durumu
        if hava == "Güneşli" and r_ust in ["Sarı", "Turuncu", "Beyaz", "Mavi"]:
            puan += 8
            notlar.append("Güneşe yakışan canlı tonlar")
        elif hava == "Kapalı" and r_alt in ["Siyah", "Lacivert", "Gri"]:
            puan += 8
            notlar.append("Kapalı havaya uygun cool tonlar")

        # 4. Kişisel Tercih
        if f"{r_ust}-{r_alt}" in self.tercihler.get("begenilenler", []):
            puan += 15
            notlar.append("⭐ Sizin favoriniz")

        # Puanı sınırla
        puan = max(10, min(99, puan))

        # Yorumları birleştir
        sebep_metni = " • ".join(notlar)
        return puan, sebep_metni

    def renk_carki_analiz(self, r1, r2):
        rgb1 = self.renk_katalogu.get(r1, (0, 0, 0))
        rgb2 = self.renk_katalogu.get(r2, (0, 0, 0))
        h1 = colorsys.rgb_to_hsv(rgb1[0] / 255, rgb1[1] / 255, rgb1[2] / 255)[0] * 360
        h2 = colorsys.rgb_to_hsv(rgb2[0] / 255, rgb2[1] / 255, rgb2[2] / 255)[0] * 360
        diff = abs(h1 - h2)
        if diff > 180: diff = 360 - diff

        if 160 <= diff <= 200: return f"{r1} ve {r2} Zıt Uyumu", 25
        if diff <= 45: return f"{r1} ve {r2} Ton Sür Ton", 15
        return "", 0

    # --- STANDART FONKSİYONLAR ---
    def kombin_hesapla(self, hava, baglam="Tümü"):
        ustler = [x for x in self.dolap if x['tur'] == 'ust']
        altlar = [x for x in self.dolap if x['tur'] == 'alt']
        ayaklar = [x for x in self.dolap if x['tur'] == 'ayakkabi']
        if not ayaklar: ayaklar = [{"dosya": None, "renk": "Yok", "tur": "ayakkabi", "tarz": "Günlük"}]

        if baglam != "Tümü":
            ustler = [x for x in ustler if x.get('tarz', 'Günlük') == baglam]
            altlar = [x for x in altlar if x.get('tarz', 'Günlük') == baglam]

        adaylar = []
        imzalar = set()

        for u in ustler:
            for a in altlar:
                # Yasaklı kontrolü
                if f"{u['renk']}-{a['renk']}" in self.tercihler.get("yasaklananlar", []): continue

                for ay in ayaklar:
                    puan, sebep = self.hesapla_uyum_puani(u, a, ay, hava)

                    imza = (u['dosya'], a['dosya'], ay['dosya'])
                    if imza not in imzalar:
                        adaylar.append({"kombin": (u, a, ay), "puan": puan, "sebep": sebep})
                        imzalar.add(imza)

        adaylar.sort(key=lambda x: x['puan'], reverse=True)
        # Çeşitlilik için en iyi 5'i karıştır
        top5 = adaylar[:5]
        random.shuffle(top5)
        return top5 + adaylar[5:]

    def otomatik_hava_durumu(self):
        try:
            res = requests.get("https://wttr.in/?format=j1", timeout=3).json()
            durum = res['current_condition'][0]['weatherDesc'][0]['value'].lower()
            if any(x in durum for x in ["rain", "shower"]): return "Yağmurlu"
            if any(x in durum for x in ["snow", "ice"]): return "Karlı"
            if any(x in durum for x in ["cloud", "fog"]): return "Kapalı"
            return "Güneşli"
        except:
            return None

    def analiz_et(self, resim_yolu):
        try:
            with open(resim_yolu, "rb") as f:
                bytes_data = bytearray(f.read())
                numpy_array = np.asarray(bytes_data, dtype=np.uint8)
                image = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
        except:
            return None, None

        if image is None: return None, None

        small = cv2.resize(image, (300, 300))
        merkez = small[100:200, 100:200].reshape((-1, 3))
        kmeans = KMeans(n_clusters=1, n_init=5).fit(merkez)
        renk = self.en_yakin_renk(kmeans.cluster_centers_[0].astype(int)[::-1])

        h, w, _ = image.shape
        oran = h / w
        if oran > 1.4:
            tur = "alt"
        elif oran < 0.9:
            tur = "ayakkabi"
        else:
            tur = "ust"
        return renk, tur

    def en_yakin_renk(self, rgb):
        min_dist = float('inf');
        isim = "Bilinmeyen"
        for k, v in self.renk_katalogu.items():
            dist = math.sqrt(sum((rgb[i] - v[i]) ** 2 for i in range(3)))
            if dist < min_dist: min_dist = dist; isim = k
        return isim

    def kiyafet_ekle(self, yol, tarz="Günlük"):
        renk, tur = self.analiz_et(yol)
        if not renk: return None
        for p in self.dolap:
            if p['dosya'] == yol: return p
        yeni = {"id": len(self.dolap) + 1, "dosya": yol, "renk": renk, "tur": tur, "tarz": tarz}
        self.dolap.append(yeni)
        self.kaydet(self.dolap, self.db_adi)
        return yeni

    def kombini_oyla(self, u_renk, a_renk, durum):
        imza = f"{u_renk}-{a_renk}"
        if durum == "like":
            if imza not in self.tercihler["begenilenler"]: self.tercihler["begenilenler"].append(imza)
            if imza in self.tercihler["yasaklananlar"]: self.tercihler["yasaklananlar"].remove(imza)
        elif durum == "dislike":
            if imza not in self.tercihler["yasaklananlar"]: self.tercihler["yasaklananlar"].append(imza)
            if imza in self.tercihler["begenilenler"]: self.tercihler["begenilenler"].remove(imza)
        self.kaydet(self.tercihler, self.tercih_adi)

    def takvime_ekle(self, veri, tarih):
        self.takvim[tarih] = veri
        self.kaydet(self.takvim, self.takvim_adi)