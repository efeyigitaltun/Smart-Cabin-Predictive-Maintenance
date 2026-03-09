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

3. main.py dosyasını açarak kendi ThingSpeak API Key ve Gmail Uygulama Şifrenizi ilgili alanlara girin.
4. Programı başlatın:
   ```bash
   python3 main.py

Sistem Mimarisi:
Sistem verileri sol taraftaki sensör bloğundan toplanır. Analog veriler MCP3008 entegresi aracılığıyla dijital veriye dönüştürülür. Merkezdeki kontrolcü (Pi), AI modelini çalıştırarak durumu analiz eder ve       çıkışları (LED, LCD, Bulut, E-posta) yönetir.

<img width="6067" height="3445" alt="devre şeması" src="https://github.com/user-attachments/assets/e2c85ab2-7bf5-425b-a553-51c0ae177312" />
![uyarımesaj1](https://github.com/user-attachments/assets/affc65f3-9272-4ab7-ac61-3c50c3d1934c)
![uyarılcdscreen](https://github.com/user-attachments/assets/57ce4919-2a79-40bf-a3c1-7261b155f712)
<img width="801" height="799" alt="ThingsSpeakGrafik" src="https://github.com/user-attachments/assets/12a64a11-704c-4d69-b6ed-410513150c84" />
<img width="1382" height="4094" alt="akışdiagram" src="https://github.com/user-attachments/assets/6339350d-53d2-4bc9-91b9-72d480679fd3" />
