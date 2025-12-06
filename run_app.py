"""
Algoritma Analizi Platformu - Başlatıcı
=======================================
Modern PyQt5 Dashboard Uygulaması

Gereksinimler:
    pip install PyQt5 matplotlib
"""

import sys
import os
import warnings

# Matplotlib font uyarılarını sustur
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Modül yolunu düzelt
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def check_dependencies():
    """Bağımlılıkları kontrol et"""
    missing = []
    
    try:
        import PyQt5
    except ImportError:
        missing.append("PyQt5")
    
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")
    
    if missing:
        print("=" * 50)
        print("[X] Eksik bagimliliklar tespit edildi!")
        print("=" * 50)
        print("\nAşağıdaki paketleri yükleyin:")
        print(f"    pip install {' '.join(missing)}")
        print("\nTam kurulum için:")
        print("    pip install PyQt5 matplotlib")
        print("=" * 50)
        return False
    
    return True


def main():
    """Ana uygulama başlatıcısı"""
    # Windows console encoding fix
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 50)
    print("[*] Algoritma Analizi Platformu")
    print("    Python Edition v2.0")
    print("=" * 50)
    
    # Bağımlılıkları kontrol et
    if not check_dependencies():
        sys.exit(1)
    
    print("\n[OK] Bagimliliklar kontrol edildi")
    print("[...] Uygulama baslatiliyor...\n")
    
    # PyQt5'i import et
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    
    # GUI modülünü import et
    from gui.main_window import MainWindow
    
    # High DPI desteği - Ölçekleme sorununu çözmek için
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Ortam değişkeni ile ölçeklemeyi zorla (gerekirse)
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Uygulama oluştur
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Font ayarı
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Uygulama bilgileri
    app.setApplicationName("Algoritma Analizi Platformu")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Algorithm Analysis")
    
    # Ana pencere
    window = MainWindow()
    window.show()
    
    print("[OK] Uygulama baslatildi!")
    print("[*] Dashboard acildi.\n")
    
    # Olay döngüsü
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
