__author__ = 'Manuel Escriche'
import locale
locale.setlocale(locale.LC_ALL, '')
import argparse, sys, os

parser = argparse.ArgumentParser(description='program for creating json transactions from excell files')
parser.add_argument('username', help='username used')
args = parser.parse_args()
#print(args)

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)
from datamodel import UserData

user = UserData(root_dir, args.username)
        
if not os.path.isdir(user.user_dir):
    print(f"user {args.user} hasn't been configured yet: use configApp tool for configuration")
    exit()
    
from tkinter import *
from tkinter import ttk, messagebox
from dbase import db_init, db_setup
from view.excel_editor import ExcelView
from view.text_editor import TextEditor
from view.ledger import LedgerView
from view.journal import JournalView
from view.log import LogView

class Blackboard(ttk.Frame):
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)
        self.dirname = user.datafiles_dir
        
        tools_bar = ttk.Frame(self, height=15)
        tools_bar.pack(expand=False, fill='x', padx=1, pady=1)
        file_bar = ttk.Labelframe(tools_bar, text='File')
        file_bar.pack(expand=True, side='left', fill='x', ipady=4, ipadx=3)
        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        save_file_btn = ttk.Button(file_bar, image=save_file_icon, command=self.save_file)
        save_file_btn.image = save_file_icon
        save_file_btn.pack(side='left', padx=5)
        self.filename = StringVar()
        ttk.Entry(file_bar, textvariable=self.filename, width=45).pack(side='left', pady=4, padx=5)
        self.editor = TextEditor(self)

    def save_file(self):
        filename = os.path.join(self.dirname, self.filename.get())
        self.editor.save_to_file(filename)
        messagebox.showinfo(parent=self, message='File Saved')
            
    def set_filename(self, filename):
        basename = os.path.basename(filename)
        name, ext = os.path.splitext(basename)
        items = name.split('_')
        youngest_date = max(map(lambda item:item.date, self.editor.data()))
        self.filename.set('_'.join((youngest_date.strftime('%Y%m%d'), items[0], items[1])) + '.json')
        
class ExcelTool(Tk):
    def __init__(self, user):
        super().__init__()
        self.title(f'Personal Accounting - Tool: Excel Reader - User: {user.name.upper()}')
        window_size = 1100, 600
        screen_size = self.winfo_screenwidth(), self.winfo_screenheight()
        center =  int((screen_size[0] - window_size[0]) / 2) , int((screen_size[1] - window_size[1]) / 2)
        self.geometry(f'{window_size[0]}x{window_size[1]}+{center[0]}+{center[1]}')
        self.resizable(True, True)
        self.style = ttk.Style()
        self.style.theme_use('default')
        #self.style.configure('TEntry', lightcolor=[('focus', 'red')])
        self.option_add('*tearOff', False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.createcommand('tk::mac::Quit', self.destroy)

        db_init(user.db_config)        
        db_setup(user.accounts_file)
            
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        
        self.input = ExcelView(self.notebook, user)
        self.notebook.add(self.input, text='Excel')

        self.ledger = LedgerView(self.notebook)
        self.notebook.add(self.ledger, text='Ledger')

        self.journal = JournalView(self.notebook)
        self.notebook.add(self.journal, text='Journal')

        self.output = Blackboard(self.notebook, user)
        self.notebook.add(self.output, text='Blackboard')

        self.log = LogView(self.notebook)
        self.notebook.add(self.log, text='Log')
        
if __name__ == '__main__':
    app = ExcelTool(user)
    app.mainloop()
