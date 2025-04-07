__author__ = 'Manuel Escriche'
from collections import namedtuple
from dbase import db_session, Transaction
from controller.report import create_graph, create_table, create_cmp_graph
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from datamodel import ReportDataSource

Data = namedtuple('Data', ['value', 'label'])
cm = 1/2.54
class TaxRepoView(ttk.Frame):
    def __init__(self, parent, user, acc_tree, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
        self.acc_tree = acc_tree
        self.eyear = IntVar()
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'TAX SUMMARY'
        ttk.Label(title_frame, text = f"{title}").pack(side='left')
        year_frame = ttk.Frame(title_frame)
        year_frame.pack(side='left')
        ttk.Label(year_frame, text = f"{'YEAR: ':>10}").pack(side='left', ipadx=0, ipady=0)
        self.year_combo = ttk.Combobox(year_frame, state='readonly', width=5, textvariable=self.eyear, postcommand=self._get_year)
        self.year_combo.pack(side='left', ipadx=0, ipady=0)
        self.year_combo.bind('<<ComboboxSelected>>', self.display_graph)
        self._get_year()
        try:
            self.year_combo.current(0)
        except:
            pass
        self.data_source = ReportDataSource(self.acc_tree)
        
        self.text = Text(self)
        scroll_bar = Scrollbar(self.text, command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')
        self.text.configure(yscrollcommand=scroll_bar.set)      
        self.text.pack(side='left', fill='both', expand=True)
        
    def _get_year(self):
        _desc = f'Income closing seat for year'
        with db_session() as db:
            years = [t.date.year for t in db.query(Transaction).\
                filter(Transaction.description.contains(_desc))]
        min_year,max_year = min(years), max(years)
        self.year_combo['values'] = values = [*range(max_year, min_year, -1)]
    
    def display_graph(self, *args):
        plt.close('all')
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        years = year-1, year
        title = '/Output/Tax'
        
        df = self.data_source.get_data(title, *years, delta=True)
        table =  create_table(df, title=title)
        self.text.insert('end', table)
        self.text.insert('end', "\n\n")

        if fig:= create_cmp_graph(df, title=title):
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            self.text.window_create('end', window=canvas.get_tk_widget())
            self.text.insert('end', "\n\n")
        
        self.text['state'] = 'disabled'

