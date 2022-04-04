import tkinter as tk
import time
import threading


class MainWindow(tk.Tk):
    def __init__(self):
        super(). __init__()
        self._HEIGHT = 200
        self._WIDTH = 500
        self.title('One-point Reader') #название окна
        self.geometry(f'{self._WIDTH}x{self._HEIGHT}')
        self._list_of_widgets = []
        self._speed = 0.5
        self._max_speed = 0.1
        self._min_speed = 2
        self._create_widgets()

    def _create_widgets(self):
        line = 1
        self._tn = tk.Label(self, text='===============================')
        self._tn.grid(row=line, column=1, columnspan=4)
        self._list_of_widgets.append(self._tn)
        line += 1
        self._ent = tk.Entry(self, width=40)
        self._ent.grid(row=line, column=1, columnspan=4)
        self._list_of_widgets.append(self._ent)

        self._spd = tk.Entry(self, width=10)
        self._spd.grid(row=line, column=5, columnspan=2)
        self._list_of_widgets.append(self._spd)
        line += 1
        self._prev_btn = tk.Button(self, text='<-', command=None)
        self._prev_btn.grid(row=line, column=1)
        self._list_of_widgets.append(self._prev_btn)

        self._play_btn = tk.Button(self, text='>', command=self._start)
        self._play_btn.grid(row=line, column=2)
        self._list_of_widgets.append(self._play_btn)

        self._stop_btn = tk.Button(self, text='||', command=self._stop)
        self._stop_btn.grid(row=line, column=3)
        self._list_of_widgets.append(self._stop_btn)

        self._next_btn = tk.Button(self, text='->', command=None)
        self._next_btn.grid(row=line, column=4)
        self._list_of_widgets.append(self._next_btn)

        self._next_btn = tk.Button(self, text='+', command=self._speed_up)
        self._next_btn.grid(row=line, column=5)
        self._list_of_widgets.append(self._next_btn)

        self._next_btn = tk.Button(self, text='-', command=self._speed_down)
        self._next_btn.grid(row=line, column=6)
        self._list_of_widgets.append(self._next_btn)

    def _reading(self):
        lst = '''   Однажды, осенним вечером, одна девушка захотела прогуляться. Выходя из дома, она взяла телефон и ключи. Выйдя на улицу, она решила пройтись по аллее, которая находилась не далеко от ее дома. Когда она дошла до места, было уже темно и безлюдно. 
   Светили фонари, она шла, совсем, совсем одна. Пройдя половину аллеи, она остановилась и присела на скамейку. Она слушала тишину, прерываемую лишь легким шуршанием ветра в кронах деревьев и далекого звука машины. 
   Очнувшись от раздумий, девушка с удивлением обнаружила, что прошел целый час. Посидев еще немного, она собиралась уже пойти обратно, как вдруг фонари мигнули и погасли. Теперь единственным источником света была луна. Сильный порыв, внезапно налетевшего ветра сбросил волосы на лицо. Неподалеку раздался странный звук, похожий на бормотание. Девушка посмотрела в ту сторону, откуда шел звук, но там были только ветер и темнота. Девушка закружилась на месте, пытаясь обнаружить источник бормотания, но тщетно. Она была одна. Девушка сильно нервничая и постоянно оглядываясь пошла обратно к дому, но не успев пройти и пяти метров она наткнулась на невидимую стену. От неожиданности она даже чуть не упала, но страх мгновенно привел ее в чувство.
   - Кто здесь?
   Сама не своя от страха, девушка заметила силуэт, стоящий недалеко от нее. Секунду назад там никого не было. При свете луны девушка пыталась всмотреться в лицо, но никак не могла его рассмотреть из-за капюшона. Неожиданно силуэт начала медленно приближаться. Балахон, в котором он был не колебался при движении. Он медленно плыл. Девушка хотела закричать, но не смогла, страх сдавил ей горло. Она сделала шаг назад, потом другой, она не могла побежать, не могла повернуться спиной, так что просто пятилась. А силуэт приближался медленно, очень медленно. Девушка не могла больше пятиться, она поняла, что вообще не может больше двигаться. Что-то невидимое держало ее. Силуэт подплыл вплотную и остановился. Он оказался низкого роста, не доставал девушке даже до плечей. Они стояли не шелохнувшись. Дул ветер. Где-то вдалеке завыла сирена. Бормотание усилилось. Капюшон приподнялся, силуэт уставился на девушку. За капюшоном не было видно его лица. Но тут капюшон откинулся назад. Два огромных белых глаза не моргая смотрели на девушку. Под глазами задвигались ноздри, кривые и вертикальные. Там где должен был быть рот, раскрылась широкая щель, раскрылась медленно с еле слышным хлюпающим звуком. И неожиданно силуэт издал леденящий душу вопль и вцепился в лицо девушки...
   С тех пор эту девушку никто не видел. Но местные говорят, что иногда в особо ветреные ночи, можно услышать тихое бормотание, как-будто кто-то невидимый бормочет, что-то невнятное, а другой голос ему отвечает.
'''
        lst = lst.strip().split()
        i = 0
        while getattr(self.reading_task, "run", True):
            if i == len(lst):
                i = 0
            self._ent.delete(0, 'end')
            self._spd.delete(0, 'end')
            self._spd.insert(tk.INSERT, str(100 - (self._speed // (self._min_speed / 100))) + '%')
            self._ent.insert(tk.INSERT, lst[i].center(60))
            i += 1

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

    def _speed_up(self):
        if self._speed <= self._max_speed:
            return
        self._speed -= 0.05


if __name__ == '__main__':
    MW = MainWindow()
    MW.mainloop()
