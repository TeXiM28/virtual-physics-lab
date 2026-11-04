import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QTextEdit, QMessageBox, QFileDialog, QSplitter)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from arrow_widget import ArrowInstrument
from digital_widget import DigitalMultimeter
from rheostat_widget import VirtualRheostat
from solenoid_widget import VirtualSolenoid
import physics

class VirtualLabStand(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР №19: Метод магнетрона")
        self.setGeometry(30, 30, 1300, 800)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)
        
        # --- ЗОНА 1: ЦИФРОВОЙ ДВОЙНИК СТЕНДА С КЛЮЧАМИ ---
        stand_widget = QWidget()
        stand_widget.setStyleSheet("background-color: #2D1A14; border: 4px solid #1A0C00;") 
        stand_layout = QVBoxLayout(stand_widget)
        
        keys_layout = QHBoxLayout()
        self.btn_fork = QPushButton("Вилка: ВЫКЛ (~220В)")
        self.btn_sa2 = QPushButton("SA2 (Накал): ВЫКЛ")
        self.btn_sa3 = QPushButton("SA3 (Анод): ВЫКЛ")
        self.btn_sa1 = QPushButton("SA1 (Соленоид): ВЫКЛ")
        
        self.keys_list = [self.btn_fork, self.btn_sa2, self.btn_sa3, self.btn_sa1]
        for btn in self.keys_list:
            btn.setCheckable(True)
            btn.setStyleSheet("background-color: #757575; color: white; font-weight: bold; padding: 8px; border: 1px solid #000;")
            btn.clicked.connect(self.sync_simulation)
            keys_layout.addWidget(btn)
        stand_layout.addLayout(keys_layout)
        
        wiring_row_layout = QHBoxLayout()
        self.rheostat_ua = VirtualRheostat("Реостат анода U_a", min_val=10, max_val=50, start_val=30)
        self.rheostat_ua.valueChanged.connect(self.sync_simulation)
        wiring_row_layout.addWidget(self.rheostat_ua)
        
        self.solenoid_visual = VirtualSolenoid()
        wiring_row_layout.addWidget(self.solenoid_visual)
        
        self.ammeter_anode = ArrowInstrument("Анодный ток (I_a)", "мкА", max_val=60.0)
        wiring_row_layout.addWidget(self.ammeter_anode)
        
        self.rheostat_ic = VirtualRheostat("Реостат катушки I_c", min_val=0, max_val=200, start_val=0)
        self.rheostat_ic.valueChanged.connect(self.sync_simulation)
        wiring_row_layout.addWidget(self.rheostat_ic)
        stand_layout.addLayout(wiring_row_layout)
        
        bottom_row_layout = QHBoxLayout()
        self.voltmeter_anode = DigitalMultimeter("Цифровой вольтметр (U_a)", "В")
        self.multimeter_ic = DigitalMultimeter("Контроль тока катушки (I_c)", "А")
        bottom_row_layout.addWidget(self.voltmeter_anode)
        bottom_row_layout.addWidget(self.multimeter_ic)
        stand_layout.addLayout(bottom_row_layout)
        
        self.lbl_status = QLabel("Стенд обесточен. Включите вилку в сеть ~220В.")
        self.lbl_status.setStyleSheet("color: #E0E0E0; font-style: italic; padding: 5px;")
        stand_layout.addWidget(self.lbl_status)
        main_splitter.addWidget(stand_widget)
        
        # --- ЗОНА 2: ЖУРНАЛ И ИСПРАВЛЕННЫЙ ГРАФИК ---
        notebook_widget = QWidget()
        notebook_layout = QVBoxLayout(notebook_widget)
        
        self.table = QTableWidget(11, 3)
        self.table.setHorizontalHeaderLabels(["U_a, В", "I_c, А", "I_a, мкА (Ввод)"])
        for i in range(11):
            self.table.setItem(i, 0, QTableWidgetItem("30.0"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{i*0.15:.2f}"))
        notebook_layout.addWidget(self.table)
        
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("I_a = f(I_c)", fontsize=10)
        self.ax.set_xlabel("I_c, А", fontsize=9)
        self.ax.set_ylabel("I_a, мкА", fontsize=9)
        self.ax.tick_params(axis='both', labelsize=8)
        self.ax.grid(True)
        self.fig.tight_layout() 
        notebook_layout.addWidget(self.canvas)
        
        self.btn_calc = QPushButton("📊 Обработать данные и выставить оценку")
        self.btn_calc.setStyleSheet("background-color: #0288D1; color: white; font-weight: bold; padding: 8px;")
        self.btn_calc.clicked.connect(self.process_lab_data)
        notebook_layout.addWidget(self.btn_calc)
        
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        notebook_layout.addWidget(self.result_view)
        
        main_splitter.addWidget(notebook_widget)
        main_splitter.setSizes([800, 400])

    def sync_simulation(self):
        style_on = "background-color: #2ECC71; color: white; font-weight: bold; padding: 8px; border: 1px solid #000;"
        style_off = "background-color: #757575; color: white; font-weight: bold; padding: 8px; border: 1px solid #000;"
        
        self.btn_fork.setText("Вилка: ВКЛ (~220В)" if self.btn_fork.isChecked() else "Вилка: ВЫКЛ (~220В)")
        self.btn_sa2.setText("SA2 (Накал): ВКЛ" if self.btn_sa2.isChecked() else "SA2 (Накал): ВЫКЛ")
        self.btn_sa3.setText("SA3 (Анод): ВКЛ" if self.btn_sa3.isChecked() else "SA3 (Анод): ВЫКЛ")
        self.btn_sa1.setText("SA1 (Соленоид): ВКЛ" if self.btn_sa1.isChecked() else "SA1 (Соленоид): ВЫКЛ")
        
        for btn in self.keys_list:
            btn.setStyleSheet(style_on if btn.isChecked() else style_off)

        has_main_power = self.btn_fork.isChecked()
        sa2_heater = self.btn_sa2.isChecked()
        sa3_anode = self.btn_sa3.isChecked()
        sa1_solenoid = self.btn_sa1.isChecked()
        
        U_a = float(self.rheostat_ua.value) if (has_main_power and sa3_anode) else 0.0
        I_c = (float(self.rheostat_ic.value) / 100.0) if (has_main_power and sa1_solenoid) else 0.0
        
        self.solenoid_visual.setActive(has_main_power and sa2_heater)
        
        if has_main_power and sa2_heater and sa3_anode:
            I_a_pure = physics.get_anode_current(float(self.rheostat_ua.value), I_c)
        else:
            I_a_pure = 0.0

        self.voltmeter_anode.set_value(U_a)
        self.multimeter_ic.set_value(I_c)
        self.ammeter_anode.set_value(I_a_pure)
        
        if not has_main_power:
            self.lbl_status.setText("Стенд обесточен. Подключите вилку к сети ~220В.")
        elif not sa2_heater:
            self.lbl_status.setText("Включите SA2 (Накал) для прогрева электронной лампы.")
        elif not sa3_anode:
            self.lbl_status.setText("Замкните ключ SA3 (Анод), чтобы подать напряжение.")
        elif not sa1_solenoid:
            self.lbl_status.setText("Замкните SA1 (Соленоид) для подачи тока в катушку.")
        else:
            self.lbl_status.setText("Стенд готов. Изменяйте параметры реостатами.")

    def process_lab_data(self):
        x_data = []
        y_data = []
        try:
            for row in range(self.table.rowCount()):
                item_ic = self.table.item(row, 1)
                item_ia = self.table.item(row, 2)
                if item_ic and item_ia and item_ic.text() and item_ia.text():
                    x_data.append(float(item_ic.text().replace(',', '.')))
                    y_data.append(float(item_ia.text().replace(',', '.')))
            
            if len(x_data) < 4:
                QMessageBox.warning(self, "Ошибка", "Заполните данные измерений!")
                return
                
            self.ax.clear()
            self.ax.plot(x_data, y_data, 'bo-', linewidth=2, markersize=5, label="Эксперимент")
            self.ax.set_title("Сбросовая характеристика I_a = f(I_c)", fontsize=10)
            self.ax.set_xlabel("I_c, А", fontsize=9)
            self.ax.set_ylabel("I_a, мкА", fontsize=9)
            self.ax.tick_params(axis='both', labelsize=8)
            self.ax.grid(True)
            self.ax.legend(fontsize=8)
            
            self.fig.tight_layout() 
            self.canvas.draw()
            
            U_a = float(self.table.item(0, 0).text())
            I_c_crit, e_m_exp, rel_error, rating = physics.calculate_results(x_data, y_data, U_a)
            
            self.result_view.setHtml(
                f"Критический ток: {I_c_crit:.3f} А<br>"
                f"Полученное e/m: {e_m_exp:.3e} Кл/кг<br>"
                f"Погрешность: {rel_error:.2f}%<br>"
                f"Оценка защиты работы: <b>{rating}</b>"
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Заполните ячейки числами! {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirtualLabStand()
    window.show()
    sys.exit(app.exec())
