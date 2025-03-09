__author__ = 'Manuel Escriche'
from collections import namedtuple
from dbase import db_session, Transaction
from controller.report import create_graph, create_table, create_joint_table, get_data
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

Data = namedtuple('Data', ['value', 'label'])
cm = 1/2.54

class BalanceRepoView(ttk.Frame):
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
        self.eyear = IntVar()
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'BALANCE SUMMARY'
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
        
        #self.year_combo.event_generate("<<ComboboxSelected>>")

    def _get_year(self):
        _desc = f'Balance closing seat for year'
        with db_session() as db:
            years = [t.date.year for t in db.query(Transaction).\
                filter(Transaction.description.contains(_desc))]
        min_year,max_year = min(years), max(years)
        self.year_combo['values'] = values = [*range(max_year, min_year-1, -1)]

    
    def _create_balance_summary(self, year):
        adata = get_data('assets', year)
        ldata = get_data('claims', year)
        Data = namedtuple('Data', ['values', 'color'])
        gdata = {
            "Fixed": Data(np.array([adata['fixed'],0]), 'tab:blue'),
            "Current": Data(np.array([adata['current'],0]), 'tab:cyan'),
            "Wealth": Data(np.array([0, ldata['wealth']]), 'tab:purple'),
            "Earnings": Data(np.array([0,ldata['earn']]), 'tab:olive'),
            "Debt": Data(np.array([0, ldata['debt']]), 'tab:red'),
        }
            
        categories = 'Assets', 'Claims'
        total = adata['fixed'] + adata['current']
        
        bottom = np.zeros(2)
        fig, ax = plt.subplots(figsize=(10*cm, 10*cm))
        for key, item in gdata.items():
            p = ax.bar(categories, item.values, label=key, width=0.8,
                       bottom = bottom, color=item.color)
            for index, bar in enumerate(p):
                height = bar.get_height()
                if height == 0: continue
                label = p.get_label()
                t = ax.text(bar.get_x() + bar.get_width()/2,
                            bottom[index]+height/2,
                            f'{label}\n{height:,.0f}€\n({height*100/total:.0f}%)',
                            ha='center', va='center')
                font_size = t.get_size()
            bottom += item.values
        ax.get_yaxis().set_visible(False)
        ax.set_title(f'Total = {total:,.0f}€', fontsize=font_size)
        ax.set_ylim(0, total*1.05)
        fig.suptitle(f'Year {year} - Balance Summary')
        return fig
          
    def display_graph(self, *args):
        plt.close('all')
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        first_year = int(self.year_combo['values'][-1])
        #######
        if year-1 >= first_year:
            fig = self._create_balance_summary(year-1)
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            self.text.window_create('end', window=canvas.get_tk_widget())
        fig = self._create_balance_summary(year)
        canvas = FigureCanvasTkAgg(fig, master=self.text)
        self.text.window_create('end', window=canvas.get_tk_widget())
        self.text.insert('end', "\n\n")
        
        if year-1 >= first_year:
            table = create_joint_table(('Assets','Claims'),(year-1,year))
            self.text.insert('end', table)
            self.text.insert('end', "\n\n")
            
        ##########
        if year-1 >= first_year:
            fig = create_graph('Current', year-1, 'tab:cyan')
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            self.text.window_create('end', window=canvas.get_tk_widget())
        fig = create_graph('Current', year, 'tab:cyan')
        canvas = FigureCanvasTkAgg(fig, master=self.text)
        self.text.window_create('end', window=canvas.get_tk_widget())
        self.text.insert('end', "\n\n")
        
        if year-1 >= first_year:
            table =  create_table('Current', (year-1, year))
            self.text.insert('end', table)
            self.text.insert('end', "\n\n")
            
        #################
        if year-1 >= first_year:
            fig = create_graph('Fixed', year-1, 'tab:blue')
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            self.text.window_create('end', window=canvas.get_tk_widget())
        fig = create_graph('Fixed', year, 'tab:blue')
        canvas = FigureCanvasTkAgg(fig, master=self.text)
        self.text.window_create('end', window=canvas.get_tk_widget())
        self.text.insert('end', "\n\n")
        
        if year-1 >= first_year:
            table = create_table('Fixed', (year-1, year))
            self.text.insert('end', table)
            self.text.insert('end', "\n\n")
        self.text['state'] = 'disabled'
