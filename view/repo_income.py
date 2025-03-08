__author__ = 'Manuel Escriche'
from collections import namedtuple
import re
from dbase import db_session, Transaction
from controller.report import create_graph, create_table, create_joint_table, get_data
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

Data = namedtuple('Data', ['value', 'label'])
cm = 1/2.54
class IncomeRepoView(ttk.Frame):
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
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
                          
    def _create_income_summary(self, year):
        idata = get_data('input', year)
        odata = get_data('output', year)
        fig, ax = plt.subplots(figsize=(10*cm, 10*cm))
        Data = namedtuple('Data', ['values', 'color'])
        gdata = {
            'Revenue': Data(np.array([idata['rev'], 0]), 'tab:blue'),
            'Outgoing': Data(np.array([0, odata['out']]), 'tab:red'),
            'Earnings':Data(np.array([0, odata['earn']]), 'tab:green')
        }
        categories = 'Input', 'Output'
        total = idata['rev']
        
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
                font_size = t.get_size()
            bottom +=item[0]
        ax.get_yaxis().set_visible(False)
        ax.set_ylim(0, total*1.05)
        fig.suptitle(f'Year {year} - Income Summary')
        return fig

    def display_graph(self, *args):
        plt.close('all')
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        first_year = int(self.year_combo['values'][-1])
        ########
        if year-1 >= first_year:
            fig = self._create_income_summary(year-1)
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            self.text.window_create('end', window=canvas.get_tk_widget())
        fig = self._create_income_summary(year)
        canvas = FigureCanvasTkAgg(fig, master=self.text)
        self.text.window_create('end', window=canvas.get_tk_widget())
        self.text.insert('end', "\n\n")
        if year-1 >= first_year:
            table = create_joint_table(('Input','Output'),(year-1,year))
            self.text.insert('end', table)
            self.text.insert('end', "\n\n")
        ###########
        if year-1 >=  first_year:
            fig = create_graph('Revenue', year-1, 'tab:blue')
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            self.text.window_create('end', window=canvas.get_tk_widget())
        fig = create_graph('Revenue', year, 'tab:blue')
        canvas = FigureCanvasTkAgg(fig, master=self.text)
        self.text.window_create('end', window=canvas.get_tk_widget())
        self.text.insert('end', "\n\n")

        if year-1 >= first_year:
            table =  create_table('Revenue', (year-1, year))
            self.text.insert('end', table)
            self.text.insert('end', "\n\n")
        
        ###########
        if year-1 >=  first_year:
            fig = create_graph('Outgoing', year-1, ('sienna', 'salmon', 'red'))
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            self.text.window_create('end', window=canvas.get_tk_widget())
        fig = create_graph('Outgoing', year, ('sienna', 'salmon', 'red'))
        canvas = FigureCanvasTkAgg(fig, master=self.text)
        self.text.window_create('end', window=canvas.get_tk_widget())
        self.text.insert('end', "\n\n")
        
        if year-1 >= first_year:
            table = create_table('Outgoing', (year-1, year))
            self.text.insert('end', table)
        self.text.insert('end', "\n\n")
        self.text['state'] = 'disabled'

