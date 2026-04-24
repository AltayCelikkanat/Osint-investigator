import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import json
import os
import re
import time
import urllib.parse
from datetime import datetime

# ── Optional imports (graceful fallback) ──────────────────────────────────────
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from googlesearch import search as google_search
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

# ── Social media platforms to check ──────────────────────────────────────────
SOCIAL_PLATFORMS = {
    "Twitter/X":   "https://twitter.com/{}",
    "Instagram":   "https://www.instagram.com/{}",
    "LinkedIn":    "https://www.linkedin.com/in/{}",
    "GitHub":      "https://github.com/{}",
    "Reddit":      "https://www.reddit.com/user/{}",
    "TikTok":      "https://www.tiktok.com/@{}",
    "Pinterest":   "https://www.pinterest.com/{}",
    "Facebook":    "https://www.facebook.com/{}",
    "YouTube":     "https://www.youtube.com/@{}",
    "Twitch":      "https://www.twitch.tv/{}",
    "Medium":      "https://medium.com/@{}",
    "Telegram":    "https://t.me/{}",
}

# ── Location keyword patterns ─────────────────────────────────────────────────
LOCATION_PATTERNS = [
    r'\b(new york|los angeles|chicago|houston|phoenix|philadelphia|san antonio|san diego|dallas|san jose)\b',
    r'\b(london|paris|berlin|tokyo|beijing|sydney|toronto|dubai|singapore|amsterdam)\b',
    r'\b(istanbul|ankara|izmir|bursa|antalya)\b',
    r'\b(united states|usa|u\.s\.a|america|uk|united kingdom|canada|australia|germany|france|turkey|türkiye)\b',
    r'\b([a-z]+,\s*[a-z]{2,})\b',  # "City, Country" pattern
]

def extract_locations(text):
    text_lower = text.lower()
    found = set()
    for pattern in LOCATION_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            found.add(m.strip().title())
    return list(found)

def check_location_consistency(all_locations):
    if len(all_locations) < 2:
        return True, []
    # Group by country/region
    countries = []
    for loc in all_locations:
        l = loc.lower()
        if any(x in l for x in ['usa', 'united states', 'america', 'new york', 'los angeles', 'chicago']):
            countries.append('USA')
        elif any(x in l for x in ['uk', 'united kingdom', 'london']):
            countries.append('UK')
        elif any(x in l for x in ['canada', 'toronto']):
            countries.append('Canada')
        elif any(x in l for x in ['turkey', 'türkiye', 'istanbul', 'ankara', 'izmir']):
            countries.append('Turkey')
        elif any(x in l for x in ['germany', 'berlin']):
            countries.append('Germany')
        elif any(x in l for x in ['australia', 'sydney']):
            countries.append('Australia')
        else:
            countries.append(loc)
    unique = list(set(countries))
    consistent = len(unique) <= 1
    return consistent, unique

def generate_username_variants(name):
    parts = name.lower().split()
    variants = []
    if len(parts) >= 2:
        f, l = parts[0], parts[-1]
        variants += [
            f"{f}{l}", f"{l}{f}", f"{f}.{l}", f"{f}_{l}",
            f"{f[0]}{l}", f"{f}{l[0]}", f"{f}{l}123",
            f"{f}_{l}1", f"_{f}{l}_", f"{l}.{f}",
            f"{f[0]}.{l}", f"{f}-{l}",
        ]
    elif len(parts) == 1:
        n = parts[0]
        variants += [n, f"{n}1", f"{n}123", f"_{n}_", f"{n}_official"]
    return list(set(variants))

def check_social_profile(platform, url_template, username, timeout=6):
    url = url_template.format(username)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if r.status_code == 200 and len(r.text) > 500:
            # Basic false-positive filter
            not_found_signals = ['page not found', 'user not found', 'doesn\'t exist',
                                  'this account doesn\'t exist', 'sorry, this page']
            body_lower = r.text.lower()
            if not any(s in body_lower for s in not_found_signals):
                return True, url
    except Exception:
        pass
    return False, url

