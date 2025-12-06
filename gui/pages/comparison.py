"""
Karşılaştırma Sayfası
"""

import json
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from gui.styles import Styles, Colors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ComparisonPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results_dir = Path(__file__).parent.parent.parent / 'results'
        self.selected_files = []
        self.init_ui()
        self.load_results()

    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(Styles.PAGE_CONTAINER)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("📊 Algoritma Karşılaştırma")
        header.setStyleSheet(Styles.LABEL_TITLE)
        
        subtitle = QLabel("Birden fazla test sonucunu karşılaştırarak algoritmaların performansını analiz edin")
        subtitle.setStyleSheet(Styles.LABEL_SUBTITLE)
        
        layout.addWidget(header)
        layout.addWidget(subtitle)
        
        # Selection Card
        card = QFrame()
        card.setStyleSheet(Styles.CARD)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        
        card_title = QLabel("Karşılaştırılacak Testleri Seçin")
        card_title.setStyleSheet("font-size: 18px; font-weight: 600; color: " + Colors.TEXT_MAIN)
        card_layout.addWidget(card_title)
        
        # Filter (Simplified)
        filter_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Yenile")
        self.refresh_btn.setStyleSheet(Styles.BUTTON_OUTLINE)
        self.refresh_btn.clicked.connect(self.load_results)
        filter_layout.addWidget(self.refresh_btn)
        filter_layout.addStretch()
        card_layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Seç", "Tarih", "Algoritmalar", "Veri Boyutları", "Dosya"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setStyleSheet(Styles.TABLE)
        card_layout.addWidget(self.table)
        
        # Compare Button
        self.compare_btn = QPushButton("📊 Karşılaştır")
        self.compare_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.compare_btn.clicked.connect(self.compare_tests)
        self.compare_btn.setEnabled(False)
        card_layout.addWidget(self.compare_btn, alignment=Qt.AlignCenter)
        
        layout.addWidget(card)
        
        # Results Section (Initially Hidden)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0,0,0,0)
        self.results_container.setVisible(False)
        
        # Charts
        charts_layout = QHBoxLayout()
        
        # Time Chart
        self.time_figure = plt.figure(figsize=(5, 4), facecolor=Colors.BG_CARD)
        self.time_canvas = FigureCanvas(self.time_figure)
        charts_layout.addWidget(self.time_canvas)
        
        # Energy Chart
        self.energy_figure = plt.figure(figsize=(5, 4), facecolor=Colors.BG_CARD)
        self.energy_canvas = FigureCanvas(self.energy_figure)
        charts_layout.addWidget(self.energy_canvas)
        
        self.results_layout.addLayout(charts_layout)
        
        layout.addWidget(self.results_container)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def load_results(self):
        self.table.setRowCount(0)
        if not self.results_dir.exists():
            return
            
        files = sorted(self.results_dir.glob("energy_benchmark_*.json"), reverse=True)
        
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Checkbox
                chk = QCheckBox()
                chk.stateChanged.connect(self.update_selection)
                cell_widget = QWidget()
                layout = QHBoxLayout(cell_widget)
                layout.addWidget(chk)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0,0,0,0)
                self.table.setCellWidget(row, 0, cell_widget)
                
                # Date
                date_str = data.get('meta', {}).get('timestamp', 'N/A')
                self.table.setItem(row, 1, QTableWidgetItem(date_str))
                
                # Algorithms
                algos = set()
                sizes = set()
                for b in data.get('benchmarks', []):
                    algos.add(b.get('algorithm', 'Unknown'))
                    sizes.add(str(b.get('size', 0)))
                
                self.table.setItem(row, 2, QTableWidgetItem(", ".join(algos)))
                self.table.setItem(row, 3, QTableWidgetItem(", ".join(sizes)))
                self.table.setItem(row, 4, QTableWidgetItem(f.name))
                
                # Store file path in item data
                self.table.item(row, 1).setData(Qt.UserRole, str(f))
                
            except Exception as e:
                print(f"Error loading {f}: {e}")

    def update_selection(self):
        self.selected_files = []
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            chk = cell_widget.layout().itemAt(0).widget()
            if chk.isChecked():
                file_path = self.table.item(row, 1).data(Qt.UserRole)
                self.selected_files.append(file_path)
        
        self.compare_btn.setEnabled(len(self.selected_files) > 0)

    def compare_tests(self):
        if not self.selected_files:
            return
            
        all_data = []
        for f_path in self.selected_files:
            with open(f_path, 'r', encoding='utf-8') as f:
                all_data.append(json.load(f))
        
        self.plot_charts(all_data)
        self.results_container.setVisible(True)

    def plot_charts(self, all_data):
        # Prepare data for plotting
        # We need to aggregate data by algorithm and size
        # For simplicity, let's plot Average Time and Energy per Algorithm (averaged over sizes if multiple)
        
        algo_stats = {}
        
        for data in all_data:
            for b in data.get('benchmarks', []):
                algo = b.get('algorithm')
                if algo not in algo_stats:
                    algo_stats[algo] = {'time': [], 'energy': []}
                
                avg = b.get('averages', {})
                algo_stats[algo]['time'].append(avg.get('execution_time_ms', 0))
                algo_stats[algo]['energy'].append(avg.get('energy_joules', 0))
        
        algos = list(algo_stats.keys())
        avg_times = [sum(algo_stats[a]['time'])/len(algo_stats[a]['time']) for a in algos]
        avg_energies = [sum(algo_stats[a]['energy'])/len(algo_stats[a]['energy']) for a in algos]
        
        # Time Chart
        self.time_figure.clear()
        ax1 = self.time_figure.add_subplot(111)
        ax1.bar(algos, avg_times, color=Colors.PRIMARY)
        ax1.set_title('Ortalama Çalışma Süresi (ms)', color=Colors.TEXT_MAIN)
        ax1.tick_params(colors=Colors.TEXT_MUTED)
        ax1.set_facecolor(Colors.BG_CARD)
        self.time_figure.patch.set_facecolor(Colors.BG_CARD)
        self.time_canvas.draw()
        
        # Energy Chart
        self.energy_figure.clear()
        ax2 = self.energy_figure.add_subplot(111)
        ax2.bar(algos, avg_energies, color=Colors.ACCENT)
        ax2.set_title('Ortalama Enerji Tüketimi (J)', color=Colors.TEXT_MAIN)
        ax2.tick_params(colors=Colors.TEXT_MUTED)
        ax2.set_facecolor(Colors.BG_CARD)
        self.energy_figure.patch.set_facecolor(Colors.BG_CARD)
        self.energy_canvas.draw()
