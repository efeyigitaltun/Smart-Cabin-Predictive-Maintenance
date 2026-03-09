import time
import sqlite3
import board
import busio
import digitalio
import adafruit_dht
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import pandas as pd
import joblib
import warnings
import requests
import smtplib
from email.mime.text import MIMEText

# Gereksiz uyarıları gizle
warnings.filterwarnings("ignore")

# --- 1. KULLANICI AYARLARI (GİZLİ TUTULMALIDIR) ---
THINGSPEAK_URL = "https://api.thingspeak.com/update"
API_KEY = "BURAYA_THINGSPEAK_API_KEY_YAZ" # Kendi API Key'inizi girin
GMAIL_KULLANICI = "gonderen_mail@gmail.com" # Kendi mailinizi girin
GMAIL_SIFRE = "16_haneli_uygulama_sifresi" # Uygulama şifrenizi girin
ALICI_EMAIL = "alici_mail@gmail.com" # Uyarıların gideceği mail

# --- 2. DONANIM AYARLARI ---
# LED ve Buzzer Pinleri (BCM Modu)
LED_YESIL = 5
LED_SARI = 6
LED_KIRMIZI = 13
BUZZER_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_YESIL, GPIO.OUT)
GPIO.setup(LED_SARI, GPIO.OUT)
GPIO.setup(LED_KIRMIZI, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Sensör Tanımlamaları
dht_device = adafruit_dht.DHT22(board.D4)
HALL_PIN = 27
GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# MCP3008 (Analog Okuyucu) Ayarları (SPI)
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D25)
mcp = MCP.MCP3008(spi, cs)

chan_hava = AnalogIn(mcp, MCP.P0)
chan_akim = AnalogIn(mcp, MCP.P1)
chan_volt = AnalogIn(mcp, MCP.P2)

# LCD Ekran Ayarları
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=20, rows=4, dotsize=8)
DB_NAME = 'bakim_verisi.db'

# Yapay Zeka Modelini Yükle
try:
    ai_model = joblib.load('bakim_modeli.pkl')
    print("Yapay Zeka Modeli Yüklendi!")
except:
    print("Model bulunamadı, varsayılan kurallar çalışacak.")
    ai_model = None

# Değişkenler
last_cloud_time = 0
last_email_time = 0
ariza_sayaci = 0
HATA_ESIGI = 3 # Hata 3 döngü devam ederse alarm ver.

# --- 3. FONKSİYONLAR ---
rpm_sayac = 0

def rpm_arttir(channel):
    global rpm_sayac
    rpm_sayac += 1

GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=rpm_arttir)

def get_rpm():
    global rpm_sayac
    rpm_sayac = 0
    time.sleep(0.5)
    return rpm_sayac * 120

