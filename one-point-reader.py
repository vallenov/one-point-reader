import tkinter as tk
from tkinter import ttk
import time
import threading
import os
from tkinter import filedialog
import tkinter.messagebox as mb
import docx
import fitz
from bs4 import BeautifulSoup


class Book:

    def __init__(self, full_name, last_point=0):
        self.full_name = full_name
        self.last_point = last_point
        self.ready_to_read = False
        self.map = {
            'txt': self.open_txt,
            'docx': self.open_docx,
            'pdf': self.open_pdf,
            'fb2': self.open_fb2
        }
        if full_name and os.path.exists(full_name):
            extension = full_name.split('.')[-1]
            func = self.map.get(extension, None)
            if func:
                self.text = func()
                self.ready_to_read = True
            else:
                mb.showerror('Ошибка!', 'Неподдерживаемый формат файла')
        else:
            raise FileNotFoundError

    def open_txt(self):
        with open(self.full_name, 'r') as book:
            return book.read().strip().split()

    def open_docx(self):
        text = ''
        doc = docx.Document(self.full_name)
        for paragraph in doc.paragraphs:
            text += f'{paragraph.text}\n'
        return text.split()

    def open_pdf(self):
        text = ''
        with fitz.open(self.full_name) as doc:
            for page in doc:
                tmp = page.get_text()
                if '. .' in tmp:
                    continue
                text += tmp
        return text.split()

    def open_fb2(self):
        with open(self.full_name, 'r') as fb2:
            data = fb2.read()
        soup = BeautifulSoup(data, 'lxml')
        body = soup.find('body')
        sections = body.find_all('section')
        text = ''
        for section in sections:
            fragments = section.find_all('p')
            for fragment in fragments:
                text += f'{fragment.text}\n'
        return text.split()


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
        self._exist_scale = False
        self._reading_process = False
        self.file_types = [('FB2', '*.fb2'),
                           ('Office Word', '*.docx'),
                           ('Текстовые файлы', '*.txt'),
                           ('PDF', '*.pdf'),
                           ('Все файлы', '*')]
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

        self.cur_row = row

    def _add_scale(self):
        if self._exist_scale:
            self._lbl.grid_remove()
            self._scale.grid_remove()

        self.geometry(f'{self._WIDTH}x{self._HEIGHT+20}')
        self.cur_row += 1

        self._var = tk.IntVar()
        self._lbl = tk.Label(self, textvariable=self._var)
        self._lbl.grid(row=self.cur_row, column=1)

        self._scale = ttk.Scale(self, from_=0, to=len(self.book.text), command=self._set_scale)
        self._scale.grid(row=self.cur_row, column=2, columnspan=5, sticky='NSEW')
        self._list_of_widgets.append(self._next_btn)
        self._exist_scale = True

    def _set_scale(self, val):
        v = int(float(val) / (len(self.book.text) / 100))
        self.book.last_point = int(float(val)) - 1
        self._var.set(v)

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
        if self._reading_process:
            return
        else:
            self._reading_process = True
        if not self._check_book(True) or not self.book.ready_to_read:
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
        if not self._check_book() or not self.book.ready_to_read:
            return
        self.reading_task.run = False
        self._reading_process = False

    def _stop(self):
        if not self._check_book() or not self.book.ready_to_read:
            return
        self.reading_task.run = False
        self._reading_process = False
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
        if not self._check_book() or not self.book.ready_to_read:
            return
        self.book.last_point += 10
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    def _jump_left(self):
        if not self._check_book() or not self.book.ready_to_read:
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
            if not self.book.ready_to_read:
                return
            file_name = file.split('/')[-1]
            self._refresh_entry(self._ent, file_name.center(60))
            self._add_scale()


if __name__ == '__main__':
    MW = MainWindow()
    MW.mainloop()
