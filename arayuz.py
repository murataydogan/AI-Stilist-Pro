import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import json
import threading
import time
from datetime import datetime, timedelta
from gardiropv2 import AkilliGardirop
import telefon_baglantisi

# Ses Kütüphanesi Kontrolü (Hata varsa çökmesin diye)
try:
    import speech_recognition as sr

    SES_AKTIF = True
except ImportError:
    SES_AKTIF = False
    print("⚠️ UYARI: 'SpeechRecognition' yüklü değil. Sesli komut çalışmaz.")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Renkler
C_BG = "#09090b"
C_PANEL = "#18181b"
C_ACCENT = "#8b5cf6"
C_SUCCESS = "#10b981"
C_DANGER = "#ef4444"
C_TEXT = "#e4e4e7"


class GardiropApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.ai = AkilliGardirop()
        self.kombinler = []
        self.index = 0
        self.user = self.load_user()

        self.title("AI Stilist - GitHub Edition")
        self.geometry("1300x900")
        self.configure(fg_color=C_BG)

        if self.user:
            self.init_main()
        else:
            self.init_login()

    def load_user(self):
        if os.path.exists("kullanici.json"):
            try:
                return json.load(open("kullanici.json", "r", encoding="utf-8"))
            except:
                return None
        return None

    def init_login(self):
        self.login_fr = ctk.CTkFrame(self, fg_color="transparent")
        self.login_fr.pack(fill="both", expand=True)
        p = ctk.CTkFrame(self.login_fr, width=400, height=500, corner_radius=20, fg_color=C_PANEL)
        p.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(p, text="AI STILIST", font=("Segoe UI", 36, "bold"), text_color=C_ACCENT).pack(pady=(50, 10))
        self.e_ad = ctk.CTkEntry(p, placeholder_text="Adınız", width=250);
        self.e_ad.pack(pady=10)
        self.e_soyad = ctk.CTkEntry(p, placeholder_text="Soyadınız", width=250);
        self.e_soyad.pack(pady=10)
        ctk.CTkButton(p, text="BAŞLAT", command=self.save_user, fg_color=C_ACCENT, width=250).pack(pady=30)

    def save_user(self):
        ad, soyad = self.e_ad.get(), self.e_soyad.get()
        if not ad: return
        self.user = {"ad": ad, "soyad": soyad}
        json.dump(self.user, open("kullanici.json", "w"), indent=4)
        self.login_fr.destroy()
        self.init_main()

    def init_main(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SOL MENÜ
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=C_PANEL, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="👤", font=("Arial", 40)).pack(pady=(40, 10))
        ctk.CTkLabel(self.sidebar, text=f"{self.user['ad']} {self.user['soyad']}", font=("Segoe UI", 18, "bold"),
                     text_color="white").pack()

        ctk.CTkLabel(self.sidebar, text="Nereye Gidiyorsun?", text_color="gray", anchor="w").pack(fill="x", padx=20,
                                                                                                  pady=(30, 5))
        self.combo_baglam = ctk.CTkComboBox(self.sidebar, values=["Tümü", "Günlük", "Spor", "Düğün/Özel", "Ofis"],
                                            state="readonly")
        self.combo_baglam.set("Tümü")
        self.combo_baglam.pack(fill="x", padx=20)

        self.weather_fr = ctk.CTkFrame(self.sidebar, fg_color="#27272a")
        self.weather_fr.pack(fill="x", padx=20, pady=20)
        self.lbl_weather = ctk.CTkLabel(self.weather_fr, text="Hava Alınıyor...", text_color=C_SUCCESS)
        self.lbl_weather.pack(pady=10)
        self.btn_weather = ctk.CTkButton(self.weather_fr, text="Güncelle", height=20, command=self.get_weather,
                                         fg_color="#333")
        self.btn_weather.pack(pady=(0, 10))

        self.menu_btn("➕  Kıyafet Yükle", self.upload_pc)
        self.menu_btn("📱  Mobil Yükle", self.open_qr)
        self.menu_btn("📅  Takvimim", self.open_calendar)
        self.menu_btn("🖼️  Dolap Yönetimi", self.open_gallery)

        # SES BUTONU (Hata varsa devre dışı bırak)
        state_mic = "normal" if SES_AKTIF else "disabled"
        text_mic = "🎙️  SESLİ KOMUT" if SES_AKTIF else "⚠️ MİKROFON YOK"
        self.btn_mic = ctk.CTkButton(self.sidebar, text=text_mic, command=self.listen_mic, fg_color=C_DANGER,
                                     hover_color="#991b1b", height=50, state=state_mic)
        self.btn_mic.pack(side="bottom", fill="x", padx=20, pady=20)

        # SAĞ PANEL
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        self.lbl_title = ctk.CTkLabel(self.main, text="Bugünün Stili", font=("Segoe UI", 32, "bold"),
                                      text_color="white")
        self.lbl_title.pack(anchor="w")

        # ANALİZ PANELİ
        self.analysis_frame = ctk.CTkFrame(self.main, fg_color="#222", corner_radius=15, height=90)
        self.analysis_frame.pack(fill="x", pady=15)
        self.analysis_frame.pack_propagate(False)

        self.lbl_score_val = ctk.CTkLabel(self.analysis_frame, text="--", font=("Arial", 32, "bold"), text_color="gray")
        self.lbl_score_val.pack(side="left", padx=(20, 5))
        self.lbl_score_txt = ctk.CTkLabel(self.analysis_frame, text="UYUM\nPUANI", font=("Segoe UI", 10),
                                          text_color="gray")
        self.lbl_score_txt.pack(side="left")

        ctk.CTkFrame(self.analysis_frame, width=2, height=50, fg_color="#444").pack(side="left", padx=20)
        self.lbl_reason = ctk.CTkLabel(self.analysis_frame, text="Kombin oluşturmak için butona basın.",
                                       font=("Segoe UI", 13), text_color="#ccc", anchor="w", wraplength=700)
        self.lbl_reason.pack(side="left", fill="x", expand=True)

        # Kartlar
        self.card_area = ctk.CTkFrame(self.main, fg_color="transparent")
        self.card_area.pack(fill="both", expand=True, pady=10)
        self.card_area.grid_columnconfigure((0, 1, 2), weight=1)

        self.c_ust = self.make_card("ÜST", 0);
        self.img_ust = self.c_ust.winfo_children()[1]
        self.c_alt = self.make_card("ALT", 1);
        self.img_alt = self.c_alt.winfo_children()[1]
        self.c_ayak = self.make_card("AYAK", 2);
        self.img_ayak = self.c_ayak.winfo_children()[1]

        # Öğrenme
        self.feedback_fr = ctk.CTkFrame(self.main, fg_color="transparent")
        self.feedback_fr.pack(pady=5)
        self.btn_like = ctk.CTkButton(self.feedback_fr, text="👍 Beğendim", width=150, fg_color=C_SUCCESS,
                                      command=lambda: self.vote("like"), state="disabled")
        self.btn_like.pack(side="left", padx=10)
        self.btn_dislike = ctk.CTkButton(self.feedback_fr, text="👎 Kötü", width=150, fg_color=C_DANGER,
                                         command=lambda: self.vote("dislike"), state="disabled")
        self.btn_dislike.pack(side="left", padx=10)

        # Kontrol
        self.ctrl = ctk.CTkFrame(self.main, height=80, corner_radius=40, fg_color=C_PANEL)
        self.ctrl.pack(fill="x", pady=10)
        self.b_prev = ctk.CTkButton(self.ctrl, text="◀", width=50, command=self.prev_c, state="disabled",
                                    fg_color="#333")
        self.b_prev.pack(side="left", padx=20, pady=15)
        self.b_gen = ctk.CTkButton(self.ctrl, text="✨ KOMBİN YARAT", command=self.gen_combin, fg_color=C_ACCENT,
                                   font=("Segoe UI", 16, "bold"), height=50)
        self.b_gen.pack(side="left", fill="x", expand=True, padx=20)
        self.b_save = ctk.CTkButton(self.ctrl, text="📅 Takvime Kaydet", command=self.save_calendar, width=120,
                                    state="disabled", fg_color="#333")
        self.b_save.pack(side="left", padx=(0, 20))
        self.b_next = ctk.CTkButton(self.ctrl, text="▶", width=50, command=self.next_c, state="disabled",
                                    fg_color="#333")
        self.b_next.pack(side="left", padx=20)

        self.after(1000, self.get_weather)

    def menu_btn(self, txt, cmd):
        ctk.CTkButton(self.sidebar, text=f"  {txt}", command=cmd, fg_color="transparent", anchor="w",
                      hover_color="#333").pack(fill="x", padx=20, pady=5)

    def make_card(self, title, col):
        f = ctk.CTkFrame(self.card_area, fg_color=C_PANEL, corner_radius=15)
        f.grid(row=0, column=col, sticky="nsew", padx=10)
        ctk.CTkLabel(f, text=title, text_color="gray").pack(pady=10)
        l = ctk.CTkLabel(f, text="?", font=("Arial", 60), text_color="#333")
        l.pack(expand=True)
        return f

    # --- GELİŞTİRİLMİŞ SESLİ KOMUT FONKSİYONU ---
    def listen_mic(self):
        if not SES_AKTIF:
            messagebox.showerror("Hata",
                                 "SpeechRecognition kütüphanesi yüklü değil.\n'pip install SpeechRecognition pyaudio' komutunu çalıştırın.")
            return

        def thread_mic():
            self.btn_mic.configure(text="👂 Dinleniyor...", fg_color=C_SUCCESS, state="disabled")
            r = sr.Recognizer()

            try:
                # Mikrofonu kontrol et
                with sr.Microphone() as source:
                    # Gürültü ayarı (Önemli!)
                    r.adjust_for_ambient_noise(source, duration=1)
                    print("Dinlemeye başladım...")

                    try:
                        # 5 saniye bekle, ses gelmezse kapat
                        audio = r.listen(source, timeout=5, phrase_time_limit=5)
                        print("Ses alındı, işleniyor...")

                        # Google'a gönder
                        text = r.recognize_google(audio, language="tr-TR").lower()
                        print(f"Algılanan: {text}")

                        # Komutları işle
                        if "kombin" in text or "yap" in text:
                            self.after(0, self.gen_combin)
                            messagebox.showinfo("Jarvis", "Kombin oluşturuluyor...")
                        elif "spor" in text:
                            self.after(0, lambda: self.set_context("Spor"))
                            messagebox.showinfo("Jarvis", "Spor modu aktif.")
                        elif "günlük" in text:
                            self.after(0, lambda: self.set_context("Günlük"))
                            messagebox.showinfo("Jarvis", "Günlük mod aktif.")
                        elif "hava" in text:
                            self.after(0, self.get_weather)
                            messagebox.showinfo("Jarvis", "Hava durumu güncellendi.")
                        else:
                            messagebox.showinfo("Jarvis", f"Dediğini anladım: '{text}'\nAncak bu bir komut değil.")

                    except sr.WaitTimeoutError:
                        messagebox.showwarning("Jarvis", "Ses algılanamadı. Lütfen tekrar deneyin.")
                    except sr.UnknownValueError:
                        messagebox.showwarning("Jarvis", "Ne dediğinizi anlayamadım.")
                    except sr.RequestError:
                        messagebox.showerror("Jarvis", "İnternet bağlantınızı kontrol edin.")

            except Exception as e:
                # Genellikle PyAudio hatası burada düşer
                messagebox.showerror("Mikrofon Hatası",
                                     f"Mikrofon başlatılamadı.\nHata: {e}\nLütfen 'pip install pyaudio' yaptığınızdan emin olun.")

            finally:
                # Butonu eski haline getir
                self.btn_mic.configure(text="🎙️  SESLİ KOMUT", fg_color=C_DANGER, state="normal")

        threading.Thread(target=thread_mic).start()

    def set_context(self, ctx):
        self.combo_baglam.set(ctx)
        self.gen_combin()

    def vote(self, type):
        if not self.kombinler: return
        data = self.kombinler[self.index]
        u, a, _ = data["kombin"]
        self.ai.kombini_oyla(u['renk'], a['renk'], type)
        msg = "Harika! Bunu hafızama aldım." if type == "like" else "Tamam, bir daha göstermem."
        messagebox.showinfo("AI Öğreniyor", msg)

    def save_calendar(self):
        if not self.kombinler: return
        data = self.kombinler[self.index]["kombin"]
        yarin = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.ai.takvime_ekle(data, yarin)
        messagebox.showinfo("Takvim", f"Kombin {yarin} tarihi için takvime eklendi!")

    def open_calendar(self):
        top = ctk.CTkToplevel(self)
        top.title("Takvimim")
        top.geometry("600x400")
        ctk.CTkLabel(top, text="Planlanan Kombinler", font=("Bold", 20)).pack(pady=20)
        scroll = ctk.CTkScrollableFrame(top)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        for tarih, data in self.ai.takvim.items():
            ust, alt, _ = data
            txt = f"📅 {tarih}: {ust['renk']} Üst + {alt['renk']} Alt"
            ctk.CTkLabel(scroll, text=txt, anchor="w", fg_color="#333", corner_radius=5).pack(fill="x", pady=5, padx=5)

    def get_weather(self):
        h = self.ai.otomatik_hava_durumu()
        if h: self.lbl_weather.configure(text=f"{h}")

    def upload_pc(self):
        path = filedialog.askopenfilename()
        if path:
            tarz = self.ask_style()
            res = self.ai.kiyafet_ekle(path, tarz)
            if res: messagebox.showinfo("Başarılı", f"Eklendi: {res['renk']} ({res['tarz']})")

    def ask_style(self):
        dialog = ctk.CTkInputDialog(text="Bu kıyafetin tarzı ne?\n(Günlük, Spor, Ofis, Düğün/Özel)",
                                    title="Tarz Belirle")
        val = dialog.get_input()
        return val if val in ["Spor", "Ofis", "Düğün/Özel"] else "Günlük"

    def open_qr(self):
        img, url = telefon_baglantisi.qr_kod_olustur()
        top = ctk.CTkToplevel(self)
        top.geometry("400x500")
        ctk.CTkLabel(top, text="Mobil Yükleme").pack(pady=20)
        ctk.CTkLabel(top, image=ctk.CTkImage(img, size=(200, 200)), text="").pack()
        ctk.CTkLabel(top, text=url).pack(pady=20)
        self.check_mobile(top)

    def check_mobile(self, win):
        if not win.winfo_exists(): return
        if telefon_baglantisi.son_yuklenen_dosya:
            path = telefon_baglantisi.son_yuklenen_dosya
            telefon_baglantisi.son_yuklenen_dosya = None
            win.destroy()
            self.ai.kiyafet_ekle(path, "Günlük")
            messagebox.showinfo("Başarılı", "Mobilden dosya geldi!")
        else:
            self.after(1000, lambda: self.check_mobile(win))

    def gen_combin(self):
        baglam = self.combo_baglam.get()
        self.kombinler = self.ai.kombin_hesapla(self.lbl_weather.cget("text"), baglam)
        self.index = 0
        if not self.kombinler:
            messagebox.showwarning("Bulunamadı",
                                   f"{baglam} tarzında veya bu havada uygun kombin yok.\nDolaba daha fazla parça ekle.")
            self.lbl_score_val.configure(text="--", text_color="gray")
            self.lbl_reason.configure(text="Kombin bulunamadı.")
            return
        self.show_c()

    def show_c(self):
        data = self.kombinler[self.index]
        u, a, ay = data["kombin"]
        score = data["puan"]
        reason = data["sebep"]

        self.set_img(u['dosya'], self.img_ust)
        self.set_img(a['dosya'], self.img_alt)
        if ay['dosya']:
            self.set_img(ay['dosya'], self.img_ayak)
        else:
            self.img_ayak.configure(image=None, text="👟")

        self.lbl_score_val.configure(text=f"{score}")
        if score >= 85:
            self.lbl_score_val.configure(text_color=C_SUCCESS)
        elif score >= 60:
            self.lbl_score_val.configure(text_color="#facc15")
        else:
            self.lbl_score_val.configure(text_color=C_DANGER)

        self.lbl_reason.configure(text=f"Stilist Notu: {reason}")

        self.btn_like.configure(state="normal")
        self.btn_dislike.configure(state="normal")
        self.b_save.configure(state="normal")
        self.b_next.configure(state="normal" if self.index < len(self.kombinler) - 1 else "disabled")
        self.b_prev.configure(state="normal" if self.index > 0 else "disabled")

    def set_img(self, path, lbl):
        try:
            i = Image.open(path)
            i.thumbnail((250, 350))
            ci = ctk.CTkImage(i, size=i.size)
            lbl.configure(image=ci, text="")
        except:
            pass

    def next_c(self):
        self.index += 1
        self.show_c()

    def prev_c(self):
        self.index -= 1
        self.show_c()

    def open_gallery(self):
        top = ctk.CTkToplevel(self)
        top.geometry("800x600")
        scroll = ctk.CTkScrollableFrame(top)
        scroll.pack(fill="both", expand=True)
        for i, p in enumerate(self.ai.dolap):
            f = ctk.CTkFrame(scroll)
            f.grid(row=i // 4, column=i % 4, padx=10, pady=10)
            try:
                img = Image.open(p['dosya'])
                img.thumbnail((100, 100))
                ctk.CTkLabel(f, image=ctk.CTkImage(img, size=img.size), text="").pack()
            except:
                ctk.CTkLabel(f, text="Resim Yok").pack()
            ctk.CTkLabel(f, text=f"{p['renk']}\n{p.get('tarz', 'Günlük')}").pack()
            ctk.CTkButton(f, text="Sil", height=20, fg_color=C_DANGER,
                          command=lambda x=p: self.delete_item(x, top)).pack(pady=5)

    def delete_item(self, item, win):
        self.ai.dolap.remove(item)
        self.ai.kaydet(self.ai.dolap, self.ai.db_adi)
        win.destroy()
        self.open_gallery()


if __name__ == "__main__":
    app = GardiropApp()
    app.mainloop()