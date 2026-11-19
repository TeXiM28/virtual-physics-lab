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
        self.setWindowTitle("ВЛК Физика НТИ УрФУ — Лабораторная работа №19")
        self.setGeometry(30, 30, 1320, 850)
        self.is_running = False
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)
        
        
        self.stand_widget = QWidget()
        self.stand_widget.setStyleSheet("background-color: #2D1A14; border: 4px solid #1A0C00;") 
        stand_layout = QVBoxLayout(self.stand_widget)

        self.is_dark = True
        self.btn_theme = QPushButton("☀️ Светлая тема")
        self.btn_theme.setStyleSheet("background-color: #FFC107; color: black; font-weight: bold; padding: 5px;")
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addWidget(self.btn_theme)
        top_bar_layout.addStretch()
        stand_layout.addLayout(top_bar_layout)
        
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
        
        self.lbl_status = QLabel("Стенд обесточен. Включите вилку в сеть ~220В.")
        self.lbl_status.setStyleSheet("color: #FFCC80; font-style: italic; padding: 4px; font-weight: bold;")
        stand_layout.addWidget(self.lbl_status)
        
        wiring_row_layout = QHBoxLayout()
        self.rheostat_ic = VirtualRheostat("Реостат катушки R1 (I_c)", min_val=0, max_val=250, start_val=0)
        self.rheostat_ic.valueChanged.connect(self.sync_simulation)
        wiring_row_layout.addWidget(self.rheostat_ic)
        
        self.solenoid_visual = VirtualSolenoid()
        wiring_row_layout.addWidget(self.solenoid_visual)
        
        self.ammeter_anode = ArrowInstrument("Анодный ток (I_a)", "мкА", max_val=1000.0)
        wiring_row_layout.addWidget(self.ammeter_anode)
        
        self.rheostat_ua = VirtualRheostat("Реостат анода R3 (U_a)", min_val=0, max_val=80, start_val=80)
        self.rheostat_ua.valueChanged.connect(self.sync_simulation)
        wiring_row_layout.addWidget(self.rheostat_ua)
        stand_layout.addLayout(wiring_row_layout)
        
        bottom_row_layout = QHBoxLayout()
        self.multimeter_ic = DigitalMultimeter("Амперметр соленоида A (I_c)", "А")
        self.voltmeter_anode = DigitalMultimeter("Цифровой вольтметр V (U_a)", "В")
        bottom_row_layout.addWidget(self.multimeter_ic)
        bottom_row_layout.addWidget(self.voltmeter_anode)
        stand_layout.addLayout(bottom_row_layout)
        
        self.manual_view = QTextEdit()
        self.manual_view.setReadOnly(True)
        self.manual_view.setStyleSheet("background-color: #21130F; color: #E0E0E0; border: 2px solid #5D4037;")
        self.manual_view.setHtml(
            "<h3>МЕТОДИЧЕСКИЕ УКАЗАНИЯ К ЛАБОРАТОРНОЙ РАБОТЕ № 19</h3>"
            "<b>Организация:</b> НТИ (филиал) ФГАОУ ВО УрФУ (Нижний Тагил, 2019 г.)<br>"
            "<b>Автор-составитель:</b> К. И. Корнисик<br><br>"
            "<b>ЦЕЛЬ РАБОТЫ:</b> Определение удельного заряда электрона (q/m) с помощью магнетрона.<br><br>"
            "<b>ПОРЯДОК ВЫПОЛНЕНИЯ РАБОТЫ (стр. 11):</b><br>"
            "1. Включите штепсельную вилку в сеть ~220В.<br>"
            "2. Ключом SA2 включите цепь накала лампы и дайте ей прогреться 3 мин.<br>"
            "3. Ключом SA3 включите анодную цепь и потенциометром R3 установите анодное напряжение 80 В.<br>"
            "4. Включите цепь соленоида с помощью ключа SA1.<br>"
            "5. Постепенно увеличивайте силу тока в соленоиде с помощью реостата R1.<br>"
            "6. Снимайте показания анодного тока I_A со стрелочного прибора и вносите их вручную в журнал эксперимента справа.<br>"
            "7. Нажмите кнопку обработки данных для расчета e/m по максимуму производной спада тока."
        )
        stand_layout.addWidget(self.manual_view)
        main_splitter.addWidget(self.stand_widget)
        
        notebook_widget = QWidget()
        notebook_layout = QVBoxLayout(notebook_widget)
        
        notebook_layout.addWidget(QLabel("<b>Журнал измерений эксперимента:</b>"))
        self.table = QTableWidget(11, 3)
        self.table.setHorizontalHeaderLabels(["U_a, В", "I_c, А", "I_a, мкА (Ввод)"])
        for i in range(11):
            item_ua = QTableWidgetItem("80.0")
            item_ua.setFlags(item_ua.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item_ua)
            self.table.setItem(i, 1, QTableWidgetItem(""))
            self.table.setItem(i, 2, QTableWidgetItem(""))
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
        
      
        main_splitter.setSizes([750, 500])

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        
        if self.is_dark:
            self.btn_theme.setText("☀️ Светлая тема")
            self.stand_widget.setStyleSheet("background-color: #2D1A14; border: 4px solid #1A0C00;")
            self.lbl_status.setStyleSheet("color: #FFCC80; font-style: italic; padding: 4px; font-weight: bold;")
            self.manual_view.setStyleSheet("background-color: #21130F; color: #E0E0E0; border: 2px solid #5D4037;")
            self.setStyleSheet("")
            self.table.setStyleSheet("")
            self.result_view.setStyleSheet("")
        else:
            self.btn_theme.setText("🌙 Тёмная тема")
            self.stand_widget.setStyleSheet("background-color: #F0F0F0; border: 4px solid #B0B0B0;")
            self.lbl_status.setStyleSheet("color: #333333; font-style: italic; padding: 4px; font-weight: bold;")
            self.manual_view.setStyleSheet("background-color: #FFFFFF; color: #000000; border: 1px solid #CCCCCC;")

            self.setStyleSheet("""
                QWidget { background-color: #FFFFFF; color: #000000; }
                QTableWidget { background-color: #FFFFFF; color: #000000; gridline-color: #CCCCCC; }
                QHeaderView::section { background-color: #F0F0F0; color: #000000; }
                QTextEdit { background-color: #FFFFFF; color: #000000; }
            """)
            
        self.ammeter_anode.set_theme(self.is_dark)
        self.rheostat_ic.set_theme(self.is_dark)
        self.rheostat_ua.set_theme(self.is_dark)
        self.multimeter_ic.set_theme(self.is_dark)
        self.voltmeter_anode.set_theme(self.is_dark)

    def sync_simulation(self):
        style_on = "background-color: #2ECC71; color: white; font-weight: bold; padding: 8px; border: 1px solid #000;"
        style_off = "background-color: #757575; color: white; font-weight: bold; padding: 8px; border: 1px solid #000;"
        
        self.btn_fork.setText("Вилка: ВКЛ (~220В)" if self.btn_fork.isChecked() else "Вилка: ВЫКЛ (~220В)")
        self.btn_sa2.setText("SA2 (Накал): ВКЛ" if self.btn_sa2.isChecked() else "SA2 (Накал): ВЫКЛ")
        self.btn_sa3.setText("SA3 (Анод): ВКЛ" if self.btn_sa3.isChecked() else "SA3 (Анод): ВЫКЛ")
        self.btn_sa1.setText("SA1 (Соленоид): ВКЛ" if self.btn_sa1.isChecked() else "SA1 (Соленоид): ВЫКЛ")
        
        for btn in self.keys_list:
            btn.setStyleSheet(style_on if btn.isChecked() else style_off)

        has_pwr = self.btn_fork.isChecked()
        sa2 = self.btn_sa2.isChecked()
        sa3 = self.btn_sa3.isChecked()
        sa1 = self.btn_sa1.isChecked()
        
        U_a = float(self.rheostat_ua.value) if (has_pwr and sa3) else 0.0
        I_c = (float(self.rheostat_ic.value) / 100.0) if (has_pwr and sa1) else 0.0
        
        self.solenoid_visual.setActive(has_pwr and sa2)
        
        if has_pwr and sa2 and sa3:
            I_a_pure = physics.get_anode_current(float(self.rheostat_ua.value), I_c)
        else:
            I_a_pure = 0.0

        self.voltmeter_anode.set_value(U_a)
        self.multimeter_ic.set_value(I_c)
        self.ammeter_anode.set_value(I_a_pure)
        
        if not has_pwr:
            self.lbl_status.setText("Стенд обесточен. Подключите вилку к сети ~220В.")
        elif not sa2:
            self.lbl_status.setText("Включите ключ SA2 (Накал) для прогрева катода лампы.")
        elif not sa3:
            self.lbl_status.setText("Замкните ключ SA3 (Анод), чтобы подать напряжение на анод.")
        elif not sa1:
            self.lbl_status.setText("Замкните ключ SA1 (Соленоид), чтобы пустить ток в катушку C.")
        else:
            self.lbl_status.setText("Стенд полностью готов. Снимайте ВАХ магнетрона.")

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
                QMessageBox.warning(self, "Ошибка", "Заполните минимум 4 строки измерений!")
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
