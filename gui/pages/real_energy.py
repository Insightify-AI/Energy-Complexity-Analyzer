"""
Enerji Analizi Sayfası - Çoklu Test ve Grafikler
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QCheckBox, QSpinBox, QPushButton, QProgressBar,
    QTextEdit, QGridLayout, QComboBox, QLineEdit, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QSplitter,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gui.styles import Colors
from algorithms import ALGORITHMS

# Matplotlib
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Algoritma türleri
ALGORITHM_TYPES = {
    'divide_conquer': {'name': 'Bol ve Yonet', 'icon': 'D&C', 'color': '#4CC9F0'},
    'dynamic_programming': {'name': 'Dinamik Programlama', 'icon': 'DP', 'color': '#F72585'},
    'greedy': {'name': 'Acgozlu', 'icon': 'GRD', 'color': '#4361EE'}
}


class EnergyTestWorker(QThread):
    """Enerji testi worker thread'i"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int, str)
    result_signal = pyqtSignal(dict)
    
    def __init__(self, algorithms, sizes, runs):
        super().__init__()
        self.algorithms = algorithms
        self.sizes = sizes
        self.runs = runs
        self._running = True
        
    def stop(self):
        self._running = False
    
    def run(self):
        results = {}
        total = len(self.algorithms) * len(self.sizes) * self.runs
        current = 0
        
        self.log_signal.emit("[*] Enerji analizi baslatiliyor...")
        self.log_signal.emit(f"    Algoritmalar: {len(self.algorithms)}")
        self.log_signal.emit(f"    Boyutlar: {self.sizes}")
        self.log_signal.emit(f"    Tekrar: {self.runs}\n")
        
        for algo_key in self.algorithms:
            if not self._running:
                break
                
            # Find algorithm
            algo_info = None
            for cat, algos in ALGORITHMS.items():
                if algo_key in algos:
                    algo_info = algos[algo_key]
                    break
            
            if not algo_info:
                continue
            
            algo_name = algo_info['name']
            self.log_signal.emit(f"[>] {algo_name}")
            
            results[algo_key] = {
                'name': algo_name,
                'complexity_time': algo_info.get('complexity_time', 'N/A'),
                'complexity_space': algo_info.get('complexity_space', 'N/A'),
                'sizes': {},
                'avg_time': 0,
                'avg_energy': 0,
                'avg_memory': 0
            }
            
            all_times = []
            all_energies = []
            all_memories = []
            
            for size in self.sizes:
                if not self._running:
                    break
                    
                size_times = []
                size_energies = []
                size_memories = []
                
                for r in range(self.runs):
                    if not self._running:
                        break
                    
                    current += 1
                    self.progress_signal.emit(current, total, algo_name)
                    
                    # Generate test data
                    data = [random.randint(1, size * 10) for _ in range(size)]
                    
                    # Measure
                    import tracemalloc
                    tracemalloc.start()
                    
                    start = time.perf_counter()
                    try:
                        algo_info['func'](data.copy())
                    except:
                        pass
                    end = time.perf_counter()
                    
                    current_mem, peak_mem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    
                    exec_time = (end - start) * 1000  # ms
                    memory = peak_mem / 1024  # KB
                    
                    # Energy estimation (power * time)
                    power = 25.0  # Estimated watts
                    energy = power * (exec_time / 1000)  # Joules
                    
                    size_times.append(exec_time)
                    size_energies.append(energy)
                    size_memories.append(memory)
                
                if size_times:
                    avg_t = sum(size_times) / len(size_times)
                    avg_e = sum(size_energies) / len(size_energies) 
                    avg_m = sum(size_memories) / len(size_memories)
                    
                    results[algo_key]['sizes'][size] = {
                        'avg_time': avg_t,
                        'avg_energy': avg_e,
                        'avg_memory': avg_m,
                        'times': size_times,
                        'energies': size_energies,
                        'memories': size_memories
                    }
                    
                    all_times.extend(size_times)
                    all_energies.extend(size_energies)
                    all_memories.extend(size_memories)
                    
                    self.log_signal.emit(f"    n={size}: {avg_t:.4f}ms, {avg_e:.6f}J")
            
            if all_times:
                results[algo_key]['avg_time'] = sum(all_times) / len(all_times)
                results[algo_key]['avg_energy'] = sum(all_energies) / len(all_energies)
                results[algo_key]['avg_memory'] = sum(all_memories) / len(all_memories)
        
        # Save results
        if results:
            results_dir = Path(__file__).parent.parent.parent / 'results'
            results_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = results_dir / f'energy_analysis_{timestamp}.json'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.log_signal.emit(f"\n[OK] Analiz tamamlandi!")
            self.log_signal.emit(f"[>] Kaydedildi: {filepath.name}")
        
        self.result_signal.emit(results)


