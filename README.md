# Smart-Cabin-Predictive-Maintenance
# 🛠️ Akıllı Kabin: IoT ve Yapay Zeka Destekli Kestirimci Bakım Sistemi

Bu proje, sunucu odaları ve endüstriyel kabinler için geliştirilmiş, Raspberry Pi tabanlı bir Kestirimci Bakım (Predictive Maintenance) sistemidir. Ortam ve donanım verilerini toplayarak Makine Öğrenmesi ile olası arızaları önceden tespit eder.

##  Projenin Özellikleri
* Gerçek Zamanlı İzleme: Sıcaklık, nem, hava kalitesi, sistem voltajı, fan devri (RPM) ve akım ölçümü.
* Yapay Zeka (AI) Entegrasyonu: `Random Forest Classifier` algoritması ile sensör verileri analiz edilerek "Normal, Uyarı, Arıza" durumları sınıflandırılır.
* IoT ve Bulut: Toplanan veriler anlık olarak ThingSpeak platformuna gönderilir.
* Acil Durum Bildirimi: Kritik bir eşik aşıldığında veya yapay zeka arıza tespit ettiğinde sistem otomatik E-posta gönderir.
* Donanım Kontrolü: IRF520 MOSFET ile güvenli ve sürekli fan kontrolü, LCD ekran ile yerel veri gösterimi.

## Kullanılan Teknolojiler ve Donanımlar
* Kontrolcü: Raspberry Pi 3 Model B+
* Sensörler: DHT22 (Sıcaklık/Nem), MQ-135 (Hava Kalitesi), ACS712 (Akım), Voltaj Sensörü, Hall Effect (A3144 - RPM)
* ADC Entegresi: MCP3008 (Analog sensörleri okumak için)
* Aktüatörler: 5V Soğutma Fanı, 20x4 I2C LCD Ekran, Uyarı LED'leri
* Yazılım: Python 3, Pandas, Scikit-Learn (Joblib), SQLite3
* Haberleşme/Bulut: I2C, SPI, ThingSpeak API, SMTP (E-posta)

##  Kurulum ve Çalıştırma
1. Bu depoyu bilgisayarınıza/Raspberry Pi'nize klonlayın.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip3 install adafruit-circuitpython-dht adafruit-circuitpython-mcp3xxx RPLCD RPi.GPIO pandas joblib requests
