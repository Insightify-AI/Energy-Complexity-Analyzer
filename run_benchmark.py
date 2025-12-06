"""
Enerji Benchmark Scripti
========================
Bu script tüm algoritmaları çeşitli veri boyutlarında test eder
ve enerji tüketim sonuçlarını JSON formatında kaydeder.

Kullanım:
    python run_benchmark.py
    python run_benchmark.py --sizes 100,500,1000
    python run_benchmark.py --algorithms bubble_sort,merge_sort
    python run_benchmark.py --runs 5
"""

import sys
import os
import json
import random
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Modül yolunu ekle
sys.path.insert(0, str(Path(__file__).parent))

from energy_meter import EnergyMeter, get_system_info, EnergyResult
from algorithms import ALGORITHMS, AlgorithmMetrics


class EnergyBenchmark:
    """Enerji benchmark yöneticisi"""
    
    def __init__(self, output_dir: str = None):
        self.meter = EnergyMeter()
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / 'results'
        self.output_dir.mkdir(exist_ok=True)
        
        self.results = {
            'meta': {
                'timestamp': datetime.now().isoformat(),
                'system_info': get_system_info(),
                'measurement_method': self.meter.get_best_method()
            },
            'benchmarks': []
        }
    
    def generate_test_data(self, size: int) -> List[int]:
        """Test verisi oluştur"""
        # Çoğu algoritma için rastgele tam sayılar yeterli
        return [random.randint(1, size * 10) for _ in range(size)]
    
    def find_algorithm(self, name: str) -> Dict:
        """İsme göre algoritma bilgisini bul"""
        for cat, algos in ALGORITHMS.items():
            if name in algos:
                return algos[name]
        return None

    def run_algorithm_benchmark(self, algorithm_name: str, data: List[int], 
                               runs: int = 3) -> Dict:
        """Genel algoritma benchmark'ı çalıştır"""
        algo_info = self.find_algorithm(algorithm_name)
        if not algo_info:
            return {'error': f'Algoritma bulunamadı: {algorithm_name}'}
        
        all_results = []
        
        for run in range(runs):
            # Veri kopyası üzerinde çalış
            data_copy = data.copy()
            
            # Algoritmayı wrapper fonksiyon ile çağır
            def run_algorithm(arr):
                return algo_info['func'](arr)
            
            # Enerji ölçümü
            energy_result = self.meter.measure(
                algorithm_name=algorithm_name,
                func=run_algorithm,
                data=data_copy
            )
            
            # Metrik bilgilerini al (son çalıştırmadan)
            # Not: measure fonksiyonu zaten çalıştırdı ama metrikleri döndürmüyor olabilir
            # Bu yüzden tekrar çalıştırıp metrikleri alıyoruz (süreye dahil değil)
            _, metrics = algo_info['func'](data.copy())
            
            result = {
                'run': run + 1,
                'energy': energy_result.to_dict(),
                'metrics': {
                    'comparisons': metrics.comparisons,
                    'swaps': metrics.swaps,
                    'iterations': metrics.iterations,
                    'memory_accesses': metrics.memory_accesses,
                    'recursive_calls': metrics.recursive_calls,
                    'operations': metrics.operations
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
        avg_power = sum(r['energy']['power_watts'] for r in all_results) / runs
        
        return {
            'algorithm': algorithm_name,
            'data_size': len(data),
            'runs': runs,
            'results': all_results,
            'averages': {
                'energy_joules': avg_energy,
                'execution_time_ms': avg_time,
                'power_watts': avg_power
            }
        }
    
    def run_full_benchmark(self, sizes: List[int] = None, 
                           algorithms: List[str] = None,
                           runs: int = 3) -> Dict:
        """Tam benchmark çalıştır"""
        if sizes is None:
            sizes = [100, 500, 1000]
        
        print("\n" + "="*70)
        print(" 🔋 ENERJİ BENCHMARK - BAŞLIYOR")
        print("="*70)
        print(f"\n📊 Ölçüm Yöntemi: {self.meter.get_best_method()}")
        print(f"📏 Veri Boyutları: {sizes}")
        print(f"🔄 Çalıştırma Sayısı: {runs}")
        print()
        
        # Çalıştırılacak algoritmaları belirle
        target_algos = []
        if algorithms:
            target_algos = algorithms
        else:
            # Hepsi
            for cat in ALGORITHMS.values():
                target_algos.extend(cat.keys())
        
        for size in sizes:
            print(f"\n{'─'*70}")
            print(f" 📦 Veri Boyutu: {size}")
            print(f"{'─'*70}")
            
            # Test verisi oluştur
            test_data = self.generate_test_data(size)
            
            for algo_name in target_algos:
                algo_info = self.find_algorithm(algo_name)
                if not algo_info:
                    print(f"⚠️ Algoritma bulunamadı: {algo_name}")
                    continue
                    
                print(f"    ⏳ {algo_info['name']}...", end=" ", flush=True)
                
                try:
                    result = self.run_algorithm_benchmark(algo_name, test_data, runs)
                    
                    if 'error' in result:
                        print(f"❌ Hata: {result['error']}")
                        continue
                        
                    self.results['benchmarks'].append({
                        'type': algo_info['category'],
                        'size': size,
                        **result
                    })
                    
                    avg = result['averages']
                    print(f"✓ {avg['execution_time_ms']:.2f}ms | "
                          f"{avg['energy_joules']:.6f}J | "
                          f"{avg['power_watts']:.2f}W")
                          
                except Exception as e:
                    print(f"❌ Hata: {str(e)}")
        
        return self.results
    
    def save_results(self, filename: str = None) -> str:
        """Sonuçları JSON dosyasına kaydet"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"energy_benchmark_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Sonuçlar kaydedildi: {filepath}")
        return str(filepath)
    
    def save_summary(self) -> str:
        """Özet rapor oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f"energy_summary_{timestamp}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write(" ENERJİ BENCHMARK ÖZET RAPORU\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Tarih: {self.results['meta']['timestamp']}\n")
            f.write(f"Ölçüm Yöntemi: {self.results['meta']['measurement_method']}\n\n")
            
            # Algoritma bazında özet
            f.write("-"*70 + "\n")
            f.write(" ALGORİTMA KARŞILAŞTIRMASI (Ortalama Değerler)\n")
            f.write("-"*70 + "\n\n")
            
            f.write(f"{'Algoritma':<20} {'Boyut':<10} {'Süre(ms)':<15} "
                    f"{'Enerji(J)':<15} {'Güç(W)':<10}\n")
            f.write("-"*70 + "\n")
            
            for benchmark in self.results['benchmarks']:
                avg = benchmark['averages']
                f.write(f"{benchmark['algorithm']:<20} {benchmark['size']:<10} "
                        f"{avg['execution_time_ms']:<15.4f} "
                        f"{avg['energy_joules']:<15.9f} "
                        f"{avg['power_watts']:<10.2f}\n")
        
        print(f"✅ Özet rapor kaydedildi: {filepath}")
        return str(filepath)


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='Enerji Benchmark Scripti')
    parser.add_argument('--sizes', type=str, default='100,500,1000',
                        help='Test veri boyutları (virgülle ayrılmış)')
    parser.add_argument('--algorithms', type=str, default=None,
                        help='Test edilecek algoritmalar (virgülle ayrılmış)')
    parser.add_argument('--runs', type=int, default=3,
                        help='Her test için çalıştırma sayısı')
    parser.add_argument('--output', type=str, default=None,
                        help='Çıktı dizini')
    
    args = parser.parse_args()
    
    # Parametreleri parse et
    sizes = [int(s.strip()) for s in args.sizes.split(',')]
    algorithms = [a.strip() for a in args.algorithms.split(',')] if args.algorithms else None
    
    # Benchmark'ı çalıştır
    benchmark = EnergyBenchmark(output_dir=args.output)
    benchmark.run_full_benchmark(sizes=sizes, algorithms=algorithms, runs=args.runs)
    
    # Sonuçları kaydet
    benchmark.save_results()
    benchmark.save_summary()
    
    print("\n" + "="*70)
    print(" 🎉 BENCHMARK TAMAMLANDI!")
    print("="*70)


if __name__ == '__main__':
    main()
