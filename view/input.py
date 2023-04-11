__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
import tkinter.font as tkfont 
from datetime import datetime
from json import load, loads, dumps
from dbase import db_session, Account, Transaction, BookEntry
from enum import Enum
import os, re

from .excelviewer import ExcelViewer
from .textviewer import TextEditor

class InputView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)
        
        DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.dirname = os.path.join(DIR, 'datafiles')
        self.filename = StringVar()
        
        self.tools_bar = ttk.Frame(self, height=15)
        self.tools_bar.pack(expand=False, fill='x', padx=1, pady=1)
        
        file_bar = ttk.Labelframe(self.tools_bar, text='File')
        file_bar.pack(expand=False, side='left', ipady=4, ipadx=3)
        new_edit_icon = PhotoImage(file='./view/icons/new_file.gif')
        new_edit_btn = ttk.Button(file_bar, image=new_edit_icon, command=self.new_edit)
        new_edit_btn.image = new_edit_icon
        new_edit_btn.pack(side='left')
        
        open_file_icon = PhotoImage(file='./view/icons/open_file.gif')
        open_file_btn = ttk.Button(file_bar, image=open_file_icon, command=self.open_file)
        open_file_btn.image = open_file_icon
        open_file_btn.pack(side='left')

        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        save_file_btn = ttk.Button(file_bar, image=save_file_icon, command=self.save_file)
        save_file_btn.image = save_file_icon
        save_file_btn.pack(side='left')

        #file_name_entry = Entry(file_bar, textvariable=self.filename, width=40)
        #file_name_entry.pack(side='left')
        self.file_name_entry = ttk.Combobox(file_bar, textvariable=self.filename, width=40)
        self.file_name_entry.pack(side='left')
        self.file_name_entry['values'] = self._get_files()
        self.file_name_entry.bind('<<ComboboxSelected>>', self._open_file)

        import_bar = ttk.Labelframe(self.tools_bar, text='Import')
        import_bar.pack(expand=False, side='left', ipadx=10)
        play_icon = PhotoImage(file='./view/icons/next.gif')
        play_btn = ttk.Button(import_bar, image=play_icon, command=self.execute_step)
        play_btn.image = play_icon
        play_btn.pack(side='left', padx=10)
        
        long_play_icon = PhotoImage(file='./view/icons/end.gif')
        long_play_btn = ttk.Button(import_bar, image=long_play_icon, command=self.execute)
        long_play_btn.image = long_play_icon
        long_play_btn.pack(padx=0)                                   
        
        self.editor = None
        self.new_edit()
        
    def _get_files(self) -> list:
        files = (file for file in os.listdir(self.dirname) if os.path.isfile(os.path.join(self.dirname, file)))
        return sorted(list(filter(lambda x: x.endswith('.json') or x.endswith('.xlsx'), files)), reverse=True)
    
                        
    def new_edit(self, *args):
        if self.editor: self.editor.destroy()
        basename = 'default.json'
        filename = os.path.join(self.dirname, basename )
        self.filename.set(basename)
        if not os.path.exists(filename):
            with open(filename, 'w') as _file: pass
        self.editor = TextEditor(self, filename)

    def _open_file(self, *args):
        filename = os.path.join(self.dirname, self.filename.get())
        if self.editor: self.editor.clean_up()
        if filename.endswith(".xlsx"):
            self.editor = ExcelViewer(self, filename)
        elif filename.endswith(".json"):
            self.editor = TextEditor(self, filename)
        else: raise Exception('Unknown file extension')
        
    def open_file(self, *args):
        filename = filedialog.askopenfilename(defaultextension="*.json", initialdir = self.dirname,
                                               filetypes=[("All Files", "*.*"),
                                                          ("Json Documents","*.json"),
                                                          ("Excel Documents","*.xlsx")])
        if filename:
            basename = os.path.basename(filename)
            self.filename.set(basename)
            self.dirname = os.path.dirname(filename)
            self.file_name_entry['values'] = self._get_files()
            self._open_file()


    def save_file(self, *args):
        if not self.filename.get():
            file_name = filedialog.asksaveasfilename(defaultextension='*.json',
                                                     initialdir = self.dirname,
                                                     filetypes=[("All Files", "*.*"),
                                                                ("Json Documents","*.json")])
            self.dirname = os.path.dirname(file_name)
            self.filename.set(os.path.basename(file_name))
            filename = os.path.join(self.dirname, self.filename)
            self.editor.save_to_file(filename)
        else:
            self.editor.save_to_file()

    def content_verification(self):
        ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\/\s\w]+')
        content = self.text.get(1.0, 'end-1c')
        data = loads(content)
        for trans in data:
            if 'date' not in trans:
                raise Exception('Transaction miss date')
            else:
                try: datetime.strptime(trans['date'], '%d-%m-%Y').date()
                except: raise Exception('Wrong date format')
            if 'description' not in trans:
                raise Exception('Transaction miss description')
            if 'entries' not in trans:
                raise Exception('Transaction miss entries')
            elif len(trans['entries']) < 2:
                raise Exception('At least two entries are required in a transaction')
            else:
                with db_session() as db:
                    for entry in trans['entries']:
                        if 'account' not in entry:
                            raise Exception('Transaction entry misses account')
                        else:
                            _account = entry['account']
                            if match := ptrn.fullmatch(_account):
                                code = match.group('code')
                                try: account = db.query(Account).filter_by(code=code).one()
                                except: raise Exception(f'Unknown account code:"{code}"')
                            if 'debit' not in entry and 'credit' not in entry:
                                raise  Exception('debit or credit amount miss in entry')
    def execute_step(self, *args):
        try: self.content_verification()
        except Exception as e:
            print(e)
            raise Exception('Verification failed')
        else:
            content = self.text.get(1.0, 'end-1c')
            data = loads(content)
            answer = messagebox.askokcancel(title='Confirmation',
                                            message=f"{len(data)} transactiosn are ready",
                                            icon=WARNING)
            if answer:
                with db_session() as db:
                    for n,trans in enumerate(data):
                        answer = messagebox.askokcancel(title='Step by step',
                                                     message="Next transaction?",
                                                     icon=WARNING)
                        if not answer: break
                        self.new_transaction(db, trans)
                    else:
                        title = "Transaction Input"
                        msg = f"{len(data)} transactions has/have been created"
                        messagebox.showinfo(title=title, message=msg)
                #self.master.master.event_generate("<<DataBaseContentChanged>>")
    
    def execute(self, *args):
        try: self.content_verification()
        except Exception as e:
            print(e)
            raise Exception('Verification failed')
        else:
            content = self.text.get(1.0, 'end-1c')
            data = loads(content)
            answer = messagebox.askokcancel(title='Confirmation',
                                            message=f"{len(data)} transactiosn are ready",
                                            icon=WARNING)
            if answer:
                with db_session() as db:
                    for n,trans in enumerate(data):
                        self.new_transaction(db, trans)
                    else:
                        title = "Transaction Input"
                        msg = f"{len(data)} transactions has/have been created"
                        messagebox.showinfo(title=title, message=msg)
                #self.master.master.event_generate("<<DataBaseContentChanged>>")

    def new_transaction(self, db, trans):
        ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\/\s\w]+')
        description = trans['description']
        date = datetime.strptime(trans['date'], '%d-%m-%Y').date()
        transaction = Transaction(date=date, description=description)
        db.add(transaction)
        for entry in trans['entries']:
            _account = entry['account']
            if match := ptrn.fullmatch(_account):
                code = match.group('code')
                try: account = db.query(Account).filter_by(code=code).one()
                except: raise Exception(f'Unknown account code:"{code}"')
                else:
                    if 'debit' in entry and 'credit' in entry:
                        print(trans)
                        raise Exception('Wrong BookEntry Format')
                    elif 'debit' in entry and entry['debit'] > 0:
                        db.add(BookEntry(account=account, transaction=transaction, type='DEBIT', amount=float(entry['debit'])))
                    elif 'credit' in entry and entry['credit'] > 0:
                        db.add(BookEntry(account=account, transaction=transaction, type='CREDIT', amount=float(entry['credit'])))
                    else: raise Exception(f'Wrong BookEntry format')
            else:
                raise Exception(f'Wrong account pattern:"{_account}"')

    

        
