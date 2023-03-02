from tkinter import *
from tkinter import ttk
from .transaction import TransactionView
from .journal import JournalView
from .ledger import LedgerView
from locale import currency

class View(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
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
        self.journal = JournalView(notebook)
        notebook.add(self.journal, text='Journal')
        self.journal.render()
        
        ## ---- Ledger
        self.ledger = LedgerView(notebook)
        notebook.add(self.ledger, text='Ledger')
        self.ledger.render()
        
        ## ---- Income
        income_frame = ttk.Frame(notebook)
        notebook.add(income_frame, text='Income')
        
        ## ---- Balance
        balance_frame = ttk.Frame(notebook)
        notebook.add(balance_frame, text='Balance')
        
    #def show_year_range(self):

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
        menu_bar.add_cascade(label='New', menu=new_menu)
        
        self.parent.config(menu=menu_bar)

    def exit_app(self):
        print('exit')
        self.parent.destroy()


    def new_transaction(self, *args):
        #print('new_transaction')
        self.ledger.render()
        self.journal.render()
        
         
