__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
from .transaction import DMTransaction, DMTransactionEncoder
from .input import InputView
from .journal import JournalView
from .ledger import LedgerView
from .income import IncomeView
from .balance import BalanceView
from .save import askSaveYearToFileDialog
from .map import MapView
from dbase import db_session, Transaction
from datetime import datetime
from locale import currency
import os, json

class View(ttk.Frame):
    color_schemes = {
        'Default': '#000000.#FFFFFF',
        'Greygarious': '#83406A.#D1D4D1',
        'Aquamarine': '#5B8340.#D1E7E0',
        'Bold Beige': '#4B4620.#FFF0E1',
        'Cobalt Blue': '#ffffBB.#3333aa',
        'Olive Green': '#D1E7E0.#5B8340',
        'Night Mode': '#FFFFFF.#000000',
    }
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_menu()
        self.create_gui()
        self.change_text_color()
       
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
        
        #top = self.winfo_toplevel()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        ## --- Input
        self.input = InputView(self.notebook)
        self.notebook.add(self.input, text='Input')
        #self.notebook.hide(self.input)
        
        ## ---- Journal
        self.journal = JournalView(self.notebook)
        self.notebook.add(self.journal, text='Journal')
        
        ## ---- Ledger
        self.ledger = LedgerView(self.notebook)
        self.notebook.add(self.ledger, text='Ledger')

        ## --- Map
        self.checking_map = MapView(self.notebook)
        self.notebook.add(self.checking_map, text='Checking Map')
        
        ## ---- Income
        self.income = IncomeView(self.notebook)
        self.notebook.add(self.income, text='Income')
        
        ## ---- Balance
        self.balance = BalanceView(self.notebook)
        self.notebook.add(self.balance, text='Balance')
        self.notebook.bind("<<DataBaseContentChanged>>", self.refresh_tabs)

    def refresh_tabs(self, event=None):
        with db_session() as db:
            trans = db.query(Transaction).order_by(Transaction.id.desc()).first()
            #print(trans)
            self.journal.refresh(trans.date)
            self.ledger.refresh(trans.date)
            self.checking_map.refresh(trans.date.year)
            self.income.refresh(trans.date.year)
            self.balance.refresh(trans.date.year)

    def toggle_input_tab(self):
        if not self.input_tab_sem.get():
            self.notebook.hide(self.input)
        else:
            self.notebook.add(self.input)
            self.notebook.select(self.input)
            
    def change_text_color(self):
        selected_color = self.text_color_choice.get()
        foreground,background = self.color_schemes.get(selected_color).split('.')
        #tabs = ('input', 'journal','income', 'balance')
        #for tab in tabs:
        #    eval(f'self.{tab}.text.config(background=background, foreground=foreground)')
        #self.input.config(background=background)
        #self.journal.filter.config(background=background)
        #self.ledger.filter.config(background=background)
        #self.income.title.config(background=background)
        #self.balance.title.config(background=background)
        
    def create_menu(self): 
        menu_bar = Menu(self.master)

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
        file_menu.add_command(label='Save', command=self.save_year_to_file)
        file_menu.add_command(label='Quit', command=self.exit_app)
        menu_bar.add_cascade(label='File', menu=file_menu)
        
        
        #new_menu = Menu(menu_bar)
        #new_menu.add_command(label='Transaction', command=lambda: TransactionEditor(self))
        #menu_bar.add_cascade(label='New', menu=new_menu)

        view_menu = Menu(menu_bar)
        self.input_tab_sem = BooleanVar()
        view_menu.add_checkbutton(label='Show/Hide Input Tab',
                                  onvalue=1, offvalue=0, variable=self.input_tab_sem,
                                  command=self.toggle_input_tab)

        

        self.text_color_choice = StringVar()
        #self.text_color_choice.set('Default')
        self.text_color_choice.set('Bold Beige')
        text_menu = Menu(menu_bar)
        view_menu.add_cascade(label='Text Colors', menu=text_menu)
        for k in sorted(self.color_schemes):
            text_menu.add_radiobutton(label=k, variable=self.text_color_choice, command=self.change_text_color)

         
        theme_menu = Menu(menu_bar)
        view_menu.add_cascade(label='Themes', menu=theme_menu)
        themes = ('aqua', 'clam', 'alt', 'default', 'classic')
        theme_choice = StringVar()
        theme_choice.set('default')
        for theme in sorted(themes):
            theme_menu.add_radiobutton(label=theme,
                                       variable=theme_choice,
                                       command=lambda: self.master.style.theme_use(theme_choice.get()))
        
        menu_bar.add_cascade(label='View', menu=view_menu)
        self.master.config(menu=menu_bar)

    def save_year_to_file(self):
        answer, year = askSaveYearToFileDialog(self)
        if answer:
            with db_session() as db:
                min_date = datetime.strptime(f'01-01-{year}', "%d-%m-%Y").date()
                max_date = datetime.strptime(f'31-12-{year}', "%d-%m-%Y").date()
                query = db.query(Transaction).filter(Transaction.date >= min_date).filter(Transaction.date <= max_date)
                if items := [item for item in query]:
                    _data = [DMTransaction.from_DBTransaction(item) for item in items]
                    _data = _data[1:]
                    for n,item in enumerate(_data, start=1): item.id = n
                    root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                    datafile_dir = os.path.join(root_dir, 'datafiles')
                    filename = f'{year}_app_seats.json'
                    _filename = os.path.join(datafile_dir, filename )
                    with open(_filename, 'w') as _file:
                        json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)

                    title = f"Save year {year} seats to file"
                    msg = f"{filename} saved "
                    messagebox.showinfo(title=title, message=msg, parent = self)
        
    def exit_app(self):
        self.parent.destroy()
        
        

        
         
