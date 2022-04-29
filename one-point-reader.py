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
import configparser


class Book:

    def __init__(self, full_name, last_point=0):
        self.full_name = full_name
        self.name = self.full_name.split('/')[-1]
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

    def open_txt(self) -> list:
        """
        Work with txt files
        """
        with open(self.full_name, 'r') as book:
            return book.read().strip().split()

    def open_docx(self) -> list:
        """
        Work with docx files
        """
        text = ''
        doc = docx.Document(self.full_name)
        for paragraph in doc.paragraphs:
            text += f'{paragraph.text}\n'
        return text.split()

    def open_pdf(self) -> list:
        """
        Work with PDF files
        """
        text = ''
        with fitz.open(self.full_name) as doc:
            for page in doc:
                tmp = page.get_text()
                if '. .' not in tmp:
                    text += tmp
        return text.split()

    def open_fb2(self) -> list:
        """
        Work with fb2 files
        """
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
        super().__init__()
        self._HEIGHT = 100
        self._WIDTH = 500
        self.title('One-point Reader')  # название окна
        self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._list_of_widgets = []
        self._speed = 50
        self._max_speed = 100
        self._min_speed = 10
        self._exist_scale = False
        self._show_widget_flag = True
        self._reading_process = False
        self.file_types = [('FB2', '*.fb2'),
                           ('Office Word', '*.docx'),
                           ('Текстовые файлы', '*.txt'),
                           ('PDF', '*.pdf'),
                           ('Все файлы', '*')]
        self._create_widgets()
        self._config = configparser.ConfigParser()
        if os.path.exists(os.path.join(os.getcwd(), 'One-point-reader.ini')):
            self._config.read(os.path.join(os.getcwd(), 'One-point-reader.ini'))
            if self._config.has_option('LAST_BOOK', 'name'):
                self.book = Book(self._config.get('LAST_BOOK', 'name'))
                self._refresh_entry(self._ent, self.book.name.center(60))

    def _on_closing(self):
        if not self._config.has_section('BOOKS_LAST_POINTS'):
            self._config.add_section('BOOKS_LAST_POINTS')
        self._config.set('BOOKS_LAST_POINTS', self.book.name, str(self.book.last_point))
        self._ini_save()
        self.destroy()

    def _create_widgets(self):
        """
        Create GUI
        """
        row = 1
        col = 1
        self._tn = tk.Label(self, text='='.center(30, '='))
        self._tn.grid(row=row, column=col, columnspan=5)
        self._list_of_widgets.append(self._tn)
        col += 5
        self._open_file_btn = tk.Button(self, text='Открыть файл', command=self._show_dlg)
        self._open_file_btn.grid(row=row, column=col, columnspan=2)
        self._list_of_widgets.append(self._open_file_btn)
        col += 2
        self._rej_btn = tk.Button(self, text='Режим чтения', command=self._change_widgets)

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
        self._speed_up_btn = tk.Button(self, text='+', command=self._speed_up)
        self._speed_up_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._speed_up_btn)
        col += 1
        self._speed_down_btn = tk.Button(self, text='-', command=self._speed_down)
        self._speed_down_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._speed_down_btn)

        self.cur_row = row

        self._show_widget_flag = not self._show_widget_flag

    def _ini_save(self):
        '''
        Сохранение изменений в іnі-файл
        '''
        with open(os.path.join(os.getcwd(), 'One-point-reader.ini'), 'w') as f:
            self._config.write(f)

    def _add_scale(self):
        """
        Create reading progress bar
        """
        self._HEIGHT += 20
        self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
        self._HEIGHT -= 20
        self.cur_row += 1

        self._var = tk.IntVar()
        if not self._exist_scale:
            self._lbl = tk.Label(self, textvariable=self._var)
            self._lbl.grid(row=self.cur_row, column=1)

            self._scale = ttk.Scale(self, from_=0, to=len(self.book.text), command=self._set_scale)
            self._scale.grid(row=self.cur_row, column=2, columnspan=5, sticky='NSEW')
            self._list_of_widgets.append(self._scale)
        self._exist_scale = True

    @staticmethod
    def _fill_text_place(start: int, book_text: list, down: bool) -> str:
        tmp = []
        buf = 0
        while True:
            if down:
                if buf + len(book_text[start]) > 57 * 20 or start >= len(book_text):
                    break
                buf += len(book_text[start])
                tmp.append(book_text[start])
                start += 1
            else:
                if buf + len(book_text[start]) > 57 * 20 or start <= 0:
                    tmp = tmp[::-1]
                    down = True
                    continue
                buf += len(book_text[start])
                tmp.append(book_text[start])
                start -= 1
        return ' '.join(tmp)

    def _callback(self, event):
        index = event.widget.index("@%s,%s" % (event.x, event.y))
        simbol_pos = int(index.split('.')[1])
        cnt = 0
        buf = 0
        for word in self._fill_text_place(self.book.last_point, self.book.text, down=True).split():
            if buf + len(word) >= simbol_pos:
                break
            cnt += 1
            buf += len(word) + 1
        self.book.last_point += cnt
        self._change_widgets()
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    def _change_widgets(self):
        [widget.grid() for widget in self._list_of_widgets] if self._show_widget_flag \
            else [widget.grid_remove() for widget in self._list_of_widgets]
        if not self._show_widget_flag:
            self._pause()
            self.geometry('600x400')
            self._txt = tk.Text(self, width=57, height=23)
            self._txt.grid(row=1, column=1, rowspan=99)
            self._txt.insert('1.0', self._fill_text_place(self.book.last_point, self.book.text, down=True))
            self._txt.bind("<Button-1>", self._callback)
            self._up_btn = tk.Button(self, text='⇑', command=self._up_text)
            self._up_btn.grid(row=33, column=8)
            self._down_btn = tk.Button(self, text='⇓', command=self._down_text)
            self._down_btn.grid(row=34, column=8)
        else:
            self.geometry(f'{self._WIDTH + 100}x{self._HEIGHT + 20}')
            self._txt.grid_remove()
            self._up_btn.grid_remove()
            self._down_btn.grid_remove()
        self._show_widget_flag = not self._show_widget_flag

    def _down_text(self):
        print(self.book.last_point)
        print(len(self._fill_text_place(self.book.last_point, self.book.text, down=True).split()))
        self.book.last_point += len(self._fill_text_place(self.book.last_point, self.book.text, down=True).split())
        self.book.last_point = len(self.book.text) \
            if self.book.last_point > len(self.book.text) \
            else self.book.last_point
        self._txt.delete('0.0', 'end')
        self._txt.insert('0.0', self._fill_text_place(self.book.last_point, self.book.text, down=True))

    def _up_text(self):
        self.book.last_point -= len(self._fill_text_place(self.book.last_point, self.book.text, down=False).split())
        self.book.last_point = 0 \
            if self.book.last_point < 0 \
            else self.book.last_point
        self._txt.delete('0.0', 'end')
        self._txt.insert('0.0', self._fill_text_place(self.book.last_point, self.book.text, down=False))

    def _set_scale(self, val):
        """
        Set value of Scale
        """
        v = int(float(val) / (len(self.book.text) / 100))
        self.book.last_point = int(float(val)) - 1
        self._var.set(v)

    def _check_book(self, show_error=False):
        """
        Book exist check
        """
        try:
            getattr(self, 'book')
        except AttributeError:
            if show_error:
                mb.showerror('Ошибка!', 'Не выбрана книга')
            return False
        try:
            getattr(self, 'reading_task')
        except AttributeError:
            return False
        return True

    def _reading(self):
        """
        Separate reading task
        """
        if self._reading_process:
            return
        else:
            self._reading_process = True
        if not self._check_book(True) or not self.book.ready_to_read:
            return
        if self._config.has_section('BOOKS_LAST_POINTS') and \
                self._config.has_option('BOOKS_LAST_POINTS', self.book.name):
            self.book.last_point = int(self._config.get('BOOKS_LAST_POINTS', self.book.name))
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
        """
        Decrease in reading speed
        """
        if self._speed <= self._min_speed:
            return
        self._speed -= 5
        self._refresh_entry(self._spd, f'{self._speed}%')

    def _speed_up(self):
        """
        Increase in reading speed
        """
        if self._speed >= self._max_speed:
            return
        self._speed += 5
        self._refresh_entry(self._spd, f'{self._speed}%')

    def _jump_right(self):
        """
        Skip 10 words
        """
        if not self._check_book() or not self.book.ready_to_read:
            return
        self.book.last_point += 10
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    def _jump_left(self):
        """
        Rewind 10 words
        """
        if not self._check_book() or not self.book.ready_to_read:
            return
        self.book.last_point -= 10
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    @staticmethod
    def _refresh_entry(entry: tk.Entry, text: str):
        """
        Clear entry and fill
        """
        entry.delete(0, 'end')
        entry.insert(tk.INSERT, text)

    def _show_dlg(self):
        """
        Show file system
        """
        file = self._open_file_dlg = tk.filedialog.askopenfilename(parent=self, filetypes=self.file_types)
        if file:
            self.book = Book(file)
            if not self.book.ready_to_read:
                return
            file_name = file.split('/')[-1]
            self._refresh_entry(self._ent, file_name.center(60))
            self._add_scale()
            self._rej_btn.grid(row=1, column=8)
            self.geometry(f'600x120')
            if not self._config.has_section('LAST_BOOK'):
                self._config.add_section('LAST_BOOK')
            self._config.set('LAST_BOOK', 'NAME', self.book.full_name)
            self._ini_save()


if __name__ == '__main__':
    MW = MainWindow()
    MW.mainloop()
