"""
Windows Enerji Ölçüm Modülü
===========================
Bu modül Windows'ta çeşitli yöntemlerle enerji tüketimini ölçer.

Desteklenen Yöntemler:
1. Intel Power Gadget (en doğru)
2. WMI ile CPU yükü tabanlı tahmin
3. Geliştirilmiş matematiksel model

Kullanım:
    from energy_meter import EnergyMeter
    
    meter = EnergyMeter()
    result = meter.measure(my_function, args)
"""

import os
import sys
import time
import json
import subprocess
import csv
import ctypes
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class EnergyResult:
    """Enerji ölçüm sonucu"""
    algorithm: str
    data_size: int
    execution_time_ms: float
    energy_joules: float
    power_watts: float
    cpu_percent: float
    memory_mb: float
    source: str  # 'intel_power_gadget', 'wmi', 'estimation'
    timestamp: str
    success: bool
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IntelPowerGadget:
    """Intel Power Gadget ile enerji ölçümü"""
    
    # Olası kurulum yolları
    POSSIBLE_PATHS = [
        r"C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe",
        r"C:\Program Files\Intel\Power Gadget 3.5\PowerLog3.0.exe",
        r"C:\Program Files (x86)\Intel\Power Gadget 3.6\PowerLog3.0.exe",
    ]
    
    def __init__(self):
        self.exe_path = self._find_power_gadget()
        self.temp_log = Path("power_gadget_log.csv")
        
    def _find_power_gadget(self) -> Optional[str]:
        """Power Gadget'ın kurulu olduğu yolu bul"""
        for path in self.POSSIBLE_PATHS:
            if os.path.exists(path):
                return path
        return None
    
    def is_available(self) -> bool:
        """Power Gadget kullanılabilir mi?"""
        return self.exe_path is not None
    
    def measure(self, func: Callable, *args, **kwargs) -> Dict:
        """
        Fonksiyonu çalıştırıp enerji tüketimini ölç
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Intel Power Gadget kurulu değil',
                'energy_joules': 0
            }
        
        # Eski log dosyasını sil
        if self.temp_log.exists():
            self.temp_log.unlink()
        
        try:
            # Power Gadget'ı arka planda başlat (5 saniye süre)
            cmd = f'"{self.exe_path}" -duration 5 -file {self.temp_log}'
            process = subprocess.Popen(cmd, shell=True, 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
            
            # Biraz bekle (Power Gadget başlasın)
            time.sleep(0.2)
            
            # Fonksiyonu çalıştır
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            
            # Power Gadget'ın bitmesini bekle
            process.wait(timeout=10)
            
            # Log dosyasını parse et
            energy_data = self._parse_log()
            
            return {
                'success': True,
                'execution_time_ms': execution_time * 1000,
                'energy_joules': energy_data.get('energy', 0),
                'power_watts': energy_data.get('avg_power', 0),
                'max_power_watts': energy_data.get('max_power', 0),
                'source': 'intel_power_gadget',
                'function_result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'energy_joules': 0
            }
    
    def _parse_log(self) -> Dict:
        """Power Gadget CSV log dosyasını parse et"""
        if not self.temp_log.exists():
            return {'energy': 0, 'avg_power': 0, 'max_power': 0}
        
        try:
            with open(self.temp_log, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    return {'energy': 0, 'avg_power': 0, 'max_power': 0}
                
                power_values = []
                energy_values = []
                
                for row in rows:
                    for key, value in row.items():
                        try:
                            val = float(value)
                            if 'Power' in key and 'Package' in key:
                                power_values.append(val)
                            if 'Cumulative' in key and 'Energy' in key:
                                energy_values.append(val)
                        except (ValueError, TypeError):
                            continue
                
                return {
                    'energy': energy_values[-1] if energy_values else 0,
                    'avg_power': sum(power_values) / len(power_values) if power_values else 0,
                    'max_power': max(power_values) if power_values else 0
                }
                
        except Exception as e:
            return {'energy': 0, 'avg_power': 0, 'max_power': 0, 'error': str(e)}


class WMIEnergyEstimator:
    """WMI ile CPU yükü tabanlı enerji tahmini"""
    
    def __init__(self):
        self.wmi_available = self._check_wmi()
        
    def _check_wmi(self) -> bool:
        """WMI kullanılabilir mi?"""
        try:
            import wmi
            return True
        except ImportError:
            return False
    
    def get_cpu_usage(self) -> float:
        """Anlık CPU kullanımını al"""
        # Önce psutil dene (daha güvenilir)
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            pass
        
        # WMI ile dene (COM thread-safe şekilde)
        try:
            import pythoncom
            pythoncom.CoInitialize()
            try:
                import wmi
                c = wmi.WMI()
                for cpu in c.Win32_Processor():
                    return float(cpu.LoadPercentage or 0)
            finally:
                pythoncom.CoUninitialize()
        except:
            pass
        
        return 50.0  # Varsayılan
    
    def estimate_power(self, cpu_usage: float, tdp_watts: float = 65) -> float:
        """
        CPU kullanımına göre güç tahmini
        
        Basit model: Power = TDP * (idle_ratio + load_ratio * cpu_usage)
        """
        idle_ratio = 0.2  # Boşta TDP'nin %20'si
        load_ratio = 0.8  # Yük altında kalan %80
        
        power = tdp_watts * (idle_ratio + load_ratio * (cpu_usage / 100))
        return power


class EnhancedEnergyModel:
    """Geliştirilmiş matematiksel enerji modeli"""
    
    # Literatürden alınan enerji sabitleri (yaklaşık değerler)
    ENERGY_PER_COMPARISON = 1e-9      # ~1 nanojoule
    ENERGY_PER_SWAP = 2e-9            # ~2 nanojoule
    ENERGY_PER_MEMORY_ACCESS = 5e-10  # ~0.5 nanojoule
    ENERGY_PER_ITERATION = 1e-9       # ~1 nanojoule
    
    # CPU güç sabitleri
    CPU_IDLE_POWER = 5.0    # Watt (boşta)
    CPU_ACTIVE_POWER = 35.0  # Watt (aktif)
    MEMORY_POWER_PER_GB = 3.0  # Watt per GB
    
    def estimate(self, metrics: Dict) -> Dict:
        """
        Algoritma metriklerine göre enerji tahmini
        
        Args:
            metrics: {
                'comparisons': int,
                'swaps': int,
                'iterations': int,
                'memory_mb': float,
                'time_ms': float
            }
        """
        # İşlem bazlı enerji
        E_comparisons = metrics.get('comparisons', 0) * self.ENERGY_PER_COMPARISON
        E_swaps = metrics.get('swaps', 0) * self.ENERGY_PER_SWAP
        E_iterations = metrics.get('iterations', 0) * self.ENERGY_PER_ITERATION
        E_memory = metrics.get('memory_accesses', 0) * self.ENERGY_PER_MEMORY_ACCESS
        
        E_operations = E_comparisons + E_swaps + E_iterations + E_memory
        
        # Zaman bazlı enerji (CPU aktif güç tüketimi)
        time_seconds = metrics.get('time_ms', 0) / 1000
        E_time = self.CPU_ACTIVE_POWER * time_seconds
        
        # Bellek enerji tüketimi
        memory_gb = metrics.get('memory_mb', 0) / 1024
        E_ram = self.MEMORY_POWER_PER_GB * memory_gb * time_seconds
        
        # Toplam enerji
        total_energy = E_operations + E_time + E_ram
        
        # Ortalama güç
        avg_power = total_energy / time_seconds if time_seconds > 0 else 0
        
        return {
            'total_energy_joules': total_energy,
            'energy_operations': E_operations,
            'energy_time_based': E_time,
            'energy_memory': E_ram,
            'avg_power_watts': avg_power,
            'breakdown': {
                'comparisons': E_comparisons,
                'swaps': E_swaps,
                'iterations': E_iterations,
                'memory_accesses': E_memory
            }
        }


class EnergyMeter:
    """
    Ana enerji ölçüm sınıfı
    Otomatik olarak en iyi yöntemi seçer
    """
    
    def __init__(self, prefer_method: str = 'auto'):
        """
        Args:
            prefer_method: 'auto', 'power_gadget', 'wmi', 'estimation'
        """
        self.intel_gadget = IntelPowerGadget()
        self.wmi_estimator = WMIEnergyEstimator()
        self.model = EnhancedEnergyModel()
        self.prefer_method = prefer_method
        
        # Hangi yöntemlerin kullanılabilir olduğunu belirle
        self.available_methods = self._check_available_methods()
        
    def _check_available_methods(self) -> List[str]:
        """Kullanılabilir ölçüm yöntemlerini kontrol et"""
        methods = ['estimation']  # Her zaman kullanılabilir
        
        if self.intel_gadget.is_available():
            methods.insert(0, 'power_gadget')
            
        if self.wmi_estimator.wmi_available:
            methods.insert(1 if 'power_gadget' in methods else 0, 'wmi')
            
        return methods
    
    def get_best_method(self) -> str:
        """En iyi ölçüm yöntemini döndür"""
        if self.prefer_method != 'auto':
            if self.prefer_method in self.available_methods:
                return self.prefer_method
        
        # Öncelik sırası: power_gadget > wmi > estimation
        for method in ['power_gadget', 'wmi', 'estimation']:
            if method in self.available_methods:
                return method
                
        return 'estimation'
    
    def measure(self, algorithm_name: str, func: Callable, data: Any, 
                metrics: Optional[Dict] = None) -> EnergyResult:
        """
        Algoritma enerji tüketimini ölç
        
        Args:
            algorithm_name: Algoritma adı
            func: Çalıştırılacak fonksiyon
            data: Algoritmaya verilecek veri
            metrics: Ek metrikler (karşılaştırma, takas sayısı vb.)
        """
        import tracemalloc
        
        method = self.get_best_method()
        timestamp = datetime.now().isoformat()
        data_size = len(data) if hasattr(data, '__len__') else 0
        
        # Bellek izlemeyi başlat
        tracemalloc.start()
        
        # CPU kullanımını ölçmeye başla
        cpu_start = self._get_cpu_percent()
        
        try:
            if method == 'power_gadget':
                result = self._measure_with_power_gadget(func, data)
            elif method == 'wmi':
                result = self._measure_with_wmi(func, data)
            else:
                result = self._measure_with_estimation(func, data, metrics)
            
            # Bellek kullanımını al
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            memory_mb = peak / (1024 * 1024)
            
            # CPU kullanımını hesapla
            cpu_end = self._get_cpu_percent()
            cpu_percent = (cpu_start + cpu_end) / 2
            
            return EnergyResult(
                algorithm=algorithm_name,
                data_size=data_size,
                execution_time_ms=result.get('execution_time_ms', 0),
                energy_joules=result.get('energy_joules', 0),
                power_watts=result.get('power_watts', 0),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                source=method,
                timestamp=timestamp,
                success=result.get('success', True),
                error_message=result.get('error', '')
            )
            
        except Exception as e:
            tracemalloc.stop()
            return EnergyResult(
                algorithm=algorithm_name,
                data_size=data_size,
                execution_time_ms=0,
                energy_joules=0,
                power_watts=0,
                cpu_percent=0,
                memory_mb=0,
                source=method,
                timestamp=timestamp,
                success=False,
                error_message=str(e)
            )
    
    def _get_cpu_percent(self) -> float:
        """CPU kullanım yüzdesini al"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return self.wmi_estimator.get_cpu_usage()
    
    def _measure_with_power_gadget(self, func: Callable, data: Any) -> Dict:
        """Intel Power Gadget ile ölç"""
        return self.intel_gadget.measure(func, data)
    
    def _measure_with_wmi(self, func: Callable, data: Any) -> Dict:
        """WMI ile CPU yükü tabanlı tahmin"""
        # Başlangıç CPU yükü
        cpu_before = self.wmi_estimator.get_cpu_usage()
        
        # Fonksiyonu çalıştır
        start_time = time.perf_counter()
        result = func(data)
        end_time = time.perf_counter()
        
        # Bitiş CPU yükü
        cpu_after = self.wmi_estimator.get_cpu_usage()
        
        execution_time = end_time - start_time
        avg_cpu = (cpu_before + cpu_after) / 2
        
        # Güç ve enerji tahmini
        power = self.wmi_estimator.estimate_power(avg_cpu)
        energy = power * execution_time
        
        return {
            'success': True,
            'execution_time_ms': execution_time * 1000,
            'energy_joules': energy,
            'power_watts': power,
            'cpu_percent': avg_cpu
        }
    
    def _measure_with_estimation(self, func: Callable, data: Any, 
                                  metrics: Optional[Dict] = None) -> Dict:
        """Geliştirilmiş model ile tahmin"""
        # Fonksiyonu çalıştır
        start_time = time.perf_counter()
        result = func(data)
        end_time = time.perf_counter()
        
        execution_time_ms = (end_time - start_time) * 1000
        
        # Metrikler verilmişse model ile hesapla
        if metrics:
            metrics['time_ms'] = execution_time_ms
            estimation = self.model.estimate(metrics)
            
            return {
                'success': True,
                'execution_time_ms': execution_time_ms,
                'energy_joules': estimation['total_energy_joules'],
                'power_watts': estimation['avg_power_watts'],
                'source': 'estimation'
            }
        
        # Basit zaman bazlı tahmin
        power = 25.0  # Varsayılan ortalama güç (Watt)
        energy = power * (execution_time_ms / 1000)
        
        return {
            'success': True,
            'execution_time_ms': execution_time_ms,
            'energy_joules': energy,
            'power_watts': power,
            'source': 'estimation'
        }