class ChartWidget(QWidget):
    """Grafik widget'i"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_MATPLOTLIB:
            plt.style.use('dark_background')
            self.figure = Figure(figsize=(8, 4), facecolor='#151922')
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
            self.show_empty()
        else:
            lbl = QLabel("Grafik icin matplotlib gerekli")
            lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; padding: 40px;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
    
    def show_empty(self):
        if not HAS_MATPLOTLIB:
            return
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#151922')
        ax.text(0.5, 0.5, 'Test calistirin\nSonuclar burada gorunecek',
                ha='center', va='center', fontsize=13, color='#64748B',
                transform=ax.transAxes)
        ax.axis('off')
        self.canvas.draw()
    
    def plot_bar_comparison(self, data, metric='time', title=''):
        """Bar chart ile karşılaştırma"""
        if not HAS_MATPLOTLIB or not data:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#151922')
        
        names = []
        values = []
        colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
        
        for key, info in data.items():
            names.append(info.get('name', key)[:15])
            if metric == 'time':
                values.append(info.get('avg_time', 0))
            elif metric == 'energy':
                values.append(info.get('avg_energy', 0))
            elif metric == 'memory':
                values.append(info.get('avg_memory', 0) / 1024)  # MB
        
        if not names:
            return
        
        bars = ax.barh(range(len(names)), values, color=colors[:len(names)], height=0.6)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=10, color='white')
        ax.invert_yaxis()
        
        labels = {'time': 'Sure (ms)', 'energy': 'Enerji (J)', 'memory': 'Bellek (MB)'}
        ax.set_xlabel(labels.get(metric, ''), color='white', fontsize=10)
        ax.set_title(title, color='white', fontsize=12, fontweight='bold', pad=10)
        
        ax.tick_params(axis='x', colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#2A303C')
        ax.grid(axis='x', alpha=0.2, color='#2A303C')
        
        for bar, val in zip(bars, values):
            ax.annotate(f'{val:.4f}', xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                       xytext=(5, 0), textcoords='offset points',
                       ha='left', va='center', color='white', fontsize=9)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_line_scaling(self, data, metric='time'):
        """Line chart ile ölçekleme analizi"""
        if not HAS_MATPLOTLIB or not data:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#151922')
        
        colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444']
        color_idx = 0
        
        for key, info in data.items():
            sizes = info.get('sizes', {})
            if not sizes:
                continue
            
            x = sorted(sizes.keys())
            y = []
            for s in x:
                if metric == 'time':
                    y.append(sizes[s].get('avg_time', 0))
                elif metric == 'energy':
                    y.append(sizes[s].get('avg_energy', 0))
                elif metric == 'memory':
                    y.append(sizes[s].get('avg_memory', 0) / 1024)
            
            ax.plot(x, y, 'o-', color=colors[color_idx % len(colors)], 
                   label=info.get('name', key)[:12], linewidth=2, markersize=6)
            color_idx += 1
        
        labels = {'time': 'Sure (ms)', 'energy': 'Enerji (J)', 'memory': 'Bellek (MB)'}
        ax.set_xlabel('Veri Boyutu (n)', color='white', fontsize=10)
        ax.set_ylabel(labels.get(metric, ''), color='white', fontsize=10)
        ax.set_title('Olcekleme Analizi', color='white', fontsize=12, fontweight='bold')
        
        ax.tick_params(colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#2A303C')
        ax.spines['bottom'].set_color('#2A303C')
        ax.grid(alpha=0.2, color='#2A303C')
        ax.legend(loc='upper left', fontsize=8, facecolor='#151922', edgecolor='#2A303C')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pie_energy(self, data):
        """Pie chart ile enerji dağılımı"""
        if not HAS_MATPLOTLIB or not data:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#151922')
        
        names = []
        values = []
        colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444']
        
        for key, info in data.items():
            names.append(info.get('name', key)[:12])
            values.append(info.get('avg_energy', 0))
        
        if not values or sum(values) == 0:
            return
        
        wedges, texts, autotexts = ax.pie(values, labels=names, autopct='%1.1f%%',
                                          colors=colors[:len(names)],
                                          textprops={'color': 'white', 'fontsize': 9})
        
        ax.set_title('Enerji Dagilimi', color='white', fontsize=12, fontweight='bold')
        
        self.figure.tight_layout()
        self.canvas.draw()


class RealEnergyPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.algo_checkboxes = []
        self.selected_type = None
        self.results_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        # Ana scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: {Colors.BG_DARK}; }}
            QScrollBar:vertical {{
                background: {Colors.BG_DARKER}; width: 8px; border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {Colors.BORDER}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {Colors.ACCENT}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        
        content = QWidget()
        content.setStyleSheet(f"background: {Colors.BG_DARK};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(24)
        
        # === HEADER ===
        header = QLabel("Enerji Analizi")
        header.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Colors.TEXT_MAIN};")
        layout.addWidget(header)
        
        desc = QLabel("Algoritmalarin enerji tuketimini analiz edin ve karsilastirin")
        desc.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_MUTED}; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # === CONFIGURATION SECTION ===
        config_card = self._create_card()
        config_layout = QVBoxLayout(config_card)
        config_layout.setContentsMargins(24, 24, 24, 24)
        config_layout.setSpacing(20)
        
        config_title = QLabel("Test Yapilandirmasi")
        config_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        config_layout.addWidget(config_title)
        
        # Row 1: Algorithm Type Selection
        type_row = QHBoxLayout()
        type_row.setSpacing(12)
        
        type_label = QLabel("Algoritma Turu:")
        type_label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-weight: 500;")
        type_row.addWidget(type_label)
        
        self.type_buttons = {}
        for key, info in ALGORITHM_TYPES.items():
            btn = QPushButton(f"{info['icon']} {info['name']}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._type_btn_style(info['color']))
            btn.clicked.connect(lambda checked, k=key: self.select_type(k))
            self.type_buttons[key] = btn
            type_row.addWidget(btn)
        
        type_row.addStretch()
        config_layout.addLayout(type_row)
        
        # Row 2: Algorithm Selection
        algo_row = QVBoxLayout()
        algo_row.setSpacing(8)
        
        algo_header = QHBoxLayout()
        algo_label = QLabel("Algoritmalar:")
        algo_label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-weight: 500;")
        algo_header.addWidget(algo_label)
        
        self.select_all_btn = QPushButton("Tumunu Sec")
        self.select_all_btn.setStyleSheet(self._small_btn_style(Colors.ACCENT))
        self.select_all_btn.clicked.connect(self.select_all_algos)
        self.select_all_btn.setEnabled(False)
        algo_header.addWidget(self.select_all_btn)
        
        self.clear_btn = QPushButton("Temizle")
        self.clear_btn.setStyleSheet(self._small_btn_style(Colors.DANGER))
        self.clear_btn.clicked.connect(self.clear_all_algos)
        self.clear_btn.setEnabled(False)
        algo_header.addWidget(self.clear_btn)
        
        algo_header.addStretch()
        algo_row.addLayout(algo_header)
        
        # Algorithm checkboxes container
        self.algo_container = QFrame()
        self.algo_container.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_DARKER};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
            }}
        """)
        self.algo_grid = QGridLayout(self.algo_container)
        self.algo_grid.setContentsMargins(16, 16, 16, 16)
        self.algo_grid.setSpacing(12)
        
        placeholder = QLabel("Bir algoritma turu secin")
        placeholder.setStyleSheet(f"color: {Colors.TEXT_MUTED}; padding: 20px;")
        placeholder.setAlignment(Qt.AlignCenter)
        self.algo_grid.addWidget(placeholder, 0, 0)
        
        algo_row.addWidget(self.algo_container)
        config_layout.addLayout(algo_row)
        
        # Row 3: Parameters
        params_row = QHBoxLayout()
        params_row.setSpacing(24)
        
        # Data sizes
        size_group = QVBoxLayout()
        size_label = QLabel("Veri Boyutlari (virgul ile):")
        size_label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-size: 12px;")
        self.size_input = QLineEdit("100, 500, 1000, 2000")
        self.size_input.setStyleSheet(self._input_style())
        size_group.addWidget(size_label)
        size_group.addWidget(self.size_input)
        params_row.addLayout(size_group, 2)
        
        # Runs
        runs_group = QVBoxLayout()
        runs_label = QLabel("Tekrar Sayisi:")
        runs_label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-size: 12px;")
        self.runs_spin = QSpinBox()
        self.runs_spin.setRange(1, 10)
        self.runs_spin.setValue(3)
        self.runs_spin.setStyleSheet(self._input_style())
        runs_group.addWidget(runs_label)
        runs_group.addWidget(self.runs_spin)
        params_row.addLayout(runs_group, 1)
        
        params_row.addStretch()
        config_layout.addLayout(params_row)
        
        # Run Button
        btn_row = QHBoxLayout()
        
        self.run_btn = QPushButton("ANALIZI BASLAT")
        self.run_btn.setFixedHeight(48)
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 #7C3AED);
                color: white; border: none; border-radius: 10px;
                font-size: 14px; font-weight: bold; padding: 0 40px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7BFF, stop:1 #9B5CF7);
            }}
            QPushButton:disabled {{ background: {Colors.BORDER}; color: {Colors.TEXT_MUTED}; }}
        """)
        self.run_btn.clicked.connect(self.start_analysis)
        btn_row.addWidget(self.run_btn)
        
        self.stop_btn = QPushButton("Durdur")
        self.stop_btn.setFixedHeight(48)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.DANGER}; color: white;
                border: none; border-radius: 10px;
                font-size: 14px; font-weight: bold; padding: 0 30px;
            }}
            QPushButton:hover {{ background: #DC2626; }}
        """)
        self.stop_btn.clicked.connect(self.stop_analysis)
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.stop_btn)
        
        btn_row.addStretch()
        config_layout.addLayout(btn_row)
        
        # Progress
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(4)
        
        self.status_label = QLabel("Hazir")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px;")
        progress_layout.addWidget(self.status_label)
        
        self.progress = QProgressBar()
        self.progress.setFixedHeight(10)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{ background: {Colors.BG_DARKER}; border: none; border-radius: 5px; }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.ACCENT}, stop:1 {Colors.PRIMARY});
                border-radius: 5px;
            }}
        """)
        progress_layout.addWidget(self.progress)
        
        self.progress_container.hide()
        config_layout.addWidget(self.progress_container)
        
        layout.addWidget(config_card)
        
        # === RESULTS SECTION ===
        self.results_card = self._create_card()
        results_layout = QVBoxLayout(self.results_card)
        results_layout.setContentsMargins(24, 24, 24, 24)
        results_layout.setSpacing(16)
        
        results_title = QLabel("Sonuclar ve Grafikler")
        results_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        results_layout.addWidget(results_title)
        
        # Tabs for different charts
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                background: {Colors.BG_DARKER};
            }}
            QTabBar::tab {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MUTED};
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background: {Colors.BG_CARD};
                color: {Colors.ACCENT};
            }}
        """)
        
        # Tab 1: Bar Charts
        bar_tab = QWidget()
        bar_layout = QVBoxLayout(bar_tab)
        bar_layout.setContentsMargins(16, 16, 16, 16)
        
        bar_controls = QHBoxLayout()
        bar_metric_label = QLabel("Metrik:")
        bar_metric_label.setStyleSheet(f"color: {Colors.TEXT_MAIN};")
        self.bar_metric_combo = QComboBox()
        self.bar_metric_combo.addItem("Sure (ms)", "time")
        self.bar_metric_combo.addItem("Enerji (J)", "energy")
        self.bar_metric_combo.addItem("Bellek (MB)", "memory")
        self.bar_metric_combo.setStyleSheet(self._combo_style())
        self.bar_metric_combo.currentIndexChanged.connect(self.update_bar_chart)
        bar_controls.addWidget(bar_metric_label)
        bar_controls.addWidget(self.bar_metric_combo)
        bar_controls.addStretch()
        bar_layout.addLayout(bar_controls)
        
        self.bar_chart = ChartWidget()
        self.bar_chart.setMinimumHeight(300)
        bar_layout.addWidget(self.bar_chart)
        
        self.tabs.addTab(bar_tab, "Karsilastirma")
        
        # Tab 2: Line Charts (Scaling)
        line_tab = QWidget()
        line_layout = QVBoxLayout(line_tab)
        line_layout.setContentsMargins(16, 16, 16, 16)
        
        line_controls = QHBoxLayout()
        line_metric_label = QLabel("Metrik:")
        line_metric_label.setStyleSheet(f"color: {Colors.TEXT_MAIN};")
        self.line_metric_combo = QComboBox()
        self.line_metric_combo.addItem("Sure (ms)", "time")
        self.line_metric_combo.addItem("Enerji (J)", "energy")
        self.line_metric_combo.addItem("Bellek (MB)", "memory")
        self.line_metric_combo.setStyleSheet(self._combo_style())
        self.line_metric_combo.currentIndexChanged.connect(self.update_line_chart)
        line_controls.addWidget(line_metric_label)
        line_controls.addWidget(self.line_metric_combo)
        line_controls.addStretch()
        line_layout.addLayout(line_controls)
        
        self.line_chart = ChartWidget()
        self.line_chart.setMinimumHeight(300)
        line_layout.addWidget(self.line_chart)
        
        self.tabs.addTab(line_tab, "Olcekleme")
        
        # Tab 3: Runs Detail - Her çalıştırma için detaylı tablo
        runs_tab = QWidget()
        runs_layout = QVBoxLayout(runs_tab)
        runs_layout.setContentsMargins(16, 16, 16, 16)
        runs_layout.setSpacing(12)
        
        # Header
        runs_header = QLabel("Performans Metrikleri")
        runs_header.setStyleSheet(f"""
            font-size: 18px; 
            font-weight: bold; 
            color: {Colors.ACCENT};
            padding: 8px 0;
        """)
        runs_layout.addWidget(runs_header)
        
        runs_info = QLabel("Her calistirma icin detayli sonuclar")
        runs_info.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px; margin-bottom: 8px;")
        runs_layout.addWidget(runs_info)
        
        # Algorithm selector
        algo_select_row = QHBoxLayout()
        algo_label = QLabel("Algoritma:")
        algo_label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-weight: 500;")
        self.runs_algo_combo = QComboBox()
        self.runs_algo_combo.setStyleSheet(self._combo_style())
        self.runs_algo_combo.setMinimumWidth(200)
        self.runs_algo_combo.currentIndexChanged.connect(self.update_runs_table)
        algo_select_row.addWidget(algo_label)
        algo_select_row.addWidget(self.runs_algo_combo)
        
        # Size selector
        size_label = QLabel("Boyut:")
        size_label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-weight: 500; margin-left: 20px;")
        self.runs_size_combo = QComboBox()
        self.runs_size_combo.setStyleSheet(self._combo_style())
        self.runs_size_combo.setMinimumWidth(120)
        self.runs_size_combo.currentIndexChanged.connect(self.update_runs_table)
        algo_select_row.addWidget(size_label)
        algo_select_row.addWidget(self.runs_size_combo)
        
        algo_select_row.addStretch()
        runs_layout.addLayout(algo_select_row)
        
        # Runs table with special styling
        self.runs_table = QTableWidget()
        self.runs_table.setColumnCount(4)
        self.runs_table.setHorizontalHeaderLabels(["Test #", "Calisma Suresi", "Bellek Kullanimi", "Enerji Tuketimi"])
        self.runs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.runs_table.setStyleSheet(f"""
            QTableWidget {{
                background: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
                border: none;
                border-radius: 12px;
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: 16px;
                border-bottom: 1px solid {Colors.BORDER};
            }}
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366F1, stop:1 #8B5CF6);
                color: white;
                padding: 14px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 12px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 12px;
            }}
        """)
        self.runs_table.setMinimumHeight(300)
        self.runs_table.setShowGrid(False)
        self.runs_table.setAlternatingRowColors(False)
        self.runs_table.verticalHeader().setVisible(False)
        runs_layout.addWidget(self.runs_table)
        
        # Summary card
        self.runs_summary = QFrame()
        self.runs_summary.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_DARKER};
                border-radius: 10px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        summary_layout = QHBoxLayout(self.runs_summary)
        summary_layout.setContentsMargins(20, 16, 20, 16)
        summary_layout.setSpacing(40)
        
        # Summary stats placeholders
        self.summary_time_label = self._create_summary_stat("Ort. Sure", "0.00 ms", Colors.ACCENT)
        self.summary_memory_label = self._create_summary_stat("Ort. Bellek", "0 B", Colors.PRIMARY)
        self.summary_energy_label = self._create_summary_stat("Ort. Enerji", "0.00 mJ", "#10B981")
        
        summary_layout.addWidget(self.summary_time_label)
        summary_layout.addWidget(self.summary_memory_label)
        summary_layout.addWidget(self.summary_energy_label)
        summary_layout.addStretch()
        
        runs_layout.addWidget(self.runs_summary)
        
        self.tabs.addTab(runs_tab, "Calistirmalar")
        
        # Tab 4: Pie Chart
        pie_tab = QWidget()
        pie_layout = QVBoxLayout(pie_tab)
        pie_layout.setContentsMargins(16, 16, 16, 16)
        
        self.pie_chart = ChartWidget()
        self.pie_chart.setMinimumHeight(300)
        pie_layout.addWidget(self.pie_chart)
        
        self.tabs.addTab(pie_tab, "Enerji Dagilimi")
        
        # Tab 5: Table
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        table_layout.setContentsMargins(16, 16, 16, 16)
        
        self.results_table = QTableWidget()
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MAIN};
                border: none;
                gridline-color: {Colors.BORDER};
            }}
            QTableWidget::item {{ padding: 8px; }}
            QHeaderView::section {{
                background: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
        """)
        table_layout.addWidget(self.results_table)
        
        self.tabs.addTab(table_tab, "Veri Tablosu")
        
        # Tab 6: Log
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(16, 16, 16, 16)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background: {Colors.BG_DARKER};
                color: {Colors.ACCENT};
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }}
        """)
        self.log_text.setPlaceholderText("Analiz loglari burada gorunecek...")
        log_layout.addWidget(self.log_text)
        
        self.tabs.addTab(log_tab, "Log")
        
        # Tab 7: PDF Report
        pdf_tab = QWidget()
        pdf_layout = QVBoxLayout(pdf_tab)
        pdf_layout.setContentsMargins(24, 24, 24, 24)
        pdf_layout.setSpacing(20)
        
        # Header
        pdf_header = QLabel("📄 PDF Rapor Oluştur")
        pdf_header.setStyleSheet(f"""
            font-size: 20px; 
            font-weight: bold; 
            color: {Colors.ACCENT};
        """)
        pdf_layout.addWidget(pdf_header)
        
        pdf_desc = QLabel("Test sonuçlarını detaylı grafikler ve tablolarla PDF formatında indirin.")
        pdf_desc.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 13px;")
        pdf_layout.addWidget(pdf_desc)
        
        # Report Options
        options_frame = QFrame()
        options_frame.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_DARKER};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(20, 20, 20, 20)
        options_layout.setSpacing(16)
        
        options_title = QLabel("📋 Rapora Dahil Edilecekler")
        options_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Colors.TEXT_MAIN};")
        options_layout.addWidget(options_title)
        
        # Checkboxes for report content
        self.pdf_include_summary = QCheckBox("Özet Bilgiler ve İstatistikler")
        self.pdf_include_summary.setChecked(True)
        self.pdf_include_summary.setStyleSheet(self._pdf_checkbox_style())
        options_layout.addWidget(self.pdf_include_summary)
        
        self.pdf_include_bar = QCheckBox("Karşılaştırma Grafikleri (Bar Chart)")
        self.pdf_include_bar.setChecked(True)
        self.pdf_include_bar.setStyleSheet(self._pdf_checkbox_style())
        options_layout.addWidget(self.pdf_include_bar)
        
        self.pdf_include_line = QCheckBox("Ölçekleme Grafikleri (Line Chart)")
        self.pdf_include_line.setChecked(True)
        self.pdf_include_line.setStyleSheet(self._pdf_checkbox_style())
        options_layout.addWidget(self.pdf_include_line)
        
        self.pdf_include_pie = QCheckBox("Enerji Dağılımı (Pie Chart)")
        self.pdf_include_pie.setChecked(True)
        self.pdf_include_pie.setStyleSheet(self._pdf_checkbox_style())
        options_layout.addWidget(self.pdf_include_pie)
        
        self.pdf_include_table = QCheckBox("Detaylı Veri Tablosu")
        self.pdf_include_table.setChecked(True)
        self.pdf_include_table.setStyleSheet(self._pdf_checkbox_style())
        options_layout.addWidget(self.pdf_include_table)
        
        pdf_layout.addWidget(options_frame)
        
        # Preview info
        preview_frame = QFrame()
        preview_frame.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        preview_layout.setSpacing(12)
        
        preview_title = QLabel("📊 Rapor Önizleme")
        preview_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Colors.TEXT_MAIN};")
        preview_layout.addWidget(preview_title)
        
        self.pdf_status_label = QLabel("⚠️ Rapor oluşturmak için önce bir test çalıştırın.")
        self.pdf_status_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px;")
        self.pdf_status_label.setWordWrap(True)
        preview_layout.addWidget(self.pdf_status_label)
        
        pdf_layout.addWidget(preview_frame)
        
        # Download Button
        btn_row = QHBoxLayout()
        
        self.pdf_download_btn = QPushButton("📥  PDF İndir")
        self.pdf_download_btn.setFixedHeight(50)
        self.pdf_download_btn.setCursor(Qt.PointingHandCursor)
        self.pdf_download_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10B981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                padding: 0 40px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #047857);
            }}
            QPushButton:disabled {{
                background: {Colors.BORDER};
                color: {Colors.TEXT_MUTED};
            }}
        """)
        self.pdf_download_btn.clicked.connect(self.generate_pdf_report)
        self.pdf_download_btn.setEnabled(False)
        btn_row.addWidget(self.pdf_download_btn)
        
        btn_row.addStretch()
        pdf_layout.addLayout(btn_row)
        
        pdf_layout.addStretch()
        
        self.tabs.addTab(pdf_tab, "📄 PDF Rapor")
        
        results_layout.addWidget(self.tabs)
        layout.addWidget(self.results_card)
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_card(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 3)
        card.setGraphicsEffect(shadow)
        return card
    
    def _create_summary_stat(self, title, value, color):
        """Özet istatistik widget'ı oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_MUTED};")
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return widget
    
    def _type_btn_style(self, color):
        return f"""
            QPushButton {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MAIN};
                border: 2px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
            }}
            QPushButton:hover {{ border-color: {color}; }}
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
                padding: 6px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background: {color}; color: white; }}
            QPushButton:disabled {{ border-color: {Colors.BORDER}; color: {Colors.TEXT_MUTED}; }}
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
            QLineEdit:focus, QSpinBox:focus {{ border-color: {Colors.ACCENT}; }}
        """
    
    def _combo_style(self):
        return f"""
            QComboBox {{
                background: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 120px;
            }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox::down-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {Colors.ACCENT};
            }}
        """
    
    def select_type(self, type_key):
        """Algoritma türü seçildiğinde"""
        self.selected_type = type_key
        
        for k, btn in self.type_buttons.items():
            btn.setChecked(k == type_key)
        
        # Clear existing checkboxes
        self.algo_checkboxes.clear()
        while self.algo_grid.count():
            item = self.algo_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add algorithm checkboxes
        algos = ALGORITHMS.get(type_key, {})
        row, col = 0, 0
        
        for algo_key, info in algos.items():
            cb = QCheckBox(info['name'])
            cb.setProperty('algo_key', algo_key)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {Colors.TEXT_MAIN};
                    font-size: 13px;
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 18px; height: 18px;
                    border: 2px solid {Colors.BORDER};
                    border-radius: 4px;
                }}
                QCheckBox::indicator:checked {{
                    background: {Colors.ACCENT};
                    border-color: {Colors.ACCENT};
                }}
            """)
            self.algo_checkboxes.append(cb)
            self.algo_grid.addWidget(cb, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        self.select_all_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
    
    def select_all_algos(self):
        for cb in self.algo_checkboxes:
            cb.setChecked(True)
    
    def clear_all_algos(self):
        for cb in self.algo_checkboxes:
            cb.setChecked(False)
    
    def start_analysis(self):
        selected = [cb.property('algo_key') for cb in self.algo_checkboxes if cb.isChecked()]
        
        if not selected:
            self.log_text.append("[!] En az bir algoritma secin!")
            return
        
        try:
            sizes = [int(s.strip()) for s in self.size_input.text().split(',')]
        except:
            self.log_text.append("[!] Gecersiz boyut formati!")
            return
        
        runs = self.runs_spin.value()
        
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_container.show()
        self.progress.setValue(0)
        self.status_label.setText("Analiz baslatiliyor...")
        self.log_text.clear()
        
        self.worker = EnergyTestWorker(selected, sizes, runs)
        self.worker.log_signal.connect(self.log_text.append)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.result_signal.connect(self.on_complete)
        self.worker.start()
    
    def stop_analysis(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        self.reset_ui()
        self.log_text.append("\n[!] Analiz durduruldu.")
    
    def update_progress(self, current, total, algo):
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        percent = int((current / total) * 100)
        self.status_label.setText(f"Ilerleme: {current}/{total} ({percent}%) - {algo}")
    
    def on_complete(self, results):
        self.reset_ui()
        self.results_data = results
        
        if results:
            self.status_label.setText("Tamamlandi!")
            self.status_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 12px;")
            self.update_all_charts()
            self.update_table()
            self.populate_runs_combos()
            self.tabs.setCurrentIndex(0)
            
            # Enable PDF download
            self.pdf_download_btn.setEnabled(True)
            algo_count = len(results)
            self.pdf_status_label.setText(
                f"✅ Rapor hazır! {algo_count} algoritma analizi sonucu PDF olarak indirilebilir.\n"
                f"📅 Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            self.pdf_status_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 12px;")
    
    def reset_ui(self):
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def update_all_charts(self):
        self.update_bar_chart()
        self.update_line_chart()
        self.pie_chart.plot_pie_energy(self.results_data)
    
    def update_bar_chart(self):
        metric = self.bar_metric_combo.currentData()
        self.bar_chart.plot_bar_comparison(self.results_data, metric, 'Algoritma Karsilastirmasi')
    
    def update_line_chart(self):
        metric = self.line_metric_combo.currentData()
        self.line_chart.plot_line_scaling(self.results_data, metric)
    
    def update_table(self):
        if not self.results_data:
            return
        
        cols = ['Algoritma', 'Karmasiklik', 'Ort. Sure', 'Ort. Enerji', 'Ort. Bellek']
        self.results_table.setColumnCount(len(cols))
        self.results_table.setHorizontalHeaderLabels(cols)
        self.results_table.setRowCount(len(self.results_data))
        
        for i, (key, info) in enumerate(self.results_data.items()):
            self.results_table.setItem(i, 0, QTableWidgetItem(info.get('name', key)))
            self.results_table.setItem(i, 1, QTableWidgetItem(info.get('complexity_time', 'N/A')))
            
            # Süre - birimli
            time_val = info.get('avg_time', 0)
            if time_val < 1:
                time_str = f"{time_val * 1000:.2f} µs"
            elif time_val < 1000:
                time_str = f"{time_val:.4f} ms"
            else:
                time_str = f"{time_val / 1000:.2f} s"
            self.results_table.setItem(i, 2, QTableWidgetItem(time_str))
            
            # Enerji - birimli
            energy_val = info.get('avg_energy', 0)
            if energy_val < 0.001:
                energy_str = f"{energy_val * 1000:.4f} mJ"
            elif energy_val < 1:
                energy_str = f"{energy_val:.6f} J"
            else:
                energy_str = f"{energy_val:.4f} J"
            self.results_table.setItem(i, 3, QTableWidgetItem(energy_str))
            
            # Bellek - birimli
            memory_val = info.get('avg_memory', 0)
            if memory_val < 1:
                memory_str = f"{memory_val * 1024:.0f} B"
            elif memory_val < 1024:
                memory_str = f"{memory_val:.2f} KB"
            else:
                memory_str = f"{memory_val / 1024:.2f} MB"
            self.results_table.setItem(i, 4, QTableWidgetItem(memory_str))
        
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def populate_runs_combos(self):
        """Çalıştırmalar tabındaki combo'ları doldur"""
        if not self.results_data:
            return
        
        # Algoritma combo'sunu doldur
        self.runs_algo_combo.blockSignals(True)
        self.runs_algo_combo.clear()
        for key, info in self.results_data.items():
            self.runs_algo_combo.addItem(info.get('name', key), key)
        self.runs_algo_combo.blockSignals(False)
        
        # İlk algoritmanın boyutlarını yükle
        if self.results_data:
            first_key = list(self.results_data.keys())[0]
            self.update_size_combo(first_key)
        
        self.update_runs_table()
    
    def update_size_combo(self, algo_key):
        """Seçilen algoritmaya göre boyut combo'sunu güncelle"""
        self.runs_size_combo.blockSignals(True)
        self.runs_size_combo.clear()
        
        if algo_key in self.results_data:
            sizes = self.results_data[algo_key].get('sizes', {})
            for size in sorted(sizes.keys()):
                self.runs_size_combo.addItem(f"n = {size}", size)
        
        self.runs_size_combo.blockSignals(False)
    
    def update_runs_table(self):
        """Çalıştırmalar tablosunu güncelle"""
        algo_key = self.runs_algo_combo.currentData()
        size = self.runs_size_combo.currentData()
        
        if not algo_key or not size:
            return
        
        # Boyut combo'sunu güncelle
        current_algo = self.runs_algo_combo.currentData()
        if current_algo and self.runs_size_combo.count() == 0:
            self.update_size_combo(current_algo)
            size = self.runs_size_combo.currentData()
        
        if not size:
            return
        
        # Veriyi al
        algo_data = self.results_data.get(algo_key, {})
        sizes_data = algo_data.get('sizes', {})
        size_data = sizes_data.get(size, {})
        
        times = size_data.get('times', [])
        energies = size_data.get('energies', [])
        memories = size_data.get('memories', [])
        
        # Tabloyu doldur
        num_runs = len(times)
        self.runs_table.setRowCount(num_runs)
        
        # Renk paleti
        test_colors = ['#4CC9F0', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444']
        
        for i in range(num_runs):
            # Test # sütunu - renkli
            test_item = QTableWidgetItem(f"#{i+1}")
            test_item.setTextAlignment(Qt.AlignCenter)
            color = test_colors[i % len(test_colors)]
            test_item.setForeground(QColor(color))
            font = test_item.font()
            font.setBold(True)
            font.setPointSize(12)
            test_item.setFont(font)
            self.runs_table.setItem(i, 0, test_item)
            
            # Çalışma Süresi
            time_val = times[i] if i < len(times) else 0
            time_item = QTableWidgetItem(f"{time_val:.2f} ms")
            time_item.setTextAlignment(Qt.AlignCenter)
            self.runs_table.setItem(i, 1, time_item)
            
            # Bellek Kullanımı
            mem_val = memories[i] if i < len(memories) else 0
            if mem_val < 1:
                mem_str = f"{int(mem_val * 1024)} B"
            elif mem_val < 1024:
                mem_str = f"{mem_val:.0f} KB"
            else:
                mem_str = f"{mem_val / 1024:.2f} MB"
            mem_item = QTableWidgetItem(mem_str)
            mem_item.setTextAlignment(Qt.AlignCenter)
            self.runs_table.setItem(i, 2, mem_item)
            
            # Enerji Tüketimi
            energy_val = energies[i] if i < len(energies) else 0
            if energy_val < 0.001:
                energy_str = f"{energy_val * 1000:.2f} mJ"
            else:
                energy_str = f"{energy_val:.4f} J"
            energy_item = QTableWidgetItem(energy_str)
            energy_item.setTextAlignment(Qt.AlignCenter)
            self.runs_table.setItem(i, 3, energy_item)
        
        # Satır yüksekliğini ayarla
        for i in range(num_runs):
            self.runs_table.setRowHeight(i, 50)
        
        # Özet istatistikleri güncelle
        if times:
            avg_time = sum(times) / len(times)
            avg_memory = sum(memories) / len(memories) if memories else 0
            avg_energy = sum(energies) / len(energies) if energies else 0
            
            # Time label
            time_label = self.summary_time_label.findChild(QLabel, "value")
            if time_label:
                time_label.setText(f"{avg_time:.2f} ms")
            
            # Memory label
            mem_label = self.summary_memory_label.findChild(QLabel, "value")
            if mem_label:
                if avg_memory < 1:
                    mem_label.setText(f"{int(avg_memory * 1024)} B")
                elif avg_memory < 1024:
                    mem_label.setText(f"{avg_memory:.0f} KB")
                else:
                    mem_label.setText(f"{avg_memory / 1024:.2f} MB")
            
            # Energy label
            energy_label = self.summary_energy_label.findChild(QLabel, "value")
            if energy_label:
                if avg_energy < 0.001:
                    energy_label.setText(f"{avg_energy * 1000:.2f} mJ")
                else:
                    energy_label.setText(f"{avg_energy:.4f} J")
    
    def _pdf_checkbox_style(self):
        return f"""
            QCheckBox {{
                color: {Colors.TEXT_MAIN};
                font-size: 13px;
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {Colors.BORDER};
                border-radius: 6px;
                background: {Colors.BG_CARD};
            }}
            QCheckBox::indicator:checked {{
                background: {Colors.SUCCESS};
                border-color: {Colors.SUCCESS};
            }}
            QCheckBox::indicator:hover {{
                border-color: {Colors.ACCENT};
            }}
        """
    
    def generate_pdf_report(self):
        """PDF rapor oluştur ve kaydet"""
        if not self.results_data:
            QMessageBox.warning(self, "Uyarı", "Rapor oluşturmak için önce bir test çalıştırın!")
            return
        
        if not HAS_MATPLOTLIB:
            QMessageBox.warning(self, "Uyarı", "PDF oluşturmak için matplotlib gerekli!")
            return
        
        # Dosya kaydetme dialogu
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"Algoritma_Analiz_Raporu_{timestamp}.pdf"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, 
            "PDF Rapor Kaydet", 
            default_name,
            "PDF Dosyası (*.pdf)"
        )
        
        if not filepath:
            return
        
        try:
            with PdfPages(filepath) as pdf:
                # Sayfa 1: Başlık ve Özet
                if self.pdf_include_summary.isChecked():
                    fig = plt.figure(figsize=(11, 8.5))
                    fig.patch.set_facecolor('#1a1a2e')
                    
                    # Başlık
                    fig.text(0.5, 0.92, '⚡ Algoritma Enerji Analizi Raporu', 
                            fontsize=24, fontweight='bold', ha='center', color='white')
                    fig.text(0.5, 0.87, f'Oluşturulma Tarihi: {datetime.now().strftime("%d.%m.%Y %H:%M")}',
                            fontsize=12, ha='center', color='#a0a0a0')
                    
                    # Özet bilgiler
                    summary_text = f"""
                    ANALIZ OZETI
                    ═══════════════════════════════════════
                    
                    Toplam Algoritma Sayisi: {len(self.results_data)}
                    
                    """
                    
                    y_pos = 0.75
                    for key, info in self.results_data.items():
                        summary_text += f"""
    {info.get('name', key)}
    ├─ Karmasiklik: {info.get('complexity_time', 'N/A')}
    ├─ Ortalama Sure: {info.get('avg_time', 0):.4f} ms
    ├─ Ortalama Enerji: {info.get('avg_energy', 0):.6f} J
    └─ Ortalama Bellek: {info.get('avg_memory', 0):.2f} KB
                        """
                    
                    fig.text(0.1, 0.7, summary_text, fontsize=10, va='top', 
                            color='white', family='monospace')
                    
                    pdf.savefig(fig, facecolor=fig.get_facecolor())
                    plt.close(fig)
                
                # Sayfa 2: Bar Chart - Süre Karşılaştırması
                if self.pdf_include_bar.isChecked():
                    for metric, label in [('time', 'Calisma Suresi (ms)'), 
                                         ('energy', 'Enerji Tuketimi (J)'),
                                         ('memory', 'Bellek Kullanimi (KB)')]:
                        fig, ax = plt.subplots(figsize=(11, 8.5))
                        fig.patch.set_facecolor('#1a1a2e')
                        ax.set_facecolor('#1a1a2e')
                        
                        names = []
                        values = []
                        colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
                        
                        for key, info in self.results_data.items():
                            names.append(info.get('name', key))
                            if metric == 'time':
                                values.append(info.get('avg_time', 0))
                            elif metric == 'energy':
                                values.append(info.get('avg_energy', 0))
                            else:
                                values.append(info.get('avg_memory', 0))
                        
                        bars = ax.barh(range(len(names)), values, color=colors[:len(names)], height=0.6)
                        ax.set_yticks(range(len(names)))
                        ax.set_yticklabels(names, fontsize=11, color='white')
                        ax.invert_yaxis()
                        
                        ax.set_xlabel(label, color='white', fontsize=12)
                        ax.set_title(f'Algoritma Karsilastirmasi - {label}', 
                                    color='white', fontsize=14, fontweight='bold', pad=20)
                        
                        ax.tick_params(axis='x', colors='white')
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        ax.spines['left'].set_visible(False)
                        ax.spines['bottom'].set_color('#2A303C')
                        ax.grid(axis='x', alpha=0.2, color='#2A303C')
                        
                        for bar, val in zip(bars, values):
                            ax.annotate(f'{val:.4f}', 
                                       xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                                       xytext=(5, 0), textcoords='offset points',
                                       ha='left', va='center', color='white', fontsize=9)
                        
                        plt.tight_layout()
                        pdf.savefig(fig, facecolor=fig.get_facecolor())
                        plt.close(fig)
                
                # Sayfa 3: Line Chart - Ölçekleme
                if self.pdf_include_line.isChecked():
                    fig, ax = plt.subplots(figsize=(11, 8.5))
                    fig.patch.set_facecolor('#1a1a2e')
                    ax.set_facecolor('#1a1a2e')
                    
                    colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444']
                    color_idx = 0
                    
                    for key, info in self.results_data.items():
                        sizes = info.get('sizes', {})
                        if not sizes:
                            continue
                        
                        x = sorted(sizes.keys())
                        y = [sizes[s].get('avg_time', 0) for s in x]
                        
                        ax.plot(x, y, 'o-', color=colors[color_idx % len(colors)], 
                               label=info.get('name', key), linewidth=2, markersize=8)
                        color_idx += 1
                    
                    ax.set_xlabel('Veri Boyutu (n)', color='white', fontsize=12)
                    ax.set_ylabel('Calisma Suresi (ms)', color='white', fontsize=12)
                    ax.set_title('Olcekleme Analizi', color='white', fontsize=14, fontweight='bold', pad=20)
                    
                    ax.tick_params(colors='white')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_color('#2A303C')
                    ax.spines['bottom'].set_color('#2A303C')
                    ax.grid(alpha=0.2, color='#2A303C')
                    ax.legend(loc='upper left', fontsize=10, facecolor='#1a1a2e', 
                             edgecolor='#2A303C', labelcolor='white')
                    
                    plt.tight_layout()
                    pdf.savefig(fig, facecolor=fig.get_facecolor())
                    plt.close(fig)
                
                # Sayfa 4: Pie Chart - Enerji Dağılımı
                if self.pdf_include_pie.isChecked():
                    fig, ax = plt.subplots(figsize=(11, 8.5))
                    fig.patch.set_facecolor('#1a1a2e')
                    ax.set_facecolor('#1a1a2e')
                    
                    names = []
                    values = []
                    colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444']
                    
                    for key, info in self.results_data.items():
                        names.append(info.get('name', key))
                        values.append(info.get('avg_energy', 0))
                    
                    if values and sum(values) > 0:
                        wedges, texts, autotexts = ax.pie(
                            values, labels=names, autopct='%1.1f%%',
                            colors=colors[:len(names)],
                            textprops={'color': 'white', 'fontsize': 11}
                        )
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_fontweight('bold')
                        
                        ax.set_title('Enerji Tuketimi Dagilimi', 
                                    color='white', fontsize=14, fontweight='bold', pad=20)
                    
                    plt.tight_layout()
                    pdf.savefig(fig, facecolor=fig.get_facecolor())
                    plt.close(fig)
                
                # Sayfa 5: Veri Tablosu
                if self.pdf_include_table.isChecked():
                    fig = plt.figure(figsize=(11, 8.5))
                    fig.patch.set_facecolor('#1a1a2e')
                    ax = fig.add_subplot(111)
                    ax.axis('off')
                    
                    # Tablo verisi - birimlerle birlikte
                    table_data = []
                    for key, info in self.results_data.items():
                        # Süre formatlama
                        time_val = info.get('avg_time', 0)
                        if time_val < 1:
                            time_str = f"{time_val * 1000:.2f} µs"
                        elif time_val < 1000:
                            time_str = f"{time_val:.4f} ms"
                        else:
                            time_str = f"{time_val / 1000:.2f} s"
                        
                        # Enerji formatlama
                        energy_val = info.get('avg_energy', 0)
                        if energy_val < 0.001:
                            energy_str = f"{energy_val * 1000:.4f} mJ"
                        else:
                            energy_str = f"{energy_val:.6f} J"
                        
                        # Bellek formatlama
                        memory_val = info.get('avg_memory', 0)
                        if memory_val < 1:
                            memory_str = f"{memory_val * 1024:.0f} B"
                        elif memory_val < 1024:
                            memory_str = f"{memory_val:.2f} KB"
                        else:
                            memory_str = f"{memory_val / 1024:.2f} MB"
                        
                        table_data.append([
                            info.get('name', key),
                            info.get('complexity_time', 'N/A'),
                            time_str,
                            energy_str,
                            memory_str
                        ])
                    
                    columns = ['Algoritma', 'Karmasiklik', 'Ort. Sure', 'Ort. Enerji', 'Ort. Bellek']
                    
                    table = ax.table(
                        cellText=table_data,
                        colLabels=columns,
                        loc='center',
                        cellLoc='center'
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(10)
                    table.scale(1.2, 2)
                    
                    # Tablo stili
                    for i in range(len(columns)):
                        table[(0, i)].set_facecolor('#4361EE')
                        table[(0, i)].set_text_props(color='white', fontweight='bold')
                    
                    for i in range(1, len(table_data) + 1):
                        for j in range(len(columns)):
                            table[(i, j)].set_facecolor('#2a2a4e')
                            table[(i, j)].set_text_props(color='white')
                    
                    fig.text(0.5, 0.92, 'Detayli Sonuc Tablosu', 
                            fontsize=16, fontweight='bold', ha='center', color='white')
                    
                    plt.tight_layout()
                    pdf.savefig(fig, facecolor=fig.get_facecolor())
                    plt.close(fig)
            
            # Başarılı mesajı
            QMessageBox.information(
                self, 
                "Başarılı", 
                f"PDF rapor başarıyla oluşturuldu!\n\n📄 {filepath}"
            )
            
            self.log_text.append(f"\n[OK] PDF rapor olusturuldu: {filepath}")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Hata", 
                f"PDF oluşturulurken hata oluştu:\n{str(e)}"
            )
            self.log_text.append(f"\n[X] PDF olusturma hatasi: {str(e)}")
    
    def refresh(self):
        pass

