"""
GERÇEK ENERJİ ÖLÇÜMÜ - LibreHardwareMonitor ile
================================================
Bu modül LibreHardwareMonitor'un WMI arayüzünü kullanarak
GERÇEK CPU/GPU güç tüketimini ölçer.

GEREKSİNİMLER:
1. LibreHardwareMonitor yüklü ve çalışır durumda olmalı
2. Yönetici olarak çalıştırılmalı
3. Python paketleri: pip install wmi pywin32

KULLANIM:
    from real_power_meter import RealPowerMeter, measure_energy
    
    meter = RealPowerMeter()
    result = meter.measure_function(my_function, args)
    print(f"Gerçek Enerji: {result['energy_joules']} J")
"""

import sys
import time
import json
import threading
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass 
class PowerReading:
    """Anlık güç okuması"""
    timestamp: float
    cpu_package: float      # CPU Package Power (W)
    cpu_cores: float        # CPU Cores Power (W)
    cpu_platform: float     # CPU Platform Power (W)
    cpu_memory: float       # CPU Memory Power (W)
    gpu_power: float        # GPU Power (W)
    total_power: float      # Toplam hesaplanan güç


@dataclass
class EnergyMeasurement:
    """Enerji ölçüm sonucu"""
    algorithm: str
    data_size: int
    
    # Zaman bilgileri
    execution_time_ms: float
    sample_count: int
    sampling_interval_ms: float
    
    # GERÇEK ENERJİ DEĞERLERİ
    energy_joules: float            # Toplam enerji (J)
    cpu_package_energy: float       # CPU Package enerji (J) 
    cpu_cores_energy: float         # CPU Cores enerji (J)
    gpu_energy: float               # GPU enerji (J)
    
    # GÜÇ İSTATİSTİKLERİ
    avg_power_watts: float          # Ortalama güç (W)
    max_power_watts: float          # Maksimum güç (W)
    min_power_watts: float          # Minimum güç (W)
    
    # Meta bilgiler
    measurement_source: str
    is_real_measurement: bool
    timestamp: str
    success: bool
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class RealPowerMeter:
    """
    LibreHardwareMonitor kullanarak GERÇEK güç ölçümü yapan sınıf
    """
    
    def __init__(self, sampling_interval_ms: int = 100):
        """
        Args:
            sampling_interval_ms: Örnekleme aralığı (milisaniye)
        """
        self.sampling_interval_ms = sampling_interval_ms
        self.wmi_connection = None
        self._available = False
        self._error_message = ""
        
        self._connect()
    
    def _connect(self):
        """WMI bağlantısını kur"""
        try:
            import wmi
            
            # Önce LibreHardwareMonitor dene
            try:
                self.wmi_connection = wmi.WMI(namespace="root\\LibreHardwareMonitor")
                self._namespace = "LibreHardwareMonitor"
            except:
                # OpenHardwareMonitor dene
                try:
                    self.wmi_connection = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    self._namespace = "OpenHardwareMonitor"
                except:
                    self._error_message = "LibreHardwareMonitor veya OpenHardwareMonitor bulunamadı"
                    return
            
            # Sensörleri kontrol et
            sensors = list(self.wmi_connection.Sensor())
            if len(sensors) == 0:
                self._error_message = "Sensör bulunamadı. Uygulama çalışıyor mu?"
                return
            
            # Power sensörü var mı kontrol et
            power_sensors = [s for s in sensors if s.SensorType == 'Power']
            if len(power_sensors) == 0:
                self._error_message = "Power sensörü bulunamadı"
                return
            
            self._available = True
            # Debug mesajı kaldırıldı - JSON çıktısını bozuyordu
            
        except ImportError:
            self._error_message = "WMI modülü yüklü değil: pip install wmi pywin32"
        except Exception as e:
            self._error_message = f"Bağlantı hatası: {str(e)}"
    
    def is_available(self) -> bool:
        """Gerçek ölçüm kullanılabilir mi?"""
        return self._available
    
    def get_error(self) -> str:
        """Hata mesajını döndür"""
        return self._error_message
    
    def read_power(self) -> PowerReading:
        """Anlık güç değerlerini oku"""
        if not self._available:
            return PowerReading(
                timestamp=time.time(),
                cpu_package=0, cpu_cores=0, cpu_platform=0,
                cpu_memory=0, gpu_power=0, total_power=0
            )
        
        sensors = self.wmi_connection.Sensor()
        
        reading = PowerReading(
            timestamp=time.time(),
            cpu_package=0,
            cpu_cores=0,
            cpu_platform=0,
            cpu_memory=0,
            gpu_power=0,
            total_power=0
        )
        
        for sensor in sensors:
            if sensor.SensorType != 'Power':
                continue
                
            name = sensor.Name.lower()
            value = float(sensor.Value) if sensor.Value else 0
            
            if 'cpu package' in name:
                reading.cpu_package = value
            elif 'cpu cores' in name:
                reading.cpu_cores = value
            elif 'cpu platform' in name:
                reading.cpu_platform = value
            elif 'cpu memory' in name:
                reading.cpu_memory = value
            elif 'gpu' in name and 'power' in name:
                reading.gpu_power = value
        
        # Toplam güç hesapla (CPU Package en güvenilir)
        reading.total_power = reading.cpu_package if reading.cpu_package > 0 else reading.cpu_cores
        
        return reading
    
    def measure_function(self, func: Callable, *args, 
                         algorithm_name: str = "unknown",
                         data_size: int = 0,
                         **kwargs) -> EnergyMeasurement:
        """
        Bir fonksiyonun enerji tüketimini GERÇEK olarak ölç
        
        Args:
            func: Ölçülecek fonksiyon
            algorithm_name: Algoritma adı
            data_size: Veri boyutu
        """
        if not self._available:
            return self._create_error_result(algorithm_name, data_size, self._error_message)
        
        # Örnekleme için değişkenler
        power_samples: List[PowerReading] = []
        sampling_active = True
        
        def sample_power():
            """Arka planda güç örneklemesi yap"""
            while sampling_active:
                reading = self.read_power()
                power_samples.append(reading)
                time.sleep(self.sampling_interval_ms / 1000)
        
        # Örnekleme thread'ini başlat
        sampler_thread = threading.Thread(target=sample_power, daemon=True)
        sampler_thread.start()
        
        # ===== FONKSİYONU ÇALIŞTIR =====
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            sampling_active = False
            return self._create_error_result(algorithm_name, data_size, f"Fonksiyon hatası: {e}")
        
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        # ================================
        
        # Örneklemeyi durdur
        sampling_active = False
        sampler_thread.join(timeout=0.5)
        
        # Örnekleri analiz et
        if len(power_samples) == 0:
            # Çok kısa çalışma - tek örnek al
            power_samples.append(self.read_power())
        
        # Enerji hesapla (Power × Time)
        execution_time_s = execution_time_ms / 1000
        sample_interval_s = self.sampling_interval_ms / 1000
        
        # Her örnek için enerji (J = W × s)
        total_energy = 0
        cpu_package_energy = 0
        cpu_cores_energy = 0
        gpu_energy = 0
        
        power_values = []
        
        for sample in power_samples:
            # Her örneğin enerjisi
            sample_energy = sample.total_power * sample_interval_s
            total_energy += sample_energy
            cpu_package_energy += sample.cpu_package * sample_interval_s
            cpu_cores_energy += sample.cpu_cores * sample_interval_s
            gpu_energy += sample.gpu_power * sample_interval_s
            power_values.append(sample.total_power)
        
        # Gerçek çalışma süresine göre normalize et
        actual_sample_time = len(power_samples) * sample_interval_s
        if actual_sample_time > 0:
            scale_factor = execution_time_s / actual_sample_time
            total_energy *= scale_factor
            cpu_package_energy *= scale_factor
            cpu_cores_energy *= scale_factor
            gpu_energy *= scale_factor
        
        # Güç istatistikleri
        avg_power = sum(power_values) / len(power_values) if power_values else 0
        max_power = max(power_values) if power_values else 0
        min_power = min(power_values) if power_values else 0
        
        return EnergyMeasurement(
            algorithm=algorithm_name,
            data_size=data_size,
            execution_time_ms=execution_time_ms,
            sample_count=len(power_samples),
            sampling_interval_ms=self.sampling_interval_ms,
            energy_joules=total_energy,
            cpu_package_energy=cpu_package_energy,
            cpu_cores_energy=cpu_cores_energy,
            gpu_energy=gpu_energy,
            avg_power_watts=avg_power,
            max_power_watts=max_power,
            min_power_watts=min_power,
            measurement_source=f"{self._namespace}_WMI",
            is_real_measurement=True,
            timestamp=datetime.now().isoformat(),
            success=True
        )
    
    def _create_error_result(self, algorithm: str, data_size: int, error: str) -> EnergyMeasurement:
        return EnergyMeasurement(
            algorithm=algorithm,
            data_size=data_size,
            execution_time_ms=0,
            sample_count=0,
            sampling_interval_ms=0,
            energy_joules=0,
            cpu_package_energy=0,
            cpu_cores_energy=0,
            gpu_energy=0,
            avg_power_watts=0,
            max_power_watts=0,
            min_power_watts=0,
            measurement_source="error",
            is_real_measurement=False,
            timestamp=datetime.now().isoformat(),
            success=False,
            error_message=error
        )


