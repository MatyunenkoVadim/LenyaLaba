import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

def show_graphs():
    # Определение универсов для каждой переменной
    attendance_universe = np.arange(0, 101, 1)
    kr_universe = np.arange(0, 6, 0.5)
    class_work_universe = np.arange(0, 16, 1)

    # Определение функций принадлежности для посещаемости
    attendance_normal = fuzz.trapmf(attendance_universe, [0, 100, 100, 100])
    attendance_high = fuzz.trimf(attendance_universe, [50, 100, 100])

    # Определение функций принадлежности для контрольных работ
    # kr_low = fuzz.trapmf(kr_universe, [0, 0, 2, 3])
    kr_medium = fuzz.trapmf(kr_universe, [2, 3, 5, 5])
    kr_high = fuzz.trapmf(kr_universe, [2.5, 4, 5, 5])

    # Определение функций принадлежности для работы в классе
    # class_work_poor = fuzz.trapmf(class_work_universe, [0, 0, 1, 2])
    class_work_good = fuzz.trapmf(class_work_universe, [0, 2, 15, 15])

    # Создание графиков
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, figsize=(8, 12))

    # График для посещаемости
    ax1.plot(attendance_universe, attendance_normal, 'b', linewidth=1.5, label='Нормальная')
    ax1.plot(attendance_universe, attendance_high, 'r', linewidth=1.5, label='Высокая')
    ax1.set_title('Посещаемость')
    ax1.legend()

    # График для контрольных работ
    # ax2.plot(kr_universe, kr_low, 'b', linewidth=1.5, label='Плохо')
    ax2.plot(kr_universe, kr_medium, 'g', linewidth=1.5, label='Нормально')
    ax2.plot(kr_universe, kr_high, 'r', linewidth=1.5, label='Отлично')
    ax2.set_title('Контрольные работы')
    ax2.legend()

    # График для работы на занятиях
    # ax3.plot(class_work_universe, class_work_poor, 'b', linewidth=1.5, label='Слабая')
    ax3.plot(class_work_universe, class_work_good, 'r', linewidth=1.5, label='Хорошая')
    ax3.set_title('Работа на занятиях')
    ax3.legend()

    # Настройка отображения
    for ax in (ax1, ax2, ax3):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

    plt.tight_layout()
    plt.show()