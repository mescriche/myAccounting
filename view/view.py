from tkinter import *
from tkinter import ttk
from .transaction import TransactionView
from dbase import db_session, Account, Transaction, BookEntry
from locale import currency

class View(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        #self.grid(column=0, row=0, padx=2, pady=2, sticky='news')
        self.pack(fill='both', expand=True)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_menu()
        self.create_gui()
        
        self.bind('<<NewTransaction>>', self.new_transaction)

    def set_controller(self, controller):
        self.controller = controller
       
    def create_gui(self):
               
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)
                
        ## ---- Journal
        journal_frame = ttk.Frame(notebook)
        journal_frame.pack(fill='both', expand=True)
        notebook.add(journal_frame, text='Journal')

        self.journal_text = Text(journal_frame)
        self.journal_text.pack(fill='both', expand=True)
        #ys = ttk.Scrollbar(journal_frame, orient='vertical', command=self.journal_text.yview)
        #self.journal_text['yscrollcommand'] = ys.set
        self.update_journal_view()
        
        ## ---- Ledger
        ledger_frame = ttk.Frame(notebook)
        notebook.add(ledger_frame, text='Ledger')
        pw = ttk.Panedwindow(ledger_frame, orient=VERTICAL)
        pw.pack(fill='both', expand=True)
    
        acc_pw = ttk.Panedwindow(pw, orient=HORIZONTAL)
        pw.add(acc_pw, weight=1)
        
        debit_acc_frame = ttk.Labelframe(acc_pw, text='Assets', labelanchor='n')
        acc_pw.add(debit_acc_frame, weight=1)
        columns = ('id', 'name', '#entries', 'balance')
        self.ledger_debit_accounts = ttk.Treeview(debit_acc_frame, columns=columns, show='headings')
        self.ledger_debit_accounts.pack(fill='both', expand=True)
        self.ledger_debit_accounts.heading('id', text='Id')
        self.ledger_debit_accounts.column('id', width=25, stretch=False, anchor='c')
        self.ledger_debit_accounts.heading('name', text='Name')
        self.ledger_debit_accounts.column('name', width=150, anchor='w')
        self.ledger_debit_accounts.heading('#entries', text='#entries')
        self.ledger_debit_accounts.column('#entries', width=25,  anchor='c')
        self.ledger_debit_accounts.heading('balance', text='Balance')
        self.ledger_debit_accounts.column('balance', width=75,  anchor='e')
        self.ledger_debit_accounts.tag_configure('total', background='#cccccc')
        self.ledger_debit_accounts.bind('<<TreeviewSelect>>', self.update_ledger_debit_entries)

        
        credit_acc_frame = ttk.Labelframe(acc_pw, text='Claims', labelanchor='n')
        acc_pw.add(credit_acc_frame, weight=1)
        columns = ('id', 'name', '#entries', 'balance')
        self.ledger_credit_accounts = ttk.Treeview(credit_acc_frame, columns=columns, show='headings')
        self.ledger_credit_accounts.pack(fill='both', expand=True)
        self.ledger_credit_accounts.heading('id', text='Id')
        self.ledger_credit_accounts.column('id', width=25, stretch=False, anchor='c')
        self.ledger_credit_accounts.heading('name', text='Name')
        self.ledger_credit_accounts.column('name', width=150, anchor='w')
        self.ledger_credit_accounts.heading('#entries', text='#entries')
        self.ledger_credit_accounts.column('#entries', width=25,  anchor='c')
        self.ledger_credit_accounts.heading('balance', text='Balance')
        self.ledger_credit_accounts.column('balance', width=75,  anchor='e')
        self.ledger_credit_accounts.bind('<<TreeviewSelect>>', self.update_ledger_credit_entries)
        self.ledger_credit_accounts.tag_configure('total', background='#cccccc')
        self.update_ledger_accounts()

        
        entries_frame = ttk.Frame(pw) 
        pw.add(entries_frame, weight=1)
        columns = ('id', 'trans','date', 'description', 'debit', 'credit')
        self.ledger_entries = ttk.Treeview(entries_frame, columns=columns, show='headings')
        self.ledger_entries.pack(fill='both', expand=True)
        self.ledger_entries.heading('id', text='Id')
        self.ledger_entries.column('id', width=25, stretch=False, anchor='c')
        self.ledger_entries.heading('trans', text='TrId')
        self.ledger_entries.column('trans', width=50, stretch=False, anchor='c')
        self.ledger_entries.heading('date', text='Date')
        self.ledger_entries.column('date', width=100, stretch=False, anchor='c')
        self.ledger_entries.heading('description', text='Description')
        self.ledger_entries.column('description',  anchor='w')
        self.ledger_entries.heading('debit', text='Debit')
        self.ledger_entries.column('debit', width=75, stretch=False, anchor='e')
        self.ledger_entries.heading('credit', text='Credit')
        self.ledger_entries.column('credit', width=75, stretch=False, anchor='e')
        self.ledger_entries.tag_configure('total', background='#cccccc')
        
        ## ---- Income
        income_frame = ttk.Frame(notebook)
        notebook.add(income_frame, text='Income')
        
        
        ## ---- Balance
        balance_frame = ttk.Frame(notebook)
        notebook.add(balance_frame, text='Balance')

        
    #def show_year_range(self):
    def update_journal_view(self, *args):
        self.journal_text.delete('1.0', 'end')
        with db_session() as db:
            for trans in reversed(db.query(Transaction).all()):
                self.journal_text.insert('end', '{:=^60} \n'.format(' Transaction #{} '.format(trans.id)))
                self.journal_text.insert('end', 'Date: {:%d-%m-%Y} \n'.format(trans.date))
                self.journal_text.insert('end', 'Description: {} \n'.format(trans.description))
                self.journal_text.insert('end', '{:-^60} \n'.format('-'))
                self.journal_text.insert('end', '| {:^10} | {:^30} | {:^10} |\n'.format('Debit', 'Account', 'Credit'))
                self.journal_text.insert('end', '{:-^60} \n'.format('-'))
                for entry in trans.entries:
                    values = (entry.debit_currency, entry.account.gname, entry.credit_currency)
                    self.journal_text.insert('end', '| {:>10} | {:<30} | {:>10} |\n'.format(*values))
                self.journal_text.insert('end', '{:-^60} \n'.format('-'))
                values = (trans.debit_currency, '', trans.credit_currency)
                self.journal_text.insert('end', '| {:>10} | {:<30} | {:>10} |\n'.format(*values))
                
                
    def update_ledger_accounts(self, *args):
        self.ledger_debit_accounts.delete(*self.ledger_debit_accounts.get_children())
        self.ledger_credit_accounts.delete(*self.ledger_credit_accounts.get_children())
        assets_balance, claims_balance = 0,0
        with db_session() as db:
            for acc in db.query(Account).all():
                if acc.type == 'asset': assets_balance += acc.balance
                if acc.type == 'claim': claims_balance += acc.balance
            
        if assets_balance != claims_balance: raise Exception("BalanceError")
        assets_balance_currency = currency(assets_balance, symbol=False, grouping=True) 
        claims_balance_currency = currency(claims_balance, symbol=False, grouping=True)
        
        self.ledger_debit_accounts.insert('', 'end', values=('','','', assets_balance_currency), tag='total')
        self.ledger_credit_accounts.insert('','end', values=('','','', claims_balance_currency), tag='total')
        
        with db_session() as db:
            for acc in db.query(Account).all():
                if acc.type == 'asset':
                    self.ledger_debit_accounts.insert('','end', text=acc.name,
                                                      values=(acc.id, acc.gname, len(acc.entries), acc.balance_currency))
                if acc.type == 'claim':
                    self.ledger_credit_accounts.insert('', 'end', text=acc.name,
                                                       values=(acc.id, acc.gname, len(acc.entries), acc.balance_currency))
                    
        

        
    def update_ledger_debit_entries(self, *args):
        self.ledger_entries.delete(*self.ledger_entries.get_children())
        item_id = self.ledger_debit_accounts.focus()
        account_name = self.ledger_debit_accounts.item(item_id)['text']
        with db_session() as db:
            try:
                account = db.query(Account).filter_by(name=account_name).one()
            except: pass
            else:
                self.ledger_entries.insert('','end', values=('','','','', account.debit_currency, account.credit_currency),tag='total')
                for entry in reversed(account.entries):
                    self.ledger_entries.insert('','end', values=(entry.id, entry.transaction.id,
                                                                 entry.transaction.date, entry.transaction.description,
                                                                 entry.debit_currency, entry.credit_currency))
                
                    
    def update_ledger_credit_entries(self, *args):
        self.ledger_entries.delete(*self.ledger_entries.get_children())
        item_id = self.ledger_credit_accounts.focus()
        account_name = self.ledger_credit_accounts.item(item_id)['text']
        with db_session() as db:
            try:
                account = db.query(Account).filter_by(name=account_name).one()
            except: pass
            else:
                self.ledger_entries.insert('','end', values=('','','','', account.debit_currency, account.credit_currency),tag='total')
                for entry in reversed(account.entries):
                    self.ledger_entries.insert('','end', values=(entry.id, entry.transaction.id,
                                                                 entry.transaction.date, entry.transaction.description,
                                                                 entry.debit_currency, entry.credit_currency))        
    def create_menu(self): 
        menu_bar = Menu(self.parent)

        #app_menu = Menu(menu_bar, name='apple')
        #app_menu.add_command(label='About Accounting')
        #app_menu.add_separator()
        #menu_bar.add_cascade(menu=app_menu)

        #help_menu = Menu(menu_bar, name='help')
        #menu_bar.add_cascade(menu=help_menu, label='Help')
        #self.createcommand('tk::mac::ShowHelp:', self.show_help)

        #window_menu = Menu(menu_bar, name='window')
        #menu_bar.add_cascade(menu= window_menu, label='Window')
        
        file_menu = Menu(menu_bar)
        file_menu.add_separator()
        file_menu.add_command(label='Import')
        file_menu.add_command(label='Quit', command=self.exit_app)
        menu_bar.add_cascade(label='File', menu=file_menu)
        
        
        new_menu = Menu(menu_bar)
        new_menu.add_command(label='Transaction', command=lambda: TransactionView(self))
        new_menu.add_command(label='Book Entry', command=self.new_bookentry)
        menu_bar.add_cascade(label='New', menu=new_menu)
        
        self.parent.config(menu=menu_bar)

    def exit_app(self):
        print('exit')
        self.parent.destroy()

    def new_bookentry(self, *args):
        print('new book entry')
        print(args)

    def new_transaction(self, *args):
        #print('new_transaction')
        self.update_ledger_accounts()
        self.update_journal_view()
        
        

   # def show_year():
        