def google_dork_search(name, log_fn):
    results = []
    if not HAS_GOOGLE:
        log_fn("  [!] googlesearch-python kurulu değil, Google dorking atlandı.")
        return results
    queries = [
        f'"{name}"',
        f'"{name}" site:linkedin.com',
        f'"{name}" site:twitter.com OR site:x.com',
        f'"{name}" email OR phone OR address',
        f'"{name}" profile OR about',
    ]
    for q in queries:
        try:
            log_fn(f"  🔍 Aranıyor: {q}")
            for url in google_search(q, num_results=5, sleep_interval=2):
                results.append({"query": q, "url": url})
                time.sleep(0.3)
        except Exception as e:
            log_fn(f"  [!] Google hata: {e}")
        time.sleep(1.5)
    return results

# ── Main Search Engine ────────────────────────────────────────────────────────
def run_osint(name, log_fn, progress_fn):
    report = {
        "target": name,
        "timestamp": datetime.now().isoformat(),
        "google_results": [],
        "social_profiles": {},
        "locations_found": [],
        "location_consistency": {},
        "summary": {}
    }
    all_locations = []

    log_fn(f"\n{'═'*55}")
    log_fn(f"  🎯  OSINT ARAŞTIRMASI: {name.upper()}")
    log_fn(f"{'═'*55}\n")

    if not HAS_REQUESTS:
        log_fn("❌ 'requests' kütüphanesi eksik. Lütfen kurun.")
        return report

    # ── PHASE 1: Google Dorking ───────────────────────────────────────────────
    log_fn("📌 PHASE 1 — Google Arama\n")
    progress_fn(10)
    google_res = google_dork_search(name, log_fn)
    report["google_results"] = google_res
    log_fn(f"\n  ✅ {len(google_res)} Google sonucu toplandı.\n")

    # Extract locations from Google results
    for r in google_res:
        locs = extract_locations(r.get("url", ""))
        all_locations.extend(locs)

    # ── PHASE 2: Social Media ─────────────────────────────────────────────────
    log_fn("📌 PHASE 2 — Sosyal Medya Profil Taraması\n")
    progress_fn(30)
    variants = generate_username_variants(name)
    log_fn(f"  🔤 Kullanıcı adı varyantları: {', '.join(variants[:6])}{'...' if len(variants)>6 else ''}\n")

    found_profiles = {}
    total = len(SOCIAL_PLATFORMS) * len(variants[:5])
    done = 0

    for platform, url_tpl in SOCIAL_PLATFORMS.items():
        found_profiles[platform] = []
        for variant in variants[:5]:  # top 5 variants per platform
            found, url = check_social_profile(platform, url_tpl, variant)
            if found:
                log_fn(f"  ✅ [{platform}] BULUNDU → {url}")
                found_profiles[platform].append(url)
            done += 1
            progress_fn(30 + int((done / total) * 40))
            time.sleep(0.2)

    report["social_profiles"] = found_profiles
    total_found = sum(len(v) for v in found_profiles.values())
    log_fn(f"\n  📊 Toplam {total_found} profil tespit edildi.\n")

    # ── PHASE 3: Location Consistency ────────────────────────────────────────
    log_fn("📌 PHASE 3 — Konum Tutarlılık Analizi\n")
    progress_fn(75)

    # Fetch snippets from found profile URLs
    for platform, urls in found_profiles.items():
        for url in urls[:1]:
            try:
                r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()[:2000]
                locs = extract_locations(text)
                if locs:
                    log_fn(f"  📍 [{platform}] Konum işaretleri: {', '.join(locs)}")
                    all_locations.extend(locs)
            except Exception:
                pass

    all_locations = list(set(all_locations))
    report["locations_found"] = all_locations

    consistent, unique_regions = check_location_consistency(all_locations)
    report["location_consistency"] = {
        "consistent": consistent,
        "regions_detected": unique_regions,
        "verdict": "✅ Tutarlı — Muhtemelen aynı kişi" if consistent
                   else f"⚠️ TUTARSIZ — {len(unique_regions)} farklı bölge ({', '.join(unique_regions)}). Farklı kişiler olabilir!"
    }

    log_fn(f"\n  {report['location_consistency']['verdict']}\n")
    log_fn(f"  Tespit edilen konumlar: {', '.join(all_locations) if all_locations else 'Konum bulunamadı'}\n")

    # ── PHASE 4: Summary ──────────────────────────────────────────────────────
    log_fn("📌 PHASE 4 — Özet Rapor\n")
    progress_fn(90)

    report["summary"] = {
        "google_hits": len(google_res),
        "social_profiles_found": total_found,
        "platforms_with_hits": [p for p, v in found_profiles.items() if v],
        "locations": all_locations,
        "identity_consistent": consistent,
    }

    log_fn(f"  🔎 Google sonuçları  : {len(google_res)}")
    log_fn(f"  👤 Sosyal profil     : {total_found}")
    log_fn(f"  🌍 Konum verileri    : {len(all_locations)}")
    log_fn(f"  🧩 Kimlik tutarlılığı: {'✅ Tutarlı' if consistent else '⚠️ Tutarsız'}")
    log_fn(f"\n{'═'*55}\n")

    progress_fn(100)
    return report

