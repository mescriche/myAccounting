__author__ = 'Manuel Escriche'
from collections import namedtuple
import re
from dbase import db_session, Transaction
from controller import create_graph, create_table,  create_cmp_graph
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from datamodel import ReportDataSource

Data = namedtuple('Data', ['value', 'label'])
cm = 1/2.54
class IncomeRepoView(ttk.Frame):
    def __init__(self, parent, user, acc_tree,  **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
        self.acc_tree = acc_tree
        self.eyear = IntVar()
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'INCOME SUMMARY'
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
                          
    def _create_income_summary(self, year):
        dfi = self.data_source.get_data('/Input', year)
        dfo = self.data_source.get_data('/Output', year)
        fig, ax = plt.subplots(figsize=(10*cm, 8*cm))
        Data = namedtuple('Data', ['values', 'color'])

        earnings = dfi.loc['Total',year]-dfo.loc['Total',year]
        gdata = {
            'Revenue': Data(np.append(dfi.loc['Total'].to_numpy(), [0]), 'tab:blue'),
            'Outgoing': Data(np.append([0], dfo.loc['Total'].to_numpy()), 'tab:red'),
            'Earnings':Data(np.array([0, earnings]), 'tab:green')
        }
        
        categories = 'Input', 'Output'
        total = dfi.loc['Total',year]
        
        bottom = np.zeros(2)
        for key, item in gdata.items():
            p = ax.bar(categories, item.values, label=key, width=0.8,
                       bottom=bottom, color=item.color)
            for index, bar in enumerate(p):
                height = bar.get_height()
                if height == 0: continue
                label = p.get_label()
                t = ax.text(bar.get_x() + bar.get_width()/2,
                            bottom[index]+height/2,
                            f'{label}\n{height:,.0f}€\n({height*100/total:.0f}%)',
                            ha='center', va='center')
            bottom +=item[0]
            
        fig.suptitle(f'Year {year} - Income Summary')
        ax.get_yaxis().set_visible(False)
        ax.set_title(f'Total = {total:,.0f}€', fontsize=10)
        ax.set_ylim(0, total*1.1)
        plt.subplots_adjust(top=0.85)
        return fig

    def display_graph(self, *args):
        plt.close('all')
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        years = year-1, year
        ########

        titles = ('/Input','/Output')
        df = [self.data_source.get_data(title, *years, delta=True ) for title in titles]    
        table = create_table(*df, title='INCOME SUMMARY')
        self.text.insert('end', table)
        self.text.insert('end', "\n\n")
        
        for year in years:
            fig = self._create_income_summary(year)
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            self.text.window_create('end', window=canvas.get_tk_widget())
        else:
            self.text.insert('end', "\n\n")

        ###########
        titles=('/Input/Revenue','tab:blue'),('/Output', ('sienna', 'salmon', 'red'))

        for title,color in titles:
            df = self.data_source.get_data(title, *years, delta=True, verbose=False)
            table =  create_table(df, title = title)
            self.text.insert('end', table)
            self.text.insert('end', "\n\n")
            
            if fig:= create_cmp_graph(df, title=title, color=color):
                canvas = FigureCanvasTkAgg(fig, master=self.text)
                self.text.window_create('end', window=canvas.get_tk_widget())
                self.text.insert('end', "\n\n")
            
        self.text['state'] = 'disabled'

