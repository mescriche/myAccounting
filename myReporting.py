__author__ = 'Manuel Escriche'
import locale
import matplotlib.pyplot as plt
locale.setlocale(locale.LC_ALL, '')

import argparse, sys, os
from datamodel import UserData, AccountsTree


parser = argparse.ArgumentParser(description='program to display reports from accounting database',
                                 epilog='')
parser.add_argument('user',help="username used")
args = parser.parse_args()
#print(args)

root_dir = os.path.dirname(os.path.realpath(__file__))
user = UserData(root_dir, args.user)

if not os.path.isdir(user.user_dir):
    print(f"user {args.user} hasn't been configured yet: use configApp tool for configuration")
    exit()

from tkinter import *
from tkinter import ttk
from view.view_repo import RepoView
from dbase import db_open

class App(Tk):
    def __init__(self, user):
        super().__init__()
        self.title(f'Personal Account Reporting  - User : {user.name.upper()}')
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
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.createcommand('tk::mac::Quit', self.close_app)

        db_open(user.db_config)
        acc_tree = AccountsTree.from_db()

        self.view = RepoView(self, user, acc_tree)
        
    def close_app(self, *args):
        plt.close('all')
        self.update()
        self.destroy()
        
        
if __name__ == '__main__':
    app = App(user)
    app.mainloop()
