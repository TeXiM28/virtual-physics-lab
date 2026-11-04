import math
import csv

TRUE_E_M = 1.76e11

def get_anode_current(U_a, I_c):
    """Физическое ядро: расчет тока анода с расширенным диапазоном до 80В"""
    TRUE_E_M = 1.76e11
    R_anode, N_turns, L_sol = 0.005, 1200, 0.12
    mu_0 = 4 * math.pi * 1e-7
    
    B = mu_0 * (N_turns / L_sol) * I_c
    
    if U_a > 0:
        B_crit = math.sqrt((8 * U_a) / (TRUE_E_M * (R_anode ** 2)))
    else:
        B_crit = 0.001
        
    # Коэффициент изменен с 45.0 на 20.0, чтобы при U_a = 80В ток не превышал 55 мкА
    I_a_max = 20.0 * (U_a / 30.0)
    delta_B = B - B_crit
    softness = 0.00025
    
    if U_a == 0:
        return 0.0
        
    return I_a_max / (1.0 + math.exp(delta_B / softness))

def calculate_results(x_data, y_data, U_a):
    """Обработка данных студента и расчет e/m"""
    max_drop, idx_crit = 0, 0
    for i in range(len(y_data) - 1):
        drop = y_data[i] - y_data[i+1]
        if drop > max_drop:
            max_drop, idx_crit = drop, i
            
    I_c_crit = (x_data[idx_crit] + x_data[idx_crit+1]) / 2
    
    N_turns, L_sol, mu_0, R_anode = 1200, 0.12, 4 * math.pi * 1e-7, 0.005
    B_crit_exp = mu_0 * (N_turns / L_sol) * I_c_crit
    e_m_exp = (8 * U_a) / ((B_crit_exp ** 2) * (R_anode ** 2))
    
    rel_error = abs(e_m_exp - TRUE_E_M) / TRUE_E_M * 100
    rating = "Отлично" if rel_error < 5.0 else "Хорошо" if rel_error < 12.0 else "Удовлетворительно"
    
    return I_c_crit, e_m_exp, rel_error, rating

def save_csv(path, rows_data):
    """Экспорт данных в CSV файл"""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["U_a (B)", "I_c (A)", "I_a (mkA)"])
        for row in rows_data:
            writer.writerow(row)
