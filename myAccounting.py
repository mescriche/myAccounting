__author__ = 'Manuel Escriche'
import locale
locale.setlocale(locale.LC_ALL, '')

import argparse, sys, os

parser = argparse.ArgumentParser(description='program for your personal finances',
                                 epilog='')
parser.add_argument('user',help="username used")
args = parser.parse_args()
#print(args)

root_dir = os.path.dirname(os.path.realpath(__file__))
user_dir = os.path.join(root_dir, 'users', args.user)
if not os.path.isdir(user_dir):
    print(f"user {args.user} hasn't been configured yet: use configApp tool for configuration")
    exit()

from tkinter import *
from tkinter import ttk
from view import View
from dbase import db_open

class App(Tk):
    def __init__(self, username):
        super().__init__()
        self.title(f'Personal Accounting - User : {username.upper()}')
        window_size = 1100,600
        screen_size = self.winfo_screenwidth(), self.winfo_screenheight()
        center =  int((screen_size[0] - window_size[0]) / 2) , int((screen_size[1] - window_size[1]) / 2)
        self.geometry(f'{window_size[0]}x{window_size[1]}+{center[0]}+{center[1]}')
        self.resizable(True, True)
        self.style = ttk.Style()
        #print(self.style.theme_names())
        self.style.theme_use('default')
        #self.config(bg='skyblue')
        
        self.option_add('*tearOff', False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.createcommand('tk::mac::Quit', self.destroy)

        dbase_file = os.path.join(user_dir,'dbase',f'{username}_accounting.db')
        db_config = {'sqlalchemy.url':f'sqlite+pysqlite:///{dbase_file}',
                     'sqlalchemy.echo':False}
        db_open(db_config)
        #db_init(db_config)
        
        #config_dir = os.path.join(user_dir, 'configfiles')        
        #db_file = os.path.join(config_dir, 'accounts.json')
        #db_setup(db_file)

        #controller = Controller()        
        view = View(self, user_dir)
        
        
if __name__ == '__main__':
    app = App(args.user)
    app.mainloop()


    
