import ccxt, time, os, json, sys, threading, requests
import pandas as pd
import configparser
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

# ===============================
# CONFIG
# ===============================
conf = configparser.ConfigParser()
conf.read("config.txt")

KOIN_LIST = ['BTC/IDR','ETH/IDR','SOL/IDR','BNB/IDR','ADA/IDR']
TIMEFRAME = '1h'
WAIT = 20
RSI_PERIOD = 14
MIN_IDR_WARNING = 50000
REPORT_INTERVAL = 1800  # 30 menit

TG_TOKEN = conf['TELEGRAM']['TOKEN']
TG_CHAT  = conf['TELEGRAM']['CHAT_ID']

BOT_ID = f"{os.environ.get('COMPUTERNAME','BOT')}-{int(time.time()%10000)}"

ONLINE_FILE = "online.json"
ONLINE_TIMEOUT = 90

# ===============================
# AUTO CREATE FILES
# ===============================
for f in ["positions.json","online.json"]:
    if not os.path.exists(f):
        json.dump({}, open(f,"w"))

# ===============================
# EXCHANGE
# ===============================
ex = ccxt.indodax({
    'apiKey': conf['SETTING']['API_KEY'],
    'secret': conf['SETTING']['SECRET_KEY'],
    'enableRateLimit': True
})

# ===============================
# UTIL
# ===============================
def load_pos(): return json.load(open("positions.json"))
def save_pos(p): json.dump(p, open("positions.json","w"), indent=2)
def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0).rolling(period).mean()
    down = -delta.clip(upper=0).rolling(period).mean()
    return 100 - (100 / (1 + up/(down+1e-9)))
def ema(series, span): return series.ewm(span=span, adjust=False).mean()
def bar(val, maxv=100, length=16, char="█"):
    val = max(0, min(val, maxv))
    fill = int(length * val / maxv)
    return char*fill + "░"*(length-fill)

def tg_send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id":TG_CHAT,"text":msg,"parse_mode":"HTML"}, timeout=5)
    except: pass

def update_online():
    now = int(time.time())
    data = {}
    if os.path.exists(ONLINE_FILE):
        try: data = json.load(open(ONLINE_FILE))
        except: data = {}
    data[BOT_ID] = now
    json.dump(data, open(ONLINE_FILE,"w"))
    online = {k:v for k,v in data.items() if now-v < ONLINE_TIMEOUT}
    return len(online)

# ===============================
# ANALYSIS + AUTO TRADE
# ===============================
def analyze(sym, bal, pos):
    base = sym.split('/')[0]
    ohlcv = ex.fetch_ohlcv(sym, TIMEFRAME, limit=50)
    df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])
    harga = df['c'].iloc[-1]

    r = rsi(df['c'], RSI_PERIOD).iloc[-1]
    trend_up = ema(df['c'],20).iloc[-1] > ema(df['c'],50).iloc[-1]
    heat = (df['h'].iloc[-1]-df['l'].iloc[-1])/harga*100

    free = bal.get(base,{}).get('free',0)
    nilai = free * harga

    aksi = "WAIT"
    if base not in pos:
        if r < 35 and trend_up and heat < 1.5 and bal['IDR']['free'] > MIN_IDR_WARNING:
            amount = round((bal['IDR']['free']*0.1)/harga,6)
            ex.create_market_buy_order(sym, amount)
            pos[base] = {"entry": harga,"amount":amount,"time":time.strftime("%Y-%m-%d %H:%M")}
            save_pos(pos)
            aksi = Fore.GREEN + "BUY"
    else:
        entry = pos[base]['entry']
        pnl = (harga-entry)/entry*100
        if r > 70 or pnl >= 2 or pnl <= -1 or not trend_up:
            ex.create_market_sell_order(sym, pos[base]['amount'])
            del pos[base]
            save_pos(pos)
            aksi = Fore.RED + "SELL"
        else:
            aksi = Fore.CYAN + "HOLD"

    return harga,r,trend_up,heat,free,aksi,nilai

# ===============================
# DASHBOARD TERMINAL
# ===============================
def dashboard():
    os.system('cls' if os.name=='nt' else 'clear')
    bal = ex.fetch_balance()
    pos = load_pos()
    online_count = update_online()

    total_aset = 0
    modal = bal.get('IDR',{}).get('total',0)

    print(Fore.CYAN + f"⚡ INDODAX DASHBOARD | {TIMEFRAME} | {time.strftime('%H:%M:%S')} | BOT {BOT_ID}")
    print(Fore.BLUE + "="*120)
    print(f"{'KOIN':8} | {'HARGA':12} | {'RSI':22} | {'TREND':5} | {'HEAT%':6} | {'SIN':6} | {'JUMLAH':>10}")
    print(Fore.BLUE + "-"*120)

    for k in KOIN_LIST:
        harga,r,trend,heat,free,aksi,nilai = analyze(k, bal, pos)
        total_aset += nilai
        w_rsi = Fore.GREEN if r<40 else Fore.RED if r>70 else Fore.YELLOW
        w_trend = Fore.GREEN if trend else Fore.RED
        w_heat = Fore.GREEN if heat<1 else Fore.YELLOW if heat<1.5 else Fore.RED

        print(f"{k:8} | {harga:12,.0f} | {w_rsi}{r:5.1f} {bar(r)}{Style.RESET_ALL} | "
              f"{w_trend}{'UP ' if trend else 'DOWN'}{Style.RESET_ALL} | "
              f"{w_heat}{heat:5.2f}%{Style.RESET_ALL} | {aksi:6} | {free:10.4f}")

    ekuitas = modal + total_aset
    pnl = (ekuitas-modal)/modal*100 if modal>0 else 0
    warn = f"⚠️ IDR RENDAH ({bal['IDR']['free']:,.0f})" if bal['IDR']['free']<MIN_IDR_WARNING else None

    print(Fore.BLUE + "="*120)
    print(f"ONLINE BOT : {online_count}")
    print(f"MODAL {modal:>12,.0f} | EKUITAS {ekuitas:>12,.0f} | PNL {Fore.GREEN if pnl>=0 else Fore.RED}{pnl:+.2f}%")
    if warn: print(Fore.YELLOW + warn)
    print(Fore.BLUE + "="*120)

