__author__ = 'Manuel Escriche'
from dbase import db_session, Transaction, Account
from tkinter import *
from tkinter import ttk
from datamodel.reports_data import ReportDataSource
from controller.report import create_table
from prettytable import PrettyTable

delta = "\u0394"

class SummaryRepoView(ttk.Frame):
    def __init__(self, parent, user, acc_tree, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
        self.acc_tree = acc_tree
        self.eyear = IntVar()
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'REPORT SUMMARY'
        ttk.Label(title_frame, text = f"{title}").pack(side='left')
        year_frame = ttk.Frame(title_frame)
        year_frame.pack(side='left')
        ttk.Label(year_frame, text = f"{'YEAR: ':>10}").pack(side='left', ipadx=0, ipady=0)
        self.year_combo = ttk.Combobox(year_frame, state='readonly', width=5, textvariable=self.eyear, postcommand=self._get_year)
        self.year_combo.pack(side='left', ipadx=0, ipady=0)
        self.year_combo.bind('<<ComboboxSelected>>', self.display_table)
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
        self.year_combo['values'] = values = [*range(max_year, min_year-1, -1)]

    def display_table(self, *args):
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        first_year = int(self.year_combo['values'][-1])
        p_year = year-1
        years = p_year, year
        #########
        titles = ('/Assets', '/Claims')
        df = [self.data_source.get_data(title, p_year, year, delta=True) for title in titles]    
        table = create_table(*df, title='BALANCE: ASSETS / CLAIMS')
        self.text.insert('end', table)
        self.text.insert('end','\n')
        ##########
        titles = ('/Assets/Current','/Assets/Fixed')
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df, title='ASSETS: CURRENT / FIXED')
        self.text.insert('end', table)
        self.text.insert('end','\n')
        ##########
        titles = ('/Claims', )
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df, title='CLAIMS')
        self.text.insert('end', table)
        self.text.insert('end','\n')
        ##########
        titles = ('/Input', '/Output')
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df, title='INCOME: INPUTS / OUTPUT')
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        titles = ('/Output/Tax', )
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df, title='TAX')
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        titles = ('/Output/Insurance', )
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df, title='INSURANCE')
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        titles = ('/Output/Expense', )
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]
        table = create_table(*df, title='EXPENSE')
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        titles = sorted([child.ext_name for child in self.acc_tree.find_node('/Output/Expense').children])
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df, title='EXPENSE - Detailed')
        self.text.insert('end',table)
        self.text.insert('end','\n') 
        
        self.text.insert('end', "\n")
        self.text['state'] = 'disabled'
