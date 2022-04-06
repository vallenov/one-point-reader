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
        self._speed = 50
        self._max_speed = 100
        self._min_speed = 10
        self.file_types = [('Текстовые файлы', '*.txt'), ('Все файлы', '*')]
        self._create_widgets()

    def _create_widgets(self):
        row = 1
        col = 1
        self._tn = tk.Label(self, text='===============================')
        self._tn.grid(row=row, column=col, columnspan=5)
        self._list_of_widgets.append(self._tn)
        col += 5
        self._open_file_btn = tk.Button(self, text='Открыть файл', command=self._show_dlg)
        self._open_file_btn.grid(row=row, column=col, columnspan=2)
        self._list_of_widgets.append(self._open_file_btn)
        row += 1
        col = 1
        self._ent = tk.Entry(self, width=40)
        self._ent.grid(row=row, column=col, columnspan=5)
        self._list_of_widgets.append(self._ent)
        col += 5
        self._spd = tk.Entry(self, width=10)
        self._spd.grid(row=row, column=col, columnspan=2)
        self._list_of_widgets.append(self._spd)
        self._spd.insert(tk.INSERT, f'{self._speed}%')
        row += 1
        col = 1
        self._prev_btn = tk.Button(self, text='<-', command=self._jump_left)
        self._prev_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._prev_btn)
        col += 1
        self._play_btn = tk.Button(self, text='▶', command=self._start)
        self._play_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._play_btn)
        col += 1
        self._pause_btn = tk.Button(self, text='||', command=self._pause)
        self._pause_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._pause_btn)
        col += 1
        self._stop_btn = tk.Button(self, text='☐', command=self._stop)
        self._stop_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._stop_btn)
        col += 1
        self._next_btn = tk.Button(self, text='->', command=self._jump_right)
        self._next_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._next_btn)
        col += 1
        self._next_btn = tk.Button(self, text='+', command=self._speed_up)
        self._next_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._next_btn)
        col += 1
        self._next_btn = tk.Button(self, text='-', command=self._speed_down)
        self._next_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._next_btn)

    def _check_book(self, show_error=False):
        try:
            getattr(self, 'book')
        except AttributeError:
            if show_error:
                mb.showerror('Ошибка!', 'Не выбрана книга')
            return False
        else:
            return True

    def _reading(self):
        if not self._check_book(True):
            return
        while getattr(self.reading_task, "run", True):
            self.book.last_point = 0 if self.book.last_point < 0 else self.book.last_point
            if self.book.last_point >= len(self.book.text):
                return
            self._ent.delete(0, 'end')
            self._ent.insert(tk.INSERT, self.book.text[self.book.last_point].center(60))
            self.book.last_point += 1
            time.sleep(0.05 + ((100 - self._speed) / 150))

    def _pause(self):
        if not self._check_book():
            return
        self.reading_task.run = False

    def _stop(self):
        if not self._check_book():
            return
        self.reading_task.run = False
        self.book.last_point = 0
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    def _start(self):
        self.reading_task = threading.Thread(target=self._reading)
        self.reading_task.start()

    def _speed_down(self):
        if self._speed <= self._min_speed:
            return
        self._speed -= 5
        self._refresh_entry(self._spd, f'{self._speed}%')

    def _speed_up(self):
        if self._speed >= self._max_speed:
            return
        self._speed += 5
        self._refresh_entry(self._spd, f'{self._speed}%')

    def _jump_right(self):
        if not self._check_book():
            return
        self.book.last_point += 10
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    def _jump_left(self):
        if not self._check_book():
            return
        self.book.last_point -= 10
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    @staticmethod
    def _refresh_entry(entry: tk.Entry, text: str):
        entry.delete(0, 'end')
        entry.insert(tk.INSERT, text)

    def _show_dlg(self):
        file = self._open_file_dlg = tk.filedialog.askopenfilename(parent=self, filetypes=self.file_types)
        if file:
            self.book = Book(file)
            file_name = file.split('/')[-1]
            self._refresh_entry(self._ent, file_name.center(60))


if __name__ == '__main__':
    MW = MainWindow()
    MW.mainloop()
