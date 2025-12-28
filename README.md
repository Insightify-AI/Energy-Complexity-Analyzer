<p align="center">
  <img src="assets/platforma giriş.png" alt="Algoritma Enerji Analizi Platformu" width="100%"/>
</p>

<div align="center">

# ⚡ Algoritma Enerji Analizi Platformu

### Modern PyQt5 Tabanlı Algoritma Performans ve Enerji Tüketimi Analiz Uygulaması

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/Lisans-MIT-blue?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

**Çeşitli algoritmaların çalışma süresini, bellek kullanımını ve gerçek enerji tüketimini ölçerek karşılaştırmalı analiz yapmanızı sağlayan kapsamlı bir platform.**

[🚀 Kurulum](#-kurulum) • [📖 Kullanım](#-kullanım) • [🧮 Algoritmalar](#-desteklenen-algoritmalar) • [📊 Test Sonuçları](#-test-sonuçları) • [📸 Ekran Görüntüleri](#-ekran-görüntüleri)

</div>

---

## 📋 İçindekiler

<details>
<summary>📑 Tüm Bölümleri Göster</summary>

- [🎯 Proje Hakkında](#-proje-hakkında)
- [✨ Özellikler](#-özellikler)
- [💻 Sistem Gereksinimleri](#-sistem-gereksinimleri)
- [🔧 Kurulum](#-kurulum)
- [📖 Kullanım](#-kullanım)
- [🧮 Desteklenen Algoritmalar](#-desteklenen-algoritmalar)
  - [Böl ve Yönet](#-böl-ve-yönet-divide--conquer)
  - [Dinamik Programlama](#-dinamik-programlama-dynamic-programming)
  - [Açgözlü Algoritmalar](#-açgözlü-algoritmalar-greedy)
- [📊 Test Sonuçları](#-test-sonuçları)
  - [Böl ve Yönet Sonuçları](#böl-ve-yönet-test-sonuçları)
  - [Dinamik Programlama Sonuçları](#dinamik-programlama-test-sonuçları)
  - [Açgözlü Algoritma Sonuçları](#açgözlü-algoritma-test-sonuçları)
- [⚡ Enerji Ölçüm Sistemi](#-enerji-ölçüm-sistemi)
- [📸 Ekran Görüntüleri](#-ekran-görüntüleri)
- [📁 Proje Yapısı](#-proje-yapısı)
- [🛠️ Geliştirici Notları](#️-geliştirici-notları)
- [🐛 Sorun Giderme](#-sorun-giderme)
- [📝 Sürüm Geçmişi](#-sürüm-geçmişi)
- [🤝 Katkıda Bulunma](#-katkıda-bulunma)
- [📄 Lisans](#-lisans)

</details>

---

## 🎯 Proje Hakkında

**Algoritma Enerji Analizi Platformu**, farklı algoritma paradigmalarını (Böl ve Yönet, Dinamik Programlama, Açgözlü) performans ve enerji verimliliği açısından karşılaştırmanıza olanak tanıyan kapsamlı bir analiz aracıdır.

### 🌟 Neden Bu Platform?

Modern yazılım geliştirmede sadece algoritma karmaşıklığı değil, aynı zamanda **enerji verimliliği** de kritik öneme sahiptir. Özellikle:

- 📱 **Mobil cihazlar** için pil ömrü optimizasyonu
- 🌍 **Yeşil bilişim** ve karbon ayak izi azaltma
- 💰 **Bulut maliyetlerini** düşürme
- 🔋 **Gömülü sistemler** için enerji yönetimi

Bu platform, **LibreHardwareMonitor** entegrasyonu sayesinde **gerçek donanım güç tüketimini** ölçerek size en verimli algoritmayı seçmenizde yardımcı olur.

---

## ✨ Özellikler

<p align="center">
  <img src="assets/platform özellikleri.png" alt="Platform Özellikleri" width="80%"/>
</p>

### 🔋 Ana Özellikler

| Özellik | Açıklama |
|---------|----------|
| ⚡ **Gerçek Enerji Ölçümü** | LibreHardwareMonitor ile CPU/GPU güç tüketimi (Watt/Joule) |
| 📊 **Görsel Grafikler** | Matplotlib ile interaktif bar, line ve pie chartlar |
| 🔄 **Çoklu Test** | Aynı anda birden fazla algoritma ve veri boyutu testi |
| 📄 **PDF Raporlama** | Profesyonel analiz raporları oluşturma |
| 💾 **Test Geçmişi** | Tüm test sonuçlarını JSON formatında kaydetme |
| 🎨 **Modern Arayüz** | Karanlık tema, responsive tasarım |

### 🖥️ Arayüz Özellikleri

- 🌙 **Karanlık Tema** - Göz yorgunluğunu azaltan modern tasarım
- 📱 **Responsive Layout** - Farklı ekran boyutlarına uyum
- ⌨️ **Klavye Kısayolları** - F11 tam ekran, ESC çıkış
- 🔔 **Gerçek Zamanlı Log** - İşlem durumu takibi
- 📈 **5 Farklı Grafik Tipi** - Karşılaştırma, ölçekleme, dağılım, veri tablosu, log

---

## 💻 Sistem Gereksinimleri

### Minimum Gereksinimler

| Bileşen | Gereksinim |
|---------|------------|
| **İşletim Sistemi** | Windows 10/11 (64-bit) |
| **Python** | 3.8 veya üzeri |
| **RAM** | 4 GB |
| **Disk Alanı** | 100 MB |
| **Ekran** | 1280x720 minimum |

### Gerçek Enerji Ölçümü İçin (Önerilen)

| Yazılım | Açıklama |
|---------|----------|
| **LibreHardwareMonitor** | [İndir](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases) |
| | ⚠️ Yönetici olarak çalıştırılmalı |
| | ⚠️ Arka planda açık kalmalı |

---

## 🔧 Kurulum

### 1️⃣ Depoyu Klonlayın

```bash
git clone https://github.com/Insightify-AI/Energy-Complexity-Analyzer.git
cd Energy-Complexity-Analyzer
```

### 2️⃣ Sanal Ortam Oluşturun (Önerilen)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

**Veya manuel kurulum:**
```bash
pip install PyQt5>=5.15.0 matplotlib>=3.5.0 wmi pywin32 reportlab
```

### 4️⃣ LibreHardwareMonitor Kurulumu (Opsiyonel)

1. [Resmi GitHub sayfasından](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases) indirin
2. ZIP dosyasını çıkarın
3. `LibreHardwareMonitor.exe` dosyasını **yönetici olarak** çalıştırın
4. Arka planda çalışır durumda bırakın

### 5️⃣ Uygulamayı Başlatın

```bash
python run_app.py
```

---

## 📖 Kullanım

### Uygulamayı Başlatma

```bash
cd python_energy
python run_app.py
```

### 📑 Sayfalar

Uygulama 4 ana sayfadan oluşur:

| Sayfa | Açıklama | Kısayol |
|-------|----------|---------|
| 🏠 **Ana Sayfa** | Dashboard, istatistikler ve hızlı erişim | - |
| ⚡ **Enerji Analizi** | Algoritma seçimi ve test yapılandırması | - |
| 📊 **Karşılaştır** | Önceki testleri karşılaştırma | - |
| 📜 **Geçmiş** | Test geçmişi ve sonuçlar | - |

### 🧪 Test Yapma Adımları

1. **Enerji Analizi** sayfasına gidin
2. **Algoritma türünü** seçin (Böl ve Yönet / Dinamik Programlama / Açgözlü)
3. Test etmek istediğiniz **algoritmaları** işaretleyin
4. **Veri boyutlarını** girin (örn: 100, 500, 1000, 2000)
5. **Tekrar sayısını** belirleyin (güvenilir sonuçlar için 3-5 önerilir)
6. **"Analizi Başlat"** butonuna tıklayın
7. Sonuçları grafik ve tablo olarak görüntüleyin
8. İsterseniz **PDF raporu** oluşturun

### ⌨️ Klavye Kısayolları

| Tuş | İşlev |
|-----|-------|
| `F11` | Tam ekran modu aç/kapat |
| `ESC` | Tam ekran modundan çık |

---

## 🧮 Desteklenen Algoritmalar

<p align="center">
  <img src="assets/desteklenen algoritmalar.png" alt="Desteklenen Algoritmalar" width="80%"/>
</p>

Platform, **3 ana kategori** altında **9 farklı algoritma** desteklemektedir:

---

### 🔀 Böl ve Yönet (Divide & Conquer)

Büyük problemleri küçük alt problemlere bölerek çözen algoritmalar.

#### 1. Merge Sort (Birleştirmeli Sıralama)

<p align="center">
  <img src="assets/böl ve yönet/merge sort.png" alt="Merge Sort" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(n log n) |
| **Alan Karmaşıklığı** | O(n) |
| **Kararlılık** | ✅ Kararlı (Stable) |
| **Yerinde Sıralama** | ❌ Hayır |

**Nasıl Çalışır:**
1. Diziyi ortadan ikiye böl
2. Her iki yarıyı rekürsif olarak sırala
3. Sıralı iki yarıyı birleştir

**Kullanım Alanları:**
- Büyük veri setlerinin sıralanması
- Dış sıralama (external sorting)
- Linked list sıralaması
- Paralel hesaplama

**Avantajları:**
- Her durumda O(n log n) performans
- Kararlı sıralama
- Büyük veriler için ideal

**Dezavantajları:**
- O(n) ekstra bellek gerektirir
- Küçük dizilerde overhead

---

#### 2. Quick Sort (Hızlı Sıralama)

<p align="center">
  <img src="assets/böl ve yönet/quick sort.png" alt="Quick Sort" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(n log n) ortalama, O(n²) en kötü |
| **Alan Karmaşıklığı** | O(log n) |
| **Kararlılık** | ❌ Kararsız (Unstable) |
| **Yerinde Sıralama** | ✅ Evet |

**Nasıl Çalışır:**
1. Bir pivot eleman seç
2. Diziyi pivottan küçük ve büyük olarak ayır (partition)
3. Alt dizileri rekürsif olarak sırala

**Kullanım Alanları:**
- Genel amaçlı sıralama
- Önbellek dostu algoritmalar
- Programlama dillerinin standart kütüphaneleri

**Avantajları:**
- Pratikte en hızlı sıralama algoritması
- Yerinde sıralama (in-place)
- Önbellek dostu

**Dezavantajları:**
- En kötü durumda O(n²)
- Kararsız sıralama

---

#### 3. Strassen Matris Çarpımı

<p align="center">
  <img src="assets/böl ve yönet/strassen matrix.png" alt="Strassen Matrix" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(n^2.81) |
| **Alan Karmaşıklığı** | O(n²) |
| **Geleneksel Çarpım** | O(n³) |
| **İyileştirme** | ~%30 daha hızlı |

**Nasıl Çalışır:**
1. Matrisleri 4 alt matrise böl
2. 7 yardımcı matris hesapla (M1-M7)
3. Sonuç matrisini yardımcı matrislerden oluştur

**Kullanım Alanları:**
- Büyük matris hesaplamaları
- Bilimsel hesaplama
- Makine öğrenmesi
- Grafik işleme

**Avantajları:**
- Standart çarpımdan daha hızlı
- Büyük matrisler için verimli

**Dezavantajları:**
- Küçük matrisler için verimsiz
- Sayısal kararlılık sorunları

---

### 🧩 Dinamik Programlama (Dynamic Programming)

Alt problemlerin çözümlerini saklayarak tekrar hesaplamayı önleyen algoritmalar.

#### 1. 0/1 Knapsack (Sırt Çantası Problemi)

<p align="center">
  <img src="assets/dinamik programlama/knapsack.png" alt="Knapsack" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(n × W) |
| **Alan Karmaşıklığı** | O(n × W) |
| **Problem Tipi** | Optimizasyon |
| **Yaklaşım** | Tabulation (Bottom-Up) |

**Problem Tanımı:**
- n adet eşya, her birinin değeri (v) ve ağırlığı (w) var
- W kapasiteli bir çanta
- Maksimum değeri elde etmek için hangi eşyalar seçilmeli?

**Nasıl Çalışır:**
1. 2D DP tablosu oluştur (n+1) × (W+1)
2. Her hücreyi optimal alt problem çözümüyle doldur
3. K[n][W] maksimum değeri verir

**Kullanım Alanları:**
- Kaynak tahsisi
- Portföy optimizasyonu
- Bütçe planlama
- Kripto para madenciliği

---

#### 2. Floyd-Warshall

<p align="center">
  <img src="assets/dinamik programlama/floyd warshall.png" alt="Floyd Warshall" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(V³) |
| **Alan Karmaşıklığı** | O(V²) |
| **Problem Tipi** | En Kısa Yol |
| **Negatif Ağırlık** | ✅ Destekler |

**Problem Tanımı:**
- Ağırlıklı bir grafta tüm düğüm çiftleri arasındaki en kısa yolları bul

**Nasıl Çalışır:**
1. Mesafe matrisini başlat
2. Her ara düğüm k için tüm i-j çiftlerini kontrol et
3. dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

**Kullanım Alanları:**
- Harita uygulamaları
- Ağ yönlendirme
- Sosyal ağ analizi
- Oyun AI pathfinding

---

#### 3. Bellman-Ford

<p align="center">
  <img src="assets/dinamik programlama/bellman ford.png" alt="Bellman Ford" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(V × E) |
| **Alan Karmaşıklığı** | O(V) |
| **Negatif Ağırlık** | ✅ Destekler |
| **Negatif Döngü** | ✅ Tespit Eder |

**Problem Tanımı:**
- Tek kaynaklı en kısa yol problemi
- Negatif ağırlıklı kenarları destekler

**Nasıl Çalışır:**
1. Mesafeleri sonsuz olarak başlat, kaynak = 0
2. V-1 kez tüm kenarları gevşet (relax)
3. Negatif döngü kontrolü yap

**Kullanım Alanları:**
- Arbitraj tespiti (finans)
- Ağ protokolleri (RIP)
- GPS navigasyon
- Oyun haritaları

---

### 🎯 Açgözlü Algoritmalar (Greedy)

Her adımda lokal olarak en iyi seçimi yapan algoritmalar.

#### 1. Dijkstra

<p align="center">
  <img src="assets/açgözlü algoritmalar/dijkstra.png" alt="Dijkstra" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(V²) veya O((V+E) log V) |
| **Alan Karmaşıklığı** | O(V) |
| **Negatif Ağırlık** | ❌ Desteklemez |
| **Veri Yapısı** | Priority Queue (Heap) |

**Problem Tanımı:**
- Tek kaynaklı en kısa yol
- Pozitif ağırlıklı kenarlar

**Nasıl Çalışır:**
1. Mesafeleri sonsuz olarak başlat, kaynak = 0
2. En küçük mesafeli ziyaret edilmemiş düğümü seç
3. Komşuların mesafelerini güncelle
4. Tüm düğümler ziyaret edilene kadar tekrarla

**Kullanım Alanları:**
- GPS navigasyon
- Ağ yönlendirme (OSPF)
- Robotik pathfinding
- Oyun AI

---

#### 2. Prim's MST (Minimum Yayılan Ağaç)

<p align="center">
  <img src="assets/açgözlü algoritmalar/prim's mst.png" alt="Prim's MST" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(V²) veya O(E log V) |
| **Alan Karmaşıklığı** | O(V) |
| **Çıktı** | Minimum Spanning Tree |
| **Veri Yapısı** | Priority Queue |

**Problem Tanımı:**
- Bağlı, ağırlıklı bir grafın minimum ağırlıklı yayılan ağacını bul

**Nasıl Çalışır:**
1. Rastgele bir düğümden başla
2. MST'ye dahil olmayan en küçük ağırlıklı kenarı ekle
3. Tüm düğümler dahil olana kadar tekrarla

**Kullanım Alanları:**
- Ağ tasarımı (kablo döşeme)
- Kümeleme algoritmaları
- Görüntü segmentasyonu
- Elektrik şebekesi planlaması

---

#### 3. Huffman Coding

<p align="center">
  <img src="assets/açgözlü algoritmalar/huffman coding.png" alt="Huffman Coding" width="70%"/>
</p>

| Özellik | Değer |
|---------|-------|
| **Zaman Karmaşıklığı** | O(n log n) |
| **Alan Karmaşıklığı** | O(n) |
| **Sıkıştırma Tipi** | Kayıpsız (Lossless) |
| **Kod Tipi** | Prefix-free |

**Problem Tanımı:**
- Karakter frekanslarına göre optimal prefix kodları oluştur

**Nasıl Çalışır:**
1. Frekans tablosu oluştur
2. İki en küçük frekansı birleştirerek ağaç oluştur
3. Sol dal = 0, sağ dal = 1 şeklinde kodla

**Kullanım Alanları:**
- Dosya sıkıştırma (ZIP, GZIP)
- Görüntü formatları (JPEG)
- Video sıkıştırma
- Veri iletimi

---

## 📊 Test Sonuçları

> **Test Koşulları:**
> - Dizi Uzunluğu: **500 eleman**
> - Tekrar Sayısı: **3**
> - Platform: Windows 11
> - İşlemci: Intel Core i5-1240P
> - Enerji Ölçümü: LibreHardwareMonitor

<p align="center">
  <img src="assets/enerji analizi.png" alt="Enerji Analizi" width="80%"/>
</p>

---

### Böl ve Yönet Test Sonuçları

<p align="center">
  <img src="assets/tablolar/böl ve yönet.png" alt="Böl ve Yönet Test Sonuçları" width="80%"/>
</p>


**📈 Analiz:**
- **Merge Sort** en düşük enerji tüketimi ve en hızlı çalışma süresi
- **Quick Sort** en az bellek kullanımı ancak en yüksek enerji tüketimi
- **Strassen** matris işlemleri için optimize edilmiş

---

### Dinamik Programlama Test Sonuçları

<p align="center">
  <img src="assets/tablolar/dinamik programlama.png" alt="Dinamik Programlama Test Sonuçları" width="80%"/>
</p>


**📈 Analiz:**
- **Bellman-Ford** en verimli dinamik programlama algoritması
- **Floyd-Warshall** en yüksek zaman ve enerji tüketimi
- **Knapsack** bellek kullanımında en yoğun

---

### Açgözlü Algoritma Test Sonuçları

<p align="center">
  <img src="assets/tablolar/açgözlü algoritmalar.png" alt="Açgözlü Algoritma Test Sonuçları" width="80%"/>
</p>

**📈 Analiz:**
- **Huffman Coding** en verimli açgözlü algoritma
- **Dijkstra** ve **Prim** benzer performans gösteriyor
- Tüm açgözlü algoritmalar düşük bellek kullanımına sahip

---

## ⚡ Enerji Ölçüm Sistemi

Platform **3 farklı enerji ölçüm yöntemi** destekler:

### 1. LibreHardwareMonitor (Önerilen - Gerçek Ölçüm)

```
✅ Gerçek CPU/GPU güç tüketimi (Watt)
✅ Joule cinsinden enerji hesabı
✅ CPU sıcaklığı takibi
✅ Anlık güç okuma
⚠️ LibreHardwareMonitor kurulu ve çalışıyor olmalı
⚠️ Yönetici izni gerekli
```

**Desteklenen Sensörler:**
- CPU Package Power
- CPU Cores Power
- CPU Platform Power
- GPU Power
- Battery Discharge Rate

### 2. Intel Power Gadget

```
✅ Intel işlemciler için RAPL okuma
✅ Yüksek hassasiyetli ölçüm
⚠️ Sadece Intel CPU'lar
⚠️ Ayrı kurulum gerekli
```

### 3. Tahmini Ölçüm (Fallback)

```
✅ Her zaman çalışır
✅ Sabit 25W varsayımı
⚠️ Gerçek değerler değil tahmini
```

### LibreHardwareMonitor Kurulumu

1. [GitHub Releases](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases) sayfasından indirin
2. ZIP dosyasını çıkarın
3. `LibreHardwareMonitor.exe` → Sağ tık → **Yönetici olarak çalıştır**
4. Uygulama arka planda çalışırken Python uygulamasını başlatın

**Doğrulama:**
Test başlattığınızda log'da şunu görmelisiniz:
```
[OK] LibreHardwareMonitor: GERCEK OLCUM AKTIF
```

---

## 📸 Ekran Görüntüleri

### Ana Sayfa (Dashboard)
<p align="center">
  <img src="assets/platforma giriş.png" alt="Ana Sayfa" width="80%"/>
</p>

### Enerji Analizi
<p align="center">
  <img src="assets/enerji analizi.png" alt="Enerji Analizi" width="80%"/>
</p>

### Algoritma Seçimi
<p align="center">
  <img src="assets/desteklenen algoritmalar.png" alt="Algoritmalar" width="80%"/>
</p>

### Sonuç Karşılaştırması
<p align="center">
  <img src="assets/algoritma sonucu karşılaştırması.png" alt="Karşılaştırma" width="80%"/>
</p>

---

## 📁 Proje Yapısı

```
python_energy/
│
├── 📄 run_app.py              # Ana başlatıcı dosya
├── 📄 algorithms.py           # 9 algoritma implementasyonu
├── 📄 energy_meter.py         # Temel enerji ölçüm modülü
├── 📄 real_energy_meter.py    # LibreHardwareMonitor entegrasyonu
├── 📄 real_power_meter.py     # Gerçek güç ölçümü
├── 📄 requirements.txt        # Python bağımlılıkları
├── 📄 README.md               # Bu dosya
├── 📄 LICENSE                 # MIT Lisansı
│
├── 📂 gui/                    # Grafik arayüz modülleri
│   ├── __init__.py
│   ├── main_window.py         # Ana pencere sınıfı
│   ├── styles.py              # Renk ve stil tanımları
│   │
│   └── 📂 pages/              # Sayfa modülleri
│       ├── home.py            # Ana sayfa (Dashboard)
│       ├── real_energy.py     # Enerji analizi sayfası
│       ├── comparison.py      # Karşılaştırma sayfası
│       └── history.py         # Geçmiş sayfası
│
├── 📂 assets/                 # Görseller ve kaynaklar
│   ├── 📂 böl ve yönet/       # Böl-Yönet algoritma görselleri
│   ├── 📂 dinamik programlama/# DP algoritma görselleri
│   └── 📂 açgözlü algoritmalar/# Greedy algoritma görselleri
│
├── 📂 results/                # Test sonuçları (JSON)
│   └── energy_analysis_*.json
│
└── 📂 _archive/               # Arşivlenmiş dosyalar
```

---

## 🛠️ Geliştirici Notları

### Yeni Algoritma Ekleme

`algorithms.py` dosyasına yeni algoritma eklemek için:

```python
def my_algorithm(data: List[int]) -> Tuple[Any, AlgorithmMetrics]:
    """Algoritma açıklaması"""
    metrics = AlgorithmMetrics()
    
    # Algoritma implementasyonu
    for item in data:
        metrics.iterations += 1
        metrics.comparisons += 1
        # ...
    
    return result, metrics
```

Ardından `ALGORITHMS` sözlüğüne ekleyin:

```python
ALGORITHMS = {
    'my_category': {
        'my_algorithm': {
            'func': my_algorithm,
            'name': 'My Algorithm',
            'complexity_time': 'O(n)',
            'complexity_space': 'O(1)',
            'category': 'my_category'
        }
    }
}
```

### Stil Özelleştirme

`gui/styles.py` dosyasından renkleri değiştirin:

```python
class Colors:
    PRIMARY = "#4A9FF5"       # Ana renk
    ACCENT = "#4CC9F0"        # Vurgu rengi  
    BG_DARK = "#0D1B2A"       # Arka plan
    BG_CARD = "#1B2838"       # Kart arka planı
    TEXT_MAIN = "#E0E6ED"     # Ana metin
    SUCCESS = "#10B981"       # Başarı rengi
    DANGER = "#EF4444"        # Hata rengi
```

---

## 🐛 Sorun Giderme

### Sık Karşılaşılan Sorunlar

#### ❌ "ModuleNotFoundError: No module named 'PyQt5'"

```bash
pip install PyQt5
```

#### ❌ LibreHardwareMonitor bağlantı hatası

1. LibreHardwareMonitor'u **yönetici olarak** çalıştırın
2. Uygulamanın arka planda açık olduğundan emin olun
3. Windows Güvenlik Duvarı'nı kontrol edin

#### ❌ "Gerçek ölçüm yok" uyarısı

Log'da `[!] LibreHardwareMonitor: YOK` görüyorsanız:
1. LibreHardwareMonitor'u başlatın
2. Python uygulamasını yeniden başlatın

#### ❌ Bellek hatası (büyük veri setlerinde)

- Daha küçük veri boyutları kullanın (≤2000)
- Aynı anda daha az algoritma test edin
- Python'u 64-bit olarak çalıştırın

#### ❌ Grafik görüntülenmiyor

```bash
pip install matplotlib
```

---

## 📝 Sürüm Geçmişi

| Sürüm | Tarih | Değişiklikler |
|-------|-------|---------------|
| **v2.2.0** | 2025-12-20 | LibreHardwareMonitor gerçek enerji ölçümü |
| **v2.1.0** | 2025-12-15 | Çalıştırma bazlı analiz, PDF raporlama |
| **v2.0.0** | 2025-12-10 | PyQt5 arayüz, görsel grafikler |
| **v1.0.0** | 2025-11-01 | İlk sürüm |

---

## 🤝 Katkıda Bulunma

Katkılarınızı memnuniyetle karşılıyoruz! 

1. Projeyi **fork** edin
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi **commit** edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'i **push** edin (`git push origin feature/YeniOzellik`)
5. **Pull Request** oluşturun

### Katkı Rehberi

- Kod stilini koruyun
- Türkçe yorum ve docstring kullanın
- Test ekleyin
- README'yi güncelleyin

---

## 📄 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için [`LICENSE`](LICENSE) dosyasına bakın.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


---

<div align="center">

## ⭐ Projeyi Beğendiyseniz

Bu projeyi faydalı bulduysanız, **yıldız** vererek destek olabilirsiniz!

[![Star](https://img.shields.io/github/stars/Insightify-AI/python_energy?style=social)](https://github.com/Insightify-AI/python_energy)


---

<p align="center">
  <b>⚡ Algoritma Enerji Analizi Platformu ⚡</b>
  <br>
  <i>Performans ve enerji verimliliği için</i>
  <br><br>
  Made with ❤️ by Insightify AI
</p>

</div>
