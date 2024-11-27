import xlrd
import csv
from openpyxl import Workbook

def csv_from_excel(file_name):
    wb = xlrd.open_workbook(file_name)
    sh1 = wb.sheet_by_name('ИТ-41')
    sh2 = wb.sheet_by_name('ИТ-42')

    # Открываем файлы с указанием кодировки UTF-8
    with open('Temp/Результаты ИТ-41.csv', 'w', newline='', encoding='utf-8-sig') as your_csv_file1:
        wr1 = csv.writer(your_csv_file1, quoting=csv.QUOTE_ALL, delimiter=';')
        for rownum in range(sh1.nrows):
            wr1.writerow(sh1.row_values(rownum))

    with open('Temp/Результаты ИТ-42.csv', 'w', newline='', encoding='utf-8-sig') as your_csv_file2:
        wr2 = csv.writer(your_csv_file2, quoting=csv.QUOTE_ALL, delimiter=';')
        for rownum in range(sh2.nrows):
            wr2.writerow(sh2.row_values(rownum))


def excel_from_csv(file_name):
    # Создаем новый Excel файл
    wb = Workbook()

    # Читаем первый CSV файл и добавляем его содержимое на первый лист
    with open('Temp/Зачет ИТ-41.csv', 'r', encoding='utf-8') as csv_file1:
        reader1 = csv.reader(csv_file1, delimiter=';')
        ws1 = wb.active
        ws1.title = 'ИТ-41'
        for row in reader1:
            ws1.append(row)

    # Читаем второй CSV файл и добавляем его содержимое на второй лист
    with open('Temp/Зачет ИТ-42.csv', 'r', encoding='utf-8') as csv_file2:
        reader2 = csv.reader(csv_file2, delimiter=';')
        ws2 = wb.create_sheet(title='ИТ-42')
        for row in reader2:
            ws2.append(row)

    # Сохраняем Excel файл
    wb.save(file_name)