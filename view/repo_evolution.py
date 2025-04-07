__author__ = 'Manuel Escriche'
import re,random
from dbase import db_session, Transaction, Account, BookEntry
from controller.utility import db_get_accounts_gname,  db_get_account_code, db_get_account_name, db_get_yearRange
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from datamodel import ReportDataSource
from controller.report import create_table, create_evo_graph, create_mevo_graph
from controller.utility import db_get_account_name, db_get_account_code

class EvoView(ttk.Frame):
    def __init__(self, parent, user, acc_tree, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
        self.acc_tree = acc_tree
        self.data_source = ReportDataSource(self.acc_tree)
        
        fframe = ttk.Frame(self)
        fframe.pack(fill='x')
        
        frame = ttk.LabelFrame(fframe, text='Accounts')
        frame.pack(side='left', fill='x')
        self.account = StringVar()
        self.acc_combo = ttk.Combobox(frame, state='readonly', width=26,
                                      textvariable=self.account,
                                      postcommand=self._get_accounts)
        self.acc_combo.pack(side='left', ipadx=2, ipady=2)
        self.acc_combo.bind('<<ComboboxSelected>>', self.display_node)
        
        self._get_accounts()
        self.acc_combo.current(0)
        
        self.text = Text(self)
        scroll_bar = Scrollbar(self.text, command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')
        self.text.configure(yscrollcommand=scroll_bar.set)      
        self.text.pack(side='left', fill='both', expand=True)
        
        #self.acc_combo.event_generate("<<ComboboxSelected>>")
         
    def _get_accounts(self):
        self.acc_combo['values'] = self.data_source.get_nodes()

    def display_node(self, event):
        selected_value = event.widget.get()
        if node := self.data_source.acc_tree.find_node(selected_value):
            self.display_graph(selected_value)
         
    def display_graph(self, name):
        plt.close('all')
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        cm = 1/2.54
        min_year,max_year = db_get_yearRange()
        min_year = max(min_year+1, max_year-10)
        years = [*range(min_year, max_year)]

        df = self.data_source.get_data(name, *years, total=True, verbose=False)
        table = create_table(df, title=name)
        self.text.insert('end', table)
        self.text.insert('end', "\n\n")

        if fig := create_evo_graph(df.loc['Total'], title=f'{name} - Total'):
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            canvas_widget = canvas.get_tk_widget()
            self.text.window_create('end', window=canvas_widget)
            self.text.insert('end', "\n\n")
            
        df = df.drop(index='Total')
        if len(df) == 1: return
        if fig := create_mevo_graph(df, title=f'{name} - Detailed'):
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            canvas_widget = canvas.get_tk_widget()
            self.text.window_create('end', window=canvas_widget)
            self.text.insert('end', "\n\n")

        self.text['state'] = 'disabled'

