"""
Karşılaştırma Sayfası - Grup Bazlı Karşılaştırma
"""

import json
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QCheckBox, QMessageBox,
    QGraphicsDropShadowEffect, QTabWidget, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from gui.styles import Styles, Colors

# Matplotlib
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# Algoritma grupları
ALGORITHM_GROUPS = {
    'divide_conquer': 'Bol ve Yonet',
    'dynamic_programming': 'Dinamik Programlama', 
    'greedy': 'Acgozlu'
}


class ChartCanvas(QWidget):
    """Grafik widget'i"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_MATPLOTLIB:
            plt.style.use('dark_background')
            self.figure = Figure(figsize=(6, 4), facecolor='#151922')
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
        else:
            lbl = QLabel("Matplotlib gerekli")
            lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; padding: 40px;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
    
    def clear(self):
        if HAS_MATPLOTLIB:
            self.figure.clear()
            self.canvas.draw()
    
    def plot_bar(self, names, values, title, xlabel, color=None):
        if not HAS_MATPLOTLIB or not names:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#151922')
        
        colors = color or ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444']
        
        bars = ax.barh(range(len(names)), values, color=colors[:len(names)], height=0.6)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=10, color='white')
        ax.invert_yaxis()
        
        ax.set_xlabel(xlabel, color='white', fontsize=10)
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
    
    def plot_grouped_bar(self, data, metric, title):
        """Grouped bar chart for test comparison"""
        if not HAS_MATPLOTLIB or not data:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#151922')
        
        test_names = list(data.keys())
        if not test_names:
            return
        
        # Get all algorithms from all tests
        all_algos = set()
        for test_data in data.values():
            all_algos.update(test_data.keys())
        all_algos = sorted(list(all_algos))
        
        if not all_algos:
            return
        
        import numpy as np
        x = np.arange(len(all_algos))
        width = 0.8 / len(test_names)
        colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B']
        
        for i, test_name in enumerate(test_names):
            test_data = data[test_name]
            values = []
            for algo in all_algos:
                if algo in test_data:
                    if metric == 'time':
                        values.append(test_data[algo].get('avg_time', 0))
                    elif metric == 'energy':
                        values.append(test_data[algo].get('avg_energy', 0))
                    elif metric == 'memory':
                        values.append(test_data[algo].get('avg_memory', 0) / 1024)
                else:
                    values.append(0)
            
            offset = (i - len(test_names)/2 + 0.5) * width
            bars = ax.bar(x + offset, values, width, label=test_name[:20], 
                         color=colors[i % len(colors)], alpha=0.9)
        
        ax.set_xticks(x)
        ax.set_xticklabels([a[:12] for a in all_algos], rotation=45, ha='right', fontsize=9, color='white')
        
        labels = {'time': 'Sure (ms)', 'energy': 'Enerji (J)', 'memory': 'Bellek (MB)'}
        ax.set_ylabel(labels.get(metric, ''), color='white', fontsize=10)
        ax.set_title(title, color='white', fontsize=12, fontweight='bold', pad=10)
        
        ax.tick_params(axis='y', colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#2A303C')
        ax.spines['bottom'].set_color('#2A303C')
        ax.grid(axis='y', alpha=0.2, color='#2A303C')
        ax.legend(loc='upper right', fontsize=8, facecolor='#151922', edgecolor='#2A303C')
        
        self.figure.tight_layout()
        self.canvas.draw()


class ComparisonPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results_dir = Path(__file__).parent.parent.parent / 'results'
        self.test_files = {}  # {group: [{file, data, name}, ...]}
        self.selected_tests = []
        self.current_group = None
        self.init_ui()
        
    def init_ui(self):
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
        header = QLabel("Karsilastirma")
        header.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Colors.TEXT_MAIN};")
        layout.addWidget(header)
        
        desc = QLabel("Ayni gruptaki test sonuclarini karsilastirin ve analiz edin")
        desc.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_MUTED}; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # === GROUP SELECTION ===
        group_card = self._create_card()
        group_layout = QVBoxLayout(group_card)
        group_layout.setContentsMargins(24, 24, 24, 24)
        group_layout.setSpacing(16)
        
        group_title = QLabel("Grup Secimi")
        group_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        group_layout.addWidget(group_title)
        
        group_info = QLabel("Sadece ayni gruptaki testler karsilastirilabilir")
        group_info.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED};")
        group_layout.addWidget(group_info)
        
        # Group buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self.group_buttons = {}
        for key, name in ALGORITHM_GROUPS.items():
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._group_btn_style())
            btn.clicked.connect(lambda checked, k=key: self.select_group(k))
            self.group_buttons[key] = btn
            btn_row.addWidget(btn)
        
        btn_row.addStretch()
        
        self.refresh_btn = QPushButton("Yenile")
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Colors.ACCENT};
                border: 1px solid {Colors.ACCENT};
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background: {Colors.ACCENT}; color: white; }}
        """)
        self.refresh_btn.clicked.connect(self.load_results)
        btn_row.addWidget(self.refresh_btn)
        
        group_layout.addLayout(btn_row)
        layout.addWidget(group_card)
        
        # === TEST SELECTION ===
        self.test_card = self._create_card()
        test_layout = QVBoxLayout(self.test_card)
        test_layout.setContentsMargins(24, 24, 24, 24)
        test_layout.setSpacing(16)
        
        test_header = QHBoxLayout()
        self.test_title = QLabel("Testler")
        self.test_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        test_header.addWidget(self.test_title)
        test_header.addStretch()
        
        self.test_count_label = QLabel("0 test secildi")
        self.test_count_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px;")
        test_header.addWidget(self.test_count_label)
        
        test_layout.addLayout(test_header)
        
        # Test table
        self.test_table = QTableWidget()
        self.test_table.setColumnCount(5)
        self.test_table.setHorizontalHeaderLabels(["Sec", "Tarih", "Algoritmalar", "Boyutlar", "Dosya"])
        self.test_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.test_table.setStyleSheet(f"""
            QTableWidget {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MAIN};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
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
        self.test_table.setMinimumHeight(200)
        test_layout.addWidget(self.test_table)
        
        # Compare button
        compare_row = QHBoxLayout()
        
        self.compare_btn = QPushButton("KARSILASTIR")
        self.compare_btn.setFixedHeight(44)
        self.compare_btn.setCursor(Qt.PointingHandCursor)
        self.compare_btn.setStyleSheet(f"""
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
        self.compare_btn.clicked.connect(self.compare_tests)
        self.compare_btn.setEnabled(False)
        compare_row.addWidget(self.compare_btn)
        compare_row.addStretch()
        
        test_layout.addLayout(compare_row)
        
        # Initial state
        placeholder = QLabel("Yukaridan bir grup secin")
        placeholder.setStyleSheet(f"color: {Colors.TEXT_MUTED}; padding: 40px;")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setObjectName("placeholder")
        test_layout.addWidget(placeholder)
        
        self.test_table.hide()
        self.compare_btn.hide()
        
        layout.addWidget(self.test_card)
        
        # === RESULTS SECTION ===
        self.results_card = self._create_card()
        self.results_card.hide()
        results_layout = QVBoxLayout(self.results_card)
        results_layout.setContentsMargins(24, 24, 24, 24)
        results_layout.setSpacing(16)
        
        results_title = QLabel("Karsilastirma Sonuclari")
        results_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        results_layout.addWidget(results_title)
        
        # Tabs
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
        
        # Tab 1: Time Chart
        time_tab = QWidget()
        time_layout = QVBoxLayout(time_tab)
        time_layout.setContentsMargins(16, 16, 16, 16)
        self.time_chart = ChartCanvas()
        self.time_chart.setMinimumHeight(350)
        time_layout.addWidget(self.time_chart)
        self.tabs.addTab(time_tab, "Calisma Suresi")
        
        # Tab 2: Energy Chart
        energy_tab = QWidget()
        energy_layout = QVBoxLayout(energy_tab)
        energy_layout.setContentsMargins(16, 16, 16, 16)
        self.energy_chart = ChartCanvas()
        self.energy_chart.setMinimumHeight(350)
        energy_layout.addWidget(self.energy_chart)
        self.tabs.addTab(energy_tab, "Enerji Tuketimi")
        
        # Tab 3: Memory Chart
        memory_tab = QWidget()
        memory_layout = QVBoxLayout(memory_tab)
        memory_layout.setContentsMargins(16, 16, 16, 16)
        self.memory_chart = ChartCanvas()
        self.memory_chart.setMinimumHeight(350)
        memory_layout.addWidget(self.memory_chart)
        self.tabs.addTab(memory_tab, "Bellek Kullanimi")
        
        # Tab 4: Comparison Table
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        table_layout.setContentsMargins(16, 16, 16, 16)
        
        self.comparison_table = QTableWidget()
        self.comparison_table.setStyleSheet(f"""
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
        table_layout.addWidget(self.comparison_table)
        self.tabs.addTab(table_tab, "Detayli Tablo")
        
        results_layout.addWidget(self.tabs)
        layout.addWidget(self.results_card)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Load initial data
        self.load_results()
    
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
    
    def _group_btn_style(self):
        return f"""
            QPushButton {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MAIN};
                border: 2px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 13px;
            }}
            QPushButton:hover {{ border-color: {Colors.ACCENT}; }}
            QPushButton:checked {{
                border-color: {Colors.ACCENT};
                background: rgba(76, 201, 240, 0.15);
                color: {Colors.ACCENT};
            }}
        """
    
    def load_results(self):
        """Load all test results and categorize by group"""
        self.test_files = {k: [] for k in ALGORITHM_GROUPS.keys()}
        
        if not self.results_dir.exists():
            return
        
        # Load energy_analysis files
        patterns = ['energy_analysis_*.json', 'energy_benchmark_*.json']
        
        for pattern in patterns:
            for f in self.results_dir.glob(pattern):
                try:
                    with open(f, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    
                    # Determine group from algorithms in the file
                    group = self._detect_group(data)
                    if group:
                        self.test_files[group].append({
                            'file': f,
                            'data': data,
                            'name': f.stem,
                            'date': self._get_date_from_file(f, data)
                        })
                except Exception as e:
                    print(f"Error loading {f}: {e}")
        
        # Refresh current display
        if self.current_group:
            self.display_group_tests(self.current_group)
    
    def _detect_group(self, data):
        """Detect algorithm group from test data"""
        # Check for new format (energy_analysis)
        if isinstance(data, dict):
            for key in data.keys():
                if key in ['divide_conquer', 'dynamic_programming', 'greedy']:
                    continue
                # Check algorithm names
                for group, algos in self._get_group_algorithms().items():
                    if key in algos:
                        return group
        
        # Check for old format (energy_benchmark)
        if 'benchmarks' in data:
            for b in data.get('benchmarks', []):
                algo = b.get('algorithm', '')
                for group, algos in self._get_group_algorithms().items():
                    if algo in algos:
                        return group
        
        return 'divide_conquer'  # Default
    
    def _get_group_algorithms(self):
        """Get algorithms for each group"""
        from algorithms import ALGORITHMS
        return {
            'divide_conquer': list(ALGORITHMS.get('divide_conquer', {}).keys()),
            'dynamic_programming': list(ALGORITHMS.get('dynamic_programming', {}).keys()),
            'greedy': list(ALGORITHMS.get('greedy', {}).keys())
        }
    
    def _get_date_from_file(self, filepath, data):
        """Extract date from file"""
        # Try from filename
        name = filepath.stem
        if '_' in name:
            parts = name.split('_')
            for part in parts:
                if len(part) == 8 and part.isdigit():
                    return f"{part[:4]}-{part[4:6]}-{part[6:8]}"
        
        # Try from data
        if 'meta' in data:
            return data['meta'].get('timestamp', 'N/A')[:10]
        
        return 'N/A'
    
    def select_group(self, group_key):
        """Select algorithm group"""
        self.current_group = group_key
        
        # Update button states
        for k, btn in self.group_buttons.items():
            btn.setChecked(k == group_key)
        
        self.display_group_tests(group_key)
    
    def display_group_tests(self, group_key):
        """Display tests for selected group"""
        tests = self.test_files.get(group_key, [])
        
        # Remove placeholder
        placeholder = self.test_card.findChild(QLabel, "placeholder")
        if placeholder:
            placeholder.hide()
        
        # Show table and button
        self.test_table.show()
        self.compare_btn.show()
        
        # Update title
        group_name = ALGORITHM_GROUPS.get(group_key, group_key)
        self.test_title.setText(f"{group_name} Testleri ({len(tests)})")
        
        # Fill table
        self.test_table.setRowCount(0)
        self.selected_tests = []
        
        if not tests:
            self.test_table.setRowCount(1)
            item = QTableWidgetItem("Bu grup icin test bulunamadi")
            item.setTextAlignment(Qt.AlignCenter)
            self.test_table.setItem(0, 1, item)
            self.test_table.setSpan(0, 0, 1, 5)
            return
        
        for test in tests:
            row = self.test_table.rowCount()
            self.test_table.insertRow(row)
            
            # Checkbox
            chk = QCheckBox()
            chk.setProperty('test_data', test)
            chk.stateChanged.connect(self.update_selection)
            
            cell = QWidget()
            cell_layout = QHBoxLayout(cell)
            cell_layout.addWidget(chk)
            cell_layout.setAlignment(Qt.AlignCenter)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            self.test_table.setCellWidget(row, 0, cell)
            
            # Date
            self.test_table.setItem(row, 1, QTableWidgetItem(test['date']))
            
            # Algorithms
            algos = list(test['data'].keys())[:3]
            algos_str = ', '.join(algos)
            if len(test['data']) > 3:
                algos_str += f" (+{len(test['data'])-3})"
            self.test_table.setItem(row, 2, QTableWidgetItem(algos_str))
            
            # Sizes
            sizes = set()
            for algo_data in test['data'].values():
                if isinstance(algo_data, dict) and 'sizes' in algo_data:
                    sizes.update(algo_data['sizes'].keys())
            sizes_str = ', '.join(str(s) for s in sorted(sizes)[:4])
            self.test_table.setItem(row, 3, QTableWidgetItem(sizes_str))
            
            # Filename
            self.test_table.setItem(row, 4, QTableWidgetItem(test['name'][:30]))
    
    def update_selection(self):
        """Update selected tests"""
        self.selected_tests = []
        
        for row in range(self.test_table.rowCount()):
            cell = self.test_table.cellWidget(row, 0)
            if cell:
                chk = cell.layout().itemAt(0).widget()
                if chk and chk.isChecked():
                    test_data = chk.property('test_data')
                    if test_data:
                        self.selected_tests.append(test_data)
        
        count = len(self.selected_tests)
        self.test_count_label.setText(f"{count} test secildi")
        self.compare_btn.setEnabled(count >= 1)
    
    def compare_tests(self):
        """Compare selected tests"""
        if not self.selected_tests:
            return
        
        # Prepare data for comparison
        comparison_data = {}
        
        for test in self.selected_tests:
            test_name = test['name'][:20]
            comparison_data[test_name] = test['data']
        
        # Show results
        self.results_card.show()
        
        # Plot charts
        self.time_chart.plot_grouped_bar(comparison_data, 'time', 'Calisma Suresi Karsilastirmasi')
        self.energy_chart.plot_grouped_bar(comparison_data, 'energy', 'Enerji Tuketimi Karsilastirmasi')
        self.memory_chart.plot_grouped_bar(comparison_data, 'memory', 'Bellek Kullanimi Karsilastirmasi')
        
        # Fill comparison table
        self.fill_comparison_table(comparison_data)
    
    def fill_comparison_table(self, comparison_data):
        """Fill the detailed comparison table"""
        if not comparison_data:
            return
        
        # Get all algorithms
        all_algos = set()
        for test_data in comparison_data.values():
            all_algos.update(test_data.keys())
        all_algos = sorted(list(all_algos))
        
        test_names = list(comparison_data.keys())
        
        # Setup table
        cols = ['Algoritma'] + [f"{t} (Sure)" for t in test_names] + [f"{t} (Enerji)" for t in test_names]
        self.comparison_table.setColumnCount(len(cols))
        self.comparison_table.setHorizontalHeaderLabels(cols)
        self.comparison_table.setRowCount(len(all_algos))
        
        for i, algo in enumerate(all_algos):
            self.comparison_table.setItem(i, 0, QTableWidgetItem(algo))
            
            col = 1
            # Time columns
            for test_name in test_names:
                test_data = comparison_data[test_name]
                if algo in test_data:
                    val = test_data[algo].get('avg_time', 0)
                    self.comparison_table.setItem(i, col, QTableWidgetItem(f"{val:.4f}"))
                else:
                    self.comparison_table.setItem(i, col, QTableWidgetItem("-"))
                col += 1
            
            # Energy columns
            for test_name in test_names:
                test_data = comparison_data[test_name]
                if algo in test_data:
                    val = test_data[algo].get('avg_energy', 0)
                    self.comparison_table.setItem(i, col, QTableWidgetItem(f"{val:.6f}"))
                else:
                    self.comparison_table.setItem(i, col, QTableWidgetItem("-"))
                col += 1
        
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
