import tkinter as tk
from PIL import ImageTk, Image
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
                self.len = len(self.text)
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
            if not self._config.has_section('LAST_BOOK'):
                self._config.add_section('LAST_BOOK')
            if not self._config.has_section('BOOKS_LAST_POINTS'):
                self._config.add_section('BOOKS_LAST_POINTS')
            self._ini_save()
            if self._config.has_option('LAST_BOOK', 'name'):
                self.book = Book(self._config.get('LAST_BOOK', 'name'))
                self._refresh_entry(self._ent, self.book.name.center(60))
                self._regimes_btn.grid(row=1, column=8)
                self._WIDTH += 100
                self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
                if self._config.has_option('BOOKS_LAST_POINTS', self.book.name):
                    self.book.last_point = int(self._config.get('BOOKS_LAST_POINTS', self.book.name))
                    self._add_scale()
                    self._load_scale(self.book.last_point)

    def _on_closing(self):
        if hasattr(self, 'book'):
            self._config.set('BOOKS_LAST_POINTS', self.book.name, str(self.book.last_point))
            self._ini_save()
            if hasattr(self, 'reading_task') and hasattr(self.reading_task, 'run'):
                self.reading_task.run = False
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
        self._regimes_btn = tk.Button(self, text='Режим чтения', command=self._change_widgets)

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
        prev_photo = ImageTk.PhotoImage(file=os.path.join('static', 'image', 'prev.png'))
        self._prev_btn = tk.Button(self, text='<-', command=self._jump_left, image=prev_photo)
        self._prev_btn.image = prev_photo
        self._prev_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._prev_btn)
        col += 1
        play_photo = ImageTk.PhotoImage(file=os.path.join('static', 'image', 'play.png'))
        self._play_btn = tk.Button(self, text='▶', command=self._start, image=play_photo)
        self._play_btn.image = play_photo
        self._play_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._play_btn)
        col += 1
        pause_photo = ImageTk.PhotoImage(file=os.path.join('static', 'image', 'pause.png'))
        self._pause_btn = tk.Button(self, text='||', command=self._pause, image=pause_photo)
        self._pause_btn.image = pause_photo
        self._pause_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._pause_btn)
        col += 1
        stop_photo = ImageTk.PhotoImage(file=os.path.join('static', 'image', 'stop.png'))
        self._stop_btn = tk.Button(self, text='☐', command=self._stop, image=stop_photo)
        self._stop_btn.image = stop_photo
        self._stop_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._stop_btn)
        col += 1
        next_photo = ImageTk.PhotoImage(file=os.path.join('static', 'image', 'next.png'))
        self._next_btn = tk.Button(self, text='->', command=self._jump_right, image=next_photo)
        self._next_btn.image = next_photo
        self._next_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._next_btn)
        col += 1
        plus_photo = ImageTk.PhotoImage(file=os.path.join('static', 'image', 'plus.png'))
        self._speed_up_btn = tk.Button(self, text='+', command=self._speed_up, image=plus_photo)
        self._speed_up_btn.image = plus_photo
        self._speed_up_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._speed_up_btn)
        col += 1
        minus_photo = ImageTk.PhotoImage(file=os.path.join('static', 'image', 'minus.png'))
        self._speed_down_btn = tk.Button(self, text='-', command=self._speed_down, image= minus_photo)
        self._speed_down_btn.image = minus_photo
        self._speed_down_btn.grid(row=row, column=col)
        self._list_of_widgets.append(self._speed_down_btn)

        self.cur_row = row

        self._show_widget_flag = not self._show_widget_flag

    @staticmethod
    def _resize_img(path):
        p = Image.open(path)
        p = p.resize((25, 25), Image.ANTIALIAS)
        p.save(path)

    def _ini_save(self):
        """
        Сохранение изменений в іnі-файл
        """
        with open(os.path.join(os.getcwd(), 'One-point-reader.ini'), 'w') as f:
            self._config.write(f)

    def _add_scale(self):
        """
        Create reading progress bar
        """
        if self._exist_scale:
            self._list_of_widgets.pop(self._list_of_widgets.index(self._scale))
            self._scale.destroy()
            self._list_of_widgets.pop(self._list_of_widgets.index(self._lbl))
            self._lbl.destroy()
            self._exist_scale = False
        else:
            self.geometry(f'{self._WIDTH}x{self._HEIGHT + 20}')
            self._var = tk.IntVar()
            self.cur_row += 1
            self._lbl = tk.Label(self, textvariable=self._var)
            self._lbl.grid(row=self.cur_row, column=1)
            self._list_of_widgets.append(self._lbl)
            self._scale = ttk.Scale(self, from_=0, to=self.book.len, command=self._set_scale)
            self._scale.grid(row=self.cur_row, column=2, columnspan=5, sticky='NSEW')
            self._list_of_widgets.append(self._scale)
            self._exist_scale = True

    def _fill_text_place(self, start: int, down: bool) -> str and int:
        """
        Get newt or prev page
        :param start: start position
        :param down: direction (up or down)
        """
        fin = start
        while True:
            if down:
                if len(' '.join(self.book.text[start:fin])) > 56 * 23 or fin >= self.book.len:
                    break
                fin += 1
            else:
                if len(' '.join(self.book.text[start:fin])) > 56 * 23 or start <= 0:
                    down = True
                    continue
                start -= 1
        return self.book.text[start:fin]

    def _callback(self, event):
        """
        Get word was clicked
        """
        index = event.widget.index("@%s,%s" % (event.x, event.y))
        simbol_pos = int(index.split('.')[1])
        cnt = 0
        buf = 0
        for word in self._fill_text_place(self.book.last_point, down=True):
            if buf + len(word) >= simbol_pos:
                break
            cnt += 1
            buf += len(word) + 1
        self.book.last_point += cnt
        self._change_widgets()
        self._refresh_entry(self._ent, self.book.text[self.book.last_point].center(60))

    def _change_widgets(self):
        """
        Change reading regimes
        """
        [widget.grid() for widget in self._list_of_widgets] if self._show_widget_flag \
            else [widget.grid_remove() for widget in self._list_of_widgets]
        if not self._show_widget_flag:
            self._pause()
            self._WIDTH = 600
            self.geometry('600x400')
            self._txt = tk.Text(self, width=57, height=23)
            self._txt.grid(row=1, column=1, rowspan=99)
            self._txt.insert('1.0', ' '.join(self._fill_text_place(self.book.last_point, down=True)))
            self._txt.bind("<Button-1>", self._callback)
            self._up_btn = tk.Button(self, text='⇑', command=self._up_text)
            self._up_btn.grid(row=33, column=8)
            self._down_btn = tk.Button(self, text='⇓', command=self._down_text)
            self._down_btn.grid(row=34, column=8)
        else:
            self.geometry(f'{self._WIDTH}x{self._HEIGHT + 20}')
            self._txt.grid_remove()
            self._up_btn.grid_remove()
            self._down_btn.grid_remove()
        self._show_widget_flag = not self._show_widget_flag

    def _down_text(self):
        """
        Load next page
        """
        self.book.last_point += len(self._fill_text_place(self.book.last_point, down=True))
        self.book.last_point = self.book.len \
            if self.book.last_point > self.book.len \
            else self.book.last_point
        self._txt.delete('0.0', 'end')
        self._txt.insert('0.0', ' '.join(self._fill_text_place(self.book.last_point, down=True)))

    def _up_text(self):
        """
        Load prev page
        """
        self._txt.delete('0.0', 'end')
        self._txt.insert('0.0', ' '.join(self._fill_text_place(self.book.last_point, down=False)))
        self.book.last_point -= len(self._fill_text_place(self.book.last_point, down=False))
        self.book.last_point = 0 \
            if self.book.last_point < 0 \
            else self.book.last_point

    def _load_scale(self, val):
        """
        Load value of Scale
        """
        v = int(float(val) / (self.book.len / 100))
        self.book.last_point = int(float(val)) - 1
        self._var.set(v)
        self._scale.set(val)

    def _set_scale(self, val):
        """
        Set value of Scale
        """
        v = int(float(val) / (self.book.len / 100))
        self.book.last_point = int(float(val)) - 1
        self._var.set(v)

    def _check_book(self, show_error=False):
        """
        Book exist check
        """
        if not hasattr(self, 'book'):
            if show_error:
                mb.showerror('Ошибка!', 'Не выбрана книга')
            return False
        if not hasattr(self, 'reading_task'):
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
        self._config.set('BOOKS_LAST_POINTS', self.book.name, str(self.book.last_point))
        self._ini_save()
        while getattr(self.reading_task, "run", True):
            self.book.last_point = 0 if self.book.last_point < 0 else self.book.last_point
            if self.book.last_point >= self.book.len:
                return
            self._ent.delete(0, 'end')
            self._ent.insert(tk.INSERT, self.book.text[self.book.last_point].center(60))
            self.book.last_point += 1
            time.sleep(0.05 + ((100 - self._speed) / 150))

    def _pause(self):
        if not self._check_book() or not self.book.ready_to_read:
            return
        self._config.set('BOOKS_LAST_POINTS', self.book.name, str(self.book.last_point))
        self._ini_save()
        self.reading_task.run = False
        self._reading_process = False

    def _stop(self):
        if not self._check_book() or not self.book.ready_to_read:
            return
        self._config.set('BOOKS_LAST_POINTS', self.book.name, str(self.book.last_point))
        self._ini_save()
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
        Clear entry and fill it
        """
        entry.delete(0, 'end')
        entry.insert(tk.INSERT, text)

    def _show_dlg(self):
        """
        Show file system
        """
        self._pause()
        file = self._open_file_dlg = tk.filedialog.askopenfilename(parent=self, filetypes=self.file_types)
        if file:
            self.book = Book(file)
            if not self.book.ready_to_read:
                return
            file_name = file.split('/')[-1]
            self._refresh_entry(self._ent, file_name.center(60))
            self._add_scale()
            self._regimes_btn.grid(row=1, column=8)
            self.geometry(f'600x120')
            self._config.set('LAST_BOOK', 'name', self.book.full_name)
            self._ini_save()
            if self._config.has_option('BOOKS_LAST_POINTS', self.book.name):
                self.book.last_point = int(self._config.get('BOOKS_LAST_POINTS', self.book.name))
            self._add_scale()
            self._load_scale(self.book.last_point)


if __name__ == '__main__':
    MW = MainWindow()
    MW.mainloop()
