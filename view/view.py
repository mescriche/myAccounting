from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from .transaction import TransactionView
from .upload import InputView
from .journal import JournalView
from .ledger import LedgerView
from .income import IncomeView
from .balance import BalanceView
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
        
        self.bind('<<NewTransaction>>', self.render_views)
        self.bind('<<DeletedTransaction>>', self.render_views)

    def set_controller(self, controller):
        self.controller = controller
       
    def create_gui(self):

        #shortcut_bar = Frame(self, height=25, background='light sea green')
        #shortcut_bar.pack(expand='no', fill='x')
        #upload_icon = PhotoImage(file='./view/icons/open_file.gif')
        #btn =Button(shortcut_bar, image=upload_icon, command=self.file_upload)
        #btn.image=upload_icon
        #btn.pack(side='left')
        #plus_icon = PhotoImage(file='./view/icons/add.gif')        
        #btn=Button(shortcut_bar, image=plus_icon, command=lambda: TransactionView(self))
        #btn.image=plus_icon
        #btn.pack(side='left')
        
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        ## --- Input
        self.upload = InputView(self.notebook)
        self.notebook.add(self.upload, text='Input')
        #self.notebook.hide(self.upload)
        
        ## ---- Journal
        self.journal = JournalView(self.notebook)
        self.notebook.add(self.journal, text='Journal')
        self.journal.render()
        
        ## ---- Ledger
        self.ledger = LedgerView(self.notebook)
        self.notebook.add(self.ledger, text='Ledger')
        self.ledger.render()
        
        ## ---- Income
        self.income = IncomeView(self.notebook)
        self.notebook.add(self.income, text='Income')
        self.income.render()
        
        ## ---- Balance
        self.balance = BalanceView(self.notebook)
        self.notebook.add(self.balance, text='Balance')
        self.balance.render()
        
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
        #file_menu.add_command(label='Upload', command=self.file_upload)
        file_menu.add_command(label='Quit', command=self.exit_app)
        menu_bar.add_cascade(label='File', menu=file_menu)
        
        
        new_menu = Menu(menu_bar)
        new_menu.add_command(label='Transaction', command=lambda: TransactionView(self))
        menu_bar.add_cascade(label='New', menu=new_menu)
        
        self.parent.config(menu=menu_bar)

    def exit_app(self):
        print('exit')
        self.parent.destroy()
        
    def file_upload(self):
        filename = filedialog.askopenfilename(defaultextension='.json',
                                              filetypes=[("All Files","*.*"),("Json Documents","*.json")])
        if filename:
            self.notebook.add(self.upload)
        else:
            self.notebook.hide(self.upload)
        
    def render_views(self, *args):
        # print('render views')
        self.journal.render()
        self.ledger.render()
        self.income.render()
        self.balance.render()

        
         
