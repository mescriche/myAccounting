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

    def title(self,name):
        return f"\n+{'-':-^58}+\n|{name: ^58}|\n"
    
    def section(self, name):
        return f"\n+{'=':=^58}+\n|{name: ^58}|\n+{'=':=^58}+\n"
    
    def display_table(self, *args):
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        first_year = int(self.year_combo['values'][-1])
        p_year = year-1
        years = p_year, year
        #########
        self.text.insert('end' ,self.section('BALANCE: ASSETS / CLAIMS'))
        titles = ('Assets', 'Claims')
        df = [self.data_source.get_data(title, p_year, year, delta=True) for title in titles]    
        table = create_table(*df)
        self.text.insert('end', table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.title('ASSETS: CURRENT / FIXED ') )
        titles = ('Current','Fixed')
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df)
        self.text.insert('end', table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.title('CLAIMS') )
        #titles = ('debt','earnings', 'wealth')
        titles = ('claims', )
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df)
        self.text.insert('end', table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.section('INCOME: INPUTS / OUTPUT'))
        titles = ('Input', 'Output')
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.title('TAX'))
        titles = ('Tax', )
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end',self.title('INSURANCE'))
        titles = ('Insurance', )
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end',self.title('EXPENSE'))
        titles = ('Expense', )
        df = self.data_source.get_data('Expense', *years, delta=True)    
        table = create_table(df)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end',self.title('EXPENSE - Detailed'))
        titles = ('Expense','Exp-Person','Exp-House','Exp-Vehicle','Exp-Services' )
        df = [self.data_source.get_data(title, *years, delta=True) for title in titles]    
        table = create_table(*df)
        self.text.insert('end',table)
        self.text.insert('end','\n') 
        
        self.text.insert('end', "\n")
        self.text['state'] = 'disabled'
