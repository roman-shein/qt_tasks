import sys

import sqlite3

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QTabWidget, QWidget, QPushButton
from PyQt6.QtWidgets import QPlainTextEdit, QComboBox, QMessageBox


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(50, 50, 800, 600)
        self.arr = []
        self.set_table()  # Создаем таблицы

        self.add_film_widget = None
        self.edit_film_widget = None

        self.add_genre_widget = None
        self.edit_genre_widget = None

    def set_table(self):
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setMovable(True)

        self.filmsTab = QWidget(self)
        self.genresTab = QWidget(self)

        self.tabWidget.addTab(self.filmsTab, "Фильмы")
        self.tabWidget.addTab(self.genresTab, "Жанры")

        self.setCentralWidget(self.tabWidget)
        self.tabWidget.currentChanged.connect(self.tab_changed)

        self.filmsTable = QTableWidget(self)
        self.filmsTable.resize(600, 400)
        self.filmsTable.move(0, 100)

        self.genresTable = QTableWidget(self)
        self.genresTable.resize(600, 400)
        self.genresTable.move(0, 100)

        self.con = sqlite3.connect("films_db.sqlite")
        self.cur = self.con.cursor()
        self.set_btn()  # Создаем кнопки
        self.tab_changed(0)

    def set_btn(self):
        self.addFilmButton = QPushButton("Добавить фильм", self)
        self.addFilmButton.resize(100, 30)
        self.addFilmButton.move(10, 30)
        self.addFilmButton.clicked.connect(self.add_film)

        self.editFilmButton = QPushButton("Изменить фильм", self)
        self.editFilmButton.resize(100, 30)
        self.editFilmButton.move(120, 30)
        self.editFilmButton.clicked.connect(self.edit_film)

        self.deleteFilmButton = QPushButton("Удалить фильм", self)
        self.deleteFilmButton.resize(100, 30)
        self.deleteFilmButton.move(230, 30)
        self.deleteFilmButton.clicked.connect(self.delete_film)

        self.films_btn = [self.addFilmButton, self.editFilmButton, self.deleteFilmButton]

        self.addGenreButton = QPushButton("Добавить жанр", self)
        self.addGenreButton.resize(100, 30)
        self.addGenreButton.move(10, 30)
        self.addGenreButton.clicked.connect(self.add_genre)

        self.editGenreButton = QPushButton("Изменить жанр", self)
        self.editGenreButton.resize(100, 30)
        self.editGenreButton.move(120, 30)
        self.editGenreButton.clicked.connect(self.edit_genre)

        self.deleteGenreButton = QPushButton("Удалить жанр", self)
        self.deleteGenreButton.resize(100, 30)
        self.deleteGenreButton.move(230, 30)
        self.deleteGenreButton.clicked.connect(self.delete_genre)

        self.genres_btn = [self.addGenreButton, self.editGenreButton, self.deleteGenreButton]

    def update_films_table(self):
        res = self.cur.execute("""select films.id, films.title, ifnull(genres.title, films.genre) as genre,
         year, duration from films left join genres on films.genre = genres.id""").fetchall()
        title = [el[0] for el in self.cur.description]

        self.filmsTable.setColumnCount(len(title))
        self.filmsTable.setHorizontalHeaderLabels(title)
        self.filmsTable.setRowCount(0)

        for i, row in enumerate(res[::-1]):
            self.filmsTable.setRowCount(self.filmsTable.rowCount() + 1)
            for j, el in enumerate(row):
                self.filmsTable.setItem(i, j, QTableWidgetItem(str(el)))

        for r, c in self.arr:
            self.filmsTable.item(r, c).setSelected(True)

    def update_genres_table(self):
        res = self.cur.execute("""select * from genres""").fetchall()
        title = [el[0] for el in self.cur.description]

        self.genresTable.setColumnCount(len(title))
        self.genresTable.setHorizontalHeaderLabels(title)
        self.genresTable.setRowCount(0)

        for i, row in enumerate(res[::-1]):
            self.genresTable.setRowCount(self.genresTable.rowCount() + 1)
            for j, el in enumerate(row):
                self.genresTable.setItem(i, j, QTableWidgetItem(str(el)))

        for r, c in self.arr:
            self.genresTable.item(r, c).setSelected(True)

    def closeEvent(self, event):
        self.con.close()

    def tab_changed(self, index):
        self.arr = []
        if index == 0:
            self.update_films_table()
            self.genresTable.hide()
            [el.hide() for el in self.genres_btn]
            [el.show() for el in self.films_btn]
            self.filmsTable.show()
        else:
            self.update_genres_table()
            self.filmsTable.hide()
            self.genresTable.show()
            [el.hide() for el in self.films_btn]
            [el.show() for el in self.genres_btn]

    def add_film(self):
        self.add_film_widget = AddFilmWidget(self)
        self.add_film_widget.show()

    def edit_film(self):
        self.arr = self.filmsTable.selectedItems()
        # print(*[arr[i].text() for i in range(len(arr))])
        if self.arr:
            r = self.arr[0].row()
            self.edit_film_widget = AddFilmWidget(self, film_id=r)
            self.edit_film_widget.show()
            self.statusBar().showMessage("")
        else:
            self.statusBar().showMessage("Некорректный запрос")
        res = []
        for el in self.arr:
            r, c = el.row(), el.column()
            res.append((r, c))
        self.arr = res

    def delete_film(self):
        self.arr = self.filmsTable.selectedItems()
        if not self.arr:
            self.statusBar().showMessage("Некорректный запрос")
        else:
            ids = []
            for el in self.arr:
                ids.append(self.filmsTable.item(el.row(), 0).text())

            ids = sorted(list(set(ids)), key=lambda x: int(x[0]))

            valid = QMessageBox.question(
                self, '', "Действительно удалить элементы с id " + ",".join(ids),
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if valid == QMessageBox.StandardButton.Yes:
                self.cur.execute("DELETE FROM films WHERE id IN (" + ", ".join(
                    '?' * len(ids)) + ")", ids)
                self.con.commit()
                self.update_films_table()
        # res = []
        # for el in self.arr:
        #     r, c = el.row(), el.column()
        #     res.append((r, c))
        # self.arr = res

    def add_genre(self):
        self.edit_genre_widget = AddGenreWidget(self)
        self.edit_genre_widget.show()

    def edit_genre(self):
        self.arr = self.genresTable.selectedItems()
        if self.arr:
            r = self.arr[0].row()
            self.edit_genre_widget = AddGenreWidget(self, genre_id=r)
            self.edit_genre_widget.show()
            self.statusBar().showMessage("")
        else:
            self.statusBar().showMessage("Некорректный запрос")
        res = []
        for el in self.arr:
            r, c = el.row(), el.column()
            res.append((r, c))
        self.arr = res

    def delete_genre(self):
        self.arr = self.genresTable.selectedItems()
        if not self.arr:
            self.statusBar().showMessage("Некорректный запрос")
        else:
            self.statusBar().showMessage("")
            ids = []
            for el in self.arr:
                ids.append(self.genresTable.item(el.row(), 0).text())

            ids = sorted(list(set(ids)), key=lambda x: int(x[0]))

            valid = QMessageBox.question(
                self, '', "Действительно удалить элементы с id " + ",".join(ids),
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if valid == QMessageBox.StandardButton.Yes:
                self.cur.execute("DELETE FROM genres WHERE id IN (" + ", ".join(
                    '?' * len(ids)) + ")", ids)
                self.con.commit()
                self.update_genres_table()
        # res = []
        # for el in self.arr:
        #     r, c = el.row(), el.column()
        #     res.append((r, c))
        # self.arr = res


class AddFilmWidget(QMainWindow):
    def __init__(self, parent=None, film_id=None):
        super().__init__(parent)
        self.setGeometry(100, 100, 300, 300)

        self.film_id = film_id

        self.title = QPlainTextEdit(self)
        self.title.resize(200, 30)
        self.title.move(10, 10)

        self.year = QPlainTextEdit(self)
        self.year.resize(200, 30)
        self.year.move(10, 50)

        self.duration = QPlainTextEdit(self)
        self.duration.resize(200, 30)
        self.duration.move(10, 90)

        self.comboBox = QComboBox(self)
        self.comboBox.resize(200, 30)
        self.comboBox.move(10, 130)

        self.params = {}

        res = self.parent().cur.execute("""select * from genres""").fetchall()

        for val, key in res:
            self.params[key] = self.params.get(key, val)
            self.comboBox.addItem(key)

        self.pushButton = QPushButton("Добавить", self)
        self.pushButton.resize(100, 30)
        self.pushButton.move(10, 170)

        if self.film_id is not None:
            self.pushButton.clicked.connect(self.edit_elem)
            self.pushButton.setText("Отредактировать")
            self.get_elem()
        else:
            self.pushButton.clicked.connect(self.add_elem)

    def get_adding_verdict(self):
        t = self.title.toPlainText()
        y = self.year.toPlainText()
        d = self.duration.toPlainText()

        if t and y.isdigit() and d.isdigit() and 0 <= int(y) <= 2025 and int(d) > 0:
            return True
        return False

    def get_editing_verdict(self):
        return self.get_adding_verdict()

    def add_elem(self):
        if self.get_adding_verdict():
            t = self.title.toPlainText()
            y = int(self.year.toPlainText())
            d = int(self.duration.toPlainText())
            g = self.params[self.comboBox.currentText()]

            self.parent().cur.execute(f"""insert into films(title, year, genre, duration)
             values("{t}", {y}, {g}, {d})""")

            self.parent().con.commit()
            self.parent().update_films_table()

            self.close()
        else:
            self.statusBar().showMessage("Неверный ввод!")

    def edit_elem(self):
        if self.get_editing_verdict():
            t = self.title.toPlainText()
            y = int(self.year.toPlainText())
            d = int(self.duration.toPlainText())
            g = self.params[self.comboBox.currentText()]

            res = self.parent().cur.execute(f"""update films
                                            set title = "{t}", year = {y}, genre = {g}, duration = {d}
                                            where id = {self.id}""")

            self.parent().con.commit()
            self.parent().update_films_table()

            self.close()
        else:
            self.statusBar().showMessage("Некорректное заполнение")

    def get_elem(self):
        arr = []
        for i in range(self.parent().filmsTable.columnCount()):
            el = self.parent().filmsTable.item(self.film_id, i).text()
            arr.append(el)
        self.title.setPlainText(arr[1])
        self.duration.setPlainText(arr[4])
        self.year.setPlainText(arr[3])
        self.comboBox.setCurrentText(arr[2])
        self.id = int(arr[0])


class AddGenreWidget(QMainWindow):
    def __init__(self, parent=None, genre_id=None):
        super().__init__(parent)
        self.setGeometry(100, 100, 300, 300)

        self.title = QPlainTextEdit(self)
        self.title.resize(200, 30)
        self.title.move(10, 10)

        self.pushButton = QPushButton(self)
        self.pushButton.resize(100, 30)
        self.pushButton.move(60, 50)

        self.genre_id = genre_id
        if self.genre_id is not None:
            self.pushButton.clicked.connect(self.edit_elem)
            self.pushButton.setText("Отредактировать")
            self.get_elem()
        else:
            self.pushButton.clicked.connect(self.add_genre)
            self.pushButton.setText("Добавить")

    def get_adding_verdict(self):
        t = self.title.toPlainText()
        if t:
            return True
        return False

    def get_editing_verdict(self):
        return self.get_adding_verdict()

    def add_genre(self):
        t = self.title.toPlainText()
        if self.get_adding_verdict():
            self.parent().cur.execute(f"""insert into genres(title) values ("{t}")""")
            self.parent().con.commit()
            self.parent().update_genres_table()

            self.close()
        else:
            self.statusBar().showMessage("Некорректное заполнение полей")

    def edit_elem(self):
        if self.get_adding_verdict():
            t = self.title.toPlainText()
            res = self.parent().cur.execute(f"""update genres
                                                set title = "{t}"
                                                where id = {self.id}""")
            self.parent().con.commit()
            self.parent().update_genres_table()

            self.close()
        else:
            self.statusBar().showMessage("Некорректное заполнение")

    def get_elem(self):
        arr = []
        for i in range(self.parent().genresTable.columnCount()):
            el = self.parent().genresTable.item(self.genre_id, i).text()
            arr.append(el)
        self.title.setPlainText(arr[1])
        self.id = int(arr[0])


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
