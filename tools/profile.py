__author__ = 'Manuel Escriche'
import locale, json
locale.setlocale(locale.LC_ALL, '')

import argparse, sys, os
from datamodel import UserData

parser = argparse.ArgumentParser(description='tool to create user profile for accounting')
parser.add_argument('user', help='username used')
args = parser.parse_args()
print(args)

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)

user = UserData(root_dir, args.user)
        
if not os.path.isdir(user.user_dir):
    print(f"user {args.user} hasn't been configured yet: use configApp tool for configuration")
    exit()

from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import Dialog
from view.text_editor import TextEditor
class AskAccountDialog(Dialog):
    def __init__(self, parent, title):
        self.answer = False
        super().__init__(parent, title)

    def apply(self):
        self.answer = True
        self.output = {'name':'Hola', 'code': 1234}

    def validate(self):
        return True
    
def askAccountDialog(master):
    w = AskAccountDialog(master, "Account Definition")
    return w.answer, w.output

class AccountsView(ttk.Frame):
    def __init__(self, parent, data, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.table = ttk.Treeview(self)
        self.table.pack(expand=True, fill='both')
        #self.table.config(show='headings')
        self.table.config(selectmode='browse', show='tree')
        columns=('name', 'type', 'content', 'code', 'parameters')
        self.table.config(columns=columns)
        #self.table.config(displaycolumns=columns)
        #self.table.heading('#0', text='Purpose')
        self.table.column('#0', width=75, stretch=False)
        self.table.heading('name', text='Name')
        self.table.column('name', width=200, stretch=False)
        self.table.heading('type', text='Type')
        self.table.column('type', width=75, stretch=False)
        self.table.heading('content', text='Content')
        self.table.column('content', width=75, stretch=False)
        self.table.heading('code', text='Code')
        self.table.column('code', width=50, stretch=False)
        self.table.heading('parameters', text='Parameters')
        self.table.column('parameters', width=20)
        self.table.tag_configure('asset', background='light green')
        self.table.tag_configure('claim', background='orange')
        self.table.tag_configure('revenue', background='light blue')
        self.table.tag_configure('outgoing', background='burlywood')
        self.assets_iid = self.table.insert('', 'end', text='Assets', open=True)
        self.claims_iid = self.table.insert('', 'end', text='Claims', open=True)
        self.revenue_iid = self.table.insert('', 'end', text='Revenue', open=True)
        self.outgoing_iid = self.table.insert('', 'end', text='Outgoing', open=True)

        
        for item in data:
            values = item['name'], item['type'], item['content'], item['code']
            if 'parameters' in item: values += (item['parameters'],)
            if item['content'] == 'REAL':
                if item['type'] == 'DEBIT':
                    self.table.insert(self.assets_iid, 'end', values=values, tag='asset')
                elif item['type'] == 'CREDIT':
                    self.table.insert(self.claims_iid, 'end', values=values, tag='claim')
                else:
                    print(f"account type error: {item['type']}")
            elif item['content'] == 'NOMINAL':    
                if item['type'] == 'CREDIT':
                    self.table.insert(self.revenue_iid, 'end', values=values, tag='revenue')
                elif item['type'] == 'DEBIT':
                    self.table.insert(self.outgoing_iid, 'end', values=values, tag='outgoing')
                else:
                    print(f"account type error: {item['type']}")
            else:
                print(f"account content error: {item['content']}")
                    
#        print(json.dumps(data, indent=4))
        
class IncomeView(ttk.Frame):
    def __init__(self, parent, data, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.table = ttk.Treeview(self)
        self.table.pack(expand=True, fill='both')
        self.table.config(selectmode='browse', show='tree')
        self.table.config(columns=('accounts',))
        self.table.column('#0', width=200, stretch=False)
        self.table.column('accounts', width=300) 
        self.table.tag_configure('revenue', background='light blue')
        self.table.tag_configure('outgoing', background='burlywood')
        
        self.revenue_iid = self.table.insert('', 'end', text='Revenue', open=True)
        self._fill_rows(self.revenue_iid, data['revenue'], 'revenue')

        self.outgoing_iid = self.table.insert('', 'end', text='Outgoing', open=True)
        self._fill_rows(self.outgoing_iid, data['outgoing'], 'outgoing')

        #print(json.dumps(data, indent=4))

        if self.table.tk.call('tk', 'windowingsystem') == 'aqua':
            self.table.bind('<2>', self._show_popup_menu)
            self.table.bind('<Control-1>', self._show_popup_menu)
        else:
            self.table.bind('<3>', self._show_popup_menu)
            
    def _fill_rows(self, p_iid, data, tag):
        if isinstance(data, dict):
            for key,value in data.items():
                iid = self.table.insert(p_iid, 'end', tag=tag, open=True,
                                        text=key.replace('_', ' ').title())
                self._fill_rows(iid, value, tag)
        elif isinstance(data, list):
            self.table.item(p_iid, value=','.join(data), tag=tag)
        else: return
        
    def _show_popup_menu(self, event):
        iid = self.table.identify_row(event.y)
        self.table.selection_set(iid)        
        menu = Menu(self.table)
        menu.add_command(label='Edit ', command=lambda:self._edit_(iid))
        menu.post(event.x_root, event.y_root) 

    def _edit_(self, iid):
        print(iid)
        
    #def _add_account(self, iid):
    #    print('add_account', iid)
    #    print(iid)
    #    answer, data = askAccountDialog(self)
    #    if answer:
    #        print(data)
    #        self.table.insert(iid, 'end', text=data['name']) 
    #        
    #def _remove_account(self, iid):
    #    if iid in (self.inflows_iid, self.outflows_iid): return
    #    self.table.delete(iid)
        
class BalanceView(ttk.Frame):
    def __init__(self, parent, data, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.table = ttk.Treeview(self)
        self.table.pack(expand=True, fill='both')
        self.table.config(selectmode='browse', show='tree')
        self.table.config(columns=('accounts',))
        self.table.column('#0', width=200, stretch=False)
        self.table.column('accounts', width=300) 
        self.table.tag_configure('asset', background='light green')
        self.table.tag_configure('claim', background='orange')

        self.assets_iid = self.table.insert('', 'end', text='Assets', open=True)
        self._fill_rows(self.assets_iid, data['assets'], 'asset')
        self.claims_iid = self.table.insert('', 'end', text='Claims', open=True)
        self._fill_rows(self.claims_iid, data['claims'], 'claim')
        
        if self.table.tk.call('tk', 'windowingsystem') == 'aqua':
            self.table.bind('<2>', self._show_popup_menu)
            self.table.bind('<Control-1>', self._show_popup_menu)
        else:
            self.table.bind('<3>', self._show_popup_menu)
            
        #print(json.dumps(data, indent=4))
    def _fill_rows(self, p_iid, data, tag):
        if isinstance(data, dict):
            for key,value in data.items():
                iid = self.table.insert(p_iid, 'end', tag=tag, open=True,
                                        text=key.replace('_',' ').title())
                self._fill_rows(iid, value, tag)
        elif isinstance(data, list):
            self.table.item(p_iid, value=','.join(data), tag=tag)
        else: return
        
    def _show_popup_menu(self, event):
        iid = self.table.identify_row(event.y)
        self.table.selection_set(iid)
        menu = Menu(self.table)
        menu.add_command(label='Edit', command=lambda:self._edit_(iid))
        menu.post(event.x_root, event.y_root) 

    def _edit_(self, iid):
        print(iid)
        
class ProfileTool(Tk):
    def __init__(self, user):
        super().__init__()
        self.title(f'Personal Accounting - Tool: Profile definition - User: {user.username.upper()}')
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
    
        filename = user.profile_file
        if not os.path.isfile(filename):
            print(f'{username}_profile.json file is not available')
                  
            return
        
        with open(filename, 'r') as _file:
            try: data = json.load(_file)
            except json.decoder.JSONDecodeError as error:
                _filename = os.path.basename(filename)
                print(f'Wrong file format: {_filename}, expected json')
                print('error:', error)
                return
            else:
                _accounts = data['accounts']
                #print(json.dumps(_accounts, indent=4))
                _balance = data['balance']
                #print(json.dumps(_balance, indent=4))
                _income = data['income']
                #print(json.dumps(_income, indent=4))
                #print(json.dumps(data, indent=4))
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        #self.profile = ProfileView(self.notebook, username, config_dir)
        #self.notebook.add(self.profile, text='Profile')

        self.accounts = AccountsView(self.notebook, _accounts)
        self.notebook.add(self.accounts, text='Accounts')

        self.income = IncomeView(self.notebook, _income)
        self.notebook.add(self.income, text='Income')

        self.balance = BalanceView(self.notebook, _balance)
        self.notebook.add(self.balance, text='Balance')
        
        
if __name__ == '__main__':
    app = ProfileTool(user)
    app.mainloop()
