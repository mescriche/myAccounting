from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from .transaction import TransactionView
from .input import InputView
from .journal import JournalView
from .ledger import LedgerView
from .income import IncomeView
from .balance import BalanceView
from locale import currency

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
        
        self.bind('<<DataBaseContentChanged>>', self.render_views)

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
        self.input = InputView(self.notebook)
        self.notebook.add(self.input, text='Input')
        #self.notebook.hide(self.input)
        
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
    def toggle_input_tab(self):
        if not self.input_tab_sem.get():
            self.notebook.hide(self.input)
        else:
            self.notebook.add(self.input)
            self.notebook.select(self.input)
    def change_text_color(self):
        selected_color = self.text_color_choice.get()
        foreground,background = self.color_schemes.get(selected_color).split('.')
        self.input.text.config(background=background, foreground=foreground)
        
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
        #file_menu.add_command(label='Upload', command=self.file_upload)
        file_menu.add_command(label='Quit', command=self.exit_app)
        menu_bar.add_cascade(label='File', menu=file_menu)
        
        
        new_menu = Menu(menu_bar)
        new_menu.add_command(label='Transaction', command=lambda: TransactionView(self))
        menu_bar.add_cascade(label='New', menu=new_menu)

        view_menu = Menu(menu_bar)
        self.input_tab_sem = BooleanVar()
        view_menu.add_checkbutton(label='Show/Hide Input Tab',
                                  onvalue=1, offvalue=0, variable=self.input_tab_sem,
                                  command=self.toggle_input_tab)

        

        self.text_color_choice = StringVar()
        self.text_color_choice.set('Default')
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
        return "break"

        
         
