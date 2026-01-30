# IndodaxBotNinja
“IndodaxBotNinja: Robot trading Indodax full-auto dengan dashboard, Telegram report, dan strategi RSI+EMA.”

IndodaxBotNinja




Robot Trading Otomatis Indodax dengan Dashboard Terminal & Laporan Telegram

Deskripsi

IndodaxBotNinja adalah bot trading otomatis untuk Indodax yang menggunakan strategi RSI, EMA, dan Heat untuk menentukan buy/sell. Bot menampilkan dashboard terminal real-time, mengirim laporan otomatis melalui Telegram, dan dapat dikontrol menggunakan perintah Telegram.

Dirancang untuk trader pemula hingga mahir yang ingin otomatisasi trading di Indodax dengan aman dan mudah.

Fitur Utama

Analisis pasar otomatis menggunakan RSI & EMA trend

Eksekusi buy/sell otomatis dengan manajemen risiko

Dashboard terminal real-time dengan status koin, modal, dan PNL

Laporan Telegram otomatis setiap 30 menit

Kontrol bot via Telegram:

/status → Cek status bot

/stop → Hentikan trading

/start → Mulai trading

/dry → Toggle mode simulasi (DRY_RUN)

/report → Laporan manual

Tracking bot online & offline

Mode DRY_RUN untuk simulasi tanpa risiko dana nyata

Persyaratan

Python 3.11+

Library Python:

ccxt, pandas, colorama, configparser, requests


File config.txt berisi:

[SETTING]
API_KEY=your_api_key
SECRET_KEY=your_secret_key

[TELEGRAM]
TOKEN=your_telegram_bot_token
CHAT_ID=your_chat_id

Cara Install & Jalankan

Clone repository:

git clone https://github.com/username/IndodaxBotNinja.git
cd IndodaxBotNinja


Install library Python:

python -m pip install -r requirements.txt


Isi file config.txt dengan API Key Indodax dan Telegram Token

Jalankan bot:

python bot_indodax.py

Mode DRY_RUN (Simulasi)

Gunakan mode DRY_RUN untuk menjalankan bot tanpa mengeksekusi order nyata. Ini berguna untuk uji strategi sebelum trading dengan dana nyata.



Screenshot Dashboard (Contoh)
⚡ INDODAX DASHBOARD | 1h | 12:34:56 | BOT BOT-1234
========================================================================================================================
KOIN     | HARGA        | RSI                     | TREND | HEAT%  | SIN    | JUMLAH    
------------------------------------------------------------------------------------------------------------------------
BTC/IDR  | 450,000,000  | 45.2 ██████░░░░░░░░░   | UP    | 0.95%  | HOLD   | 0.0021    
ETH/IDR  | 30,000,000   | 38.5 █████░░░░░░░░░░   | DOWN  | 1.20%  | BUY    | 0.0500    
...
========================================================================================================================
ONLINE BOT : 1
MODAL 1,000,000 | EKUITAS 1,050,000 | PNL +5.00%



Contoh Laporan Telegram
📊 LAPORAN BOT INDODAX

🆔 Bot ID: BOT-1234
🕒 2026-01-30 12:30:00

💼 Aset
• BTC: 0.0021 ≈ 945,000 IDR
• ETH: 0.05 ≈ 1,500,000 IDR

💰 Total Ekuitas: 2,445,000 IDR
DRY_RUN: False
BOT_RUNNING: True

Catatan

Pastikan saldo IDR cukup sebelum trading.

Gunakan mode DRY_RUN=True untuk simulasi.

Bot ini untuk edukasi & otomasi trading; gunakan dengan risiko Anda sendiri.
