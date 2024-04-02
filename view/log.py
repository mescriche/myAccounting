__author__ = 'Manuel Escriche'

from tkinter import *
from tkinter import ttk


class LogView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.pack(fill='both', expand=True)
        self.text = Text(self)
        self.text.pack(expand=True, fill='both')
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')
        self.print('Logging window')

    def print(self, msg):
        self.text['state'] = 'normal'
        self.text.insert('end', msg)
        self.text.insert('end', '\n')
        self.text['state'] = 'disabled'
