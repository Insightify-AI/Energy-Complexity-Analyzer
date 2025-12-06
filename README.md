# ⚡ Algoritma Enerji Analizi Platformu

**Modern PyQt5 Tabanlı Algoritma Performans ve Enerji Tüketimi Analiz Uygulaması**

Bu platform, çeşitli algoritmaların çalışma süresini, bellek kullanımını ve **gerçek enerji tüketimini** ölçerek karşılaştırmalı analiz yapmanızı sağlar.

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Ekran Görüntüleri](#-ekran-görüntüleri)
- [Sistem Gereksinimleri](#-sistem-gereksinimleri)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Desteklenen Algoritmalar](#-desteklenen-algoritmalar)
- [Enerji Ölçüm Yöntemleri](#-enerji-ölçüm-yöntemleri)
- [Proje Yapısı](#-proje-yapısı)
- [Geliştirici Notları](#-geliştirici-notları)
- [Lisans](#-lisans)

---

## 🚀 Özellikler

### Ana Özellikler
- **Gerçek Enerji Ölçümü**: LibreHardwareMonitor ile gerçek CPU/GPU güç tüketimi ölçümü
- **Algoritma Karşılaştırma**: Farklı algoritmaları yan yana karşılaştırma
- **Detaylı Metrikler**: Çalışma süresi, bellek kullanımı ve enerji tüketimi
- **Görsel Grafikler**: Matplotlib ile interaktif performans grafikleri
- **PDF Raporlama**: Analiz sonuçlarını PDF olarak dışa aktarma
- **Test Geçmişi**: Önceki test sonuçlarını kaydetme ve görüntüleme

### Arayüz Özellikleri
- Modern ve karanlık tema tasarımı
- Tam ekran desteği (F11)
- Responsive layout
- Kolay navigasyon

---

## 💻 Sistem Gereksinimleri

### Minimum Gereksinimler
- **İşletim Sistemi**: Windows 10/11 (64-bit)
- **Python**: 3.8 veya üzeri
- **RAM**: 4 GB
- **Disk Alanı**: 100 MB

### Gerçek Enerji Ölçümü İçin (Opsiyonel)
- **LibreHardwareMonitor**: [İndir](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases)
  - Yönetici olarak çalıştırılmalıdır
  - WMI desteği aktif olmalıdır

---

## 🔧 Kurulum

### 1. Depoyu Klonlayın veya İndirin

```bash
git clone https://github.com/your-username/python_energy.git
cd python_energy
```

### 2. Sanal Ortam Oluşturun (Önerilen)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install PyQt5 matplotlib
```

**Tüm Bağımlılıklar (requirements.txt):**
```
PyQt5>=5.15.0
matplotlib>=3.5.0
```

### 4. Uygulamayı Başlatın

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

### Navigasyon

Uygulama 4 ana sayfadan oluşur:

| Sayfa | Açıklama |
|-------|----------|
| 🏠 **Ana Sayfa** | Dashboard ve genel bilgiler |
| ⚡ **Enerji Analizi** | Algoritma seçimi ve enerji tüketimi ölçümü |
| 📊 **Karşılaştır** | Farklı algoritmaları karşılaştırma |
| 📜 **Geçmiş** | Önceki test sonuçlarını görüntüleme |

### Enerji Analizi Yapma

1. **Enerji Analizi** sayfasına gidin
2. Test etmek istediğiniz **algoritmaları** seçin
3. **Veri boyutlarını** belirleyin
4. **Çalıştırma sayısını** ayarlayın (güvenilir sonuçlar için 3-5 önerilir)
5. **"Analiz Başlat"** butonuna tıklayın
6. Sonuçları grafik ve tablo olarak görüntüleyin
7. İsterseniz **PDF raporu** oluşturun

### Klavye Kısayolları

| Tuş | İşlev |
|-----|-------|
| `F11` | Tam ekran modu aç/kapat |
| `ESC` | Tam ekran modundan çık |

---

## 🧮 Desteklenen Algoritmalar

### Böl ve Yönet (Divide & Conquer)
| Algoritma | Zaman Karmaşıklığı | Alan Karmaşıklığı |
|-----------|-------------------|-------------------|
| Merge Sort | O(n log n) | O(n) |
| Quick Sort | O(n log n) | O(log n) |
| Strassen Matrix | O(n^2.81) | O(n²) |

### Dinamik Programlama
| Algoritma | Zaman Karmaşıklığı | Alan Karmaşıklığı |
|-----------|-------------------|-------------------|
| 0/1 Knapsack | O(n*W) | O(n*W) |
| Floyd-Warshall | O(n³) | O(n²) |
| Bellman-Ford | O(V*E) | O(V) |

### Açgözlü (Greedy) Algoritmalar
| Algoritma | Zaman Karmaşıklığı | Alan Karmaşıklığı |
|-----------|-------------------|-------------------|
| Dijkstra | O(V²) | O(V) |
| Prim's MST | O(V²) | O(V) |
| Huffman Coding | O(n log n) | O(n) |

---

## ⚡ Enerji Ölçüm Yöntemleri

Platform 3 farklı enerji ölçüm yöntemi destekler:

### 1. LibreHardwareMonitor (Önerilen - Gerçek Ölçüm)
```
✅ Gerçek CPU/GPU güç tüketimi
✅ Watt ve Joule cinsinden ölçüm
✅ Anlık güç okuma
⚠️ LibreHardwareMonitor kurulu olmalı
⚠️ Yönetici izni gerekli
```

### 2. Intel Power Gadget
```
✅ Intel işlemciler için doğru ölçüm
⚠️ Sadece Intel CPU'lar
⚠️ Ayrı kurulum gerekli
```

### 3. Tahmini Ölçüm (Fallback)
```
✅ Her zaman çalışır
✅ CPU kullanımına dayalı tahmin
⚠️ Gerçek değerler değil tahmini
```

### LibreHardwareMonitor Kurulumu

1. [Resmi siteden](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases) indirin
2. Zip dosyasını çıkarın
3. `LibreHardwareMonitor.exe` dosyasını **yönetici olarak** çalıştırın
4. **Options > Remote Web Server** seçeneğini aktif edin (opsiyonel)
5. Uygulamayı arka planda çalışır durumda bırakın

---

## 📁 Proje Yapısı

```
python_energy/
├── 📄 run_app.py              # Ana başlatıcı dosya
├── 📄 algorithms.py           # Algoritma implementasyonları
├── 📄 energy_meter.py         # Enerji ölçüm modülü
├── 📄 real_power_meter.py     # Gerçek güç ölçümü (LibreHWM)
├── 📄 real_energy_meter.py    # Gerçek enerji ölçümü
├── 📄 run_benchmark.py        # Benchmark çalıştırıcı
├── 📄 run_real_benchmark.py   # Gerçek ölçüm benchmark
├── 📄 measure_for_php.py      # PHP API entegrasyonu
│
├── 📂 gui/                    # Grafik arayüz modülleri
│   ├── __init__.py
│   ├── main_window.py         # Ana pencere
│   ├── styles.py              # Stil tanımlamaları
│   │
│   └── 📂 pages/              # Sayfa modülleri
│       ├── home.py            # Ana sayfa
│       ├── real_energy.py     # Enerji analizi sayfası
│       ├── comparison.py      # Karşılaştırma sayfası
│       └── history.py         # Geçmiş sayfası
│
├── 📂 results/                # Test sonuçları (JSON)
│   ├── energy_analysis_*.json
│   └── energy_summary_*.txt
│
└── 📂 _archive/               # Arşivlenmiş dosyalar
```

---

## 🔬 Teknik Detaylar

### Metrik Açıklamaları

| Metrik | Açıklama | Birim |
|--------|----------|-------|
| Çalışma Süresi | Algoritmanın toplam yürütme süresi | ms (milisaniye) |
| Bellek Kullanımı | İşlem sırasında kullanılan bellek | MB (megabyte) |
| Enerji Tüketimi | Toplam tüketilen enerji | mJ (milijoule) |
| Güç (Watts) | Ortalama güç tüketimi | W (watt) |
| CPU Kullanımı | İşlemci kullanım yüzdesi | % |

### Veri Formatı

Sonuçlar JSON formatında kaydedilir:

```json
{
  "timestamp": "2024-12-06T22:30:04",
  "algorithms": ["merge_sort", "quick_sort"],
  "data_sizes": [1000, 5000, 10000],
  "runs_per_test": 3,
  "results": [
    {
      "algorithm": "merge_sort",
      "data_size": 1000,
      "execution_time_ms": 2.45,
      "energy_joules": 0.0012,
      "memory_mb": 0.85
    }
  ]
}
```

---

## 🛠️ Geliştirici Notları

### Yeni Algoritma Ekleme

`algorithms.py` dosyasına yeni algoritma eklemek için:

```python
def my_algorithm(data: List[int]) -> Tuple[Any, AlgorithmMetrics]:
    metrics = AlgorithmMetrics()
    
    # Algoritmayı uygula ve metrikleri topla
    result = ...
    metrics.comparisons += 1
    metrics.iterations += 1
    
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

`gui/styles.py` dosyasından renk ve stil ayarlarını değiştirebilirsiniz:

```python
class Colors:
    PRIMARY = "#4A9FF5"       # Ana renk
    BG_DARK = "#0D1B2A"       # Arka plan
    TEXT_MAIN = "#E0E6ED"     # Ana metin rengi
    # ...
```

---

## 🐛 Sorun Giderme

### Sık Karşılaşılan Sorunlar

#### "Eksik bağımlılıklar" hatası
```bash
pip install PyQt5 matplotlib
```

#### LibreHardwareMonitor bağlantı hatası
- LibreHardwareMonitor'u **yönetici olarak** çalıştırdığınızdan emin olun
- Uygulamanın arka planda çalıştığını kontrol edin

#### Ölçek/Bulanıklık sorunu
- Windows DPI ayarlarını kontrol edin
- Uygulama otomatik DPI ölçekleme kullanır

#### Bellek hatası (büyük veri setlerinde)
- Daha küçük veri boyutları kullanın
- Aynı anda daha az algoritma test edin

---

## 📊 Örnek Çıktılar

### Konsol Çıktısı
```
==================================================
[*] Algoritma Analizi Platformu
    Python Edition v2.0
==================================================

[OK] Bağımlılıklar kontrol edildi
[...] Uygulama başlatılıyor...

[OK] Uygulama başlatıldı!
[*] Dashboard açıldı.
```

### PDF Rapor
Uygulama, analiz sonuçlarını içeren profesyonel PDF raporları oluşturabilir:
- Algoritma performans grafikleri
- Detaylı metrik tabloları
- Karşılaştırmalı analiz

---

## 📝 Sürüm Geçmişi

| Sürüm | Tarih | Değişiklikler |
|-------|-------|---------------|
| v2.1.0 | 2024-12 | Çalıştırma bazlı analiz, PDF raporlama |
| v2.0.0 | 2024-12 | PyQt5 arayüz, gerçek enerji ölçümü |
| v1.0.0 | 2024-11 | İlk sürüm |

---

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/YeniOzellik`)
5. Pull Request oluşturun

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.


<div align="center">

**⚡ Algoritma Enerji Analizi Platformu ⚡**

*Performans ve enerji verimliliği için*

</div>
