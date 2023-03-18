import os
from typing import List, Tuple, NoReturn


class Sorter(object):
    """
    Класс для работы с файловой системой на основе библиотеки os.
    """

    def __init__(self) -> NoReturn:
        """Конструктор класса. Путь по умолчанию - текущая директория."""

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

    def fnames_fsizes(self) -> List[Tuple[str, str]]:
        """Возвращает список кортежей вида (файл, размер) в текущей директории."""

        return [(f.name, f.stat().st_size) for f in self.files]

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
