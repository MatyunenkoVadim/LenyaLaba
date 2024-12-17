import csv
import numpy as np
import skfuzzy as fuzz

from converter import csv_from_excel
from converter import excel_from_csv
from graphs import show_graphs
from skfuzzy import control as ctrl


class Student:
    def __init__(self, number, last_name, first_name, iz_number, iz_submitted, grade_1, grade_2, grade_3, grade_4,
                 absences, class_work):
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
        self.attendance = ((16 - absences) / 16) * 100

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
attendance = ctrl.Antecedent(np.arange(0, 101, 0.01), 'attendance')
kr = ctrl.Antecedent(np.arange(0, 6, 0.5), 'kr1')
class_work = ctrl.Antecedent(np.arange(0, 17, 1), 'class_work')

# Определение функций принадлежности для посещаемости
attendance['normal'] = fuzz.trapmf(attendance.universe, [0, 100, 100, 100])
attendance['high'] = fuzz.trimf(attendance.universe, [50, 100, 100])

# Определение функций принадлежности для контрольных работ
kr['medium'] = fuzz.trapmf(kr.universe, [2, 3, 5, 5])
kr['high'] = fuzz.trapmf(kr.universe, [2.5, 4, 5, 5])

# Определение функций принадлежности для работы на парах
class_work['good'] = fuzz.trapmf(class_work.universe, [0, 2, 16, 16])


def rules_check(student):
    conditions_1 = np.array([
        fuzz.interp_membership(attendance.universe, attendance['normal'].mf, student.attendance),
        fuzz.interp_membership(kr.universe, kr['medium'].mf, student.grade_1),
        fuzz.interp_membership(kr.universe, kr['medium'].mf, student.grade_2),
        fuzz.interp_membership(kr.universe, kr['medium'].mf, student.grade_3),
        fuzz.interp_membership(kr.universe, kr['medium'].mf, student.grade_4)
    ])

    cond_2_temp = np.array([
        fuzz.interp_membership(kr.universe, kr['high'].mf, student.grade_1),
        fuzz.interp_membership(kr.universe, kr['high'].mf, student.grade_2),
        fuzz.interp_membership(kr.universe, kr['high'].mf, student.grade_3),
        fuzz.interp_membership(kr.universe, kr['high'].mf, student.grade_4)
    ])

    # Удаляем минимальное значение по индексу
    cond_2_temp = np.delete(cond_2_temp, np.argmin(cond_2_temp))

    conditions_2 = np.array([
        fuzz.interp_membership(attendance.universe, attendance['high'].mf, student.attendance),
        fuzz.interp_membership(class_work.universe, class_work['good'].mf, student.class_work)
    ])

    # Вычисляем минимум для каждого набора условий
    min_conditions_1 = np.min(conditions_1)
    min_conditions_2 = np.min(np.append(conditions_2, cond_2_temp))  # Объединяем условия

    # Находим максимум из минимумов
    res = np.max([min_conditions_1, min_conditions_2])

    return res


def check_and_write_results(students, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Фамилия', 'Имя', 'Уверенность', 'Результат'])

        for student in students:
            try:
                result = rules_check(student)
                print(f"Уверенность в оценке студента {student.last_name} {student.first_name}: {result}")
                result_text = 'Зачет' if result > 0.5 else 'Незачет'
                writer.writerow([student.last_name, student.first_name, result, result_text])
            except Exception as e:
                writer.writerow([student.last_name, student.first_name, 'Ошибка', str(e)])


# Пример использования

csv_from_excel('резы.xls')  # Название входного файла
file_path1 = 'Temp/Результаты ИТ-41.csv'
file_path2 = 'Temp/Результаты ИТ-42.csv'
students1 = read_students_from_csv(file_path1)
students2 = read_students_from_csv(file_path2)
output_file = 'Temp/Зачет ИТ-41.csv'
check_and_write_results(students1, output_file)
output_file = 'Temp/Зачет ИТ-42.csv'
check_and_write_results(students2, output_file)
excel_from_csv("Зачет.xlsx")  # Название выходного файла

show_graphs()