def get_system_info() -> Dict:
    """Sistem bilgilerini al"""
    info = {
        'platform': sys.platform,
        'python_version': sys.version,
        'available_methods': []
    }
    
    # Intel Power Gadget kontrolü
    gadget = IntelPowerGadget()
    if gadget.is_available():
        info['available_methods'].append('intel_power_gadget')
        info['power_gadget_path'] = gadget.exe_path
    
    # WMI kontrolü
    try:
        import wmi
        info['available_methods'].append('wmi')
    except ImportError:
        pass
    
    # psutil kontrolü
    try:
        import psutil
        info['available_methods'].append('psutil')
        info['cpu_count'] = psutil.cpu_count()
        info['total_memory_gb'] = psutil.virtual_memory().total / (1024**3)
    except ImportError:
        pass
    
    info['available_methods'].append('estimation')
    
    return info


if __name__ == '__main__':
    # Test
    print("="*60)
    print("Enerji Ölçüm Modülü - Sistem Kontrolü")
    print("="*60)
    
    info = get_system_info()
    print(f"\nPlatform: {info['platform']}")
    print(f"Python: {info['python_version']}")
    print(f"\nKullanılabilir Yöntemler:")
    for method in info['available_methods']:
        print(f"  ✅ {method}")
    
    if 'intel_power_gadget' not in info['available_methods']:
        print("\n⚠️  Intel Power Gadget bulunamadı.")
        print("   Gerçek enerji ölçümü için kurulum yapın:")
        print("   https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html")
