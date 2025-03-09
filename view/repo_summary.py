__author__ = 'Manuel Escriche'
from collections import namedtuple
from dbase import db_session, Transaction
from controller.report import get__data
from datamodel.seeds import seed
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
from prettytable import PrettyTable
delta = "\u0394"
class SummaryRepoView(ttk.Frame):
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
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

    def _update_DF(self, df, data):
        out = {(k,y):data[y][k] for y in data for k in data[y]}
        concept_keys = set([k for k,y in out.keys()])
        for key in concept_keys:
            row = {'Concept':seed[key].name} | {y:data[y][key] for y in data }
            df = pd.concat([df,  pd.DataFrame(row, index=[0])], ignore_index=True)
        return df

    def create_table(self, titles:tuple, years:tuple):
        assert(len(years) == 2)
        p_year, year = years
        table = PrettyTable()
        table.min_table_width = 60

        for title in titles:
            df = pd.DataFrame()
            data = get__data(title, years)
            df = self._update_DF(df, data)
            df[delta] = df[year] - df[p_year]
            df.sort_values(by=year, inplace=True)
            table.field_names = df.columns.tolist()
            #
            for row in df.itertuples(index=False):
                table.add_row(row)
            else:
                table.add_divider()
                if len(df)>1:
                    table.add_row(['Total', df[p_year].sum(),
                                   df[year].sum(), df[delta].sum()])
                table.add_divider()
        else:
            table.align = 'r'
            table.align["Concept"] = 'l'
            table.custom_format[str(year)] = lambda f,v: f"{v:,.0f}"
            table.custom_format[f"{p_year}"] = lambda f,v: f"{v:,.0f}"
            table.custom_format[delta] = lambda f,v: f"{v:,.0f}"
        return table
    
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
        self.text.insert('end' ,self.section('BALANCE SUMMARY'))
        titles = ('Assets', 'Claims')
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n') 
        ##########
        self.text.insert('end', self.title('ASSETS') )
        titles = ('Current','Fixed')
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.title('CLAIMS') )
        #titles = ('debt','earnings', 'wealth')
        titles = ('claims', )
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.section('INCOME SUMMARY'))
        titles = ('Input', 'Output')
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.title('REVENUE'))
        titles = ('Revenue', )
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.title('OUTGOING'))
        titles = ('Outgoing', )
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end', self.title('TAX'))
        titles = ('Tax', )
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n\n')
        ##########
        self.text.insert('end',self.title('INSURANCE'))
        titles = ('Insurance', )
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n')
        ##########
        self.text.insert('end',self.title('EXPENSE'))
        titles = ('Expense', )
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n\n')
        ##########
        self.text.insert('end',self.title('EXPENSE - Detailed'))
        titles = ('Persons','House','Vehicle','Services' )
        table = self.create_table(titles, years)
        self.text.insert('end',table)
        self.text.insert('end','\n') 
        
        self.text.insert('end', "\n")
        self.text['state'] = 'disabled'
