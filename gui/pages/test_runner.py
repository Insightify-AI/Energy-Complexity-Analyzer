"""
Test Çalıştırıcı Sayfası - Profesyonel Tasarım
"""

import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QCheckBox, QSpinBox, QPushButton, QProgressBar,
    QTextEdit, QGridLayout, QComboBox, QLineEdit, QGraphicsDropShadowEffect,
    QButtonGroup, QRadioButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont

from gui.styles import Colors
from algorithms import ALGORITHMS
from run_benchmark import EnergyBenchmark

# Matplotlib
try:
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
    
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Türkçe isimler
TYPES = {
    'divide_conquer': {'name': 'Böl ve Yönet', 'icon': '🔀', 'color': '#4CC9F0'},
    'dynamic_programming': {'name': 'Dinamik Programlama', 'icon': '📊', 'color': '#F72585'},
    'greedy': {'name': 'Açgözlü', 'icon': '🎯', 'color': '#4361EE'}
}


class BenchmarkWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int, str)  # current, total, current_algo
    done_signal = pyqtSignal(str, dict)
    
    def __init__(self, sizes, algos, runs):
        super().__init__()
        self.sizes = sizes
        self.algos = algos
        self.runs = runs
        self._is_running = True
        
    def run(self):
        path = ""
        results = {}
        
        try:
            self.log_signal.emit("Test baslatiliyor...")
            
            total_steps = len(self.sizes) * len(self.algos) * self.runs
            current_step = 0
            
            # EnergyBenchmark kullanarak test yap
            from run_benchmark import EnergyBenchmark
            bm = EnergyBenchmark()
            
            # Her algoritma için bilgi ver
            for algo_key in self.algos:
                self.log_signal.emit(f"\n[*] {algo_key} algoritmasi...")
                for size in self.sizes:
                    for r in range(self.runs):
                        if not self._is_running:
                            return
                        current_step += 1
                        self.progress_signal.emit(current_step, total_steps, algo_key)
            
            # Benchmark'ı çalıştır
            self.log_signal.emit("\n[...] Benchmark calistiriliyor...")
            
            try:
                results = bm.run_full_benchmark(
                    sizes=self.sizes,
                    algorithms=self.algos,
                    runs=self.runs
                )
                
                if results:
                    path = bm.save_results()
                    bm.save_summary()
                    self.log_signal.emit(f"\n[OK] Testler tamamlandi!")
                    self.log_signal.emit(f"[>] Sonuc: {path}")
                else:
                    self.log_signal.emit("\n[!] Sonuc alinamadi")
                    
            except Exception as e:
                self.log_signal.emit(f"\n[X] Benchmark hatasi: {str(e)}")
                import traceback
                self.log_signal.emit(traceback.format_exc())
                
        except Exception as e:
            self.log_signal.emit(f"[X] Genel hata: {str(e)}")
        
        self.done_signal.emit(path, results if results else {})
    
    def stop(self):
        self._is_running = False


class TestRunnerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.selected_type = None
        self.algo_checkboxes = []
        self.results_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        # SCROLL AREA
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: {Colors.BG_DARK};
            }}
            QScrollBar:vertical {{
                background: {Colors.BG_DARKER};
                width: 8px;
                border-radius: 4px;
                margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {Colors.BORDER};
                border-radius: 4px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Colors.ACCENT};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        
        # CONTENT
        content = QWidget()
        content.setStyleSheet(f"background: {Colors.BG_DARK};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(50, 40, 50, 50)
        layout.setSpacing(30)
        
        # === HEADER ===
        header = QLabel("Test Çalıştırıcı")
        header.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {Colors.TEXT_MAIN};
        """)
        layout.addWidget(header)
        
        desc = QLabel("Algoritma performanslarını test edin ve karşılaştırın")
        desc.setStyleSheet(f"font-size: 15px; color: {Colors.TEXT_MUTED}; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # === MAIN GRID ===
        main_grid = QHBoxLayout()
        main_grid.setSpacing(24)
        
        # LEFT COLUMN - Configuration
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        
        # -- Algorithm Type Selection --
        type_card = self._create_card("Algoritma Türü Seçin")
        type_layout = QVBoxLayout()
        type_layout.setSpacing(12)
        
        self.type_buttons = {}
        for key, info in TYPES.items():
            btn = QPushButton(f"{info['icon']}  {info['name']}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)
            btn.setStyleSheet(self._type_btn_style(info['color']))
            btn.clicked.connect(lambda checked, k=key: self.select_type(k))
            self.type_buttons[key] = btn
            type_layout.addWidget(btn)
        
        type_card.layout().addLayout(type_layout)
        left_col.addWidget(type_card)
        
        # -- Algorithms Selection --
        self.algo_card = self._create_card("Algoritmalar")
        self.algo_container = QVBoxLayout()
        self.algo_container.setSpacing(8)
        
        self.algo_placeholder = QLabel("Önce yukarıdan bir tür seçin")
        self.algo_placeholder.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 13px;
            padding: 30px;
            background: {Colors.BG_DARKER};
            border-radius: 8px;
        """)
        self.algo_placeholder.setAlignment(Qt.AlignCenter)
        self.algo_container.addWidget(self.algo_placeholder)
        
        self.algo_card.layout().addLayout(self.algo_container)
        
        # Quick buttons
        quick_row = QHBoxLayout()
        quick_row.setSpacing(8)
        
        self.sel_all_btn = QPushButton("Tümünü Seç")
        self.sel_all_btn.setStyleSheet(self._small_btn_style(Colors.ACCENT))
        self.sel_all_btn.clicked.connect(self.select_all)
        self.sel_all_btn.setEnabled(False)
        
        self.clr_btn = QPushButton("Temizle")
        self.clr_btn.setStyleSheet(self._small_btn_style(Colors.DANGER))
        self.clr_btn.clicked.connect(self.clear_all)
        self.clr_btn.setEnabled(False)
        
        quick_row.addWidget(self.sel_all_btn)
        quick_row.addWidget(self.clr_btn)
        quick_row.addStretch()
        self.algo_card.layout().addLayout(quick_row)
        
        left_col.addWidget(self.algo_card)
        
        # -- Test Parameters --
        param_card = self._create_card("Test Parametreleri")
        param_grid = QGridLayout()
        param_grid.setSpacing(16)
        param_grid.setColumnStretch(1, 1)
        
        # Sizes
        size_lbl = QLabel("Veri Boyutları:")
        size_lbl.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-size: 13px;")
        self.size_input = QLineEdit("100, 500, 1000")
        self.size_input.setStyleSheet(self._input_style())
        self.size_input.setPlaceholderText("100, 500, 1000")
        
        param_grid.addWidget(size_lbl, 0, 0)
        param_grid.addWidget(self.size_input, 0, 1)
        
        # Runs
        runs_lbl = QLabel("Tekrar Sayısı:")
        runs_lbl.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-size: 13px;")
        self.runs_input = QSpinBox()
        self.runs_input.setRange(1, 10)
        self.runs_input.setValue(3)
        self.runs_input.setStyleSheet(self._input_style())
        
        param_grid.addWidget(runs_lbl, 1, 0)
        param_grid.addWidget(self.runs_input, 1, 1)
        
        param_card.layout().addLayout(param_grid)
        left_col.addWidget(param_card)
        
        # -- Run Button --
        self.run_btn = QPushButton("▶  TESTİ BAŞLAT")
        self.run_btn.setFixedHeight(52)
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 #7C3AED);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7BFF, stop:1 #9B5CF7);
            }}
            QPushButton:disabled {{
                background: {Colors.BORDER};
                color: {Colors.TEXT_MUTED};
            }}
        """)
        self.run_btn.clicked.connect(self.run_test)
        left_col.addWidget(self.run_btn)
        
        # Progress Area
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 10, 0, 0)
        progress_layout.setSpacing(8)
        
        # Status Label
        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 12px;
            font-weight: 500;
        """)
        progress_layout.addWidget(self.status_label)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(12)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p%")
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background: {Colors.BG_DARKER};
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 10px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.ACCENT}, stop:0.5 {Colors.PRIMARY}, stop:1 #7C3AED);
                border-radius: 6px;
            }}
        """)
        self.progress.setValue(0)
        progress_layout.addWidget(self.progress)
        
        # Current Algorithm Label
        self.current_algo_label = QLabel("")
        self.current_algo_label.setStyleSheet(f"""
            color: {Colors.ACCENT};
            font-size: 11px;
        """)
        progress_layout.addWidget(self.current_algo_label)
        
        self.progress_container.hide()
        left_col.addWidget(self.progress_container)
        
        left_col.addStretch()
        
        # RIGHT COLUMN - Results
        right_col = QVBoxLayout()
        right_col.setSpacing(20)
        
        # -- Results Header --
        results_header = QHBoxLayout()
        results_title = QLabel("📊 Sonuçlar")
        results_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Colors.ACCENT};")
        results_header.addWidget(results_title)
        results_header.addStretch()
        
        self.chart_combo = QComboBox()
        self.chart_combo.addItem("Süre (ms)", "time")
        self.chart_combo.addItem("Enerji (J)", "energy")
        self.chart_combo.addItem("Bellek (KB)", "memory")
        self.chart_combo.setStyleSheet(f"""
            QComboBox {{
                background: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 120px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {Colors.ACCENT};
            }}
            QComboBox QAbstractItemView {{
                background: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
                selection-background-color: {Colors.ACCENT};
            }}
        """)
        self.chart_combo.currentIndexChanged.connect(self.refresh_chart)
        results_header.addWidget(self.chart_combo)
        
        right_col.addLayout(results_header)
        
        # -- Chart Area --
        self.chart_card = self._create_card(None)
        self.chart_card.setMinimumHeight(320)
        
        chart_layout = QVBoxLayout()
        
        if HAS_MATPLOTLIB:
            plt.style.use('dark_background')
            self.figure = Figure(figsize=(8, 4), facecolor='#151922')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background: transparent;")
            chart_layout.addWidget(self.canvas)
            
            # Initial empty state
            self._show_empty_chart()
        else:
            no_mp = QLabel("Grafik için matplotlib gerekli")
            no_mp.setStyleSheet(f"color: {Colors.TEXT_MUTED}; padding: 60px;")
            no_mp.setAlignment(Qt.AlignCenter)
            chart_layout.addWidget(no_mp)
        
        self.chart_card.layout().addLayout(chart_layout)
        right_col.addWidget(self.chart_card)
        
        # -- Log Area --
        log_card = self._create_card("Çalışma Logu")
        log_card.setMinimumHeight(200)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background: {Colors.BG_DARKER};
                color: {Colors.ACCENT};
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        self.log_text.setPlaceholderText("Test sonuçları burada görünecek...")
        log_card.layout().addWidget(self.log_text)
        right_col.addWidget(log_card)
        
        # Add columns to grid
        left_widget = QWidget()
        left_widget.setLayout(left_col)
        left_widget.setFixedWidth(380)
        
        right_widget = QWidget()
        right_widget.setLayout(right_col)
        
        main_grid.addWidget(left_widget)
        main_grid.addWidget(right_widget, 1)
        
        layout.addLayout(main_grid)
        
        scroll.setWidget(content)
        
        # Main layout
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(scroll)
    
    def _create_card(self, title):
        """Create a styled card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        if title:
            lbl = QLabel(title)
            lbl.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: {Colors.TEXT_MAIN};
                padding-bottom: 8px;
                border-bottom: 1px solid {Colors.BORDER};
            """)
            layout.addWidget(lbl)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 3)
        card.setGraphicsEffect(shadow)
        
        return card
    
    def _type_btn_style(self, color):
        return f"""
            QPushButton {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MAIN};
                border: 2px solid {Colors.BORDER};
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                border-color: {color};
                background: rgba({self._hex_to_rgb(color)}, 0.1);
            }}
            QPushButton:checked {{
                border-color: {color};
                background: rgba({self._hex_to_rgb(color)}, 0.15);
                color: {color};
            }}
        """
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))
    
    def _small_btn_style(self, color):
        return f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {color};
                color: white;
            }}
            QPushButton:disabled {{
                border-color: {Colors.BORDER};
                color: {Colors.TEXT_MUTED};
            }}
        """
    
    def _input_style(self):
        return f"""
            QLineEdit, QSpinBox {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MAIN};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border-color: {Colors.ACCENT};
            }}
        """
    
    def _show_empty_chart(self):
        """Show empty chart state"""
        if not HAS_MATPLOTLIB:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#151922')
        ax.text(0.5, 0.5, 'Test calistirin\nSonuclar burada gorunecek',
                ha='center', va='center', fontsize=14, color='#64748B',
                transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw()
    
    def select_type(self, type_key):
        """Select algorithm type"""
        self.selected_type = type_key
        
        # Update buttons
        for key, btn in self.type_buttons.items():
            btn.setChecked(key == type_key)
        
        # Clear old checkboxes
        self.algo_checkboxes.clear()
        while self.algo_container.count():
            item = self.algo_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        
        # Add new checkboxes
        algos = ALGORITHMS.get(type_key, {})
        
        for algo_key, info in algos.items():
            row = QWidget()
            row.setStyleSheet(f"""
                QWidget {{
                    background: {Colors.BG_DARKER};
                    border-radius: 8px;
                }}
                QWidget:hover {{
                    background: #1A1F2E;
                }}
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 10, 12, 10)
            
            cb = QCheckBox(info['name'])
            cb.setProperty('key', algo_key)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {Colors.TEXT_MAIN};
                    font-size: 13px;
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {Colors.BORDER};
                    border-radius: 4px;
                }}
                QCheckBox::indicator:checked {{
                    background: {Colors.ACCENT};
                    border-color: {Colors.ACCENT};
                }}
            """)
            row_layout.addWidget(cb)
            
            complexity = QLabel(info.get('complexity_time', ''))
            complexity.setStyleSheet(f"""
                color: {Colors.TEXT_MUTED};
                font-size: 11px;
                background: {Colors.BG_CARD};
                padding: 3px 8px;
                border-radius: 4px;
            """)
            row_layout.addStretch()
            row_layout.addWidget(complexity)
            
            self.algo_checkboxes.append(cb)
            self.algo_container.addWidget(row)
        
        self.sel_all_btn.setEnabled(True)
        self.clr_btn.setEnabled(True)
    
    def select_all(self):
        for cb in self.algo_checkboxes:
            cb.setChecked(True)
    
    def clear_all(self):
        for cb in self.algo_checkboxes:
            cb.setChecked(False)
    
    def run_test(self):
        """Start the benchmark"""
        selected = [cb.property('key') for cb in self.algo_checkboxes if cb.isChecked()]
        
        if not selected:
            self.log_text.append("⚠️ En az bir algoritma seçin!")
            return
        
        try:
            sizes = [int(s.strip()) for s in self.size_input.text().split(',')]
        except:
            self.log_text.append("⚠️ Geçersiz boyut formatı!")
            return
        
        runs = self.runs_input.value()
        total_steps = len(sizes) * len(selected) * runs
        
        # UI Updates
        self.run_btn.setEnabled(False)
        self.run_btn.setText("⏳ Test Çalışıyor...")
        self.progress_container.show()
        self.progress.setRange(0, total_steps)
        self.progress.setValue(0)
        self.status_label.setText("🔄 Test başlatılıyor...")
        self.status_label.setStyleSheet(f"color: {Colors.WARNING}; font-size: 12px; font-weight: 500;")
        self.current_algo_label.setText("")
        
        self.log_text.clear()
        self.log_text.append(f"📋 Algoritmalar: {', '.join(selected)}")
        self.log_text.append(f"📊 Boyutlar: {sizes}")
        self.log_text.append(f"🔄 Tekrar: {runs}")
        self.log_text.append(f"📈 Toplam adım: {total_steps}\n")
        
        self.worker = BenchmarkWorker(sizes, selected, runs)
        self.worker.log_signal.connect(self.log_text.append)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.done_signal.connect(self.on_done)
        self.worker.start()
    
    def update_progress(self, current, total, algo_name):
        """Update progress bar and status"""
        self.progress.setValue(current)
        percent = int((current / total) * 100)
        self.status_label.setText(f"🔄 İlerleme: {current}/{total} ({percent}%)")
        self.current_algo_label.setText(f"📌 Çalışan: {algo_name}")
    
    def on_done(self, path, results):
        """Handle completion"""
        self.run_btn.setEnabled(True)
        self.run_btn.setText("▶  TESTİ BAŞLAT")
        
        if path:
            self.status_label.setText("✅ Tamamlandı!")
            self.status_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 12px; font-weight: 500;")
            self.current_algo_label.setText("")
            self.progress.setValue(self.progress.maximum())
            
            self.log_text.append(f"\n✅ Tamamlandı!")
            self.log_text.append(f"📁 {path}")
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.results_data = json.load(f)
                self.refresh_chart()
            except Exception as e:
                self.log_text.append(f"⚠️ Grafik hatası: {e}")
        else:
            self.status_label.setText("❌ Test başarısız!")
            self.status_label.setStyleSheet(f"color: {Colors.DANGER}; font-size: 12px; font-weight: 500;")
            self.log_text.append("\n❌ Test başarısız!")
    
    def refresh_chart(self):
        """Update chart with current data"""
        if not HAS_MATPLOTLIB or not self.results_data:
            return
        
        chart_type = self.chart_combo.currentData()
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#151922')
        
        names = []
        values = []
        colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
        
        for key, data in self.results_data.items():
            if isinstance(data, dict):
                names.append(key.replace('_', ' ').title())
                if chart_type == 'time':
                    values.append(data.get('avg_time', 0) * 1000)
                elif chart_type == 'energy':
                    values.append(data.get('avg_energy', 0))
                elif chart_type == 'memory':
                    values.append(data.get('avg_memory', 0) / 1024)
        
        if not names:
            self._show_empty_chart()
            return
        
        bars = ax.barh(range(len(names)), values, color=colors[:len(names)], height=0.6)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=11, color='white')
        ax.invert_yaxis()
        
        labels = {'time': 'Süre (ms)', 'energy': 'Enerji (J)', 'memory': 'Bellek (KB)'}
        ax.set_xlabel(labels.get(chart_type, ''), color='white', fontsize=11)
        
        ax.tick_params(axis='x', colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#2A303C')
        ax.grid(axis='x', alpha=0.2, color='#2A303C')
        
        for bar, val in zip(bars, values):
            ax.annotate(f'{val:.2f}', xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                       xytext=(5, 0), textcoords='offset points',
                       ha='left', va='center', color='white', fontsize=10, fontweight='bold')
        
        self.figure.tight_layout()
        self.canvas.draw()
