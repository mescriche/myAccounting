from tkinter import *
from tkinter import ttk
from .transaction import TransactionView
from dbase import db_session, Account, Transaction, BookEntry

class View(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(column=0, row=0, padx=2, pady=2, sticky='news')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_menu()
        self.create_gui()

    def set_controller(self, controller):
        self.controller = controller
       
    def create_gui(self):
               
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)
                
        ## ---- Journal
        journal_frame = ttk.Frame(notebook)
        notebook.add(journal_frame, text='Journal')
        

        
        ## ---- Ledger
        ledger_frame = ttk.Frame(notebook)
        notebook.add(ledger_frame, text='Ledger')
        pw = ttk.Panedwindow(ledger_frame, orient=VERTICAL)
        pw.pack(fill='both', expand=True)
        frame1 = ttk.Frame(pw)
        pw.add(frame1, weight=1)
        columns = ('id', 'name', 'type', '#entries', 'balance')
        self.ledger_accounts = ttk.Treeview(frame1, columns=columns, show='headings')
        self.ledger_accounts.pack(fill='both', expand=True)
        self.ledger_accounts.heading('id', text='Id')
        self.ledger_accounts.column('id', width=25, stretch=False, anchor='c')
        self.ledger_accounts.heading('name', text='Name')
        self.ledger_accounts.column('name', width=200, anchor='c')
        self.ledger_accounts.heading('type', text='Type')
        self.ledger_accounts.column('type', width=100,  anchor='c')
        self.ledger_accounts.heading('#entries', text='#entries')
        self.ledger_accounts.column('#entries', width=100,  anchor='c')
        self.ledger_accounts.heading('balance', text='Balance')
        self.ledger_accounts.column('balance', width=100,  anchor='c')
        with db_session() as db:
            for acc in db.query(Account).all():
                self.ledger_accounts.insert('','end', text=acc.name,
                                            values=(acc.id, acc.name, acc.type, len(acc.entries), acc.balance))
        self.ledger_accounts.bind('<<TreeviewSelect>>', self.update_ledger)
                
        frame2 = ttk.Frame(pw) 
        pw.add(frame2, weight=5)
        columns = ('id', 'date', 'description', 'amount', 'balance')
        self.ledger_entries = ttk.Treeview(frame2, columns=columns, show='headings')
        self.ledger_entries.pack(fill='both', expand=True)
        self.ledger_entries.heading('id', text='Id')
        self.ledger_entries.column('id', width=25, stretch=False, anchor='c')
        self.ledger_entries.heading('date', text='Date')
        self.ledger_entries.column('date', width=100, stretch=False, anchor='c')
        self.ledger_entries.heading('description', text='Description')
        self.ledger_entries.column('description',  anchor='w')
        self.ledger_entries.heading('amount', text='Amount')
        self.ledger_entries.column('amount', width=50, stretch=False, anchor='e')
        self.ledger_entries.heading('balance', text='Balance')
        self.ledger_entries.column('balance', width=50, stretch=False, anchor='e')
        
        
        ## ---- Income
        income_frame = ttk.Frame(notebook)
        notebook.add(income_frame, text='Income')
        
        
        ## ---- Balance
        balance_frame = ttk.Frame(notebook)
        notebook.add(balance_frame, text='Balance')

        
        
        
        #print(notebook.tab(0,'sticky'))
        
        #self.feet = StringVar()
        #feet_entry=ttk.Entry(journal_frame, width=7, textvariable = self.feet)
        #feet_entry.grid(column=2, row=1, sticky=(W,E))

        #ttk.Label(journal_frame, text="Hola").grid(column=1, row=1, sticky=(W,E))

        #ttk.Button(journal_frame, text="Calculate", command=self.calculate).grid(column=3, row=2, sticky=W)

        #for child in journal_frame.winfo_children():
            #child.grid_configure(padx=5, pady=5)
            
        #feet_entry.focus()
        
    #def show_year_range(self):
    def update_ledger(self, *args):
        self.ledger_entries.delete(*self.ledger_entries.get_children())
        item_id = self.ledger_accounts.focus()
        account_name = self.ledger_accounts.item(item_id)['text']
        with db_session() as db:
            account = db.query(Account).filter_by(name=account_name).one()
            for entry in reversed(account.entries):
                self.ledger_entries.insert('','end', values=(entry.id, entry.transaction.date,
                                                             entry.transaction.description,
                                                             entry.amount, entry.balance))
        #for child_id in self.ledger_accounts.get_children():
        #    self.ledger_accounts.delete(child_id)            
        #with db_session() as db:
        #    for acc in db.query(Account).all():
        #        self.ledger_accounts.insert('','end', text = acc.name, values=(acc.id, acc.name, acc.type,
        #                                                                       len(acc.entries), acc.balance))
        
    def calculate(self, *args):
        print("calculate")
        try: value = int(self.feet.get())*2
        except ValueError: print("Error")
        else : print("Valor=", value)
        
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

    def new_bookentry(self):
        print('new book entry')

   # def show_year():
        
