__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog
from controller.utility import  db_get_yearRange

class SaveSeatsDialog(Dialog):
    def __init__(self, parent, title):
        self.answer = False
        self.min_year, self.max_year = db_get_yearRange()
        self.years = [*range(self.min_year, self.max_year+1)]
        self.year = IntVar()
        self.all_years = BooleanVar()
        super().__init__(parent, title)

    def body(self, master):
        _frame = ttk.Frame(master)
        _combo_frame = ttk.Frame(_frame)
        _combo_frame.pack(expand=True, fill='x')
        ttk.Label(_combo_frame, text=f"Select Year:").pack(side='left', ipadx=0, ipady=0)

        self.year_combo = ttk.Combobox(_combo_frame, state='readonly', width=5, text='Year:', textvariable=self.year)
        self.year_combo.pack(fill='x', ipadx=0, ipady=0, padx=10, pady=10)
        self.year_combo['values'] = values = [*range(self.max_year, self.min_year-1, -1)]
        self.year_combo.current(0)
        self.year_combo.bind('<<ComboboxSelected>>', lambda e: self.all_years.set(False))

        ttk.Separator(_frame, orient='horizontal').pack(expand=True, fill='x')
        
        check_button = ttk.Checkbutton(_frame, text=f"All {len(self.years)} Years: from {self.years[0]} to {self.years[-1]}",
                                       onvalue=True, offvalue=False,
                                       variable=self.all_years, command=self.combo_handler)
        check_button.pack(expand=True, fill='x', ipadx=0, ipady=0, padx=10, pady=10)
        self.all_years.set(False)
        
        _frame.pack(fill='x')
        return self.year_combo
    
    def combo_handler(self, event=None):
        if self.all_years.get():
            self.year_combo.state(['disabled',])
        else:
            self.year_combo.state(['!disabled','selected'])


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
        self.output = self.years if self.all_years.get() else [self.year.get(),]
        
    def validate(self):
        return True

def askSaveDBToFileDialog(master):
    w = SaveSeatsDialog(master, "Save years' seats to file")
    return w.answer, w.output
