__author__ = 'Manuel Escriche'
import re
from dbase import db_session, Transaction, Account, BookEntry
from controller.utility import db_get_accounts_gname,  db_get_account_code, db_get_yearRange
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

class EvoView(ttk.Frame):
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
        frame = ttk.LabelFrame(self, text='Account')
        frame.pack(fill='x')

        self.account = StringVar()
        self.acc_combo = ttk.Combobox(frame, state='readonly',
                                      width=26,
                                      textvariable=self.account,
                                      postcommand=self._get_accounts)
        self.acc_combo.pack(side='left', ipadx=2, ipady=2)
        self.acc_combo.bind('<<ComboboxSelected>>', self.display_graph)
        self._get_accounts()
        try:
            self.acc_combo.current(0)
        except:
            pass

        self.text = Text(self)
        scroll_bar = Scrollbar(self.text, command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')
        self.text.configure(yscrollcommand=scroll_bar.set)      
        self.text.pack(side='left', fill='both', expand=True)
        
        #self.acc_combo.event_generate("<<ComboboxSelected>>")
        
    def _get_accounts(self):
        self.acc_combo['values'] = db_get_accounts_gname(False)

    def _get_data(self, gname) -> dict:
        code = db_get_account_code(gname)
        match = re.search(r'[6,7]0', code)
        seed = code[0] if match else code
        data = dict()
        _description = "closing seat for year"
        min_year,max_year = db_get_yearRange()
        years = [*range(min_year, max_year)]
        with db_session() as db:
            codes = [x.code for x in  db.query(Account).
                     where(Account.code.startswith(seed))]
            entries = db.query(BookEntry).\
                join(Transaction).\
                where(Transaction.description.contains(_description)).\
                join(Account).where(Account.code.in_(codes))
       
            data = [[entry.transaction.date.year, entry.amount]
                    for entry in entries]
            #print(data)
            amounts = list()
            for year in years:
                items = [item[1] for item in data if item[0] == year]
                amount = 0 if not items else sum(items)
                amounts.append(round(amount,2))
        return dict(year=years, amount=amounts)
    
    def display_graph(self, *args):
        plt.close('all')
        self.text['state'] = 'normal'
        self.text.delete(1.0, 'end')
        cm = 1/2.54
        if account_gname := self.account.get():
            data = self._get_data(account_gname)
            amounts = np.array(data['amount'])
            #years = np.array(data['year'])
            fig, ax = plt.subplots(figsize=(27*cm, 10*cm), layout='constrained')
            category = [str(year) for year in data['year']]
            bar = ax.bar(category, amounts)
            ax.set_title(f"{account_gname}")
            ax.set_xlabel("Year")
            ax.set_ylabel("Amount(€)")
            labels = [f'{x:,.0f}' for x in amounts]
            ax.bar_label(bar, labels=labels)

            # Integrar el gráfico en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.text)
            canvas_widget = canvas.get_tk_widget()
            self.text.window_create('end', window=canvas_widget)
            self.text.insert('end', "\n\n")
