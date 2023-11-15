import sqlite3
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QDialog
from PyQt5 import uic


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.update_table()
        self.add_btn.clicked.connect(self.add_film)
        self.edit_btn.clicked.connect(self.edit_film)
        self.dialog = None

    def update_table(self):
        cur = self.con.cursor()
        results = cur.execute("select * from types").fetchall()
        if not results:
            return
        self.tableWidget.setColumnCount(len(results[0]))
        self.tableWidget.setHorizontalHeaderLabels(
            ["ID", "Название сорта", "Степень обжарки", "Консистенция", "Вкус", "Цена упаковки", "Объем упаковки"])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(results):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def add_film(self):
        self.dialog = AddEditCoffeeForm(self)
        self.dialog.show()

    def edit_film(self):
        rows = list(map(lambda x: x.row(), self.tableWidget.selectedItems()))
        if len(rows) == 0:
            self.error_lbl.setText("Выберите сорт кофе для редактирования")
        elif len(rows) >= 2:
            self.error_lbl.setText("Слишком много сортов кофе для редактирования")
        else:
            self.error_lbl.setText("")
            row = rows[0]
            params = [self.tableWidget.item(row, i).text() for i in range(7)]
            self.dialog = AddEditCoffeeForm(self, *params)
            self.dialog.show()


class AddEditCoffeeForm(QDialog):
    def __init__(self, main_window, *params):
        super().__init__()
        uic.loadUi('Edit.ui', self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.main_window = main_window
        self.action = "edit" if params else "add"
        if params:
            id, name, roast, substance, taste, price, volume = params
            self.id = id
            self.name_edit.insert(name)
            self.roast_edit.insert(roast)
            self.substance_edit.insert(substance)
            self.taste_edit.insert(taste)
            self.price_edit.insert(price)
            self.volume_edit.insert(volume)
        self.save_btn.clicked.connect(self.save_changes)
        self.setModal(True)

    def save_changes(self):
        name = self.name_edit.text()
        roast = self.roast_edit.text()
        substance = self.substance_edit.text()
        taste = self.taste_edit.text()
        price = self.price_edit.text()
        volume = self.volume_edit.text()
        cur = self.con.cursor()
        try:
            if self.action == "edit":
                cur.execute(
                    f"update types set name = '{name}', roast = '{roast}', substance = '{substance}', "
                    f"taste = '{taste}', price = {price}, volume = {volume} where id = {self.id}")
            elif self.action == "add":
                cur.execute(
                    f"insert into types (name, roast, substance, taste, price, volume) "
                    f"values ('{name}', '{roast}', '{substance}', '{taste}', {price}, {volume})")
            self.con.commit()
            self.main_window.update_table()
            self.close()
        except sqlite3.OperationalError:
            self.error_lbl.setText("Ошибка ввода данных")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