def veriyi_kaydet(sicaklik, nem, hava, akim, voltaj, rpm):
    try:
        conn = sqlite3.connect(DB_NAME)
        curs = conn.cursor()
        curs.execute("""
            CREATE TABLE IF NOT EXISTS sensor_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
                sicaklik REAL, nem REAL, hava_kalitesi REAL,
                akim REAL, voltaj REAL, fan_rpm INTEGER
            )
        """)
        curs.execute("""
            INSERT INTO sensor_log (sicaklik, nem, hava_kalitesi, akim, voltaj, fan_rpm)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sicaklik, nem, hava, akim, voltaj, rpm))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

def buluta_gonder(sicaklik, nem, hava, akim, voltaj, rpm, durum_kodu):
    try:
        durum_sayi = 0
        if "UYARI" in durum_kodu: durum_sayi = 1
        if "ARIZA" in durum_kodu: durum_sayi = 2
        payload = {
            "api_key": API_KEY, "field1": sicaklik, "field2": nem, "field3": hava,
            "field4": akim, "field5": voltaj, "field6": rpm, "field7": durum_sayi
        }
        requests.get(THINGSPEAK_URL, params=payload)
    except:
        pass

def email_gonder(hata_listesi):
    try:
        sorunlar = "\n".join(hata_listesi)
        icerik = f"""
ACİL DURUM UYARISI! 
-----------------------
Kestirimci Bakım Sistemi KALICI bir arıza tespit etti.

TESPİT EDİLEN SORUNLAR:
{sorunlar}

Lütfen sistemi kontrol ediniz.
"""
        msg = MIMEText(icerik)
        msg['Subject'] = "KABİN ARIZASI: Müdahale Gerekli'
        msg['From'] = GMAIL_KULLANICI
        msg['To'] = ALICI_EMAIL
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_KULLANICI, GMAIL_SIFRE)
        server.sendmail(GMAIL_KULLANICI, ALICI_EMAIL, msg.as_string())
        server.quit()
        print(f"\n>> 📧 EMAIL GÖNDERİLDİ! ({time.ctime()})\n")
    except Exception as e:
        print(f"!! Email Hatası: {e}")

# --- 4. ANA DÖNGÜ ---
print("--- SİSTEM BAŞLATILDI (Gürültü Filtreli & Buzzer Aktif) ---")

# Başlangıç Testi
GPIO.output(BUZZER_PIN, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(BUZZER_PIN, GPIO.LOW)

lcd.clear()
lcd.write_string("Sistem Aktif")
time.sleep(2)
lcd.clear()

try:
    while True:
        # A. Okuma
        try:
            sicaklik = dht_device.temperature
            nem = dht_device.humidity
        except RuntimeError:
            sicaklik = 0
            nem = 0
        
        if sicaklik is None: sicaklik = 0

        hava_volt = chan_hava.voltage
        akim_volt = chan_akim.voltage
        akim_amper = abs((akim_volt - 2.50) / 0.185)
        sistem_volt = chan_volt.voltage * 5.0
        fan_rpm = get_rpm()

        # B. Karar (Yapay Zeka)
        tahmin = 0
        if ai_model is not None:
            veri = pd.DataFrame([[sicaklik, nem, hava_volt, akim_volt, sistem_volt, fan_rpm]],
                                columns=['sicaklik', 'nem', 'hava', 'akim', 'voltaj', 'rpm'])
            tahmin = ai_model.predict(veri)[0]

        # Temizlik
        GPIO.output(LED_YESIL, GPIO.LOW)
        GPIO.output(LED_SARI, GPIO.LOW)
        GPIO.output(LED_KIRMIZI, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        durum_metni = "NORMAL "

        # C. FİLTRELİ ALARM MANTIĞI
        aktif_hatalar = []

        if tahmin == 1: 
            aktif_hatalar.append("- YAPAY ZEKA: Anormal!")
        if sicaklik > 30: 
            aktif_hatalar.append(f"- YÜKSEK SICAKLIK: {sicaklik:.1f} C")
        if hava_volt > 2.0: 
            aktif_hatalar.append(f"- KÖTÜ HAVA: {hava_volt:.2f} V")
        
        if len(aktif_hatalar) > 0:
            ariza_sayaci += 1
            print(f"!! HATA TESPİT EDİLDİ (Sayaç: {ariza_sayaci}/{HATA_ESIGI})")

            # Anlık hata olsa bile Kırmızı LED yansın
            GPIO.output(LED_KIRMIZI, GPIO.HIGH)
            durum_metni = "ARIZA! "

            # Kalıcı Hata Kontrolü
            if ariza_sayaci >= HATA_ESIGI:
                GPIO.output(BUZZER_PIN, GPIO.HIGH) # Buzzer Öter

                if time.time() - last_email_time > 300:
                    email_gonder(aktif_hatalar)
                    last_email_time = time.time()
        else:
            ariza_sayaci = 0 # Hata yoksa sayacı sıfırla

            # Sarı Alarm Kontrolü (Hafif Uyarı)
            if sicaklik > 27 or hava_volt > 0.8 or fan_rpm < 4000:
                GPIO.output(LED_SARI, GPIO.HIGH)
                durum_metni = "UYARI! "
            else:
                GPIO.output(LED_YESIL, GPIO.HIGH)
                durum_metni = "NORMAL "

        # D. Ekran ve Loglama
        print(f"Isı:{sicaklik:.1f} | Hava:{hava_volt:.2f} | Akım:{akim_amper:.2f} | Durum: {durum_metni}")

        lcd.cursor_pos = (0, 0)
        lcd.write_string(f"Sicak:{sicaklik:.1f}C Nem:{nem:.0f}%")
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"Durum: {durum_metni}")
        
        if sicaklik > 0:
            veriyi_kaydet(sicaklik, nem, hava_volt, akim_amper, sistem_volt, fan_rpm)
        
        if time.time() - last_cloud_time > 60: # 1 Dakikada bir buluta gönder
            buluta_gonder(sicaklik, nem, hava_volt, akim_amper, sistem_volt, fan_rpm, durum_metni)
            last_cloud_time = time.time()

except KeyboardInterrupt:
    print("\nKapatılıyor...")
    GPIO.cleanup()
    lcd.clear()
