"""
LibreHardwareMonitor Enerji Ölçümü Test Scripti
============================================
Bu script LibreHardwareMonitor'un WMI arayüzünü kullanarak
gerçek CPU güç tüketimini okur.

ÖNEMLİ: LibreHardwareMonitor'un açık ve çalışır durumda olması gerekir!
"""

import sys
import time
from datetime import datetime

def test_libre_hardware_monitor():
    """LibreHardwareMonitor WMI bağlantısını test et"""
    
    print("="*70)
    print(" 🔍 LibreHardwareMonitor Bağlantı Testi")
    print("="*70)
    
    # WMI modülünü kontrol et
    print("\n1. WMI modülü kontrol ediliyor...")
    try:
        import wmi
        print("   ✅ WMI modülü yüklü")
    except ImportError:
        print("   ❌ WMI modülü yüklü değil. Kurun: pip install wmi pywin32")
        return False
    
    # LibreHardwareMonitor namespace kontrol et
    print("\n2. LibreHardwareMonitor WMI namespace kontrol ediliyor...")
    try:
        w = wmi.WMI(namespace="root\\LibreHardwareMonitor")
        print("   ✅ LibreHardwareMonitor WMI namespace bulundu!")
    except Exception as e:
        # OpenHardwareMonitor namespace dene
        try:
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            print("   ✅ OpenHardwareMonitor WMI namespace bulundu!")
        except:
            print("   ❌ LibreHardwareMonitor WMI namespace BULUNAMADI!")
            print("\n   ⚠️  LibreHardwareMonitor uygulaması çalışıyor mu?")
            print("   ⚠️  Yönetici olarak çalıştırdığınızdan emin olun.")
            print("\n   Hata detayı:", str(e)[:100])
            return False
    
    # Sensörleri listele
    print("\n3. Sensörler okunuyor...")
    try:
        sensors = w.Sensor()
        
        power_sensors = []
        temp_sensors = []
        other_sensors = []
        
        for sensor in sensors:
            sensor_info = {
                'name': sensor.Name,
                'value': sensor.Value,
                'type': sensor.SensorType,
                'parent': sensor.Parent if hasattr(sensor, 'Parent') else 'N/A'
            }
            
            if sensor.SensorType == 'Power':
                power_sensors.append(sensor_info)
            elif sensor.SensorType == 'Temperature':
                temp_sensors.append(sensor_info)
            else:
                other_sensors.append(sensor_info)
        
        print(f"\n   📊 Toplam {len(sensors)} sensör bulundu:")
        
        # Güç sensörlerini göster
        print("\n   ⚡ GÜÇ SENSÖRLERİ (Power):")
        if power_sensors:
            for s in power_sensors:
                print(f"      • {s['name']}: {s['value']:.2f} W")
        else:
            print("      (Güç sensörü bulunamadı)")
        
        # Sıcaklık sensörlerini göster
        print("\n   🌡️  SICAKLIK SENSÖRLERİ (Temperature):")
        if temp_sensors:
            for s in temp_sensors[:5]:  # İlk 5'ini göster
                print(f"      • {s['name']}: {s['value']:.1f} °C")
            if len(temp_sensors) > 5:
                print(f"      ... ve {len(temp_sensors) - 5} sensör daha")
        else:
            print("      (Sıcaklık sensörü bulunamadı)")
        
        # Gerçek ölçüm mümkün mü?
        print("\n" + "="*70)
        if power_sensors:
            print(" ✅ GERÇEK ENERJİ ÖLÇÜMÜ: MÜMKÜN!")
            print("="*70)
            print("\n   LibreHardwareMonitor üzerinden gerçek güç değerleri")
            print("   okunabilir durumda.")
            return True
        else:
            print(" ⚠️  GERÇEK ENERJİ ÖLÇÜMÜ: GÜÇ SENSÖRLERİ YOK")
            print("="*70)
            print("\n   CPU'nuz güç sensörü raporlamıyor olabilir.")
            print("   Sadece tahmin modeli kullanılabilir.")
            return False
            
    except Exception as e:
        print(f"   ❌ Sensör okuma hatası: {e}")
        return False


def measure_power_sample():
    """Anlık güç ölçümü örneği"""
    print("\n" + "="*70)
    print(" 🔋 ANLİK GÜÇ ÖLÇÜMÜ ÖRNEĞİ")
    print("="*70)
    
    try:
        import wmi
        
        # Namespace'i bul
        try:
            w = wmi.WMI(namespace="root\\LibreHardwareMonitor")
        except:
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        
        print("\n   5 saniye boyunca güç değerleri okunuyor...")
        print("   " + "-"*50)
        
        samples = []
        for i in range(5):
            sensors = w.Sensor()
            
            for sensor in sensors:
                if sensor.SensorType == 'Power' and 'Package' in sensor.Name:
                    power = sensor.Value
                    samples.append(power)
                    print(f"   [{i+1}] CPU Package Power: {power:.2f} W")
                    break
            
            time.sleep(1)
        
        if samples:
            print("\n   " + "-"*50)
            print(f"   📊 Ortalama Güç: {sum(samples)/len(samples):.2f} W")
            print(f"   📊 Maksimum Güç: {max(samples):.2f} W")
            print(f"   📊 Minimum Güç: {min(samples):.2f} W")
            
    except Exception as e:
        print(f"   ❌ Ölçüm hatası: {e}")


if __name__ == '__main__':
    success = test_libre_hardware_monitor()
    
    if success:
        measure_power_sample()
    
    print("\n" + "="*70)
    print(" TEST TAMAMLANDI")
    print("="*70)
