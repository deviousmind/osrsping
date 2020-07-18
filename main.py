from tkinter import *
import os
import threading
import queue
from multiprocessing.dummy import Pool


class PingUI:
    def __init__(self, master, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.master = master
        master.title("OSRS World Ping Tester")
        master.geometry('800x600')
        lbl = Label(master, text="Worlds", font=("Comic Sans MS", 12))
        lbl.grid(column=1, row=0)
        btn = Button(master, text="Refresh", command=self.on_refresh)
        btn.grid(column=5, row=0)
        pings = []
        self.add_rows(master, 1, 301, 325, pings)
        self.add_rows(master, 4, 326, 350, pings)
        self.add_rows(master, 7, 351, 375, pings)
        self.add_rows(master, 10, 376, 400, pings)
        self.add_rows(master, 13, 401, 425, pings)
        self.add_rows(master, 16, 426, 450, pings)
        self.add_rows(master, 19, 451, 475, pings)
        self.add_rows(master, 22, 476, 500, pings)
        self.add_rows(master, 25, 501, 511, pings)
        self.in_queue.put(pings)

    def process_incoming(self):
        while self.out_queue.qsize():
            try:
                msg = self.out_queue.get(0)
            except queue.Empty:
                pass

    def add_rows(self, master, column, start, end, collector):
        self.add_header(master, column, 1)
        for i in range(start, end + 1):
            row_num = i - start + 2
            world = Label(master, text=i)
            world.grid(column=column, row=row_num)
            ping = Label(master, text='...')
            ping.grid(column=column + 1, row=row_num)
            collector.append((ping, i))
            breaker = Label(master, text='|')
            breaker.grid(column=column + 2, row=row_num)

    def add_header(self, master, col_start=1, row_start=1):
        hdr_world = Label(master, text="World")
        hdr_world.grid(column=col_start, row=row_start)
        hdr_ping = Label(master, text="Ping")
        hdr_ping.grid(column=col_start + 1, row=row_start)
        breaker = Label(master, text='|')
        breaker.grid(column=col_start + 2, row=row_start)

    def on_refresh(self):
        self.master.update_idletasks()


class Threadsing:

    def __init__(self, master):
        self.master = master
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue()
        self.pool = Pool(8)
        self.ui = PingUI(master, self.in_queue, self.out_queue)
        self.running = 1
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()
        self.check_outbound()

    def check_outbound(self):
        self.ui.process_incoming()
        if not self.running:
            import sys
            sys.exit(1)
        self.master.after(200, self.check_outbound)

    def worker(self):
        while self.running:
            while self.in_queue.qsize() and self.running:
                try:
                    in_msg = self.in_queue.get()

                    def get_pings(msg):
                        if self.running:
                            ele = msg[0]
                            world_num = msg[1]
                            result = os.popen("ping " + f'oldschool{world_num}.runescape.com -n 2')
                            ping = 'N/A'
                            for line in result:
                                ping = line.split('Average = ', 1)[-1]
                            ele.configure(text=ping)
                            self.out_queue.put(ping)

                    self.pool.map(get_pings, in_msg)
                except queue.Empty:
                    pass

    def hard_stop(self):
        self.running = 0
        self.pool.close()
        self.pool.terminate()
        self.master.destroy()


window = Tk()
client = Threadsing(window)
window.protocol("WM_DELETE_WINDOW", client.hard_stop)
window.mainloop()
