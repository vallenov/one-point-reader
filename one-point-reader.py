import tkinter as tk
import time
import threading
import os
from tkinter import filedialog
import tkinter.messagebox as mb


class Book:

    def __init__(self, full_name, last_point=0):
        self.full_name = full_name
        self.last_point = last_point
        if full_name and os.path.exists(full_name):
            self.text = self.open_file_book()
        else:
            raise FileNotFoundError

    def open_file_book(self):
        with open(self.full_name, 'r') as book:
            return book.read().strip().split()


class MainWindow(tk.Tk):
    def __init__(self):
        super(). __init__()
        self._HEIGHT = 100
        self._WIDTH = 500
        self.title('One-point Reader') #название окна
        self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
        self._list_of_widgets = []
        self._speed = 0.5
        self._max_speed = 0.1
        self._min_speed = 1
        self.file_types = [('Текстовые файлы', '*.txt'), ('Все файлы', '*')]
        self._create_widgets()

    def _create_widgets(self):
        line = 1
        self._tn = tk.Label(self, text='===============================')
        self._tn.grid(row=line, column=1, columnspan=4)
        self._list_of_widgets.append(self._tn)

        self._open_file_btn = tk.Button(self, text='Открыть файл', command=self._show_dlg)
        self._open_file_btn.grid(row=line, column=5, columnspan=2)
        self._list_of_widgets.append(self._open_file_btn)
        line += 1
        self._ent = tk.Entry(self, width=40)
        self._ent.grid(row=line, column=1, columnspan=4)
        self._list_of_widgets.append(self._ent)

        self._spd = tk.Entry(self, width=10)
        self._spd.grid(row=line, column=5, columnspan=2)
        self._list_of_widgets.append(self._spd)
        self._spd.insert(tk.INSERT, str(100 - (self._speed // (self._min_speed / 100))) + '%')
        line += 1
        self._prev_btn = tk.Button(self, text='<-', command=self._jump_left)
        self._prev_btn.grid(row=line, column=1)
        self._list_of_widgets.append(self._prev_btn)

        self._play_btn = tk.Button(self, text='▶', command=self._start)
        self._play_btn.grid(row=line, column=2)
        self._list_of_widgets.append(self._play_btn)

        self._stop_btn = tk.Button(self, text='||', command=self._stop)
        self._stop_btn.grid(row=line, column=3)
        self._list_of_widgets.append(self._stop_btn)

        self._next_btn = tk.Button(self, text='->', command=self._jump_right)
        self._next_btn.grid(row=line, column=4)
        self._list_of_widgets.append(self._next_btn)

        self._next_btn = tk.Button(self, text='+', command=self._speed_up)
        self._next_btn.grid(row=line, column=5)
        self._list_of_widgets.append(self._next_btn)

        self._next_btn = tk.Button(self, text='-', command=self._speed_down)
        self._next_btn.grid(row=line, column=6)
        self._list_of_widgets.append(self._next_btn)

    def _reading(self):
        try:
            getattr(self, 'book')
        except AttributeError as ae:
            mb.showerror('Ошибка!', 'Не выбрана книга')
            return
        while getattr(self.reading_task, "run", True):
            self.book.last_point = 0 if self.book.last_point < 0 else self.book.last_point
            if self.book.last_point >= len(self.book.text):
                return
            self._ent.delete(0, 'end')
            self._ent.insert(tk.INSERT, self.book.text[self.book.last_point].center(60))
            self.book.last_point += 1
            time.sleep(self._speed)

    def _stop(self):
        self.reading_task.run = False

    def _start(self):
        self.reading_task = threading.Thread(target=self._reading)
        self.reading_task.start()

    def _speed_down(self):
        if self._speed >= self._min_speed:
            return
        self._speed += 0.05
        self._refresh_entry(self._spd, str(100 - (self._speed // (self._min_speed / 100))) + '%')

    def _speed_up(self):
        if self._speed <= self._max_speed:
            return
        self._speed -= 0.05
        self._refresh_entry(self._spd, str(100 - (self._speed // (self._min_speed / 100))) + '%')

    def _jump_right(self):
        self.book.last_point += 10
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    def _jump_left(self):
        self.book.last_point -= 10
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    @staticmethod
    def _refresh_entry(entry, text):
        entry.delete(0, 'end')
        entry.insert(tk.INSERT, text)

    def _show_dlg(self):
        file = self._open_file_dlg = tk.filedialog.askopenfilename(parent=self, filetypes=self.file_types)
        if file:
            self.book = Book(file)


if __name__ == '__main__':
    MW = MainWindow()
    MW.mainloop()
