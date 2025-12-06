"""
GERÇEK ENERJİ BENCHMARK
=======================
Intel Power Gadget kullanarak GERÇEK enerji ölçümü yapan benchmark scripti.

KULLANIM:
    python run_real_benchmark.py
    python run_real_benchmark.py --sizes 100,500,1000
    python run_real_benchmark.py --algorithms bubble_sort,quick_sort
"""

import sys
import os
import json
import random
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Modül yolunu ekle
sys.path.insert(0, str(Path(__file__).parent))

from real_energy_meter import RealEnergyMeter, RealEnergyResult, check_system_status
from algorithms import ALGORITHMS, AlgorithmMetrics


class RealEnergyBenchmark:
    """Gerçek enerji benchmark yöneticisi"""
    
    def __init__(self, output_dir: str = None):
        self.meter = RealEnergyMeter()
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / 'results'
        self.output_dir.mkdir(exist_ok=True)
        
        self.results = {
            'meta': {
                'timestamp': datetime.now().isoformat(),
                'measurement_status': self.meter.get_status(),
                'is_real_measurement': self.meter.is_available(),
                'measurement_method': self.meter.get_method()
            },
            'benchmarks': []
        }
    
    def generate_test_data(self, size: int, data_type: str = 'random') -> List[int]:
        """Test verisi oluştur"""
        if data_type == 'random':
            return [random.randint(1, size * 10) for _ in range(size)]
        elif data_type == 'sorted':
            return list(range(size))
        elif data_type == 'reverse':
            return list(range(size, 0, -1))
        else:
            return [random.randint(1, size * 10) for _ in range(size)]
    
    def run_sorting_benchmark(self, algorithm_name: str, data: List[int], 
                              runs: int = 3) -> Dict:
        """Sıralama algoritması benchmark'ı"""
        algo_info = ALGORITHMS['sorting'].get(algorithm_name)
        if not algo_info:
            return {'error': f'Algoritma bulunamadı: {algorithm_name}'}
        
        all_results = []
        
        for run in range(runs):
            # Algoritmayı wrapper ile çağır
            data_copy = data.copy()
            
            def run_algorithm():
                return algo_info['func'](data_copy)
            
            # GERÇEK enerji ölçümü
            energy_result = self.meter.measure(
                run_algorithm,
                algorithm_name=algorithm_name,
                data_size=len(data)
            )
            
            # Metrikleri al
            _, metrics = algo_info['func'](data.copy())
            
            result = {
                'run': run + 1,
                'energy': energy_result.to_dict(),
                'metrics': {
                    'comparisons': metrics.comparisons,
                    'swaps': metrics.swaps,
                    'iterations': metrics.iterations,
                    'memory_accesses': metrics.memory_accesses,
                    'recursive_calls': metrics.recursive_calls
                },
                'algorithm_info': {
                    'name': algo_info['name'],
                    'complexity_time': algo_info['complexity_time'],
                    'complexity_space': algo_info['complexity_space'],
                    'category': algo_info['category']
                }
            }
            
            all_results.append(result)
        
        # Ortalamaları hesapla
        avg_energy = sum(r['energy']['energy_joules'] for r in all_results) / runs
        avg_time = sum(r['energy']['execution_time_ms'] for r in all_results) / runs
        avg_power = sum(r['energy']['avg_power_watts'] for r in all_results) / runs
        avg_max_power = sum(r['energy']['max_power_watts'] for r in all_results) / runs
        
        return {
            'algorithm': algorithm_name,
            'data_size': len(data),
            'runs': runs,
            'is_real_measurement': all_results[0]['energy']['is_real_measurement'],
            'results': all_results,
            'averages': {
                'energy_joules': avg_energy,
                'execution_time_ms': avg_time,
                'avg_power_watts': avg_power,
                'max_power_watts': avg_max_power
            }
        }
    
    def run_search_benchmark(self, algorithm_name: str, data: List[int],
                             runs: int = 3) -> Dict:
        """Arama algoritması benchmark'ı"""
        algo_info = ALGORITHMS['searching'].get(algorithm_name)
        if not algo_info:
            return {'error': f'Algoritma bulunamadı: {algorithm_name}'}
        
        sorted_data = sorted(data)
        target = sorted_data[len(sorted_data) // 2]
        
        all_results = []
        
        for run in range(runs):
            def run_algorithm():
                return algo_info['func'](sorted_data, target)
            
            # GERÇEK enerji ölçümü
            energy_result = self.meter.measure(
                run_algorithm,
                algorithm_name=algorithm_name,
                data_size=len(data)
            )
            
            _, metrics = algo_info['func'](sorted_data, target)
            
            result = {
                'run': run + 1,
                'energy': energy_result.to_dict(),
                'metrics': {
                    'comparisons': metrics.comparisons,
                    'iterations': metrics.iterations,
                    'memory_accesses': metrics.memory_accesses
                },
                'algorithm_info': {
                    'name': algo_info['name'],
                    'complexity_time': algo_info['complexity_time'],
                    'complexity_space': algo_info['complexity_space']
                }
            }
            
            all_results.append(result)
        
        avg_energy = sum(r['energy']['energy_joules'] for r in all_results) / runs
        avg_time = sum(r['energy']['execution_time_ms'] for r in all_results) / runs
        avg_power = sum(r['energy']['avg_power_watts'] for r in all_results) / runs
        
        return {
            'algorithm': algorithm_name,
            'data_size': len(data),
            'runs': runs,
            'is_real_measurement': all_results[0]['energy']['is_real_measurement'],
            'results': all_results,
            'averages': {
                'energy_joules': avg_energy,
                'execution_time_ms': avg_time,
                'avg_power_watts': avg_power
            }
        }
    
    def run_full_benchmark(self, sizes: List[int] = None, 
                           algorithms: List[str] = None,
                           runs: int = 3) -> Dict:
        """Tam benchmark çalıştır"""
        if sizes is None:
            sizes = [100, 500, 1000, 2000, 5000]
        
        print("\n" + "="*70)
        print(" 🔋 GERÇEK ENERJİ BENCHMARK - BAŞLIYOR")
        print("="*70)
        
        # Sistem durumunu kontrol et
        if not self.meter.is_available():
            print("\n" + "!"*70)
            print(" ⚠️  UYARI: Intel Power Gadget bulunamadı!")
            print(" ⚠️  Gerçek enerji ölçümü yapılamayacak.")
            print(" ⚠️  Lütfen Intel Power Gadget'ı kurun:")
            print("     https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html")
            print("!"*70)
            return self.results
        
        print(f"\n✅ Ölçüm Yöntemi: {self.meter.get_method()}")
        print(f"✅ Gerçek Ölçüm: EVET")
        print(f"📏 Veri Boyutları: {sizes}")
        print(f"🔄 Çalıştırma Sayısı: {runs}")
        print()
        
        sorting_algos = algorithms or list(ALGORITHMS['sorting'].keys())
        search_algos = algorithms or list(ALGORITHMS['searching'].keys())
        
        if algorithms:
            sorting_algos = [a for a in algorithms if a in ALGORITHMS['sorting']]
            search_algos = [a for a in algorithms if a in ALGORITHMS['searching']]
        
        for size in sizes:
            print(f"\n{'─'*70}")
            print(f" 📦 Veri Boyutu: {size}")
            print(f"{'─'*70}")
            
            test_data = self.generate_test_data(size)
            
            # Sıralama algoritmaları
            if sorting_algos:
                print("\n  🔢 Sıralama Algoritmaları:")
                for algo_name in sorting_algos:
                    print(f"    ⏳ {algo_name}...", end=" ", flush=True)
                    
                    result = self.run_sorting_benchmark(algo_name, test_data, runs)
                    self.results['benchmarks'].append({
                        'type': 'sorting',
                        'size': size,
                        **result
                    })
                    
                    avg = result['averages']
                    real = "✅" if result.get('is_real_measurement') else "❌"
                    print(f"{real} {avg['execution_time_ms']:.2f}ms | "
                          f"{avg['energy_joules']:.6f}J | "
                          f"{avg['avg_power_watts']:.2f}W")
            
            # Arama algoritmaları
            if search_algos:
                print("\n  🔍 Arama Algoritmaları:")
                for algo_name in search_algos:
                    print(f"    ⏳ {algo_name}...", end=" ", flush=True)
                    
                    result = self.run_search_benchmark(algo_name, test_data, runs)
                    self.results['benchmarks'].append({
                        'type': 'searching',
                        'size': size,
                        **result
                    })
                    
                    avg = result['averages']
                    real = "✅" if result.get('is_real_measurement') else "❌"
                    print(f"{real} {avg['execution_time_ms']:.4f}ms | "
                          f"{avg['energy_joules']:.9f}J | "
                          f"{avg['avg_power_watts']:.2f}W")
        
        return self.results
    
    def save_results(self, filename: str = None) -> str:
        """Sonuçları kaydet"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            real_tag = "_REAL" if self.results['meta']['is_real_measurement'] else "_EST"
            filename = f"energy_benchmark{real_tag}_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Sonuçlar kaydedildi: {filepath}")
        return str(filepath)
    
    def print_summary(self):
        """Özet tablo yazdır"""
        print("\n" + "="*70)
        print(" 📊 ÖZET TABLO")
        print("="*70)
        
        is_real = self.results['meta']['is_real_measurement']
        print(f"\n{'⚡ GERÇEK ÖLÇÜM' if is_real else '📐 TAHMİN'}")
        print()
        
        print(f"{'Algoritma':<20} {'Boyut':<8} {'Süre(ms)':<12} "
              f"{'Enerji(J)':<15} {'Güç(W)':<10}")
        print("-"*70)
        
        for benchmark in self.results['benchmarks']:
            avg = benchmark['averages']
            print(f"{benchmark['algorithm']:<20} {benchmark['size']:<8} "
                  f"{avg['execution_time_ms']:<12.4f} "
                  f"{avg['energy_joules']:<15.9f} "
                  f"{avg['avg_power_watts']:<10.2f}")


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='Gerçek Enerji Benchmark')
    parser.add_argument('--sizes', type=str, default='100,500,1000,2000',
                        help='Veri boyutları')
    parser.add_argument('--algorithms', type=str, default=None,
                        help='Algoritmalar')
    parser.add_argument('--runs', type=int, default=3,
                        help='Çalıştırma sayısı')
    parser.add_argument('--check', action='store_true',
                        help='Sadece sistem kontrolü yap')
    
    args = parser.parse_args()
    
    # Sadece kontrol
    if args.check:
        check_system_status()
        return
    
    # Benchmark çalıştır
    sizes = [int(s.strip()) for s in args.sizes.split(',')]
    algorithms = [a.strip() for a in args.algorithms.split(',')] if args.algorithms else None
    
    benchmark = RealEnergyBenchmark()
    
    if not benchmark.meter.is_available():
        print("\n❌ HATA: Gerçek enerji ölçümü için Intel Power Gadget gerekli!")
        print("\n📥 İndirme Linki:")
        print("   https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html")
        print("\n📋 Kurulum Adımları:")
        print("   1. Yukarıdaki linkten indirin")
        print("   2. PowerGadget.msi dosyasını çalıştırın")
        print("   3. Kurulumu tamamlayın")
        print("   4. Bu scripti tekrar çalıştırın")
        return
    
    benchmark.run_full_benchmark(sizes=sizes, algorithms=algorithms, runs=args.runs)
    benchmark.save_results()
    benchmark.print_summary()
    
    print("\n" + "="*70)
    print(" 🎉 GERÇEK ENERJİ BENCHMARK TAMAMLANDI!")
    print("="*70)


if __name__ == '__main__':
    main()
