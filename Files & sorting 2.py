import ctypes
import sys
import os
from typing import List, NoReturn
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *


class Sorter(object):
    """
    Класс для работы с файловой системой на основе библиотеки os.
    """

    def __init__(self) -> NoReturn:
        """Конструктор класса. Путь по умолчанию - текущая директория."""

        self.start_path = os.getcwd()
        self.absolute_path = os.getcwd()
        self.get_files()

    @property
    def path(self) -> str:
        """Возвращает текущий путь."""

        return self.absolute_path

    @property
    def filenames(self) -> List[str]:
        """Возвращает список имен файлов в текущей директории."""

        return [f.name for f in self.files]

    @property
    def subdirs(self) -> List[str]:
        """Возвращает список имен дочерних директорий в текущей директории."""

        return [d.name for d in self.get_subdirs()]

    @staticmethod
    def bit2mb(bits):
        return round(bits / 8 * 0.001, 4)

    def fnames_fsizes(self) -> List[str]:
        """Возвращает список кортежей вида (файл, размер) в текущей директории."""

        sizes = [f'{self.bit2mb(f.stat().st_size)} мб' for f in self.files]
        lens = [len(size) for size in sizes]
        names = [f.name for f in self.files]

        spis = []
        for size, name in zip(sizes, names):
            spacer = max(lens) - len(size)
            spis.append(size + ' ' * spacer + f' - {name}')

        return spis

    @staticmethod
    def fc(path: str) -> bool:
        """
        Возвращает логическое значение, является ли путь файлом.

        Args:
        path - путь
        """

        if type(path) != str:
            raise TypeError('Путь должен быть строкой!')

        return os.path.isfile(path)

    @staticmethod
    def dc(path: str) -> bool:
        """
        Возвращает логическое значение, является ли путь директорией.

        Args:
        path - путь
        """

        if type(path) != str:
            raise TypeError('Путь должен быть строкой!')

        return os.path.isdir(path)

    @staticmethod
    def get_abs(path: str) -> str:
        """
        Возвращает абсолютный путь из относительного.

        Args:
        path - путь
        """

        if type(path) != str:
            raise TypeError('Путь должен быть строкой!')

        if len(path.split('\\')) == 1:
            return path

        return os.path.abspath(path)

    def to_parent_dir(self) -> NoReturn:
        """Меняет директорию на родительскую."""

        dirs = self.absolute_path.split('\\')
        parent_dir = '\\'.join(dirs[:-1])
        if self.dc(parent_dir):
            self.set_dir(parent_dir)
        else:
            print('Нет возможности переместиться в родительскую директорию!')

    def to_sub_dir(self, name: str) -> NoReturn:
        """
        Меняет директорию на дочернюю.

        Args:
        name - имя дочерней директории
        """

        if type(name) != str:
            raise TypeError('Имя папки должно быть строкой!')

        if name in self.subdirs:
            self.set_dir(os.path.join(self.absolute_path, name))
        else:
            print(f'Нет такой директории! Можете выбрать из списка: {self.subdirs}')

    def get_subdirs(self):
        """Возвращает список дочерних директорий в текущей директории."""

        subdirs = []
        for entity in os.scandir(self.absolute_path):
            if self.dc(entity.path):
                subdirs.append(entity)

        return subdirs

    def get_files(self) -> NoReturn:
        """Задает список файлов в текущей директории."""

        files = []
        for entity in os.scandir(self.absolute_path):
            if self.fc(entity.path):
                files.append(entity)
        self.files = files

    def set_dir(self, path: str) -> NoReturn:
        """
        Меняет текущую директорию.

        Args:
        path - новый путь к директории
        """

        if type(path) != str:
            raise TypeError('Путь должен быть строкой!')

        if self.dc(path):
            self.absolute_path = self.get_abs(path)
            self.get_files()
        else:
            print('Указанный путь не является директорией!')

    def bubble_sort(self, reverse: bool = False, mode: str = 'name') -> NoReturn:
        """
        Алгоритм сортировки пузырьком.

        Args:
        reverse - нужна ли сортировка по убыванию
        mode - параметр, по которому будет выполнена сортировка
        """

        if type(reverse) != bool:
            raise TypeError('Параметр reverse должен быть типа bool!')

        if type(mode) != str:
            raise TypeError('Параметр mode должен быть типа str!')

        our_list = self.files.copy()

        possible = ['name', 'size']
        if mode not in possible:
            raise ValueError(f'Недопустимый параметр сортировки, выберите один из списка! {possible}')

        has_swapped = True

        num_of_iterations = 0

        while has_swapped:
            has_swapped = False

            for i in range(len(our_list) - num_of_iterations - 1):
                if mode == 'name':
                    if not reverse:
                        case = our_list[i].name >= our_list[i + 1].name
                    else:
                        case = our_list[i].name <= our_list[i + 1].name

                elif mode == 'size':
                    if not reverse:
                        case = our_list[i].stat().st_size >= our_list[i + 1].stat().st_size
                    else:
                        case = our_list[i].stat().st_size <= our_list[i + 1].stat().st_size

                if case:
                    our_list[i], our_list[i + 1] = our_list[i + 1], our_list[i]
                    has_swapped = True

            num_of_iterations += 1

        self.files = our_list


