__author__ = 'Manuel Escriche'

from tkinter import *
from tkinter import ttk
from .repo_evolution import EvoView
from .repo_income import IncomeRepoView
from .repo_tax import TaxRepoView
from .repo_ins import InsRepoView
from .repo_exp import ExpRepoView
from .repo_balance import BalanceRepoView
from .repo_summary import SummaryRepoView

class RepoView(ttk.Frame):
    color_schemes = {
        'Default': '#000000.#FFFFFF',
        'Greygarious': '#83406A.#D1D4D1',
        'Aquamarine': '#5B8340.#D1E7E0',
        'Bold Beige': '#4B4620.#FFF0E1',
        'Cobalt Blue': '#ffffBB.#3333aa',
        'Olive Green': '#D1E7E0.#5B8340',
        'Night Mode': '#FFFFFF.#000000',
    }
    def __init__(self, parent, user,  **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.user= user
        self.create_menu()
        self.create_gui()

    def create_gui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        ## -- Evolution
        self.evo = EvoView(self.notebook, self.user)
        self.notebook.add(self.evo, text='Evolution')

        self.income = IncomeRepoView(self.notebook, self.user)
        self.notebook.add(self.income, text='Income')

        self.tax = TaxRepoView(self.notebook, self.user)
        self.notebook.add(self.tax, text='Tax')

        self.insurance = InsRepoView(self.notebook, self.user)
        self.notebook.add(self.insurance, text='Insurance')

        self.expenses = ExpRepoView(self.notebook, self.user)
        self.notebook.add(self.expenses, text='Expense')
        
        self.balance = BalanceRepoView(self.notebook, self.user)
        self.notebook.add(self.balance, text='Balance')

        self.summary = SummaryRepoView(self.notebook, self.user)
        self.notebook.add(self.summary, text='Summary')

        #self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

    def _on_tab_selected(self, event):
        selected_index = event.widget.index("current")
        tab_text = event.widget.tab(selected_index, 'text')
        print("Selected tab:", tab_text)
        
    def create_menu(self): 
        menu_bar = Menu(self.master)
        file_menu = Menu(menu_bar)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=self.exit_app)

    def exit_app(self):
        self.parent.destroy()
