"""
Test Çalıştırıcı Sayfası
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QCheckBox, QSpinBox, QPushButton, QProgressBar,
    QTextEdit, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from gui.styles import Styles, Colors
from algorithms import ALGORITHMS
from run_benchmark import EnergyBenchmark

class BenchmarkWorker(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(str)
    
    def __init__(self, sizes, algorithms, runs):
        super().__init__()
        self.sizes = sizes
        self.algorithms = algorithms
        self.runs = runs
        
    def run(self):
        try:
            self.log.emit("🚀 Benchmark başlatılıyor...")
            benchmark = EnergyBenchmark()
            
            # Capture stdout to emit logs
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                results = benchmark.run_full_benchmark(
                    sizes=self.sizes,
                    algorithms=self.algorithms,
                    runs=self.runs
                )
                json_path = benchmark.save_results()
                benchmark.save_summary()
            
            self.log.emit(f.getvalue())
            self.finished.emit(json_path)
            
        except Exception as e:
            self.log.emit(f"❌ Hata: {str(e)}")
            self.finished.emit("")

class TestRunnerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
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
        header = QLabel("🚀 Test Çalıştırıcı")
        header.setStyleSheet(Styles.LABEL_TITLE)
        
        subtitle = QLabel("Yeni performans testleri çalıştırın ve sonuçları kaydedin")
        subtitle.setStyleSheet(Styles.LABEL_SUBTITLE)
        
        layout.addWidget(header)
        layout.addWidget(subtitle)
        
        # Config Card
        card = QFrame()
        card.setStyleSheet(Styles.CARD)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        
        # Algorithms Selection
        algo_group = QGroupBox("Algoritmalar")
        algo_group.setStyleSheet(f"QGroupBox {{ color: {Colors.TEXT_MAIN}; font-weight: bold; border: 1px solid {Colors.BORDER}; border-radius: 8px; margin-top: 12px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; }}")
        algo_layout = QGridLayout()
        
        self.algo_checks = []
        row = 0
        col = 0
        for cat, algos in ALGORITHMS.items():
            cat_label = QLabel(cat.replace('_', ' ').title())
            cat_label.setStyleSheet(f"color: {Colors.ACCENT}; font-weight: bold;")
            algo_layout.addWidget(cat_label, row, 0, 1, 2)
            row += 1
            col = 0
            for key, info in algos.items():
                chk = QCheckBox(info['name'])
                chk.setProperty('algo_key', key)
                chk.setStyleSheet(f"color: {Colors.TEXT_MAIN};")
                algo_layout.addWidget(chk, row, col)
                self.algo_checks.append(chk)
                col += 1
                if col > 2:
                    col = 0
                    row += 1
            if col != 0:
                row += 1
                
        algo_group.setLayout(algo_layout)
        card_layout.addWidget(algo_group)
        
        # Settings
        settings_layout = QHBoxLayout()
        
        # Sizes
        size_layout = QVBoxLayout()
        size_label = QLabel("Veri Boyutları (virgülle ayırın):")
        self.size_input = QTextEdit()
        self.size_input.setPlaceholderText("100, 500, 1000")
        self.size_input.setText("100, 500, 1000")
        self.size_input.setMaximumHeight(40)
        self.size_input.setStyleSheet(Styles.INPUT_FIELD)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_input)
        settings_layout.addLayout(size_layout)
        
        # Runs
        runs_layout = QVBoxLayout()
        runs_label = QLabel("Tekrar Sayısı:")
        self.runs_spin = QSpinBox()
        self.runs_spin.setRange(1, 10)
        self.runs_spin.setValue(3)
        self.runs_spin.setStyleSheet(Styles.INPUT_FIELD)
        runs_layout.addWidget(runs_label)
        runs_layout.addWidget(self.runs_spin)
        settings_layout.addLayout(runs_layout)
        
        card_layout.addLayout(settings_layout)
        
        # Run Button
        self.run_btn = QPushButton("🚀 Testi Başlat")
        self.run_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.run_btn.clicked.connect(self.start_test)
        card_layout.addWidget(self.run_btn)
        
        layout.addWidget(card)
        
        # Progress & Log
        self.progress = QProgressBar()
        self.progress.setStyleSheet(Styles.PROGRESS_BAR)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(Styles.LOG_TEXT)
        self.log_text.setMinimumHeight(200)
        layout.addWidget(self.log_text)
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def start_test(self):
        # Get selected algorithms
        selected_algos = [chk.property('algo_key') for chk in self.algo_checks if chk.isChecked()]
        if not selected_algos:
            self.log_text.append("⚠️ Lütfen en az bir algoritma seçin!")
            return
            
        # Get sizes
        try:
            sizes = [int(s.strip()) for s in self.size_input.toPlainText().split(',')]
        except:
            self.log_text.append("⚠️ Geçersiz veri boyutu formatı!")
            return
            
        runs = self.runs_spin.value()
        
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0) # Indeterminate
        self.log_text.clear()
        
        self.worker = BenchmarkWorker(sizes, selected_algos, runs)
        self.worker.log.connect(self.log_text.append)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def on_finished(self, json_path):
        self.run_btn.setEnabled(True)
        self.progress.setVisible(False)
        if json_path:
            self.log_text.append(f"\n✅ Test tamamlandı! Sonuçlar kaydedildi: {json_path}")