class Browser(QWidget):
    """
    Класс, реализующий визуальный интерфейс проекта. Наследуется от виджета.
    """

    def __init__(self) -> NoReturn:
        """
        Конструктор класса. Создает объект для работы с файлами и запускает графический интерфейс.
        """

        super().__init__()

        self.Sorter = Sorter()
        self.initUI()

    def UPD(self) -> NoReturn:
        """
        Обновляет текстовые элементы после каких=либо действий.
        """

        self.path.setText(self.Sorter.path)
        self.flist.clear()
        self.flist.addItems(self.Sorter.fnames_fsizes())
        self.slist.clear()
        self.slist.addItems(self.Sorter.subdirs)

    def initUI(self) -> NoReturn:
        """
        Реализация графического интерфейса.
        """

        # Установка параметров окна
        self.setGeometry(1000, 400, 800, 500)
        self.setWindowTitle('Files & Sorting')

        # Установка иконки окна
        icon_image_url = 'https://cdn0.iconfinder.com/data/icons/material-design-flat/24/folder-1024.png'
        self.nam = QNetworkAccessManager(self)
        self.nam.finished.connect(self.set_window_icon_from_reply)
        self.nam.get(QNetworkRequest(QUrl(icon_image_url)))

        myappid = u'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        main_layout = QVBoxLayout(self)

        # Наполнение содержимого
        pred1 = QLabel('Текущий путь:')  # Строка сверху
        main_layout.addWidget(pred1)

        self.path = QLineEdit(self.Sorter.path)  # Строка с текущим путем
        self.path.returnPressed.connect(self.path_change)
        main_layout.addWidget(self.path)

        lists = QHBoxLayout()

        slist_box = QVBoxLayout()
        slist_box.addWidget(QLabel('Список под-директорий:'))  # Пояснение к списку слева
        self.slist = QListWidget()  # Список слева
        self.slist.addItems(self.Sorter.subdirs)
        self.slist.setMaximumWidth(250)
        self.slist.itemClicked.connect(self.list_act)
        slist_box.addWidget(self.slist)

        self.mtpd = QPushButton('В родительскую директорию')  # Кнопка возврата в род. директорию
        self.mtpd.clicked.connect(self.mtpd_act)
        slist_box.addWidget(self.mtpd)

        self.mtsd = QPushButton('В стартовую директорию')  # Кнопка возврата в стартовую директорию
        self.mtsd.clicked.connect(self.mtsd_act)
        slist_box.addWidget(self.mtsd)

        flist_box = QVBoxLayout()
        flist_box.addWidget(QLabel('Список файлов:'))  # Пояснение к списку справа
        self.flist = QListWidget()  # Список справа
        self.flist.addItems(self.Sorter.fnames_fsizes())
        self.flist.setMinimumWidth(500)
        flist_box.addWidget(self.flist)

        btns = QHBoxLayout()
        self.mode = QComboBox()  # Выпадающий список параметров сортировки 1
        self.mode.addItems(['По имени', 'По размеру'])
        btns.addWidget(self.mode)

        self.reverse = QComboBox()  # Выпадающий список параметров сортировки 2
        self.reverse.addItems(['По возрастанию', 'По убыванию'])
        btns.addWidget(self.reverse)
        flist_box.addLayout(btns)

        self.sort = QPushButton('Сортировать')  # Кнопка сортировки
        self.sort.clicked.connect(self.sort_act)
        flist_box.addWidget(self.sort)

        lists.addLayout(slist_box)
        lists.addLayout(flist_box)

        main_layout.addLayout(lists)

        self.setLayout(main_layout)

        self.show()  # Отображение интерфейса

    def list_act(self, item) -> NoReturn:
        """
        Действия по нажатию на элемент списка слева.
        """

        self.Sorter.to_sub_dir(item.text())
        self.UPD()

    def mtpd_act(self) -> NoReturn:
        """
        Действия по нажатию на кнопку "В родительскую директорию".
        """

        self.Sorter.to_parent_dir()
        self.UPD()

    def sort_act(self) -> NoReturn:
        """
        Действия по нажатию на кнопку "Сортировать".
        """

        conv = {'По убыванию': True,
                'По возрастанию': False,
                'По имени': 'name',
                'По размеру': 'size'}
        self.Sorter.bubble_sort(mode=conv[self.mode.currentText()], reverse=conv[self.reverse.currentText()])
        self.UPD()

    def mtsd_act(self) -> NoReturn:
        """
        Действия по нажатию на кнопку "В стартовую директорию".
        """

        self.Sorter.set_dir(self.Sorter.start_path)
        self.UPD()

    def path_change(self) -> NoReturn:
        """
        Действия при вводе нового пути в окно сверху.
        """

        self.Sorter.set_dir(self.path.text())
        self.UPD()

    def set_window_icon_from_reply(self, reply) -> NoReturn:
        """
        Установка иконки приложения.
        """

        pixmap = QPixmap()
        pixmap.loadFromData(reply.readAll())
        icon = QIcon(pixmap)
        self.setWindowIcon(icon)


app = QCoreApplication.instance()
if app is None:
    app = QApplication(sys.argv)

b = Browser()
sys.exit(app.exec())
