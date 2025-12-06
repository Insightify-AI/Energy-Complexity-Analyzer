"""
Geçmiş Sayfası
"""

import json
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, 
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from gui.styles import Styles, Colors

class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results_dir = Path(__file__).parent.parent.parent / 'results'
        self.init_ui()
        self.load_history()

    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(Styles.PAGE_CONTAINER)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("📜 Test Geçmişi")
        header.setStyleSheet(Styles.LABEL_TITLE)
        
        layout.addWidget(header)
        
        # Table Card
        card = QFrame()
        card.setStyleSheet(Styles.CARD)
        card_layout = QVBoxLayout(card)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tarih", "Algoritmalar", "Veri Boyutları", "İşlemler"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(Styles.TABLE)
        card_layout.addWidget(self.table)
        
        layout.addWidget(card)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def load_history(self):
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
                
                date_str = data.get('meta', {}).get('timestamp', 'N/A')
                self.table.setItem(row, 0, QTableWidgetItem(date_str))
                
                algos = set()
                sizes = set()
                for b in data.get('benchmarks', []):
                    algos.add(b.get('algorithm', 'Unknown'))
                    sizes.add(str(b.get('size', 0)))
                
                self.table.setItem(row, 1, QTableWidgetItem(", ".join(algos)))
                self.table.setItem(row, 2, QTableWidgetItem(", ".join(sizes)))
                
                # Actions
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0,0,0,0)
                
                view_btn = QPushButton("👁️")
                view_btn.setToolTip("Görüntüle")
                view_btn.clicked.connect(lambda checked, path=f: self.view_result(path))
                
                del_btn = QPushButton("🗑️")
                del_btn.setToolTip("Sil")
                del_btn.clicked.connect(lambda checked, path=f: self.delete_result(path))
                
                btn_layout.addWidget(view_btn)
                btn_layout.addWidget(del_btn)
                self.table.setCellWidget(row, 3, btn_widget)
                
            except Exception as e:
                print(f"Error loading {f}: {e}")

    def view_result(self, path):
        # TODO: Open detailed view
        QMessageBox.information(self, "Bilgi", f"Dosya yolu: {path}\nDetaylı görünüm eklenecek.")

    def delete_result(self, path):
        reply = QMessageBox.question(self, 'Sil', "Bu kaydı silmek istediğinize emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(path)
                self.load_history()
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))
