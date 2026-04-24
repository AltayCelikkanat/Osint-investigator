<div align="center">

<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge"/>

# 🔍 OSINT Investigator

**Open Source Intelligence tool — isim girerek kişi hakkında açık kaynaklardan veri topla.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Roadmap](#-roadmap)

</div>

---

## 🧠 Nedir?

OSINT Investigator, bir kişinin adını girerek sosyal medya profillerini, Google arama sonuçlarını ve konum verilerini otomatik olarak toplayan bir masaüstü aracıdır. Toplanan konum verileri çapraz karşılaştırılarak kimlik tutarlılığı analiz edilir.

> ⚠️ **Yasal Uyarı:** Bu araç yalnızca herkese açık bilgileri toplar. Sadece izinli senaryolarda (kendi araştırma, penetrasyon testi, yetkili kullanım) kullanın.

---

## ✨ Features

| Özellik | Açıklama |
|---|---|
| 🌐 Google Dorking | 5 farklı gelişmiş Google sorgusu |
| 👤 Sosyal Medya Taraması | 12 platform — Twitter/X, Instagram, LinkedIn, GitHub, Reddit, TikTok ve daha fazlası |
| 🔤 Username Varyantları | İsimden otomatik 12+ kullanıcı adı tahmini |
| 📍 Konum Analizi | Farklı kaynaklardaki konum verilerini karşılaştırır, tutarsızlık varsa uyarır |
| 💾 Rapor Dışa Aktarma | JSON + TXT formatında kayıt |
| 🖥️ Modern GUI | Tkinter tabanlı, sekmeli arayüz |
| ⚡ Canlı Log | İşlem adımlarını gerçek zamanlı takip et |

---

## 🚀 Installation

### Yöntem 1 — Direkt Çalıştır (Python gerekli)

```bash
git clone https://github.com/AltayCelikkanat/osint-investigator
cd osint-investigator
pip install -r requirements.txt
python osint_gui.py
```

### Yöntem 2 — Otomatik Kurulum (Windows)

`OSINT_BASLAT.bat` dosyasına çift tıkla — Python yoksa otomatik kurar, sonra programı başlatır.

### Yöntem 3 — .exe Derle

```bash
BUILD_EXE.bat
```
`dist/OSINT_Investigator.exe` oluşur ve masaüstüne kopyalanır.

---

## 🖥️ Usage

1. Uygulamayı başlat
2. **Hedef İsim** alanına tam isim gir (örn. `John Doe`)
3. **▶ TARA** butonuna bas
4. Sekmeleri takip et:
   - 📋 Canlı Log — anlık işlem adımları
   - 👤 Sosyal Medya — bulunan profiller
   - 🌐 Google — dork sonuçları
   - 📍 Konum — tutarlılık analizi
5. **💾 Kaydet** ile JSON/TXT rapor al

---

## 🗺️ Roadmap

- [x] Google Dorking
- [x] 12 platform sosyal medya taraması
- [x] Konum tutarlılık analizi
- [x] JSON + TXT rapor
- [ ] HaveIBeenPwned e-posta sorgulama
- [ ] Shodan IP entegrasyonu
- [ ] Whois domain sorgusu
- [ ] Proxy / VPN desteği
- [ ] PDF rapor export

---

## 🛠️ Tech Stack

- **Python 3.8+**
- `tkinter` — GUI
- `requests` + `beautifulsoup4` — web scraping
- `googlesearch-python` — Google dorking
- `PyInstaller` — .exe derleme

---

## 📄 License

MIT License — özgürce kullan, değiştir, dağıt.

---

<div align="center">
Made with 🔍 by [Altay Çelikkanat](https://github.com/AltayCelikkanat)
</div>
