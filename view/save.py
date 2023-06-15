from tkinter import *
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog
from dbase import  db_get_yearRange

class SaveYearSeatsDialog(Dialog):
    def __init__(self, parent, title):
        self.answer = False
        self.year = IntVar()
        super().__init__(parent, title)

    def body(self, master):
        year_frame = ttk.Frame(master)
        year_frame.pack(side='left', padx=10, pady=10)
        ttk.Label(year_frame, text = f"{'YEAR: ':>10}").pack(side='left', ipadx=0, ipady=0)
        year_combo = ttk.Combobox(year_frame, state='readonly', width=5, textvariable=self.year)
        year_combo.pack(side='left', ipadx=0, ipady=0)
        min_year,max_year = db_get_yearRange()
        year_combo['values'] = values = [*range(max_year, min_year-1, -1)]        
        year_combo.current(0)
        return year_combo
    
    def buttonbox(self):
        control_bar = ttk.Frame(self)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Cancel", width=10, command=self.cancel).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Save", width=10, command=self.ok, default=ACTIVE).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        control_bar.pack(fill='x')

    def apply(self):
        self.answer = True

    def validate(self):
        return True

def askSaveYearToFileDialog(master):
    w = SaveYearSeatsDialog(master, 'Save year seats to file')
    return w.answer, w.year.get()
