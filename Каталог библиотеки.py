import sys

import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QApplication, QComboBox, QPushButton, QLineEdit, QListWidget, QListWidgetItem
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap


class LibraryCatalog(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(50, 50, 500, 500)

        self.combobox = QComboBox(self)
        self.combobox.resize(200, 30)
        self.combobox.move(10, 10)
        self.combobox.addItems(["Автор", "Название"])
        self.combobox.currentIndexChanged.connect(self.change_val)

        self.btn = QPushButton("Искать", self)
        self.btn.resize(100, 100)
        self.btn.move(350, 10)
        self.btn.clicked.connect(self.search)

        self.lineedit = QLineEdit(self)
        self.lineedit.resize(250, 30)
        self.lineedit.move(10, 80)

        self.listwidget = QListWidget(self)
        self.listwidget.resize(480, 300)
        self.listwidget.move(10, 200)

        self.con = sqlite3.connect("library_catalog.sqlite")
        self.cur = self.con.cursor()

        self.status = 0
        self.cur_status = 0

        self.new_window = None

    def search(self):
        s = self.lineedit.text()
        self.cur_status = self.status
        res = []
        if s and self.combobox.currentText() == "Название":
            res = self.cur.execute(f"""select authors.name as author, books.title, books.image, genres.title, books.year
                        from books left join authors on books.author = authors.id
                        left join genres on books.genre = genres.id 
                        where books.title like "{s}%"
                        """).fetchall()
            self.listwidget.clear()
        elif s and self.combobox.currentText() == "Автор":
            res = self.cur.execute(f"""select authors.name as author, books.title, books.image, genres.title, books.year
                        from books left join authors on books.author = authors.id
                        left join genres on books.genre = genres.id
                        where authors.name like "{s}%"
                        """).fetchall()
            self.listwidget.clear()

        for el in res:
            item = QListWidgetItem()

            widget = QPushButton(el[1])
            widget.clicked.connect(self.open_info_book)

            item.setSizeHint(widget.sizeHint())
            self.listwidget.addItem(item)
            self.listwidget.setItemWidget(item, widget)

    def open_info_book(self):
        s = self.sender().text()
        res = self.cur.execute(f"""select authors.name as author, books.title, books.image, genres.title, books.year
                        from books left join authors on books.author = authors.id
                        left join genres on books.genre = genres.id
                    where books.title = "{s}"
                    """).fetchall()
        self.new_window = InfoWindow(res)
        self.new_window.show()

    def change_val(self):
        self.status = (self.status + 1) % 2

    def closeEvent(self, event):
        self.con.close()


class InfoWindow(QMainWindow):
    def __init__(self, res: tuple):
        super().__init__()
        self.setGeometry(100, 100, 600, 500)

        self.author = QLabel(self)
        self.author.resize(300, 30)
        self.author.move(10, 10)
        self.author.setText(f"Автор: {res[0][0]}")

        self.title = QLabel(self)
        self.title.resize(300, 30)
        self.title.move(10, 50)
        self.title.setText(f"Название: {res[0][1]}")

        self.year = QLabel(self)
        self.year.resize(300, 30)
        self.year.move(10, 90)
        self.year.setText(f"Год издания: {res[0][4]}")

        self.genre = QLabel(self)
        self.genre.resize(300, 30)
        self.genre.move(10, 130)
        self.genre.setText(f"Жанр: {res[0][3]}")

        self.image = QLabel(self)
        self.image.resize(300, 300)
        self.image.move(270, 10)

        image_for_pixmap = res[0][2] if res[0][2] is not None else r"data\book_standart.jpg"
        pixmap = QPixmap(image_for_pixmap).scaled(300, 300, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.image.setPixmap(pixmap)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LibraryCatalog()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
