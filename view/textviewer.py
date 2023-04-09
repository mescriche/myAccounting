__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk

class TextEditor(Text):
    def __init__(self, parent, filename='default.json', **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        scroll_bar = Scrollbar(self)
        self.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.yview)
        scroll_bar.pack(side='right', fill='y')

        #with open(filename) as _file:
        #    self.insert(1.0, _file.read())
            
        
