from tkinter import *
from tkinter import ttk
from datetime import datetime
from dbase import db_session, db_currency, db_get_account_code, db_get_accounts_gname, db_get_yearRange
from dbase import Account, Transaction, BookEntry
from locale import currency

class LedgerView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.acc_gnames = db_get_accounts_gname()
        self.accounts = StringVar(value=self.acc_gnames)
        self.acc_lbox = Listbox(self, listvariable=self.accounts, width=26, exportselection=False)
        self.acc_lbox.pack(side='left', fill='y', expand=False)
        self.acc_lbox.bind('<<ListboxSelect>>', self.render_account)

        self.filter = LabelFrame(self, text='Filter')
        self.filter.pack(fill='x', expand=False)
        
        self.etrans_year = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Year:').pack(side='left', ipadx=2, ipady=2)
        year_combo = ttk.Combobox(frame, state='readonly', width=5, textvariable=self.etrans_year)
        year_combo.pack(ipadx=2, ipady=2)
        min_year,max_year = db_get_yearRange()
        values = [''] + [*range(max_year, min_year-1, -1)]
        year_combo['values'] = values
        year_combo.bind('<<ComboboxSelected>>', self.render_account)

        self.etrans_date = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Date:').pack(side='left', ipadx=2, ipady=2)
        date_entry = ttk.Entry(frame, textvariable=self.etrans_date, width=10)
        date_entry.pack(ipadx=2, ipady=2)
        date_entry.bind('<Return>', self.render_account)
        
        self.etrans_description = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Description:').pack(side='left', ipadx=2, ipady=2)
        desc_entry = ttk.Entry(frame, textvariable=self.etrans_description, width=30)
        desc_entry.pack(ipadx=2, ipady=2)
        desc_entry.bind('<Return>', self.render_account)

        ttk.Button(self.filter, text='Filter', command=self.render_account).pack(side='left', padx=5)
        ttk.Button(self.filter, text='Clear', command=self.clear_filter).pack(side='right', padx=5)
        
        vframe = ttk.Frame(self)
        vframe.pack(fill='both', expand=True)
        
        self.account_label = StringVar()
        label = Label(vframe, textvariable=self.account_label, width=126, anchor='w', background='blue')
        label.pack(fill='x', expand=False)

        
        columns = ('eid', 'tid', 'date', 'amount', 'description')
        data = dict()
        data['eid'] = {'text':'Eid', 'width':40, 'anchor':'c'}
        data['tid'] = {'text':'Tid', 'width':40, 'anchor':'c'}
        data['date'] = {'text':'Date', 'width':100, 'anchor':'c'}
        data['amount'] = {'text':'Amount', 'width':80, 'anchor':'e'}
        data['description'] = {'text':'Description', 'width':800, 'anchor':'w'}
        
        self.table = ttk.Treeview(vframe, columns=columns, show='headings')
        self.table.pack(fill='both', expand=True)

        for topic in columns:
            self.table.heading(topic, text=data[topic]['text'])
            self.table.column(topic, width=data[topic]['width'], anchor=data[topic]['anchor'])
            
        self.acc_lbox.select_set(0)
        self.acc_lbox.event_generate("<<ListboxSelect>>")

    def clear_filter(self, *args):
        self.etrans_description.set('')
        self.etrans_year.set('')
        self.etrans_date.set('')

    def render_account(self, *args):
        idx = self.acc_lbox.curselection()[0]
        gname = self.acc_gnames[idx]
        code = db_get_account_code(gname)
        with db_session() as db:
            account = db.query(Account).filter_by(code=code).one()
            entries = account.entries
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
                self.render_entries(gname, items)
            else:
                self.table.delete(*self.table.get_children())

    def render_entries(self, name, items:list):
        self.account_label.set(f'{name}')
        self.table.delete(*self.table.get_children())
        with db_session() as db:
            for _id in reversed(items):
                try: entry = db.query(BookEntry).get(_id)
                except Exception as e:
                    print(e)
                else:
                    values = entry.id, entry.transaction.id, entry.transaction.date.strftime("%d-%m-%Y"),\
                        db_currency(entry.amount), entry.transaction.description
                    self.table.insert('','end', values=values)
        
