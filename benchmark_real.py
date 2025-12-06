"""
GERÇEK ENERJİ BENCHMARK - LibreHardwareMonitor ile
===================================================
Bu script GERÇEK güç sensörlerini kullanarak
tüm algoritmaların enerji tüketimini ölçer.
"""

import sys
import json
import random
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from real_power_meter import RealPowerMeter, EnergyMeasurement
from algorithms import ALGORITHMS


def run_real_benchmark():
    """Gerçek enerji ölçümü ile benchmark"""
    
    print("\n" + "="*70)
    print(" 🔋 GERÇEK ENERJİ BENCHMARK")
    print("="*70)
    
    # Ölçüm sistemini başlat
    meter = RealPowerMeter(sampling_interval_ms=50)
    
    if not meter.is_available():
        print(f"\n❌ HATA: {meter.get_error()}")
        print("\n📝 LibreHardwareMonitor'un açık olduğundan emin olun!")
        return None
    
    print("\n✅ Gerçek ölçüm sistemi hazır!")
    
    # Anlık güç okuması
    reading = meter.read_power()
    print(f"\n📊 Anlık Güç: {reading.cpu_package:.2f} W (CPU Package)")
    
    # Test boyutları
    sizes = [500, 1000, 2000]
    runs = 2
    
    results = {
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'measurement_type': 'REAL',
            'source': 'LibreHardwareMonitor_WMI',
            'is_real_measurement': True
        },
        'benchmarks': []
    }
    
    print(f"\n📏 Veri Boyutları: {sizes}")
    print(f"🔄 Çalıştırma: {runs}")
    
    for size in sizes:
        print(f"\n{'─'*60}")
        print(f" 📦 Veri Boyutu: {size}")
        print(f"{'─'*60}")
        
        # Test verisi
        test_data = [random.randint(1, size*10) for _ in range(size)]
        
        print("\n  🔢 Sıralama Algoritmaları:")
        
        for algo_name, algo_info in ALGORITHMS['sorting'].items():
            print(f"    ⏳ {algo_name}...", end=" ", flush=True)
            
            all_energy = []
            all_time = []
            all_power = []
            
            for run in range(runs):
                data_copy = test_data.copy()
                
                def run_algo():
                    return algo_info['func'](data_copy)
                
                result = meter.measure_function(
                    run_algo,
                    algorithm_name=algo_name,
                    data_size=size
                )
                
                all_energy.append(result.energy_joules)
                all_time.append(result.execution_time_ms)
                all_power.append(result.avg_power_watts)
            
            avg_energy = sum(all_energy) / len(all_energy)
            avg_time = sum(all_time) / len(all_time)
            avg_power = sum(all_power) / len(all_power)
            
            results['benchmarks'].append({
                'type': 'sorting',
                'algorithm': algo_name,
                'data_size': size,
                'runs': runs,
                'is_real_measurement': True,
                'averages': {
                    'energy_joules': avg_energy,
                    'execution_time_ms': avg_time,
                    'avg_power_watts': avg_power
                }
            })
            
            print(f"✅ {avg_time:.1f}ms | {avg_energy:.4f}J | {avg_power:.1f}W")
    
    # Sonuçları kaydet
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"REAL_energy_benchmark_{timestamp}.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n{'='*70}")
    print(" 📊 ÖZET")
    print("="*70)
    print(f"\n✅ GERÇEK ENERJİ ÖLÇÜMÜ TAMAMLANDI!")
    print(f"📁 Sonuçlar: {filepath}")
    
    # Özet tablo
    print(f"\n{'Algoritma':<20} {'Boyut':<8} {'Süre(ms)':<12} {'Enerji(J)':<12} {'Güç(W)':<10}")
    print("-"*70)
    
    for b in results['benchmarks']:
        a = b['averages']
        print(f"{b['algorithm']:<20} {b['data_size']:<8} {a['execution_time_ms']:<12.2f} "
              f"{a['energy_joules']:<12.6f} {a['avg_power_watts']:<10.1f}")
    
    return results


if __name__ == '__main__':
    run_real_benchmark()