# ===============================
# TELEGRAM REPORT OTOMATIS 30 MENIT
# ===============================
def telegram_report():
    while True:
        try:
            bal = ex.fetch_balance()
            pos = load_pos()
            total = bal.get('IDR',{}).get('total',0)
            aset = []
            for k in KOIN_LIST:
                base = k.split('/')[0]
                free = bal.get(base,{}).get('free',0)
                if free>0:
                    ohlcv = ex.fetch_ohlcv(k, TIMEFRAME, limit=1)
                    harga = ohlcv[-1][4]
                    nilai = free*harga
                    total += nilai
                    aset.append(f"• {base}: {free:.4f} ≈ {nilai:,.0f} IDR")
            msg = (f"📊 <b>LAPORAN BOT INDODAX</b>\n\n"
                   f"🆔 Bot ID: {BOT_ID}\n"
                   f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                   f"💼 <b>Aset</b>\n{chr(10).join(aset) if aset else '-'}\n\n"
                   f"💰 Total Ekuitas: <b>{total:,.0f} IDR</b>")
            tg_send(msg)
        except: pass
        time.sleep(REPORT_INTERVAL)

# ===============================
# TELEGRAM COMMANDS (/status /stop /start /dry /report)
# ===============================
DRY_RUN = False
BOT_RUNNING = True

def telegram_listener():
    global DRY_RUN, BOT_RUNNING
    last_update = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates?offset={last_update+1}"
            resp = requests.get(url, timeout=5).json()
            for result in resp.get('result',[]):
                update_id = result['update_id']
                msg_text = result['message']['text']
                chat_id = result['message']['chat']['id']
                last_update = update_id

                if msg_text.lower() == '/status':
                    tg_send(f"Bot {BOT_ID} running. DRY_RUN={DRY_RUN}")
                elif msg_text.lower() == '/stop':
                    BOT_RUNNING = False
                    tg_send("Bot stopped.")
                elif msg_text.lower() == '/start':
                    BOT_RUNNING = True
                    tg_send("Bot started.")
                elif msg_text.lower() == '/dry':
                    DRY_RUN = not DRY_RUN
                    tg_send(f"DRY_RUN mode set to {DRY_RUN}")
                elif msg_text.lower() == '/report':
                    bal = ex.fetch_balance()
                    pos = load_pos()
                    total = bal.get('IDR',{}).get('total',0)
                    aset = []
                    for k in KOIN_LIST:
                        base = k.split('/')[0]
                        free = bal.get(base,{}).get('free',0)
                        if free>0:
                            ohlcv = ex.fetch_ohlcv(k, TIMEFRAME, limit=1)
                            harga = ohlcv[-1][4]
                            nilai = free*harga
                            total += nilai
                            aset.append(f"• {base}: {free:.4f} ≈ {nilai:,.0f} IDR")
                    ekuitas = total
                    msg = (
                        f"📊 <b>LAPORAN BOT INDODAX</b>\n\n"
                        f"🆔 Bot ID: {BOT_ID}\n"
                        f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"💼 <b>Aset</b>\n{chr(10).join(aset) if aset else '-'}\n\n"
                        f"💰 Total Ekuitas: <b>{ekuitas:,.0f} IDR</b>\n"
                        f"DRY_RUN: {DRY_RUN}\n"
                        f"BOT_RUNNING: {BOT_RUNNING}"
                    )
                    tg_send(msg)
        except: pass
        time.sleep(3)

# ===============================
# MAIN LOOP
# ===============================
print(Fore.GREEN + "✅ BOT STARTED (FULL AUTO + DASHBOARD + TELEGRAM)")
threading.Thread(target=telegram_report, daemon=True).start()
threading.Thread(target=telegram_listener, daemon=True).start()

while True:
    try:
        if BOT_RUNNING: dashboard()
        for i in range(WAIT,0,-1):
            done = int(((WAIT-i)/WAIT)*100)
            sys.stdout.write(f"\rNext Update {bar(done,100,30,'■')} {done}% ({i}s)")
            sys.stdout.flush()
            time.sleep(1)
        print()
    except Exception as e:
        print(Fore.RED + f"ERROR: {e}")
        time.sleep(5)
