__author__ = 'Manuel Escriche'
import re
from tkinter import *
from tkinter import ttk
from datetime import datetime
from dbase import db_session
from controller.utility import db_currency, db_get_account_code, db_get_account_name, db_get_yearRange
from dbase import Account, Transaction, BookEntry
import locale

class LedgerView(ttk.Frame):
    def __init__(self, parent, acc_tree):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill='both', expand=True)

        self.acc_tree = acc_tree
        
        self.filter = ttk.LabelFrame(self, text='Filter')
        self.filter.pack(fill='x', expand=False)
        
        self.account = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=3)
        ttk.Label(frame, text='Account:').pack(side='left', ipadx=2, ipady=2)
        self.acc_combo = ttk.Combobox(frame, state='readonly', width=26, textvariable=self.account, postcommand=self._get_accounts)
        self.acc_combo.pack(ipadx=2, ipady=2)
        self.acc_combo.bind('<<ComboboxSelected>>', self.render_filter)
        self._get_accounts()
        try: 
            self.acc_combo.current(0)
        except:
            pass
        
        self.etrans_year = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=3)
        ttk.Label(frame, text='Year:').pack(side='left', ipadx=2, ipady=2)
        self.year_combo = ttk.Combobox(frame, state='readonly', width=5, textvariable=self.etrans_year, postcommand=self._get_years)
        self.year_combo.pack(ipadx=2, ipady=2)
        self.year_combo.bind('<<ComboboxSelected>>', self.render_filter)
        self._get_years()
        self.year_combo.current(0)

        self.etrans_date = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=3)
        ttk.Label(frame, text='Date:').pack(side='left', ipadx=2, ipady=2)
        date_entry = ttk.Entry(frame, textvariable=self.etrans_date, width=10)
        date_entry.pack(ipadx=2, ipady=2)
        date_entry.bind('<Return>', self.render_filter)
        
        self.etrans_description = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=3)
        ttk.Label(frame, text='Description:').pack(side='left', ipadx=2, ipady=2)
        desc_entry = ttk.Entry(frame, textvariable=self.etrans_description, width=30)
        desc_entry.pack(ipadx=2, ipady=2)
        desc_entry.bind('<Return>', self.render_filter)

        ttk.Button(self.filter, text='Filter', command=self.render_filter).pack(side='left', padx=5)
        ttk.Button(self.filter, text='Clear', command=self.clear_filter).pack(side='right', padx=5)
        
        vframe = ttk.Frame(self)
        vframe.pack(fill='both', expand=True)
        
        self.account_label = StringVar()
        label = Label(vframe, textvariable=self.account_label, width=126, anchor='w', background='blue')
        label.pack(fill='x', expand=False)

        
        columns = ('eid', 'tid', 'account', 'date', 'amount', 'description')
        
        self.table = ttk.Treeview(vframe, columns=columns, selectmode='browse', show='headings')
        self.table.pack(fill='both', expand=True)
        self.table.heading('eid', text='Eid', command=lambda:self._sort_column('eid'))
        self.table.heading('tid', text='Tid', command=lambda:self._sort_column('tid'))
        self.table.heading('account', text='Account', command=lambda:self._sort_column('account'))
        self.table.heading('date', text='Date', command=lambda:self._sort_column('date'))
        self.table.heading('amount', text='Amount', command=lambda:self._sort_column('amount'))
        self.table.heading('description', text='Description', command=lambda:self._sort_column('description'))
        self.table.column('eid', width=40, anchor='c')
        self.table.column('tid', width=40, anchor='c')
        self.table.column('account', width=180, anchor='w')
        self.table.column('date', width=100, anchor='c')
        self.table.column('amount', width=80, anchor='e')
        self.table.column('description', width=800, anchor='w')        
        self.table.bind('<<TreeviewSelect>>', self.display_transaction)
        
        self.render_filter()
        
    def _sort_column(self, col, reverse=False):
        if col in ('description','account'): key = lambda x: str(x[0])
        elif col in ( 'eid', 'tid') : key = lambda x: int(x[0])
        elif col == 'date':   key = lambda x: datetime.strptime(x[0], "%d-%m-%Y").date()
        elif col == 'amount': key = lambda x: locale.atof(x[0].replace('.','').replace(',','.'))
        else: return
        
        l = [(self.table.set(iid, col), iid) for iid in self.table.get_children()]
        l.sort(key=key, reverse=reverse)
        for ndx, (val, iid) in enumerate(l):
            self.table.move(iid, '', ndx)
        else:
            self.table.heading(col, command=lambda: self._sort_column(col, not reverse))
            
    def _get_accounts(self):
        self.acc_combo['values'] = self.acc_tree.get_nodes()
        
    def _get_years(self):
        min_year,max_year = db_get_yearRange()
        self.year_combo['values'] = [*range(max_year, min_year-1, -1)] + ['']
        
    def refresh(self, date):
        self.etrans_year.set(date.year)
        #self.render_filter()
        
    def display_transaction(self, event):
        if iid := event.widget.focus():
            trans_id = self.table.set(iid, column='tid')
            self.parent.master.journal.render([trans_id])
            self.parent.master.notebook.select(1)
        return 'break'
            
    def clear_filter(self, *args):
        self.etrans_description.set('')
        self.etrans_date.set('')

    def render_filter(self, *args):
        if acc_value := self.account.get():
            node = self.acc_tree.find_node(acc_value)
            node_proxy = node.proxy()
            codes = self.acc_tree.get_account_codes(node_proxy)            
            with db_session() as db:
                accounts = db.query(Account).filter(Account.code.in_(codes)).all()
                #accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), codes)
                entries = [entry for account in accounts for entry in account.entries]
                if self.etrans_description.get():
                    description = self.etrans_description.get()
                    entries = filter(lambda x: description in x.transaction.description, entries)
                if self.etrans_year.get():
                    year = self.etrans_year.get()
                    min_date = datetime.strptime(f'01-01-{year}', "%d-%m-%Y").date()
                    max_date = datetime.strptime(f'31-12-{year}', "%d-%m-%Y").date()
                    entries = filter(lambda x: x.transaction.date >= min_date and x.transaction.date <= max_date, entries)
                if self.etrans_date.get():
                    _date = self.etrans_date.get()
                    date = datetime.strptime(_date, "%d-%m-%Y").date()
                    entries = filter(lambda x:x.transaction.date == date, entries)
                if items := [item.id for item in entries]:
                    self.render_entries(acc_value, items)
                else:
                    self.account_label.set(f'{acc_value}')
                    self.table.delete(*self.table.get_children())
                    

    def render_entries(self, title:str, items:list):
        self.account_label.set(f'{title}')
        self.table.delete(*self.table.get_children())
        with db_session() as db:
            total = 0
            for _id in reversed(items):
                try: entry = db.query(BookEntry).get(_id)
                except Exception as e:
                    print(e)
                else:
                    total += entry.value
                    values = entry.id, entry.transaction.id, entry.account.gname, entry.transaction.date.strftime("%d-%m-%Y"),\
                        db_currency(entry.value), entry.transaction.description
                    self.table.insert('','end', values=values)
            else:
                total = db_currency(total)
                self.account_label.set(f'{title} : {total}')
