import SQLiteData
from GUI.UiInterface import UiInterface
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from asyncqt import asyncSlot


def singleton(ui_class):
    instances = {}

    def getinstance(*args, **kwargs):
        if ui_class not in instances:
            instances[ui_class] = ui_class(*args, **kwargs)
        return instances[ui_class]

    return getinstance


@singleton
class SystemCRM(QMainWindow):
    def __init__(self):
        super().__init__()
        self.query_data = None
        self.tbl_name = None
        self.vaccine = None
        self.get_tbl = None
        self.type_btn = None
        self.suppliers_dict = {}
        self.ui = UiInterface(self)
        self.db = SQLiteData.ex
        self.new_row_warning = True
        self.delete_all_warning = False
        self.async_init()
        self.dict_animals = {"Корова": [1, "cows"], "Свинья": [2, "pigs"],
                             "Овца": [3, "sheeps"], "Весь скот": [4, "all_animals"]}
        self.dict_genders = {"Женский": 1, "Мужской": 2}
        self.show()

    @asyncSlot()
    async def async_init(self):
        all_animals = await self.db.get_animals()
        self.ui.main_win.combo_tbls.addItems(all_animals)
        self.ui.main_win.combo_tbls.currentIndexChanged.connect(self.combo_tbl)
        await self.combo_tbl()
        self.ui.main_win.combo_tbls2.currentIndexChanged.connect(self.combo_tbl)
        await self.clicked_btn()

    @asyncSlot()
    async def combo_tbl(self):
        self.get_tbl = self.ui.main_win.combo_tbls.currentText()
        self.vaccine = self.ui.main_win.combo_tbls2.currentText()
        self.tbl_name = self.dict_animals[self.get_tbl][1]
        self.query_data = []

        if self.vaccine == "Неважно" and self.get_tbl == "Весь скот":
            self.query_data = [0, 1]
        elif self.vaccine == "Есть":
            self.query_data = [1, '']
        elif self.vaccine == "Нет":
            self.query_data = [0, '']
        else:
            self.query_data = [0, 1]
        await self.load_date(self.ui.main_win.main_tbl)

    async def clicked_btn(self):
        win = self.ui.main_win
        win.btn_load_orders.clicked.connect(lambda: self.load_date(self.ui.main_win.main_tbl))
        win.btn_add_orders.clicked.connect(lambda: self.add_new_row(self.ui.main_win.main_tbl))
        win.btn_del_orders.clicked.connect(lambda: self.delete_row(self.ui.main_win.main_tbl))
        win.btn_save_orders.clicked.connect(lambda: self.save_data(self.ui.main_win.main_tbl))
        win.btn_xls_orders.clicked.connect(lambda: self.load_excel(self.ui.main_win.main_tbl))

    @asyncSlot()
    async def load_date(self, tbl):
        tbl.setRowCount(0)
        data = await self.db.tbl_data(self.get_tbl, self.query_data)

        for row_number, row_data in enumerate(data):
            tbl.insertRow(row_number)
            for col_number, col_data in enumerate(row_data):
                tbl.setItem(row_number, col_number, QtWidgets.QTableWidgetItem(str(col_data)))

        self.new_row_warning = True
        self.ui.main_win.lbl_info_tbl.setText('Таблица загружена')
        self.delete_all_warning = False

    @asyncSlot()
    async def save_data(self, tbl):
        self.ui.main_win.lbl_info_tbl.setText('')
        try:
            data = []
            for row in range(tbl.rowCount()):
                data.append([])
                if not tbl.item(row, 0).text().isdigit():
                    raise Exception
                for col in range(tbl.columnCount()):
                    if col == 2:
                        type_animal = self.dict_animals[tbl.item(row, col).text()][0]
                        data[row].append(type_animal)
                    elif col == 3:
                        gender = self.dict_genders[tbl.item(row, col).text()]
                        data[row].append(gender)
                    else:
                        data[row].append(tbl.item(row, col).text())

            self.new_row_warning = True
            await self.db.data_save(data, self.tbl_name)
            self.ui.main_win.lbl_info_tbl.setText('Таблица сохранена')
        except AttributeError:
            self.ui.main_win.lbl_info_tbl.setText('Введите все поял корректно')

    def add_new_row(self, tbl):
        if self.get_tbl != "Весь скот" and self.vaccine == "Неважно":
            if self.new_row_warning:
                row_position = tbl.rowCount()
                new_id = str(int(tbl.item(row_position - 1, 0).text()) + 1)
                tbl.insertRow(row_position)
                tbl.setItem(row_position, 0, QtWidgets.QTableWidgetItem(new_id))
                self.new_row_warning = False
            else:
                self.ui.main_win.lbl_info_tbl.setText('Сохраните таблицу')
        else:
            self.ui.main_win.lbl_info_tbl.setText('Выберите таблицу скота без фильтров')

    def delete_row(self, tbl):
        if self.get_tbl != "Весь скот" and self.vaccine == "Неважно":
            if tbl.rowCount() > 0 and tbl.currentRow() != -1:
                current_row = tbl.currentRow()
                tbl.removeRow(current_row)
        else:
            self.ui.main_win.lbl_info_tbl.setText('Выберите таблицу скота без фильтров')

    def load_excel(self, tbl):
        k = 0
        data = [[tbl.item(row, column).text() for row in range(tbl.rowCount())] for column in range(tbl.columnCount())]

        dict_xls = {"ID": [], "Номер": [], "Животное": "", "Пол": [],
                    "Вес": [], "Дата рождения": [], "Вакцинация": []}

        for key in dict_xls:
            dict_xls[key] = data[k]
            k += 1

        data_frame = pd.DataFrame(dict_xls)
        if self.vaccine == "Есть":
            data_frame.to_excel(f"./ExcelData/{self.tbl_name}_вакцина.xlsx", index=False)
            self.ui.main_win.lbl_info_tbl.setText(f'Данные загружены в {self.tbl_name}_вакцина.xlsx')
        elif self.vaccine == "Нет":
            data_frame.to_excel(f"./ExcelData/{self.tbl_name}_без_вакцины.xlsx", index=False)
            self.ui.main_win.lbl_info_tbl.setText(f'Данные загружены в {self.tbl_name}_без_вакцины.xlsx')
        else:
            data_frame.to_excel(f"./ExcelData/{self.tbl_name}.xlsx", index=False)
            self.ui.main_win.lbl_info_tbl.setText(f'Данные загружены в {self.tbl_name}.xlsx')
