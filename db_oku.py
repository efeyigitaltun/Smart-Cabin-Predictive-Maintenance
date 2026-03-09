import sqlite3
import pandas as pd

# Veritabanına bağlan
conn = sqlite3.connect('bakim_verisi.db')
print("--- VERİTABANI İÇERİĞİ (Son 20 Kayıt) ---")

try:
    # Verileri çek ve pandas tablosuna çevir
    df = pd.read_sql_query("SELECT * FROM sensor_log", conn)

    # Son 20 satırı göster(değiştirilebilir)
    print(df.tail(20))
    print(f"\nToplam Kayıt Sayısı: {len(df)}")
except Exception as e:
    print("Tablo okunamadı:", e)

conn.close()
