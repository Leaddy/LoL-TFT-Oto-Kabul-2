import cv2
import numpy as np
import pyautogui
import threading
import tkinter as tk
from tkinter import ttk
import time
import sys
import webbrowser
import psutil

class EkranIzlemeUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("LoL & TFT Oto Kabul")
        self.root.geometry("540x230")
        
        root.resizable(width=False, height=False)

        # İkon dosyasının adını ve yolunu belirtin (1.ico'nun olduğu yolu doğru şekilde verin)
        icon_path = "1.ico"
        
        # İkonu ayarlayın
        root.iconbitmap(default=icon_path)
        
        self.etiket = tk.Label(root, text="", font=("Helvetica", 16))
        self.etiket.pack(pady=20)
        
        self.baslat_button = ttk.Button(root, text="Başlat", command=self.baslat, style="TButton")
        self.baslat_button.pack(pady=10)
        
        self.durdur_button = ttk.Button(root, text="Durdur", state=tk.DISABLED, command=self.durdur, style="TButton")
        self.durdur_button.pack(pady=10)

        ttk.Style().configure("TButton", padding=5, relief="flat")

        # Sol alt köşede "Başlat/Durdur : Alt+K" yazısını gösteren etiket
        self.baslat_durdur_etiket = tk.Label(root, text="Başlat/Durdur : Alt+K", font=("Helvetica", 9), fg="black")
        self.baslat_durdur_etiket.pack(side=tk.LEFT, padx=10, pady=10, anchor='sw')

        self.leaddy_etiket = tk.Label(root, text="Coded By Leaddy", font=("Helvetica", 12), fg="red", cursor="hand2")
        self.leaddy_etiket.pack(side=tk.RIGHT, padx=10, pady=10, anchor='sw')
        self.leaddy_etiket.bind("<Button-1>", self.ac_leaddy_link)

        self.thread = None
        self.calisiyor = False
        self.kabul_et_bulundu = False
        self.bekleme_suresi = 10
        self.bekleme_sayaci = self.bekleme_suresi

        # Alt + K kombinasyonu için klavye olaylarını dinleyin
        self.root.bind_all("<Alt-k>", self.baslat_durdur_toggle)

    def baslat_durdur_toggle(self, event):
        if self.calisiyor:
            self.durdur()
        else:
            self.baslat()

    def baslat(self):
        self.calisiyor = True
        self.baslat_button.config(state=tk.DISABLED)
        self.durdur_button.config(state=tk.NORMAL)
        self.etiket.config(text="Program başlatıldı.")
        self.thread = threading.Thread(target=self.ekrani_izle_ve_kabul_et)
        self.thread.start()

    def durdur(self):
        self.calisiyor = False
        self.baslat_button.config(state=tk.NORMAL)
        self.durdur_button.config(state=tk.DISABLED)
        self.etiket.config(text="Program durduruldu.")

    def ekrani_izle_ve_kabul_et(self):
        self.etiket.config(text="Oyun tespit edildi. Ekran izleniyor...")

        while self.calisiyor:
            if not self.oyun_acik_mi("LeagueClient.exe"):
                self.etiket.config(text="Oyun açık değil. Lütfen oyunu açınız.")
            else:
                tespit_koordinatlar = self.tespit_et_kabul_et()

                if tespit_koordinatlar:
                    self.etiket.config(text="KABUL ET yazısı tespit edildi. Tıklanıyor...")
                    self.kabul_et_tikla(tespit_koordinatlar)
                    self.kabul_et_bulundu = True
                
                else:
                    if self.kabul_et_bulundu:
                        if self.bekleme_sayaci > 0:
                            self.etiket.config(text=f"KABUL ET yazısı kayboldu.")
                        else:
                            self.etiket.config(text="KABUL ET yazısı tekrar görülmedi.")
                            self.durdur()
                            self.kabul_et_bulundu = False
                            self.bekleme_sayaci = self.bekleme_suresi

            time.sleep(1)

    def oyun_acik_mi(self, uygulama_adi):
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if uygulama_adi.lower() in process.info['name'].lower():
                return True
        return False

    def tespit_et_kabul_et(self):
        ekran_goruntusu = pyautogui.screenshot()
        ekran_goruntu_np = np.array(ekran_goruntusu)
        ekran_goruntu_bgr = cv2.cvtColor(ekran_goruntu_np, cv2.COLOR_RGB2BGR)

        kabul_et_kalip = cv2.imread('kabul_et_kalip.png', cv2.IMREAD_COLOR)

        sonuc = cv2.matchTemplate(ekran_goruntu_bgr, kabul_et_kalip, cv2.TM_CCOEFF_NORMED)
        _, _, _, maksimum_lokasyon = cv2.minMaxLoc(sonuc)

        threshold_degeri = 0.8
        if sonuc[maksimum_lokasyon[1], maksimum_lokasyon[0]] >= threshold_degeri:
            x, y = maksimum_lokasyon
            x += 75
            y += 40
            return (x, y)
        else:
            return None

    def kabul_et_tikla(self, koordinatlar):
        x, y = koordinatlar
        pyautogui.click(x, y)

    def ac_leaddy_link(self, event):
        webbrowser.open("https://linktr.ee/leaddy")

if __name__ == "__main__":
    root = tk.Tk()
    uygulama = EkranIzlemeUygulamasi(root)
    root.mainloop()
