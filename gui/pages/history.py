"""
Geçmiş Sayfası - Modern Tasarım
"""

import json
import os
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, 
    QPushButton, QMessageBox, QGraphicsDropShadowEffect,
    QDialog, QTextEdit, QTabWidget, QGridLayout, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from gui.styles import Colors

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


class TestDetailDialog(QDialog):
    """Test detay dialogu"""
    
    def __init__(self, filepath, data, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.data = data
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Test Detaylari")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background: {Colors.BG_DARK};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header = QLabel(f"Test Detaylari")
        header.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Colors.TEXT_MAIN};")
        layout.addWidget(header)
        
        filename = QLabel(Path(self.filepath).name)
        filename.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED};")
        layout.addWidget(filename)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                background: {Colors.BG_CARD};
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
        
        # Tab 1: Summary
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        
        # Calculate stats
        algo_count = len(self.data) if isinstance(self.data, dict) else 0
        sizes = set()
        total_time = 0
        total_energy = 0
        
        if isinstance(self.data, dict):
            for key, info in self.data.items():
                if isinstance(info, dict):
                    if 'sizes' in info:
                        sizes.update(info['sizes'].keys())
                    total_time += info.get('avg_time', 0)
                    total_energy += info.get('avg_energy', 0)
        
        # Stat cards
        stats = [
            ("Algoritma Sayisi", str(algo_count), Colors.ACCENT),
            ("Boyut Sayisi", str(len(sizes)), Colors.PRIMARY),
            ("Toplam Sure", f"{total_time:.2f} ms", "#10B981"),
            ("Toplam Enerji", f"{total_energy:.4f} J", "#F59E0B")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background: {Colors.BG_DARKER};
                    border-radius: 8px;
                    border-left: 3px solid {color};
                }}
            """)
            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setContentsMargins(16, 12, 16, 12)
            
            val_label = QLabel(value)
            val_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
            
            name_label = QLabel(label)
            name_label.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED};")
            
            stat_layout.addWidget(val_label)
            stat_layout.addWidget(name_label)
            
            stats_grid.addWidget(stat_frame, 0, i)
        
        summary_layout.addLayout(stats_grid)
        
        # Algorithm list
        algo_label = QLabel("Algoritmalar:")
        algo_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Colors.TEXT_MAIN}; margin-top: 16px;")
        summary_layout.addWidget(algo_label)
        
        algo_table = QTableWidget()
        algo_table.setColumnCount(4)
        algo_table.setHorizontalHeaderLabels(["Algoritma", "Ort. Sure (ms)", "Ort. Enerji (J)", "Ort. Bellek (KB)"])
        algo_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        algo_table.setStyleSheet(f"""
            QTableWidget {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MAIN};
                border: none;
                gridline-color: {Colors.BORDER};
            }}
            QHeaderView::section {{
                background: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
                padding: 8px;
                border: none;
            }}
        """)
        
        if isinstance(self.data, dict):
            algo_table.setRowCount(len(self.data))
            for i, (key, info) in enumerate(self.data.items()):
                if isinstance(info, dict):
                    algo_table.setItem(i, 0, QTableWidgetItem(info.get('name', key)))
                    algo_table.setItem(i, 1, QTableWidgetItem(f"{info.get('avg_time', 0):.4f}"))
                    algo_table.setItem(i, 2, QTableWidgetItem(f"{info.get('avg_energy', 0):.6f}"))
                    algo_table.setItem(i, 3, QTableWidgetItem(f"{info.get('avg_memory', 0):.2f}"))
        
        summary_layout.addWidget(algo_table)
        tabs.addTab(summary_tab, "Ozet")
        
        # Tab 2: Chart
        if HAS_MATPLOTLIB:
            chart_tab = QWidget()
            chart_layout = QVBoxLayout(chart_tab)
            chart_layout.setContentsMargins(16, 16, 16, 16)
            
            plt.style.use('dark_background')
            figure = Figure(figsize=(8, 5), facecolor='#151922')
            canvas = FigureCanvas(figure)
            
            ax = figure.add_subplot(111)
            ax.set_facecolor('#151922')
            
            names = []
            times = []
            colors = ['#4CC9F0', '#F72585', '#4361EE', '#10B981', '#F59E0B', '#EF4444']
            
            if isinstance(self.data, dict):
                for key, info in self.data.items():
                    if isinstance(info, dict):
                        names.append(info.get('name', key)[:15])
                        times.append(info.get('avg_time', 0))
            
            if names:
                bars = ax.barh(range(len(names)), times, color=colors[:len(names)], height=0.6)
                ax.set_yticks(range(len(names)))
                ax.set_yticklabels(names, fontsize=10, color='white')
                ax.invert_yaxis()
                ax.set_xlabel('Sure (ms)', color='white')
                ax.set_title('Algoritma Performansi', color='white', fontsize=12, fontweight='bold')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_color('#2A303C')
                ax.tick_params(axis='x', colors='white')
                ax.grid(axis='x', alpha=0.2, color='#2A303C')
            
            figure.tight_layout()
            canvas.draw()
            
            chart_layout.addWidget(canvas)
            tabs.addTab(chart_tab, "Grafik")
        
        # Tab 3: Raw JSON
        json_tab = QWidget()
        json_layout = QVBoxLayout(json_tab)
        json_layout.setContentsMargins(16, 16, 16, 16)
        
        json_text = QTextEdit()
        json_text.setReadOnly(True)
        json_text.setStyleSheet(f"""
            QTextEdit {{
                background: {Colors.BG_DARKER};
                color: {Colors.ACCENT};
                border: none;
                font-family: Consolas, monospace;
                font-size: 11px;
                padding: 12px;
            }}
        """)
        json_text.setText(json.dumps(self.data, indent=2, ensure_ascii=False))
        json_layout.addWidget(json_text)
        tabs.addTab(json_tab, "JSON")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #5A7BFF; }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)


class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results_dir = Path(__file__).parent.parent.parent / 'results'
        self.all_tests = []
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
        header_row = QHBoxLayout()
        
        header = QLabel("Test Gecmisi")
        header.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Colors.TEXT_MAIN};")
        header_row.addWidget(header)
        
        header_row.addStretch()
        
        # Stats
        self.stats_label = QLabel("0 test")
        self.stats_label.setStyleSheet(f"""
            background: {Colors.BG_CARD};
            color: {Colors.ACCENT};
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: bold;
        """)
        header_row.addWidget(self.stats_label)
        
        layout.addLayout(header_row)
        
        desc = QLabel("Gecmis test sonuclarini goruntuleyin ve yonetin")
        desc.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_MUTED}; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # === CONTROLS ===
        controls_card = self._create_card()
        controls_layout = QHBoxLayout(controls_card)
        controls_layout.setContentsMargins(20, 16, 20, 16)
        controls_layout.setSpacing(12)
        
        self.refresh_btn = QPushButton("Yenile")
        self.refresh_btn.setStyleSheet(self._btn_style(Colors.ACCENT))
        self.refresh_btn.clicked.connect(self.load_history)
        controls_layout.addWidget(self.refresh_btn)
        
        self.clear_all_btn = QPushButton("Tumunu Sil")
        self.clear_all_btn.setStyleSheet(self._btn_style(Colors.DANGER))
        self.clear_all_btn.clicked.connect(self.clear_all)
        controls_layout.addWidget(self.clear_all_btn)
        
        controls_layout.addStretch()
        
        # Search placeholder (for future)
        search_label = QLabel("Toplam: ")
        search_label.setStyleSheet(f"color: {Colors.TEXT_MUTED};")
        controls_layout.addWidget(search_label)
        
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-weight: bold;")
        controls_layout.addWidget(self.total_label)
        
        layout.addWidget(controls_card)
        
        # === TEST LIST ===
        list_card = self._create_card()
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(24, 24, 24, 24)
        list_layout.setSpacing(16)
        
        list_title = QLabel("Test Kayitlari")
        list_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        list_layout.addWidget(list_title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Tarih", "Tur", "Algoritmalar", "Boyutlar", "Dosya", "Islemler"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {Colors.BG_DARKER};
                color: {Colors.TEXT_MAIN};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                gridline-color: {Colors.BORDER};
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {Colors.BORDER};
            }}
            QTableWidget::item:selected {{
                background: rgba(76, 201, 240, 0.2);
            }}
            QHeaderView::section {{
                background: {Colors.BG_CARD};
                color: {Colors.TEXT_MAIN};
                padding: 12px;
                border: none;
                font-weight: bold;
            }}
        """)
        self.table.setMinimumHeight(400)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(False)
        
        list_layout.addWidget(self.table)
        
        layout.addWidget(list_card)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Load data
        self.load_history()
    
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
    
    def _btn_style(self, color):
        return f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {color};
                color: white;
            }}
        """
    
    def load_history(self):
        """Load all test history"""
        self.table.setRowCount(0)
        self.all_tests = []
        
        if not self.results_dir.exists():
            self.stats_label.setText("0 test")
            self.total_label.setText("0")
            return
        
        # Load all JSON files
        patterns = ['energy_analysis_*.json', 'energy_benchmark_*.json']
        
        for pattern in patterns:
            for f in sorted(self.results_dir.glob(pattern), reverse=True):
                try:
                    with open(f, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    
                    self.all_tests.append({
                        'file': f,
                        'data': data,
                        'type': 'analysis' if 'energy_analysis' in f.name else 'benchmark'
                    })
                except Exception as e:
                    print(f"Error loading {f}: {e}")
        
        # Update stats
        self.stats_label.setText(f"{len(self.all_tests)} test")
        self.total_label.setText(str(len(self.all_tests)))
        
        # Fill table
        for test in self.all_tests:
            self._add_table_row(test)
    
    def _add_table_row(self, test):
        """Add a row to the table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        filepath = test['file']
        data = test['data']
        test_type = test['type']
        
        # Date
        date_str = self._extract_date(filepath.name, data)
        date_item = QTableWidgetItem(date_str)
        date_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, date_item)
        
        # Type
        type_str = "Enerji Analizi" if test_type == 'analysis' else "Benchmark"
        type_item = QTableWidgetItem(type_str)
        type_item.setTextAlignment(Qt.AlignCenter)
        if test_type == 'analysis':
            type_item.setForeground(QColor(Colors.ACCENT))
        else:
            type_item.setForeground(QColor(Colors.PRIMARY))
        self.table.setItem(row, 1, type_item)
        
        # Algorithms
        algos = self._extract_algorithms(data)
        algo_str = ', '.join(algos[:3])
        if len(algos) > 3:
            algo_str += f" (+{len(algos)-3})"
        self.table.setItem(row, 2, QTableWidgetItem(algo_str))
        
        # Sizes
        sizes = self._extract_sizes(data)
        size_str = ', '.join(str(s) for s in sizes[:4])
        if len(sizes) > 4:
            size_str += f" (+{len(sizes)-4})"
        self.table.setItem(row, 3, QTableWidgetItem(size_str))
        
        # Filename
        self.table.setItem(row, 4, QTableWidgetItem(filepath.name[:35]))
        
        # Actions
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(4, 4, 4, 4)
        btn_layout.setSpacing(6)
        
        view_btn = QPushButton("Gor")
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background: #5A7BFF; }}
        """)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.clicked.connect(lambda checked, t=test: self.view_result(t))
        
        del_btn = QPushButton("Sil")
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.DANGER};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background: #DC2626; }}
        """)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda checked, f=filepath: self.delete_result(f))
        
        btn_layout.addWidget(view_btn)
        btn_layout.addWidget(del_btn)
        self.table.setCellWidget(row, 5, btn_widget)
    
    def _extract_date(self, filename, data):
        """Extract date from filename or data"""
        # From filename
        parts = filename.replace('.json', '').split('_')
        for part in parts:
            if len(part) == 8 and part.isdigit():
                return f"{part[:4]}-{part[4:6]}-{part[6:8]}"
        
        # From data
        if 'meta' in data:
            return data['meta'].get('timestamp', 'N/A')[:10]
        
        return 'N/A'
    
    def _extract_algorithms(self, data):
        """Extract algorithm list from data"""
        algos = []
        
        # New format
        if isinstance(data, dict):
            for key, info in data.items():
                if isinstance(info, dict) and 'name' in info:
                    algos.append(info['name'])
                elif key not in ['meta', 'benchmarks']:
                    algos.append(key)
        
        # Old format
        if 'benchmarks' in data:
            for b in data['benchmarks']:
                algo = b.get('algorithm', '')
                if algo and algo not in algos:
                    algos.append(algo)
        
        return algos
    
    def _extract_sizes(self, data):
        """Extract data sizes from data"""
        sizes = set()
        
        # New format
        if isinstance(data, dict):
            for key, info in data.items():
                if isinstance(info, dict) and 'sizes' in info:
                    sizes.update(int(s) for s in info['sizes'].keys())
        
        # Old format
        if 'benchmarks' in data:
            for b in data['benchmarks']:
                size = b.get('size', 0)
                if size:
                    sizes.add(size)
        
        return sorted(sizes)
    
    def view_result(self, test):
        """Show test details dialog"""
        dialog = TestDetailDialog(str(test['file']), test['data'], self)
        dialog.exec_()
    
    def delete_result(self, filepath):
        """Delete a test result"""
        reply = QMessageBox.question(
            self, 
            'Sil', 
            f"Bu kaydi silmek istediginize emin misiniz?\n\n{filepath.name}",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(filepath)
                self.load_history()
                QMessageBox.information(self, "Basarili", "Kayit silindi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))
    
    def clear_all(self):
        """Delete all test results"""
        if not self.all_tests:
            QMessageBox.information(self, "Bilgi", "Silinecek kayit yok.")
            return
        
        reply = QMessageBox.question(
            self, 
            'Tumunu Sil', 
            f"TUM {len(self.all_tests)} kaydi silmek istediginize emin misiniz?\n\nBu islem geri alinamaz!",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted = 0
            for test in self.all_tests:
                try:
                    os.remove(test['file'])
                    deleted += 1
                except:
                    pass
            
            self.load_history()
            QMessageBox.information(self, "Basarili", f"{deleted} kayit silindi.")
