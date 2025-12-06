"""
Gerçek Enerji Ölçümü Sayfası
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QSpinBox, QPushButton, QProgressBar,
    QTextEdit, QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor

import sys
import random
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gui.styles import Styles, Colors
from algorithms import ALGORITHMS

try:
    from real_power_meter import RealPowerMeter
    REAL_METER_AVAILABLE = True
except:
    REAL_METER_AVAILABLE = False


class RealMeasurementRunner(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    log = pyqtSignal(str)
    
    def __init__(self, algo_key, data_size, runs=3):
        super().__init__()
        self.algo_key = algo_key
        self.data_size = data_size
        self.runs = runs
        self._running = True
    
    def stop(self):
        self._running = False
    
    def run(self):
        try:
            # Find algorithm
            algo_info = None
            algo_cat = None
            for cat, algos in ALGORITHMS.items():
                if self.algo_key in algos:
                    algo_info = algos[self.algo_key]
                    algo_cat = cat
                    break
            
            if not algo_info:
                self.result.emit({'success': False, 'error': 'Algoritma bulunamadı'})
                return
            
            self.log.emit(f"🔋 Gerçek enerji ölçümü başlatılıyor...")
            self.log.emit(f"📊 Algoritma: {algo_info['name']}")
            self.log.emit(f"📏 Veri boyutu: {self.data_size:,}")
            
            if REAL_METER_AVAILABLE:
                meter = RealPowerMeter(sampling_interval_ms=50)
                is_real = meter.is_available()
            else:
                is_real = False
            
            if is_real:
                self.log.emit("✅ LibreHardwareMonitor bağlantısı kuruldu")
            else:
                self.log.emit("⚠️ Gerçek ölçüm yapılamıyor, tahmin modu")
            
            # Test data
            test_data = [random.randint(1, self.data_size * 10) for _ in range(self.data_size)]
            is_search = algo_cat == 'searching'
            if is_search:
                test_data = sorted(test_data)
                target = test_data[len(test_data) // 2]
            
            all_energy = []
            all_time = []
            all_power = []
            
            for i in range(self.runs):
                if not self._running:
                    return
                
                self.log.emit(f"\n🏃 Çalıştırma {i+1}/{self.runs}")
                data_copy = test_data.copy()
                
                if is_real:
                    def run_algo():
                        if is_search:
                            return algo_info['func'](data_copy, target)
                        return algo_info['func'](data_copy)
                    
                    measurement = meter.measure_function(
                        run_algo,
                        algorithm_name=self.algo_key,
                        data_size=self.data_size
                    )
                    
                    all_energy.append(measurement.energy_joules)
                    all_time.append(measurement.execution_time_ms)
                    all_power.append(measurement.avg_power_watts)
                    
                    self.log.emit(f"   ⚡ Enerji: {measurement.energy_joules:.6f} J")
                    self.log.emit(f"   🔌 Güç: {measurement.avg_power_watts:.2f} W")
                else:
                    # Estimation mode
                    start = time.perf_counter()
                    if is_search:
                        algo_info['func'](data_copy, target)
                    else:
                        algo_info['func'](data_copy)
                    end = time.perf_counter()
                    
                    exec_time = (end - start) * 1000
                    power = 25.0  # Estimated watts
                    energy = power * (exec_time / 1000)
                    
                    all_time.append(exec_time)
                    all_energy.append(energy)
                    all_power.append(power)
                    
                    self.log.emit(f"   ⏱️ Süre: {exec_time:.4f} ms")
                    self.log.emit(f"   ⚡ Tahmini enerji: {energy:.6f} J")
                
                self.progress.emit(int((i + 1) / self.runs * 100))
            
            # Results
            avg_time = sum(all_time) / len(all_time)
            avg_energy = sum(all_energy) / len(all_energy)
            avg_power = sum(all_power) / len(all_power)
            
            self.log.emit(f"\n{'='*40}")
            self.log.emit("✅ Ölçüm tamamlandı!")
            self.log.emit(f"📊 Ortalama süre: {avg_time:.4f} ms")
            self.log.emit(f"⚡ Ortalama enerji: {avg_energy:.6f} J")
            self.log.emit(f"🔌 Ortalama güç: {avg_power:.2f} W")
            
            self.result.emit({
                'success': True,
                'algorithm': algo_info['name'],
                'data_size': self.data_size,
                'is_real': is_real,
                'avg_time_ms': avg_time,
                'avg_energy_joules': avg_energy,
                'avg_power_watts': avg_power,
                'runs': self.runs
            })
            
        except Exception as e:
            self.log.emit(f"\n❌ Hata: {str(e)}")
            self.result.emit({'success': False, 'error': str(e)})


class RealEnergyPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.runner = None
        self.init_ui()
    
    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(Styles.PAGE_CONTAINER)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("🔋 Gerçek Enerji Ölçümü")
        header.setStyleSheet(Styles.LABEL_TITLE)
        
        subtitle = QLabel("LibreHardwareMonitor ile gerçek güç tüketimi ölçümü")
        subtitle.setStyleSheet(Styles.LABEL_SUBTITLE)
        
        layout.addWidget(header)
        layout.addWidget(subtitle)
        
        # Status card
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background: {'#d1fae5' if REAL_METER_AVAILABLE else '#fef3c7'};
                border-radius: 12px;
                border-left: 4px solid {'#10b981' if REAL_METER_AVAILABLE else '#f59e0b'};
            }}
        """)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(16, 16, 16, 16)
        
        status_icon = QLabel("✅" if REAL_METER_AVAILABLE else "⚠️")
        status_icon.setStyleSheet("font-size: 24px;")
        
        status_text = QLabel(
            "LibreHardwareMonitor hazır - Gerçek ölçüm yapılabilir" 
            if REAL_METER_AVAILABLE else 
            "LibreHardwareMonitor bulunamadı - Tahmin modu kullanılacak"
        )
        status_text.setStyleSheet("font-size: 14px; font-weight: 500;")
        
        status_layout.addWidget(status_icon)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        
        layout.addWidget(status_frame)
        
        # Config panel
        config = QFrame()
        config.setStyleSheet("QFrame { background: white; border-radius: 16px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        config.setGraphicsEffect(shadow)
        
        config_layout = QVBoxLayout(config)
        config_layout.setContentsMargins(24, 24, 24, 24)
        config_layout.setSpacing(16)
        
        config_title = QLabel("⚙️ Ölçüm Yapılandırması")
        config_title.setStyleSheet("font-size: 18px; font-weight: 600;")
        config_layout.addWidget(config_title)
        
        # Form
        form = QHBoxLayout()
        form.setSpacing(20)
        
        # Algorithm
        algo_layout = QVBoxLayout()
        algo_label = QLabel("Algoritma:")
        algo_label.setStyleSheet("font-weight: 600;")
        
        self.algo_combo = QComboBox()
        self.algo_combo.setStyleSheet(Styles.COMBOBOX)
        self.algo_combo.setMinimumWidth(250)
        
        categories = [
            ('sorting', '🔀'),
            ('searching', '🔍'),
            ('divide_conquer', '⚔️'),
            ('dynamic_programming', '🧩'),
            ('greedy', '🎲')
        ]
        
        for cat_key, icon in categories:
            for key, info in ALGORITHMS.get(cat_key, {}).items():
                self.algo_combo.addItem(f"{icon} {info['name']}", key)
        
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algo_combo)
        
        # Data size
        size_layout = QVBoxLayout()
        size_label = QLabel("Veri Boyutu:")
        size_label.setStyleSheet("font-weight: 600;")
        
        self.size_spin = QSpinBox()
        self.size_spin.setStyleSheet(Styles.INPUT_FIELD)
        self.size_spin.setRange(100, 50000)
        self.size_spin.setValue(1000)
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)
        
        # Runs
        runs_layout = QVBoxLayout()
        runs_label = QLabel("Çalıştırma:")
        runs_label.setStyleSheet("font-weight: 600;")
        
        self.runs_spin = QSpinBox()
        self.runs_spin.setStyleSheet(Styles.INPUT_FIELD)
        self.runs_spin.setRange(1, 10)
        self.runs_spin.setValue(3)
        
        runs_layout.addWidget(runs_label)
        runs_layout.addWidget(self.runs_spin)
        
        form.addLayout(algo_layout)
        form.addLayout(size_layout)
        form.addLayout(runs_layout)
        form.addStretch()
        
        config_layout.addLayout(form)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setStyleSheet(Styles.PROGRESS_BAR)
        self.progress.setVisible(False)
        config_layout.addWidget(self.progress)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🔋  Ölçümü Başlat")
        self.start_btn.setStyleSheet(Styles.BUTTON_SUCCESS)
        self.start_btn.setMinimumSize(180, 48)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_measurement)
        
        self.stop_btn = QPushButton("⏹️  Durdur")
        self.stop_btn.setStyleSheet(Styles.BUTTON_DANGER)
        self.stop_btn.setMinimumSize(100, 48)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_measurement)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        
        config_layout.addLayout(btn_layout)
        layout.addWidget(config)
        
        # Log panel
        log_frame = QFrame()
        log_frame.setStyleSheet("QFrame { background: white; border-radius: 16px; }")
        
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(20, 20, 20, 20)
        
        log_title = QLabel("📝 Ölçüm Logu")
        log_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #0f172a;
                color: #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
            }
        """)
        self.log_text.setMinimumHeight(250)
        self.log_text.append("🔋 Gerçek Enerji Ölçümü hazır.")
        self.log_text.append("📝 Bir algoritma seçin ve ölçümü başlatın.")
        
        log_layout.addWidget(log_title)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_frame)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def start_measurement(self):
        algo_key = self.algo_combo.currentData()
        if not algo_key:
            return
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        self.log_text.append(f"\n{'='*40}")
        
        self.runner = RealMeasurementRunner(
            algo_key, 
            self.size_spin.value(),
            self.runs_spin.value()
        )
        self.runner.progress.connect(self.progress.setValue)
        self.runner.log.connect(self.log_text.append)
        self.runner.result.connect(self.on_complete)
        self.runner.start()
    
    def stop_measurement(self):
        if self.runner:
            self.runner.stop()
            self.runner.wait()
        self.reset_ui()
        self.log_text.append("\n⏹️ Ölçüm durduruldu.")
    
    def on_complete(self, result):
        self.reset_ui()
    
    def reset_ui(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setVisible(False)
    
    def refresh(self):
        pass
