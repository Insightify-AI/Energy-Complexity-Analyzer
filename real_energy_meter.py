"""
GERÇEK ENERJİ ÖLÇÜM MODÜLÜ
===========================
Bu modül Windows'ta Intel Power Gadget kullanarak GERÇEK enerji ölçümü yapar.

KURULUM GEREKSİNİMLERİ:
1. Intel Power Gadget: 
   https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html

2. Python paketleri:
   pip install psutil wmi pywin32

KULLANIM:
    from real_energy_meter import RealEnergyMeter
    
    meter = RealEnergyMeter()
    if meter.is_available():
        result = meter.measure(my_function, args)
        print(f"Gerçek Enerji: {result['energy_joules']} J")
"""

import os
import sys
import time
import json
import subprocess
import csv
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import ctypes


@dataclass
class RealEnergyResult:
    """Gerçek enerji ölçüm sonucu"""
    algorithm: str
    data_size: int
    execution_time_ms: float
    
    # GERÇEK ÖLÇÜMLER (Intel Power Gadget'tan)
    energy_joules: float           # Toplam enerji (Joule)
    avg_power_watts: float         # Ortalama güç (Watt)
    max_power_watts: float         # Maksimum güç (Watt)
    min_power_watts: float         # Minimum güç (Watt)
    
    # CPU bilgileri
    cpu_frequency_mhz: float       # CPU frekansı
    cpu_temperature_c: float       # CPU sıcaklığı
    cpu_utilization: float         # CPU kullanımı %
    
    # Ölçüm meta bilgileri
    measurement_source: str        # 'intel_power_gadget', 'wmi', 'estimation'
    is_real_measurement: bool      # Gerçek ölçüm mü?
    sample_count: int              # Kaç örnek alındı
    sampling_interval_ms: float    # Örnekleme aralığı
    
    timestamp: str
    success: bool
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IntelPowerGadgetMeter:
    """
    Intel Power Gadget ile GERÇEK enerji ölçümü
    
    Intel Power Gadget, CPU'nun dahili RAPL (Running Average Power Limit)
    sayaçlarını okuyarak GERÇEK enerji tüketimini ölçer.
    """
    
    POSSIBLE_PATHS = [
        r"C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe",
        r"C:\Program Files\Intel\Power Gadget 3.5\PowerLog3.0.exe",
        r"C:\Program Files (x86)\Intel\Power Gadget 3.6\PowerLog3.0.exe",
        r"C:\Program Files (x86)\Intel\Power Gadget 3.5\PowerLog3.0.exe",
    ]
    
    def __init__(self):
        self.exe_path = self._find_power_gadget()
        self._temp_dir = tempfile.gettempdir()
        
    def _find_power_gadget(self) -> Optional[str]:
        """Intel Power Gadget kurulum yolunu bul"""
        for path in self.POSSIBLE_PATHS:
            if os.path.exists(path):
                return path
        
        # Registry'den de kontrol et
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                 r"SOFTWARE\Intel\Power Gadget 3.6")
            install_path = winreg.QueryValueEx(key, "InstallPath")[0]
            exe_path = os.path.join(install_path, "PowerLog3.0.exe")
            if os.path.exists(exe_path):
                return exe_path
        except:
            pass
            
        return None
    
    def is_available(self) -> bool:
        """Intel Power Gadget kullanılabilir mi?"""
        return self.exe_path is not None
    
    def get_info(self) -> Dict:
        """Power Gadget bilgilerini döndür"""
        return {
            'available': self.is_available(),
            'path': self.exe_path,
            'version': self._get_version() if self.is_available() else None
        }
    
    def _get_version(self) -> str:
        """Power Gadget versiyonunu al"""
        if self.exe_path:
            if "3.6" in self.exe_path:
                return "3.6"
            elif "3.5" in self.exe_path:
                return "3.5"
        return "unknown"
    
    def measure(self, func: Callable, *args, 
                duration_hint_ms: int = 5000,
                resolution_ms: int = 50,
                **kwargs) -> RealEnergyResult:
        """
        Fonksiyonu çalıştırıp GERÇEK enerji tüketimini ölç
        
        Args:
            func: Ölçülecek fonksiyon
            duration_hint_ms: Tahmini çalışma süresi (ms)
            resolution_ms: Örnekleme çözünürlüğü (ms)
        """
        if not self.is_available():
            return self._create_error_result("Intel Power Gadget kurulu değil")
        
        # Benzersiz log dosyası oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_file = os.path.join(self._temp_dir, f"power_log_{timestamp}.csv")
        
        try:
            # Tahmini süreyi hesapla (en az 1 saniye)
            duration_sec = max(duration_hint_ms / 1000, 1)
            
            # Power Gadget'ı başlat
            cmd = f'"{self.exe_path}" -duration {duration_sec + 2} -resolution {resolution_ms} -file "{log_file}"'
            
            process = subprocess.Popen(
                cmd, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Power Gadget'ın başlaması için bekle
            time.sleep(0.3)
            
            # ===== FONKSİYONU ÇALIŞTIR =====
            start_time = time.perf_counter()
            start_timestamp = datetime.now()
            
            result = func(*args, **kwargs)
            
            end_time = time.perf_counter()
            end_timestamp = datetime.now()
            execution_time_ms = (end_time - start_time) * 1000
            # ================================
            
            # Power Gadget'ın durmasını bekle
            time.sleep(0.5)
            
            try:
                process.terminate()
            except:
                pass
            
            # Log dosyasını parse et
            energy_data = self._parse_power_log(
                log_file, 
                start_timestamp, 
                end_timestamp,
                execution_time_ms
            )
            
            # Temizlik
            try:
                os.remove(log_file)
            except:
                pass
            
            return RealEnergyResult(
                algorithm="measured_function",
                data_size=0,
                execution_time_ms=execution_time_ms,
                energy_joules=energy_data['energy_joules'],
                avg_power_watts=energy_data['avg_power'],
                max_power_watts=energy_data['max_power'],
                min_power_watts=energy_data['min_power'],
                cpu_frequency_mhz=energy_data.get('avg_frequency', 0),
                cpu_temperature_c=energy_data.get('avg_temperature', 0),
                cpu_utilization=energy_data.get('avg_utilization', 0),
                measurement_source='intel_power_gadget',
                is_real_measurement=True,
                sample_count=energy_data.get('sample_count', 0),
                sampling_interval_ms=resolution_ms,
                timestamp=datetime.now().isoformat(),
                success=True
            )
            
        except Exception as e:
            # Temizlik
            try:
                os.remove(log_file)
            except:
                pass
            return self._create_error_result(str(e))
    
    def _parse_power_log(self, log_file: str, 
                         start_time: datetime, 
                         end_time: datetime,
                         execution_time_ms: float) -> Dict:
        """
        Power Gadget CSV log dosyasını parse et ve enerji hesapla
        """
        if not os.path.exists(log_file):
            return self._empty_energy_data()
        
        try:
            # Dosyanın yazılmasını bekle
            time.sleep(0.2)
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CSV formatını belirle
            lines = content.strip().split('\n')
            if len(lines) < 2:
                return self._empty_energy_data()
            
            # Header'ı bul
            header_line = None
            data_start = 0
            for i, line in enumerate(lines):
                if 'Elapsed Time' in line or 'System Time' in line:
                    header_line = line
                    data_start = i + 1
                    break
            
            if header_line is None:
                # Alternatif format dene
                header_line = lines[0]
                data_start = 1
            
            # Sütun indekslerini bul
            headers = [h.strip() for h in header_line.split(',')]
            
            col_indices = {
                'power': None,
                'energy': None,
                'frequency': None,
                'temperature': None,
                'utilization': None,
                'elapsed': None
            }
            
            for i, h in enumerate(headers):
                h_lower = h.lower()
                if 'package power' in h_lower or 'processor power' in h_lower:
                    col_indices['power'] = i
                elif 'cumulative' in h_lower and 'energy' in h_lower:
                    col_indices['energy'] = i
                elif 'frequency' in h_lower and 'average' in h_lower:
                    col_indices['frequency'] = i
                elif 'temperature' in h_lower:
                    col_indices['temperature'] = i
                elif 'utilization' in h_lower or 'gt utilization' in h_lower:
                    col_indices['utilization'] = i
                elif 'elapsed' in h_lower:
                    col_indices['elapsed'] = i
            
            # Verileri oku
            power_values = []
            energy_values = []
            frequency_values = []
            temperature_values = []
            utilization_values = []
            
            for line in lines[data_start:]:
                if not line.strip():
                    continue
                    
                values = line.split(',')
                
                try:
                    if col_indices['power'] is not None and col_indices['power'] < len(values):
                        val = values[col_indices['power']].strip()
                        if val and val != '':
                            power_values.append(float(val))
                    
                    if col_indices['energy'] is not None and col_indices['energy'] < len(values):
                        val = values[col_indices['energy']].strip()
                        if val and val != '':
                            energy_values.append(float(val))
                    
                    if col_indices['frequency'] is not None and col_indices['frequency'] < len(values):
                        val = values[col_indices['frequency']].strip()
                        if val and val != '':
                            frequency_values.append(float(val))
                    
                    if col_indices['temperature'] is not None and col_indices['temperature'] < len(values):
                        val = values[col_indices['temperature']].strip()
                        if val and val != '':
                            temperature_values.append(float(val))
                            
                except (ValueError, IndexError):
                    continue
            
            # Enerji hesapla
            if energy_values and len(energy_values) >= 2:
                # Kümülatif enerjiden hesapla (daha doğru)
                # Çalışma süresi oranında enerji al
                total_energy = energy_values[-1] - energy_values[0]
                total_time = len(energy_values) * 0.05  # 50ms resolution varsayımı
                
                # Orantılı hesapla
                if total_time > 0:
                    energy_joules = total_energy * (execution_time_ms / 1000) / total_time
                else:
                    energy_joules = total_energy
            elif power_values:
                # Güç değerlerinden hesapla
                avg_power = sum(power_values) / len(power_values)
                energy_joules = avg_power * (execution_time_ms / 1000)
            else:
                energy_joules = 0
            
            return {
                'energy_joules': energy_joules,
                'avg_power': sum(power_values) / len(power_values) if power_values else 0,
                'max_power': max(power_values) if power_values else 0,
                'min_power': min(power_values) if power_values else 0,
                'avg_frequency': sum(frequency_values) / len(frequency_values) if frequency_values else 0,
                'avg_temperature': sum(temperature_values) / len(temperature_values) if temperature_values else 0,
                'avg_utilization': sum(utilization_values) / len(utilization_values) if utilization_values else 0,
                'sample_count': len(power_values)
            }
            
        except Exception as e:
            print(f"Log parse hatası: {e}")
            return self._empty_energy_data()
    
    def _empty_energy_data(self) -> Dict:
        return {
            'energy_joules': 0,
            'avg_power': 0,
            'max_power': 0,
            'min_power': 0,
            'avg_frequency': 0,
            'avg_temperature': 0,
            'avg_utilization': 0,
            'sample_count': 0
        }
    
    def _create_error_result(self, error: str) -> RealEnergyResult:
        return RealEnergyResult(
            algorithm="error",
            data_size=0,
            execution_time_ms=0,
            energy_joules=0,
            avg_power_watts=0,
            max_power_watts=0,
            min_power_watts=0,
            cpu_frequency_mhz=0,
            cpu_temperature_c=0,
            cpu_utilization=0,
            measurement_source='error',
            is_real_measurement=False,
            sample_count=0,
            sampling_interval_ms=0,
            timestamp=datetime.now().isoformat(),
            success=False,
            error_message=error
        )


class WMIPowerMeter:
    """
    WMI (Windows Management Instrumentation) ile güç izleme
    Open Hardware Monitor veya HWiNFO ile birlikte çalışabilir
    """
    
    def __init__(self):
        self.wmi_available = self._check_wmi()
        
    def _check_wmi(self) -> bool:
        try:
            import wmi
            return True
        except ImportError:
            return False
    
    def is_available(self) -> bool:
        return self.wmi_available
    
    def get_cpu_power(self) -> Optional[float]:
        """WMI üzerinden CPU gücünü al (Open Hardware Monitor gerekli)"""
        if not self.wmi_available:
            return None
            
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            
            for sensor in w.Sensor():
                if sensor.SensorType == 'Power' and 'CPU' in sensor.Name:
                    return float(sensor.Value)
        except:
            pass
        
        return None


class LibreHardwareMonitorMeter:
    """
    LibreHardwareMonitor API kullanarak enerji ölçümü
    LibreHardwareMonitor kurulu ve çalışıyor olmalı
    """
    
    def __init__(self):
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        try:
            import wmi
            w = wmi.WMI(namespace="root\\LibreHardwareMonitor")
            return True
        except:
            return False
    
    def is_available(self) -> bool:
        return self.available
    
    def get_power_data(self) -> Dict:
        """CPU güç verilerini al"""
        if not self.available:
            return {}
            
        try:
            import wmi
            w = wmi.WMI(namespace="root\\LibreHardwareMonitor")
            
            data = {}
            for sensor in w.Sensor():
                if sensor.SensorType == 'Power':
                    data[sensor.Name] = float(sensor.Value)
            return data
        except:
            return {}


class RealEnergyMeter:
    """
    Ana enerji ölçüm sınıfı
    En iyi mevcut yöntemi otomatik seçer
    """
    
    def __init__(self):
        self.intel_meter = IntelPowerGadgetMeter()
        self.wmi_meter = WMIPowerMeter()
        self.libre_meter = LibreHardwareMonitorMeter()
        
        self._select_best_method()
    
    def _select_best_method(self):
        """En iyi ölçüm yöntemini seç"""
        if self.intel_meter.is_available():
            self.primary_meter = self.intel_meter
            self.method = 'intel_power_gadget'
        elif self.libre_meter.is_available():
            self.primary_meter = self.libre_meter
            self.method = 'libre_hardware_monitor'
        elif self.wmi_meter.is_available():
            self.primary_meter = self.wmi_meter
            self.method = 'wmi'
        else:
            self.primary_meter = None
            self.method = 'none'
    
    def is_available(self) -> bool:
        """Gerçek ölçüm kullanılabilir mi?"""
        return self.method == 'intel_power_gadget'
    
    def get_method(self) -> str:
        """Kullanılan ölçüm yöntemini döndür"""
        return self.method
    
    def get_status(self) -> Dict:
        """Ölçüm durumu bilgisi"""
        return {
            'intel_power_gadget': {
                'available': self.intel_meter.is_available(),
                'info': self.intel_meter.get_info()
            },
            'libre_hardware_monitor': {
                'available': self.libre_meter.is_available()
            },
            'wmi': {
                'available': self.wmi_meter.is_available()
            },
            'selected_method': self.method,
            'is_real_measurement': self.is_available()
        }
    
    def measure(self, func: Callable, *args, 
                algorithm_name: str = "unknown",
                data_size: int = 0,
                **kwargs) -> RealEnergyResult:
        """
        Fonksiyonu çalıştırıp enerji tüketimini ölç
        """
        if not self.is_available():
            return RealEnergyResult(
                algorithm=algorithm_name,
                data_size=data_size,
                execution_time_ms=0,
                energy_joules=0,
                avg_power_watts=0,
                max_power_watts=0,
                min_power_watts=0,
                cpu_frequency_mhz=0,
                cpu_temperature_c=0,
                cpu_utilization=0,
                measurement_source='none',
                is_real_measurement=False,
                sample_count=0,
                sampling_interval_ms=0,
                timestamp=datetime.now().isoformat(),
                success=False,
                error_message="Gerçek ölçüm için Intel Power Gadget gerekli"
            )
        
        result = self.intel_meter.measure(func, *args, **kwargs)
        result.algorithm = algorithm_name
        result.data_size = data_size
        
        return result


def check_system_status():
    """Sistem durumunu kontrol et ve raporla"""
    print("="*70)
    print(" 🔍 GERÇEK ENERJİ ÖLÇÜMÜ - SİSTEM KONTROLÜ")
    print("="*70)
    
    meter = RealEnergyMeter()
    status = meter.get_status()
    
    print("\n📊 ÖLÇÜM YÖNTEMLERİ:")
    print("-"*50)
    
    # Intel Power Gadget
    ipg = status['intel_power_gadget']
    if ipg['available']:
        print(f"  ✅ Intel Power Gadget: KURULU")
        print(f"     Yol: {ipg['info']['path']}")
        print(f"     Versiyon: {ipg['info']['version']}")
    else:
        print(f"  ❌ Intel Power Gadget: KURULU DEĞİL")
        print(f"     İndirme: https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html")
    
    # LibreHardwareMonitor
    lhm = status['libre_hardware_monitor']
    print(f"\n  {'✅' if lhm['available'] else '❌'} LibreHardwareMonitor: {'KURULU' if lhm['available'] else 'KURULU DEĞİL'}")
    
    # WMI
    wmi_status = status['wmi']
    print(f"  {'✅' if wmi_status['available'] else '❌'} WMI Desteği: {'MEVCUT' if wmi_status['available'] else 'MEVCUT DEĞİL'}")
    
    print("\n" + "="*70)
    print(f" 🎯 SEÇİLEN YÖNTEM: {status['selected_method'].upper()}")
    print(f" ⚡ GERÇEK ÖLÇÜM: {'EVET ✅' if status['is_real_measurement'] else 'HAYIR ❌'}")
    print("="*70)
    
    if not status['is_real_measurement']:
        print("\n⚠️  GERÇEK ÖLÇÜM İÇİN:")
        print("    Intel Power Gadget'ı indirin ve kurun:")
        print("    https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html")
        print()
    
    return status


def demo_measurement():
    """Demo ölçüm"""
    meter = RealEnergyMeter()
    
    if not meter.is_available():
        print("❌ Gerçek ölçüm için Intel Power Gadget gerekli!")
        return
    
    print("\n🔋 Demo Ölçüm Başlıyor...")
    
    # Test fonksiyonu
    def test_calculation():
        result = 0
        for i in range(1000000):
            result += i * i
        return result
    
    result = meter.measure(test_calculation, algorithm_name="test_calculation")
    
    print("\n📊 ÖLÇÜM SONUÇLARI:")
    print("-"*50)
    print(f"  Çalışma Süresi: {result.execution_time_ms:.2f} ms")
    print(f"  Enerji Tüketimi: {result.energy_joules:.6f} Joule")
    print(f"  Ortalama Güç: {result.avg_power_watts:.2f} Watt")
    print(f"  Maksimum Güç: {result.max_power_watts:.2f} Watt")
    print(f"  Minimum Güç: {result.min_power_watts:.2f} Watt")
    print(f"  Örnek Sayısı: {result.sample_count}")
    print(f"  Gerçek Ölçüm: {'Evet ✅' if result.is_real_measurement else 'Hayır ❌'}")


if __name__ == '__main__':
    status = check_system_status()
    
    if status['is_real_measurement']:
        demo_measurement()
