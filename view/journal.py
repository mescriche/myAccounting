__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account, Transaction
from dbase import db_get_yearRange, db_get_accounts_gname, db_get_account_code
from .transaction import TransactionViewer, TransactionEditor, DMTransaction
from datetime import datetime

class JournalView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        
        self.filter = ttk.LabelFrame(self, text='Filter')
        self.filter.pack(fill='x', expand=False)
        
        self.etrans_id = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Trans Id:').pack(side='left', ipadx=2, ipady=2)
        id_entry = ttk.Entry(frame, textvariable=self.etrans_id, width=7)
        id_entry.pack(ipadx=2, ipady=2)
        id_entry.bind('<Return>', self.render_request)

        self.etrans_year = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Year:').pack(side='left', ipadx=2, ipady=2)
        self.year_combo = ttk.Combobox(frame, state='readonly', width=5, textvariable=self.etrans_year)
        self.year_combo.pack(ipadx=2, ipady=2)
        min_year,max_year = db_get_yearRange()
        self.year_combo['values'] = [*range(max_year, min_year-1, -1)] + ['']
        self.year_combo.bind('<<ComboboxSelected>>', self.render_request)
        self.year_combo.current(0)

        self.etrans_date = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Date:').pack(side='left', ipadx=2, ipady=2)
        date_entry = ttk.Entry(frame, textvariable=self.etrans_date, width=10)
        date_entry.pack(ipadx=2, ipady=2)
        date_entry.bind('<Return>', self.render_request)
        
        self.etrans_description = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Description:').pack(side='left', ipadx=2, ipady=2)
        desc_entry = ttk.Entry(frame, textvariable=self.etrans_description, width=30)
        desc_entry.pack(ipadx=2, ipady=2)
        desc_entry.bind('<Return>', self.render_request)

        ttk.Button(self.filter, text='Filter', command=self.render_request).pack(side='left', padx=20,pady=2)
        ttk.Button(self.filter, text='Clear', command=self.clear_filter).pack(padx=0, pady=2)
            
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')
        self.text.tag_configure('transaction', background='blue', foreground='yellow', justify='left')
        self.text.tag_configure('account', background='blue')
        self.render_request()

    
    def refresh(self, date):
        min_year,max_year = db_get_yearRange()
        self.year_combo['values'] = [*range(max_year, min_year-1, -1)] + ['']
        self.etrans_year.set(date.year)
        self.etrans_date.set(date.strftime('%d-%m-%Y'))
        self.render_request()
            
    def clear_filter(self, *args):
        self.etrans_id.set('')
        self.etrans_description.set('')
        #self.etrans_year.set('')
        self.etrans_date.set('')
        
    def render_request(self, *args):
        with db_session() as db:
            query = db.query(Transaction)
            if self.etrans_id.get():
                _id = self.etrans_id.get()
                query = query.filter(Transaction.id == _id)
            if self.etrans_description.get():
                description = self.etrans_description.get()
                query = query.filter(Transaction.description.contains(description))
            if self.etrans_year.get():
                year = self.etrans_year.get()
                min_date = datetime.strptime(f'01-01-{year}', "%d-%m-%Y").date()
                max_date = datetime.strptime(f'31-12-{year}', "%d-%m-%Y").date()
                query = query.filter(Transaction.date >= min_date).filter(Transaction.date <= max_date)    
            if self.etrans_date.get():
                _date = self.etrans_date.get()
                date = datetime.strptime(_date, "%d-%m-%Y").date()
                query = query.filter(Transaction.date == date)
            if items := [item.id for item in query]:
                self.render(items)
            else:
                self.text['state'] = 'normal'
                self.text.delete('1.0', 'end')
                msg = f'{"No Items Found": ^180}'
                label = Label(self.text, text=msg, background='dark red')
                self.text.window_create('end', window=label)
                self.text['state'] = 'disabled'
            
    def render(self, trans:list=None):
        self.text['state'] = 'normal'
        self.text.delete('1.0', 'end')
        if trans is None:
        ## list of last 20 transactions
            with db_session() as db:
                query = db.query(Transaction).order_by(Transaction.id.desc()).limit(20)
                if items := [item.id for item in query]:
                    items.reverse()
                    trans = items
        ## display list of items id's
        
        with db_session() as db:
            #print(trans)
            for _id in reversed(trans):
                try: db_trans = db.query(Transaction).get(_id)
                except Exception as e:
                    print(e)
                else:
                    dm_trans = DMTransaction.from_DBTransaction(db_trans)
                    wdgt = TransactionViewer(self.text, dm_trans, borderwidth=2)
                    for child in wdgt.winfo_children():
                        child.bindtags((dm_trans.id,) + child.bindtags())
                    else:
                        wdgt.bindtags((dm_trans.id,) + self.bindtags())
                    self.text.window_create('end', window=wdgt)
                    self._create_popup_menu(wdgt, dm_trans)
        self.text['state'] = 'disabled'

    def _create_popup_menu(self, widget, value):
        menu = Menu(widget)
        menu.add_command(label='Remove Transaction', command= lambda e=value.id: self.remove_transaction(e))
        menu.add_command(label='Edit Transaction', command=lambda e=value: self._get_updated_transaction(e))
        if self.text.tk.call('tk', 'windowingsystem') == 'aqua':
            widget.bind_class(value.id, '<2>',         lambda e: menu.post(e.x_root, e.y_root))
            widget.bind_class(value.id, '<Control-1>', lambda e: menu.post(e.x_root, e.y_root))
        else:
            widget.bind_class(value.id, '<3>', lambda e: menu.post(e.x_root, e.y_root))
        return 'break'

    def _get_updated_transaction(self, trans:DMTransaction):
        editor = TransactionEditor(self, trans)
        updated_trans = editor.trans
        with db_session() as db:
            db_trans = db.query(Transaction).get(updated_trans.id)
            setattr(db_trans, 'date', updated_trans.date)
            setattr(db_trans, 'description', updated_trans.description)
            for i in range(len(updated_trans.entries), len(db_trans.entries)):
                db.query(BookEntry).filter_by(id=db_trans.entries[i].id).delete()
            for n,entry in enumerate(updated_trans.entries):
                code = db_get_account_code(entry.account)
                account = db.query(Account).filter_by(code=code).one()
                try: _entry = db_trans.entries[n]
                except IndexError: #not enough entries
                    db.add(BookEntry(account=account, transaction=db_trans, type=entry.type, amount=entry.amount))
                else: # using existing entries
                    setattr(_entry, 'account', account)
                    setattr(_entry, 'type', entry.type)
                    setattr(_entry, 'amount', entry.amount)
        self.master.event_generate("<<DataBaseContentChanged>>")
                         
    def remove_transaction(self, trans_id):
        with db_session() as db:
            trans = db.query(Transaction).get(trans_id)
            for entry in trans.entries:
                db.delete(entry)
            else:
                db.delete(trans)
        self.master.event_generate("<<DataBaseContentChanged>>")
            
    def display_account(self, event):
        if iid := event.widget.focus():
            account_gname = event.widget.item(iid)['values'][1]
            print(account_gname)
            self.parent.master.ledger.account.set(account_gname)
            self.parent.master.ledger.render_filter()
            self.parent.master.notebook.select(2)
        return 'break'