# ── GUI ───────────────────────────────────────────────────────────────────────
class OSINTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OSINT Name Investigator")
        self.root.geometry("900x680")
        self.root.configure(bg="#0d1117")
        self.root.resizable(True, True)

        self._report = {}
        self._build_ui()

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg="#0d1117")
        hdr.pack(fill="x", padx=20, pady=(18, 0))

        tk.Label(hdr, text="🔍  OSINT NAME INVESTIGATOR",
                 font=("Consolas", 18, "bold"), fg="#58a6ff", bg="#0d1117").pack(side="left")
        tk.Label(hdr, text="v1.0  —  Open Source Intelligence Tool",
                 font=("Consolas", 9), fg="#484f58", bg="#0d1117").pack(side="left", padx=14, pady=4)

        # ── Input row ─────────────────────────────────────────────────────────
        inp = tk.Frame(self.root, bg="#0d1117")
        inp.pack(fill="x", padx=20, pady=12)

        tk.Label(inp, text="Hedef İsim:", font=("Consolas", 11),
                 fg="#8b949e", bg="#0d1117").pack(side="left")

        self.name_var = tk.StringVar()
        self.entry = tk.Entry(inp, textvariable=self.name_var,
                              font=("Consolas", 12), bg="#161b22", fg="#e6edf3",
                              insertbackground="#58a6ff", relief="flat",
                              highlightthickness=1, highlightbackground="#30363d",
                              highlightcolor="#58a6ff", width=30)
        self.entry.pack(side="left", padx=10, ipady=6)
        self.entry.bind("<Return>", lambda e: self._start_search())

        self.btn_search = tk.Button(inp, text="▶  TARA", font=("Consolas", 11, "bold"),
                                    bg="#238636", fg="white", activebackground="#2ea043",
                                    relief="flat", padx=16, pady=4, cursor="hand2",
                                    command=self._start_search)
        self.btn_search.pack(side="left", padx=6)

        self.btn_save = tk.Button(inp, text="💾  Kaydet", font=("Consolas", 10),
                                  bg="#21262d", fg="#8b949e", activebackground="#30363d",
                                  relief="flat", padx=12, pady=4, cursor="hand2",
                                  command=self._save_report, state="disabled")
        self.btn_save.pack(side="left", padx=4)

        self.btn_clear = tk.Button(inp, text="🗑  Temizle", font=("Consolas", 10),
                                   bg="#21262d", fg="#8b949e", activebackground="#30363d",
                                   relief="flat", padx=12, pady=4, cursor="hand2",
                                   command=self._clear)
        self.btn_clear.pack(side="left", padx=4)

        # ── Progress bar ──────────────────────────────────────────────────────
        prog_frame = tk.Frame(self.root, bg="#0d1117")
        prog_frame.pack(fill="x", padx=20, pady=(0, 4))

        self.progress = ttk.Progressbar(prog_frame, mode="determinate", maximum=100)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TProgressbar", troughcolor="#21262d",
                         background="#238636", thickness=6)
        self.progress.pack(fill="x", ipady=2)

        self.status_var = tk.StringVar(value="Hazır.")
        tk.Label(prog_frame, textvariable=self.status_var,
                 font=("Consolas", 8), fg="#484f58", bg="#0d1117",
                 anchor="w").pack(fill="x")

        # ── Tabs ──────────────────────────────────────────────────────────────
        nb_style = ttk.Style()
        nb_style.configure("Dark.TNotebook", background="#0d1117", borderwidth=0)
        nb_style.configure("Dark.TNotebook.Tab", background="#161b22",
                           foreground="#8b949e", font=("Consolas", 9),
                           padding=[12, 4])
        nb_style.map("Dark.TNotebook.Tab",
                     background=[("selected", "#21262d")],
                     foreground=[("selected", "#58a6ff")])

        self.nb = ttk.Notebook(self.root, style="Dark.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=20, pady=(4, 12))

        # Tab 1 — Log
        log_frame = tk.Frame(self.nb, bg="#0d1117")
        self.nb.add(log_frame, text="  📋 Canlı Log  ")
        self.log_text = scrolledtext.ScrolledText(
            log_frame, font=("Consolas", 10), bg="#0d1117", fg="#e6edf3",
            insertbackground="#58a6ff", relief="flat", state="disabled",
            wrap="word", padx=10, pady=8)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("green",  foreground="#3fb950")
        self.log_text.tag_config("yellow", foreground="#d29922")
        self.log_text.tag_config("red",    foreground="#f85149")
        self.log_text.tag_config("blue",   foreground="#58a6ff")
        self.log_text.tag_config("dim",    foreground="#484f58")

        # Tab 2 — Social
        social_frame = tk.Frame(self.nb, bg="#0d1117")
        self.nb.add(social_frame, text="  👤 Sosyal Medya  ")
        self.social_text = scrolledtext.ScrolledText(
            social_frame, font=("Consolas", 10), bg="#0d1117", fg="#e6edf3",
            relief="flat", state="disabled", wrap="word", padx=10, pady=8)
        self.social_text.pack(fill="both", expand=True)

        # Tab 3 — Google
        google_frame = tk.Frame(self.nb, bg="#0d1117")
        self.nb.add(google_frame, text="  🌐 Google  ")
        self.google_text = scrolledtext.ScrolledText(
            google_frame, font=("Consolas", 10), bg="#0d1117", fg="#e6edf3",
            relief="flat", state="disabled", wrap="word", padx=10, pady=8)
        self.google_text.pack(fill="both", expand=True)

        # Tab 4 — Location
        loc_frame = tk.Frame(self.nb, bg="#0d1117")
        self.nb.add(loc_frame, text="  📍 Konum  ")
        self.loc_text = scrolledtext.ScrolledText(
            loc_frame, font=("Consolas", 10), bg="#0d1117", fg="#e6edf3",
            relief="flat", state="disabled", wrap="word", padx=10, pady=8)
        self.loc_text.pack(fill="both", expand=True)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _log(self, msg):
        self.root.after(0, self._append_log, msg)

    def _append_log(self, msg):
        self.log_text.config(state="normal")
        tag = None
        if "✅" in msg or "BULUNDU" in msg:  tag = "green"
        elif "⚠️" in msg or "[!]" in msg:    tag = "yellow"
        elif "❌" in msg:                     tag = "red"
        elif "PHASE" in msg or "═" in msg:   tag = "blue"
        elif msg.strip().startswith("#") or msg.strip() == "": tag = "dim"
        if tag:
            self.log_text.insert("end", msg + "\n", tag)
        else:
            self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _set_progress(self, v):
        self.root.after(0, lambda: self.progress.config(value=v))
        self.root.after(0, lambda: self.status_var.set(f"İlerleme: %{v}"))

    def _start_search(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Uyarı", "Lütfen bir isim girin.")
            return
        self._clear_results()
        self.btn_search.config(state="disabled")
        self.btn_save.config(state="disabled")
        threading.Thread(target=self._run_thread, args=(name,), daemon=True).start()

    def _run_thread(self, name):
        try:
            self._report = run_osint(name, self._log, self._set_progress)
            self.root.after(0, self._populate_tabs)
            self.root.after(0, lambda: self.btn_save.config(state="normal"))
        except Exception as e:
            self._log(f"❌ Hata: {e}")
        finally:
            self.root.after(0, lambda: self.btn_search.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("Tamamlandı."))

    def _populate_tabs(self):
        r = self._report

        # Social tab
        self.social_text.config(state="normal")
        self.social_text.delete("1.0", "end")
        self.social_text.insert("end", f"Hedef: {r.get('target','')}\n\n")
        profiles = r.get("social_profiles", {})
        for plat, urls in profiles.items():
            if urls:
                self.social_text.insert("end", f"✅  {plat}\n")
                for u in urls:
                    self.social_text.insert("end", f"    → {u}\n")
            else:
                self.social_text.insert("end", f"    {plat}: bulunamadı\n")
        self.social_text.config(state="disabled")

        # Google tab
        self.google_text.config(state="normal")
        self.google_text.delete("1.0", "end")
        google_res = r.get("google_results", [])
        if google_res:
            for item in google_res:
                self.google_text.insert("end", f"🔍 {item['query']}\n    {item['url']}\n\n")
        else:
            self.google_text.insert("end", "Google sonucu bulunamadı veya kütüphane eksik.\n")
        self.google_text.config(state="disabled")

        # Location tab
        self.loc_text.config(state="normal")
        self.loc_text.delete("1.0", "end")
        locs = r.get("locations_found", [])
        consistency = r.get("location_consistency", {})
        self.loc_text.insert("end", f"Tespit edilen konumlar:\n  {', '.join(locs) if locs else 'Yok'}\n\n")
        self.loc_text.insert("end", f"Tutarlılık analizi:\n  {consistency.get('verdict','')}\n\n")
        regions = consistency.get("regions_detected", [])
        if regions:
            self.loc_text.insert("end", f"Tespit edilen bölgeler: {', '.join(regions)}\n")
        self.loc_text.config(state="disabled")

    def _save_report(self):
        if not self._report:
            messagebox.showinfo("Bilgi", "Kaydedilecek rapor yok.")
            return
        name_slug = re.sub(r'\W+', '_', self._report.get("target", "report")).lower()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"osint_{name_slug}_{ts}"

        # Save JSON
        json_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Tümü", "*.*")],
            initialfile=default_name + ".json",
            title="JSON Raporu Kaydet"
        )
        if json_path:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self._report, f, ensure_ascii=False, indent=2)

        # Save TXT
        txt_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("Tümü", "*.*")],
            initialfile=default_name + ".txt",
            title="TXT Raporu Kaydet"
        )
        if txt_path:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"OSINT RAPORU\n{'='*50}\n")
                f.write(f"Hedef : {self._report.get('target')}\n")
                f.write(f"Tarih : {self._report.get('timestamp')}\n\n")
                f.write("SOSYAL MEDYA PROFİLLERİ\n" + "-"*30 + "\n")
                for plat, urls in self._report.get("social_profiles", {}).items():
                    if urls:
                        for u in urls:
                            f.write(f"  [{plat}] {u}\n")
                f.write("\nGOOGLE SONUÇLARI\n" + "-"*30 + "\n")
                for g in self._report.get("google_results", []):
                    f.write(f"  {g['url']}\n")
                f.write("\nKONUM ANALİZİ\n" + "-"*30 + "\n")
                f.write(f"  {self._report.get('location_consistency', {}).get('verdict','')}\n")
                locs = self._report.get("locations_found", [])
                if locs:
                    f.write(f"  Konumlar: {', '.join(locs)}\n")
            messagebox.showinfo("Kaydedildi", f"Raporlar kaydedildi.")

    def _clear_results(self):
        for widget in [self.log_text, self.social_text, self.google_text, self.loc_text]:
            widget.config(state="normal")
            widget.delete("1.0", "end")
            widget.config(state="disabled")
        self.progress.config(value=0)
        self.status_var.set("Tarama başlatılıyor...")

    def _clear(self):
        self._clear_results()
        self.name_var.set("")
        self.status_var.set("Hazır.")
        self._report = {}
        self.btn_save.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = OSINTApp(root)
    root.mainloop()
