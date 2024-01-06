__author__ = 'Manuel Escriche'
import locale
locale.setlocale(locale.LC_ALL, '')

import argparse, sys, os

parser = argparse.ArgumentParser(description='program for creating json transactions from excell files')
parser.add_argument('user', help='username used')
args = parser.parse_args()
#print(args)

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
user_dir = os.path.join(root_dir, 'users', args.user)
        
if not os.path.isdir(user_dir):
    print(f"user {args.user} hasn't been configured yet: use configApp tool for configuration")
    exit()
    
sys.path.append(root_dir)

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from dbase import db_init, db_setup
from view.excel_editor import ExcelView
from view.ledger import LedgerView

class ExcelTool(Tk):
    def __init__(self, username):
        super().__init__()
        self.title(f'Personal Accounting - Tool: Excel Reader - User: {username.upper()}')
        window_size = 1100, 600
        screen_size = self.winfo_screenwidth(), self.winfo_screenheight()
        center =  int((screen_size[0] - window_size[0]) / 2) , int((screen_size[1] - window_size[1]) / 2)
        self.geometry(f'{window_size[0]}x{window_size[1]}+{center[0]}+{center[1]}')
        self.resizable(True, True)
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.option_add('*tearOff', False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.createcommand('tk::mac::Quit', self.destroy)

        dbase_dir = os.path.join(user_dir, 'dbase')
        dbase_file = os.path.join(dbase_dir, f'{username}_accounting.db')
        db_config = {'sqlalchemy.url':f'sqlite+pysqlite:///{dbase_file}',
                     'sqlalchemy.echo':False}
        db_init(db_config)
        
        config_dir = os.path.join(user_dir, 'configfiles')        
        db_file = os.path.join(config_dir, 'accounts.json')
        db_setup(db_file)
            
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.input = ExcelView(self.notebook, user_dir)
        self.notebook.add(self.input, text='Excel')

        self.ledger = LedgerView(self.notebook)
        self.notebook.add(self.ledger, text='Ledger')
        
if __name__ == '__main__':
    app = ExcelTool(args.user)
    app.mainloop()
