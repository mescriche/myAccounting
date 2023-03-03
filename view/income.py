from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency

class IncomeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        self.render()

    def render(self):
        self.text['state'] = 'normal'
        
        self.text.delete('1.0', 'end')
        self.text.insert('end', 'Hola Income\n')
        
        self.text['state'] = 'disabled'