def measure_energy(func: Callable, *args, 
                   algorithm_name: str = "unknown",
                   data_size: int = 0,
                   **kwargs) -> EnergyMeasurement:
    """
    Kolay kullanım için wrapper fonksiyon
    """
    meter = RealPowerMeter()
    return meter.measure_function(func, *args, 
                                   algorithm_name=algorithm_name,
                                   data_size=data_size,
                                   **kwargs)


def demo():
    """Demo"""
    print("="*70)
    print(" 🔋 GERÇEK ENERJİ ÖLÇÜMÜ - DEMO")
    print("="*70)
    
    meter = RealPowerMeter(sampling_interval_ms=50)
    
    if not meter.is_available():
        print(f"\n❌ Hata: {meter.get_error()}")
        print("\n📝 Çözüm:")
        print("   1. LibreHardwareMonitor'u başlatın")
        print("   2. Yönetici olarak çalıştırın")
        print("   3. Bu scripti tekrar çalıştırın")
        return
    
    # Anlık güç okuması
    print("\n📊 Anlık Güç Değerleri:")
    reading = meter.read_power()
    print(f"   CPU Package: {reading.cpu_package:.2f} W")
    print(f"   CPU Cores: {reading.cpu_cores:.2f} W")
    print(f"   GPU Power: {reading.gpu_power:.2f} W")
    
    # Test fonksiyonu
    print("\n⏳ Test hesaplaması çalıştırılıyor...")
    
    def heavy_calculation():
        result = 0
        for i in range(5000000):
            result += i * i % 12345
        return result
    
    result = meter.measure_function(
        heavy_calculation,
        algorithm_name="heavy_calculation",
        data_size=5000000
    )
    
    print("\n" + "="*70)
    print(" 📊 ÖLÇÜM SONUÇLARI")
    print("="*70)
    print(f"\n   ✅ Gerçek Ölçüm: {result.is_real_measurement}")
    print(f"   📍 Kaynak: {result.measurement_source}")
    print(f"\n   ⏱️  Çalışma Süresi: {result.execution_time_ms:.2f} ms")
    print(f"   📈 Örnek Sayısı: {result.sample_count}")
    print(f"\n   ⚡ ENERJİ:")
    print(f"      Toplam: {result.energy_joules:.6f} Joule")
    print(f"      CPU Package: {result.cpu_package_energy:.6f} J")
    print(f"      CPU Cores: {result.cpu_cores_energy:.6f} J")
    print(f"      GPU: {result.gpu_energy:.6f} J")
    print(f"\n   🔌 GÜÇ:")
    print(f"      Ortalama: {result.avg_power_watts:.2f} W")
    print(f"      Maksimum: {result.max_power_watts:.2f} W")
    print(f"      Minimum: {result.min_power_watts:.2f} W")
    print("\n" + "="*70)


if __name__ == '__main__':
    demo()
