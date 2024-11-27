import csv
import numpy as np
import skfuzzy as fuzz
import skfuzzy.control

from converter import csv_from_excel
from converter import excel_from_csv
from graphs import show_graphs
from skfuzzy import control as ctrl


class Student:
    def __init__(self, number, last_name, first_name, iz_number, iz_submitted, grade_1, grade_2, grade_3, grade_4, absences,
                 class_work):
        self.number = number
        self.last_name = last_name
        self.first_name = first_name
        self.iz_number = iz_number
        self.iz_submitted = iz_submitted
        self.grade_1 = grade_1
        self.grade_2 = grade_2
        self.grade_3 = grade_3
        self.grade_4 = grade_4
        self.absences = absences
        self.class_work = class_work
        self.attendance = ((15-absences)/15) * 100

    def __repr__(self):
        return (f"Student({self.number}, {self.last_name}, {self.first_name}, "
                f"{self.iz_number}, {self.iz_submitted}, {self.grade_1}, "
                f"{self.grade_2}, {self.grade_3}, {self.absences}, {self.class_work})")


def parse_int(value):
    if value.lower() == "неявка":
        return 0
    try:
        return int(value)
    except ValueError:
        res = ''
        for i in value:
            if i.isdigit():
                res += i
            else:
                break
        return int(res)


def read_students_from_csv(file_path):
    students = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        # Пропускаем первые три строки
        for _ in range(3):
            next(reader)

        for row in reader:
            if not row or all(not cell.strip() for cell in row):
                break  # Прерываем цикл, если строка пустая
            student = Student(
                number=parse_int(row[0]),
                last_name=row[1],
                first_name=row[2],
                iz_number=row[3],
                iz_submitted=row[4].lower() == '+',
                grade_1=parse_int(row[5]),
                grade_2=parse_int(row[6]),
                grade_3=parse_int(row[7]),
                grade_4=parse_int(row[8]),
                absences=parse_int(row[9]),
                class_work=parse_int(row[10])
            )
            students.append(student)
    return students

# Определение лингвистических переменных
attendance = ctrl.Antecedent(np.arange(0, 101, 0.1), 'attendance')
kr1 = ctrl.Antecedent(np.arange(0, 6, 1), 'kr1')
kr2 = ctrl.Antecedent(np.arange(0, 6, 1), 'kr2')
kr3 = ctrl.Antecedent(np.arange(0, 6, 1), 'kr3')
kr4 = ctrl.Antecedent(np.arange(0, 6, 1), 'kr4')
class_work = ctrl.Antecedent(np.arange(0, 16, 1), 'class_work')
auto_grade = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'auto_grade')

# Определение функций принадлежности для посещаемости
attendance['normal'] = fuzz.trapmf(attendance.universe, [25, 75, 100, 100])
attendance['high'] = fuzz.trimf(attendance.universe, [75, 100, 100])

# Определение функций принадлежности для контрольных работ
kr1['low'] = fuzz.trapmf(kr1.universe, [0, 0, 2, 3])
kr1['medium'] = fuzz.trapmf(kr1.universe, [2, 3, 5, 5])
kr1['high'] = fuzz.trapmf(kr1.universe, [3, 4, 5, 5])

kr2['low'] = fuzz.trapmf(kr2.universe, [0, 0, 2, 3])
kr2['medium'] = fuzz.trapmf(kr2.universe, [2, 3, 5, 5])
kr2['high'] = fuzz.trapmf(kr2.universe, [3, 4, 5, 5])

kr3['low'] = fuzz.trapmf(kr3.universe, [0, 0, 2, 3])
kr3['medium'] = fuzz.trapmf(kr3.universe, [2, 3, 5, 5])
kr3['high'] = fuzz.trapmf(kr3.universe, [3, 4, 5, 5])

kr4['low'] = fuzz.trapmf(kr4.universe, [0, 0, 2, 3])
kr4['medium'] = fuzz.trapmf(kr4.universe, [2, 3, 5, 5])
kr4['high'] = fuzz.trapmf(kr4.universe, [3, 4, 5, 5])

# Определение функций принадлежности для работы на парах
class_work['poor'] = fuzz.trapmf(class_work.universe, [0, 0, 1, 2])
class_work['good'] = fuzz.trapmf(class_work.universe, [1, 2, 15, 15])

# Определение функций принадлежности
auto_grade['no'] = fuzz.trimf(auto_grade.universe, [0, 0, 0.5])   # Узкий треугольник около 0
auto_grade['yes'] = fuzz.trimf(auto_grade.universe, [0.5, 1, 1])  # Узкий треугольник около 1

auto_grade.defuzzify_method = 'centroid'

# Определение правил
rule1 = ctrl.Rule(
    (attendance['normal'] | attendance['high'])
    & (kr1['medium'] | kr1['high'])
    & (kr2['medium'] | kr2['high'])
    & (kr3['medium'] | kr3['high'])
    & (kr4['medium'] | kr4['high'])
    , auto_grade['yes']
)

# Для второго правила создаем несколько подправил, чтобы учесть все комбинации
rule2 = ctrl.Rule(
    attendance['high'] & class_work['good'] &
    ((kr1['high'] & kr2['high'] & kr3['high']) |
     (kr1['high'] & kr2['high'] & kr4['high']) |
     (kr1['high'] & kr3['high'] & kr4['high']) |
     (kr2['high'] & kr3['high'] & kr4['high'])),
    auto_grade['yes']
)

# Добавляем правило по умолчанию для всех остальных случаев
rule3 = ctrl.Rule(
    ~(
        rule1.antecedent |
        rule2.antecedent
    ),
    auto_grade['no']
)

# Создание системы управления
auto_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
auto_simulation = ctrl.ControlSystemSimulation(auto_ctrl)

def check_and_write_results(students, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Фамилия', 'Имя', 'Auto_Grade', 'Результат'])

        for student in students:
            auto_simulation.input['attendance'] = student.attendance
            auto_simulation.input['kr1'] = student.grade_1
            auto_simulation.input['kr2'] = student.grade_2
            auto_simulation.input['kr3'] = student.grade_3
            auto_simulation.input['kr4'] = student.grade_4
            auto_simulation.input['class_work'] = student.class_work
            # Вывод значений функций принадлежности
            try:
                auto_simulation.compute()
                result = auto_simulation.output['auto_grade']
                print(f"Auto Grade: {result}")
                result_text = 'Зачет' if result > 0.5 else 'Незачет'
                writer.writerow([student.last_name, student.first_name, result, result_text])
            except Exception as e:
                writer.writerow([student.last_name, student.first_name, 'Ошибка', str(e)])

# Пример использования
csv_from_excel('резы.xls') # Название входного файла
file_path1 = 'Temp/Результаты ИТ-41.csv'
file_path2 = 'Temp/Результаты ИТ-42.csv'
students1 = read_students_from_csv(file_path1)
students2 = read_students_from_csv(file_path2)
output_file = 'Temp/Зачет ИТ-41.csv'
check_and_write_results(students1, output_file)
output_file = 'Temp/Зачет ИТ-42.csv'
check_and_write_results(students2, output_file)
excel_from_csv("Зачет.xlsx") # Название выходного файла

# show_graphs()