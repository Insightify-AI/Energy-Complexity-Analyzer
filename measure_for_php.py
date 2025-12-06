"""
PHP-Python Köprüsü - Gerçek Enerji Ölçümü
=========================================
Bu script PHP'den çağrılarak algoritmaları çalıştırır ve
GERÇEK enerji ölçümü yapar.

KULLANIM:
    php'den: shell_exec('python measure_for_php.py algorithm_name data_size')
"""

import sys
import json
import random
import os
import warnings
import threading
from pathlib import Path

# Uyarıları bastır
warnings.filterwarnings('ignore')

# Thread hatalarını bastır
threading.excepthook = lambda args: None

# Modül yolunu ekle
sys.path.insert(0, str(Path(__file__).parent))

from real_power_meter import RealPowerMeter
from algorithms import ALGORITHMS


def run_measurement(algorithm_name: str, data_size: int, runs: int = 3):
    """
    Algoritma enerji ölçümü yap ve JSON olarak döndür
    """
    result = {
        'success': False,
        'is_real_measurement': False,
        'algorithm': algorithm_name,
        'data_size': data_size,
        'error': None
    }
    
    try:
        # Ölçüm sistemini başlat
        meter = RealPowerMeter(sampling_interval_ms=50)
        
        if not meter.is_available():
            # Gerçek ölçüm mümkün değil, tahmin kullan
            result['error'] = meter.get_error()
            result['is_real_measurement'] = False
            result['measurement_source'] = 'estimation_fallback'
            
            # Basit tahmin ile devam et
            return run_estimation_fallback(algorithm_name, data_size, runs)
        
        result['is_real_measurement'] = True
        result['measurement_source'] = 'LibreHardwareMonitor_WMI'
        
        # Algoritmayı bul
        algo_info = None
        for category in ALGORITHMS.values():
            if algorithm_name in category:
                algo_info = category[algorithm_name]
                break
        
        if not algo_info:
            result['error'] = f'Algoritma bulunamadı: {algorithm_name}'
            return result
        
        # Test verisi oluştur
        test_data = [random.randint(1, data_size * 10) for _ in range(data_size)]
        
        # Çoklu çalıştırma
        all_energy = []
        all_time = []
        all_power = []
        metrics_data = None
        
        for run in range(runs):
            data_copy = test_data.copy()
            
            def run_algo():
                return algo_info['func'](data_copy)
            
            measurement = meter.measure_function(
                run_algo,
                algorithm_name=algorithm_name,
                data_size=data_size
            )
            
            all_energy.append(measurement.energy_joules)
            all_time.append(measurement.execution_time_ms)
            all_power.append(measurement.avg_power_watts)
            
            # Son çalıştırmadan metrikleri al
            _, metrics_data = algo_info['func'](test_data.copy())
        
        # Ortalama hesapla
        result['success'] = True
        result['averages'] = {
            'execution_time_ms': sum(all_time) / len(all_time),
            'energy_joules': sum(all_energy) / len(all_energy),
            'avg_power_watts': sum(all_power) / len(all_power),
            'max_power_watts': max(all_power),
            'min_power_watts': min(all_power)
        }
        result['runs'] = runs
        result['algorithm_info'] = {
            'name': algo_info['name'],
            'complexity_time': algo_info['complexity_time'],
            'complexity_space': algo_info['complexity_space']
        }
        
        if metrics_data:
            result['metrics'] = {
                'comparisons': metrics_data.comparisons,
                'swaps': metrics_data.swaps,
                'iterations': metrics_data.iterations
            }
        
    except Exception as e:
        result['error'] = str(e)
        result['success'] = False
    
    return result


def run_estimation_fallback(algorithm_name: str, data_size: int, runs: int = 3):
    """
    Gerçek ölçüm mümkün değilse tahmin modeli kullan
    """
    import time
    
    result = {
        'success': False,
        'is_real_measurement': False,
        'algorithm': algorithm_name,
        'data_size': data_size,
        'measurement_source': 'estimation'
    }
    
    try:
        # Algoritmayı bul
        algo_info = None
        for category in ALGORITHMS.values():
            if algorithm_name in category:
                algo_info = category[algorithm_name]
                break
        
        if not algo_info:
            result['error'] = f'Algoritma bulunamadı: {algorithm_name}'
            return result
        
        # Test verisi
        test_data = [random.randint(1, data_size * 10) for _ in range(data_size)]
        
        all_time = []
        all_energy = []
        metrics_data = None
        
        ESTIMATED_POWER = 25.0  # Watt (tahmin)
        
        for run in range(runs):
            data_copy = test_data.copy()
            
            start = time.perf_counter()
            _, metrics_data = algo_info['func'](data_copy)
            end = time.perf_counter()
            
            exec_time_ms = (end - start) * 1000
            energy = ESTIMATED_POWER * (exec_time_ms / 1000)
            
            all_time.append(exec_time_ms)
            all_energy.append(energy)
        
        result['success'] = True
        result['averages'] = {
            'execution_time_ms': sum(all_time) / len(all_time),
            'energy_joules': sum(all_energy) / len(all_energy),
            'avg_power_watts': ESTIMATED_POWER,
            'max_power_watts': ESTIMATED_POWER,
            'min_power_watts': ESTIMATED_POWER
        }
        result['runs'] = runs
        result['algorithm_info'] = {
            'name': algo_info['name'],
            'complexity_time': algo_info['complexity_time'],
            'complexity_space': algo_info['complexity_space']
        }
        
        if metrics_data:
            result['metrics'] = {
                'comparisons': metrics_data.comparisons,
                'swaps': metrics_data.swaps,
                'iterations': metrics_data.iterations
            }
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main():
    """Ana fonksiyon - komut satırı argümanları"""
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'error': 'Kullanım: python measure_for_php.py <algorithm_name> <data_size> [runs]'
        }))
        return
    
    algorithm_name = sys.argv[1]
    data_size = int(sys.argv[2])
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    result = run_measurement(algorithm_name, data_size, runs)
    
    # JSON olarak yazdır (PHP bunu okuyacak)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
